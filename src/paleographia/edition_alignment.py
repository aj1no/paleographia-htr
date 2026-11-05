"""Align a line-preserving published transcription to segmented manuscript lines.

Used only to build *training* pairs. The base recognizer's reading of each crop
is a guide: a monotonic dynamic programme pairs crops with edition lines in
reading order, skipping margins, signatures and lines the edition does not
carry. A pair is kept only when the guide reading is close to the edition line,
so the label comes from the edition and never from the model. Pairs produced
here are ``edition_aligned``: they are not human visual validation.
"""
import re
import unicodedata

FOLIO_MARKER = re.compile(r"^\s*(\d{3})(/Verso\.?)?\s*$")


def normalize(text):
    return " ".join(unicodedata.normalize("NFC", text or "").split())


def levenshtein(a, b):
    if len(a) < len(b):
        a, b = b, a
    previous = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        current = [i]
        for j, cb in enumerate(b, 1):
            current.append(min(previous[j] + 1, current[j - 1] + 1, previous[j - 1] + (ca != cb)))
        previous = current
    return previous[-1]


def cer(reference, hypothesis):
    reference, hypothesis = normalize(reference), normalize(hypothesis)
    return levenshtein(reference, hypothesis) / max(1, len(reference))


def split_by_folio(lines):
    """Split edition lines at folio markers such as ``269`` and ``269/Verso.``.

    Returns ``{"269r": [...], "269v": [...], ...}``; lines before the first
    marker are kept under ``"_antes"`` because a heading may sit above it.
    """
    folios, current = {"_antes": []}, "_antes"
    for raw in lines:
        match = FOLIO_MARKER.match(raw)
        if match:
            current = match.group(1) + ("v" if match.group(2) else "r")
            folios.setdefault(current, [])
            continue
        if raw.strip():
            folios[current].append(raw.rstrip())
    return folios


def align(edition_lines, guide_readings, max_cer=0.45, skip_penalty=0.6):
    """Monotonic alignment of edition lines (labels) to crops (guide readings).

    Returns ``[(crop_index, edition_index, cer)]`` for pairs at or under ``max_cer``.
    """
    n, m = len(guide_readings), len(edition_lines)
    cost = [[cer(edition_lines[j], guide_readings[i]) for j in range(m)] for i in range(n)]
    INF = float("inf")
    best = [[INF] * (m + 1) for _ in range(n + 1)]
    move = [[None] * (m + 1) for _ in range(n + 1)]
    best[0][0] = 0.0
    for i in range(n + 1):
        for j in range(m + 1):
            here = best[i][j]
            if here == INF:
                continue
            if i < n and here + skip_penalty < best[i + 1][j]:
                best[i + 1][j], move[i + 1][j] = here + skip_penalty, ("skip_crop", i, j)
            if j < m and here + skip_penalty < best[i][j + 1]:
                best[i][j + 1], move[i][j + 1] = here + skip_penalty, ("skip_line", i, j)
            if i < n and j < m:
                step = here + min(cost[i][j], 1.0)
                if step < best[i + 1][j + 1]:
                    best[i + 1][j + 1], move[i + 1][j + 1] = step, ("pair", i, j)
    pairs, i, j = [], n, m
    while (i, j) != (0, 0):
        kind, pi, pj = move[i][j]
        if kind == "pair" and cost[pi][pj] <= max_cer:
            pairs.append((pi, pj, cost[pi][pj]))
        i, j = pi, pj
    return list(reversed(pairs))
