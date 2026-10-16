'use strict';
const $ = id => document.getElementById(id);
const clone = value => JSON.parse(JSON.stringify(value));
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);
let state = {pages: [], lines: [], predictions: []};
let recognitionState = 'not_loaded';
let pageId = null, lineId = null, mode = 'select', drag = null, pendingBox = null;
let renderedPage = null, renderedLine = null, displayedPageForm = null;
const drafts = {page: new Map(), line: new Map()}, activeRegions = new Map();
const pageFields = ['document', 'folio', 'side', 'pageReviewer', 'pageValidated', 'sourceUrl', 'credits'];
const coverageFields = ['coverage', 'coverageRegion', 'coverageSource', 'coveragePages', 'complete'];
const lineFields = ['diplomatic', 'modernized', 'order', 'region', 'reviewer', 'validated',
    'geometryChecked', 'exclusion', 'referenceSource', 'referencePages', 'x1', 'y1', 'x2', 'y2'];
const checkboxes = new Set(['pageValidated', 'complete', 'validated', 'geometryChecked']);
const regionLabel = value => value === 'page' ? 'principal' : value;
const regionId = value => value === 'principal' ? 'page' : value;
const page = () => state.pages.find(p => p.page_id === pageId);
const lines = () => state.lines.filter(l => l.page_id === pageId);
const selected = () => state.lines.find(l => l.line_id === lineId);
const entity = (kind, id) => (kind === 'page' ? state.pages : state.lines).find(r => r[kind + '_id'] === id);

function message(text, error = false) {
    $('message').textContent = text;
    $('message').classList.toggle('error', error);
}
async function request(url, method = 'GET', body) {
    const r = await fetch(url, {method, headers: body instanceof FormData ? {} : body ? {'Content-Type': 'application/json'} : {},
        body: body instanceof FormData ? body : body ? JSON.stringify(body) : undefined});
    if (!r.ok) {
        let detail;
        try { detail = (await r.json()).detail; } catch { /* Keep the local draft on invalid responses too. */ }
        const error = Error(typeof detail === 'string' ? detail : 'Há campos ausentes ou inválidos. Confira os valores.');
        error.status = r.status;
        throw error;
    }
    return r.json();
}
async function action(fn) {
    document.querySelectorAll('button').forEach(b => b.disabled = true);
    try { await fn(); }
    catch (e) {
        captureDrafts();
        message(e.status === 409 ? 'Conflito de revisão. Seu rascunho foi preservado. Atualize o catálogo e confira a versão salva antes de tentar novamente.'
            : e instanceof TypeError ? 'Não foi possível concluir a operação. Confira a conexão com o servidor local. Seu rascunho foi preservado.' : e.message, true);
    } finally {
        document.querySelectorAll('button').forEach(b => b.disabled = false);
        $('recognize').disabled = recognitionState === 'disabled';
    }
}
function readFields(fields) {
    return Object.fromEntries(fields.map(id => [id, checkboxes.has(id) ? $(id).checked : $(id).value]));
}
function writeFields(form, fields) {
    for (const id of fields) {
        if (checkboxes.has(id)) $(id).checked = form[id];
        else $(id).value = form[id];
    }
}
function coverageForm(c) {
    return {coverage: c?.bbox_xyxy.join(', ') || '', coverageRegion: regionLabel(c?.region_id || 'page'),
        coverageSource: c?.reference_source || '', coveragePages: c?.reference_pages?.join(', ') || '',
        complete: !!(c?.complete && c?.review_status === 'validated')};
}
function pageForm(p) {
    return {document: p.document_id, folio: p.folio_id, side: p.side, pageReviewer: p.reviewer || '',
        pageValidated: p.correspondence_status === 'validated', sourceUrl: p.source_url || '', credits: p.credits || '',
        regions: p.transcribed_coverage.map(c => ({original: clone(c), values: coverageForm(c)}))};
}
function lineForm(l) {
    return {diplomatic: l.text_diplomatic || '', modernized: l.text_modernized || '', order: String(l.reading_order),
        region: regionLabel(l.region_id), reviewer: l.reviewer || '', validated: l.review_status === 'validated',
        geometryChecked: l.geometry_status === 'validated', exclusion: l.exclusion_reason || '',
        referenceSource: l.reference_source || '', referencePages: l.reference_pages.join(', '),
        ...Object.fromEntries(['x1', 'y1', 'x2', 'y2'].map((id, i) => [id, String(l.bbox_xyxy[i])]))};
}
const formFor = (kind, record) => kind === 'page' ? pageForm(record) : lineForm(record);
function rebaseForm(kind, draft, record) {
    const before = formFor(kind, draft.base), latest = formFor(kind, record);
    const mergeFields = (old, local, remote, fields) => Object.fromEntries(fields.map(key =>
        [key, same(local[key], old[key]) ? remote[key] : local[key]]));
    const form = mergeFields(before, draft.form, latest, kind === 'page' ? pageFields : lineFields);
    if (kind === 'page') {
        // Keep remote changes to untouched fields/regions, including provenance.
        const id = region => region.original?.region_id;
        form.regions = latest.regions.flatMap(region => {
            const old = before.regions.find(r => id(r) === id(region));
            if (!old) return [region];
            const local = draft.form.regions.find(r => id(r) === id(region));
            return local ? [{original: region.original, values: mergeFields(old.values, local.values, region.values, coverageFields)}] : [];
        });
        for (const local of draft.form.regions) {
            const old = before.regions.find(r => id(r) === id(local));
            if (!local.original || (!latest.regions.some(r => id(r) === id(local)) && !same(local, old))) form.regions.push(local);
        }
    }
    return form;
}
function remember(kind, id, form) {
    const record = entity(kind, id);
    if (!record) return;
    const old = drafts[kind].get(id);
    const base = old?.base || clone(record);
    if (same(form, formFor(kind, base))) drafts[kind].delete(id);
    else drafts[kind].set(id, {form: clone(form), base, revision: old?.revision || state.revision});
}
function captureDrafts() {
    if (renderedLine) remember('line', renderedLine, readFields(lineFields));
    if (renderedPage && displayedPageForm) {
        const form = {...readFields(pageFields), regions: clone(displayedPageForm.regions)};
        const index = activeRegions.get(renderedPage) ?? 0;
        if (form.regions[index]) form.regions[index].values = readFields(coverageFields);
        displayedPageForm = form;
        remember('page', renderedPage, form);
    }
    renderDraftStatus();
}
function renderDraftStatus() {
    const count = drafts.page.size + drafts.line.size;
    $('draftStatus').textContent = count ? `${count} rascunho(s) local(is), ainda não salvo(s). Mantidos ao navegar; podem se perder ao fechar ou recarregar esta aba.` : 'Sem alterações locais pendentes.';
    const conflict = [['line', lineId], ['page', pageId]].find(([kind, id]) => {
        const d = drafts[kind].get(id);
        return d && entity(kind, id) && !same(d.base, entity(kind, id));
    });
    $('conflictPanel').hidden = !conflict;
    if (conflict) {
        const [kind, id] = conflict;
        const record = entity(kind, id);
        $('conflictVersion').textContent = kind === 'line'
            ? `Linha ${record.reading_order} · versão salva\nTranscrição: ${record.text_diplomatic || '(vazia)'}\nEdição de apoio: ${record.text_modernized || '(vazia)'}\nRecorte: ${record.bbox_xyxy.join(', ')}\nRegião: ${regionLabel(record.region_id)}\nRevisor: ${record.reviewer || '(não informado)'}\nTranscrição conferida: ${record.review_status === 'validated' ? 'sim' : 'não'}\nGeometria conferida: ${record.geometry_status === 'validated' ? 'sim' : 'não'}\nFonte: ${record.reference_source || '(vazia)'}\nPáginas: ${record.reference_pages.join(', ')}\nExclusão: ${record.exclusion_reason || '(nenhuma)'}`
            : `Fólio ${record.folio_id} · versão salva\nDocumento: ${record.document_id}\nLado: ${{recto: 'reto', verso: 'verso', unknown: 'a identificar'}[record.side]}\nCréditos: ${record.credits || '(vazios)'}\nFonte: ${record.source_url || '(vazia)'}\nRevisor: ${record.reviewer || '(não informado)'}\nCorrespondência conferida: ${record.correspondence_status === 'validated' ? 'sim' : 'não'}\nRegiões:\n` + record.transcribed_coverage.map(c => `${regionLabel(c.region_id)}: ${c.bbox_xyxy.join(', ')}; edição ${c.reference_source || '(vazia)'}; páginas ${(c.reference_pages || []).join(', ')}; cobertura conferida: ${c.complete && c.review_status === 'validated' ? 'sim' : 'não'}`).join('\n');
        $('rebaseDraft').onclick = () => {
            captureDrafts();
            const d = drafts[kind].get(id);
            if (!d) return;
            d.form = rebaseForm(kind, d, record);
            d.base = clone(record);
            d.revision = state.revision;
            renderPage();
            message('Versão conferida usada como base. O rascunho continua local; confira os campos e salve para gravar.');
        };
    }
}
async function refresh() {
    captureDrafts();
    state = await request('/api/catalog');
    // Unrelated saves may advance the global revision without changing this entity.
    // Actual entity conflicts keep their old revision until explicit human review.
    for (const kind of ['page', 'line']) for (const [id, draft] of drafts[kind]) {
        if (same(draft.base, entity(kind, id))) draft.revision = state.revision;
    }
    $('pages').replaceChildren();
    for (const p of state.pages) {
        const o = document.createElement('option'); o.value = p.page_id;
        o.textContent = p.original_name + ' · ' + p.folio_id; $('pages').append(o);
    }
    if (!pageId && state.pages.length) pageId = state.pages[0].page_id;
    $('pages').value = pageId || '';
    renderPage();
    const h = await request('/health');
    const recState = recognitionState = h.recognition.state;
    $('health').textContent = recState === 'disabled' ? 'Reconhecimento desativado · revisão manual disponível'
        : recState === 'unavailable' ? 'Reconhecedor indisponível · revisão manual disponível'
        : !state.presentation_policy?.automatic_transcription_enabled ? 'Revisão disponível · leitura automática em português indisponível'
        : recState === 'ready' ? 'PP-OCRv6 experimental disponível' : 'Revisão disponível · PP-OCRv6 sob demanda';
    $('recognize').disabled = recState === 'disabled';
    $('recognize').title = recState === 'disabled' ? 'Configure o reconhecedor PP-OCRv6 para executar uma nova leitura.' : '';
}
function renderCoverage() {
    const regions = displayedPageForm.regions;
    let index = activeRegions.get(pageId) ?? 0;
    if (index >= regions.length) index = Math.max(0, regions.length - 1);
    activeRegions.set(pageId, index);
    $('coverageSelect').replaceChildren();
    regions.forEach((r, i) => {
        const option = document.createElement('option'); option.value = String(i);
        option.textContent = r.values.coverageRegion || `Região ${i + 1}`; $('coverageSelect').append(option);
    });
    if (!regions.length) {
        const option = document.createElement('option'); option.textContent = 'Nenhuma região; use Adicionar região.';
        $('coverageSelect').append(option);
    }
    $('coverageSelect').value = String(index);
    writeFields(regions[index]?.values || coverageForm(null), coverageFields);
    coverageFields.forEach(id => $(id).disabled = !regions.length);
}
function renderPage() {
    const p = page(); if (!p) return;
    $('empty').hidden = true; $('pageImage').hidden = false;
    $('pageImage').src = '/api/pages/' + pageId + '/image'; $('pageName').textContent = p.folio_id;
    displayedPageForm = clone(drafts.page.get(pageId)?.form || pageForm(p));
    renderedPage = pageId;
    writeFields(displayedPageForm, pageFields); renderCoverage(); renderLines(); renderDraftStatus();
}
function selectLine(id) {
    captureDrafts(); lineId = id; pendingBox = null; renderLines(); renderDraftStatus();
}
function renderLines() {
    const ls = lines().sort((a, b) => a.reading_order - b.reading_order);
    $('count').textContent = ls.length + ' linhas · ' + ls.filter(l => l.review_status === 'validated').length + ' validadas';
    $('lineList').replaceChildren();
    for (const l of ls) {
        const b = document.createElement('button');
        b.textContent = (l.comparison_line ?? l.reading_order) + (l.review_status === 'validated' ? ' ✓' : l.review_status === 'rejected' ? ' ×' : '');
        b.classList.toggle('active', l.line_id === lineId); b.onclick = () => selectLine(l.line_id); $('lineList').append(b);
    }
    renderEditor(); renderOverlay();
}
function renderEditor() {
    const l = selected(); renderedLine = l?.line_id || null;
    $('editor').hidden = !l; $('noLines').hidden = !!l; if (!l) return;
    $('status').textContent = l.review_status === 'validated' ? 'Referência validada' : l.review_status === 'rejected' ? 'Rejeitada' : 'Revisão pendente';
    $('status').classList.toggle('valid', l.review_status === 'validated');
    $('crop').src = `/lines/${pageId}/${l.line_id}.png?v=${state.revision}`;
    writeFields(drafts.line.get(lineId)?.form || lineForm(l), lineFields);
    renderPublishedReference(l);
    pendingBox = drafts.line.has(lineId) ? box() : null;
    const pred = state.predictions.filter(p => p.line_id === lineId).at(-1);
    $('raw').textContent = pred ? (pred.presentation?.text || 'Leitura automática em português indisponível.') : 'Nenhum reconhecimento executado para esta linha.';
    $('predictionInfo').textContent = pred?.presentation?.message || '';
}
function renderPublishedReference(line) {
    const reference = line.published_reference;
    $('publishedPanel').hidden = !reference?.text;
    $('publishedText').value = reference?.text || '';
    $('assistedText').textContent = reference?.assisted_proposal || '';
    $('publishedInfo').textContent = reference
        ? `Páginas da edição: ${(reference.reference_pages || []).join(', ')}. ${reference.note || ''}` : '';
    $('publishedNotes').textContent = (reference?.human_observations || []).map(observation =>
        `${observation.original_message}\n${observation.scope || ''}\n${observation.effect || ''}`).join('\n\n');
    $('pageContextLink').href = `/api/pages/${line.page_id}/image`;
}
function setBox(b) { ['x1', 'y1', 'x2', 'y2'].forEach((id, i) => $(id).value = String(b[i])); }
function box() { return ['x1', 'y1', 'x2', 'y2'].map(id => Number($(id).value)); }
function numbers(value) {
    if (!value.trim()) return [];
    return value.split(',').map(v => {
        const n = Number(v.trim()); if (!v.trim() || !Number.isInteger(n)) throw Error('Use números inteiros separados por vírgula.'); return n;
    });
}
function buildPageChanges(form, p) {
    const values = {document_id: form.document, folio_id: form.folio, side: form.side, reviewer: form.pageReviewer || null,
        correspondence_status: form.pageValidated ? 'validated' : 'pending_review', source_url: form.sourceUrl || null, credits: form.credits || null};
    const changes = Object.fromEntries(Object.entries(values).filter(([key, value]) => !same(value, p[key])));
    if (!same(form.regions, pageForm(p).regions)) {
        changes.transcribed_coverage = form.regions.map(({original, values: f}) => {
            if (original && same(f, coverageForm(original))) return clone(original);
            const bounds = numbers(f.coverage);
            if (bounds.length !== 4) throw Error('Informe os quatro limites da região. Para excluir, use Remover região selecionada.');
            return {...original, region_id: regionId(f.coverageRegion), bbox_xyxy: bounds,
                reference_source: f.coverageSource || null, reference_pages: numbers(f.coveragePages),
                complete: f.complete, review_status: f.complete ? 'validated' : 'pending_review'};
        });
    }
    return changes;
}
function finishSave(kind, id, sentForm, saved) {
    captureDrafts();
    const draft = drafts[kind].get(id);
    if (!draft || same(draft.form, sentForm)) drafts[kind].delete(id);
    else draft.base = clone(saved); // Typing during a request remains a new local draft.
    if (kind === 'line' && renderedLine === id) renderedLine = null;
    if (kind === 'page' && renderedPage === id) renderedPage = null;
}
async function saveLine(reject = false) {
    captureDrafts(); const l = selected(); if (!l) throw Error('Selecione uma linha.');
    const id = l.line_id, draft = drafts.line.get(id), f = clone(draft?.form || lineForm(l));
    const validated = f.validated && !reject;
    const changes = {bbox_xyxy: ['x1', 'y1', 'x2', 'y2'].map(key => Number(f[key])), reading_order: Number(f.order),
        region_id: regionId(f.region), text_diplomatic: f.diplomatic || null, text_modernized: f.modernized || null,
        reference_kind: validated ? 'human_diplomatic' : l.reference_kind, review_status: reject ? 'rejected' : validated ? 'validated' : 'pending_review',
        geometry_status: f.geometryChecked ? 'validated' : 'pending_review', reviewer: f.reviewer || null,
        exclusion_reason: f.exclusion || null, reference_source: f.referenceSource || null, reference_pages: numbers(f.referencePages)};
    const saved = await request('/api/lines/' + id, 'PATCH', {changes, revision: draft?.revision || state.revision});
    finishSave('line', id, f, saved); pendingBox = null; await refresh();
    message('Revisão salva. Histórico e sugestões originais preservados.');
}
async function savePage() {
    captureDrafts(); const p = page(); if (!p) throw Error('Selecione um fólio.');
    const id = p.page_id, draft = drafts.page.get(id), form = clone(draft?.form || pageForm(p));
    const saved = await request('/api/pages/' + id, 'PATCH', {changes: buildPageChanges(form, p), revision: draft?.revision || state.revision});
    finishSave('page', id, form, saved); await refresh(); message('Identificação salva. Regiões e proveniência não editadas foram preservadas.');
}
$('coverageSelect').onchange = () => { captureDrafts(); activeRegions.set(pageId, Number($('coverageSelect').value)); renderCoverage(); };
$('addCoverage').onclick = () => {
    if (!page()) return; captureDrafts();
    const values = {...coverageForm(null), coverageRegion: 'regiao_' + (displayedPageForm.regions.length + 1)};
    displayedPageForm.regions.push({original: null, values});
    activeRegions.set(pageId, displayedPageForm.regions.length - 1);
    remember('page', pageId, displayedPageForm); renderCoverage(); renderDraftStatus();
};
$('removeCoverage').onclick = () => {
    if (!page()) return; captureDrafts();
    displayedPageForm.regions.splice(activeRegions.get(pageId) ?? 0, 1);
    remember('page', pageId, displayedPageForm); renderCoverage(); renderDraftStatus();
};
$('pages').onchange = () => { captureDrafts(); pageId = $('pages').value; lineId = null; renderedLine = null; pendingBox = null; renderPage(); };
$('refresh').onclick = () => action(refresh);
$('saveLine').onclick = () => action(() => saveLine());
$('rejectLine').onclick = () => action(() => saveLine(true));
$('savePage').onclick = () => action(savePage);
for (const id of [...lineFields, ...pageFields, ...coverageFields]) {
    $(id).addEventListener('input', captureDrafts);
    $(id).addEventListener('change', captureDrafts);
}
window.addEventListener('beforeunload', e => {
    captureDrafts();
    if (drafts.page.size || drafts.line.size) { e.preventDefault(); e.returnValue = ''; }
});
function setMode(value) { mode = value; $('mode').textContent = value === 'new' ? 'Desenhar nova linha' : value === 'edit' ? 'Ajustar selecionada' : 'Selecionar linha'; }
$('drawNew').onclick = () => setMode('new');
$('drawEdit').onclick = () => { if (!selected()) return message('Selecione uma linha.', true); setMode('edit'); };
function point(e) {
    const r = $('pageImage').getBoundingClientRect(), p = page();
    return [Math.max(0, Math.min(p.width, Math.round((e.clientX - r.left) * p.width / r.width))),
        Math.max(0, Math.min(p.height, Math.round((e.clientY - r.top) * p.height / r.height)))];
}
function renderOverlay() {
    const p = page(); if (!p) return;
    const svg = $('overlay'); svg.setAttribute('viewBox', `0 0 ${p.width} ${p.height}`); svg.replaceChildren();
    const boxes = lines().map(l => ({box: l.line_id === lineId && pendingBox ? pendingBox : l.bbox_xyxy,
        color: l.review_status === 'rejected' ? '#999' : l.line_id === lineId ? '#d3741e' : '#287455'}));
    if (drag?.box) boxes.push({box: drag.box, color: '#f80'});
    for (const {box: b, color} of boxes) {
        const r = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        for (const [key, value] of Object.entries({x: b[0], y: b[1], width: b[2] - b[0], height: b[3] - b[1],
            fill: '#e9ad451a', stroke: color, 'stroke-width': Math.max(2, p.width / 500)})) r.setAttribute(key, value);
        svg.append(r);
    }
}
$('viewer').onpointerdown = e => {
    if (!page()) return; const pos = point(e);
    if (mode === 'select') {
        const hit = lines().find(l => pos[0] >= l.bbox_xyxy[0] && pos[0] < l.bbox_xyxy[2] && pos[1] >= l.bbox_xyxy[1] && pos[1] < l.bbox_xyxy[3]);
        if (hit) selectLine(hit.line_id); return;
    }
    drag = {start: pos, box: [...pos, ...pos]}; $('viewer').setPointerCapture(e.pointerId);
};
$('viewer').onpointermove = e => {
    if (!drag) return; const p = point(e), s = drag.start;
    drag.box = [Math.min(s[0], p[0]), Math.min(s[1], p[1]), Math.max(s[0], p[0]), Math.max(s[1], p[1])]; renderOverlay();
};
$('viewer').onpointerup = () => {
    if (!drag) return; const b = drag.box; drag = null; if (b[2] - b[0] < 2 || b[3] - b[1] < 2) return;
    if (mode === 'edit') {
        pendingBox = b; setBox(b); $('geometryChecked').checked = false; $('validated').checked = false;
        captureDrafts(); renderOverlay(); message('Limites ajustados. Confira e salve a revisão.');
    } else action(async () => {
        captureDrafts(); const ls = lines();
        const added = await request(`/api/pages/${pageId}/lines`, 'POST', {bbox_xyxy: b,
            reading_order: ls.length ? Math.max(...ls.map(l => l.reading_order)) + 1 : 0, region_id: regionId($('coverageRegion').value) || 'page'});
        lineId = added.line_id; await refresh(); message('Linha criada como pendente.');
    });
    setMode('select');
};
$('uploadBtn').onclick = () => $('file').click();
$('file').onchange = () => action(async () => {
    if (!$('file').files.length) return; captureDrafts(); const f = new FormData(); f.append('file', $('file').files[0]);
    const p = await request('/api/pages', 'POST', f); pageId = p.page_id; lineId = null;
    await refresh(); message('Imagem importada. Identifique o fólio e detecte ou desenhe as linhas.');
});
$('segment').onclick = () => action(async () => {
    if (!page()) throw Error('Importe uma imagem.'); await request(`/api/pages/${pageId}/segment`, 'POST');
    await refresh(); message('Linhas detectadas. Confira os recortes antes de reconhecer.');
});
$('recognize').onclick = () => action(async () => {
    if (!page()) throw Error('Selecione um fólio.'); captureDrafts(); message('Executando diagnóstico do reconhecedor.');
    await request(`/api/pages/${pageId}/recognize`, 'POST'); await refresh();
    message(state.presentation_policy?.automatic_transcription_enabled ? 'Sugestões salvas. Confira cada palavra na imagem.'
        : 'Diagnóstico salvo. O modelo atual ainda não oferece uma leitura utilizável em português. Continue pela conferência da imagem e da edição.');
});
action(refresh);
