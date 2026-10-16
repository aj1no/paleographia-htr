// DOM simulado, sem dependências. Executa o mesmo JavaScript servido ao navegador.
const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const web = path.join(__dirname, '../src/paleographia/web');
const source = fs.readFileSync(process.env.REVIEW_SCRIPT || path.join(web, 'review.js'), 'utf8');
const copy = x => JSON.parse(JSON.stringify(x));

class Element {
    constructor() { this.value = ''; this.checked = false; this.hidden = false; this.children = []; this.listeners = {}; this.disabled = false; }
    classList = {toggle() {}};
    append(child) { this.children.push(child); }
    replaceChildren() { this.children = []; }
    setAttribute(name, value) { this[name] = value; }
    addEventListener(name, callback) { this.listeners[name] = callback; }
    setPointerCapture() {}
}
function fixture(count = 2) {
    const regions = Array.from({length: count}, (_, i) => ({region_id: i ? 'margin' : 'body',
        bbox_xyxy: [0, i * 100, 600, (i + 1) * 100], reference_source: 'edicao.pdf', reference_pages: [i + 1],
        complete: true, review_status: 'validated', reviewer: 'Revisor anterior', reviewed_at: '2026-10-14T12:00:00Z',
        provenance: {note: 'manter integralmente'}}));
    const p = {page_id: 'p1', document_id: 'doc', folio_id: '100r', side: 'recto', reviewer: 'Revisor da página',
        correspondence_status: 'validated', credits: 'Créditos salvos', source_url: null, original_name: 'Sintético.png',
        width: 600, height: 300, transcribed_coverage: regions};
    const l = {page_id: 'p1', line_id: 'l1', reading_order: 1, region_id: 'body', bbox_xyxy: [10, 20, 500, 40],
        text_diplomatic: 'Texto salvo', text_modernized: '', review_status: 'pending_review', geometry_status: 'pending_review',
        reference_kind: 'unknown', reviewer: null, reference_source: null, reference_pages: [], exclusion_reason: null};
    return {revision: 'r1', pages: [p, {...copy(p), page_id: 'p2', folio_id: '100v'}],
        lines: [l, {...copy(l), line_id: 'l2', reading_order: 2}, {...copy(l), line_id: 'l3', page_id: 'p2'}],
        predictions: [], presentation_policy: {automatic_transcription_enabled: false}};
}
async function harness(count = 2, configure = () => {}) {
    let catalog = fixture(count), fail = null, revision = 1;
    configure(catalog);
    const elements = Object.fromEntries([...fs.readFileSync(path.join(web, 'index.html'), 'utf8').matchAll(/id="([^"]+)"/g)].map(m => [m[1], new Element()]));
    const buttonIds = [...fs.readFileSync(path.join(web, 'index.html'), 'utf8').matchAll(/<button\b[^>]*id="([^"]+)"/g)].map(m => m[1]);
    const calls = [], windowEvents = {};
    const context = vm.createContext({document: {
        getElementById: id => { assert.ok(elements[id], `Elemento ${id} ausente`); return elements[id]; },
        querySelectorAll: selector => selector === 'button' ? buttonIds.map(id => elements[id]) : [], createElement: () => new Element(), createElementNS: () => new Element()},
        window: {addEventListener: (event, callback) => windowEvents[event] = callback}, FormData, console,
        fetch: async (url, options) => {
            const method = options?.method || 'GET', body = options?.body ? JSON.parse(options.body) : null;
            calls.push({url, method, body});
            if (method === 'PATCH' && fail) {
                if (fail === 'network') throw new TypeError('rede indisponível');
                return {ok: false, status: fail, json: async () => ({detail: fail === 409 ? 'A revisão mudou.' : 'Valores inválidos.'})};
            }
            let result;
            if (url === '/api/catalog') result = catalog;
            else if (url === '/health') result = {recognition: {state: catalog.testRecognitionState || 'test_only'}};
            else if (method === 'PATCH') {
                if (body.revision !== catalog.revision) return {ok: false, status: 409, json: async () => ({detail: 'A revisão mudou.'})};
                const kind = url.includes('/lines/') ? 'line' : 'page';
                const record = catalog[kind === 'line' ? 'lines' : 'pages'].find(r => r[kind + '_id'] === url.split('/').at(-1));
                Object.assign(record, body.changes); catalog.revision = 'r' + (++revision); result = record;
            } else if (url.endsWith('/recognize')) { catalog.revision = 'r' + (++revision); result = []; }
            else throw Error('Rota inesperada: ' + url);
            return {ok: true, status: 200, json: async () => copy(result)};
        }});
    vm.runInContext(source, context);
    await new Promise(resolve => setImmediate(resolve));
    return {el: elements, calls, windowEvents,
        catalog: () => copy(catalog), fail: value => fail = value,
        externalEdit: fn => { fn(catalog); catalog.revision = 'r' + (++revision); },
        edit: (id, value) => {
            if (typeof value === 'boolean') elements[id].checked = value; else elements[id].value = String(value);
            elements[id].listeners.input?.();
        },
        click: async id => { assert.equal(typeof elements[id].onclick, 'function', id + ' precisa ter ação'); await elements[id].onclick(); },
        line: async index => elements.lineList.children[index].onclick(),
        page: async id => { elements.pages.value = id; await elements.pages.onchange(); },
        region: async index => { elements.coverageSelect.value = String(index); await elements.coverageSelect.onchange(); }};
}
const patches = h => h.calls.filter(c => c.method === 'PATCH');

test('Transcrição publicada fica separada do texto humano e preserva intervenções editoriais', async () => {
    const published = {kind: 'published_paleographic_transcription', text: 'torze dias da dita Hera',
        assisted_proposal: 'torze Dias da dita Hera', reference_pages: [1],
        human_observations: [{original_message: 'Vejo Dias', scope: 'Confirmação parcial.', effect: 'Linha pendente.'}]};
    const h = await harness(2, catalog => {
        catalog.lines[0].published_reference = published;
        catalog.lines[0].text_diplomatic = null;
    });
    await h.line(0);
    assert.equal(h.el.publishedPanel.hidden, false);
    assert.equal(h.el.publishedText.value, published.text);
    assert.equal(h.el.assistedText.textContent, published.assisted_proposal);
    assert.match(h.el.publishedNotes.textContent, /Confirmação parcial/);
    assert.equal(h.el.pageContextLink.href, '/api/pages/p1/image');
    assert.equal(h.el.diplomatic.value, ''); assert.equal(h.el.modernized.value, '');
    assert.equal(h.el.validated.checked, false); assert.equal(h.el.geometryChecked.checked, false);
    h.edit('diplomatic', 'Rascunho humano'); await h.click('saveLine');
    assert.equal(patches(h)[0].body.changes.reference_kind, 'unknown');
    assert.equal(patches(h)[0].body.changes.review_status, 'pending_review');
    assert.deepEqual(h.catalog().lines[0].published_reference, published);
    await h.line(1); assert.equal(h.el.publishedPanel.hidden, true);
});

test('Apoio modernizado legado continua editável e não recebe classificação nova', async () => {
    const h = await harness(2, catalog => {
        catalog.lines[0].text_modernized = 'Texto da edição modernizada';
        catalog.lines[0].reference_kind = 'modernized_edition';
    });
    await h.line(0);
    assert.equal(h.el.publishedPanel.hidden, true);
    assert.equal(h.el.modernized.value, 'Texto da edição modernizada');
    h.edit('diplomatic', 'Rascunho'); await h.click('saveLine');
    assert.equal(patches(h)[0].body.changes.reference_kind, 'modernized_edition');
});

for (const count of [0, 1, 2]) test(`Créditos preservam as ${count} regiões sem reconstruir a cobertura`, async () => {
    const h = await harness(count), original = h.catalog().pages[0].transcribed_coverage;
    h.edit('credits', 'Novos créditos'); await h.click('savePage');
    assert.equal(patches(h).length, 1);
    assert.equal('transcribed_coverage' in patches(h)[0].body.changes, false);
    assert.deepEqual(h.catalog().pages[0].transcribed_coverage, original);
    assert.equal(h.el.draftStatus.textContent, 'Sem alterações locais pendentes.');
});
test('Editar a segunda região preserva a primeira e os campos adicionais', async () => {
    const h = await harness(), original = h.catalog().pages[0].transcribed_coverage;
    await h.region(1); h.edit('coverage', '1, 100, 599, 200'); await h.click('savePage');
    const regions = patches(h)[0].body.changes.transcribed_coverage;
    assert.equal(regions.length, 2); assert.deepEqual(regions[0], original[0]);
    assert.deepEqual(regions[1].bbox_xyxy, [1, 100, 599, 200]);
    assert.deepEqual(regions[1].provenance, original[1].provenance);
    assert.deepEqual(h.catalog().pages[0].transcribed_coverage, regions);
});
test('Apagar os limites não remove região; exige remoção explícita', async () => {
    const h = await harness(); h.edit('coverage', ''); await h.click('savePage');
    assert.equal(patches(h).length, 0); assert.equal(h.el.coverage.value, '');
    assert.match(h.el.message.textContent, /quatro limites/);
    await h.click('removeCoverage'); await h.click('savePage');
    assert.deepEqual(h.catalog().pages[0].transcribed_coverage.map(c => c.region_id), ['margin']);
});
test('Página sem região permite adicionar uma cobertura explicitamente', async () => {
    const h = await harness(0); await h.click('addCoverage'); h.edit('coverage', '0, 0, 600, 100');
    await h.click('savePage'); assert.equal(h.catalog().pages[0].transcribed_coverage.length, 1);
});
test('Clicar na mesma linha e alternar linhas preserva todos os campos locais', async () => {
    const h = await harness(); await h.line(0);
    const fields = {diplomatic: 'Texto ainda não salvo', modernized: 'Apoio', order: '9', region: 'outra',
        x1: '15', y1: '21', x2: '490', y2: '45', reviewer: 'Pessoa', validated: true,
        geometryChecked: true, exclusion: 'Conferir', referenceSource: 'edicao.pdf', referencePages: '2, 3'};
    for (const [id, value] of Object.entries(fields)) h.edit(id, value);
    await h.line(0); await h.line(1); h.edit('diplomatic', 'Outro rascunho'); await h.line(0);
    for (const [id, value] of Object.entries(fields)) assert.equal(typeof value === 'boolean' ? h.el[id].checked : h.el[id].value, value, id);
    assert.equal(h.catalog().lines[0].text_diplomatic, 'Texto salvo');
    assert.equal(h.catalog().lines[0].review_status, 'pending_review');
    assert.equal(patches(h).length, 0);
});
test('Trocar fólios, atualizar catálogo e diagnosticar preserva linha e identificação', async () => {
    const h = await harness(); await h.line(0); h.edit('diplomatic', 'Minha leitura'); h.edit('x1', '12');
    h.edit('document', 'Documento local'); h.edit('credits', 'Créditos locais');
    await h.region(1); h.edit('coveragePages', '3, 4'); await h.region(0);
    await h.page('p2'); await h.page('p1'); await h.line(0);
    await h.click('refresh'); await h.click('recognize');
    assert.equal(h.el.diplomatic.value, 'Minha leitura'); assert.equal(h.el.x1.value, '12');
    assert.equal(h.el.document.value, 'Documento local'); assert.equal(h.el.credits.value, 'Créditos locais');
    await h.region(1); assert.equal(h.el.coveragePages.value, '3, 4'); assert.equal(patches(h).length, 0);
});
test('Salvar uma linha limpa somente seu rascunho; salvar página mantém as outras linhas', async () => {
    const h = await harness(); await h.line(0); h.edit('diplomatic', 'Salvar primeira');
    await h.line(1); h.edit('diplomatic', 'Manter segunda'); h.edit('credits', 'Página local');
    await h.line(0); await h.click('saveLine'); assert.equal(h.catalog().lines[0].text_diplomatic, 'Salvar primeira');
    await h.line(1); assert.equal(h.el.diplomatic.value, 'Manter segunda');
    await h.click('savePage'); assert.equal(h.el.diplomatic.value, 'Manter segunda');
    assert.match(h.el.draftStatus.textContent, /^1 rascunho/);
});
for (const error of [409, 422, 'network']) test(`Falha ${error} preserva o conteúdo e não declara salvamento`, async () => {
    const h = await harness(); await h.line(0); h.edit('diplomatic', 'Recuperar edição'); h.edit('credits', 'Recuperar página');
    h.fail(error); await h.click('saveLine'); await h.click('savePage');
    assert.equal(h.el.diplomatic.value, 'Recuperar edição'); assert.equal(h.el.credits.value, 'Recuperar página');
    assert.equal(h.catalog().lines[0].text_diplomatic, 'Texto salvo');
    if (error === 409) assert.match(h.el.message.textContent, /Conflito/);
    assert.doesNotMatch(h.el.message.textContent, /Revisão salva|Identificação salva/);
});
for (const kind of ['linha', 'página']) test(`Conflito real de ${kind} exige conferência antes de trocar a revisão base`, async () => {
    const h = await harness(); await h.line(0);
    h.edit(kind === 'linha' ? 'diplomatic' : 'credits', 'Rascunho local');
    h.externalEdit(c => { if (kind === 'linha') c.lines[0].text_diplomatic = 'Outra revisão'; else c.pages[0].credits = 'Outra revisão'; });
    await h.click('refresh');
    assert.equal(h.el.conflictPanel.hidden, false); assert.match(h.el.conflictVersion.textContent, /Outra revisão/);
    await h.click(kind === 'linha' ? 'saveLine' : 'savePage'); assert.equal(patches(h).at(-1).body.revision, 'r1');
    assert.match(h.el.message.textContent, /Conflito/);
    await h.click('rebaseDraft'); await h.click(kind === 'linha' ? 'saveLine' : 'savePage');
    assert.equal(kind === 'linha' ? h.catalog().lines[0].text_diplomatic : h.catalog().pages[0].credits, 'Rascunho local');
});
test('Conferir conflito da página preserva regiões e campos remotos não editados localmente', async () => {
    const h = await harness(); h.edit('credits', 'Meus créditos');
    h.externalEdit(c => { c.pages[0].source_url = 'https://fonte.example/edicao';
        c.pages[0].transcribed_coverage[1].bbox_xyxy = [1, 100, 590, 200];
        c.pages[0].transcribed_coverage[1].reviewer = 'Outro revisor'; });
    await h.click('refresh'); await h.click('rebaseDraft'); await h.click('savePage');
    const saved = h.catalog().pages[0];
    assert.equal(saved.credits, 'Meus créditos'); assert.equal(saved.source_url, 'https://fonte.example/edicao');
    assert.deepEqual(saved.transcribed_coverage[1].bbox_xyxy, [1, 100, 590, 200]);
    assert.equal(saved.transcribed_coverage[1].reviewer, 'Outro revisor');
    assert.equal('transcribed_coverage' in patches(h)[0].body.changes, false);
});
test('Proteção ao sair só aparece quando há alterações locais', async () => {
    const h = await harness(); let prevented = false;
    h.windowEvents.beforeunload({preventDefault() { prevented = true; }}); assert.equal(prevented, false);
    await h.line(0); h.edit('diplomatic', 'Ainda local');
    h.windowEvents.beforeunload({preventDefault() { prevented = true; }}); assert.equal(prevented, true);
    await h.click('saveLine'); prevented = false;
    h.windowEvents.beforeunload({preventDefault() { prevented = true; }}); assert.equal(prevented, false);
});

test('Backend desativado continua bloqueado depois de atualizar ou salvar', async () => {
    const h = await harness(2, catalog => { catalog.testRecognitionState = 'disabled'; });
    assert.equal(h.el.recognize.disabled, true);
    assert.match(h.el.health.textContent, /Reconhecimento desativado/);
    await h.click('refresh');
    assert.equal(h.el.recognize.disabled, true);
    await h.line(0); h.edit('diplomatic', 'Revisão manual'); await h.click('saveLine');
    assert.equal(h.el.recognize.disabled, true);
    assert.equal(h.catalog().lines[0].text_diplomatic, 'Revisão manual');
});

test('Sugestão experimental e reconhecimento preservam o rascunho humano', async () => {
    const h = await harness(2, catalog => {
        catalog.testRecognitionState = 'ready';
        catalog.presentation_policy.automatic_transcription_enabled = true;
        catalog.predictions = [{line_id: 'l1', presentation: {status: 'candidate', text: 'SAÍDA SINTÉTICA', message: 'Experimental'}}];
    });
    await h.line(0);
    assert.equal(h.el.raw.textContent, 'SAÍDA SINTÉTICA');
    assert.match(h.el.health.textContent, /PP-OCRv6 experimental/);
    h.edit('diplomatic', 'Meu rascunho'); await h.click('recognize');
    assert.equal(h.el.diplomatic.value, 'Meu rascunho');
    assert.equal(h.catalog().lines[0].text_diplomatic, 'Texto salvo');
    assert.equal(h.el.validated.checked, false);
});
