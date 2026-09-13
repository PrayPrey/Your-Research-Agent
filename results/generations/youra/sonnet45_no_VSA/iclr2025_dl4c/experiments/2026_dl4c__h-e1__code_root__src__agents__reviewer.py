"""Reviewer agent for code quality assessment."""


class ReviewerAgent:
    """Agent for code quality assessment."""

    def __init__(self, model, tokenizer):
        self.model = model
        self.tokenizer = tokenizer

    def review(self, code: str) -> dict:
        """Assess code quality."""
        prompt = f"""You are a code reviewer. Assess the quality of this Python code.

Code:
```python
{code}
```

Is this code acceptable? Answer with just "YES" or "NO":"""

        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=10,
            temperature=0.3,
            do_sample=False
        )
        response = self.tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)

        approved = 'yes' in response.lower()
        return {
            'approved': approved,
            'feedback': response.strip(),
            'quality_score': 1.0 if approved else 0.5
        }
