# Revisões humanas ainda pendentes

Material preparado por Codex (IA), em 23/10/2026. **Nenhuma concordância,
transcrição ou contribuição individual foi preenchida em nome da equipe.**
Os pontos abaixo são tarefas propostas. O artigo atual está em [PDF](artigo.pdf),
[Word](artigo.docx) e [Markdown](artigo.md).

## Conferência do artigo pelos quatro autores

Use os formulários já existentes no notebook; os links abaixo abrem diretamente
a seção de cada participante. Preencha quem registra, data real da atividade,
relato próprio, evidências e uso de IA. Execute seu formulário, baixe o ZIP e
envie à coordenação pelo canal do grupo. A existência de JSON é autodeclaração;
conferência pelo participante e revisão entre colegas continuam pendentes.

| Integrante e formulário existente | Pontos concretos para conferir | Evidência a informar |
| --- | --- | --- |
| [Caio](https://colab.research.google.com/github/aj1no/paleographia-htr/blob/dbcd8ce100147ba066233d9b4d6078b7159dcec9/docs/entregas/pi_iv_pln_20261023_colab/colaboracao_colab.ipynb#scrollTo=equipe-caio-formulario) | T1 p. 958–963: consistência textual e limites dos casos; T4 p. 3–6 e 8–9: altura/idiomas do preprint, NFD/macro e resultado negativo de MAKHZAN; conferir a interpretação no artigo | Fonte/página consultada e sugestão ou concordância justificada |
| [Guilherme](https://colab.research.google.com/github/aj1no/paleographia-htr/blob/dbcd8ce100147ba066233d9b4d6078b7159dcec9/docs/entregas/pi_iv_pln_20261023_colab/colaboracao_colab.ipynb#scrollTo=equipe-guilherme-formulario) | Variantes/implementações, CPU/float32, hashes declarados, versões e execução do cálculo; distinguir 48 inferências históricas do recálculo e do ajuste fino posterior | Arquivos, versões e resultado da checagem que efetivamente realizou |
| [Tiago](https://colab.research.google.com/github/aj1no/paleographia-htr/blob/dbcd8ce100147ba066233d9b4d6078b7159dcec9/docs/entregas/pi_iv_pln_20261023_colab/colaboracao_colab.ipynb#scrollTo=equipe-tiago-formulario) | IDs/imagens das linhas 1, 17 e 24; exemplos de erros do artigo e distinção entre saída incorreta e dúvida do alvo; declarar consulta à edição/saídas | Observações próprias identificadas por linha, sem validar o manuscrito inteiro |
| [Rodolfo](https://colab.research.google.com/github/aj1no/paleographia-htr/blob/dbcd8ce100147ba066233d9b4d6078b7159dcec9/docs/entregas/pi_iv_pln_20261023_colab/colaboracao_colab.ipynb#scrollTo=equipe-rodolfo-formulario) | Conferir nomes/contatos, conteúdo dos três formatos, links, fonte documental, declaração de IA e relatos recebidos; informar execução/coordenação real | Arquivos/commits e ações próprias; os 17 registros de reconferência mantêm a autoria histórica |

O cotejo desta etapa é por IA. T1/T4 foram lidos integralmente por IA; outras
fontes têm escopo parcial documentado em [citacoes.json](citacoes.json).
A leitura humana e a revisão sistemática não são consideradas concluídas.
Versão, modelo, prompts e mudanças específicas do uso inicial de Antigravity
ainda precisam ser individualizados. Prompts não recuperados devem ser
identificados como ausentes, não reconstituídos como se fossem literais.

Proposta após os relatos: Caio e Guilherme conferem os registros um do outro;
Tiago e Rodolfo fazem o mesmo. Só depois a coordenação pode redigir uma declaração
factual de contribuições e marcar as confirmações efetivamente recebidas.
Esta preparação não envia mensagens nem registra aprovação dos autores.

## Rodada de curadoria dos oito recortes

Página candidata da **sessão de 1795**, fólio indicado **91r**, grupo documental
`sessao_1795`. [Página contextual](../../dataset_expansion_20261023/curation_sessao_1795_bloco01/context.jpg),
[limites sobrepostos](../../dataset_expansion_20261023/curation_sessao_1795_bloco01/overlay.jpg)
e [caderno original com oito imagens e edição separada](../../dataset_expansion_20261023/curation_sessao_1795_bloco01/README.md).
O bloco corresponde de forma candidata às linhas editoriais 4–11 da página 3;
a reprodução do manuscrito está também na página 4 do PDF. A transcrição e
edição são de Gilson Santos Lino, com revisão de Isabella Ferraro (AHMJ).

**Decisão de página, antes das linhas:** conferir se imagem e edição pertencem
à mesma sessão, se o numeral/face confirmam 91r, a ordem física e se a região
`body_first8_candidate` cobre apenas parte da página. Conferir a reprodução PDF
e o JPEG como variantes da mesma fonte, sem transformá-los em documentos
independentes. Identidade/independência documental continua pendente.

Para **cada** recorte, responder separadamente: (a) limites corretos ou novas
coordenadas; (b) correspondência com a linha física/editorial; (c) leitura histórica
efetivamente visível, dúvidas e abreviaturas; (d) cobertura completa da linha.
Registrar revisor, data/hora com fuso, fonte consultada e escopo da confirmação.
Se não for possível ler tudo, manter pendente e indicar o trecho confirmado.

| Ordem / edição | Recorte e ID | Limites candidatos `[x1,y1,x2,y2]` | Pergunta específica para a leitura |
| --- | --- | --- | --- |
| 1 / 4 | [l_24b904b9ad9473450172](../../dataset_expansion_20261023/curation_sessao_1795_bloco01/l_24b904b9ad9473450172.png) | `[95,325,1030,377]` | Quais grafias, sinais e abreviaturas aparecem na data inicial? A edição modernizada não resolve a forma histórica. |
| 2 / 5 | [l_b8a06d58bd7cced4f3a2](../../dataset_expansion_20261023/curation_sessao_1795_bloco01/l_b8a06d58bd7cced4f3a2.png) | `[95,374,1030,421]` | Confirmar a quebra física da data entre as linhas 1–2 e eventuais abreviaturas ao final. |
| 3 / 6 | [l_4882de66b18aa948f2a4](../../dataset_expansion_20261023/curation_sessao_1795_bloco01/l_4882de66b18aa948f2a4.png) | `[95,416,1030,468]` | Registrar as formas históricas dos topônimos e os limites dos traços junto às linhas vizinhas. |
| 4 / 7 | [l_98962db568a2f74aab38](../../dataset_expansion_20261023/curation_sessao_1795_bloco01/l_98962db568a2f74aab38.png) | `[95,466,1030,517]` | Preservar a representação de títulos/abreviaturas e verificar se o limite direito contém a linha inteira. |
| 5 / 8 | [l_27cb89d5763a6e64c484](../../dataset_expansion_20261023/curation_sessao_1795_bloco01/l_27cb89d5763a6e64c484.png) | `[95,514,1030,566]` | Conferir nome próprio e sinais elevados sem copiar expansões da edição. |
| 6 / 9 | [l_6077eea6d3ac418348ec](../../dataset_expansion_20261023/curation_sessao_1795_bloco01/l_6077eea6d3ac418348ec.png) | `[95,563,1030,619]` | Existe hífen físico no final? O `trat-` da edição não comprova o sinal no manuscrito. |
| 7 / 10 | [l_40d2333b12328973de24](../../dataset_expansion_20261023/curation_sessao_1795_bloco01/l_40d2333b12328973de24.png) | `[95,614,1030,669]` | Conferir a continuidade física da linha anterior e a separação das palavras, sem juntar automaticamente através da quebra. |
| 8 / 11 | [l_53dcba6fe1e315e30873](../../dataset_expansion_20261023/curation_sessao_1795_bloco01/l_53dcba6fe1e315e30873.png) | `[95,666,1030,721]` | Conferir nome/título e o limite inferior; as linhas seguintes ficam fora deste bloco parcial. |

Não há proposta de alvo diplomático neste material. Consultar a edição é
permitido e deve ser registrado; não equivale a leitura independente. Não usar
predições para escolher a referência de futuro teste. Uma palavra confirmada
não valida a linha, e uma leitura textual não confirma automaticamente geometria,
correspondência e cobertura. Aplicar a [política textual](../../transcription_policy.md).

### Registrar no editor existente

Com o ambiente do projeto e os originais restaurados pelo comando do guia,
use o workspace específico da configuração existente. **Importe apenas se esse
workspace estiver vazio**; se já houver trabalho, abra-o e preserve seu histórico.

```powershell
python -m paleographia import-catalog --config configs/curation_sessao_1795.toml --pages docs/dataset_expansion_20261023/curation_sessao_1795_bloco01/pages.jsonl --lines docs/dataset_expansion_20261023/curation_sessao_1795_bloco01/lines.jsonl
python -m paleographia serve --config configs/curation_sessao_1795.toml --host 127.0.0.1 --port 8012
```

Abra `http://127.0.0.1:8012`. Sugestões automáticas estão desativadas nessa
configuração. Use rascunho para leituras incompletas e os controles explícitos
para cada confirmação com revisor e data. Ao terminar, exporte para uma pasta nova:

```powershell
python -m paleographia export --config configs/curation_sessao_1795.toml --output-dir output/revisao_1795_RODADA_COM_IDENTIFICADOR_UNICO
```

O servidor não foi iniciado e os oito candidatos não foram importados ou
promovidos por este fechamento. Após respostas, conferir os registros exportados
e incorporar somente os campos explicitamente confirmados em uma nova versão.
O treinamento científico permanece bloqueado enquanto faltarem pares aptos,
grupos independentes e partições persistentes. O ensaio anterior não deve ser
reexecutado para validar alterações editoriais.
