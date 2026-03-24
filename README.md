# RAG + RAGAS — Avaliação com Golden Dataset

Projeto exemplo para estudar geração de golden dataset (evaluation set) com RAGAS em uma aplicação RAG real, usando modelos **Claude da Anthropic**.

## Como funciona

```
Documentos (data/sample_docs/)
        ↓
  RAG Pipeline (src/rag_pipeline.py)
  • Divide em chunks (500 chars, overlap 50)
  • Gera embeddings locais (HuggingFace, sem custo de API)
  • Armazena no ChromaDB (local, persistido)
  • Responde perguntas via Claude Haiku
        ↓
  Golden Dataset (src/golden_dataset.py)
  • RAGAS gera perguntas + ground truth automaticamente
  • Tipos: simples, raciocínio, multi-contexto
  • Salvo em outputs/golden_dataset.csv
        ↓
  Avaliação (src/evaluate.py)
  • Roda o RAG em cada pergunta do dataset
  • Calcula 5 métricas RAGAS
  • Salvo em outputs/evaluation_scores.csv
```

## Estrutura do Projeto

```
RAGAS-Project/
├── src/
│   ├── rag_pipeline.py       # Pipeline RAG completo
│   ├── golden_dataset.py     # Geração do golden dataset com RAGAS
│   └── evaluate.py           # Avaliação com métricas RAGAS
│
├── data/
│   └── sample_docs/          # Coloque seus .txt ou .pdf aqui
│       └── historia_ia.txt   # Documento de exemplo incluído
│
├── outputs/                  # Criado automaticamente ao rodar os scripts
│   ├── golden_dataset.csv    # Perguntas + ground truth gerados
│   └── evaluation_scores.csv # Scores por pergunta
│
├── notebooks/
│   └── walkthrough.ipynb     # Guia interativo passo a passo
│
├── requirements.txt
└── .env                      # Chave de API (não commitado)
```

## Pré-requisitos

- Python 3.10+
- Conta na [Anthropic](https://console.anthropic.com/) com créditos disponíveis

## Instalação

```bash
# 1. Clonar o repositório
git clone https://github.com/RegiMaria/RAGAS-project.git
cd RAGAS-Project

# 2. Criar e ativar ambiente virtual
python -m venv venv
source venv/bin/activate      # Linux/Mac
# venv\Scripts\activate       # Windows

# 3. Instalar dependências
pip install -r requirements.txt

# 4. Configurar a chave da API
cp .env.example .env
# Editar .env e adicionar: ANTHROPIC_API_KEY="sk-ant-..."
```

## Uso

```bash
# Passo 1 (opcional): testar o pipeline RAG diretamente
python src/rag_pipeline.py

# Passo 2: gerar o golden dataset a partir dos seus documentos
python src/golden_dataset.py

# Passo 3: avaliar o sistema RAG
python src/evaluate.py
```

Ou explore o fluxo completo no notebook interativo:
```bash
jupyter notebook notebooks/walkthrough.ipynb
```

## Modelos Utilizados

| Papel | Modelo | Motivo |
|---|---|---|
| Geração de respostas RAG | `claude-haiku-4-5` | Rápido e econômico |
| Geração de perguntas (RAGAS) | `claude-haiku-4-5` | Volume alto de chamadas |
| Crítica das perguntas (RAGAS) | `claude-sonnet-4-6` | Maior qualidade para filtragem |
| Embeddings | `all-MiniLM-L6-v2` | Roda localmente, sem custo de API |

## Métricas RAGAS

| Métrica | Compara | Mede |
|---|---|---|
| **Faithfulness** | Resposta ↔ Contexto | O LLM usou o contexto ou inventou? |
| **Answer Correctness** | Resposta ↔ Ground Truth | A resposta está correta? |
| **Answer Relevance** | Resposta ↔ Pergunta | A resposta é relevante à pergunta? |
| **Context Precision** | Contexto ↔ Pergunta+GT | O contexto recuperado é preciso? |
| **Context Recall** | Contexto ↔ Ground Truth | O contexto necessário foi recuperado? |

### Interpretando os Scores

- **>= 0.7** — Bom
- **0.4 a 0.7** — Atenção
- **< 0.4** — Problema

O `evaluate.py` detecta automaticamente casos onde `faithfulness < 0.5` e `answer_correctness > 0.6` — sinal de que o LLM está usando conhecimento próprio em vez do contexto recuperado (alucinação fundamentada).

## Adicionando seus próprios documentos

Coloque arquivos `.txt` ou `.pdf` em `data/sample_docs/` e rode novamente os scripts. O ChromaDB é reconstruído automaticamente se não existir.

Para forçar a reconstrução do índice:
```python
rag = RAGPipeline()
rag.build(force_rebuild=True)
```
## Referências

- HUYEN, Chip. *AI Engineering*. Sebastopol: O'Reilly Media, 2024.  
  [Acessar conteúdo](https://learning.oreilly.com/library/view/ai-engineering/9781098166298/ch06.html)

- RAGAS. *Faithfulness Metric*.  
  [Documentação](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/faithfulness/)

- RAGAS. *Answer Relevance Metric*.  
  [Documentação](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/answer_relevance/)

- RAGAS. *Context Recall Metric*.  
  [Documentação](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/context_recall/)

- RAGAS. *Context Precision Metric*.  
  [Documentação](https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/context_precision/)

- DHANAKOTTI, Karthikeyan. *RAGAS for RAG in LLMs: A Comprehensive Guide to Evaluation Metrics*. Medium, 2024.  
  [Ler artigo](https://dkaarthick.medium.com/ragas-for-rag-in-llms-a-comprehensive-guide-to-evaluation-metrics-3aca142d6e38)

- GARSON, Jessica. *Evaluating your Elasticsearch LLM Applications with Ragas*. Elastic, 2025.  
  [Ler artigo](https://www.elastic.co/search-labs/blog/elasticsearch-ragas-llm-app-evaluation)

- ES, Shahul et al. *Ragas: Automated Evaluation of Retrieval Augmented Generation*. EACL, 2024.  
  [Acessar paper](https://aclanthology.org/2024.eacl-demo.16/)

- SHELTON, Robert. *Get Better RAG Responses with Ragas*. Redis Blog, 2024.  
  [Ler artigo](https://redis.io/blog/get-better-rag-responses-with-ragas/)