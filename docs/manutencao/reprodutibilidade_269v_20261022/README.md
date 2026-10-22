# Correções de reprodução e orientação da CI — 22/10/2026

Correção aditiva à base `4d429c9c1a51d616b84452269895e4951f4464c4`. Mantém
inalterado o [pacote integral do 269 verso](../../experimentos/traslado_269v_integral_edicao_20261022/README.md),
incluindo seu verificador, inventário e resultados originais. Use o **verificador
v2 desta pasta** para as instruções atuais. Não houve inferência, treinamento,
alteração de referência ou promoção de estados humanos.

## O problema e a fonte encontrada

O verificador histórico exige o PDF no caminho
`data/raw/import_20261015/6e82cef18b04_5b58a915f024a80e.pdf`. Esse arquivo **extraído**
não acompanha o clone. A auditoria local original passou porque ele já estava
presente nesta máquina; isso não garantia que o mesmo comando funcionasse em
um clone novo.

Foi encontrada uma cópia exata **dentro do RAR já versionado**:

- Arquivo: `data/raw/Transcrições.rar`.
- SHA-256 do RAR: `6e82cef18b04d2aaf7a2cc1c1f88bf82d47347b8b123cae92394b153806f7a0d`.
- Membro: `Transcrições/Traslado do Auto de Criação da Vila de Jundiahy/Traslado do Auto de Criação da Vila de Jundiahy - Fólio 269 - 273.pdf`.
- PDF: **16.729.975 bytes**; SHA-256 obrigatório:
  `e1c779a4713340adbf5e6102b0c3edc716c12612d18597e9d22228676ab9b3e0`.

O membro foi lido e seu hash conferido. O download atual de
[“Baixar documento PDF” no registro 102201 do acervo](https://jundiai.sismu.app/obra/102201/traslado-do-auto-de-criacao-da-vila-de-jundiai-no-ano-de-1656-a-14-dezembro)
também foi conferido e coincide byte a byte com essa identidade. O
[endereço direto observado](https://acervos.sismu.com.br/api/beta/anexos/original/74780.pdf)
é uma alternativa; se mudar ou entregar outros bytes, a auditoria deve rejeitá-los.
O [registro de proveniência](fonte_original.json) mantém a origem, o membro e os hashes.
Não foi adicionada outra cópia do PDF ao repositório nem alterada sua política de uso.

## Recuperar a fonte sem download

Na raiz de um clone com Python 3.11/3.12, instale o projeto e o extra PDF:

```powershell
.venv/Scripts/python.exe -m pip install -e ".[pdf]"
```

O comando abaixo usa a função de recuperação **já existente** no projeto.
Ela confere o hash do RAR e do membro antes de gravar. Não sobrescreve um
destino divergente nem toca nos workspaces de revisão.

```powershell
@'
import json
from pathlib import Path
from paleographia.preparation import ensure_archive_reference

root = Path.cwd()
entries = json.loads((root/'data/manifests/archive_members.json').read_bytes())
expected = 'e1c779a4713340adbf5e6102b0c3edc716c12612d18597e9d22228676ab9b3e0'
entry = next(item for item in entries if item['sha256'] == expected)
ensure_archive_reference(root, entry, 'output/fontes/traslado_269_273.pdf')
print('PDF recuperado e conferido em output/fontes/traslado_269_273.pdf')
'@ | .venv/Scripts/python.exe -
```

Em Linux, execute o mesmo código Python e use `.venv/bin/python`.
O membro deste RAR está armazenado sem compressão; `rarfile==4.2`, incluído
no extra `pdf`, consegue lê-lo sem programa externo de descompressão.

## Auditoria completa com o PDF

Use o arquivo recuperado ou uma cópia externa exata:

```powershell
.venv/Scripts/python.exe docs/manutencao/reprodutibilidade_269v_20261022/verificar.py --facsimile output/fontes/traslado_269_273.pdf
```

```powershell
.venv/Scripts/python.exe docs/manutencao/reprodutibilidade_269v_20261022/verificar.py --facsimile "D:/Fontes/74780.pdf"
```

O caminho externo resolve a entrada histórica apenas **durante a auditoria**.
Os caminhos e hashes originais continuam intactos nos snapshots. Sem argumento,
o modo completo ainda procura o caminho histórico. Fonte ausente ou com hash
incorreto gera mensagem em português, hash esperado e próximo comando, com
código de saída 2, sem aprovação ou traceback simples.

A aprovação completa exige: todos os controles da versão original, hash exato
do PDF e igualdade dos bytes do JPEG publicado com a imagem embutida na página 2.
Retorna `resultado: aprovado`, `auditoria_completa: true` e
`comparacao_bytes_imagem_embutida_executada: true`. Não carrega pesos, não usa
Docker, não acessa rede nem reconhece texto novamente.

## Conferir somente os artefatos publicados

```powershell
.venv/Scripts/python.exe docs/manutencao/reprodutibilidade_269v_20261022/verificar.py --modo artefatos
```

Sem o PDF extraído, esse modo confere os 69 arquivos do inventário histórico,
as demais entradas congeladas, a edição textual versionada, os alvos, o JPEG
publicado, as caixas e pixels dos recortes, o bruto, as métricas e as ressalvas.
Mantém a segunda implementação independente da distância de edição.

Retorna **`conferencia_parcial_aprovada`**, `auditoria_completa: false`,
`hash_pdf_original_verificado: false` e
`comparacao_bytes_imagem_embutida_executada: false`, com as duas verificações
pendentes explicitadas. Não declara comprovada a correspondência do JPEG ao
PDF ausente. Fornecer `--facsimile` nesse modo é rejeitado para evitar ambiguidade.
Esse modo não enfraquece a aprovação completa; o usuário o escolhe explicitamente.

## CI vigente e documentação histórica

O [workflow atual](../../../.github/workflows/ci.yml) contém:

| Grupo | Cobertura |
| --- | --- |
| Quatro ambientes leves | Ubuntu e Windows × Python 3.11 e 3.12; suíte e verificadores explícitos do workflow |
| Dois trabalhos acadêmicos | Entregas `20261020` e `20261022`, em Ubuntu/Python 3.12; auditoria e reexecução dos notebooks sem inferência |
| Diagnósticos integrais 269 reto e verso | **Não incluídos** nessas verificações automáticas; auditorias locais registradas separadamente |

A frase sobre a CI ainda executar apenas 20/10, no
[README congelado da entrega de 22/10](../../entregas/pi_iv_pln_20261022/README.md),
registra a situação anterior à atualização da matriz. Foi preservada como parte
do pacote histórico; esta nota, o [índice ativo](../../README.md) e o
[README principal](../../../README.md) fornecem a orientação vigente.
CI verde não comprova a auditoria dos diagnósticos integrais. Esta correção
não modifica o workflow nem acrescenta os diagnósticos à CI.

## Verificações e preservação

```powershell
.venv/Scripts/python.exe -m pip install -e ".[test,pdf]"
.venv/Scripts/python.exe -m pytest -q docs/manutencao/reprodutibilidade_269v_20261022/test_verificar.py
```

Os seis testes usam uma extração isolada de `git archive HEAD`, sem o PDF no
caminho histórico e sem pesos. A fonte correta é recuperada do RAR desse clone
e fornecida por caminho externo. Incluem fonte ausente, edição textual incorreta,
fonte correta, recuperação do RAR, conferência parcial sem PDF e rejeição de bruto
adulterado. O caso correto não é omitido nem depende de rede.

Os [recibos](validacao.json), a [auditoria completa](auditoria_completa.json),
a [conferência parcial](auditoria_artefatos.json) e o
[inventário desta correção](inventario.json)
registram a execução. Foram executados apenas os testes do comportamento novo
e os verificadores afetados. Métricas conservadas: verso **CER 16,48% / WER 56,25%**;
reto **26,97% / 60,31%**. O diagnóstico de 24 recortes e os pacotes acadêmicos não
foram recalculados ou substituídos. As coberturas e convenções desses protocolos
diferem; suas taxas não isolam uma mudança no reconhecedor.

As oito ressalvas históricas e suas reconferências, a autoria, as revisões e o
bruto permanecem preservados. Reto e verso pertencem ao mesmo documento de
desenvolvimento, sem promoção a teste reservado ou validação entre documentos.
`reproduzir.py`, os alvos, os parâmetros e os inventários das rodadas originais
não foram editados. Para eventual uso do executor histórico, a fonte deve estar
no caminho histórico que ele exige; esta correção cobre sua auditoria, sem executar
novamente as etapas de reconhecimento.
