# PaleographIA: Transcription System for Jundiaí's Historical Archive

*[Ler em Português](README.pt-br.md)*

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14-000000?style=flat-square&logo=nextdotjs&logoColor=white)](https://nextjs.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0-EE4C2C?style=flat-square&logo=pytorch&logoColor=white)](https://pytorch.org/)
[![License MIT](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![CI](https://img.shields.io/github/actions/workflow/status/aj1no/paleographia-htr/ci.yml?branch=main&label=CI&style=flat-square)](https://github.com/aj1no/paleographia-htr/actions)

PaleographIA is a specialized high-performance HTR (Handwritten Text Recognition) system designed specifically for the historical documentation of Jundiaí (1657 - 1889). 

The system leverages state-of-the-art AI architecture (TrOCR) to decipher irregular calligraphy, paper textures from the 17th-19th centuries, and archaic Portuguese terminology.

---

## Key Features

### Deep Calibration for Portuguese Paleography
Unlike generic OCRs, PaleographIA uses a specialized fine-tuning process to understand the nuances of 300-year-old Italian paper texture and the specific cursive styles of regional scribes.
- **Literal Decoding (Greedy Search):** Forced character-by-character interpretation to prevent English-biased hallucinations.
- **Noise Filtering:** Advanced CV2 filters to ignore vergê paper textures and ink stains.

### Hardware Stabilization (CPU Safe Mode)
Designed to run on notebook hardware (16GB RAM / GTX 1050 Ti) without causing system crashes or overheating.
- **Thread Limiting:** Controlled processing power to prevent TDR (Timeout Detection and Recovery) errors.
- **Cooling Pauses:** Wait times between line inferences to keep hardware temperatures stable.

### Expert-First Interface
A distraction-free, high-contrast dark environment designed for long professional transcription sessions.
- **Intelligent Sidebar:** Real-time editor with horizontal/vertical manuscript sync.
- **Segmented Visualization:** Visual overlays on the document to track transcription progress line-by-line.

---

## Project Structure

```text
├── client/          # Next.js Frontend (Expert UI)
├── server/          # FastAPI Backend (AI Inference)
├── data/
│   ├── raw/         # Historical scans
│   └── processed/   # Segmented lines for training
├── models/          # Specialized TrOCR weights (TrOCR-Jundiahy)
└── scripts/         # Automated training & processing scripts
```

---

## Getting Started

1. **Start the Backend:**
   Run the safe starter: `.\start_safe.bat`
   
2. **Start the Frontend:**
   ```bash
   cd client
   npm run dev
   ```

3. **Transcription:**
   Upload a scan, wait for the AI segmentation, and use the Smart Editor to finalize the transcription.

---

## History & Context
This project was developed to preserve and digitalize the history of Jundiaí, providing historians with a powerful assisted transcription tool that respects the complexity of original manuscripts while using modern AI to speed up the process.

---
*Developed for the Jundiaí Historical Archive (1615 - 2026).*
