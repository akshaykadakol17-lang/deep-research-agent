# Deep Research Agent with Memory Constraints

An AI agent that answers complex, multi-part research questions while operating under strict memory and cost constraints. Built for the Binox 2026 Graduate FDE Assessment (G3).

## Demo

**Query:** Compare AI regulations in the EU, United States, and China — what are the key differences in approach, enforcement, and impact on innovation?

**Result:** Agent decomposed into 5 sub-questions, researched each with growing memory context, and synthesized a comprehensive answer in 3 steps — using only $0.00085 of the $0.10 session budget.

## Architecture
```
User query
    ↓
Query Decomposer        → breaks into 3–5 focused sub-questions
    ↓
Token Budget Check      → enforces max 3,000 tokens of context per sub-query
    ↓
Memory Layer
  ├── Vector Store       → Chroma (semantic retrieval of past answers)
  ├── Episodic Buffer    → last 5 results kept in working memory
  └── Summary Cache      → compressed context for long sessions
    ↓
LLM (Llama 3.2 via Ollama)  → answers each sub-question with retrieved context
    ↓
Synthesizer             → combines all answers into final response
    ↓
Budget Report           → tokens used, cost, session limit status
```

## Constraints (Self-Defined)

| Constraint | Limit | Enforced in |
|---|---|---|
| Max context tokens per sub-query | 3,000 tokens | `budget.py` |
| Max cost per session | $0.10 | `budget.py` |
| Episodic buffer size | 5 items | `memory.py` |

If context exceeds 3,000 tokens, it is automatically trimmed to episodic-only before the LLM call. If session cost exceeds $0.10, remaining sub-queries are skipped with a logged warning.

## Memory Strategy

The agent uses a **three-layer hybrid memory architecture**:

1. **Episodic buffer** — a fixed-size deque (max 5 items) holding the most recent sub-question/answer pairs. Fast, always available, no retrieval needed.
2. **Vector store (Chroma)** — all answers are embedded and stored. Semantic similarity search retrieves the most relevant past findings for each new sub-question.
3. **Token budget gate** — before every LLM call, total context is counted. If it exceeds 3,000 tokens, only the episodic buffer is used (truncated to 1,500 chars). This ensures the constraint is never silently violated.

## Project Structure
```
deep-research-agent/
├── main.py           # entry point
├── decomposer.py     # query decomposition
├── memory.py         # episodic buffer + Chroma vector store
├── researcher.py     # per-sub-question LLM calls with memory
├── synthesizer.py    # final answer synthesis
├── budget.py         # token counting + cost tracking
├── requirements.txt
├── README.md
└── evaluation.md     # architecture trade-off analysis
```

## Setup

**Requirements:** Python 3.10+, [Ollama](https://ollama.com)
```bash
# 1. Install Ollama and pull the model
brew install ollama
ollama pull llama3.2
ollama serve   # run in a separate terminal tab

# 2. Clone and install dependencies
git clone https://github.com/YOUR_USERNAME/deep-research-agent
cd deep-research-agent
pip install -r requirements.txt

# 3. Run the agent
python main.py
```

No API keys required. Runs entirely locally.

## Example Output
```
[Step 1] Decomposing query into sub-questions...
[Decomposer] 5 sub-questions generated
  1. How do EU, US, and Chinese AI regulations differ in addressing job displacement?
  2. What is the role of government oversight in enforcing AI regulations?
  ...

[Step 2] Researching each sub-question...
[Budget] sub-question 1: 256 tokens | $0.00003 | Session total: $0.00003
[Budget] sub-question 2: 728 tokens | $0.00009 | Session total: $0.00012
  ...

[Step 3] Synthesizing final answer...

[Budget Report] Total tokens: 6767 | Total cost: $0.00085
Session budget OK (limit: $0.10)
```

## Self-Assessment

**What works well:**
- Memory context visibly grows between sub-queries (token counts increase each step), confirming RAG is active
- Budget enforcement is real — sub-queries are skipped if limit is hit, not just warned
- Fully local, zero API cost, reproducible on any Mac with Ollama

**What I would improve with more time:**
- Add a summarization cascade for very long sessions (currently just truncates)
- Expose a simple CLI interface for custom queries
- Add evaluation metrics (answer relevance scoring per sub-question)
- Persist vector store across sessions for cross-session memory

## Tech Stack

| Component | Tool | Why |
|---|---|---|
| LLM | Llama 3.2 via Ollama | Free, local, no quota limits |
| Vector store | Chroma | Lightweight, no server needed |
| Embeddings | all-MiniLM-L6-v2 | Fast, good semantic quality |
| Token counting | tiktoken | Accurate, same tokenizer as GPT-4 |
| Memory | Custom Python (deque) | Simple, inspectable, no overhead |