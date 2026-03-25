"""
evaluate.py
-----------
Avalia o sistema RAG usando o Golden Dataset gerado.

Usa a API clássica do RAGAS (compatível com Anthropic via LangChain).

Uso:
    python src/evaluate.py
"""

import os
import sys
import warnings
warnings.filterwarnings("ignore")  # silencia deprecation warnings do RAGAS/LangChain

from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

import pandas as pd
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_correctness, answer_relevancy, context_precision, context_recall
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_anthropic import ChatAnthropic
from langchain_huggingface import HuggingFaceEmbeddings

sys.path.insert(0, str(Path(__file__).parent))
from rag_pipeline import RAGPipeline

# ─────────────────────────────────────────────
# Configurações
# ─────────────────────────────────────────────
GOLDEN_DATASET_PATH = Path(__file__).parent.parent / "outputs" / "golden_dataset.csv"
OUTPUT_DIR  = Path(__file__).parent.parent / "outputs"
OUTPUT_FILE = OUTPUT_DIR / "evaluation_scores.csv"

METRIC_NAMES = [
    "faithfulness",
    "answer_correctness",
    "answer_relevancy",
    "context_precision",
    "context_recall",
]


def configure_metrics():
    """Configura LLM e embeddings nas métricas globais do RAGAS."""
    ragas_llm = LangchainLLMWrapper(
        ChatAnthropic(model="claude-sonnet-4-6", temperature=0)
    )
    ragas_emb = LangchainEmbeddingsWrapper(
        HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    )

    faithfulness.llm        = ragas_llm
    answer_correctness.llm  = ragas_llm
    answer_relevancy.llm    = ragas_llm
    answer_relevancy.embeddings = ragas_emb
    context_precision.llm   = ragas_llm
    context_recall.llm      = ragas_llm

    return [faithfulness, answer_correctness, answer_relevancy, context_precision, context_recall]


# ─────────────────────────────────────────────
# Funções
# ─────────────────────────────────────────────
def load_golden_dataset():
    if not GOLDEN_DATASET_PATH.exists():
        print(f"❌ Golden Dataset não encontrado em: {GOLDEN_DATASET_PATH}")
        print("   Execute primeiro: python src/golden_dataset.py")
        sys.exit(1)

    df = pd.read_csv(GOLDEN_DATASET_PATH)
    print(f"📊 Golden Dataset carregado: {len(df)} perguntas")
    print(f"   Colunas: {list(df.columns)}\n")
    return df


def run_rag_on_dataset(df, rag):
    print("🔍 Rodando RAG em todas as perguntas do dataset...")
    print(f"   Total: {len(df)} perguntas\n")

    ragas_data = {
        "question":     [],
        "answer":       [],
        "contexts":     [],
        "ground_truth": [],
    }

    for i, row in df.iterrows():
        question     = row["question"]
        ground_truth = row["ground_truth"]

        print(f"  [{i+1}/{len(df)}] {question[:65]}...")
        result = rag.query(question)

        ragas_data["question"].append(question)
        ragas_data["answer"].append(result["answer"])
        ragas_data["contexts"].append(result["contexts"])
        ragas_data["ground_truth"].append(ground_truth)

    print(f"\n   ✅ RAG executado em {len(df)} perguntas\n")
    return ragas_data


def run_ragas_evaluation(ragas_data):
    print("📐 Calculando métricas RAGAS...")
    print(f"   Métricas: {METRIC_NAMES}\n")

    metrics = configure_metrics()
    dataset = Dataset.from_dict(ragas_data)
    result  = evaluate(dataset=dataset, metrics=metrics)
    return result.to_pandas()


def print_summary(df_scores):
    available = [c for c in METRIC_NAMES if c in df_scores.columns]

    print("\n" + "=" * 70)
    print("RESUMO DA AVALIAÇÃO RAGAS")
    print("=" * 70)

    print("\n📊 SCORES MÉDIOS:")
    print("-" * 40)
    for col in available:
        mean_val = df_scores[col].mean()
        bar = "█" * int(mean_val * 20)
        print(f"  {col:<25} {mean_val:.3f}  {bar}")

    print("\n\n📋 SCORES POR PERGUNTA:")
    print("-" * 70)
    for i, row in df_scores.iterrows():
        print(f"\n[{i+1}] ❓ {row['question'][:65]}...")
        for col in available:
            val  = row[col]
            flag = "✅" if val >= 0.7 else ("⚠️ " if val >= 0.4 else "❌")
            print(f"     {flag} {col:<25} {val:.3f}")

    if "faithfulness" in df_scores.columns and "answer_correctness" in df_scores.columns:
        problematic = df_scores[
            (df_scores["faithfulness"] < 0.5) &
            (df_scores["answer_correctness"] > 0.6)
        ]
        if len(problematic) > 0:
            print("\n\n⚠️  ATENÇÃO — LLM usando conhecimento próprio (não o contexto):")
            for _, row in problematic.iterrows():
                print(f"   → {row['question'][:70]}...")


def save_results(df_scores):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df_scores.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")
    print(f"\n\n✅ Resultados salvos em: {OUTPUT_FILE}")


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────
if __name__ == "__main__":
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ ANTHROPIC_API_KEY não encontrada!")
        sys.exit(1)

    df_golden = load_golden_dataset()

    print("🚀 Inicializando Pipeline RAG...")
    rag = RAGPipeline()
    rag.build()

    ragas_data = run_rag_on_dataset(df_golden, rag)
    df_scores  = run_ragas_evaluation(ragas_data)

    print_summary(df_scores)
    save_results(df_scores)

    print("\n🎉 Avaliação concluída!")