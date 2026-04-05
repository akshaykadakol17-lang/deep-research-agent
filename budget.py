import tiktoken

MAX_TOKENS_PER_SUBQUERY = 3000
MAX_COST_PER_SESSION = 0.10
COST_PER_1K_TOKENS = 0.000125  # Gemini 1.5 Flash pricing

class BudgetTracker:
    def __init__(self):
        self.total_tokens_used = 0
        self.total_cost = 0.0
        self.session_log = []

    def count_tokens(self, text: str) -> int:
        enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text))

    def fits_subquery_budget(self, context: str) -> bool:
        return self.count_tokens(context) <= MAX_TOKENS_PER_SUBQUERY

    def fits_session_budget(self) -> bool:
        return self.total_cost < MAX_COST_PER_SESSION

    def log_usage(self, tokens: int, label: str):
        cost = (tokens / 1000) * COST_PER_1K_TOKENS
        self.total_tokens_used += tokens
        self.total_cost += cost
        self.session_log.append({"label": label, "tokens": tokens, "cost": cost})
        print(f"[Budget] {label}: {tokens} tokens | ${cost:.5f} | Session total: ${self.total_cost:.5f}")

    def report(self):
        print(f"\n[Budget Report] Total tokens: {self.total_tokens_used} | Total cost: ${self.total_cost:.5f}")
        over = self.total_cost > MAX_COST_PER_SESSION
        print(f"Session budget {'EXCEEDED' if over else 'OK'} (limit: ${MAX_COST_PER_SESSION})")