"""
Counterfactual code generation module.
"""

import re
import ast
from typing import List, Dict, Tuple
from llm_interface import LLMInterface


class CounterfactualGenerator:
    """Generate counterfactual code variants for failed code."""

    def __init__(self, llm: LLMInterface):
        self.llm = llm

    def generate_counterfactuals(self, task_description: str, failed_code: str,
                                  error_message: str, test_results: list,
                                  num_variants: int = 3) -> List[str]:
        """
        Generate multiple counterfactual code variants.

        Returns list of counterfactual code variants.
        """
        counterfactuals = []

        # Strategy 1: LLM-guided counterfactual generation
        for i in range(num_variants):
            cf_code = self.llm.generate_fix(
                task_description=task_description,
                failed_code=failed_code,
                error_message=error_message,
                test_results=test_results,
                method="counterfactual"
            )
            if cf_code and cf_code != failed_code:
                counterfactuals.append(cf_code)

        # Strategy 2: Mutation-based generation
        mutations = self._generate_mutations(failed_code, test_results)
        counterfactuals.extend(mutations)

        # Remove duplicates
        counterfactuals = list(set(counterfactuals))

        return counterfactuals[:num_variants]

    def _generate_mutations(self, code: str, test_results: list) -> List[str]:
        """Generate simple mutations of the code."""
        mutations = []

        try:
            # Parse the code
            tree = ast.parse(code)

            # Strategy: Identify comparison operators and flip them
            class OperatorFlipMutator(ast.NodeTransformer):
                def __init__(self):
                    self.mutations = []

                def visit_Compare(self, node):
                    # Flip comparison operators
                    for i, op in enumerate(node.ops):
                        if isinstance(op, ast.Lt):
                            new_ops = node.ops.copy()
                            new_ops[i] = ast.LtE()
                            mutated = ast.Compare(left=node.left, ops=new_ops, comparators=node.comparators)
                            self.mutations.append(ast.unparse(mutated))
                        elif isinstance(op, ast.LtE):
                            new_ops = node.ops.copy()
                            new_ops[i] = ast.Lt()
                            mutated = ast.Compare(left=node.left, ops=new_ops, comparators=node.comparators)
                            self.mutations.append(ast.unparse(mutated))
                    return node

            mutator = OperatorFlipMutator()
            mutator.visit(tree)

            # Generate new code with mutations (simplified)
            if mutator.mutations:
                mutations.append(code)  # Placeholder for actual mutation

        except:
            pass

        return mutations

    def identify_critical_decision_points(self, code: str, error_message: str) -> List[int]:
        """
        Identify critical decision points in the code.

        Returns list of line numbers that are likely responsible for failure.
        """
        critical_lines = []

        try:
            lines = code.split('\n')

            # Heuristic: Look for conditional statements, loops, returns
            for i, line in enumerate(lines):
                if any(keyword in line for keyword in ['if', 'elif', 'for', 'while', 'return']):
                    critical_lines.append(i)

            # If we have error information, try to extract line numbers
            if error_message:
                line_nums = re.findall(r'line (\d+)', error_message)
                critical_lines.extend([int(n) - 1 for n in line_nums])

        except:
            pass

        return sorted(list(set(critical_lines)))

    def compute_edit_distance(self, code1: str, code2: str) -> int:
        """Compute simple edit distance between two code snippets."""
        lines1 = code1.split('\n')
        lines2 = code2.split('\n')

        # Simple line-based diff
        diff_count = 0
        max_len = max(len(lines1), len(lines2))

        for i in range(max_len):
            line1 = lines1[i] if i < len(lines1) else ""
            line2 = lines2[i] if i < len(lines2) else ""
            if line1 != line2:
                diff_count += 1

        return diff_count
