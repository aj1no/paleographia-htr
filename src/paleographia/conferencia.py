"""Apoio à conferência humana: leituras às cegas, concordância entre revisores e tempos anônimos.

Leituras às cegas ficam num registro próprio do workspace e nunca alteram a linha: a
transcrição oficial continua passando pelo fluxo normal de validação. Os tempos de
conferência não guardam nome nem texto, só a duração, a condição (com ou sem sugestão
do modelo) e o tamanho da leitura.
"""
import json
import statistics
import unicodedata
import uuid

from .evaluation import counts, normalize
from .io import now

BLIND_FILE = "leituras_cegas.jsonl"
TIMING_FILE = "tempos_conferencia.jsonl"
CONDITIONS = {"com_sugestao", "sem_sugestao"}
ACTIONS = {"validada", "rascunho", "cega"}


def _folder(workspace):
    folder = workspace/"conferencia"
    folder.mkdir(parents=True, exist_ok=True)
    return folder


def _append(path, row):
    with open(path, "a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def _read(path):
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def add_blind_reading(workspace, line, reviewer, text):
    reviewer, text = (reviewer or "").strip(), unicodedata.normalize("NFC", (text or "").strip())
    if not reviewer:
        raise ValueError("Leitura às cegas exige revisor identificado.")
    if not text:
        raise ValueError("Escreva a leitura antes de registrar.")
    row = {"id": uuid.uuid4().hex, "line_id": line["line_id"], "page_id": line["page_id"],
           "reviewer": reviewer, "text": text, "created_at": now()}
    _append(_folder(workspace)/BLIND_FILE, row)
    return row


def latest_blind_readings(workspace, page_id):
    """Última leitura de cada revisor em cada linha: {line_id: {reviewer: row}}."""
    latest = {}
    for row in _read(_folder(workspace)/BLIND_FILE):
        if row["page_id"] == page_id:
            latest.setdefault(row["line_id"], {})[row["reviewer"]] = row
    return latest


def blind_status(workspace, page_id, reviewer):
    """Quantas leituras cada linha tem e se o revisor já leu, sem revelar os textos."""
    reviewer = (reviewer or "").strip()
    return {line_id: {"count": len(rows), "mine": reviewer in rows}
            for line_id, rows in latest_blind_readings(workspace, page_id).items()}


def agreement(workspace, page_id):
    """Concordância entre revisores: distância de edição de caracteres ÷ média dos comprimentos.

    A distância de edição é simétrica; dividir pela média evita escolher um revisor como
    referência. É o teto humano realista para comparar com o CER do modelo.
    """
    lines, distance, size = [], 0, 0
    for line_id, rows in latest_blind_readings(workspace, page_id).items():
        if len(rows) < 2:
            continue
        readers = sorted(rows)
        pairs = []
        for i, a in enumerate(readers):
            for b in readers[i + 1:]:
                ta, tb = rows[a]["text"], rows[b]["text"]
                errors = counts(ta, tb)["characters"]["errors"]
                mean = (len(normalize(ta)) + len(normalize(tb))) / 2
                pairs.append({"reviewers": [a, b], "distance": errors, "rate": errors / mean if mean else None})
                distance, size = distance + errors, size + mean
        lines.append({"line_id": line_id, "readings": {r: rows[r]["text"] for r in readers}, "pairs": pairs})
    return {"page_id": page_id, "lines": lines, "pairs": sum(len(l["pairs"]) for l in lines),
            "rate": distance / size if size else None,
            "method": "distância de edição de caracteres ÷ média dos comprimentos (NFC, espaços simplificados)"}


def add_timing(workspace, line, seconds, condition, action, chars):
    if condition not in CONDITIONS or action not in ACTIONS:
        raise ValueError("Condição ou ação de tempo desconhecida.")
    if not 0 < seconds <= 3600 or not 0 <= chars <= 2000:
        raise ValueError("Tempo fora do intervalo aceito.")
    row = {"line_id": line["line_id"], "page_id": line["page_id"], "seconds": round(float(seconds), 1),
           "condition": condition, "action": action, "chars": int(chars), "created_at": now()}
    _append(_folder(workspace)/TIMING_FILE, row)
    return row


def timing_summary(workspace):
    rows = [r for r in _read(_folder(workspace)/TIMING_FILE) if r["action"] in ("validada", "cega")]
    summary = {}
    for condition in sorted(CONDITIONS):
        group = [r for r in rows if r["condition"] == condition]
        per_char = [r["seconds"] / r["chars"] for r in group if r["chars"]]
        summary[condition] = {"lines": len(group),
                              "median_seconds": statistics.median(r["seconds"] for r in group) if group else None,
                              "median_seconds_per_char": statistics.median(per_char) if per_char else None}
    return summary
