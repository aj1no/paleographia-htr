import json

from fastapi.testclient import TestClient

from paleographia.api import create_app


def test_repertoire_is_read_only_and_only_serves_catalogued_assets(corpus):
    root, config, pages, lines = corpus
    app = create_app(root, config)
    with TestClient(app) as client:
        assert client.get("/api/repertorio").status_code == 404
        catalog = {"edicao": "data/raw/edicao.pdf", "itens": [{
            "id": "exemplo", "imagem": lines[0]["crop_image"],
            "contexto": lines[0]["crop_image"], "estado": "aguarda conferência humana",
            "revisor": None, "validado_em": None}]}
        target = root / "data/manifests/repertorio_100r.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(catalog), encoding="utf-8")
        assert client.get("/repertorio").status_code == 200
        data = client.get("/api/repertorio").json()
        assert data["itens"][0]["revisor"] is None
        response = client.get(data["itens"][0]["imagem_url"])
        assert response.content == (root / lines[0]["crop_image"]).read_bytes()
        assert client.get(data["itens"][0]["contexto_url"]).status_code == 200
        assert client.get("/api/repertorio/exemplo/fonte").status_code == 404
        assert client.get("/api/repertorio/desconhecido/imagem").status_code == 404
        assert not (root / config["paths"]["workspace"] / "current.json").exists()
