from typing import TypedDict
from analyzers import BanditAnalyzer, PylintAnalyzer
from feedback_formatter import format_issues_for_prompt
from metrics import count_issues


class IterationRecord(TypedDict):
    iteration: int
    code: str
    security_count: int
    reliability_count: int


class LoopResult(TypedDict):
    initial: dict
    final: dict
    iterations: int
    history: list[IterationRecord]


class IterationController:
    def __init__(
        self,
        generator,
        bandit: BanditAnalyzer,
        pylint: PylintAnalyzer,
        max_iterations: int = 5,
        timeout_s: int = 30,
    ):
        self.generator = generator
        self.bandit = bandit
        self.pylint = pylint
        self.max_iterations = max_iterations
        self.timeout_s = timeout_s

    def _analyze(self, code: str) -> tuple[list[dict], list[dict]]:
        bandit_issues = self.bandit.run(code, self.timeout_s)
        pylint_issues = self.pylint.run(code, self.timeout_s)
        return bandit_issues, pylint_issues

    def run(self, initial_code: str, prompt: str, temperature: float = 0.2, max_new_tokens: int = 512) -> LoopResult:
        code = initial_code
        bandit_issues, pylint_issues = self._analyze(code)
        counts = count_issues(bandit_issues, pylint_issues)
        sec0, rel0 = counts["security"], counts["reliability"]

        initial = {"code": code, "security_count": sec0, "reliability_count": rel0}
        history: list[IterationRecord] = [{
            "iteration": 0,
            "code": code,
            "security_count": sec0,
            "reliability_count": rel0
        }]

        current_sec, current_rel = sec0, rel0
        for i in range(1, self.max_iterations + 1):
            if current_sec == 0 and current_rel == 0:
                break

            feedback = format_issues_for_prompt(bandit_issues, pylint_issues)
            code = self.generator.refine(prompt, code, feedback, temperature, max_new_tokens)

            bandit_issues, pylint_issues = self._analyze(code)
            counts = count_issues(bandit_issues, pylint_issues)
            current_sec, current_rel = counts["security"], counts["reliability"]

            history.append({
                "iteration": i,
                "code": code,
                "security_count": current_sec,
                "reliability_count": current_rel
            })

        final = {"code": code, "security_count": current_sec, "reliability_count": current_rel}
        return {
            "initial": initial,
            "final": final,
            "iterations": len(history) - 1,
            "history": history
        }
