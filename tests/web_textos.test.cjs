'use strict';
// Aba Textos: corte do texto nos trechos marcados como palavras a conferir.
const test = require('node:test');
const assert = require('node:assert');
const fs = require('node:fs');
const path = require('node:path');

const html = fs.readFileSync(path.join(__dirname, '..', 'src', 'paleographia', 'web', 'textos.html'), 'utf8');
const source = html.match(/function pieces[\s\S]*?\r?\n}\r?\n/)[0];
const pieces = new Function(`${source}; return pieces;`)();

test('corta o texto nas marcas, com a linha de origem', () => {
  assert.deepStrictEqual(pieces('aos batecins. Pentiado', [[4, 12, 'duvida', 6], [14, 22, 'nome', 18]]), [
    {texto: 'aos ', tipo: null}, {texto: 'batecins', tipo: 'duvida', linha: 6},
    {texto: '. ', tipo: null}, {texto: 'Pentiado', tipo: 'nome', linha: 18}]);
});

test('sem marcas devolve o texto inteiro; marca fora do texto é ignorada', () => {
  assert.deepStrictEqual(pieces('Anno do', []), [{texto: 'Anno do', tipo: null}]);
  assert.deepStrictEqual(pieces('Anno', [[2, 9, 'duvida']]), [{texto: 'Anno', tipo: null}]);
  assert.deepStrictEqual(pieces('', undefined), [{texto: '', tipo: null}]);
});

test('marca sem número de linha (lado a lado) fica com linha nula', () => {
  assert.deepStrictEqual(pieces('madico', [[0, 6, 'duvida']]), [{texto: 'madico', tipo: 'duvida', linha: null}]);
});

test('número da nota entra logo depois da palavra, também numa palavra marcada', () => {
  assert.deepStrictEqual(pieces('em magotes e aos batecins.', [[17, 25, 'duvida', 6]], [[3, 10, 1], [17, 25, 2]]), [
    {texto: 'em magotes', tipo: null}, {nota: 1}, {texto: ' e aos ', tipo: null},
    {texto: 'batecins', tipo: 'duvida', linha: 6}, {nota: 2}, {texto: '.', tipo: null}]);
  assert.deepStrictEqual(pieces('rocio', [], [[0, 5, 3]]), [{texto: 'rocio', tipo: null}, {nota: 3}]);
});
