# Histórico preservado

Arquivos `.py.txt` são cópias byte a byte dos scripts legados auditados. Foram conservados para leitura e comparação; não os execute sobre os dados. Eles contêm associação por posição, remoção de diretórios e outros comportamentos substituídos. Os scripts com os nomes antigos, na raiz, agora apontam para comandos seguros da CLI.

`server/main.py` mantém entrada ASGI compatível e delega ao pacote novo. O gitlink `client` não foi removido; a interface mínima atual é servida pelo próprio backend. `metadata.csv`, transcrições antigas e arquivos compactados permanecem intactos, sem validação retroativa.
