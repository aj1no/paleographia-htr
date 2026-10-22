"""Gera a leitura do diagnóstico a partir dos artefatos, sem inferência."""
import argparse
import html
import json
from pathlib import Path


def read(path):
    return json.loads(path.read_bytes())


def rows(path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]


def pct(value):
    return f'{100*value:.2f}%'.replace('.', ',')


def generate(base):
    require_new = [base/'relatorio.md', base/'relatorio.html']
    assert not any(p.exists() for p in require_new), 'Relatório existente; preserve a versão anterior.'
    result = read(base/'comparacao.json')
    areas = rows(base/'por_area.jsonl')
    predictions = rows(base/'ppocrv6/predictions.jsonl')
    targets = rows(base/'alvos_editoriais.jsonl')
    labels = {'cabecalho': 'Cabeçalho e foliação', 'titulo': 'Título', 'resumo': 'Resumo', 'corpo': 'Corpo'}
    all_rows = [('Página completa', result['metrics']), *[(labels[g['area']], g['metrics']) for g in areas]]
    table = ['| Área | CER | Erros/caracteres | WER | Erros/palavras |', '| --- | ---: | ---: | ---: | ---: |']
    for name, metrics in all_rows:
        c, w = metrics['characters'], metrics['words']
        table.append(f"| {name} | {pct(c['rate'])} | {c['errors']}/{c['reference_length']} | {pct(w['rate'])} | {w['errors']}/{w['reference_length']} |")
    empty = [p['reading_order'] for p in predictions if not p['text_raw'].strip()]
    source_examples = [
        ('Cabeçalho completo', ' '.join(t['texto_alvo'] for t in targets if t['area'] == 'cabecalho'), predictions[1]['text_raw']),
        ('Título, primeira linha', next(t['texto_alvo'] for t in targets if t['area'] == 'titulo'), predictions[2]['text_raw']),
        ('Corpo, linha 1', next(t['texto_alvo'] for t in targets if t['area'] == 'corpo'), predictions[10]['text_raw']),
        ('Corpo, linha 14', [t['texto_alvo'] for t in targets if t['area'] == 'corpo'][13], predictions[23]['text_raw']),
        ('Corpo, linha 18', [t['texto_alvo'] for t in targets if t['area'] == 'corpo'][17], predictions[27]['text_raw']),
        ('Corpo, linha 24', [t['texto_alvo'] for t in targets if t['area'] == 'corpo'][23], predictions[33]['text_raw']),
    ]
    markdown = '''# Fólio 269 reto inteiro — comparação automática com a edição

**Diagnóstico de desenvolvimento.** Referência editorial publicada, sem nova
conferência humana do texto, treinamento ou teste reservado. Reconhecedor:
**PP-OCRv6 medium/Kraken**, com os pesos, a imagem Docker e a configuração já existentes.

## Resultado principal

'''+ '\n'.join(table) + f'''

A página completa é uma única sequência para o cálculo principal. As áreas
são diagnósticos separados; suas taxas não foram usadas para fazer média.
O teste gerou **{result['recortes_automaticos']} recortes automáticos**, comparados a
**36 unidades da edição**: três elementos do cabeçalho/foliação, duas linhas do
título, sete do resumo e 24 do corpo. Essas 36 unidades não equivalem a 36 linhas
físicas do manuscrito: os três elementos do cabeçalho compartilham a faixa superior.

Houve **{result['falhas']} falhas técnicas** e **{len(empty)} saídas vazias**, nas ordens
{', '.join(map(str, empty))} (ordens iniciadas em zero). As faixas 0 e 34 são bordas
da imagem; a ordem 4 contém a primeira linha do resumo e também retornou vazia.
Esses recortes não foram removidos ou reconhecidos novamente.

## Principais erros e diferenças de representação

- **Resumo:** seis recortes automáticos para sete linhas da edição, com extensa
  perda de conteúdo. A caixa `[70, 473, 1096, 550]` reúne as duas últimas linhas
  visíveis desse bloco. A primeira linha do resumo retornou vazia. As causas
  de cada omissão não foram isoladas entre recorte, escala e reconhecimento.
- **Título e cabeçalho:** palavras omitidas e abreviadas pela saída automática;
  `Villa` desaparece no cabeçalho. As margens fixas de 70 pixels à esquerda e
  70 à direita limitam os recortes; não foram ajustadas para melhorar a taxa.
- **Corpo:** junções e separações de palavras, trocas de letras, caixa, acentos
  e pontuação. Exemplos incluem `Anno do`/`Annodo`, `Jundiahy`/`Sundialg` e
  `deligençias`/`de Ligencias`.
- **Edição e abreviaturas:** o alvo final é `Magestade`, conforme a edição;
  a forma abreviada `Magᵈᵉ` permanece na revisão humana anterior. O erro medido
  inclui essa diferença de convenção. Grafias, espaços e quebras editoriais,
  como `Se / nhora`, também fazem parte deste alvo.

## Exemplos completos

| Local | Edição oficial | Saída bruta |
| --- | --- | --- |
'''
    for place, ref, pred in source_examples:
        markdown += f'| {place} | {ref} | {pred} |\n'
    markdown += '''
Os exemplos do corpo têm correspondência geométrica inspecionada pelo assistente
para apresentação, sem alterar as previsões ou promover uma leitura a validada.
A versão normalizada usada nas contas aplica somente NFC e colapso de espaços;
o JSON e o texto bruto conservam os caracteres realmente emitidos.

## Cobertura e protocolo

Foram selecionados os trechos do reto nas páginas 1 e 2 do PDF, encerrando antes
de `269/Verso.`. Metadados e créditos da edição foram excluídos por não fazerem
parte da imagem manuscrita. A fonte foi extraída e renderizada para conferir
a cobertura. A ordem espacial do cabeçalho foi fixada antes da inferência:
`Villa de Jundiahy`, `Anno de 1767`, `269`; o PDF dispõe esses campos em outra
sequência vertical. Nenhuma palavra foi substituída por interpretação posterior.

O detector OpenCV por projeção recebeu a imagem inteira, com os parâmetros já
existentes. Não foram usados os 24 recortes humanos nem as cinco regiões
revisadas. Todos os recortes foram enviados ao PP-OCRv6, apenas como imagem,
sem os textos da edição. Falhas e saídas vazias permanecem na comparação.
As áreas diagnósticas foram delimitadas antes da execução por faixas verticais
e associadas pelo centro das caixas; limites cruzados ficam registrados no JSON.

CER/WER usam NFC, colapso de espaços, caixa e diacríticos preservados; somam
substituições, deleções e inserções contra 1.450 caracteres e 262 palavras no
reto completo. Essas taxas não são porcentagens simples de acerto.

## Preservação e interpretação

O reconhecimento bruto, os recortes, os alvos editoriais e os parâmetros ficam
arquivados nesta pasta. Os workspaces e os arquivos anteriores foram conferidos
por hash antes e depois da execução, sem alterações. Permanecem os pacotes
de 20/10 e 22/10, as oito ressalvas históricas e as confirmações humanas anteriores.
Nenhum peso foi alterado, nenhum treinamento foi executado e nenhum estado
humano foi promovido.

Este teste **mede o fluxo de segmentação e reconhecimento contra a edição**.
Difere do experimento de 24 recortes humanos com referência assistida e
agregação em cinco blocos; a diferença de CER/WER não demonstra isoladamente
melhora ou piora do reconhecedor. O 269r já é documento de desenvolvimento;
o resultado não mede generalização para outro documento.

## Arquivos para conferir

- [Saída bruta completa](transcricao_bruta.txt), [JSON original](ppocrv6/predictions.jsonl).
- [Texto da edição adotado](texto_oficial.txt), [proveniência de cada unidade](alvos_editoriais.jsonl).
- [Imagem com os recortes automáticos](segmentacao/p_traslado_269r_overlay.png).
- [Métricas](comparacao.json), [tabela por área](por_area.csv), [alinhamentos de erros](erros_palavras.jsonl).
- [Protocolo congelado](protocolo.json), [identidade da execução](ppocrv6/proveniencia.json).
- [Auditoria](validacao.json), [preservação](preservacao_depois.json), [inventário](inventario.json).
'''
    (base/'relatorio.md').write_text(markdown, encoding='utf-8', newline='\n')
    esc = lambda value: html.escape(str(value))
    metric_rows = ''.join('<tr><td>'+esc(name)+'</td><td>'+pct(m['characters']['rate'])+'</td><td>'
                          +pct(m['words']['rate'])+'</td></tr>' for name, m in all_rows)
    details = ''
    for name, _, _ in [('cabecalho', 0, 130), ('titulo', 130, 240), ('resumo', 240, 550), ('corpo', 550, 1873)]:
        area = next(g for g in areas if g['area'] == name)
        details += '<section><h2>'+esc(labels[name])+'</h2><div class="colunas"><div><h3>Edição oficial</h3><pre>'
        details += esc('\n'.join(t['texto_alvo'] for t in targets if t['area'] == name))+'</pre></div><div><h3>Saída bruta</h3><pre>'
        details += esc(area['predicao_bruta'])+'</pre></div></div></section>'
    prediction_rows = ''.join('<tr><td>'+str(p['reading_order'])+'</td><td>'+esc(p['bbox_xyxy'])+'</td><td>'
                              +esc(p['text_raw'])+'</td></tr>' for p in predictions)
    body = '''<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>269 reto — diagnóstico integral contra a edição</title>
<style>body{font:16px/1.65 system-ui,sans-serif;color:#253943;max-width:1120px;margin:36px auto;padding:0 24px;background:#fcfbf8}h1,h2{color:#184657;line-height:1.3}table{width:100%;border-collapse:collapse;background:white}th,td{text-align:left;padding:10px;border-bottom:1px solid #d9dfe1;vertical-align:top}th{background:#e9eff0}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:15px/1.7 Georgia,serif;background:#fff;padding:18px;border:1px solid #e0ded7}.colunas{display:grid;grid-template-columns:1fr 1fr;gap:20px}section{margin:32px 0}.aviso{padding:18px;background:#f2ead8;border-left:4px solid #9c7b3f}img{max-width:100%;height:auto}a{color:#086680}@media(max-width:700px){.colunas{grid-template-columns:1fr}td{overflow-wrap:anywhere}}</style>
<h1>Fólio 269 reto inteiro</h1><p>PP-OCRv6 medium/Kraken · edição publicada · 22/10/2026</p>
<p class="aviso"><strong>Diagnóstico de desenvolvimento.</strong> Segmentação automática na imagem inteira; 35 recortes; 36 unidades editoriais; zero falhas técnicas e três saídas vazias. Referência assistida pela edição, sem nova conferência humana, treinamento ou avaliação reservada. As revisões anteriores permanecem intactas.</p>
<table><thead><tr><th>Área</th><th>CER</th><th>WER</th></tr></thead><tbody>'''+metric_rows+'''</tbody></table>
<p>Taxa principal sobre uma única sequência do reto: 391/1.450 operações em caracteres e 158/262 em palavras. As áreas são diagnósticas, sem média de taxas. Caixa, grafia, acentos, pontuação e expansões editoriais foram preservados.</p>
<p>O resumo teve a maior perda de conteúdo. O detector juntou duas linhas, e a primeira retornou vazia. A atribuição de cada erro à segmentação ou ao reconhecedor não foi isolada. O alvo Magestade segue a edição, enquanto a revisão anterior conserva Magᵈᵉ. Este resultado não é diretamente comparável à medição anterior com recortes humanos.</p>
<p><a href="relatorio.md">Relatório completo e limites</a> · <a href="transcricao_bruta.txt">Texto bruto</a> · <a href="texto_oficial.txt">Texto oficial</a> · <a href="por_area.csv">CSV</a> · <a href="validacao.json">Auditoria</a></p>
'''+details+'''<h2>Recortes automáticos</h2><p>Ordens iniciadas em zero. As faixas de borda foram mantidas, assim como o recorte vazio do resumo.</p><img src="segmentacao/p_traslado_269r_overlay.png" alt="Imagem integral com os 35 recortes automáticos numerados">
<h2>Todas as saídas brutas</h2><table><thead><tr><th>Ordem</th><th>Caixa</th><th>Texto emitido</th></tr></thead><tbody>'''+prediction_rows+'</tbody></table></html>'
    (base/'relatorio.html').write_text(body, encoding='utf-8', newline='\n')
    print(json.dumps({'relatorios': ['relatorio.md', 'relatorio.html'], 'novas_inferencias': 0}))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-root', default='docs/experimentos/traslado_269r_integral_edicao_20261022')
    generate(Path(parser.parse_args().output_root).resolve())
