# PaleographIA: Sistema de Transcrição para o Arquivo Histórico de Jundiaí

*[Read in English](README.md)*

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14-000000?style=flat-square&logo=nextdotjs&logoColor=white)](https://nextjs.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0-EE4C2C?style=flat-square&logo=pytorch&logoColor=white)](https://pytorch.org/)
[![License MIT](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![CI](https://img.shields.io/github/actions/workflow/status/aj1no/paleographia-htr/ci.yml?branch=main&label=CI&style=flat-square)](https://github.com/aj1no/paleographia-htr/actions)

PaleographIA é um sistema especializado de HTR (Handwritten Text Recognition - Reconhecimento de Texto Manuscrito) de alto desempenho, projetado especificamente para a documentação histórica de Jundiaí (1657 - 1889).

O sistema utiliza a arquitetura de IA de última geração (TrOCR) para decifrar caligrafias irregulares, texturas de papel dos séculos XVII a XIX e terminologias arcaicas em português.

---

## Principais Funcionalidades

### Calibração Profunda para Paleografia em Português
Diferente de OCRs genéricos, o PaleographIA utiliza um processo de ajuste fino especializado para compreender as nuances das texturas de papéis italianos de 300 anos e os estilos específicos de escrita cursiva dos escrivães regionais.
- **Decodificação Literal (Greedy Search):** Interpretação forçada caractere por caractere para evitar alucinações baseadas em inglês.
- **Filtragem de Ruído:** Filtros avançados com OpenCV para ignorar texturas de papel vergê e manchas de tinta.

### Estabilização de Hardware (Modo Seguro para CPU)
Projetado para rodar em notebooks (16GB RAM / GTX 1050 Ti) sem causar travamentos no sistema ou superaquecimento.
- **Limitação de Threads:** Controle de poder de processamento para evitar erros de TDR (Timeout Detection and Recovery).
- **Pausas de Resfriamento:** Intervalos de espera entre inferências de linha para manter a temperatura do hardware estável.

### Interface Focada no Especialista
Um ambiente escuro de alto contraste, livre de distrações, projetado para longas sessões de transcrição profissional.
- **Barra Lateral Inteligente:** Editor em tempo real com sincronização horizontal e vertical do manuscrito.
- **Visualização Segmentada:** Sobreposições visuais no documento para acompanhar o progresso da transcrição linha por linha.

---

## Estrutura do Projeto

```text
├── client/          # Frontend Next.js (Interface de Especialista)
├── server/          # Backend FastAPI (Inferência de IA)
├── data/
│   ├── raw/         # Digitalizações históricas
│   └── processed/   # Linhas segmentadas para treinamento
├── models/          # Pesos especializados TrOCR (TrOCR-Jundiahy)
└── scripts/         # Scripts automatizados de treinamento e processamento
```

---

## Como Começar

1. **Iniciar o Backend:**
   Execute o script de inicialização segura: `.\start_safe.bat`
   
2. **Iniciar o Frontend:**
   ```bash
   cd client
   npm run dev
   ```

3. **Transcrição:**
   Faça o upload de uma digitalização, aguarde a segmentação por IA e utilize o Editor Inteligente para finalizar a transcrição.

---

## História & Contexto
Este projeto foi desenvolvido para preservar e digitalizar a história de Jundiaí, fornecendo aos historiadores uma ferramenta poderosa de transcrição assistida que respeita a complexidade dos manuscritos originais enquanto utiliza IA moderna para acelerar o processo.

---
*Desenvolvido para o Arquivo Histórico de Jundiaí (1615 - 2026).*
