"""Refinement loops: AI-critic and random baseline."""

import random
from typing import List
from model import CodeLLM
import config


class AICriticRefinement:
    """Iteratively refine code using LLM-generated critique."""

    def __init__(self, generator: CodeLLM, k: int = config.K_ITERS):
        self.generator = generator
        self.k = k

    def generate_initial(self, prompt: str) -> str:
        """Generate initial code from problem description."""
        gen_prompt = f"{prompt}\n# Write the function implementation below:\n"
        return self.generator.generate(gen_prompt)

    def generate_feedback(self, code: str, problem: str) -> str:
        """AI critic generates natural language feedback."""
        critique_prompt = f"""Review this code for the problem:

Problem: {problem}

Code:
```python
{code}
```

Identify any bugs, logic errors, or edge cases missed. Be specific and concise."""
        return self.generator.generate(critique_prompt)

    def refine_code(self, code: str, feedback: str, problem: str) -> str:
        """Refine code based on feedback."""
        refine_prompt = f"""Fix the code based on this feedback:

Problem: {problem}

Current code:
```python
{code}
```

Feedback: {feedback}

Provide only the corrected Python code:"""
        return self.generator.generate(refine_prompt)

    def run(self, problem: str) -> List[str]:
        """Full refinement loop. Returns code snapshots at each iteration."""
        code = self.generate_initial(problem)
        snapshots = [code]

        for _ in range(self.k):
            feedback = self.generate_feedback(code, problem)
            code = self.refine_code(code, feedback, problem)
            snapshots.append(code)

        return snapshots


class RandomFeedbackRefinement(AICriticRefinement):
    """Control: Replace AI critique with random text."""

    RANDOM_FEEDBACK = [
        "The code looks fine.",
        "Consider edge cases.",
        "Check variable names.",
        "Maybe add comments.",
        "Looks good to me.",
        "Try a different approach.",
        "Review the logic.",
        "Test more cases.",
    ]

    def generate_feedback(self, code: str, problem: str) -> str:
        """Override: return random/nonsense feedback."""
        random.seed(hash(code) % (2**31))
        return random.choice(self.RANDOM_FEEDBACK)
