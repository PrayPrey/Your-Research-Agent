import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import re


class CodeGenerator:
    def __init__(self, model_id: str, device: str = "cuda", seed: int = 1):
        self.device = device
        self.tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_id,
            torch_dtype=torch.float16,
            device_map="auto",
            trust_remote_code=True
        )
        self.model.eval()
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

    def _extract_code(self, text: str) -> str:
        match = re.search(r"```(?:python)?\n?(.*?)```", text, re.DOTALL)
        if match:
            return match.group(1).strip()
        lines = text.strip().split("\n")
        code_lines = []
        in_code = False
        for line in lines:
            if line.startswith("def ") or line.startswith("class ") or line.startswith("import ") or line.startswith("from "):
                in_code = True
            if in_code:
                code_lines.append(line)
        return "\n".join(code_lines) if code_lines else text.strip()

    def generate(self, prompt: str, temperature: float = 0.2, max_new_tokens: int = 512) -> str:
        full_prompt = f"Write Python code for the following task:\n{prompt}\n\nPython code:"
        inputs = self.tokenizer(full_prompt, return_tensors="pt").to(self.device)
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                do_sample=temperature > 0,
                pad_token_id=self.tokenizer.pad_token_id
            )
        text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        if full_prompt in text:
            text = text[len(full_prompt):]
        return self._extract_code(text)

    def refine(self, prompt: str, code: str, feedback: str, temperature: float = 0.2, max_new_tokens: int = 512) -> str:
        from feedback_formatter import build_refine_prompt
        full_prompt = build_refine_prompt(prompt, code, feedback)
        inputs = self.tokenizer(full_prompt, return_tensors="pt", truncation=True, max_length=2048).to(self.device)
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                do_sample=temperature > 0,
                pad_token_id=self.tokenizer.pad_token_id
            )
        text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        if full_prompt in text:
            text = text[len(full_prompt):]
        return self._extract_code(text)
