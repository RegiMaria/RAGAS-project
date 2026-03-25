# RAGAS-Project
### Relatório de Interpretação dos Resultados

> **Para quem é este relatório?** Para quem está começando com avaliação de sistemas RAG e quer entender o que os números significam na prática, não só ver os scores, mas saber o que fazer com eles.

---

## Sumário

1. [Por que 50 avaliações se só tínhamos 10 perguntas?](#por-que-50-avaliações)
2. [Quantas perguntas são suficientes? A estatística por trás](#quantas-perguntas-são-suficientes)
3. [O que cada métrica mede — em linguagem simples](#o-que-cada-métrica-mede)
4. [Interpretando os scores médios](#interpretando-os-scores-médios)
5. [Análise pergunta por pergunta](#análise-pergunta-por-pergunta)
6. [Os padrões mais importantes para diagnosticar](#os-padrões-mais-importantes)
7. [O que fazer com esses resultados](#o-que-fazer-com-esses-resultados)

---

## Por que 50 avaliações?

Quando o terminal mostra `Evaluating: 100%|████| 50/50`, você pode ter estranhado, afinal, eram só 10 perguntas. Por que 50?

A resposta é simples: **cada pergunta é avaliada por 5 métricas diferentes**.

```
10 perguntas × 5 métricas = 50 avaliações individuais
```

Cada "avaliação" é uma chamada separada ao LLM (Claude Sonnet) para julgar um aspecto específico da resposta. Pense assim:

<table>
  <thead>
    <tr>
      <th style="background:#1F3864;color:#fff;padding:10px 14px;">#</th>
      <th style="background:#1F3864;color:#fff;padding:10px 14px;">Pergunta</th>
      <th style="background:#1F3864;color:#fff;padding:10px 14px;">Faithfulness</th>
      <th style="background:#1F3864;color:#fff;padding:10px 14px;">Correctness</th>
      <th style="background:#1F3864;color:#fff;padding:10px 14px;">Relevancy</th>
      <th style="background:#1F3864;color:#fff;padding:10px 14px;">Precision</th>
      <th style="background:#1F3864;color:#fff;padding:10px 14px;">Recall</th>
    </tr>
  </thead>
  <tbody>
    <tr style="background:#f0f4ff;">
      <td style="padding:8px 14px;">1</td>
      <td style="padding:8px 14px;">Quem cunhou o termo IA?</td>
      <td style="padding:8px 14px;text-align:center;">avaliação 1</td>
      <td style="padding:8px 14px;text-align:center;">avaliação 2</td>
      <td style="padding:8px 14px;text-align:center;">avaliação 3</td>
      <td style="padding:8px 14px;text-align:center;">avaliação 4</td>
      <td style="padding:8px 14px;text-align:center;">avaliação 5</td>
    </tr>
    <tr>
      <td style="padding:8px 14px;">2</td>
      <td style="padding:8px 14px;">O que foi o Teste de Turing?</td>
      <td style="padding:8px 14px;text-align:center;">avaliação 6</td>
      <td style="padding:8px 14px;text-align:center;">avaliação 7</td>
      <td style="padding:8px 14px;text-align:center;">avaliação 8</td>
      <td style="padding:8px 14px;text-align:center;">avaliação 9</td>
      <td style="padding:8px 14px;text-align:center;">avaliação 10</td>
    </tr>
    <tr style="background:#f0f4ff;">
      <td style="padding:8px 14px;">...</td>
      <td style="padding:8px 14px;">...</td>
      <td style="padding:8px 14px;text-align:center;">...</td>
      <td style="padding:8px 14px;text-align:center;">...</td>
      <td style="padding:8px 14px;text-align:center;">...</td>
      <td style="padding:8px 14px;text-align:center;">...</td>
      <td style="padding:8px 14px;text-align:center;">...</td>
    </tr>
    <tr>
      <td style="padding:8px 14px;">10</td>
      <td style="padding:8px 14px;">Aplicações atuais da IA?</td>
      <td style="padding:8px 14px;text-align:center;">avaliação 46</td>
      <td style="padding:8px 14px;text-align:center;">avaliação 47</td>
      <td style="padding:8px 14px;text-align:center;">avaliação 48</td>
      <td style="padding:8px 14px;text-align:center;">avaliação 49</td>
      <td style="padding:8px 14px;text-align:center;">avaliação 50</td>
    </tr>
  </tbody>
</table>

> **Resumindo:** 50 não é o número de perguntas. É o número de **julgamentos individuais** que o Claude fez para avaliar o sistema.

---

## Quantas perguntas são suficientes?

Esta é uma das perguntas mais importantes — e frequentemente ignoradas — em avaliação de sistemas RAG.

### O problema da confiança estatística

Quando você tem 10 perguntas e vê um score médio de 0.812 de faithfulness, você pode confiar nesse número? Ele realmente representa o comportamento do sistema?

A resposta vem da **estatística**: para estimar uma proporção com uma margem de erro de ±10% e 95% de confiança, você precisa de aproximadamente **100 amostras**. Para ±5%, são necessárias cerca de **400 amostras**.

<table>
  <thead>
    <tr>
      <th style="background:#1F3864;color:#fff;padding:10px 14px;">Tamanho do Dataset</th>
      <th style="background:#1F3864;color:#fff;padding:10px 14px;">Margem de Erro</th>
      <th style="background:#1F3864;color:#fff;padding:10px 14px;">Confiança</th>
      <th style="background:#1F3864;color:#fff;padding:10px 14px;">Uso recomendado</th>
    </tr>
  </thead>
  <tbody>
    <tr style="background:#fee2e2;">
      <td style="padding:9px 14px;font-weight:600;">10 perguntas</td>
      <td style="padding:9px 14px;">± 31%</td>
      <td style="padding:9px 14px;">95%</td>
      <td style="padding:9px 14px;">⚠️ Apenas para exploração e aprendizado</td>
    </tr>
    <tr style="background:#fef3c7;">
      <td style="padding:9px 14px;font-weight:600;">50 perguntas</td>
      <td style="padding:9px 14px;">± 14%</td>
      <td style="padding:9px 14px;">95%</td>
      <td style="padding:9px 14px;">⚠️ Prototipagem — tendências visíveis</td>
    </tr>
    <tr style="background:#fef3c7;">
      <td style="padding:9px 14px;font-weight:600;">100 perguntas</td>
      <td style="padding:9px 14px;">± 10%</td>
      <td style="padding:9px 14px;">95%</td>
      <td style="padding:9px 14px;">✅ Mínimo para decisões de produto</td>
    </tr>
    <tr style="background:#dcfce7;">
      <td style="padding:9px 14px;font-weight:600;">400 perguntas</td>
      <td style="padding:9px 14px;">± 5%</td>
      <td style="padding:9px 14px;">95%</td>
      <td style="padding:9px 14px;">✅ Recomendado para sistemas em produção</td>
    </tr>
    <tr style="background:#dcfce7;">
      <td style="padding:9px 14px;font-weight:600;">1.000+ perguntas</td>
      <td style="padding:9px 14px;">± 3%</td>
      <td style="padding:9px 14px;">95%</td>
      <td style="padding:9px 14px;">✅ Alta confiança — sistemas críticos</td>
    </tr>
  </tbody>
</table>

### O que isso significa para este projeto

Nosso dataset tem **10 perguntas**, com margem de erro de ±31%. Isso quer dizer que quando vemos faithfulness = 0.812, o valor real do sistema pode estar entre **0.50 e 1.0**.

Isso não significa que o exercício foi inútil — pelo contrário. Com 10 perguntas conseguimos:
- Entender como o pipeline funciona
- Identificar padrões de problemas
- Aprender a interpretar as métricas

Mas para tomar decisões sobre um sistema em produção — "esse RAG está pronto?" — você precisaria de pelo menos 100 perguntas.

> **Regra prática da literatura:** para sistemas RAG em produção, o golden dataset
> mínimo recomendado é de **100 a 200 perguntas**, cobrindo diferentes tipos
> (simples, raciocínio, multi-contexto) e diferentes partes do domínio.

---

### 📖 Chip Huyen — *AI Engineering* (O'Reilly, 2024), Capítulos 4 e 6

O livro usa o termo **evaluation set** e define que cada entrada precisa
obrigatoriamente de **três elementos**:

1. A **pergunta** de teste
2. Os **chunks anotados** como relevantes para aquela pergunta
3. A **resposta esperada** (ground truth)

> Sem os três, métricas como **Context Recall** são incalculáveis.

⚠️ **Para o iniciante:** cada "entrada" do evaluation set é exatamente isso:
```
1 entrada = 1 pergunta + 1 resposta esperada + 1 chunk de origem
```

Não é só uma lista de perguntas. Cada pergunta precisa ter a resposta correta
anotada **e** o trecho do documento de onde essa resposta vem. Sem isso, o
RAGAS não consegue julgar se o sistema recuperou o contexto certo.

#### Volume recomendado — tabela da OpenAI citada no livro
```
| Diferença que você quer detectar | Entradas necessárias |
|---|---|
| 30% de diferença entre sistemas | ~10 entradas |
| 10% de diferença | ~100 entradas |
| 3% de diferença | ~1.000 entradas |
| 1% de diferença | ~10.000 entradas |
```

**Números concretos do livro:**

- **Mínimo absoluto: 300 entradas** — abaixo disso o resultado não é
  estatisticamente confiável. Os scores que você vê podem ser ruído.
- **Preferível: 1.000 entradas** — a partir daí você tem confiança razoável
  para comparar versões do sistema e tomar decisões.
- **Por slice** (ex: tipo de pergunta × domínio): mínimo **30–50 entradas**
  para que o score do slice seja confiável

> *"Manual inspection of data is especially important. Staring at data for
> just 15 minutes usually gives some insight that could save hours of
> headaches."*
>
> — Chip Huyen, AI Engineering, Cap. 4

Traduzindo: antes de anotar centenas de entradas, valide o formato com 20,
rode o pipeline completo e ajuste.
---

## O que cada métrica mede

Antes de interpretar os números, é essencial entender o que cada métrica pergunta ao sistema.

<table>
  <thead>
    <tr>
      <th style="background:#1F3864;color:#fff;padding:10px 14px;">Métrica</th>
      <th style="background:#1F3864;color:#fff;padding:10px 14px;">Pergunta que ela responde</th>
      <th style="background:#1F3864;color:#fff;padding:10px 14px;">Compara</th>
      <th style="background:#1F3864;color:#fff;padding:10px 14px;">Quem avalia</th>
    </tr>
  </thead>
  <tbody>
    <tr style="background:#f0f4ff;">
      <td style="padding:9px 14px;font-weight:600;color:#1F3864;">Faithfulness</td>
      <td style="padding:9px 14px;">"O LLM usou o contexto ou inventou?"</td>
      <td style="padding:9px 14px;font-family:monospace;font-size:13px;">Answer ↔ Context</td>
      <td style="padding:9px 14px;">LLM (Claude)</td>
    </tr>
    <tr>
      <td style="padding:9px 14px;font-weight:600;color:#1F3864;">Answer Correctness</td>
      <td style="padding:9px 14px;">"A resposta está certa?"</td>
      <td style="padding:9px 14px;font-family:monospace;font-size:13px;">Answer ↔ Ground Truth</td>
      <td style="padding:9px 14px;">LLM (Claude)</td>
    </tr>
    <tr style="background:#f0f4ff;">
      <td style="padding:9px 14px;font-weight:600;color:#1F3864;">Answer Relevancy</td>
      <td style="padding:9px 14px;">"A resposta responde o que foi perguntado?"</td>
      <td style="padding:9px 14px;font-family:monospace;font-size:13px;">Answer ↔ Question</td>
      <td style="padding:9px 14px;">Embeddings (OpenAI)</td>
    </tr>
    <tr>
      <td style="padding:9px 14px;font-weight:600;color:#1F3864;">Context Precision</td>
      <td style="padding:9px 14px;">"O retrieval trouxe só o que era necessário?"</td>
      <td style="padding:9px 14px;font-family:monospace;font-size:13px;">Context ↔ Q + GT</td>
      <td style="padding:9px 14px;">LLM (Claude)</td>
    </tr>
    <tr style="background:#f0f4ff;">
      <td style="padding:9px 14px;font-weight:600;color:#1F3864;">Context Recall</td>
      <td style="padding:9px 14px;">"O retrieval encontrou tudo que era necessário?"</td>
      <td style="padding:9px 14px;font-family:monospace;font-size:13px;">Context ↔ Ground Truth</td>
      <td style="padding:9px 14px;">LLM (Claude)</td>
    </tr>
  </tbody>
</table>

Uma analogia para fixar: imagine que você pediu para um funcionário responder um e-mail usando um manual de instruções.

- **Faithfulness** → ele usou o manual ou respondeu do próprio conhecimento?
- **Correctness** → a resposta dele está certa de acordo com o gabarito?
- **Relevancy** → ele respondeu o que foi perguntado ou fugiu do assunto?
- **Context Precision** → ele buscou só as páginas certas do manual, ou trouxe páginas irrelevantes também?
- **Context Recall** → ele encontrou todas as páginas necessárias para responder?

---

## Interpretando os scores médios

```
faithfulness        0.812  ████████████████
answer_correctness  0.797  ███████████████
answer_relevancy    0.857  █████████████████
context_precision   0.733  ██████████████   ← ponto de atenção
context_recall      0.867  █████████████████
```

<table>
  <thead>
    <tr>
      <th style="background:#1F3864;color:#fff;padding:10px 14px;">Métrica</th>
      <th style="background:#1F3864;color:#fff;padding:10px 14px;text-align:center;">Score</th>
      <th style="background:#1F3864;color:#fff;padding:10px 14px;">Nível</th>
      <th style="background:#1F3864;color:#fff;padding:10px 14px;">O que significa</th>
    </tr>
  </thead>
  <tbody>
    <tr style="background:#f0f4ff;">
      <td style="padding:9px 14px;font-weight:600;">Faithfulness</td>
      <td style="padding:9px 14px;text-align:center;"><span style="background:#dcfce7;color:#166534;font-weight:700;padding:3px 10px;border-radius:8px;">0.812</span></td>
      <td style="padding:9px 14px;"><span style="background:#dcfce7;color:#166534;padding:2px 8px;border-radius:12px;font-size:12px;">✅ Bom</span></td>
      <td style="padding:9px 14px;">Em 8 de cada 10 respostas, o LLM baseou-se no contexto recuperado. Nas outras 2, foi além do contexto.</td>
    </tr>
    <tr>
      <td style="padding:9px 14px;font-weight:600;">Answer Correctness</td>
      <td style="padding:9px 14px;text-align:center;"><span style="background:#dcfce7;color:#166534;font-weight:700;padding:3px 10px;border-radius:8px;">0.797</span></td>
      <td style="padding:9px 14px;"><span style="background:#dcfce7;color:#166534;padding:2px 8px;border-radius:12px;font-size:12px;">✅ Bom</span></td>
      <td style="padding:9px 14px;">As respostas estão corretas em ~80%. Puxado para baixo pela pergunta 10, que falhou completamente.</td>
    </tr>
    <tr style="background:#f0f4ff;">
      <td style="padding:9px 14px;font-weight:600;">Answer Relevancy</td>
      <td style="padding:9px 14px;text-align:center;"><span style="background:#dcfce7;color:#166534;font-weight:700;padding:3px 10px;border-radius:8px;">0.857</span></td>
      <td style="padding:9px 14px;"><span style="background:#dcfce7;color:#166534;padding:2px 8px;border-radius:12px;font-size:12px;">✅ Bom</span></td>
      <td style="padding:9px 14px;">Quando o sistema responde, responde ao ponto. Também afetado pela pergunta 10 (score 0.000).</td>
    </tr>
    <tr>
      <td style="padding:9px 14px;font-weight:600;">Context Precision</td>
      <td style="padding:9px 14px;text-align:center;"><span style="background:#fef3c7;color:#92400e;font-weight:700;padding:3px 10px;border-radius:8px;">0.733</span></td>
      <td style="padding:9px 14px;"><span style="background:#fef3c7;color:#92400e;padding:2px 8px;border-radius:12px;font-size:12px;">⚠️ Atenção</span></td>
      <td style="padding:9px 14px;">O retrieval traz chunks desnecessários junto com os relevantes. O sistema "busca demais".</td>
    </tr>
    <tr style="background:#f0f4ff;">
      <td style="padding:9px 14px;font-weight:600;">Context Recall</td>
      <td style="padding:9px 14px;text-align:center;"><span style="background:#dcfce7;color:#166534;font-weight:700;padding:3px 10px;border-radius:8px;">0.867</span></td>
      <td style="padding:9px 14px;"><span style="background:#dcfce7;color:#166534;padding:2px 8px;border-radius:12px;font-size:12px;">✅ Bom</span></td>
      <td style="padding:9px 14px;">O retrieval encontra a maioria do que é necessário. Raro deixar informação importante de fora.</td>
    </tr>
  </tbody>
</table>

**Diagnóstico geral:** o sistema está funcionando bem, com um ponto de atenção claro no retrieval — ele encontra o que precisa (recall alto), mas traz bagagem desnecessária junto (precision mais baixa).

---

## Análise pergunta por pergunta

<table>
  <thead>
    <tr>
      <th style="background:#1F3864;color:#fff;padding:10px 14px;">#</th>
      <th style="background:#1F3864;color:#fff;padding:10px 14px;">Pergunta (resumida)</th>
      <th style="background:#1F3864;color:#fff;padding:10px 14px;text-align:center;">Faith</th>
      <th style="background:#1F3864;color:#fff;padding:10px 14px;text-align:center;">Correct</th>
      <th style="background:#1F3864;color:#fff;padding:10px 14px;text-align:center;">Relev</th>
      <th style="background:#1F3864;color:#fff;padding:10px 14px;text-align:center;">Prec</th>
      <th style="background:#1F3864;color:#fff;padding:10px 14px;text-align:center;">Recall</th>
      <th style="background:#1F3864;color:#fff;padding:10px 14px;">Diagnóstico</th>
    </tr>
  </thead>
  <tbody>
    <tr style="background:#f0f4ff;">
      <td style="padding:8px 10px;font-weight:600;">1</td>
      <td style="padding:8px 10px;">Quem cunhou o termo IA?</td>
      <td style="padding:8px 10px;text-align:center;color:#166534;font-weight:700;">1.00</td>
      <td style="padding:8px 10px;text-align:center;color:#166534;font-weight:700;">0.886</td>
      <td style="padding:8px 10px;text-align:center;color:#166534;font-weight:700;">0.981</td>
      <td style="padding:8px 10px;text-align:center;color:#dc2626;font-weight:700;">0.333</td>
      <td style="padding:8px 10px;text-align:center;color:#166534;font-weight:700;">1.000</td>
      <td style="padding:8px 10px;font-size:13px;">Retrieval trouxe 2 chunks irrelevantes junto com o certo.</td>
    </tr>
    <tr>
      <td style="padding:8px 10px;font-weight:600;">2</td>
      <td style="padding:8px 10px;">O que foi o Teste de Turing?</td>
      <td style="padding:8px 10px;text-align:center;color:#166534;font-weight:700;">0.750</td>
      <td style="padding:8px 10px;text-align:center;color:#166534;font-weight:700;">0.992</td>
      <td style="padding:8px 10px;text-align:center;color:#166534;font-weight:700;">0.948</td>
      <td style="padding:8px 10px;text-align:center;color:#166534;font-weight:700;">1.000</td>
      <td style="padding:8px 10px;text-align:center;color:#166534;font-weight:700;">1.000</td>
      <td style="padding:8px 10px;font-size:13px;">✅ Excelente. Retrieval perfeito. LLM foi além do contexto em 25% da resposta.</td>
    </tr>
    <tr style="background:#f0f4ff;">
      <td style="padding:8px 10px;font-weight:600;">3</td>
      <td style="padding:8px 10px;">Os Invernos da IA</td>
      <td style="padding:8px 10px;text-align:center;color:#166534;font-weight:700;">1.000</td>
      <td style="padding:8px 10px;text-align:center;color:#166534;font-weight:700;">0.988</td>
      <td style="padding:8px 10px;text-align:center;color:#166534;font-weight:700;">0.974</td>
      <td style="padding:8px 10px;text-align:center;color:#166534;font-weight:700;">1.000</td>
      <td style="padding:8px 10px;text-align:center;color:#166534;font-weight:700;">1.000</td>
      <td style="padding:8px 10px;font-size:13px;">🏆 Perfeita. O melhor resultado do dataset. Tudo funcionou.</td>
    </tr>
    <tr>
      <td style="padding:8px 10px;font-weight:600;">4</td>
      <td style="padding:8px 10px;">A importância da AlexNet</td>
      <td style="padding:8px 10px;text-align:center;color:#d97706;font-weight:700;">0.545</td>
      <td style="padding:8px 10px;text-align:center;color:#d97706;font-weight:700;">0.556</td>
      <td style="padding:8px 10px;text-align:center;color:#166534;font-weight:700;">1.000</td>
      <td style="padding:8px 10px;text-align:center;color:#d97706;font-weight:700;">0.500</td>
      <td style="padding:8px 10px;text-align:center;color:#166534;font-weight:700;">1.000</td>
      <td style="padding:8px 10px;font-size:13px;">⚠️ O documento tem pouco sobre AlexNet. Resposta parcial e incompleta.</td>
    </tr>
    <tr style="background:#f0f4ff;">
      <td style="padding:8px 10px;font-weight:600;">5</td>
      <td style="padding:8px 10px;">Parâmetros do GPT-3</td>
      <td style="padding:8px 10px;text-align:center;color:#166534;font-weight:700;">1.000</td>
      <td style="padding:8px 10px;text-align:center;color:#166534;font-weight:700;">0.840</td>
      <td style="padding:8px 10px;text-align:center;color:#166534;font-weight:700;">0.959</td>
      <td style="padding:8px 10px;text-align:center;color:#166534;font-weight:700;">1.000</td>
      <td style="padding:8px 10px;text-align:center;color:#166534;font-weight:700;">1.000</td>
      <td style="padding:8px 10px;font-size:13px;">✅ Ótimo. Retrieval perfeito, resposta correta e fiel ao contexto.</td>
    </tr>
    <tr>
      <td style="padding:8px 10px;font-weight:600;">6</td>
      <td style="padding:8px 10px;">ChatGPT — crescimento mais rápido</td>
      <td style="padding:8px 10px;text-align:center;color:#d97706;font-weight:700;">0.600</td>
      <td style="padding:8px 10px;text-align:center;color:#166534;font-weight:700;">0.908</td>
      <td style="padding:8px 10px;text-align:center;color:#166534;font-weight:700;">1.000</td>
      <td style="padding:8px 10px;text-align:center;color:#166534;font-weight:700;">1.000</td>
      <td style="padding:8px 10px;text-align:center;color:#166534;font-weight:700;">1.000</td>
      <td style="padding:8px 10px;font-size:13px;">⚠️ LLM completou com conhecimento próprio sobre o ChatGPT além do contexto.</td>
    </tr>
    <tr style="background:#f0f4ff;">
      <td style="padding:8px 10px;font-weight:600;">7</td>
      <td style="padding:8px 10px;">Linha do tempo — quanto tempo?</td>
      <td style="padding:8px 10px;text-align:center;color:#166534;font-weight:700;">0.833</td>
      <td style="padding:8px 10px;text-align:center;color:#166534;font-weight:700;">0.739</td>
      <td style="padding:8px 10px;text-align:center;color:#166534;font-weight:700;">0.773</td>
      <td style="padding:8px 10px;text-align:center;color:#166534;font-weight:700;">1.000</td>
      <td style="padding:8px 10px;text-align:center;color:#d97706;font-weight:700;">0.667</td>
      <td style="padding:8px 10px;font-size:13px;">⚠️ Pergunta de raciocínio. O retrieval não encontrou todos os fatos necessários para calcular.</td>
    </tr>
    <tr>
      <td style="padding:8px 10px;font-weight:600;">8</td>
      <td style="padding:8px 10px;">Desafios éticos da IA</td>
      <td style="padding:8px 10px;text-align:center;color:#166534;font-weight:700;">1.000</td>
      <td style="padding:8px 10px;text-align:center;color:#166534;font-weight:700;">0.992</td>
      <td style="padding:8px 10px;text-align:center;color:#166534;font-weight:700;">0.947</td>
      <td style="padding:8px 10px;text-align:center;color:#d97706;font-weight:700;">0.500</td>
      <td style="padding:8px 10px;text-align:center;color:#166534;font-weight:700;">1.000</td>
      <td style="padding:8px 10px;font-size:13px;">✅ Resposta excelente. Precisão baixa indica retrieval com ruído, mas o LLM ignorou bem.</td>
    </tr>
    <tr style="background:#f0f4ff;">
      <td style="padding:8px 10px;font-weight:600;">9</td>
      <td style="padding:8px 10px;">Brasil e regulamentação de IA</td>
      <td style="padding:8px 10px;text-align:center;color:#d97706;font-weight:700;">0.556</td>
      <td style="padding:8px 10px;text-align:center;color:#166534;font-weight:700;">0.842</td>
      <td style="padding:8px 10px;text-align:center;color:#166534;font-weight:700;">0.989</td>
      <td style="padding:8px 10px;text-align:center;color:#166534;font-weight:700;">1.000</td>
      <td style="padding:8px 10px;text-align:center;color:#166534;font-weight:700;">1.000</td>
      <td style="padding:8px 10px;font-size:13px;">⚠️ O LLM complementou com conhecimento sobre regulação no Brasil além do documento.</td>
    </tr>
    <tr style="background:#fee2e2;">
      <td style="padding:8px 10px;font-weight:600;">10</td>
      <td style="padding:8px 10px;">Aplicações atuais da IA</td>
      <td style="padding:8px 10px;text-align:center;color:#166534;font-weight:700;">0.833</td>
      <td style="padding:8px 10px;text-align:center;color:#dc2626;font-weight:700;">0.222</td>
      <td style="padding:8px 10px;text-align:center;color:#dc2626;font-weight:700;">0.000</td>
      <td style="padding:8px 10px;text-align:center;color:#dc2626;font-weight:700;">0.000</td>
      <td style="padding:8px 10px;text-align:center;color:#dc2626;font-weight:700;">0.000</td>
      <td style="padding:8px 10px;font-size:13px;">❌ Falha total de retrieval. O sistema não encontrou os chunks certos.</td>
    </tr>
  </tbody>
</table>

---

## Os padrões mais importantes para diagnosticar

### Padrão 1 — Retrieval com ruído (Pergunta 1, 4, 8)

**O que acontece:** Context Recall alto (encontrou tudo), mas Context Precision baixo (trouxe coisas a mais).

**Por que isso importa:** o LLM recebe contexto irrelevante junto com o relevante. Isso aumenta custo de tokens e pode confundir o modelo em casos mais complexos.

**Causa provável:** o `chunk_size` está pequeno demais ou o documento tem seções semanticamente próximas (como "Brasil e IA" aparecendo junto com qualquer outro tema).

---

### Padrão 2 — LLM usando conhecimento próprio (Perguntas 6 e 9)

**O que acontece:** Faithfulness baixa (~0.55–0.60) mas Answer Correctness alta (>0.85).

```
Pergunta 6:  faithfulness=0.600  correctness=0.908  ← LLM acertou sem usar o contexto
Pergunta 9:  faithfulness=0.556  correctness=0.842  ← mesmo padrão
```

**Por que isso importa:** o LLM respondeu certo, mas não usou os documentos para isso. Em sistemas corporativos ou médicos, isso é crítico — você não consegue rastrear de onde veio a informação. Se o documento mudar, a resposta não muda.

**Causa provável:** o Claude tem conhecimento sobre ChatGPT e regulação brasileira de IA no seu treinamento. Quando o contexto recuperado é incompleto, ele "completa" com o que sabe.

---

### Padrão 3 — Falha total de retrieval (Pergunta 10)

**O que acontece:** todas as métricas de contexto zeradas, resposta incorreta e irrelevante.

```
Pergunta 10: context_precision=0.000  context_recall=0.000  answer_relevancy=0.000
```

**Por que isso importa:** o retrieval falhou completamente — os chunks recuperados não tinham nenhuma relação com a pergunta. O LLM não tinha base para responder.

**Causa provável:** "Aplicações atuais da IA" é uma pergunta que exige múltiplos exemplos espalhados pelo documento. Com `top_k=3`, o sistema pode ter recuperado os 3 chunks mais próximos semanticamente mas nenhum contendo a lista completa.

---

### Padrão 4 — Pergunta boa demais para o documento (Pergunta 4)

**O que acontece:** faithfulness e correctness medianos, mas o LLM claramente fez o que pôde.

```
Pergunta 4: faithfulness=0.545  correctness=0.556
```

**Por que isso importa:** o documento de exemplo menciona AlexNet em apenas uma frase. A pergunta exigia mais do que o documento continha. Isso é um problema do **golden dataset**, não do RAG — a pergunta foi gerada automaticamente sem verificar se o documento tinha conteúdo suficiente para respondê-la.

**Lição:** ao gerar golden datasets automaticamente, sempre revisar manualmente se as perguntas são respondíveis com o conteúdo disponível.

---

## O que fazer com esses resultados

Com base na análise, as melhorias prioritárias são:

<table>
  <thead>
    <tr>
      <th style="background:#1F3864;color:#fff;padding:10px 14px;">Prioridade</th>
      <th style="background:#1F3864;color:#fff;padding:10px 14px;">Problema identificado</th>
      <th style="background:#1F3864;color:#fff;padding:10px 14px;">Ação recomendada</th>
      <th style="background:#1F3864;color:#fff;padding:10px 14px;">Métrica que melhora</th>
    </tr>
  </thead>
  <tbody>
    <tr style="background:#fee2e2;">
      <td style="padding:9px 14px;font-weight:600;color:#dc2626;">🔴 Alta</td>
      <td style="padding:9px 14px;">Falha total na pergunta 10</td>
      <td style="padding:9px 14px;">Aumentar <code>top_k</code> de 3 para 5 ou 6 para perguntas que exigem múltiplos fatos</td>
      <td style="padding:9px 14px;">Context Recall, Correctness</td>
    </tr>
    <tr style="background:#fef3c7;">
      <td style="padding:9px 14px;font-weight:600;color:#92400e;">🟡 Média</td>
      <td style="padding:9px 14px;">Retrieval com ruído (chunks irrelevantes)</td>
      <td style="padding:9px 14px;">Aumentar <code>chunk_size</code> para reduzir fragmentação e testar re-ranking dos resultados</td>
      <td style="padding:9px 14px;">Context Precision</td>
    </tr>
    <tr style="background:#fef3c7;">
      <td style="padding:9px 14px;font-weight:600;color:#92400e;">🟡 Média</td>
      <td style="padding:9px 14px;">LLM usando conhecimento próprio</td>
      <td style="padding:9px 14px;">Adicionar instrução explícita no prompt: "responda APENAS com base no contexto fornecido"</td>
      <td style="padding:9px 14px;">Faithfulness</td>
    </tr>
    <tr style="background:#dcfce7;">
      <td style="padding:9px 14px;font-weight:600;color:#166534;">🟢 Baixa</td>
      <td style="padding:9px 14px;">Golden dataset com perguntas sem resposta</td>
      <td style="padding:9px 14px;">Revisar manualmente as perguntas geradas e remover as que o documento não suporta</td>
      <td style="padding:9px 14px;">Correctness geral</td>
    </tr>
    <tr style="background:#dcfce7;">
      <td style="padding:9px 14px;font-weight:600;color:#166534;">🟢 Baixa</td>
      <td style="padding:9px 14px;">Dataset pequeno (10 perguntas)</td>
      <td style="padding:9px 14px;">Expandir para 100+ perguntas para ter confiança estatística nas decisões</td>
      <td style="padding:9px 14px;">Confiança em todos os scores</td>
    </tr>
  </tbody>
</table>

---

> **Conclusão:** os scores médios são enganosamente bons porque uma única pergunta com falha total (pergunta 10) revela um problema real de retrieval que os scores gerais não mostram com clareza. Isso reforça a importância de **sempre analisar pergunta por pergunta**, não só as médias.

---

*RAGAS-Project — Relatório de Interpretação dos Resultados*