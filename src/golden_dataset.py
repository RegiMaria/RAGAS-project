"""
golden_dataset.py
-----------------
Gera automaticamente um Golden Dataset (Evaluation Set) usando RAGAS.

O RAGAS analisa seus documentos e cria automaticamente:
  - Questions (perguntas variadas sobre o conteúdo)
  - Ground Truth (respostas corretas esperadas)

Tipos de perguntas geradas pelo RAGAS:
  - simple     → perguntas diretas e objetivas
  - reasoning  → perguntas que exigem raciocínio
  - multi_context → perguntas que exigem múltiplos trechos

Uso:
    python src/golden_dataset.py
    
Saída:
    outputs/golden_dataset.csv  ← salvo automaticamente
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ─────────────────────────────────────────────
# Imports RAGAS
# ─────────────────────────────────────────────
from ragas.testset.generator import TestsetGenerator
from ragas.testset.evolutions import simple, reasoning, multi_context
from langchain_anthropic import ChatAnthropic
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import DirectoryLoader, TextLoader
import pandas as pd

# ─────────────────────────────────────────────
# Configurações
# ─────────────────────────────────────────────
DOCS_DIR = Path(__file__).parent.parent / "data" / "sample_docs"
OUTPUT_DIR = Path(__file__).parent.parent / "outputs"
OUTPUT_FILE = OUTPUT_DIR / "golden_dataset.csv"

# Quantas perguntas gerar no total
TEST_SIZE = 10

# Distribuição dos tipos de perguntas (deve somar 1.0)
DISTRIBUTIONS = {
    simple: 0.5,           # 50% perguntas simples e diretas
    reasoning: 0.3,        # 30% perguntas que exigem raciocínio
    multi_context: 0.2,    # 20% perguntas que cruzam múltiplos trechos
}


# ─────────────────────────────────────────────
# Funções
# ─────────────────────────────────────────────
def load_documents():
    """Carrega documentos da pasta de dados."""
    print(f"📂 Carregando documentos de: {DOCS_DIR}")
    loader = DirectoryLoader(
        str(DOCS_DIR),
        glob="**/*.txt",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
    )
    docs = loader.load()
    print(f"   ✅ {len(docs)} documento(s) carregado(s)\n")
    return docs


def generate_golden_dataset(docs) -> pd.DataFrame:
    """
    Usa o TestsetGenerator do RAGAS para gerar perguntas e ground truth
    automaticamente a partir dos documentos fornecidos.
    
    O RAGAS usa:
      - generator_llm  → para gerar as perguntas
      - critic_llm     → para filtrar/melhorar as perguntas geradas
      - embeddings     → para entender similaridade semântica entre chunks
    """
    print("🧪 Iniciando geração do Golden Dataset com RAGAS...")
    print(f"   Tamanho alvo: {TEST_SIZE} perguntas")
    print(f"   Distribuição: simple={DISTRIBUTIONS[simple]}, "
          f"reasoning={DISTRIBUTIONS[reasoning]}, "
          f"multi_context={DISTRIBUTIONS[multi_context]}\n")

    # LLMs usados pelo RAGAS internamente
    generator_llm = ChatAnthropic(model="claude-haiku-4-5-20251001", temperature=0.3)
    critic_llm = ChatAnthropic(model="claude-sonnet-4-6", temperature=0)  # modelo mais forte para crítica
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    # Cria o gerador
    generator = TestsetGenerator.from_langchain(
        generator_llm=generator_llm,
        critic_llm=critic_llm,
        embeddings=embeddings,
    )

    # Gera o testset
    testset = generator.generate_with_langchain_docs(
        documents=docs,
        test_size=TEST_SIZE,
        distributions=DISTRIBUTIONS,
        with_debugging_logs=False,  # mude para True para ver logs detalhados
    )

    # Converte para DataFrame
    df = testset.to_pandas()
    return df


def save_golden_dataset(df: pd.DataFrame):
    """Salva o dataset gerado em CSV."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")
    print(f"\n✅ Golden Dataset salvo em: {OUTPUT_FILE}")
    print(f"   Total de registros: {len(df)}")


def preview_dataset(df: pd.DataFrame):
    """Exibe uma prévia do dataset gerado no terminal."""
    print("\n" + "=" * 70)
    print("PRÉVIA DO GOLDEN DATASET GERADO")
    print("=" * 70)

    cols_to_show = ["question", "ground_truth", "question_type"]
    cols_available = [c for c in cols_to_show if c in df.columns]

    for i, row in df[cols_available].iterrows():
        print(f"\n[{i+1}] Tipo: {row.get('question_type', 'N/A')}")
        print(f"    ❓ Pergunta:     {row['question']}")
        print(f"    ✅ Ground Truth: {row['ground_truth'][:150]}...")
        print("-" * 70)


# ─────────────────────────────────────────────
# Execução
# ─────────────────────────────────────────────
if __name__ == "__main__":
    # Verifica API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ ANTHROPIC_API_KEY não encontrada!")
        print("   Configure: export ANTHROPIC_API_KEY='sk-ant-...'")
        sys.exit(1)

    # Fluxo principal
    docs = load_documents()
    df = generate_golden_dataset(docs)
    preview_dataset(df)
    save_golden_dataset(df)

    print("\n🎉 Pronto! Use o arquivo gerado como entrada para evaluate.py")