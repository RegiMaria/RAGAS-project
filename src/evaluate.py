"""
evaluate.py
-----------
Avalia o sistema RAG usando o Golden Dataset gerado pelo RAGAS.

Fluxo:
  1. Carrega o golden_dataset.csv (questions + ground_truth)
  2. Roda cada pergunta no pipeline RAG → obtém answer + contexts
  3. Avalia com métricas RAGAS:
        - Faithfulness       (answer ↔ context)
        - Answer Correctness (answer ↔ ground_truth)
        - Answer Relevance   (answer ↔ question)
        - Context Precision  (context ↔ question + ground_truth)
        - Context Recall     (context ↔ ground_truth)
  4. Salva resultados em outputs/evaluation_scores.csv

Uso:
    # Passo 1: gerar o golden dataset
    python src/golden_dataset.py
    
    # Passo 2: avaliar
    python src/evaluate.py
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

import pandas as pd
from datasets import Dataset

# Métricas RAGAS
from ragas import evaluate
from ragas.metrics.collections import (
    faithfulness,
    answer_correctness,
    answer_relevancy,
    context_precision,
    context_recall,
)

# Pipeline RAG local
sys.path.insert(0, str(Path(__file__).parent))
from rag_pipeline import RAGPipeline

# ─────────────────────────────────────────────
# Configurações
# ─────────────────────────────────────────────
GOLDEN_DATASET_PATH = Path(__file__).parent.parent / "outputs" / "golden_dataset.csv"
OUTPUT_DIR = Path(__file__).parent.parent / "outputs"
OUTPUT_FILE = OUTPUT_DIR / "evaluation_scores.csv"

# Métricas a calcular (remova/adicione conforme necessidade)
METRICS = [
    faithfulness,        # O LLM usou o contexto? (Answer ↔ Context)
    answer_correctness,  # Resposta certa? (Answer ↔ Ground Truth)
    answer_relevancy,    # Resposta relevante? (Answer ↔ Question)
    context_precision,   # Contexto preciso? (Context ↔ Question + GT)
    context_recall,      # Contexto completo? (Context ↔ Ground Truth)
]


# ─────────────────────────────────────────────
# Funções
# ─────────────────────────────────────────────
def load_golden_dataset() -> pd.DataFrame:
    """Carrega o golden dataset gerado anteriormente."""
    if not GOLDEN_DATASET_PATH.exists():
        print(f"❌ Golden Dataset não encontrado em: {GOLDEN_DATASET_PATH}")
        print("   Execute primeiro: python src/golden_dataset.py")
        sys.exit(1)

    df = pd.read_csv(GOLDEN_DATASET_PATH)
    print(f"📊 Golden Dataset carregado: {len(df)} perguntas")
    print(f"   Colunas: {list(df.columns)}\n")
    return df


def run_rag_on_dataset(df: pd.DataFrame, rag: RAGPipeline) -> list[dict]:
    """
    Roda o pipeline RAG em cada pergunta do golden dataset.
    
    Para cada linha do dataset (question + ground_truth), o RAG:
      - recupera os contextos relevantes
      - gera uma resposta
    
    Retorna lista de dicts prontos para o RAGAS avaliar.
    """
    print("🔍 Rodando RAG em todas as perguntas do dataset...")
    print(f"   Total: {len(df)} perguntas\n")

    ragas_data = {
        "question": [],
        "answer": [],
        "contexts": [],      # lista de strings (chunks recuperados)
        "ground_truth": [],
    }

    for i, row in df.iterrows():
        question = row["question"]
        ground_truth = row["ground_truth"]

        print(f"  [{i+1}/{len(df)}] {question[:65]}...")

        # Consulta o RAG
        result = rag.query(question)

        ragas_data["question"].append(question)
        ragas_data["answer"].append(result["answer"])
        ragas_data["contexts"].append(result["contexts"])   # lista de strings
        ragas_data["ground_truth"].append(ground_truth)

    print(f"\n   ✅ RAG executado em {len(df)} perguntas\n")
    return ragas_data


def run_ragas_evaluation(ragas_data: dict) -> pd.DataFrame:
    """
    Avalia os resultados do RAG usando as métricas RAGAS.
    
    Entrada: dict com question, answer, contexts, ground_truth
    Saída: DataFrame com scores por pergunta + médias
    """
    print("📐 Calculando métricas RAGAS...")
    print(f"   Métricas: {[m.name for m in METRICS]}\n")

    # RAGAS espera um HuggingFace Dataset
    dataset = Dataset.from_dict(ragas_data)

    # Avalia!
    result = evaluate(dataset=dataset, metrics=METRICS)

    df_scores = result.to_pandas()
    return df_scores


def print_summary(df_scores: pd.DataFrame):
    """Exibe um resumo dos scores no terminal."""
    metric_cols = [m.name for m in METRICS if m.name in df_scores.columns]

    print("\n" + "=" * 70)
    print("RESUMO DA AVALIAÇÃO RAGAS")
    print("=" * 70)

    # Médias gerais
    print("\n📊 SCORES MÉDIOS:")
    print("-" * 40)
    for col in metric_cols:
        mean_val = df_scores[col].mean()
        bar = "█" * int(mean_val * 20)
        print(f"  {col:<25} {mean_val:.3f}  {bar}")

    # Tabela por pergunta
    print("\n\n📋 SCORES POR PERGUNTA:")
    print("-" * 70)
    for i, row in df_scores.iterrows():
        print(f"\n[{i+1}] ❓ {row['question'][:65]}...")
        for col in metric_cols:
            val = row[col]
            flag = "✅" if val >= 0.7 else ("⚠️ " if val >= 0.4 else "❌")
            print(f"     {flag} {col:<25} {val:.3f}")

    # Diagnóstico: faithfulness baixa com answer_correctness alta
    if "faithfulness" in df_scores.columns and "answer_correctness" in df_scores.columns:
        problematic = df_scores[
            (df_scores["faithfulness"] < 0.5) & (df_scores["answer_correctness"] > 0.6)
        ]
        if len(problematic) > 0:
            print("\n\n⚠️  ATENÇÃO — LLM usando conhecimento próprio (não o contexto):")
            print("   (faithfulness baixa + answer_correctness alta)")
            for _, row in problematic.iterrows():
                print(f"   → {row['question'][:70]}...")


def save_results(df_scores: pd.DataFrame):
    """Salva os scores em CSV."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df_scores.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")
    print(f"\n\n✅ Resultados salvos em: {OUTPUT_FILE}")


# ─────────────────────────────────────────────
# Execução
# ─────────────────────────────────────────────
if __name__ == "__main__":
    # Verifica API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ ANTHROPIC_API_KEY não encontrada!")
        sys.exit(1)

    # 1. Carrega golden dataset
    df_golden = load_golden_dataset()

    # 2. Inicializa e constrói o pipeline RAG
    print("🚀 Inicializando Pipeline RAG...")
    rag = RAGPipeline()
    rag.build()

    # 3. Roda o RAG em todas as perguntas
    ragas_data = run_rag_on_dataset(df_golden, rag)

    # 4. Avalia com RAGAS
    df_scores = run_ragas_evaluation(ragas_data)

    # 5. Exibe resumo
    print_summary(df_scores)

    # 6. Salva resultados
    save_results(df_scores)

    print("\n🎉 Avaliação concluída!")