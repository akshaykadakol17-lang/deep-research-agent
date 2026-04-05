# Evaluation: Architecture Trade-offs

## Why this memory architecture

The agent uses a hybrid of two memory types — an episodic buffer and a vector store.

The episodic buffer stores the most recent Q&A pairs (up to 5). This handles recency — the most recently discovered information is almost always useful for the next sub-question. It is fast, always available, and needs no retrieval step.

The vector store (Chroma) handles relevance — even older findings can be retrieved if they are semantically related to the current sub-question. Together they give the agent both short-term and longer-term memory without exceeding the token budget.

## Alternatives considered

| Approach | Why I didn't use it |
|---|---|
| Full conversation history | Would exceed 3,000 token limit after 2–3 sub-queries |
| Vector RAG only | No context on the first sub-question — cold start problem |
| Summarization cascade | Adds complexity and latency; details get lost in compression |
| Hybrid episodic + vector (chosen) | Best balance for this constraint profile |

## Why these constraint values

**3,000 tokens per sub-query** — at roughly 750 words of context, this gives the model enough background to reason well. Beyond this, the model started ignoring earlier parts of the context anyway, so the constraint matches real observed behaviour.

**$0.10 per session** — this maps to a realistic cost ceiling for a deployed research tool. It forces the agent to be efficient rather than making unlimited calls, which is a real concern in production.

**5 items in episodic buffer** — at roughly 200 tokens per Q&A pair, 5 items use about 1,000 tokens, leaving 2,000 for vector context and the actual prompt. Going beyond 5 would eat too much of the per-query budget.

## LLM choice

I used Llama 3.2 via Ollama because it runs locally with no quota limits, making the project fully reproducible. In a production deployment this would swap to a stronger model like Claude Haiku for better reasoning quality — the architecture doesn't change, just the API call.

## What I would improve with more time

- Add a summarization layer so older memory gets compressed instead of dropped when the buffer fills up
- Add a simple interface where users can type their own research queries instead of editing the script
- Add evaluation metrics to score each sub-answer for relevance and flag low-confidence results
- Persist the vector store across sessions so memory carries over between runs

## Business relevance

LLM-powered research tools often fail in production because they either exceed context limits on complex queries or make too many expensive API calls. The constraint enforcement in this agent makes it predictably deployable — a cost ceiling can be set and it will never be exceeded, while still delivering comprehensive multi-part research answers.