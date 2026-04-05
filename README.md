# Deep Research Agent with Memory Constraints

A research agent that answers complex, multi-part questions while operating under strict memory and cost constraints. Built as part of the Binox 2026 Graduate FDE Assessment (G3).

## Why I built this

I chose G3 because it focuses more on system design and reasoning rather than building something like a voice agent or a social scraper. I liked that it allowed me to design the architecture myself, especially around how memory works and how to manage constraints like tokens and cost. It felt more aligned with the kind of engineering decisions you'd make in real-world AI systems.

## How it works

The agent takes a complex research question and breaks it into 3–5 focused sub-questions. Each sub-question is researched individually using context retrieved from memory, then all answers are synthesized into a final response.
```
User query
    ↓
Query Decomposer     → breaks into 3–5 sub-questions
    ↓
Token Budget Check   → max 3,000 tokens of context per sub-query
    ↓
Memory Layer
  ├── Episodic Buffer    → last 5 Q&A pairs (short-term memory)
  └── Vector Store       → Chroma semantic search (long-term memory)
    ↓
LLM (Llama 3.2 via Ollama)
    ↓
Synthesizer          → combines all answers into final response
    ↓
Budget Report        → tokens used, cost, session limit status
```

## Constraints

| Constraint | Limit | Where enforced |
|---|---|---|
| Max context tokens per sub-query | 3,000 tokens | `budget.py` |
| Max cost per session | $0.10 | `budget.py` |
| Episodic buffer size | 5 items | `memory.py` |

If context exceeds 3,000 tokens it is trimmed automatically before the LLM call. If session cost exceeds $0.10, remaining sub-queries are skipped with a logged warning.

## Memory design

The episodic buffer stores the most recent question and answer pairs so the agent remembers what it just discovered. When the next sub-question is processed, the system reuses those recent results as context instead of starting from scratch. It acts like short-term memory for the agent.

Alongside the episodic buffer, all answers are stored in a Chroma vector store. This allows the agent to retrieve semantically relevant past findings even if they weren't the most recent — acting as longer-term memory.

## Why Ollama

I used Ollama because it runs the model locally, which avoids API quota issues and keeps the project completely reproducible without needing external keys or credits. Since the goal of the task was to demonstrate the architecture and memory strategy, using a local model made development easier and ensures anyone reviewing the project can run it without setup friction.

## Project structure
```
deep-research-agent/
├── main.py           # entry point
├── decomposer.py     # breaks query into sub-questions
├── memory.py         # episodic buffer + Chroma vector store
├── researcher.py     # LLM calls with memory context per sub-question
├── synthesizer.py    # combines answers into final response
├── budget.py         # token counting + cost tracking
├── requirements.txt
├── README.md
└── evaluation.md
```

## Setup

Requirements: Python 3.10+, [Ollama](https://ollama.com)
```bash
# 1. Install Ollama and pull the model
brew install ollama
ollama pull llama3.2
ollama serve    # run in a separate terminal tab

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run
python main.py
```

No API keys needed. Runs entirely locally.

## Example output
```
[Step 1] Decomposing query into sub-questions...
[Decomposer] 5 sub-questions generated

[Step 2] Researching each sub-question...
[Budget] sub-question 1: 256 tokens | $0.00003 | Session total: $0.00003
[Budget] sub-question 2: 728 tokens | $0.00009 | Session total: $0.00012
[Budget] sub-question 3: 1181 tokens | $0.00015 | Session total: $0.00027

[Step 3] Synthesizing final answer...

[Budget Report] Total tokens: 6767 | Total cost: $0.00085
Session budget OK (limit: $0.10)
```

Notice how token counts grow with each sub-query — that's the memory working, pulling in more context as the session progresses.

## What I would improve

- Add a summarization layer so older memory gets compressed instead of dropped when the buffer fills up
- Add a simple interface where users can enter their own queries instead of it being hardcoded
- Add evaluation metrics to score each sub-answer for relevance and flag low-confidence results
- Persist the vector store across sessions so memory carries over between runs

## Tech stack

| Component | Tool | Reason |
|---|---|---|
| LLM | Llama 3.2 via Ollama | Local, free, no quota limits, fully reproducible |
| Vector store | Chroma | Lightweight, no server needed |
| Embeddings | all-MiniLM-L6-v2 | Fast, good semantic quality |
| Token counting | tiktoken | Accurate token counting |
| Memory | Custom Python deque | Simple, inspectable, no overhead |