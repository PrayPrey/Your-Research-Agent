"""
Agent implementations with realistic mock support.
"""

from typing import Dict, List, Tuple
from code_executor import CodeExecutor
from counterfactual_generator import CounterfactualGenerator


class BaseAgent:
    """Base agent for code generation."""

    def __init__(self, llm, executor: CodeExecutor):
        self.llm = llm
        self.executor = executor

    def generate_initial_code(self, task_description: str, function_name: str, task_id: int = None) -> str:
        """Generate initial code for a task."""
        if hasattr(self.llm, 'set_current_task') and task_id:
            self.llm.set_current_task(task_id)

        prompt = f"""Write a Python function to solve the following task:

Task: {task_description}

The function should be named '{function_name}'.

Provide only the function code, no explanations or test cases.
"""
        system_prompt = "You are an expert Python programmer. Write clean, correct, and efficient code."

        return self.llm.generate_code(prompt, system_prompt)

    def solve_task(self, task: Dict, max_attempts: int = 5) -> Dict:
        """Solve a programming task."""
        raise NotImplementedError


class SimpleRetryAgent(BaseAgent):
    """Agent that uses simple retry with error feedback."""

    def solve_task(self, task: Dict, max_attempts: int = 5) -> Dict:
        """Solve task using simple retry strategy."""
        task_id = task["id"]
        description = task["description"]
        function_name = task["function_name"]
        test_cases = task["test_cases"]

        attempts = []
        success = False

        # Generate initial code
        code = self.generate_initial_code(description, function_name, task_id)

        for attempt in range(max_attempts):
            # Execute code
            passed, results, error_msg = self.executor.execute_code(code, test_cases)

            attempts.append({
                "attempt": attempt + 1,
                "code": code,
                "passed": passed,
                "test_results": results,
                "error": error_msg
            })

            if passed:
                success = True
                break

            # Generate fix if not passed
            if attempt < max_attempts - 1:
                if hasattr(self.llm, 'set_current_task'):
                    self.llm.set_current_task(task_id)

                code = self.llm.generate_fix(
                    task_description=description,
                    failed_code=code,
                    error_message=error_msg,
                    test_results=results,
                    method="simple"
                )

        return {
            "task_id": task_id,
            "success": success,
            "attempts": len(attempts),
            "attempt_history": attempts
        }


class ReflectionAgent(BaseAgent):
    """Agent that uses reflection-based debugging."""

    def solve_task(self, task: Dict, max_attempts: int = 5) -> Dict:
        """Solve task using reflection strategy."""
        task_id = task["id"]
        description = task["description"]
        function_name = task["function_name"]
        test_cases = task["test_cases"]

        attempts = []
        success = False

        # Generate initial code
        code = self.generate_initial_code(description, function_name, task_id)

        for attempt in range(max_attempts):
            # Execute code
            passed, results, error_msg = self.executor.execute_code(code, test_cases)

            attempts.append({
                "attempt": attempt + 1,
                "code": code,
                "passed": passed,
                "test_results": results,
                "error": error_msg
            })

            if passed:
                success = True
                break

            # Generate fix using reflection
            if attempt < max_attempts - 1:
                if hasattr(self.llm, 'set_current_task'):
                    self.llm.set_current_task(task_id)

                code = self.llm.generate_fix(
                    task_description=description,
                    failed_code=code,
                    error_message=error_msg,
                    test_results=results,
                    method="reflection"
                )

        return {
            "task_id": task_id,
            "success": success,
            "attempts": len(attempts),
            "attempt_history": attempts
        }


class SECACEAgent(BaseAgent):
    """SECACE: Self-Evolving Code Agent through Counterfactual Execution Feedback."""

    def __init__(self, llm, executor: CodeExecutor):
        super().__init__(llm, executor)
        self.cf_generator = CounterfactualGenerator(llm)
        self.counterfactual_memory = []

    def solve_task(self, task: Dict, max_attempts: int = 5) -> Dict:
        """Solve task using SECACE strategy with counterfactual learning."""
        task_id = task["id"]
        description = task["description"]
        function_name = task["function_name"]
        test_cases = task["test_cases"]

        attempts = []
        success = False
        counterfactuals_generated = 0

        # Generate initial code
        code = self.generate_initial_code(description, function_name, task_id)

        for attempt in range(max_attempts):
            # Execute code
            passed, results, error_msg = self.executor.execute_code(code, test_cases)

            attempts.append({
                "attempt": attempt + 1,
                "code": code,
                "passed": passed,
                "test_results": results,
                "error": error_msg
            })

            if passed:
                success = True
                break

            # Generate counterfactual variants
            if attempt < max_attempts - 1:
                if hasattr(self.llm, 'set_current_task'):
                    self.llm.set_current_task(task_id)

                cf_variants = self.cf_generator.generate_counterfactuals(
                    task_description=description,
                    failed_code=code,
                    error_message=error_msg,
                    test_results=results,
                    num_variants=3
                )

                counterfactuals_generated += len(cf_variants)

                # Test each counterfactual
                best_variant = None
                best_score = -1

                for cf_code in cf_variants:
                    cf_passed, cf_results, cf_error = self.executor.execute_code(cf_code, test_cases)

                    # Score based on number of tests passed
                    score = sum(1 for r in cf_results if r["passed"])

                    if cf_passed:
                        # Found a successful counterfactual!
                        self.counterfactual_memory.append({
                            "failed_code": code,
                            "success_code": cf_code,
                            "task": description
                        })
                        code = cf_code
                        break

                    if score > best_score:
                        best_score = score
                        best_variant = cf_code

                # If no perfect counterfactual found, use best or generate new
                if not passed:
                    if best_variant and best_score > 0:
                        code = best_variant
                    else:
                        # Fallback to counterfactual method
                        code = self.llm.generate_fix(
                            task_description=description,
                            failed_code=code,
                            error_message=error_msg,
                            test_results=results,
                            method="counterfactual"
                        )

        return {
            "task_id": task_id,
            "success": success,
            "attempts": len(attempts),
            "counterfactuals_generated": counterfactuals_generated,
            "counterfactuals_in_memory": len(self.counterfactual_memory),
            "attempt_history": attempts
        }
