# Histórico preservado

Arquivos `.py.txt` são cópias byte a byte dos scripts legados auditados. Foram conservados para leitura e comparação; não os execute sobre os dados. Eles contêm associação por posição, remoção de diretórios e outros comportamentos substituídos. Os scripts com os nomes antigos, na raiz, agora apontam para comandos seguros da CLI.

`server/main.py` mantém entrada ASGI compatível e delega ao pacote novo. O gitlink `client` não foi removido; a interface mínima atual é servida pelo próprio backend. `metadata.csv`, transcrições antigas e arquivos compactados permanecem intactos, sem validação retroativa.

## Auxiliares arquivados em 20/10/2026

Seis arquivos sem dependência encontrada no fluxo atual foram movidos para
[auxiliares_20261020](auxiliares_20261020/README.md): diagnóstico de PDF,
listagens, log vazio, anotações de ambiente e protótipo visual estático.
O inventário registra caminhos originais/destinos, hashes e commit de origem.
Os bytes publicados foram preservados; o histórico Git não foi reescrito.
Esse arquivamento não altera as cópias de implementação exigidas pelos auditores.
