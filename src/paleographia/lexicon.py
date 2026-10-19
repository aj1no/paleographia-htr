"""Consulta documental determinística; não executa HTR nem corrige referências."""
import hashlib
import json
import unicodedata
from datetime import datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from .io import now, safe_path


REPERTOIRES = {"portugues_historico": "Português histórico", "acervo": "Vocabulário do acervo",
               "indigena": "Repertórios indígenas (conforme a fonte)"}


class Origin(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    document_id: str = Field(min_length=1)
    split_group: str = Field(min_length=1)
    revision: str = Field(min_length=1)
    line_id: str = Field(min_length=1)
    split: str | None
    dataset_role: str = Field(min_length=1)
    reviewer: str = Field(min_length=1)
    reviewed_at: str = Field(min_length=1)


class Entry(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    id: str = Field(pattern=r"^[a-zA-Z0-9_-]+$")
    form: str = Field(min_length=1, max_length=80)
    repertoire: Literal["portugues_historico", "acervo", "indigena"]
    language: str | None
    language_note: str
    kind: str = Field(min_length=1)
    meaning: str | None
    note: str
    attestation_period: str = Field(min_length=1)
    source_id: str = Field(min_length=1)
    volume: str | None
    printed_page: str | None
    pdf_page: int | None = Field(ge=1)
    locator: str = Field(min_length=1)
    url: str = Field(pattern=r"^https://")
    source_file: str | None
    source_sha256: str | None = Field(pattern=r"^[a-f0-9]{64}$")
    evidence_file: str | None = None
    evidence_sha256: str | None = Field(default=None, pattern=r"^[a-f0-9]{64}$")
    evidence: Literal["verificado_na_fonte", "atestado_no_acervo", "pendente"]
    checked_by: str = Field(min_length=1)
    checked_at: str = Field(min_length=1)
    extraction: str = Field(min_length=1)
    variant_of: str | None = None
    expansion: str | None = None
    corpus_origin: Origin | None = None


def nfc(text):
    return unicodedata.normalize("NFC", text)


def folded(text):
    return "".join(c for c in unicodedata.normalize("NFD", nfc(text).casefold()) if not unicodedata.combining(c))


def distance(a, b):
    previous = list(range(len(b) + 1))
    for i, left in enumerate(a, 1):
        current = [i]
        for j, right in enumerate(b, 1):
            current.append(min(current[-1] + 1, previous[j] + 1, previous[j-1] + (left != right)))
        previous = current
    return previous[-1]


class Lexicon:
    def __init__(self, root, directory="data/lexicon"):
        directory = safe_path(root, directory)
        try:
            source_bytes = (directory/"sources.json").read_bytes()
            entry_bytes = (directory/"entries.jsonl").read_bytes()
            catalog = json.loads(source_bytes)
            self.version = catalog["version"]
            if not isinstance(self.version, str) or not self.version.strip():
                raise ValueError("Versão ausente.")
            self.sources = {s["id"]: s for s in catalog["sources"]}
            if len(self.sources) != len(catalog["sources"]):
                raise ValueError("Fonte duplicada.")
            for source in self.sources.values():
                if not all(isinstance(source.get(k), str) and source[k].strip() for k in ("title", "url", "use_conditions")):
                    raise ValueError("Fonte sem identificação ou condições de uso.")
                if not source["url"].startswith("https://"):
                    raise ValueError("URL de fonte inválida.")
            models = [Entry.model_validate(json.loads(line)) for line in entry_bytes.decode("utf-8").splitlines() if line.strip()]
            ids = {e.id for e in models}
            if len(ids) != len(models):
                raise ValueError("Entrada duplicada.")
            for entry in models:
                if entry.source_id not in self.sources or not entry.form.strip() or not entry.locator.strip():
                    raise ValueError("Entrada sem fonte/localizador.")
                if entry.variant_of and entry.variant_of not in ids:
                    raise ValueError("Variante sem entrada de origem.")
                if entry.repertoire == "acervo" and (not entry.corpus_origin or entry.evidence not in {"atestado_no_acervo", "pendente"}):
                    raise ValueError("Atestação do acervo exige proveniência documental.")
                if entry.evidence == "atestado_no_acervo" and not entry.corpus_origin:
                    raise ValueError("Atestação sem revisão de origem.")
                if entry.repertoire == "indigena" and not entry.language and entry.evidence != "pendente":
                    raise ValueError("Repertório indígena exige identificação sustentada pela fonte.")
                if entry.evidence == "verificado_na_fonte" and not entry.printed_page and not entry.pdf_page:
                    raise ValueError("Verbete conferido exige página.")
                if not datetime.fromisoformat(entry.checked_at).tzinfo:
                    raise ValueError("Conferência documental exige data com fuso.")
                if entry.corpus_origin and not datetime.fromisoformat(entry.corpus_origin.reviewed_at).tzinfo:
                    raise ValueError("Revisão de origem exige data com fuso.")
                for filename, checksum in ((entry.source_file, entry.source_sha256), (entry.evidence_file, entry.evidence_sha256)):
                    if filename and (not checksum or hashlib.sha256(safe_path(root, filename).read_bytes()).hexdigest() != checksum):
                        raise ValueError("Arquivo de evidência divergente.")
            self.entries = [entry.model_dump() for entry in models]
            self.fingerprint = hashlib.sha256(source_bytes+b"\0"+entry_bytes).hexdigest()
        except (OSError, ValueError, KeyError, TypeError, ValidationError) as exc:
            raise ValueError("Base lexical indisponível ou com registros inválidos. A revisão manual continua disponível.") from exc

    def status(self):
        return {"available": True, "version": self.version, "fingerprint": self.fingerprint,
                "entries": len(self.entries), "pending": sum(e["evidence"] == "pendente" for e in self.entries),
                "repertoires": [{"id": key, "label": label,
                    "entries": sum(e["repertoire"] == key and e["evidence"] != "pendente" for e in self.entries)} for key, label in REPERTOIRES.items()]}

    def query(self, text, repertoire="all", limit=5, exclude_groups=()):
        if not isinstance(text, str) or not 1 <= len(text.strip()) <= 80:
            raise ValueError("Consulte uma palavra ou trecho de até 80 caracteres.")
        if repertoire not in {"all", *REPERTOIRES} or type(limit) is not int or not 1 <= limit <= 8:
            raise ValueError("Repertório ou limite de candidatos inválido.")
        text = nfc(text.strip())
        entries = [e for e in self.entries if e["evidence"] != "pendente"
                   and (repertoire == "all" or e["repertoire"] == repertoire)
                   and not (e["corpus_origin"] and e["corpus_origin"]["split_group"] in exclude_groups)]
        candidates = []

        def add(items, match, cost, priority):
            replacement = " ".join(e["form"] for e in items)
            ids = [e["id"] for e in items]
            candidate_id = hashlib.sha256(json.dumps([self.fingerprint, ids, match, replacement], ensure_ascii=False).encode()).hexdigest()[:24]
            candidates.append({"id": candidate_id, "replacement": replacement, "match": match, "distance": cost,
                               "entries": [dict(e, source=self.sources[e["source_id"]]) for e in items], "priority": priority})

        for entry in entries:
            form = nfc(entry["form"])
            if text == form:
                add([entry], "exact", 0, 0)
            elif text.casefold() == form.casefold():
                add([entry], "case", 0, 1)
            elif folded(text) == folded(form):
                add([entry], "accent", distance(text.casefold(), form.casefold()), 2)
            elif len(text) >= 4:
                cost = distance(text.casefold(), form.casefold())
                if cost <= (2 if len(text) >= 8 else 1) and cost/max(len(text), len(form)) <= .25:
                    add([entry], "edit_distance", cost, 3)
        if " " not in text and len(text) <= 40:
            # Explicit segmentation only; no handwritten-letter substitutions.
            vocabulary = {}
            for entry in entries:
                if " " not in entry["form"] and len(entry["form"]) >= 2:
                    vocabulary.setdefault(nfc(entry["form"]).casefold(), []).append(entry)

            def split(start, parts):
                if start == len(text):
                    if len(parts) >= 2:
                        add(parts, "word_split", len(parts)-1, 4)
                    return
                if len(parts) >= 3 or sum(c["match"] == "word_split" for c in candidates) >= 8:
                    return
                for end in range(start+2, len(text)+1):
                    for entry in vocabulary.get(text[start:end].casefold(), ()):
                        split(end, [*parts, entry])
            split(0, [])
        candidates.sort(key=lambda c: (c["priority"], c["distance"], c["replacement"], [e["id"] for e in c["entries"]]))
        for candidate in candidates:
            candidate.pop("priority")
        return {**self.status(), "query": text, "repertoire": repertoire, "candidates": candidates[:limit],
                "message": "Distância de edição ordena candidatos; não é probabilidade de acerto." if candidates else "Sem candidato sustentado neste repertório. Ausência no léxico não significa erro."}


def append_assistance(root, directory, previous, supplied):
    """Preserve old events; verify every new application against the exact lexicon."""
    if not isinstance(supplied, list) or supplied[:len(previous)] != previous or len(supplied) > 100:
        raise ValueError("Histórico da assistência lexical não pode ser apagado ou substituído.")
    if len(supplied) == len(previous):
        return previous
    lexicon = Lexicon(root, directory)
    result = list(previous)
    for event in supplied[len(previous):]:
        if not isinstance(event, dict) or event.get("fingerprint") != lexicon.fingerprint or event.get("version") != lexicon.version:
            raise ValueError("A base lexical mudou. Consulte novamente antes de salvar a assistência.")
        response = lexicon.query(event.get("query"), event.get("repertoire", "all"), 8)
        candidate = next((c for c in response["candidates"] if c["id"] == event.get("candidate_id")), None)
        before, after = event.get("before"), event.get("after")
        start, end = event.get("start"), event.get("end")
        if (not candidate or not isinstance(before, str) or not isinstance(after, str) or max(len(before), len(after)) > 10000
                or type(start) is not int or type(end) is not int or not 0 <= start <= end <= len(before)
                or (start != end and before[start:end] != event["query"])
                or after != before[:start]+candidate["replacement"]+before[end:]):
            raise ValueError("Registro de aplicação lexical inválido; consulte e aplique novamente.")
        result.append({"version": lexicon.version, "fingerprint": lexicon.fingerprint, "candidate_id": candidate["id"],
                       "entry_ids": [e["id"] for e in candidate["entries"]], "query": event["query"],
                       "repertoire": response["repertoire"], "match": candidate["match"], "distance": candidate["distance"],
                       "replacement": candidate["replacement"], "before": before, "after": after,
                       "start": start, "end": end, "recorded_at": now()})
    return result
