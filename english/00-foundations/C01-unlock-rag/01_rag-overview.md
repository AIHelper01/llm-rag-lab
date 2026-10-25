<!-- derived-from: ../../../00_%E5%A4%AF%E5%AE%9E%E5%9F%BA%E7%A1%80/C01_%E8%A7%A3%E9%94%81RAG/01_RAG%E7%AE%80%E4%BB%8B.md -->
> English mirror, derived from the Chinese master: [lesson 1 of C01](../../../00_%E5%A4%AF%E5%AE%9E%E5%9F%BA%E7%A1%80/C01_%E8%A7%A3%E9%94%81RAG/01_RAG%E7%AE%80%E4%BB%8B.md). The Chinese text is the source of truth; figures are shared with it.

# Lesson 1 - RAG Overview

## 1. What is RAG?

### 1.1 The core definition

At heart, RAG (Retrieval-Augmented Generation) is a technical paradigm built to fix a very specific weakness of large language models: they know *what* but not *why*. The idea is to combine the **parametric knowledge** a model has absorbed into its weights - a fuzzy, frozen "memory" - with **non-parametric knowledge** from an external knowledge base: precise data you can update at any time. Operationally, before the LLM generates anything, a retrieval step pulls the relevant material out of that external store and folds it into the generation process, which makes the answer both more accurate and more current [^1] [^2] [^3].

> 💡 **In one sentence**: RAG teaches the LLM to sit an open-book exam - it can still use what it learned, but it may also consult the references whenever it needs to.

### 1.2 How it works

So how does a RAG system actually combine parametric and non-parametric knowledge? As figure 1-1 shows, the architecture does it in two stages:

(1) **Retrieval stage: finding the non-parametric knowledge**
-   **Vectorising the knowledge**: the **embedding model** acts as the connector. It encodes the external knowledge base into a vector index and stores it in a **vector database**.
-   **Semantic recall**: when a user asks something, the retrieval module encodes the question with the *same* embedding model and uses **similarity search** to home in on the document chunks that best match it, out of everything stored.

(2) **Generation stage: merging the two kinds of knowledge**
-   **Context assembly**: the **generation module** receives the retrieved chunks together with the user's original question.
-   **Instruction-guided generation**: following a prepared **prompt**, it combines context and question, then steers the LLM (Qwen3, for instance) into controlled, evidence-backed generation.

<div align="center">
   <img src="../../../00_%E5%A4%AF%E5%AE%9E%E5%9F%BA%E7%A1%80/C01_%E8%A7%A3%E9%94%81RAG/images/1_1_1.svg" width="60%" alt="Two-stage RAG architecture" />
   <p>Figure 1-1 The two-stage RAG architecture</p>
</div>

### 1.3 How the architecture evolved

RAG architectures grew from simple to elaborate; as figure 1-2 suggests, they fall into three broad generations [^4].

<div align="center">
   <img src="../../../00_%E5%A4%AF%E5%AE%9E%E5%9F%BA%E7%A1%80/C01_%E8%A7%A3%E9%94%81RAG/images/1_1_2.png" width="80%" alt="Classification of RAG evolution" />
   <p>Figure 1-2 The three generations of RAG</p>
</div>

Table 1-1 compares those three stages in detail.

<div align="center">
<table border="1" style="margin: 0 auto;">
  <tr>
    <th style="text-align: center;"></th>
    <th style="text-align: center;">Naive RAG</th>
    <th style="text-align: center;">Advanced RAG</th>
    <th style="text-align: center;">Modular RAG</th>
  </tr>
  <tr>
    <td style="text-align: center;"><strong>Pipeline</strong></td>
    <td style="text-align: center;"><strong>Offline:</strong> <code>index</code><br><strong>Online:</strong> <code>retrieve &rarr; generate</code></td>
    <td style="text-align: center;"><strong>Offline:</strong> <code>index</code><br><strong>Online:</strong> <code>...&rarr; pre-retrieval &rarr; ... &rarr; post-retrieval &rarr; ...</code></td>
    <td style="text-align: center;">Building-block pipeline you orchestrate</td>
  </tr>
  <tr>
    <td style="text-align: center;"><strong>Traits</strong></td>
    <td style="text-align: center;">Basic linear flow</td>
    <td style="text-align: center;">Adds optimisation steps <strong>before and after retrieval</strong></td>
    <td style="text-align: center;">Modular, composable, dynamically adjustable</td>
  </tr>
  <tr>
    <td style="text-align: center;"><strong>Key techniques</strong></td>
    <td style="text-align: center;">Plain vector retrieval</td>
    <td style="text-align: center;"><strong>Query rewrite</strong><br><strong>Rerank</strong></td>
    <td style="text-align: center;"><strong>Routing</strong><br><strong>Query transformation</strong><br><strong>Multi-way fusion</strong></td>
  </tr>
  <tr>
    <td style="text-align: center;"><strong>Limits</strong></td>
    <td style="text-align: center;">Unstable quality, little to optimise</td>
    <td style="text-align: center;">Fixed flow, a limited set of tuning points</td>
    <td style="text-align: center;">High system complexity</td>
  </tr>
</table>
<p><em>Table 1-1 The three generations of RAG compared</em></p>
</div>

> "Offline" means the data preparation done in advance (index building, for example); "online" means what happens in real time once a user request arrives.

## 2. Why use RAG?

### 2.1 Choosing an approach: RAG vs. fine-tuning

When you pick a technical route, cost-effectiveness decides a lot. The rule of thumb is to change the model as little as possible for as little money as possible, so the usual order is **prompt engineering &rarr; retrieval-augmented generation &rarr; fine-tuning**.

Two axes make the difference clear. As figure 1-3 shows, the **horizontal axis is LLM optimisation** - how deeply you modify the model itself. Moving right, the surgery gets deeper: prompt engineering and RAG leave the weights untouched, while fine-tuning rewrites them. The **vertical axis is context optimisation** - how much you enrich what you feed the model. Moving up, the enrichment grows: prompt engineering only refines the question, while RAG pulls in an external knowledge base and massively expands the context.

<div align="center">
  <img src="../../../00_%E5%A4%AF%E5%AE%9E%E5%9F%BA%E7%A1%80/C01_%E8%A7%A3%E9%94%81RAG/images/1_1_3.svg" width="60%" alt="The technology selection path" />
  <p>Figure 1-3 The selection path</p>
</div>

With that, the route is obvious:
- **Try prompt engineering first**: carefully engineered prompts are enough when the task is simple and the model already knows the material.
- **Then reach for RAG**: when the model cannot answer because it lacks domain-specific or up-to-date knowledge, bolt on a knowledge base and hand it the context.
- **Consider fine-tuning last**: it is the right - and final - tool when you want to change *how* the model behaves (behaviour, style, format) rather than *what* it knows. Think enforcing a very particular output format, imitating a specific conversational voice, or distilling an extremely complex instruction set into the weights.

RAG closes the gap between general-purpose models and specialist domains, and it is especially effective against the limitations in table 1-2:

<div align="center">
<table border="1" style="margin: 0 auto;">
  <tr>
    <th style="text-align: center;">Limitation</th>
    <th style="text-align: center;">What RAG does about it</th>
  </tr>
  <tr>
    <td style="text-align: center;"><strong>Static knowledge</strong></td>
    <td style="text-align: center;">Retrieves from an external base in real time, so content can be updated continuously</td>
  </tr>
  <tr>
    <td style="text-align: center;"><strong>Hallucination</strong></td>
    <td style="text-align: center;">Generates from retrieved evidence, which lowers the error rate</td>
  </tr>
  <tr>
    <td style="text-align: center;"><strong>Weak domain expertise</strong></td>
    <td style="text-align: center;">Plugs in domain knowledge bases (medical, legal, and so on)</td>
  </tr>
  <tr>
    <td style="text-align: center;"><strong>Data privacy risk</strong></td>
    <td style="text-align: center;">Keeps the knowledge base deployed locally, so sensitive data stays in-house</td>
  </tr>
</table>
<p><em>Table 1-2 How RAG answers the limitations of LLMs</em></p>
</div>

### 2.2 The main advantages

(1) **Accuracy and trustworthiness improve together**

RAG's core value is that it escapes the ceiling of pre-training knowledge. It **fills professional blind spots** and, by supplying concrete source material, it strongly **suppresses confident nonsense**. The research also shows RAG output is markedly better on **specificity** and **diversity** than plain LLM output. Just as important, RAG is **traceable**: every answer can be traced back to the document it came from, and that "show me the source" property is what makes the technology usable in serious settings such as law and medicine.

(2) **Freshness guaranteed**

On the knowledge side, RAG cures the **knowledge lag** every LLM inherits (the model knows nothing after its cut-off date). The knowledge base updates **independently of the model**: a new policy or dataset is searchable the moment it lands. The literature calls this **index hot-swapping** - like swapping a memory card in a robot, you replace its world model instantly, with no retraining, so knowledge is always live.

(3) **Much better total cost**

Economically, RAG is the high-value option. It **avoids frequent fine-tuning** and its enormous compute bill; and because external knowledge does the heavy lifting, a **smaller base model** often reaches comparable quality on domain tasks, which cuts inference cost directly. It also removes the compute needed to force huge amounts of knowledge into model weights.

(4) **Modular, extensible architecture**

RAG is architecturally inclusive: it supports **multi-source ingestion**, so PDFs, Word documents, and web pages all end up in one knowledge base. Its **modular design** decouples retrieval from generation, which means the retrieval side can be optimised on its own (a better embedding model, say) without disturbing the stability of generation - a big deal for long-term iteration.

### 2.3 Risk tiers for adoption

Table 1-3 shows how well RAG fits scenarios at different risk levels.

<div align="center">
<table border="1" style="margin: 0 auto;">
  <tr>
    <th style="text-align: center;">Risk level</th>
    <th style="text-align: center;">Example</th>
    <th style="text-align: center;">RAG fit</th>
  </tr>
  <tr>
    <td style="text-align: center;"><strong>Low risk</strong></td>
    <td style="text-align: center;">Translation / grammar checking</td>
    <td style="text-align: center;">Highly reliable as-is</td>
  </tr>
  <tr>
    <td style="text-align: center;"><strong>Medium risk</strong></td>
    <td style="text-align: center;">Contract drafting / legal consultation</td>
    <td style="text-align: center;">Needs human review in the loop</td>
  </tr>
  <tr>
    <td style="text-align: center;"><strong>High risk</strong></td>
    <td style="text-align: center;">Evidence analysis / visa decisions</td>
    <td style="text-align: center;">Needs strict quality control</td>
  </tr>
</table>
<p><em>Table 1-3 RAG fit by risk tier</em></p>
</div>

## 3. How do you get started with RAG?

### 3.1 Picking the basic tool chain

Building a RAG system means choosing along several axes. For the **development model**, mature frameworks such as **LangChain** and **LlamaIndex** get you integrated quickly, and **framework-free native development** is a perfectly good alternative when you want fine-grained control over the flow (hardly a burden with AI pair programming). For the **memory substrate** (the vector database), **Milvus** and **Pinecone** suit large-scale data, while **FAISS** and **Chroma** are the lightweight or local options - decide by actual scale. Later, to measure quality, add an automated **evaluation tool** such as **RAGAS** or **TruLens**.

### 3.2 Four steps to a minimum viable system (MVP)

(1) **Data preparation and cleaning**: this is the foundation. Standardise heterogeneous sources - PDF, Word, and the rest - and choose a sensible **chunking strategy** (split on semantic paragraphs rather than a fixed character count) so information is not shredded at the seams.

(2) **Index building**: turn the chunks into vectors with an **embedding model** and store them. Attach **metadata** here (source, page number) - it pays off later when you need precise citations.

(3) **Retrieval strategy**: do not rely on vector search alone. **Hybrid retrieval** (vectors plus keywords) lifts recall, and a **reranker** curates the candidates a second time so the LLM only sees the good parts.

(4) **Generation and prompt engineering**: finally, design a clear **prompt template** that makes the LLM answer from the retrieved context, and state explicitly that it must say "I don't know" rather than invent an answer.

### 3.3 The friendly route for beginners

If you would rather validate an idea than live in the code, a visual knowledge-base platform such as **FastGPT** or **Dify** wraps the whole RAG pipeline: upload documents and ask questions. Developers can start from open-source templates such as **LangChain4j Easy RAG** or **TinyRAG** [^6] on GitHub, which are efficient starting points.

### 3.4 Going further: the challenges

Once a basic RAG system works, the next step is learning to measure it, diagnose it, and break through its limits.

(1) **What to measure, and what hurts**

You cannot judge a RAG system by feel. The industry quantifies it along a few dimensions: first **retrieval relevance** (does the retrieved material actually contain the answer), then **generation quality**, which splits into **semantic accuracy** (is the meaning right) and **lexical match** (are the technical terms used correctly).

Those same dimensions map onto the main challenges. There is the **retrieval dependency** problem - if retrieval hands back the wrong material, even a strong LLM will produce confident nonsense. And **multi-hop reasoning** questions, which need synthesis across several documents, routinely defeat common RAG architectures.

(2) **Where to optimise, and how architectures evolve**

The community has explored several routes. On the **performance** side: **index tiering** (cache the frequently hit data) and **multimodal extension** (retrieve images and tables) push both efficiency and capability boundaries. On the **architecture** side: simple linear flows are giving way to richer **design patterns** - a **branching pattern** runs several retrievals in parallel, a **looping pattern** lets the system correct itself. These flexible shapes are the road to smarter RAG.

## 4. Is RAG dead?

As context windows grew, voices appeared declaring RAG dead. Two arguments drive it: first, long contexts can brute-force digest huge amounts of text, so an elaborate retrieval system is unnecessary; second, the term RAG is itself too broad, blurring technical detail and getting in the way of understanding and optimisation.

Both arguments ignore a regularity in how technical concepts evolve. It would be easy to give a modern, complex RAG system a sharper - and more intimidating - name, such as a **Large Language Model Knowledge Management Expert System (LKE)**, because it long ago outgrew the simple "retrieve-augment-generate" original. But that renaming game is exactly what makes the "RAG is dead" claim superficial: it is pouring continuously ageing wine into a new bottle.

> The author is not trying to coin a term here - so why the name LKE? It encodes three core elements:
> -   **L (Large Language Model)**: the driving force of the system is an LLM.
> -   **K (Knowledge Management)**: the system behaves like a knowledge manager, precisely finding (**retrieving**) the knowledge you need so you can build higher-order applications on top of the model.
> -   **E (Expert)**: the system answers like an expert, working through routing, analysis, fusion, and correction before it produces the answer (**generation**) and solves the problem.

Consider **Transformer**. Today, whether it is a decoder-only model in the GPT lineage or an encoder-only model in the BERT lineage, we say "based on the Transformer architecture", even though both differ hugely from the complete original in the paper. That label captured one core leap in a paradigm and became the symbol of an era. The same holds here: **the core of RAG is "combining an LLM's internal parametric knowledge with external non-parametric knowledge"**. As long as that idea and its demand survive, however many modules you bolt on - query transformation, multi-way recall, self-correction - it is still evolution inside the same frame.

So "RAG is dead" is a pseudo-proposition. On the contrary, **RAG as a concept is thriving**: like Transformer, it has become a foundational architectural paradigm that keeps absorbing new techniques and keeps evolving. Its vitality lies precisely in being unrecognisable and all-embracing. **The goal of this course is to draw that clear map of the whole RAG territory, because once you can take every module apart and understand every possibility, whether you call it RAG or LKE stops mattering.** What matters is using RAG as the classic worked example through which we learn the whole family of problems: combining an LLM's internal parametric knowledge with external non-parametric knowledge.

> RAG is still moving fast - keep watching what academia and industry publish next.

## References

[^1]: [Genesis, J. (2025). *Retrieval-Augmented Text Generation: Methods, Challenges, and Applications*](https://www.researchgate.net/publication/391141346_Retrieval-Augmented_Generation_Methods_Applications_and_Challenges).

[^2]: [Gao et al. (2023). *Retrieval-Augmented Generation for Large Language Models: A Survey*](https://arxiv.org/abs/2312.10997).

[^3]: [Lewis et al. (2020). *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks*](https://arxiv.org/abs/2005.11401).

[^4]: [Gao et al. (2024). *Modular RAG: Transforming RAG Systems into LEGO-like Reconfigurable Frameworks*](https://arxiv.org/abs/2407.21059).

[^6]: [*TinyRAG: GitHub project*](https://github.com/KMnO4-zx/TinyRAG).
