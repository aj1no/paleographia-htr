'use strict';
// Comparação de palavras do modo leitura: marca só o que o modelo leu diferente da leitura humana.
const test = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');

const html = fs.readFileSync(path.join(__dirname, '..', 'src', 'paleographia', 'web', 'leitura.html'), 'utf8');
// Aceita LF ou CRLF: o checkout no Windows grava as páginas com CRLF.
const source = html.match(/function differingWords[\s\S]*?\r?\n}\r?\n/)[0];
const differingWords = new Function(`${source}; return differingWords;`)();
const marked = (model, mine) => differingWords(model, mine).filter(w => w.differs).map(w => w.word);

test('marca as palavras coladas e o acento a mais do modelo', () => {
  assert.deepStrictEqual(marked('lando sobre obem commûm dopovo', 'lando sobre o bem commum do povo'), ['obem', 'commûm', 'dopovo']);
});

test('leituras iguais não marcam nada', () => {
  assert.deepStrictEqual(marked('torze Dias do mes', 'torze  Dias do mes'), []);
});

test('leitura humana vazia marca tudo e não quebra', () => {
  assert.deepStrictEqual(marked('Anno do', ''), ['Anno', 'do']);
  assert.deepStrictEqual(marked('', 'Anno'), []);
});

test('respeita a ordem: palavra repetida em outro lugar não conta como igual', () => {
  assert.deepStrictEqual(marked('de mil de', 'mil de seis'), ['de']);
});

// Filtros de visualização do recorte: só CSS, na ordem que mantém o negativo por último.
const filterSource = html.match(/function lensFilter[\s\S]*?\r?\n}\r?\n/)[0];
const lensFilter = new Function(`${filterSource}; return lensFilter;`)();
const base = {zoom: 1, contrast: 100, brightness: 100, invert: false, gray: false, threshold: false};

test('sem ajustes não aplica filtro', () => {
  assert.strictEqual(lensFilter(base), 'none');
});

test('contraste, brilho e negativo combinam na ordem certa', () => {
  assert.strictEqual(lensFilter({...base, contrast: 180, brightness: 90, invert: true}), 'contrast(180%) brightness(90%) invert(1)');
});

test('preto e branco passa por tons de cinza e pelo limiar, e o negativo vem depois', () => {
  assert.strictEqual(lensFilter({...base, threshold: true, invert: true}), 'grayscale(1) url(#limiar) invert(1)');
  assert.strictEqual(lensFilter({...base, gray: true, threshold: true}), 'grayscale(1) url(#limiar)');
});

// Foco na linha: a faixa de tinta é achada no perfil horizontal, preferindo o centro do recorte.
const bandSource = html.match(/function inkBand[\s\S]*?\r?\n}\r?\n/)[0];
const inkBand = new Function(`${bandSource}; return inkBand;`)();
const profile = (n, spans) => Array.from({length: n}, (_, y) => spans.reduce((s, [a, b, v]) => s + (y >= a && y < b ? v : 0), 0));

test('acha a faixa da linha central e deixa as vizinhas de fora', () => {
  // 100 linhas de pixels: descendentes da linha de cima (0-15), linha atual (40-60), ascendentes de baixo (88-100).
  const band = inkBand(profile(100, [[0, 15, 30], [40, 60, 80], [88, 100, 25]]));
  assert.ok(band.top > 0.2 && band.top < 0.4, `top ${band.top}`);
  assert.ok(band.bottom > 0.6 && band.bottom < 0.82, `bottom ${band.bottom}`);
});

test('um vizinho com um pouco mais de tinta na borda não rouba o foco do centro', () => {
  const band = inkBand(profile(100, [[0, 14, 95], [42, 58, 80]]));
  assert.ok(band.top > 0.25 && band.bottom < 0.8, JSON.stringify(band));
});

test('recorte sem tinta não aplica foco', () => {
  assert.strictEqual(inkBand(new Array(50).fill(0)), null);
  assert.strictEqual(inkBand([]), null);
});

test('linha vizinha cortada pela borda superior não vence a linha do meio (caso da linha 21 do 269r)', () => {
  const band = inkBand(profile(100, [[0, 24, 90], [40, 75, 70], [92, 100, 20]]));
  assert.ok(band.top > 0.2 && band.bottom > 0.7, JSON.stringify(band));
});

// Fila por discordância: distância de edição entre a leitura do modelo e a edição publicada.
const fnSource = name => html.match(new RegExp(String.raw`function ${name}[\s\S]*?\r?\n}\r?\n`))[0];
const discordance = new Function(`${fnSource('editDistance')}${fnSource('discordance')}; return discordance;`)();

test('discordância é a distância de edição sobre o tamanho da edição', () => {
  assert.strictEqual(discordance('lando sobre obem', 'lando sobre o bem'), 1 / 17);
  assert.strictEqual(discordance('torze Dias', 'torze Dias'), 0);
});

test('sem leitura do modelo ou sem edição não há discordância', () => {
  assert.strictEqual(discordance('', 'Anno'), null);
  assert.strictEqual(discordance('Anno', undefined), null);
});

test('conta caracteres combinados como letras, em NFC', () => {
  assert.strictEqual(discordance('Nossa', 'No\u0303ssa'.normalize('NFD')), 1 / 5);
});

// Aviso antes de validar: texto que parece nota do revisor, e não leitura do manuscrito.
const noteSource = html.match(/function looksLikeNote[\s\S]*?\r?\n}\r?\n/)[0];
const looksLikeNote = new Function(`${noteSource}; return looksLikeNote;`)();

test('reconhece notas do revisor no lugar da leitura', () => {
  for (const nota of ['não e possivele ler', 'Não é possível ler', 'ilegível', 'nao consigo ler', 'não dá pra ler', '???', '[...]', '…'])
    assert.strictEqual(looksLikeNote(nota), true, nota);
});

test('não confunde leituras de verdade com notas', () => {
  for (const leitura of ['Com', 'não', 'de o', 'Nosso mandado sendo primeiro', 'por nos assinado em seu cumpri', 'ou', ''])
    assert.strictEqual(looksLikeNote(leitura), false, leitura);
});

// Setas movem a imagem ampliada: 15% da área visível, 60% com Shift; outras teclas não movem.
const panSource = html.match(/function panDelta[\s\S]*?\r?\n}\r?\n/)[0];
const panDelta = new Function(`${panSource}; return panDelta;`)();

test('setas movem a imagem ampliada em passos proporcionais à área visível', () => {
  assert.deepStrictEqual(panDelta('ArrowRight', false, 600, 200), [90, 0]);
  assert.deepStrictEqual(panDelta('ArrowLeft', true, 600, 200), [-360, 0]);
  assert.deepStrictEqual(panDelta('ArrowDown', false, 600, 200), [0, 30]);
  assert.strictEqual(panDelta('Enter', false, 600, 200), null);
});

// Contexto: trecho da página com a linha atual e até k vizinhas da mesma região, com folga.
const contextSource = html.match(/function contextBox[\s\S]*?\r?\n}\r?\n/)[0];
const contextBox = new Function(`${contextSource}; return contextBox;`)();

test('contexto pega as vizinhas da mesma região, acima e abaixo separadas, e respeita a borda', () => {
  const linha = (y, region = 'page') => ({region_id: region, bbox_xyxy: [100, y, 900, y + 40]});
  const ls = [linha(0), linha(50), linha(100), linha(400, 'margem'), linha(150), linha(200)];
  assert.deepStrictEqual(contextBox(ls, 2, 1, 1, 1000, 1000), [88, 38, 912, 202]);   // 50 a 190, folga de 12
  assert.deepStrictEqual(contextBox(ls, 2, 2, 0, 1000, 1000), [88, 0, 912, 152]);    // só acima, sem passar do topo
  assert.deepStrictEqual(contextBox(ls, 2, 0, 3, 1000, 1000), [88, 88, 912, 252]);   // só abaixo, pulando a margem
  assert.deepStrictEqual(contextBox(ls, 3, 3, 3, 1000, 1000), [88, 388, 912, 452]);  // margem: só ela
  assert.strictEqual(contextBox(ls, 2, 0, 0, 1000, 1000), null);
});
