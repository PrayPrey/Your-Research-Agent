import re
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from sandbox import execute_code
from feedback import format_execution_feedback, generate_random_feedback
from config import CONFIG

class ExecutionFeedbackRefinement:
    def __init__(
        self,
        model_id: str = None,
        max_iterations: int = None,
        temperature: float = None,
        max_tokens: int = None,
        top_p: float = None,
    ):
        self.model_id = model_id or CONFIG.model_id
        self.max_iterations = max_iterations or CONFIG.max_iterations
        self.temperature = temperature or CONFIG.temperature
        self.max_tokens = max_tokens or CONFIG.max_tokens
        self.top_p = top_p or CONFIG.top_p

        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_id,
            torch_dtype=torch.float16,
            device_map="auto",
        )
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

    def _extract_code(self, text: str) -> str:
        # Extract code from markdown fences
        match = re.search(r"```(?:python)?\n?(.*?)```", text, re.DOTALL)
        if match:
            return match.group(1).strip()
        # If no fences, return as-is (might be raw code)
        return text.strip()

    def initial_generate(self, prompt: str) -> str:
        full_prompt = f"Write a Python function to solve the following problem:\n\n{prompt}\n\nProvide only the code, no explanation."
        inputs = self.tokenizer(full_prompt, return_tensors="pt").to(self.model.device)
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=self.max_tokens,
            temperature=self.temperature,
            top_p=self.top_p,
            do_sample=True,
            pad_token_id=self.tokenizer.pad_token_id,
        )
        generated = self.tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
        return self._extract_code(generated)

    def refine_code(self, prompt: str, code: str, feedback: str) -> str:
        full_prompt = f"""Fix the following Python code based on the feedback.

Problem:
{prompt}

Previous attempt:
```python
{code}
```

Feedback:
{feedback}

Fixed code:"""
        inputs = self.tokenizer(full_prompt, return_tensors="pt").to(self.model.device)
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=self.max_tokens,
            temperature=self.temperature,
            top_p=self.top_p,
            do_sample=True,
            pad_token_id=self.tokenizer.pad_token_id,
        )
        generated = self.tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
        return self._extract_code(generated)

    def generate_with_refinement(
        self,
        problem: dict,
        feedback_type: str,
    ) -> tuple[str, bool, int, list[str]]:
        code = self.initial_generate(problem["prompt"])
        feedback_log = []

        for iteration in range(1, self.max_iterations + 1):
            result = execute_code(code, problem["tests"], CONFIG.timeout_sec, CONFIG.mem_limit_mb)
            if result.passed:
                return code, True, iteration, feedback_log

            if feedback_type == "execution":
                feedback = format_execution_feedback(result)
            else:
                feedback = generate_random_feedback()

            feedback_log.append(feedback)
            code = self.refine_code(problem["prompt"], code, feedback)

        # Final check
        result = execute_code(code, problem["tests"], CONFIG.timeout_sec, CONFIG.mem_limit_mb)
        return code, result.passed, self.max_iterations, feedback_log
