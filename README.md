
# RAG + RAGAS — Avaliação com Golden Dataset

Projeto exemplo para estudar geração de golden dataset (evaluation set) com RAGAS em uma aplicação RAG real.

## 📁 Estrutura do Projeto

```
rag_ragas_boilerplate/
│
├── README.md
├── requirements.txt
│
├── data/
│   └── sample_docs/          # Coloque seus PDFs/TXTs aqui
│       └── exemplo.txt
│
├── src/
│   ├── rag_pipeline.py       # Pipeline RAG completo (chunking → embedding → retrieval → LLM)
│   ├── golden_dataset.py     # Geração automática do golden dataset com RAGAS
│   └── evaluate.py           # Avaliação do sistema RAG com métricas RAGAS
│
├── outputs/
│   ├── golden_dataset.csv    # Dataset gerado (questions + ground_truth)
│   └── evaluation_scores.csv # Scores das métricas (faithfulness, correctness, etc.)
│
└── notebooks/
    └── walkthrough.ipynb     # Notebook interativo para explorar passo a passo
```

## Início Rápido

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Configurar sua chave OpenAI
export OPENAI_API_KEY="sk-..."

# 3. Gerar o Golden Dataset a partir dos seus documentos
python src/golden_dataset.py

# 4. Rodar a avaliação RAG com o dataset gerado
python src/evaluate.py
```

## Conceitos Estudados

| Etapa | Script | O que faz |
|---|---|---|
| **RAG Pipeline** | `rag_pipeline.py` | Chunking → Embeddings → VectorStore → Retrieval → LLM |
| **Golden Dataset** | `golden_dataset.py` | RAGAS gera Questions + Ground Truth automaticamente |
| **Avaliação** | `evaluate.py` | Calcula Faithfulness, Answer Correctness e outras métricas |

## Métricas Avaliadas

- **Faithfulness** — O LLM usou o contexto recuperado? (Answer ↔ Context)
- **Answer Correctness** — A resposta está certa? (Answer ↔ Ground Truth)
- **Answer Relevance** — A resposta é relevante à pergunta? (Answer ↔ Question)
- **Context Precision** — O contexto recuperado é preciso?
- **Context Recall** — O quanto do contexto necessário foi recuperado?