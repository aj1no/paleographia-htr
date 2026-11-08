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
