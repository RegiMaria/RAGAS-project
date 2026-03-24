"""
rag_pipeline.py
---------------
Pipeline RAG completo:
  1. Carrega documentos da pasta data/sample_docs/
  2. Divide em chunks
  3. Gera embeddings e armazena no ChromaDB (local)
  4. Recupera contexto relevante para uma pergunta
  5. Chama o LLM para gerar a resposta final

Uso:
    python src/rag_pipeline.py
    ou importe RAGPipeline em outros scripts.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_anthropic import ChatAnthropic
from langchain_community.vectorstores import Chroma
from langchain_classic.chains import RetrievalQA
from langchain_core.documents import Document

load_dotenv()  # carrega ANTHROPIC_API_KEY do arquivo .env


# ─────────────────────────────────────────────
# Configurações
# ─────────────────────────────────────────────
DOCS_DIR = Path(__file__).parent.parent / "data" / "sample_docs"
CHROMA_DIR = Path(__file__).parent.parent / "data" / "chroma_db"

CHUNK_SIZE = 500                      # tamanho de cada chunk em caracteres
CHUNK_OVERLAP = 50                    # sobreposição entre chunks
TOP_K_RETRIEVAL = 3                   # quantos chunks recuperar por pergunta
LLM_MODEL = "claude-haiku-4-5-20251001"  # modelo Anthropic a usar


# ─────────────────────────────────────────────
# Classe principal
# ─────────────────────────────────────────────
class RAGPipeline:
    """
    Pipeline RAG reutilizável.
    
    Exemplo de uso:
        rag = RAGPipeline()
        rag.build()
        result = rag.query("Quando foi cunhado o termo inteligência artificial?")
        print(result["answer"])
        print(result["contexts"])
    """

    def __init__(self):
        # Embeddings gratuitos via HuggingFace (roda localmente, sem API key)
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.llm = ChatAnthropic(model=LLM_MODEL, temperature=0)
        self.vectorstore = None
        self.retriever = None
        self.qa_chain = None

    # ── 1. Carregar documentos ──────────────────
    def load_documents(self) -> list[Document]:
        """Carrega todos os .txt e .pdf da pasta de dados."""
        print(f"📂 Carregando documentos de: {DOCS_DIR}")

        loader = DirectoryLoader(
            str(DOCS_DIR),
            glob="**/*.txt",
            loader_cls=TextLoader,
            loader_kwargs={"encoding": "utf-8"},
            show_progress=True,
        )
        docs = loader.load()
        print(f"   ✅ {len(docs)} arquivo(s) carregado(s)")
        return docs

    # ── 2. Dividir em chunks ────────────────────
    def split_documents(self, docs: list[Document]) -> list[Document]:
        """Divide documentos em chunks menores."""
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            separators=["\n\n", "\n", ". ", " ", ""],
        )
        chunks = splitter.split_documents(docs)
        print(f"   ✅ {len(chunks)} chunks gerados (tamanho={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})")
        return chunks

    # ── 3. Criar / carregar VectorStore ────────
    def build_vectorstore(self, chunks: list[Document]) -> Chroma:
        """Cria embeddings e persiste no ChromaDB local."""
        print(f"🔢 Gerando embeddings e armazenando em: {CHROMA_DIR}")
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=self.embeddings,
            persist_directory=str(CHROMA_DIR),
        )
        print(f"   ✅ VectorStore criado com {vectorstore._collection.count()} vetores")
        return vectorstore

    def load_vectorstore(self) -> Chroma:
        """Carrega um VectorStore já existente (evita reprocessar)."""
        print(f"📦 Carregando VectorStore existente de: {CHROMA_DIR}")
        return Chroma(
            persist_directory=str(CHROMA_DIR),
            embedding_function=self.embeddings,
        )

    # ── 4. Montar pipeline completo ─────────────
    def build(self, force_rebuild: bool = False):
        """
        Monta o pipeline completo.
        Se o ChromaDB já existir, reutiliza (a menos que force_rebuild=True).
        """
        if CHROMA_DIR.exists() and not force_rebuild:
            self.vectorstore = self.load_vectorstore()
        else:
            docs = self.load_documents()
            chunks = self.split_documents(docs)
            self.vectorstore = self.build_vectorstore(chunks)

        self.retriever = self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": TOP_K_RETRIEVAL},
        )

        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",           # "stuff" = concatena todos os chunks no prompt
            retriever=self.retriever,
            return_source_documents=True,  # retorna os chunks usados
        )
        print("🚀 Pipeline RAG pronto!\n")

    # ── 5. Consultar ────────────────────────────
    def query(self, question: str) -> dict:
        """
        Faz uma pergunta ao sistema RAG.
        
        Retorna:
            {
                "question": str,
                "answer": str,
                "contexts": list[str],   # textos dos chunks recuperados
                "sources": list[str],    # caminhos dos arquivos fonte
            }
        """
        if not self.qa_chain:
            raise RuntimeError("Pipeline não iniciado. Chame .build() primeiro.")

        result = self.qa_chain.invoke({"query": question})

        contexts = [doc.page_content for doc in result["source_documents"]]
        sources = [doc.metadata.get("source", "desconhecido") for doc in result["source_documents"]]

        return {
            "question": question,
            "answer": result["result"],
            "contexts": contexts,
            "sources": sources,
        }

    # ── 6. Consultas em batch ───────────────────
    def query_batch(self, questions: list[str]) -> list[dict]:
        """Faz múltiplas perguntas e retorna lista de resultados."""
        results = []
        for i, q in enumerate(questions, 1):
            print(f"  [{i}/{len(questions)}] {q[:60]}...")
            results.append(self.query(q))
        return results


# ─────────────────────────────────────────────
# Execução direta (teste rápido)
# ─────────────────────────────────────────────
if __name__ == "__main__":
    rag = RAGPipeline()
    rag.build()

    perguntas_teste = [
        "Quando foi cunhado o termo inteligência artificial?",
        "O que foi o Inverno da IA?",
        "Quantos parâmetros tem o GPT-3?",
        "Como o ChatGPT cresceu rapidamente?",
    ]

    print("=" * 60)
    print("TESTE DO PIPELINE RAG")
    print("=" * 60)

    for pergunta in perguntas_teste:
        resultado = rag.query(pergunta)
        print(f"\n❓ Pergunta: {resultado['question']}")
        print(f"💬 Resposta: {resultado['answer']}")
        print(f"📄 Contextos ({len(resultado['contexts'])} chunks):")
        for i, ctx in enumerate(resultado["contexts"], 1):
            print(f"   [{i}] {ctx[:120]}...")
        print("-" * 60)