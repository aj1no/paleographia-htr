# Histórico preservado

Arquivos `.py.txt` são cópias byte a byte dos scripts legados auditados. Foram conservados para leitura e comparação; não os execute sobre os dados. Eles contêm associação por posição, remoção de diretórios e outros comportamentos substituídos.

Até 12/11/2026, dez scripts numerados na raiz eram avisos de compatibilidade (não executavam
nada e terminavam com código 1). Eles saíram na
[organização da entrega](../docs/manutencao/organizacao_entrega_20261112/README.md) e continuam
no histórico do Git.
O [catálogo dos caminhos antigos](../docs/manutencao/scripts_numerados_20261020/README.md)
registra orientações atuais e hashes dos avisos e originais. Treino e geração
automática de dataset TrOCR permanecem desativados; as orientações não são
promessas de operações equivalentes a todos os comportamentos antigos.

`server/main.py` mantém entrada ASGI compatível e delega ao pacote novo. O gitlink `client`, que apontava para um submódulo sem `.gitmodules`, saiu em 12/11/2026; a interface é servida pelo próprio backend. `metadata.csv` e as transcrições antigas permanecem intactos, sem validação retroativa; os arquivos compactados de `data/raw` saíram do repositório na mesma data.

## Auxiliares arquivados em 20/10/2026

Seis arquivos sem dependência encontrada no fluxo atual foram movidos para
[auxiliares_20261020](auxiliares_20261020/README.md): diagnóstico de PDF,
listagens, log vazio, anotações de ambiente e protótipo visual estático.
O inventário registra caminhos originais/destinos, hashes e commit de origem.
Os bytes publicados foram preservados; o histórico Git não foi reescrito.
Esse arquivamento não altera as cópias de implementação exigidas pelos auditores.
