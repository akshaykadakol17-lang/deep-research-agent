import os, json, requests
from dotenv import load_dotenv

load_dotenv()

def decompose_query(query: str) -> list[str]:
    prompt = f"""Break the following research question into 3-5 focused sub-questions.
Return ONLY a JSON array of strings. No explanation, no markdown.

Question: {query}"""

    response = requests.post("http://localhost:11434/api/generate", json={
        "model": "llama3.2",
        "prompt": prompt,
        "stream": False
    })
    text = response.json()["response"].strip().strip("```json").strip("```").strip()
    try:
        sub_questions = json.loads(text)
        print(f"[Decomposer] {len(sub_questions)} sub-questions generated")
        return sub_questions
    except json.JSONDecodeError:
        lines = [l.strip("- ").strip() for l in text.split("\n") if l.strip()]
        return lines[:5]