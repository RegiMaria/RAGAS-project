# RAGAS-Project
### Relatório Técnico — Avaliação de Sistemas RAG com RAGAS Framework

---

## Sumário

1. [Visão Geral](#visão-geral)
2. [Bibliotecas Utilizadas](#bibliotecas-utilizadas)
3. [Por Que Fizemos o Downgrade](#por-que-fizemos-o-downgrade)
4. [Por Que Precisamos da API da OpenAI](#por-que-precisamos-da-api-da-openai)
5. [Análise da Configuração](#análise-da-configuração)
6. [Resultados Obtidos](#resultados-obtidos)

---

## Visão Geral

O **RAGAS-Project** é um projeto de estudo focado em avaliar a qualidade de sistemas RAG *(Retrieval-Augmented Generation)* de forma sistemática e automatizada.

O objetivo central é demonstrar que **construir um pipeline RAG é apenas metade do trabalho**, avaliar se ele está funcionando corretamente é igualmente essencial. A maioria dos projetos monta o pipeline e para por aí, sem saber se o modelo está realmente usando os documentos ou simplesmente inventando respostas corretas por acaso.

O projeto utiliza o framework **RAGAS** para:

- Gerar automaticamente um **golden dataset** (conjunto de avaliação) a partir dos documentos do sistema
- Medir **5 métricas distintas** para diagnosticar problemas tanto no componente de recuperação quanto no de geração
- Identificar o padrão crítico de **faithfulness baixa + correctness alta** — quando o LLM acerta mas sem usar o contexto

---

## Bibliotecas Utilizadas

<table>
  <thead>
    <tr>
      <th style="background:#1F3864;color:#fff;padding:10px 14px;">Biblioteca</th>
      <th style="background:#1F3864;color:#fff;padding:10px 14px;">Versão</th>
      <th style="background:#1F3864;color:#fff;padding:10px 14px;">Atividade</th>
      <th style="background:#1F3864;color:#fff;padding:10px 14px;">O que faz</th>
    </tr>
  </thead>
  <tbody>
    <tr style="background:#f0f4ff;">
      <td style="padding:9px 14px;font-weight:600;color:#1F3864;">ragas</td>
      <td style="padding:9px 14px;font-family:monospace;">0.1.21</td>
      <td style="padding:9px 14px;"><span style="background:#dbeafe;color:#1e40af;padding:2px 8px;border-radius:12px;font-size:13px;">Avaliação</span></td>
      <td style="padding:9px 14px;">Framework principal. Gera o golden dataset e calcula as 5 métricas de qualidade do RAG.</td>
    </tr>
    <tr>
      <td style="padding:9px 14px;font-weight:600;color:#1F3864;">langchain</td>
      <td style="padding:9px 14px;font-family:monospace;">0.2.17</td>
      <td style="padding:9px 14px;"><span style="background:#dcfce7;color:#166534;padding:2px 8px;border-radius:12px;font-size:13px;">Pipeline RAG</span></td>
      <td style="padding:9px 14px;">Orquestra o pipeline: conecta carregadores, splitters, vector store e LLM em uma cadeia.</td>
    </tr>
    <tr style="background:#f0f4ff;">
      <td style="padding:9px 14px;font-weight:600;color:#1F3864;">langchain-core</td>
      <td style="padding:9px 14px;font-family:monospace;">0.2.43</td>
      <td style="padding:9px 14px;"><span style="background:#f3f4f6;color:#374151;padding:2px 8px;border-radius:12px;font-size:13px;">Infraestrutura</span></td>
      <td style="padding:9px 14px;">Base do ecossistema LangChain. Define interfaces e tipos usados por todos os pacotes <code>langchain-*</code>.</td>
    </tr>
    <tr>
      <td style="padding:9px 14px;font-weight:600;color:#1F3864;">langchain-anthropic</td>
      <td style="padding:9px 14px;font-family:monospace;">0.1.23</td>
      <td style="padding:9px 14px;"><span style="background:#fef3c7;color:#92400e;padding:2px 8px;border-radius:12px;font-size:13px;">LLM</span></td>
      <td style="padding:9px 14px;">Integração com a API da Anthropic. Permite usar o Claude como LLM no pipeline RAG e nas métricas.</td>
    </tr>
    <tr style="background:#f0f4ff;">
      <td style="padding:9px 14px;font-weight:600;color:#1F3864;">langchain-community</td>
      <td style="padding:9px 14px;font-family:monospace;">0.2.19</td>
      <td style="padding:9px 14px;"><span style="background:#dcfce7;color:#166534;padding:2px 8px;border-radius:12px;font-size:13px;">Pipeline RAG</span></td>
      <td style="padding:9px 14px;">Integrações da comunidade LangChain: <code>DirectoryLoader</code>, <code>TextLoader</code> e <code>Chroma</code>.</td>
    </tr>
    <tr>
      <td style="padding:9px 14px;font-weight:600;color:#1F3864;">langchain-huggingface</td>
      <td style="padding:9px 14px;font-family:monospace;">0.0.3</td>
      <td style="padding:9px 14px;"><span style="background:#ede9fe;color:#5b21b6;padding:2px 8px;border-radius:12px;font-size:13px;">Embeddings</span></td>
      <td style="padding:9px 14px;">Integração com modelos HuggingFace. Fornece os embeddings locais — sem custo de API.</td>
    </tr>
    <tr style="background:#f0f4ff;">
      <td style="padding:9px 14px;font-weight:600;color:#1F3864;">sentence-transformers</td>
      <td style="padding:9px 14px;font-family:monospace;">3.0.0</td>
      <td style="padding:9px 14px;"><span style="background:#ede9fe;color:#5b21b6;padding:2px 8px;border-radius:12px;font-size:13px;">Embeddings</span></td>
      <td style="padding:9px 14px;">Roda o modelo <code>all-MiniLM-L6-v2</code> localmente. Converte texto em vetores numéricos.</td>
    </tr>
    <tr>
      <td style="padding:9px 14px;font-weight:600;color:#1F3864;">chromadb</td>
      <td style="padding:9px 14px;font-family:monospace;">0.5.0</td>
      <td style="padding:9px 14px;"><span style="background:#dcfce7;color:#166534;padding:2px 8px;border-radius:12px;font-size:13px;">Pipeline RAG</span></td>
      <td style="padding:9px 14px;">Banco de dados vetorial local. Armazena embeddings dos chunks e realiza buscas por similaridade.</td>
    </tr>
    <tr style="background:#f0f4ff;">
      <td style="padding:9px 14px;font-weight:600;color:#1F3864;">datasets</td>
      <td style="padding:9px 14px;font-family:monospace;">2.20.0</td>
      <td style="padding:9px 14px;"><span style="background:#dbeafe;color:#1e40af;padding:2px 8px;border-radius:12px;font-size:13px;">Avaliação</span></td>
      <td style="padding:9px 14px;">Biblioteca HuggingFace para datasets. O RAGAS exige que os dados sejam fornecidos neste formato.</td>
    </tr>
    <tr>
      <td style="padding:9px 14px;font-weight:600;color:#1F3864;">anthropic</td>
      <td style="padding:9px 14px;font-family:monospace;">0.28.0</td>
      <td style="padding:9px 14px;"><span style="background:#fef3c7;color:#92400e;padding:2px 8px;border-radius:12px;font-size:13px;">LLM</span></td>
      <td style="padding:9px 14px;">SDK oficial da Anthropic. Camada de baixo nível usada pelo <code>langchain-anthropic</code>.</td>
    </tr>
    <tr style="background:#f0f4ff;">
      <td style="padding:9px 14px;font-weight:600;color:#1F3864;">openai / langchain-openai</td>
      <td style="padding:9px 14px;font-family:monospace;">pinados</td>
      <td style="padding:9px 14px;"><span style="background:#fee2e2;color:#991b1b;padding:2px 8px;border-radius:12px;font-size:13px;">Dependência indireta</span></td>
      <td style="padding:9px 14px;">Necessários internamente pelo RAGAS 0.1.21 para calcular embeddings durante a avaliação das métricas.</td>
    </tr>
    <tr>
      <td style="padding:9px 14px;font-weight:600;color:#1F3864;">python-dotenv</td>
      <td style="padding:9px 14px;font-family:monospace;">1.0.0</td>
      <td style="padding:9px 14px;"><span style="background:#f3f4f6;color:#374151;padding:2px 8px;border-radius:12px;font-size:13px;">Infraestrutura</span></td>
      <td style="padding:9px 14px;">Carrega variáveis do <code>.env</code> (<code>ANTHROPIC_API_KEY</code>, <code>OPENAI_API_KEY</code>).</td>
    </tr>
    <tr style="background:#f0f4ff;">
      <td style="padding:9px 14px;font-weight:600;color:#1F3864;">pandas</td>
      <td style="padding:9px 14px;font-family:monospace;">2.0.0</td>
      <td style="padding:9px 14px;"><span style="background:#dbeafe;color:#1e40af;padding:2px 8px;border-radius:12px;font-size:13px;">Avaliação</span></td>
      <td style="padding:9px 14px;">Manipula os scores retornados pelo RAGAS e salva o CSV final de resultados.</td>
    </tr>
  </tbody>
</table>

---

## Por Que Fizemos o Downgrade

### Versão inicial — RAGAS 0.4.3

O projeto foi iniciado com a versão mais recente disponível do RAGAS (0.4.3). Essa versão introduziu uma API completamente nova chamada `ragas.metrics.collections`, com classes instanciadas em vez de objetos globais.

**O problema:** a API nova só aceita o `llm_factory` próprio do RAGAS, que suporta exclusivamente OpenAI. Qualquer tentativa de passar o Claude gerava:

```
ValueError: Collections metrics only support modern InstructorLLM.
Found: LangchainLLMWrapper. Use: llm_factory('gpt-4o-mini', ...)
```

### Tentativas intermediárias

Antes de decidir pelo downgrade, foram testadas três abordagens:

| Tentativa | Resultado |
|-----------|-----------|
| Usar `ragas.metrics` (API antiga) com RAGAS 0.4.3 | O `aevaluate()` interno chamava `embedding_factory` hardcoded para OpenAI |
| Passar embeddings HuggingFace via `LangchainEmbeddingsWrapper` | Ignorado — o RAGAS tentava OpenAI mesmo assim |
| Usar `HuggingFaceEmbeddings` nativo do RAGAS | A classe `collections` rejeitava o `LangchainLLMWrapper` antes de chegar nos embeddings |

### Solução — downgrade para RAGAS 0.1.21

A versão 0.1.21 usa a API clássica com objetos globais (`faithfulness`, `answer_correctness` etc.) que aceitam qualquer LLM via `LangchainLLMWrapper`, incluindo o Claude.

O downgrade gerou **conflitos em cascata** de dependências — o pip resolveu automaticamente para versões antigas do LangChain, quebrando o `langchain-anthropic` novo. A solução foi **recriar o ambiente virtual do zero** com todas as versões pinadas e compatíveis entre si.

```
ragas 0.4.3       → exigia langchain-core 1.x
ragas 0.1.21      → puxou langchain-core 0.2.x
langchain-core 0.2.x → quebrou langchain-anthropic 1.4.0
```

**Resolução:** recriação do venv com versões pinadas explicitamente no `requirements.txt`.

---

## Por Que Precisamos da API da OpenAI

Mesmo usando o Claude (Anthropic) como LLM principal e como avaliador nas métricas, **a OpenAI ainda é necessária por um motivo específico**.

### O que a OpenAI faz no projeto

O RAGAS 0.1.21, internamente na função `aevaluate()`, chama `embedding_factory()` que instancia um `OpenAIEmbeddings` para calcular similaridade semântica durante a avaliação. Esse comportamento está **hardcoded no código-fonte do RAGAS** — não é configurável sem modificar a biblioteca.

Especificamente, a métrica **Answer Relevancy** precisa calcular a similaridade entre a pergunta original e a resposta gerada. Para isso, o RAGAS converte ambos em vetores usando o modelo `text-embedding-ada-002` da OpenAI.

<table>
  <thead>
    <tr>
      <th style="background:#1F3864;color:#fff;padding:10px 14px;">Componente</th>
      <th style="background:#1F3864;color:#fff;padding:10px 14px;">Usa Anthropic</th>
      <th style="background:#1F3864;color:#fff;padding:10px 14px;">Usa OpenAI</th>
      <th style="background:#1F3864;color:#fff;padding:10px 14px;">Modelo</th>
    </tr>
  </thead>
  <tbody>
    <tr style="background:#f0f4ff;">
      <td style="padding:9px 14px;">Pipeline RAG — geração de respostas</td>
      <td style="padding:9px 14px;text-align:center;">✅</td>
      <td style="padding:9px 14px;text-align:center;">—</td>
      <td style="padding:9px 14px;font-family:monospace;font-size:13px;">claude-haiku-4-5</td>
    </tr>
    <tr>
      <td style="padding:9px 14px;">Embeddings do VectorStore (ChromaDB)</td>
      <td style="padding:9px 14px;text-align:center;">—</td>
      <td style="padding:9px 14px;text-align:center;">—</td>
      <td style="padding:9px 14px;font-family:monospace;font-size:13px;">all-MiniLM-L6-v2 (local)</td>
    </tr>
    <tr style="background:#f0f4ff;">
      <td style="padding:9px 14px;">Golden dataset — geração de perguntas</td>
      <td style="padding:9px 14px;text-align:center;">✅</td>
      <td style="padding:9px 14px;text-align:center;">—</td>
      <td style="padding:9px 14px;font-family:monospace;font-size:13px;">claude-sonnet-4-6</td>
    </tr>
    <tr>
      <td style="padding:9px 14px;">Métricas RAGAS — LLM avaliador</td>
      <td style="padding:9px 14px;text-align:center;">✅</td>
      <td style="padding:9px 14px;text-align:center;">—</td>
      <td style="padding:9px 14px;font-family:monospace;font-size:13px;">claude-sonnet-4-6</td>
    </tr>
    <tr style="background:#fff3cd;">
      <td style="padding:9px 14px;font-weight:600;">Métricas RAGAS — embeddings internos</td>
      <td style="padding:9px 14px;text-align:center;">—</td>
      <td style="padding:9px 14px;text-align:center;">⚠️ obrigatório</td>
      <td style="padding:9px 14px;font-family:monospace;font-size:13px;">text-embedding-ada-002</td>
    </tr>
  </tbody>
</table>

> **Custo real:** apenas embeddings de 10 perguntas e 10 respostas. O custo total de uma execução completa é inferior a **$0,01** (menos de 1 centavo de dólar).

---

## Análise da Configuração

O projeto foi estruturado com uma configuração centralizada usando `@dataclass`:

```python
@dataclass
class Config:
    # Pipeline
    chunk_size: int = 500
    chunk_overlap: int = 50
    top_k: int = 3

    # Modelos
    llm_model: str = "claude-haiku-4-5-20251001"
    critic_model: str = "claude-sonnet-4-6"
    embeddings_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    # Paths
    docs_dir: str = "data/sample_docs"
    vectorstore_dir: str = "data/vectorstore"
    outputs_dir: str = "outputs"

    # RAGAS
    test_size: int = 10
```

<table>
  <thead>
    <tr>
      <th style="background:#1F3864;color:#fff;padding:10px 14px;">Parâmetro</th>
      <th style="background:#1F3864;color:#fff;padding:10px 14px;">Mudança</th>
      <th style="background:#1F3864;color:#fff;padding:10px 14px;">Status</th>
      <th style="background:#1F3864;color:#fff;padding:10px 14px;">Motivo</th>
    </tr>
  </thead>
  <tbody>
    <tr style="background:#f0f4ff;">
      <td style="padding:9px 14px;font-family:monospace;font-weight:600;">vectorstore_dir</td>
      <td style="padding:9px 14px;font-family:monospace;font-size:13px;">data/vectorstore → data/chroma_db</td>
      <td style="padding:9px 14px;text-align:center;"><span style="background:#fef3c7;color:#92400e;padding:2px 8px;border-radius:12px;font-size:12px;">Trocado</span></td>
      <td style="padding:9px 14px;">O ChromaDB cria uma subpasta com seu próprio nome. Renomear evita confusão sobre o que está armazenado ali.</td>
    </tr>
    <tr>
      <td style="padding:9px 14px;font-family:monospace;font-weight:600;">llm_model</td>
      <td style="padding:9px 14px;font-family:monospace;font-size:13px;">claude-haiku-4-5-20251001</td>
      <td style="padding:9px 14px;text-align:center;"><span style="background:#dcfce7;color:#166534;padding:2px 8px;border-radius:12px;font-size:12px;">Mantido</span></td>
      <td style="padding:9px 14px;">Haiku é mais rápido e barato para geração de respostas em lote. Suficiente para o pipeline RAG.</td>
    </tr>
    <tr style="background:#f0f4ff;">
      <td style="padding:9px 14px;font-family:monospace;font-weight:600;">critic_model</td>
      <td style="padding:9px 14px;font-family:monospace;font-size:13px;">claude-sonnet-4-6</td>
      <td style="padding:9px 14px;text-align:center;"><span style="background:#dcfce7;color:#166534;padding:2px 8px;border-radius:12px;font-size:12px;">Mantido</span></td>
      <td style="padding:9px 14px;">Usado no golden dataset e no evaluate.py como avaliador. Modelo mais capaz para julgamentos de qualidade.</td>
    </tr>
    <tr>
      <td style="padding:9px 14px;font-family:monospace;font-weight:600;">embeddings_model</td>
      <td style="padding:9px 14px;font-family:monospace;font-size:13px;">all-MiniLM-L6-v2</td>
      <td style="padding:9px 14px;text-align:center;"><span style="background:#dcfce7;color:#166534;padding:2px 8px;border-radius:12px;font-size:12px;">Mantido</span></td>
      <td style="padding:9px 14px;">Leve, gratuito e suficientemente preciso. Roda 100% local sem nenhuma API externa.</td>
    </tr>
    <tr style="background:#f0f4ff;">
      <td style="padding:9px 14px;font-family:monospace;font-weight:600;">chunk_size / overlap</td>
      <td style="padding:9px 14px;font-family:monospace;font-size:13px;">500 / 50</td>
      <td style="padding:9px 14px;text-align:center;"><span style="background:#dcfce7;color:#166534;padding:2px 8px;border-radius:12px;font-size:12px;">Mantido</span></td>
      <td style="padding:9px 14px;">Valores conservadores e adequados para o documento de exemplo (~2.000 palavras).</td>
    </tr>
    <tr>
      <td style="padding:9px 14px;font-family:monospace;font-weight:600;">test_size</td>
      <td style="padding:9px 14px;font-family:monospace;font-size:13px;">10</td>
      <td style="padding:9px 14px;text-align:center;"><span style="background:#dcfce7;color:#166534;padding:2px 8px;border-radius:12px;font-size:12px;">Mantido</span></td>
      <td style="padding:9px 14px;">Suficiente para demonstrar todos os padrões diagnósticos sem custo excessivo de API.</td>
    </tr>
  </tbody>
</table>

---

## Resultados Obtidos

Execução bem-sucedida sobre **10 perguntas geradas automaticamente** a partir do documento de exemplo (história da Inteligência Artificial). Total de 50 avaliações calculadas em 3 minutos e 26 segundos.

<table>
  <thead>
    <tr>
      <th style="background:#1F3864;color:#fff;padding:10px 14px;">Métrica</th>
      <th style="background:#1F3864;color:#fff;padding:10px 14px;">Compara</th>
      <th style="background:#1F3864;color:#fff;padding:10px 14px;text-align:center;">Score Médio</th>
      <th style="background:#1F3864;color:#fff;padding:10px 14px;">Interpretação</th>
    </tr>
  </thead>
  <tbody>
    <tr style="background:#f0f4ff;">
      <td style="padding:9px 14px;font-weight:600;">Faithfulness</td>
      <td style="padding:9px 14px;font-family:monospace;font-size:13px;">Answer ↔ Context</td>
      <td style="padding:9px 14px;text-align:center;"><span style="background:#dcfce7;color:#166534;font-weight:700;padding:4px 12px;border-radius:8px;">0.794</span></td>
      <td style="padding:9px 14px;">O LLM usou o contexto recuperado em ~80% das respostas.</td>
    </tr>
    <tr>
      <td style="padding:9px 14px;font-weight:600;">Answer Correctness</td>
      <td style="padding:9px 14px;font-family:monospace;font-size:13px;">Answer ↔ Ground Truth</td>
      <td style="padding:9px 14px;text-align:center;"><span style="background:#dcfce7;color:#166534;font-weight:700;padding:4px 12px;border-radius:8px;">0.792</span></td>
      <td style="padding:9px 14px;">As respostas estão corretas em ~79% comparadas ao ground truth.</td>
    </tr>
    <tr style="background:#f0f4ff;">
      <td style="padding:9px 14px;font-weight:600;">Answer Relevancy</td>
      <td style="padding:9px 14px;font-family:monospace;font-size:13px;">Answer ↔ Question</td>
      <td style="padding:9px 14px;text-align:center;"><span style="background:#dcfce7;color:#166534;font-weight:700;padding:4px 12px;border-radius:8px;">0.862</span></td>
      <td style="padding:9px 14px;">As respostas são relevantes às perguntas em ~86% dos casos.</td>
    </tr>
    <tr>
      <td style="padding:9px 14px;font-weight:600;">Context Precision</td>
      <td style="padding:9px 14px;font-family:monospace;font-size:13px;">Context ↔ Q + GT</td>
      <td style="padding:9px 14px;text-align:center;"><span style="background:#fef3c7;color:#92400e;font-weight:700;padding:4px 12px;border-radius:8px;">0.733</span></td>
      <td style="padding:9px 14px;">Score mais baixo — o retrieval trouxe chunks com ruído em ~27% dos casos.</td>
    </tr>
    <tr style="background:#f0f4ff;">
      <td style="padding:9px 14px;font-weight:600;">Context Recall</td>
      <td style="padding:9px 14px;font-family:monospace;font-size:13px;">Context ↔ Ground Truth</td>
      <td style="padding:9px 14px;text-align:center;"><span style="background:#dcfce7;color:#166534;font-weight:700;padding:4px 12px;border-radius:8px;">0.867</span></td>
      <td style="padding:9px 14px;">O retrieval capturou ~87% das informações necessárias para responder.</td>
    </tr>
  </tbody>
</table>

### Diagnóstico observado

O chunk **"Brasil e IA"** apareceu como contexto recuperado em perguntas não relacionadas ao Brasil — por exemplo, perguntas sobre o GPT-3 ou o Teste de Turing. Isso é **ruído no retrieval**, e se reflete diretamente no **Context Precision de 0.733**, o score mais baixo entre todas as métricas.

Esse é exatamente o tipo de problema que o RAGAS foi projetado para detectar, invisível só olhando as respostas, mas **evidente quando os scores são analisados sistematicamente**.

---

*RAGAS-Project — Projeto de Estudo em Avaliação de Sistemas RAG*