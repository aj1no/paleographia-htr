# Dataset revisado de 1795: sete referências por linha

Pacote derivado em **03/11/2026**, após a observação 038. Contém sete referências com texto e geometria aprovados, associação ao fólio 91r da sessão de 25/06/1795 e descrição da cobertura parcial confirmadas. [Prontidão e validações](prontidao.json).

- [Sete linhas revisadas](linhas_revisadas_7.jsonl): linhas físicas 1–7 do bloco.
- [Linha provável excluída](linhas_excluidas_1.jsonl): oitava linha preservada, com abriu provável e alternativa abrio.
- [Página e cobertura](pages.jsonl): associação validada; região de oito linhas com complete=false.
- [Inventário de hashes](inventario.json).

A seleção é explícita e mantém a oitava linha em arquivo próprio e no [snapshot completo](../../../revisao_humana/sessao_1795/sessao_20261103/exportacao_apos_observacao_038/lines.jsonl). Não apresenta os sete itens como se resolvessem todo o bloco ou a página. Não houve nova inferência, treinamento ou seleção de modelo.

## Uso e limites

Os caminhos são relativos à raiz do repositório. Os recortes das sete linhas têm cópias publicadas; a primeira linha aponta para a cópia estável com o mesmo hash, preservando o caminho canônico do workspace no campo canonical_crop_image. Imagem original e edição em data/raw devem ser restauradas pelo procedimento do corpus v0.2 em outro checkout. Este pacote não é autossuficiente e não exige alterar o editor para consultá-lo.

A validação estrutural de referência por linha passa nos sete pares. A referência da região de oito linhas não é integral: a linha 8 tem dúvida e complete=false permanece. Uma futura avaliação regional deve delimitar seu próprio escopo completo e registrar a exclusão, sem omitir silenciosamente a oitava linha.

O pacote tem um único grupo documental. Não foram criadas divisões aleatórias ou atribuídos estes itens a treino/validação/teste. A validação de treinamento continua bloqueada por falta de partições e o seletor científico atual recusa o protocolo pela independência ainda pendente. Próxima etapa: confirmar grupos independentes e preparar mais referências revisadas antes de definir o protocolo de avaliação.

Ferramenta: Codex, da OpenAI. Utilização: aplicar confirmações humanas, derivar manifests, conferir hashes e executar validadores sem modelos. As leituras pertencem ao revisor identificado nos registros. As condições de uso das fontes continuam por esclarecer.
