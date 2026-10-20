# Auxiliares históricos arquivados — 20/10/2026

Seis arquivos foram retirados dos caminhos operacionais e preservados neste
diretório, por autorização do responsável. A aplicação atual não depende deles.
Não são instruções de instalação, conjunto de treino ou resultado de avaliação.

| Caminho original | Destino nesta pasta | Motivo |
| --- | --- | --- |
| `test_encoding.py` | [test_encoding.py.txt](test_encoding.py.txt) | Diagnóstico antigo de PDF; extensão de texto para leitura histórica |
| `downloads_list.txt` | [downloads_list.txt](downloads_list.txt) | Listagem auxiliar antiga |
| `downloads_utf8.txt` | [downloads_utf8.txt](downloads_utf8.txt) | Outra listagem auxiliar |
| `train_log.txt` | [train_log.txt](train_log.txt) | Log vazio preservado |
| `server/Texto importantes.txt` | [server/Texto importantes.txt](<server/Texto importantes.txt>) | Anotações de ambiente antigo |
| `index.html` da raiz | [index.html](index.html) | Protótipo visual estático, distinto do editor atual |

O HTML conserva números, textos e indicadores ilustrativos de sua criação.
**Não representa métricas, funcionalidades ou leituras humanas atuais.** A tela
ativa está em `src/paleographia/web/`; o servidor de compatibilidade
`server/main.py` continua no lugar. O diagnóstico de PDF foi preservado como
texto e não faz parte da suíte de testes atual.

## Bytes, caminhos e histórico

O [inventário](inventario.json) registra seis pares de caminhos, motivo,
tamanho, SHA-256 e identificador do blob no commit
`398aafafce895c104a6f16d69167453213cdc50d`. Os arquivos arquivados têm os
**mesmos bytes dos blobs publicados nesse commit**, sem reformatar ou recodificar.
Os hashes e tamanhos do checkout Windows anterior também foram registrados:
em quatro arquivos, o Git havia convertido LF para CRLF. Essa diferença é
distinta de alteração de conteúdo. `.gitattributes` impede nova conversão
automática neste diretório.

O arquivamento é um novo commit na `codex/refatoracao-piloto`, com movimentações
rastreáveis; não reescreve commits nem altera `main`. Os caminhos anteriores
continuam recuperáveis pelo commit de origem. As implementações congeladas,
originais, revisões e evidências acadêmicas não foram movidas.

## Conferir

Na raiz do repositório, com Python 3.11 ou 3.12 e histórico Git disponível:

```powershell
python legacy/auxiliares_20261020/verificar.py
```

O verificador usa somente a biblioteca padrão e o Git. Compara os seis arquivos
com o inventário e os blobs de origem; não executa o diagnóstico ou o HTML.
Não exige modelo ou acesso à rede. A CI faz essa auditoria nas quatro combinações
Windows/Ubuntu e Python 3.11/3.12, com histórico completo no checkout.

O [recibo de validação](validacao.json) registra testes, auditorias e preservação
desta entrega. O inventário cobre os seis arquivos históricos; o recibo e este
guia são documentação nova, mantida separadamente dos originais.
