"""Coder agent for code generation."""


class CoderAgent:
    """Agent for code generation from plans."""

    def __init__(self, model, tokenizer):
        self.model = model
        self.tokenizer = tokenizer

    def generate_code(self, plan: str, task_description: str, max_attempts: int = 3) -> str:
        """Generate initial code solution."""
        prompt = f"""You are a Python code generator. Based on the plan and task, generate clean Python code.

Plan: {plan}

Task: {task_description}

Generate Python code:
```python"""

        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=512,
            temperature=0.7,
            top_p=0.95,
            do_sample=True
        )
        code = self.tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)

        # Extract code from markdown if present
        if '```python' in code:
            code = code.split('```python')[1].split('```')[0]
        elif '```' in code:
            code = code.split('```')[1].split('```')[0]

        return code.strip()
