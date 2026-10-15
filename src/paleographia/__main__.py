import argparse
import json
import sys
from pathlib import Path

from .config import load_config
from .io import read_jsonl, relative, sha256, write_json, write_jsonl


def parser():
    p = argparse.ArgumentParser(description="PaleographIA — piloto local verificável")
    commands = p.add_subparsers(dest="command", required=True)

    def command(name, help):
        return commands.add_parser(name, help=help)

    c = command("inventory", "Catalogar imagens, sem associar textos por ordem")
    c.add_argument("--input-dir", required=True)
    c.add_argument("--output", required=True)
    c = command("extract", "Extrair ZIP/RAR sem alterar originais")
    c.add_argument("--input-dir", required=True)
    c.add_argument("--output-dir", required=True)
    c = command("extract-reference", "Extrair páginas de edição como apoio pendente, nunca labels")
    c.add_argument("--pdf", required=True)
    c.add_argument("--output", required=True)
    c = command("associate", "Aplicar correspondências explícitas de documento, fólio e cobertura")
    c.add_argument("--pages", required=True)
    c.add_argument("--mapping", required=True)
    c.add_argument("--output", required=True)
    c = command("validate", "Validar catálogo, referências ou treino")
    c.add_argument("--manifest", required=True)
    c.add_argument("--pages", default="data/manifests/pages.jsonl")
    c.add_argument("--purpose", choices=["catalog", "evaluation", "training"], default="catalog")
    c.add_argument("--report", required=True)
    c = command("split", "Persistir divisão por documento com semente")
    c.add_argument("--lines", required=True)
    c.add_argument("--output", required=True)
    c.add_argument("--seed", type=int, default=1831)
    c.add_argument("--exploratory", action="store_true")
    c = command("segment", "Detectar e recortar linhas; referências ficam pendentes")
    c.add_argument("--pages", required=True)
    c.add_argument("--method", choices=["opencv", "kraken"], default="opencv")
    c.add_argument("--config", default="configs/pilot.toml")
    c.add_argument("--output-dir", required=True)
    c = command("recognize", "Reconhecer recortes de linha com modelo sob demanda")
    c.add_argument("--lines", required=True)
    c.add_argument("--config", default="configs/pilot.toml")
    c.add_argument("--output", required=True)
    c = command("prepare-weights", "Baixar explicitamente pesos e processador")
    c.add_argument("--config", default="configs/pilot.toml")
    c.add_argument("--output-dir", required=True)
    c = command("evaluate", "Avaliar cobertura revisada; omissões e inserções contam")
    c.add_argument("--reference", required=True)
    c.add_argument("--pages", required=True)
    c.add_argument("--predictions", required=True)
    c.add_argument("--output-dir", required=True)
    c = command("compare", "Comparar OpenCV/Kraken e controle humano, reconhecedor fixo")
    c.add_argument("--config", default="configs/pilot.toml")
    c.add_argument("--output-dir", required=True)
    c = command("train", "Dry run por padrão; execução exige --execute e dados aptos")
    c.add_argument("--config", default="configs/pilot.toml")
    c.add_argument("--output-dir", required=True)
    c.add_argument("--execute", action="store_true")
    c = command("import-catalog", "Importar manifests no editor vazio")
    c.add_argument("--pages", required=True)
    c.add_argument("--lines", required=True)
    c.add_argument("--config", default="configs/pilot.toml")
    c = command("export", "Exportar o estado revisado para manifests canônicos")
    c.add_argument("--config", default="configs/pilot.toml")
    c.add_argument("--output-dir", required=True)
    c = command("review", "Salvar uma revisão explícita no workspace, preservando histórico")
    c.add_argument("--line-id", required=True)
    c.add_argument("--changes", required=True, help="Arquivo JSON com campos alterados")
    c.add_argument("--config", default="configs/pilot.toml")
    c = command("serve", "Abrir interface local de revisão e API")
    c.add_argument("--config", default="configs/pilot.toml")
    c.add_argument("--host", default="127.0.0.1")
    c.add_argument("--port", type=int, default=8000)
    return p


def dispatch(args):
    root = Path.cwd()
    name = args.command
    if name == "inventory":
        from .data import inventory
        return inventory(args.input_dir, args.output, root)
    if name == "extract":
        from .data import extract_archives
        rows = extract_archives(args.input_dir, args.output_dir)
        return {"extracted": len(rows), "output": args.output_dir}
    if name == "extract-reference":
        from pypdf import PdfReader
        if Path(args.output).exists():
            raise ValueError("Extração de referência exige saída nova.")
        source = relative(args.pdf, root)
        rows = [{"reference_source": source, "reference_page": i+1, "text_raw": page.extract_text() or "",
                 "reference_kind": "unknown", "review_status": "pending_review", "source_sha256": sha256(args.pdf),
                 "editorial_exclusions": [], "note": "Página integral de apoio; separar títulos/créditos por trechos explícitos após inspeção."}
                for i, page in enumerate(PdfReader(args.pdf).pages)]
        write_jsonl(args.output, rows)
        return {"pages": len(rows), "labels_created": 0}
    if name == "associate":
        from .data import associate
        return {"pages": len(associate(args.pages, args.mapping, args.output, root))}
    if name == "validate":
        from .data import validate
        report = validate(read_jsonl(args.manifest), root, args.purpose, read_jsonl(args.pages))
        write_json(args.report, report)
        return report
    if name == "split":
        from .data import make_splits, require_valid
        if Path(args.output).exists():
            raise ValueError("Divisão exige saída nova; não refaça o teste reservado.")
        rows, protocol = make_splits(read_jsonl(args.lines), args.seed, args.exploratory)
        require_valid(rows, root, "catalog")
        write_jsonl(args.output, rows)
        write_json(Path(args.output).with_suffix(".protocol.json"), protocol)
        return protocol
    config = load_config(args.config) if hasattr(args, "config") else None
    if name == "segment":
        from .segmentation import segment_pages
        from .experiments import provenance
        rows, timings = segment_pages(read_jsonl(args.pages), args.method, config, args.output_dir, root)
        write_json(Path(args.output_dir)/"provenance.json", provenance(config, [args.pages]))
        return {"lines": len(rows), "review_status": "pending_review", "timings": timings}
    if name == "recognize":
        from .recognition import TrOCRRecognizer, recognize_lines
        from .data import require_valid
        from .experiments import provenance
        rows = read_jsonl(args.lines)
        require_valid(rows, root, "catalog")
        if not rows or any(not r.get("crop_image") or not r.get("bbox_xyxy") for r in rows):
            raise ValueError("Reconhecimento exige recortes de linha existentes com geometria.")
        predictions = recognize_lines(rows, TrOCRRecognizer(config), args.output, root)
        write_json(Path(args.output).with_suffix(".provenance.json"), provenance(config, [args.lines]))
        failures = sum(p["status"] != "ok" for p in predictions)
        return {"predictions": len(predictions), "failures": failures, "valid": failures == 0}
    if name == "prepare-weights":
        from .recognition import prepare_weights
        return prepare_weights(config, args.output_dir)
    if name == "evaluate":
        from .evaluation import evaluate
        from .experiments import provenance
        result = evaluate(read_jsonl(args.reference), read_jsonl(args.predictions), args.output_dir, root, read_jsonl(args.pages))
        write_json(Path(args.output_dir)/"provenance.json", provenance({}, [args.reference, args.predictions, args.pages]))
        return result
    if name in {"compare", "train"}:
        pages_path, lines_path = config["paths"]["pages"], config["paths"]["lines"]
        pages, lines = read_jsonl(pages_path), read_jsonl(lines_path)
        if name == "compare":
            from .experiments import compare
            return compare(pages, lines, config, args.output_dir, root, [pages_path, lines_path])
        from .training import training_run
        return training_run(lines, pages, config, args.output_dir, root, args.execute, [pages_path, lines_path])
    if name in {"import-catalog", "export", "review"}:
        from .services import ReviewService
        service = ReviewService(root, config)
        if name == "import-catalog":
            result = service.import_catalog(read_jsonl(args.pages), read_jsonl(args.lines))
            return {"pages": len(result["pages"]), "lines": len(result["lines"]), "revision": result["revision"]}
        if name == "export":
            return {"output": str(service.export(args.output_dir))}
        changes = json.loads(Path(args.changes).read_text(encoding="utf-8-sig"))
        return service.update_line(args.line_id, changes)
    if name == "serve":
        import uvicorn
        from .api import create_app
        # One worker shares a model instance and a local serialized revision store.
        uvicorn.run(create_app(root, config), host=args.host, port=args.port, workers=1)
        return {"status": "stopped"}
    raise ValueError("Comando desconhecido.")


def main(argv=None):
    args = parser().parse_args(argv)
    try:
        result = dispatch(args)
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
        failed = result.get("valid") is False or result.get("status") in {"failed", "not_executed", "partial"}
        return 2 if failed else 0
    except Exception as exc:
        print(f"PaleographIA: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
