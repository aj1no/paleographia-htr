import io
import json
import zipfile
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, Response
from pydantic import BaseModel, ConfigDict, Field, ValidationError
from starlette.concurrency import run_in_threadpool

from .config import load_config
from .io import safe_path
from .recognition import ModelUnavailable
from .presentation import present_predictions, review_policy
from .services import Conflict, ReviewService


class Edit(BaseModel):
    model_config = ConfigDict(extra="forbid")
    changes: dict
    revision: str | None = None


class AddLine(BaseModel):
    bbox_xyxy: list[int] = Field(min_length=4, max_length=4)
    region_id: str = "page"
    reading_order: int = Field(ge=0)


def create_app(root=None, config=None, recognizer=None):
    root = Path(root or Path.cwd()).resolve()
    config = config or load_config(root/"configs/pilot.toml")
    service = ReviewService(root, config, recognizer)
    @asynccontextmanager
    async def lifespan(app):
        try:
            yield
        finally:
            close = getattr(service.recognizer, "close", None)
            if close:
                await run_in_threadpool(close)

    app = FastAPI(title="PaleographIA — revisão local", lifespan=lifespan)
    app.state.service = service

    @app.exception_handler(ModelUnavailable)
    async def unavailable(request, exc):
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=503, content={"detail": str(exc), "review_available": True})

    @app.exception_handler(RequestValidationError)
    @app.exception_handler(ValidationError)
    async def invalid_fields(request, exc):
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=422, content={
            "detail": "Há campos ausentes ou inválidos. Confira os valores e tente novamente."})

    @app.exception_handler(Conflict)
    async def conflict(request, exc):
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    @app.exception_handler(ValueError)
    async def invalid(request, exc):
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=422, content={"detail": str(exc)})

    @app.exception_handler(KeyError)
    async def missing(request, exc):
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=404, content={"detail": "ID não encontrado."})

    @app.get("/")
    def index():
        return FileResponse(Path(__file__).parent/"web/index.html")

    @app.get("/review.js")
    def review_script():
        return FileResponse(Path(__file__).parent/"web/review.js", media_type="text/javascript")

    def repertoire_catalog():
        path = root / "data/manifests/repertorio_100r.json"
        if not path.is_file():
            raise HTTPException(404, "O repertório ainda não foi preparado.")
        return json.loads(path.read_text(encoding="utf-8"))

    @app.get("/repertorio")
    def repertoire():
        return FileResponse(Path(__file__).parent/"web/repertorio.html")

    @app.get("/api/repertorio")
    def repertoire_data():
        catalog = repertoire_catalog()
        return dict(catalog, itens=[dict(item,
                    imagem_url=f"/api/repertorio/{item['id']}/imagem",
                    contexto_url=f"/api/repertorio/{item['id']}/contexto") for item in catalog["itens"]])

    @app.get("/api/repertorio/edicao")
    def repertoire_edition():
        return FileResponse(safe_path(root, repertoire_catalog()["edicao"]), media_type="application/pdf")

    @app.get("/api/repertorio/{item_id}/{asset}")
    def repertoire_image(item_id: str, asset: str):
        item = next((item for item in repertoire_catalog()["itens"] if item["id"] == item_id), None)
        field = {"imagem": "imagem", "contexto": "contexto"}.get(asset)
        if item is None or field is None:
            raise HTTPException(404, "Exemplo ou imagem do repertório não encontrado.")
        return FileResponse(safe_path(root, item[field]), media_type="image/png")

    @app.get("/health")
    def health():
        return {"status": "online", "review_available": True, "recognition": service.recognizer.status()}

    @app.get("/api/catalog")
    def catalog():
        state = service.state()
        return dict(state, predictions=present_predictions(state["predictions"], state["lines"], config),
                    presentation_policy=review_policy(config))

    @app.post("/api/pages")
    async def upload(file: UploadFile = File(...)):
        content = await file.read(25*1024*1024+1)
        if len(content) > 25*1024*1024:
            raise HTTPException(413, "Imagem excede 25 MiB.")
        try:
            return await run_in_threadpool(service.import_image, content, file.filename)
        except ValueError as exc:
            raise HTTPException(400, str(exc)) from exc

    @app.post("/process-folio")
    async def process_folio(file: UploadFile = File(...), recognize: bool = False):
        page = await upload(file)
        state = service.state()
        lines = [l for l in state["lines"] if l["page_id"] == page["page_id"]]
        if not lines:
            lines = await run_in_threadpool(service.segment, page["page_id"])
        predictions = await run_in_threadpool(service.recognize_page, page["page_id"]) if recognize else []
        by_id = {p["line_id"]: p for p in present_predictions(predictions, lines, config)}
        return {"session_id": page["page_id"], "page_id": page["page_id"], "total_lines": len(lines),
                "lines": [dict(l, id=l["line_id"], text=by_id.get(l["line_id"], {}).get("presentation", {}).get("text", ""),
                          image_url=f"/lines/{page['page_id']}/{l['line_id']}.png",
                          y_percent=100*l["bbox_xyxy"][1]/page["height"],
                          height_percent=100*(l["bbox_xyxy"][3]-l["bbox_xyxy"][1])/page["height"]) for l in lines]}

    @app.post("/api/pages/{page_id}/segment")
    def segment(page_id: str, method: str = "opencv"):
        return service.segment(page_id, method)

    @app.post("/api/pages/{page_id}/recognize")
    def recognize(page_id: str):
        predictions = service.recognize_page(page_id)
        return present_predictions(predictions, service.state()["lines"], config)

    @app.patch("/api/pages/{page_id}")
    def edit_page(page_id: str, edit: Edit):
        return service.update_page(page_id, edit.changes, edit.revision)

    @app.post("/api/pages/{page_id}/lines")
    def add_line(page_id: str, line: AddLine):
        return service.add_line(page_id, line.bbox_xyxy, line.region_id, line.reading_order)

    @app.patch("/api/lines/{line_id}")
    def edit_line(line_id: str, edit: Edit):
        return service.update_line(line_id, edit.changes, edit.revision)

    @app.get("/api/pages/{page_id}/image")
    def image(page_id: str):
        page = service.get_page(page_id)
        if not page:
            raise HTTPException(404, "Página não encontrada.")
        # Render native pixels without an EXIF orientation hint. Geometry is always
        # measured on the encoded original, which remains unchanged on disk.
        from PIL import Image
        with Image.open(safe_path(root, page["source_image"])) as opened:
            preview = opened.convert("RGB")
            preview.info.clear()
            buffer = io.BytesIO()
            preview.save(buffer, format="PNG")
        return Response(buffer.getvalue(), media_type="image/png")

    @app.get("/lines/{page_id}/{filename}")
    def crop(page_id: str, filename: str):
        line_id = filename.removesuffix(".png")
        line = next((l for l in service.state()["lines"] if l["line_id"] == line_id and l["page_id"] == page_id), None)
        if line is None or filename != line_id+".png":
            raise HTTPException(404, "Recorte não encontrado.")
        return FileResponse(safe_path(root, line["crop_image"]))

    @app.get("/api/export")
    def export():
        state = service.state()
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
            for key in ("pages", "lines", "predictions"):
                archive.writestr(key+".jsonl", "".join(json.dumps(r, ensure_ascii=False)+"\n" for r in state[key]))
            archive.writestr("provenance.json", json.dumps({"revision": state["revision"]}))
        return Response(buffer.getvalue(), media_type="application/zip", headers={"Content-Disposition": "attachment; filename=paleographia-review.zip"})

    return app
