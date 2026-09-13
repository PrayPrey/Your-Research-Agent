"""Compute budget tracking for fair baseline comparison."""

from dataclasses import dataclass, field
from typing import Optional
import time


@dataclass
class ComputeBudget:
    """Compute budget for an experiment run."""
    total_tokens: int = 0
    verifier_time_seconds: float = 0.0
    llm_api_calls: int = 0
    iterations: int = 0

    def to_dict(self):
        return {
            'total_tokens': self.total_tokens,
            'verifier_time_seconds': self.verifier_time_seconds,
            'llm_api_calls': self.llm_api_calls,
            'iterations': self.iterations
        }


class ComputeBudgetTracker:
    """Tracks compute budget (tokens + verifier time) for fair comparison."""

    def __init__(self, target_budget: Optional[ComputeBudget] = None):
        self.target_budget = target_budget
        self.current_budget = ComputeBudget()
        self._iteration_count = 0

    def record_llm_call(self, prompt_tokens: int, completion_tokens: int):
        """Record an LLM API call."""
        self.current_budget.total_tokens += (prompt_tokens + completion_tokens)
        self.current_budget.llm_api_calls += 1

    def record_verifier_call(self, execution_time: float):
        """Record a verifier execution."""
        self.current_budget.verifier_time_seconds += execution_time

    def start_iteration(self):
        """Mark the start of a new iteration."""
        self._iteration_count += 1
        self.current_budget.iterations = self._iteration_count

    def get_budget(self) -> ComputeBudget:
        """Get current budget."""
        return self.current_budget

    def exceeds_target(self, tolerance: float = 0.10) -> bool:
        """Check if current budget exceeds target by more than tolerance."""
        if self.target_budget is None:
            return False

        token_ratio = self.current_budget.total_tokens / max(self.target_budget.total_tokens, 1)
        time_ratio = self.current_budget.verifier_time_seconds / max(self.target_budget.verifier_time_seconds, 0.1)

        return token_ratio > (1.0 + tolerance) or time_ratio > (1.0 + tolerance)

    def fork(self) -> 'ComputeBudgetTracker':
        """Create a new tracker with the same target budget."""
        return ComputeBudgetTracker(target_budget=self.target_budget)
