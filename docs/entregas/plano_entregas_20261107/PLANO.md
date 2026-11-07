# Plano de entregas PI IV e PLN (07/11/2026)

Plano da equipe para fechar as entregas dentro do que o professor pediu nas aulas de PLN
(slides das aulas 05, 07, 08, 09 e 10). Prioridade: cumprir os requisitos, não ampliar o escopo.

## 1. Requisitos oficiais (slide "Informações Projeto", aula 07; avaliação, aula 05)

1. **Artigo científico** de 3 a 5 páginas, num dos modelos do Drive do professor (.doc, Google Docs
   ou LaTeX). Primeiro o link do arquivo editável, depois o PDF.
2. **Notebook da implementação** (Colab ou Jupyter), com a comparação entre 2 modelos (aula 05).
3. **Planilha de documentação do uso de IA** (obrigatória).
4. **Apresentação oral presencial**: até 5 min + 5 min de perguntas, em 19/11 (ou 12/11). Deve
   contemplar PI IV e PLN, ou o grupo faz uma apresentação por disciplina.
5. **Planilha de entrega**: links do artigo, do Notebook 1 e do Notebook 2, mesmo em desenvolvimento.
6. **Acompanhamentos** pelo forms: 01 até 06/11 e 02 até 19/11; um integrante responde pelo grupo;
   só vale se os links já estiverem na planilha.

A confirmar com o professor: apresentação de 5 ou 10 min (preparar para 5); se o artigo precisa
estar no modelo oficial.

## 2. O que já existe

- Comparação entre 2 modelos: PP-OCRv5 × PP-OCRv6; VGSL do zero × pré-treinado; PP-OCRv6 base ×
  ajustado no Traslado (validação de 1795: CER 14,20% → 10,72%, WER 56,72% → 41,79%; treino gravado em 06/11).
- Notebook 1: `docs/entregas/notebook_1_offline/PaleographIA_Notebook_1_Entrega.ipynb`.
- Notebook 2: `docs/entregas/continuidade_20261103/avaliacao_linhas_1767/PaleographIA_Notebook_2_Carta_1767.ipynb`.
- Artigo de 23/10 (`artigo.docx`, `artigo.pdf`, `artigo.md`): levar ao modelo oficial, 3 a 5 páginas.
- Declaração de uso de IA no artigo (Codex e Antigravity); falta a planilha oficial e as entradas dos colegas.
- Divisão de tarefas: não registrada. Não inventar; pedir a cada integrante.

## 3. Reforço da parte de PLN

### 3.1 Análise linguística dos erros
Com predições e referências já salvas, sem rodar o reconhecedor de novo: alinhar por distância de
edição linha a linha; classificar erros (abreviaturas, acentos e til, maiúsculas, nomes próprios,
grafias históricas, palavras coladas ou separadas, pontuação); tabela das confusões de caracteres
mais frequentes e parcela do CER por tipo. Resultado: tabela e gráfico no notebook, parágrafo no artigo.

### 3.2 Pós-correção lexical: dois métodos
- Método A: vocabulário + distância de Levenshtein (palavra mais próxima).
- Método B: n-gramas de caracteres com TF-IDF (aula 03) e cosseno, desempate pela frequência.
- CER e WER antes e depois, nas linhas de validação de 1795.

Regras: o vocabulário não contém palavras das referências de validação nem do teste (só
`data/lexicon` e transcrições de treino); NFC preservando maiúsculas, acentos, pontuação e grafia;
a correção é sugestão, guardada separada da saída bruta e da transcrição humana; se piorar,
registrar. LLM para pós-correção fica como trabalho futuro.

### 3.3 Enquadramento nas aulas
Sequência para sequência (aula 06); pré-treino continuado e ajuste fino como adaptação de domínio
(aula 09); tokenização e vocabulário por caractere (aulas 02 e 05); CER/WER no papel de BLEU/ROUGE
(aula 06); pós-correção como recuperação lexical (TF-IDF e BM25, aula 10); treino, validação,
teste e generalização (aula 04).

## 4. Tarefas por entrega

- **Planilha de entrega**: link do artigo editável, do Notebook 1 e do Notebook 2.
- **Notebook final**: introdução; comparação 1 (base × ajustado); análise de erros; comparação 2
  (pós-correção A × B); teste final se pronto, senão deixar claro que são números de
  desenvolvimento; conclusão e limitações. Roda no Colab ou localmente, com dados incorporados,
  sem GPU nem Docker.
- **Artigo** (3 a 5 páginas, modelo oficial): resumo, introdução, fundamentação, materiais e
  métodos, resultados, discussão, conclusão, referências, declaração de uso de IA. Foco em dados,
  modelos, métricas e PLN. Usar "manuscritos históricos em português dos séculos XVII a XIX".
  CER e WER como taxa de erro (100% − CER só como comentário). Citar a autorização de uso das
  imagens do Arquivo Histórico de Jundiaí, com crédito e uso sem fins comerciais.
- **Planilha de uso de IA**: Codex, Antigravity, ChatGPT e Claude, com o que cada um fez; cada
  integrante preenche as próprias entradas.
- **Repositório**: README e `docs/sources.md` com a autorização do Arquivo Histórico (imagens
  públicas no site da prefeitura, uso permitido sem fins comerciais); remover a pendência sobre a
  distribuição.
- **Apresentação** (até 5 min): problema (30 s); solução (45 s); como funciona (1 min);
  resultados (1 min); parte de PLN (1 min); limitações e próximos passos (45 s).

## 5. Prioridade

1. Links na planilha e forms do Acompanhamento 01.
2. Análise de erros e pós-correção no notebook.
3. Artigo no modelo oficial.
4. Planilha de uso de IA e atualização do repositório.
5. Teste final no documento independente, se der tempo.
6. Slides e ensaio da apresentação.
