"""
Reward model implementations for HierAlign experiment.

Implements:
1. BinaryReward: Standard pass/fail (0 or 1)
2. HierarchicalReward: Multi-level feedback (syntactic + runtime + coverage + semantic)
3. SyntaxOnlyReward: Only syntactic validity (ablation)
4. CoverageReward: Syntax + partial coverage (ablation)
"""
import ast
import math
from typing import List, Dict, Tuple
from utils import check_syntax, run_test_case, extract_function_name


# Error penalty weights based on semantic distance from correctness
ERROR_PENALTY_WEIGHTS = {
    "SyntaxError": 1.0,       # Worst - not even valid code
    "IndentationError": 0.95,
    "NameError": 0.4,          # Easily repaired
    "TypeError": 0.5,
    "AttributeError": 0.45,
    "IndexError": 0.35,        # Suggests partial logic
    "KeyError": 0.35,
    "ValueError": 0.3,
    "ZeroDivisionError": 0.25,
    "RecursionError": 0.6,     # Harder to repair
    "AssertionError": 0.2,     # Test failed but code ran
    "TimeoutError": 0.7,
    "StopIteration": 0.3,
    "Other": 0.5,
}


def get_error_penalty(error_type: str) -> float:
    """Get penalty weight for a given error type."""
    return ERROR_PENALTY_WEIGHTS.get(error_type, ERROR_PENALTY_WEIGHTS["Other"])


class BinaryReward:
    """Standard binary pass/fail reward."""
    name = "binary"

    def compute(self, code: str, tests: List[str]) -> Dict:
        if not tests:
            syntax_ok, _ = check_syntax(code)
            score = 1.0 if syntax_ok else 0.0
            return {"reward": score, "passed_tests": 0, "total_tests": 0}

        all_passed = True
        for test in tests:
            result = run_test_case(code, test)
            if not result["passed"]:
                all_passed = False
                break

        score = 1.0 if all_passed else 0.0
        passed = sum(1 for t in tests if run_test_case(code, t)["passed"])
        return {
            "reward": score,
            "passed_tests": passed,
            "total_tests": len(tests),
            "components": {"binary": score}
        }


class SyntaxOnlyReward:
    """Ablation: only syntactic validity."""
    name = "syntax_only"

    def compute(self, code: str, tests: List[str]) -> Dict:
        syntax_ok, err = check_syntax(code)
        score = 1.0 if syntax_ok else 0.0
        passed = sum(1 for t in tests if run_test_case(code, t)["passed"])
        return {
            "reward": score,
            "passed_tests": passed,
            "total_tests": len(tests),
            "components": {"syntax": score}
        }


class CoverageReward:
    """Ablation: syntax + partial test coverage (no runtime/semantic)."""
    name = "coverage"

    def compute(self, code: str, tests: List[str]) -> Dict:
        syntax_ok, _ = check_syntax(code)
        r_syn = 1.0 if syntax_ok else 0.0

        if not syntax_ok:
            return {
                "reward": 0.0,
                "passed_tests": 0,
                "total_tests": len(tests),
                "components": {"syntax": 0.0, "coverage": 0.0}
            }

        if not tests:
            return {
                "reward": r_syn * 0.5,
                "passed_tests": 0,
                "total_tests": 0,
                "components": {"syntax": r_syn, "coverage": 0.0}
            }

        passed_tests = []
        for test in tests:
            result = run_test_case(code, test)
            passed_tests.append(result["passed"])

        r_cov = sum(passed_tests) / len(tests)
        reward = 0.3 * r_syn + 0.7 * r_cov

        return {
            "reward": reward,
            "passed_tests": sum(passed_tests),
            "total_tests": len(tests),
            "components": {"syntax": r_syn, "coverage": r_cov}
        }


class HierarchicalReward:
    """
    Full HierAlign hierarchical reward:
    Level 1: Syntactic validity
    Level 2: Runtime error classification with penalty shaping
    Level 3: Partial test coverage
    Level 4: Semantic distance via code structure similarity
    Combined via learned weights (approximated here with principled fixed weights).
    """
    name = "hierarchical"

    # Weights for combining reward components
    # These approximate the learned combiner g_psi
    WEIGHTS = {
        "syntax": 0.15,
        "runtime": 0.20,
        "coverage": 0.45,
        "semantic": 0.20,
    }

    def compute(self, code: str, tests: List[str]) -> Dict:
        # Level 1: Syntactic validity
        syntax_ok, _ = check_syntax(code)
        r_syn = 1.0 if syntax_ok else 0.0

        if not syntax_ok:
            return {
                "reward": 0.0,
                "passed_tests": 0,
                "total_tests": len(tests),
                "components": {
                    "syntax": 0.0,
                    "runtime": 0.0,
                    "coverage": 0.0,
                    "semantic": 0.0
                }
            }

        # Level 2: Runtime error classification
        r_run = self._compute_runtime_reward(code, tests)

        # Level 3: Partial test coverage
        passed_results = []
        error_types = []
        for test in tests:
            res = run_test_case(code, test)
            passed_results.append(res["passed"])
            if not res["passed"] and res.get("error_type"):
                error_types.append(res["error_type"])

        r_cov = sum(passed_results) / len(tests) if tests else 0.0

        # Level 4: Semantic distance via structural analysis
        r_sem = self._compute_semantic_reward(code)

        # Combine with weighted sum
        w = self.WEIGHTS
        reward = (w["syntax"] * r_syn +
                  w["runtime"] * r_run +
                  w["coverage"] * r_cov +
                  w["semantic"] * r_sem)

        return {
            "reward": reward,
            "passed_tests": sum(passed_results),
            "total_tests": len(tests),
            "components": {
                "syntax": r_syn,
                "runtime": r_run,
                "coverage": r_cov,
                "semantic": r_sem
            }
        }

    def _compute_runtime_reward(self, code: str, tests: List[str]) -> float:
        """Level 2: Runtime error classification with penalty shaping."""
        if not tests:
            # Try to execute with empty call to detect immediate errors
            try:
                exec(code, {})
                return 1.0
            except Exception as e:
                penalty = get_error_penalty(type(e).__name__)
                return 1.0 - penalty

        # Run first test case to get runtime behavior
        first_result = run_test_case(code, tests[0])
        if first_result["passed"] or first_result.get("error_type") == "AssertionError":
            return 1.0  # Code runs, just maybe wrong answer

        error_type = first_result.get("error_type", "Other")
        penalty = get_error_penalty(error_type)
        return 1.0 - penalty

    def _compute_semantic_reward(self, code: str) -> float:
        """
        Level 4: Semantic similarity via code structure analysis.
        Approximates trace embedding similarity using AST features.
        """
        try:
            tree = ast.parse(code)
        except Exception:
            return 0.0

        # Extract structural features as proxy for execution trace similarity
        features = self._extract_ast_features(tree)

        # Score based on structural quality indicators
        score = 0.0

        # Has a function definition
        if features["has_function"]:
            score += 0.3

        # Uses return statement
        if features["has_return"]:
            score += 0.2

        # Has reasonable complexity (not trivial, not excessively complex)
        n_ops = features["n_operations"]
        if 1 <= n_ops <= 20:
            score += 0.2
        elif n_ops > 0:
            score += 0.1

        # Uses appropriate control flow
        if features["has_control_flow"]:
            score += 0.15

        # Has meaningful variable usage
        if features["n_assignments"] > 0:
            score += 0.1

        # Penalize empty functions
        if features["n_statements"] <= 1:
            score -= 0.2

        return max(0.0, min(1.0, score))

    def _extract_ast_features(self, tree: ast.AST) -> Dict:
        """Extract structural features from AST."""
        features = {
            "has_function": False,
            "has_return": False,
            "has_control_flow": False,
            "n_operations": 0,
            "n_assignments": 0,
            "n_statements": 0,
        }

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                features["has_function"] = True
                features["n_statements"] = len(node.body)
            elif isinstance(node, ast.Return):
                features["has_return"] = True
            elif isinstance(node, (ast.If, ast.For, ast.While, ast.Try)):
                features["has_control_flow"] = True
            elif isinstance(node, (ast.Add, ast.Sub, ast.Mult, ast.Div,
                                   ast.Compare, ast.BoolOp, ast.UnaryOp)):
                features["n_operations"] += 1
            elif isinstance(node, (ast.Assign, ast.AugAssign, ast.AnnAssign)):
                features["n_assignments"] += 1

        return features


def get_reward_model(name: str):
    """Factory function for reward models."""
    models = {
        "binary": BinaryReward,
        "syntax_only": SyntaxOnlyReward,
        "coverage": CoverageReward,
        "hierarchical": HierarchicalReward,
    }
    if name not in models:
        raise ValueError(f"Unknown reward model: {name}. Choose from {list(models.keys())}")
    return models[name]()
