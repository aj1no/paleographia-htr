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
