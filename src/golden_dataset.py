"""
golden_dataset.py
-----------------
Gera automaticamente um Golden Dataset (Evaluation Set).

Tenta usar a API nova do RAGAS (v0.2+). Se o documento for pequeno
demais e o RAGAS não conseguir gerar perguntas, usa geração direta
via LLM como fallback — garantindo que o dataset seja criado sempre.

Uso:
    python src/golden_dataset.py

Saída:
    outputs/golden_dataset.csv
"""

import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from langchain_anthropic import ChatAnthropic
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import DirectoryLoader, TextLoader
import pandas as pd

DOCS_DIR    = Path(__file__).parent.parent / "data" / "sample_docs"
OUTPUT_DIR  = Path(__file__).parent.parent / "outputs"
OUTPUT_FILE = OUTPUT_DIR / "golden_dataset.csv"

TEST_SIZE = 10


# ─────────────────────────────────────────────
# Carrega documentos
# ─────────────────────────────────────────────
def load_documents():
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


# ─────────────────────────────────────────────
# Tentativa 1: RAGAS TestsetGenerator (API nova)
# ─────────────────────────────────────────────
def try_ragas_generator(docs):
    """
    Tenta gerar com o TestsetGenerator do RAGAS.
    Retorna DataFrame se conseguir, None se falhar ou gerar vazio.
    """
    try:
        print("🧪 Tentando geração automática com RAGAS TestsetGenerator...")

        from ragas.testset import TestsetGenerator
        from ragas.llms import LangchainLLMWrapper
        from ragas.embeddings import LangchainEmbeddingsWrapper

        llm = LangchainLLMWrapper(
            ChatAnthropic(model="claude-haiku-4-5-20251001", temperature=0.3)
        )
        embeddings = LangchainEmbeddingsWrapper(
            HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        )

        generator = TestsetGenerator(llm=llm, embedding_model=embeddings)

        testset = generator.generate_with_langchain_docs(
            documents=docs,
            testset_size=TEST_SIZE,
        )

        df = testset.to_pandas()

        if len(df) == 0:
            print("   ⚠️  RAGAS gerou 0 perguntas (documento pequeno demais). Usando fallback.\n")
            return None

        print(f"   ✅ RAGAS gerou {len(df)} perguntas!\n")
        return df

    except Exception as e:
        print(f"   ⚠️  RAGAS falhou ({type(e).__name__}): {e}\n   Usando fallback.\n")
        return None


# ─────────────────────────────────────────────
# Tentativa 2: Geração direta via LLM (fallback)
# ─────────────────────────────────────────────
def generate_via_llm(docs):
    """
    Fallback: usa o Claude diretamente para gerar perguntas e
    ground truths a partir do texto dos documentos.
    Mais confiável para documentos pequenos.
    """
    print("🤖 Gerando golden dataset via LLM (fallback)...")

    full_text = "\n\n".join([doc.page_content for doc in docs])

    llm = ChatAnthropic(model="claude-sonnet-4-6", temperature=0.3)

    prompt = f"""Você é um especialista em avaliação de sistemas RAG.

Analise o texto abaixo e gere exatamente {TEST_SIZE} pares de pergunta + resposta esperada (ground truth).

Regras:
- As perguntas devem ser variadas: algumas simples/diretas, algumas que exigem raciocínio, algumas que cruzam múltiplas partes do texto
- As respostas (ground_truth) devem ser completas, corretas e baseadas APENAS no texto fornecido
- Cada pergunta deve ter uma resposta clara encontrável no texto
- Varie os temas cobertos pelo texto

Responda SOMENTE com um JSON válido, sem texto adicional, no formato:
[
  {{
    "question": "pergunta aqui",
    "ground_truth": "resposta completa aqui",
    "question_type": "simple|reasoning|multi_context"
  }}
]

TEXTO:
{full_text}
"""

    print(f"   Chamando Claude para gerar {TEST_SIZE} perguntas...")
    response = llm.invoke(prompt)
    raw = response.content.strip()

    # Remove markdown code blocks se existirem
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    try:
        data = json.loads(raw)
        df = pd.DataFrame(data)
        print(f"   ✅ {len(df)} perguntas geradas via LLM!\n")
        return df
    except json.JSONDecodeError as e:
        print(f"   ❌ Erro ao parsear JSON: {e}")
        print(f"   Resposta recebida:\n{raw[:500]}")
        sys.exit(1)


# ─────────────────────────────────────────────
# Preview e save
# ─────────────────────────────────────────────
def preview_dataset(df):
    print("=" * 70)
    print("PRÉVIA DO GOLDEN DATASET GERADO")
    print("=" * 70)

    for i, row in df.iterrows():
        tipo = row.get("question_type", "N/A")
        q    = row.get("question", "—")
        gt   = str(row.get("ground_truth", "—"))[:150]
        print(f"\n[{i+1}] Tipo: {tipo}")
        print(f"    ❓ Pergunta:     {q}")
        print(f"    ✅ Ground Truth: {gt}...")
        print("-" * 70)


def save_golden_dataset(df):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")
    print(f"\n✅ Golden Dataset salvo em: {OUTPUT_FILE}")
    print(f"   Total de registros: {len(df)}")


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────
if __name__ == "__main__":
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ ANTHROPIC_API_KEY não encontrada!")
        print("   Configure: export ANTHROPIC_API_KEY='sk-ant-...'")
        sys.exit(1)

    docs = load_documents()

    # Tenta RAGAS primeiro, usa LLM como fallback
    df = try_ragas_generator(docs)
    if df is None:
        df = generate_via_llm(docs)

    preview_dataset(df)
    save_golden_dataset(df)

    print("\n🎉 Pronto! Use o arquivo gerado como entrada para evaluate.py")