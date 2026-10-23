"""Versão Colab aditiva; preserva o notebook e os cálculos anteriores."""
from pathlib import Path
import hashlib
import json
import re

import nbformat as nbf

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
ORIGEM = ROOT / 'docs/entregas/pi_iv_pln_20261023_equipe/colaboracao_equipe.ipynb'
CAMINHO = 'docs/entregas/pi_iv_pln_20261023_colab/colaboracao_colab.ipynb'
COLAB = 'https://colab.research.google.com/github/aj1no/paleographia-htr/blob/main/' + CAMINHO
REVISAO = 'c8a3e9a7f1cc55b66d630c510eff17ff95dfdece'


def link_absoluto(match):
    alvo = match.group(2)
    if re.match(r'^[a-z]+:|^#', alvo):
        return match.group(0)
    caminho = (ORIGEM.parent / alvo).resolve().relative_to(ROOT).as_posix()
    return '[' + match.group(1) + '](https://github.com/aj1no/paleographia-htr/blob/' + REVISAO + '/' + caminho + ')'


def gerar():
    nb = nbf.read(ORIGEM, as_version=4)
    for cell in nb.cells:
        if cell.cell_type == 'markdown':
            cell.source = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', link_absoluto, cell.source)
            if cell.id == 'ced5cb39':
                cell.source = '''## 1. Ambiente e localização dos arquivos

A célula **Preparar o projeto** acima busca os dados e prepara as bibliotecas no
Colab. Execute as células em ordem. Os resultados derivados podem ser recriados;
os pacotes históricos são somente lidos. Fora do Colab, use o checkout local com
as dependências de notebook já instaladas.
'''
            for pid in ['caio', 'guilherme', 'tiago', 'rodolfo']:
                cell.source = cell.source.replace('Preencha `resposta_' + pid + '`', 'Preencha os campos do formulário')
        elif cell.cell_type == 'code':
            cell.outputs = []
            cell.execution_count = None
            cell.source = cell.source.replace('output/equipe_20261023/calculos', 'output/equipe_colab_20261023/calculos')
            for pid in ['caio', 'guilherme', 'tiago', 'rodolfo']:
                if cell.id != 'equipe-' + pid + '-formulario':
                    continue
                prefixo = cell.source.split('resposta_' + pid + ' = {')[0]
                campos = []
                for campo, rotulo in [
                    ('preenchido_por', 'Nome de quem preenche'), ('data_atividade', 'AAAA-MM-DD, data real'),
                    ('relato', 'Descreva sua contribuição concreta'),
                    ('evidencias', 'Caminho, URL ou relato: descrição; separe itens com ponto e vírgula'),
                    ('uso_de_ia', 'Ferramenta e função, ou declaração de não utilização'),
                ]:
                    configuracao = json.dumps({'type': 'string', 'placeholder': rotulo}, ensure_ascii=False)
                    campos.append(campo + '_' + pid + ' = "" # @param ' + configuracao)
                cell.source = '# @title ' + pid.capitalize() + ' — preencher e executar { display-mode: "form" }\n' + prefixo + '\n'.join(campos) + '\n'
                cell.source += 'resposta_' + pid + ' = {\n'
                for campo in ['preenchido_por', 'data_atividade', 'relato', 'evidencias', 'uso_de_ia']:
                    valor = campo + '_' + pid
                    if campo == 'evidencias':
                        valor = '[e.strip() for e in ' + valor + '.split(";") if e.strip()]'
                    cell.source += '    "' + campo + '": ' + valor + ',\n'
                cell.source += '}\nresultado_' + pid + ' = registrar_participacao(RAIZ, "' + pid + '", resposta_' + pid + ')\nprint(resultado_' + pid + ')'
    abertura = '''# PaleographIA — participação da equipe no Google Colab

[![Abrir no Colab](https://colab.research.google.com/assets/colab-badge.svg)](''' + COLAB + ''')

1. Abra pelo botão e escolha **Arquivo → Salvar uma cópia no Drive**. Use seu nome no título.
2. Conecte ao ambiente padrão de **CPU** e use **Ambiente de execução → Executar tudo**.
   A primeira célula busca os dados e prepara as bibliotecas. Aguarde a conclusão.
3. Na seção com seu nome, leia a tarefa e preencha os cinco campos. A data deve ser
   a data real da atividade, no formato AAAA-MM-DD. Separe evidências por ponto e vírgula.
   Execute novamente **a célula do seu formulário** para salvar o relato.
4. Ao final, em **Baixar minha contribuição**, selecione seu nome, marque
   `baixar_contribuicoes` e execute essa célula. Envie o **ZIP baixado** à coordenação
   pelo grupo. Salve também sua cópia do notebook no Drive.

**Salvamento:** os JSONs ficam na máquina temporária do Colab. Salvar a cópia do
notebook no Drive não salva esses arquivos. Baixe o ZIP antes de encerrar a sessão.
O ZIP leva os relatos em JSON; evidências externas e arquivos produzidos por você
devem ser enviados junto, quando necessários. Nenhum envio ao grupo ou ao GitHub
é feito automaticamente. Sem formulário preenchido, nenhum relato é criado.

Cada participante descreve o que realmente discutiu, analisou ou revisou e informa
o uso de IA. Os relatos continuam sujeitos à conferência. Não é preciso carregar
imagens, montar o Drive, baixar pesos ou habilitar GPU para esta atividade.

Os dados vêm da revisão `''' + REVISAO + '''`, para manter o diagnóstico
reproduzível. A preparação exige internet. Para reler as instruções no GitHub,
consulte o [guia do Colab](https://github.com/aj1no/paleographia-htr/blob/main/docs/entregas/pi_iv_pln_20261023_colab/README.md).
'''
    bootstrap = (BASE / 'preparar_colab.py').read_text(encoding='utf-8')
    nb.cells[0:0] = [nbf.v4.new_markdown_cell(abertura, id='colab-instrucoes'),
        nbf.v4.new_code_cell('# @title 1. Preparar o projeto (execute primeiro)\n' + bootstrap +
            '\nRAIZ_COLAB = preparar_ambiente_colab()\nNO_COLAB = esta_no_colab()\n', id='colab-preparacao')]
    nb.cells.extend([
        nbf.v4.new_markdown_cell('''## Baixar minha contribuição

Depois de executar seu formulário, escolha seu nome, marque a caixa e execute
a célula abaixo. O ZIP reúne **somente os registros do integrante selecionado**
encontrados nesta sessão, incluindo versões sucessivas. Conferir e incorporar
esses registros à documentação continua sendo tarefa da equipe.

Se corrigir um campo, execute seu formulário novamente e baixe outro ZIP.
Você pode rodar novamente a consolidação acima para atualizar a tabela.
''', id='colab-download-instrucoes'),
        nbf.v4.new_code_cell('# @title Baixar minha contribuição { display-mode: "form" }\n' +
            (BASE / 'exportar_contribuicoes.py').read_text(encoding='utf-8') + '''
participante_download = "caio" # @param ["caio", "guilherme", "tiago", "rodolfo"]
baixar_contribuicoes = False # @param {type:"boolean"}
if baixar_contribuicoes:
    pacote_download = criar_pacote_contribuicoes(RAIZ, participante_download)
    if pacote_download is None:
        print('Nenhum registro encontrado. Preencha e execute seu formulário primeiro.')
    elif NO_COLAB:
        from google.colab import files
        files.download(str(pacote_download))
    else:
        print('Pacote salvo em:', pacote_download)
else:
    print('Depois de salvar seu formulário, selecione seu nome, marque a caixa e execute esta célula.')
''', id='colab-download'),
    ])
    nb.metadata['colab'] = {'name': 'PaleographIA — contribuição da equipe.ipynb', 'provenance': []}
    nb.metadata['paleographia_colab'] = {
        'origem': ORIGEM.relative_to(ROOT).as_posix(),
        'origem_sha256': hashlib.sha256(ORIGEM.read_bytes()).hexdigest(),
        'revisao_dados': REVISAO, 'nova_inferencia': False,
        'formularios_inicialmente_vazios': True,
    }
    nbf.validate(nb)
    nbf.write(nb, BASE / 'colaboracao_colab.ipynb')
    print('Notebook Colab gerado:', len(nb.cells), 'células,', sum(c.cell_type == 'code' for c in nb.cells), 'de código.')


if __name__ == '__main__':
    gerar()
