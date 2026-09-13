"""Planner agent for task decomposition."""


class PlannerAgent:
    """Agent for task decomposition and planning."""

    def __init__(self, model, tokenizer):
        self.model = model
        self.tokenizer = tokenizer

    def plan(self, task_description: str) -> str:
        """Generate task decomposition strategy."""
        prompt = f"""You are a software development planner. Given a task description, create a clear plan.

Task: {task_description}

Provide a concise plan with key steps:"""

        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        outputs = self.model.generate(
            **inputs,
            max_new_tokens=256,
            temperature=0.7,
            top_p=0.95,
            do_sample=True
        )
        plan = self.tokenizer.decode(outputs[0][inputs['input_ids'].shape[1]:], skip_special_tokens=True)
        return plan.strip()
