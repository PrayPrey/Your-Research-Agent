"""
Realistic mock LLM interface that simulates varying success rates and shows differences between methods.
"""

import random
from typing import Optional
from llm_interface_mock import MockLLMInterface


class RealisticMockLLM(MockLLMInterface):
    """More realistic mock with varying success rates and method differentiation."""

    def __init__(self, model_name: str = "realistic-mock", temperature: float = 0.7, max_tokens: int = 2048, seed_offset: int = 0):
        super().__init__(model_name, temperature, max_tokens)
        # Different difficulty levels for different tasks
        self.task_difficulty = {
            1: 0.3,  # easy
            2: 0.3,  # easy
            3: 0.2,  # easy
            4: 0.4,  # easy-medium
            5: 0.4,  # easy-medium
            6: 0.4,  # easy-medium
            7: 0.5,  # medium
            8: 0.5,  # medium
            9: 0.5,  # medium
            10: 0.7, # medium-hard
            11: 0.6, # medium-hard
            12: 0.4, # medium
            13: 0.6, # medium-hard
            14: 0.7, # hard
            15: 0.6, # medium-hard
            16: 0.7, # hard
            17: 0.6, # medium-hard
            18: 0.8, # hard
            19: 0.5, # medium
            20: 0.9, # very hard
        }
        self.current_task_id = None
        self.attempt_count = {}  # Track attempts per task
        self.seed_offset = seed_offset
        random.seed(42 + seed_offset)

    def set_current_task(self, task_id: int):
        """Set the current task being worked on."""
        self.current_task_id = task_id
        if task_id not in self.attempt_count:
            self.attempt_count[task_id] = 0

    def generate_code(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate mock code with realistic failure rates."""
        self.call_count += 1

        # Extract task info
        function_name = self._extract_function_name(prompt)

        # Determine if this should fail based on task difficulty
        difficulty = self.task_difficulty.get(self.current_task_id, 0.3)

        # First attempt has higher failure rate
        if self.current_task_id and self.attempt_count.get(self.current_task_id, 0) == 0:
            failure_prob = difficulty
        else:
            # Reduce failure probability with attempts
            attempt = self.attempt_count.get(self.current_task_id, 0)
            failure_prob = max(0.05, difficulty - attempt * 0.1)

        # Generate base code
        base_code = super().generate_code(prompt, system_prompt)

        # Decide if we should introduce a bug
        if random.random() < failure_prob:
            return self._introduce_realistic_bug(base_code)

        return base_code

    def generate_fix(self, task_description: str, failed_code: str, error_message: str,
                     test_results: list, method: str = "simple") -> str:
        """Generate a fix with method-specific success rates."""
        self.call_count += 1

        if self.current_task_id:
            self.attempt_count[self.current_task_id] = self.attempt_count.get(self.current_task_id, 0) + 1

        difficulty = self.task_difficulty.get(self.current_task_id, 0.3)
        attempt = self.attempt_count.get(self.current_task_id, 1)

        # Different methods have different base success rates
        if method == "simple":
            base_success = 0.40
        elif method == "reflection":
            base_success = 0.50
        elif method == "counterfactual":
            base_success = 0.65
        else:
            base_success = 0.35

        # Success improves with attempts
        success_prob = base_success + (attempt - 1) * 0.10
        # But is hindered by task difficulty
        success_prob = success_prob * (1.0 - difficulty * 0.5)
        # Cap at reasonable maximum
        success_prob = min(0.95, success_prob)

        # Generate code
        prompt = f"Task: {task_description}\nFailed code: {failed_code}"
        base_code = super().generate_code(prompt)

        # Decide if the fix is successful
        if random.random() < success_prob:
            return base_code
        else:
            return self._introduce_realistic_bug(base_code)

    def _introduce_realistic_bug(self, code: str) -> str:
        """Introduce realistic bugs into code."""
        lines = code.split('\n')

        # Choose a random bug type
        bug_type = random.choice(['comparison', 'boundary', 'logic', 'return'])

        if bug_type == 'comparison' and len(lines) > 2:
            # Change comparison operators
            for i in range(len(lines)):
                if '<=' in lines[i] and random.random() < 0.7:
                    lines[i] = lines[i].replace('<=', '<', 1)
                    break
                elif '>=' in lines[i] and random.random() < 0.7:
                    lines[i] = lines[i].replace('>=', '>', 1)
                    break
                elif '==' in lines[i] and random.random() < 0.5:
                    lines[i] = lines[i].replace('==', '!=', 1)
                    break

        elif bug_type == 'boundary' and len(lines) > 2:
            # Off-by-one errors
            for i in range(len(lines)):
                if 'range(' in lines[i]:
                    # Modify range bounds
                    if '- 1' in lines[i]:
                        lines[i] = lines[i].replace('- 1', '', 1)
                    elif '+ 1' in lines[i]:
                        lines[i] = lines[i].replace('+ 1', '', 1)
                    break

        elif bug_type == 'logic' and len(lines) > 2:
            # Change logical operators
            for i in range(len(lines)):
                if ' and ' in lines[i] and random.random() < 0.6:
                    lines[i] = lines[i].replace(' and ', ' or ', 1)
                    break
                elif ' or ' in lines[i] and random.random() < 0.6:
                    lines[i] = lines[i].replace(' or ', ' and ', 1)
                    break

        elif bug_type == 'return':
            # Wrong return value in edge cases
            for i in range(len(lines)):
                if 'return None' in lines[i]:
                    lines[i] = lines[i].replace('return None', 'return 0')
                    break
                elif 'return 0' in lines[i] and 'return' in lines[i]:
                    lines[i] = lines[i].replace('return 0', 'return None')
                    break

        return '\n'.join(lines)
