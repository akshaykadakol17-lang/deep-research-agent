import os, requests
from dotenv import load_dotenv
from budget import BudgetTracker
from memory import MemoryManager

load_dotenv()

def research_subquery(sub_question: str, memory: MemoryManager, budget: BudgetTracker) -> str:
    if not budget.fits_session_budget():
        print(f"[Researcher] Session budget exceeded. Skipping: {sub_question}")
        return "Skipped due to budget constraint."

    vector_context = memory.retrieve(sub_question)
    episodic_context = memory.get_episodic_context()

    context_parts = []
    if vector_context:
        context_parts.append(f"[Relevant past research]\n{vector_context}")
    if episodic_context:
        context_parts.append(f"[Recent findings]\n{episodic_context}")

    context_block = "\n\n".join(context_parts)

    if context_block and not budget.fits_subquery_budget(context_block):
        print(f"[Researcher] Context too large, trimming to episodic only")
        context_block = episodic_context[:1500] if episodic_context else ""

    prompt = f"""{context_block + chr(10) + chr(10) if context_block else ""}Research question: {sub_question}

Provide a concise, factual answer in 150-200 words."""

    response = requests.post("http://localhost:11434/api/generate", json={
        "model": "llama3.2",
        "prompt": prompt,
        "stream": False
    })
    answer = response.json()["response"].strip()

    tokens_used = budget.count_tokens(prompt + answer)
    budget.log_usage(tokens_used, sub_question[:40])
    memory.store(sub_question, answer)

    return answer