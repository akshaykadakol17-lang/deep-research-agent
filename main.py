from decomposer import decompose_query
from researcher import research_subquery
from synthesizer import synthesize
from memory import MemoryManager
from budget import BudgetTracker

def run_agent(query: str):
    print(f"\n{'='*60}")
    print(f"Research Query: {query}")
    print(f"{'='*60}\n")

    memory = MemoryManager()
    budget = BudgetTracker()

    print("[Step 1] Decomposing query into sub-questions...")
    sub_questions = decompose_query(query)
    for i, q in enumerate(sub_questions, 1):
        print(f"  {i}. {q}")

    print("\n[Step 2] Researching each sub-question...")
    answers = []
    for q in sub_questions:
        print(f"\n  Researching: {q}")
        answer = research_subquery(q, memory, budget)
        answers.append(answer)
        print(f"  Answer preview: {answer[:100]}...")

    print("\n[Step 3] Synthesizing final answer...")
    final_answer = synthesize(query, sub_questions, answers, budget)

    print(f"\n{'='*60}")
    print("FINAL ANSWER")
    print(f"{'='*60}")
    print(final_answer)

    budget.report()
    return final_answer

if __name__ == "__main__":
    query = "Compare AI regulations in the EU, United States, and China — what are the key differences in approach, enforcement, and impact on innovation?"
    run_agent(query)