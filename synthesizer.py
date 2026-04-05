import os, requests
from dotenv import load_dotenv
from budget import BudgetTracker

load_dotenv()

def synthesize(original_query: str, sub_questions: list, answers: list, budget: BudgetTracker) -> str:
    qa_pairs = "\n\n".join([f"Q: {q}\nA: {a}" for q, a in zip(sub_questions, answers)])
    prompt = f"""You are a research synthesizer. Using the findings below, write a comprehensive answer to the original question.

Original question: {original_query}

Findings:
{qa_pairs}

Write a clear, structured answer in 300-400 words."""

    response = requests.post("http://localhost:11434/api/generate", json={
        "model": "llama3.2",
        "prompt": prompt,
        "stream": False
    })
    answer = response.json()["response"].strip()

    tokens = budget.count_tokens(prompt + answer)
    budget.log_usage(tokens, "synthesis")
    return answer