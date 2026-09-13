import ast as ast_module
import json
from typing import Any, Dict, List


class MetricsEvaluator:
    def compute_ast_failure_rate(self, pool: Dict[str, List[str]]) -> float:
        """Fraction of all completions failing ast.parse()."""
        total = 0
        failures = 0
        for completions in pool.values():
            for code in completions:
                total += 1
                try:
                    ast_module.parse(code)
                except SyntaxError:
                    failures += 1
        return failures / total if total > 0 else 0.0

    def compute_delta_ast(
        self,
        baseline_pool: Dict[str, List[str]],
        syncode_pool: Dict[str, List[str]],
    ) -> float:
        """delta_ast = baseline_fail_rate - syncode_fail_rate. Gate: > 0."""
        baseline_rate = self.compute_ast_failure_rate(baseline_pool)
        syncode_rate = self.compute_ast_failure_rate(syncode_pool)
        return baseline_rate - syncode_rate

    def compute_z3_eligibility_rate(
        self, eligibility: Dict[str, bool]
    ) -> float:
        """eligible_count / total_humaneval_count. Gate: >= 0.15."""
        if not eligibility:
            return 0.0
        eligible = sum(1 for v in eligibility.values() if v)
        return eligible / len(eligibility)

    def compute_mypy_structured_rate(
        self, mypy_results: Dict[str, Any]
    ) -> float:
        """Rate at which mypy returns structured output (exit_code in {0,1,2}).
        Exit codes 0 (clean), 1 (type errors found), 2 (fatal/syntax error) all
        indicate mypy ran and produced parseable output. A crash or exception would
        leave exit_code as None. Gate: >= 0.90."""
        if not mypy_results:
            return 0.0
        structured = sum(
            1 for r in mypy_results.values()
            if r.get("exit_code") in (0, 1, 2)
        )
        return structured / len(mypy_results)

    def evaluate_gate(
        self,
        delta_ast: float,
        z3_rate: float,
        mypy_rate: float,
        output_path: str,
    ) -> Dict[str, Any]:
        """Evaluate gate conditions; serialize metrics; return result dict."""
        gate_pass = (
            delta_ast > 0.0 and
            z3_rate >= 0.15 and
            mypy_rate >= 0.90
        )

        result = {
            "delta_ast": delta_ast,
            "z3_eligibility_rate": z3_rate,
            "mypy_structured_rate": mypy_rate,
            "gate_pass": gate_pass,
            "gate_checks": {
                "delta_ast_pass": delta_ast > 0.0,
                "z3_rate_pass": z3_rate >= 0.15,
                "mypy_rate_pass": mypy_rate >= 0.90,
            },
            "thresholds": {
                "delta_ast_min": 0.0,
                "z3_eligibility_min": 0.15,
                "mypy_structured_rate_min": 0.90,
            },
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2)

        status = "GATE PASS" if gate_pass else "GATE FAIL"
        print(f"\n{'='*60}")
        print(f"  {status}")
        print(f"  delta_ast={delta_ast:.4f} (>0: {delta_ast > 0})")
        print(f"  z3_rate={z3_rate:.4f} (>=0.15: {z3_rate >= 0.15})")
        print(f"  mypy_rate={mypy_rate:.4f} (>=0.90: {mypy_rate >= 0.90})")
        print(f"{'='*60}\n")

        return result
