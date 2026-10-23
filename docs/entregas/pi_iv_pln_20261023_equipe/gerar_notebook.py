"""Cria uma versão colaborativa aditiva, sem alterar os notebooks históricos."""
from pathlib import Path
import hashlib
import json

import nbformat as nbf

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
ORIGINAL = ROOT / 'docs/entregas/pi_iv_pln_20261022/comparacao_reproduzivel.ipynb'


def md(text, ident):
    return nbf.v4.new_markdown_cell(text.strip(), id=ident)


def code(text, ident):
    return nbf.v4.new_code_cell(text.strip(), id=ident)


def main():
    notebook = nbf.read(ORIGINAL, as_version=4)
    for cell in notebook.cells:
        if cell.cell_type == 'code':
            cell.source = cell.source.replace('output/entrega_academica_269r24_20261022',
                                              'output/equipe_20261023/calculos')
            cell.outputs = []
            cell.execution_count = None
    notebook.cells[0].source = '''# PaleographIA — diagnóstico reproduzível e participação da equipe

**24 linhas do 269r; dois reconhecedores; referência assistida e oito ressalvas.**

Equipe: Caio Augusto de Souza Soares; Guilherme Rodrigues Veiga;
Rodolfo Vinicius Cima Takemoto; Tiago Galhardo Avelar.
FATEC Jundiaí, Ciência de Dados, 5º semestre, Jundiaí – SP.

## Como trabalhar em equipe neste notebook

1. Execute a parte comum para reproduzir e compreender o diagnóstico.
2. Vá à seção **Participação individual** e faça a atividade da sua frente.
3. Preencha seu formulário com o que você realmente discutiu, analisou ou revisou.
   Inclua a data real, a evidência e o uso de IA. Participação em discussão
   também pode ser registrada: explique a sua contribuição concreta.
4. Execute sua célula. Um formulário vazio não cria registro. Um preenchido
   gera um novo JSON em `output/participacao_equipe_20261023/`, para conferência.
5. Compartilhe esse JSON e as observações com a equipe. A execução do notebook
   por outra pessoa ou por IA não comprova sua participação individual.

**Situação relatada pelo solicitante em 23/10:** a equipe discutiu o projeto,
mas a execução prática está concentrada nele. Esse relato coletivo
não identifica retrospectivamente a tarefa feita por cada colega. A divisão do
artigo inicial é **planejamento**, adaptado abaixo ao experimento atual.

| Integrante | Frente prevista/adaptada | Registro novo nesta versão |
| --- | --- | --- |
| Caio | Bibliografia e interpretação das fontes | A preencher pelo participante |
| Guilherme | Modelos, ambiente e condições da comparação | A preencher pelo participante |
| Tiago | Inventário, associação imagem–texto e inspeção de erros | A preencher pelo participante |
| Rodolfo | Coordenação, dados e consolidação | A preencher; histórico de revisão do manuscrito preservado |

O [roteiro e cronograma](roteiro_equipe.md) organiza a rodada. A seção histórica
de reconferência identifica os 17 registros de Rodolfo; ela não é redistribuída
entre autores. Discussão relatada, atividade planejada e execução documentada
continuam distintas.

## Escopo da execução

A parte comum deriva do notebook de 22/10 e recalcula o experimento de 20/10.
Não baixa pesos, não executa reconhecedores, não treina modelos e não altera
catálogo, editor, alvos ou revisões. Os dez códigos originais são mantidos,
com mudança apenas da pasta dos derivados. A execução de demonstração desta
versão é por Codex (IA), com os quatro formulários vazios.

O [artigo revisto](../pi_iv_pln_20261023_entrega/README.md) e os [fichamentos integrais](../../bibliografia/leitura_t1_t4_20261023/README.md)
estão disponíveis. O treinamento técnico posterior e a expansão do corpus têm
evidências próprias e não mudam os resultados deste diagnóstico.
'''
    for cell in notebook.cells:
        if cell.cell_type != 'markdown':
            continue
        cell.source = cell.source.replace('`requirements-notebook.txt`',
            '`../pi_iv_pln_20261022/requirements-notebook.txt`')
        cell.source = cell.source.replace('- Não houve treino, ajuste fino, pós-correção, nova segmentação ou estudo de esforço humano.',
            '- Na comparação de 20/10 não houve treino, ajuste fino, pós-correção, nova segmentação ou estudo de esforço humano.')
        cell.source = cell.source.replace('- A meta operacional de 30–50 linhas e a avaliação em outros documentos continuam futuras.',
            '- A meta inicial de 30–50 linhas não é garantia de suficiência; a expansão de 23/10 não torna o 269r reservado.')
        cell.source = cell.source.replace('O artigo é um primeiro rascunho. Modelo e rubricas ainda precisam\nser informados; a revisão bibliográfica inicial não equivale à revisão sistemática de PI IV.',
            'O artigo de 23/10 está diagramado no modelo encontrado; o enquadramento docente\ne a revisão sistemática de PI IV continuam pendentes.')
    notebook.cells[-1].source = '''## Fontes e articulação com a entrega

- [Artigo preparado para PI IV e PLN](../pi_iv_pln_20261023_entrega/README.md).
- [Fontes e conferência de citações](../pi_iv_pln_20261023_entrega/citacoes.json).
- [Fichamentos completos T1/T4 por IA](../../bibliografia/leitura_t1_t4_20261023/README.md).
- [Notebook histórico de 22/10](../pi_iv_pln_20261022/README.md), preservado.
- [Experimento e reprodução opcional de inferências](../../experimentos/traslado_269r_reconhecedores_24_20261020/README.md).
- [Expansão e ensaio técnico posteriores](../../dataset_expansion_20261023/README.md).

Recalcular métricas sobre saídas arquivadas não é nova inferência. A discussão
abaixo deve considerar o diagnóstico de desenvolvimento e as oito ressalvas.
'''
    notebook.cells.extend([
        md('''# Participação individual

As tabelas e imagens desta seção são geradas automaticamente como material de
trabalho. Elas **não são respostas de Caio, Guilherme, Tiago ou Rodolfo**.
Cada integrante preenche apenas o seu relato. Use também este espaço para
documentar uma contribuição concreta da discussão já ocorrida, sem precisar
alegar programação ou autoria de uma execução feita por outra pessoa.

**Formulário:** `preenchido_por` = quem está escrevendo; `data_atividade` = data
real (AAAA-MM-DD); `relato` = contribuição e interpretação próprias;
`evidencias` = caminhos de arquivos no repositório, URLs ou `relato: descrição
da discussão`; `uso_de_ia` = ferramenta e função, ou declaração de não utilização.
Se alguém registrar o relato de um colega, identifique quem preencheu; o
colega ainda precisa conferir. Os registros são autodeclarações, sem autenticação
ou aprovação automática e sem validação de linhas do manuscrito.
''', 'equipe-orientacao'),
        code('''EQUIPE_DIR = RAIZ / 'docs/entregas/pi_iv_pln_20261023_equipe'
PARTICIPACAO = runpy.run_path(str(EQUIPE_DIR / 'participacao.py'))
registrar_participacao = PARTICIPACAO['registrar']
listar_participacoes = PARTICIPACAO['registros']
modelo_formulario = PARTICIPACAO['formulario_vazio']
print('Formulários preparados; nenhuma participação individual foi atribuída pela execução.')
''', 'equipe-preparacao'),
        md('''## Caio — bibliografia e fundamentação

**Previsto no primeiro artigo:** revisão bibliográfica de HTR/segmentação.
**Atividade atual:** conferir as relações entre T1/T4 e o artigo do diagnóstico.

Abra as fontes e os fichamentos nas referências abaixo. Explique, com página,
uma afirmação que T1 sustenta e um limite de usar seus casos como comparação.
Em T4, identifique uma condição na qual o ajuste não melhora o CER e explique
por que NFD/macro não equivale a NFC/micro local. Aponte uma sugestão de revisão
ou uma concordância justificada com a fundamentação. Se sua contribuição já
ocorreu na conversa do grupo, descreva a proposta ou a dúvida que você trouxe.

Preencha `resposta_caio` e execute a célula. As respostas não são pré-escritas.
''', 'equipe-caio-roteiro'),
        code('''FONTES_ARTIGO = ler_json(RAIZ / 'docs/entregas/pi_iv_pln_20261023_entrega/citacoes.json')
tabela(['Fonte', 'Uso previsto no artigo', 'Escopo da consulta registrada'],
       [(r['key'], '; '.join(r['uses']), r['scope']) for r in FONTES_ARTIGO['references']
        if r['key'] in ['muehlberger2019', 'kiessling2026a', 'kiessling2026b']])
resposta_caio = {
    'preenchido_por': '', 'data_atividade': '', 'relato': '',
    'evidencias': [], 'uso_de_ia': '',
}
resultado_caio = registrar_participacao(RAIZ, 'caio', resposta_caio)
print(resultado_caio)
''', 'equipe-caio-formulario'),
        md('''## Guilherme — modelos e reprodução

**Previsto no primeiro artigo:** avaliação de modelos/dependências e pipeline.
**Atividade atual:** verificar as configurações dos dois reconhecedores e a
reprodução dos cálculos, usando os registros já disponíveis.

Compare os identificadores, hashes declarados, dispositivo e precisão das
proveniências. Relacione essa comparação ao resumo CER/WER recalculado.
Explique duas diferenças de configuração que impedem atribuir o resultado só
à versão da arquitetura. Distinga reexecução do cálculo de nova inferência e
de ajuste fino. Registre uma checagem que você fez ou uma questão técnica que
levantou na discussão. O notebook lê a proveniência; não carrega pesos para
comprovar novamente o hash do arquivo do modelo.
''', 'equipe-guilherme-roteiro'),
        code('''PROV5 = ler_json(PACOTE / 'ppocrv5/provenance.json')
PROV6 = ler_json(PACOTE / 'ppocrv6/provenance.json')
PESO5 = PROV5['identidade']['loaded_model']
CFG6 = PROV6['config']['recognition']
tabela(['Configuração', 'Identidade declarada', 'SHA-256 declarado'], [
    ('PP-OCRv5 / ONNX / CPU / float32', PESO5['id'], PESO5['sha256']),
    ('PP-OCRv6 / Kraken / ' + CFG6['device'] + ' / ' + CFG6['precision'], CFG6['model'], CFG6['sha256']),
])
resposta_guilherme = {
    'preenchido_por': '', 'data_atividade': '', 'relato': '',
    'evidencias': [], 'uso_de_ia': '',
}
resultado_guilherme = registrar_participacao(RAIZ, 'guilherme', resposta_guilherme)
print(resultado_guilherme)
''', 'equipe-guilherme-formulario'),
        md('''## Tiago — imagens, associações e erros

**Previsto no primeiro artigo:** inventário e associações imagem–texto com
Rodolfo, além de colaboração no pipeline tradicional com Guilherme.
**Atividade atual:** inspecionar o vínculo entre os recortes e o diagnóstico.

Confira as linhas 1, 17 e 24: imagem, ID, coordenadas e correspondência com a
linha física. Compare os resultados brutos e descreva um problema de recorte,
espaçamento, letra ou abreviatura que você observou. Diferencie erro do modelo
de uma dúvida já existente no alvo. Informe no relato se consultou a edição,
o alvo ou as saídas; esta atividade não presume leitura independente. Ela não
altera o catálogo nem promove uma ressalva a validação. Na próxima rodada,
o mesmo método pode apoiar o inventário dos novos candidatos do corpus.
''', 'equipe-tiago-roteiro'),
        code('''from IPython.display import Image

for numero in [1, 17, 24]:
    alvo = next(a for a in ALVOS if a['linha'] == numero)
    recorte = next(r for r in RECORTES if r['line_id'] == alvo['line_id'])
    display(Markdown('### Inspeção proposta — linha ' + str(numero)))
    display(Image(filename=str(RAIZ / recorte['crop_image']), width=800))
    tabela(['Campo', 'Informação arquivada'], [
        ('ID', recorte['line_id']), ('Coordenadas', recorte['bbox_xyxy']),
        ('Imagem de origem', recorte['source_image']),
        ('Alvo assistido', alvo['texto_alvo']), ('Estado histórico', alvo['estado_visual_original']),
        *[(MODELOS[m], next(p['text_raw'] for p in PREDICOES[m] if p['line_id'] == alvo['line_id'])) for m in MODELOS],
    ])
resposta_tiago = {
    'preenchido_por': '', 'data_atividade': '', 'relato': '',
    'evidencias': [], 'uso_de_ia': '',
}
resultado_tiago = registrar_participacao(RAIZ, 'tiago', resposta_tiago)
print(resultado_tiago)
''', 'equipe-tiago-formulario'),
        md('''## Rodolfo — coordenação e consolidação

**Previsto no primeiro artigo:** dados, associações e pipeline, além das
entregas da equipe. **Evidência histórica disponível:** os 17 registros humanos
da reconferência de 21/10, mostrados na parte comum. Não precisam ser reatribuídos.

Nesta rodada, reúna as respostas dos colegas e confira se o relato distingue
planejamento, discussão e execução. Registre também sua própria implementação,
revisão ou coordenação efetivamente realizada, indicando arquivos, commits ou
outros registros. As contribuições dos colegas devem ser conferidas por eles.
Não preencha o formulário alheio como se fosse confirmação do participante.
''', 'equipe-rodolfo-roteiro'),
        code('''resposta_rodolfo = {
    'preenchido_por': '', 'data_atividade': '', 'relato': '',
    'evidencias': [], 'uso_de_ia': '',
}
resultado_rodolfo = registrar_participacao(RAIZ, 'rodolfo', resposta_rodolfo)
print(resultado_rodolfo)
''', 'equipe-rodolfo-formulario'),
        md('''## Consolidação da rodada e preservação

A tabela abaixo só lista arquivos realmente encontrados na pasta de registros.
Ausência de registro individual não apaga uma discussão coletiva; significa
que a contribuição ainda não foi individualizada aqui. A existência de JSON
também não autentica identidade nem prova revisão independente do manuscrito.

Depois da rodada, Caio e Guilherme podem conferir os relatos um do outro;
Tiago e Rodolfo podem fazer o mesmo. São revisões propostas, ainda não feitas.
A coordenação poderá usar os relatos conferidos para redigir a contribuição
dos autores em uma nova versão do artigo. O artigo já publicado não é alterado
automaticamente por estes formulários.
''', 'equipe-consolidacao-roteiro'),
        code('''REGISTROS_EQUIPE = listar_participacoes(RAIZ)
tabela(['Participante previsto', 'Registros individuais disponíveis', 'Situação'], [
    (nome, sum(r['participante_id'] == pid for r in REGISTROS_EQUIPE),
     'Relato(s) disponível(is), por conferir' if any(r['participante_id'] == pid for r in REGISTROS_EQUIPE)
     else 'Contribuição individual a preencher')
    for pid, nome in PARTICIPACAO['PARTICIPANTES'].items()
])
assert {nome: digest(PACOTE / nome) for nome in INVENTARIO} == HASHES_ANTES
assert digest(RECONFERENCIA / 'inventario.json') == HASH_INVENTARIO_RECONFERENCIA
if WORKSPACE_ANTES is not None:
    assert {p.relative_to(RAIZ).as_posix(): digest(p) for p in WORKSPACE.rglob('*') if p.is_file()} == WORKSPACE_ANTES
RESUMO_EQUIPE = {
    'tipo': 'roteiro_colaborativo_com_registros_autodeclarados',
    'formularios_desta_execucao': {pid: resultado for pid, resultado in [
        ('caio', resultado_caio), ('guilherme', resultado_guilherme),
        ('tiago', resultado_tiago), ('rodolfo', resultado_rodolfo)]},
    'registros_individuais_encontrados': len(REGISTROS_EQUIPE),
    'identidade_autenticada': False, 'participacao_individual_inferida_do_cronograma': False,
    'novas_inferencias': 0, 'catalogo_alterado': False,
}
(SAIDA.parent / 'resumo_participacao.json').write_text(json.dumps(RESUMO_EQUIPE, ensure_ascii=False, indent=2) + '\\n', encoding='utf-8')
print('Diagnóstico preservado. Relatos individuais são registros separados, sujeitos à conferência.')
''', 'equipe-consolidacao'),
        md('''## Comentários sobre uso de IA

Ferramenta: Codex, da OpenAI. Utilização: organização deste roteiro a partir
do planejamento inicial e do relato do solicitante, preparação das células,
reprodução dos cálculos e verificações. Os formulários individuais da execução
de demonstração estão vazios. Nenhuma resposta dos colegas foi escrita ou
confirmada pela IA. Cada participante deve registrar seu próprio uso de IA.
''', 'equipe-comentarios'),
    ])
    notebook.metadata['paleographia_equipe'] = {
        'origem': ORIGINAL.relative_to(ROOT).as_posix(),
        'origem_sha256': hashlib.sha256(ORIGINAL.read_bytes()).hexdigest(),
        'codigos_originais': 10,
        'alteracao_no_codigo_original': 'somente pasta SAIDA',
        'formularios_individuais_inicialmente_vazios': True,
    }
    nbf.validate(notebook)
    nbf.write(notebook, BASE / 'colaboracao_equipe.ipynb')
    print(json.dumps({'celulas': len(notebook.cells), 'codigo': sum(c.cell_type == 'code' for c in notebook.cells)}, ensure_ascii=False))


if __name__ == '__main__':
    main()
