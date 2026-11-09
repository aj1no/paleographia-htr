"""Demonstração da apresentação: uma cópia da aplicação com fólios prontos, fora dos dados oficiais.

Uso, na raiz do projeto:

    python scripts/demo_apresentacao.py montar --de tmp/demo_folios/workspace --config tmp/demo_folios/config.toml
    python scripts/demo_apresentacao.py guardar PAGE_ID     # tira o fólio da lista e o deixa pré-processado
    python scripts/demo_apresentacao.py restaurar           # volta a demonstração ao estado guardado
    python scripts/demo_apresentacao.py listar

Tudo fica em data/demo_apresentacao/ (fora do Git): o workspace, os recortes copiados, o estado de
referência (estado_guardado.json) e o cache de fólios pré-processados. Um fólio "guardado" some da
lista; quando alguém fizer o upload da mesma imagem, as linhas e a leitura do modelo voltam na hora,
com o aviso de que vieram do processamento anterior. Os workspaces oficiais são só lidos.
"""
import argparse
import json
import shutil
import sys
import tomllib
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))
from paleographia.io import now  # noqa: E402
from paleographia.services import ReviewService  # noqa: E402

PASTA = RAIZ / "data/demo_apresentacao"
CONFIG = RAIZ / "configs/demo_apresentacao.toml"
GUARDADO = PASTA / "estado_guardado.json"
CACHE = PASTA / "cache"


def servico():
    return ReviewService(RAIZ, tomllib.loads(CONFIG.read_text(encoding="utf-8")))


def copiar_recortes(itens, destino, raiz_temporaria):
    """Copia para ``destino`` os recortes que moram em pastas temporárias e reescreve os caminhos."""
    destino.mkdir(parents=True, exist_ok=True)
    for item in itens:
        caminho = item.get("crop_image")
        if not caminho:
            continue
        if raiz_temporaria is None or Path(caminho).as_posix().startswith(raiz_temporaria):
            origem = RAIZ / caminho
            alvo = destino / origem.name
            if not alvo.exists():
                shutil.copyfile(origem, alvo)
            item["crop_image"] = alvo.relative_to(RAIZ).as_posix()


def montar(args):
    if (PASTA / "workspace").exists() and not args.substituir:
        raise SystemExit("A demonstração já existe. Use --substituir para montar de novo.")
    origem = RAIZ / args.de
    revisao = json.loads((origem / "current.json").read_text(encoding="utf-8"))["revision"]
    estado = json.loads((origem / "revisions" / f"{revisao}.json").read_text(encoding="utf-8"))
    # Recortes de pastas temporárias (tmp/) passam a morar na demonstração; os oficiais só são lidos.
    copiar_recortes(estado["lines"] + estado["predictions"], PASTA / "recortes", "tmp/")
    if PASTA.exists() and args.substituir:
        shutil.rmtree(PASTA / "workspace", ignore_errors=True)
    config = (RAIZ / args.config).read_text(encoding="utf-8")
    linhas = []
    for linha in config.splitlines():
        if linha.startswith("workspace ="):
            linha = 'workspace = "data/demo_apresentacao/workspace"'
        linhas.append(linha)
    texto = "\n".join(linhas).rstrip() + '\n\n[demo]\n# Fólios pré-processados: o upload da mesma imagem carrega linhas e leitura na hora.\ncache_dir = "data/demo_apresentacao/cache"\n'
    cabecalho = ("# Demonstração da apresentação (cópia; dados oficiais intocados). Gerado por\n"
                 "# scripts/demo_apresentacao.py. Workspace e cache ficam fora do Git.\n")
    CONFIG.write_text(cabecalho + texto, encoding="utf-8")
    servico().save({k: estado[k] for k in ("pages", "lines", "predictions")} | {"revision": None}, "montar_demonstracao")
    guardar_estado()
    print("Demonstração montada:", len(estado["pages"]), "fólios,", len(estado["lines"]), "linhas,",
          len(estado["predictions"]), "leituras do modelo.")


def guardar_estado():
    estado = servico().state()
    GUARDADO.write_text(json.dumps({k: estado[k] for k in ("pages", "lines", "predictions")}, ensure_ascii=False),
                        encoding="utf-8")


def guardar(args):
    service = servico()
    estado = service.state()
    pagina = next((p for p in estado["pages"] if p["page_id"] == args.page_id), None)
    if pagina is None:
        raise SystemExit(f"Fólio {args.page_id} não está na demonstração.")
    linhas = [l for l in estado["lines"] if l["page_id"] == args.page_id]
    leituras = [p for p in estado["predictions"] if p["page_id"] == args.page_id]
    if not linhas or not leituras:
        raise SystemExit("Detecte as linhas e rode o reconhecedor neste fólio antes de guardá-lo.")
    copiar_recortes(linhas + leituras, CACHE / "recortes", None)
    entrada = {"page": pagina, "lines": linhas, "predictions": leituras, "processed_at": now()}
    CACHE.mkdir(parents=True, exist_ok=True)
    (CACHE / f"{pagina['source_sha256']}.json").write_text(json.dumps(entrada, ensure_ascii=False), encoding="utf-8")
    estado["pages"] = [p for p in estado["pages"] if p["page_id"] != args.page_id]
    estado["lines"] = [l for l in estado["lines"] if l["page_id"] != args.page_id]
    estado["predictions"] = [p for p in estado["predictions"] if p["page_id"] != args.page_id]
    service.save(estado, "guardar_folio_pre_processado")
    guardar_estado()
    print(f"{pagina['original_name']}: {len(linhas)} linhas e {len(leituras)} leituras guardadas. "
          "Ele saiu da lista e volta na hora quando a mesma imagem for enviada.")


def restaurar(_args):
    service = servico()
    estado = service.state()
    guardado = json.loads(GUARDADO.read_text(encoding="utf-8"))
    service.save(dict(estado, **guardado), "restaurar_demonstracao")
    print("Demonstração restaurada:", len(guardado["pages"]), "fólios.")


def listar(_args):
    estado = servico().state()
    for p in estado["pages"]:
        n = [l for l in estado["lines"] if l["page_id"] == p["page_id"]]
        print(f"- {p['page_id']}: {p['original_name']} ({len(n)} linhas)")
    for entrada in sorted(CACHE.glob("*.json")):
        dados = json.loads(entrada.read_text(encoding="utf-8"))
        print(f"* pré-processado: {dados['page']['original_name']} ({len(dados['lines'])} linhas)")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="comando", required=True)
    m = sub.add_parser("montar")
    m.add_argument("--de", required=True)
    m.add_argument("--config", required=True)
    m.add_argument("--substituir", action="store_true")
    m.set_defaults(func=montar)
    g = sub.add_parser("guardar")
    g.add_argument("page_id")
    g.set_defaults(func=guardar)
    sub.add_parser("restaurar").set_defaults(func=restaurar)
    sub.add_parser("listar").set_defaults(func=listar)
    args = parser.parse_args()
    args.func(args)
