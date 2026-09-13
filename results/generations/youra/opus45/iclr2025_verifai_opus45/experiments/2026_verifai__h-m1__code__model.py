"""CodeLlama model wrapper for H-E1."""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from typing import Optional
from tqdm import tqdm

from config import ExperimentConfig
from data import format_prompt


class CodeGenerator:
    """CodeLlama-7B-Instruct inference wrapper."""

    def __init__(self, config: ExperimentConfig):
        """Initialize with config; model/tokenizer loaded lazily via load()."""
        self.config = config
        self.model: Optional[AutoModelForCausalLM] = None
        self.tokenizer: Optional[AutoTokenizer] = None

    def load(self) -> None:
        """Load tokenizer and model in float16 with device_map='auto'."""
        print(f"Loading model: {self.config.model_id}")
        self.tokenizer = AutoTokenizer.from_pretrained(self.config.model_id)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.config.model_id,
            torch_dtype=torch.float16,
            device_map="auto",
        )
        self.model.eval()
        print(f"Model loaded on device: {self.model.device}")

    def generate(self, prompt: str) -> str:
        """Single inference call.

        Args:
            prompt: Input prompt string

        Returns:
            Extracted code string
        """
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)

        with torch.no_grad():
            output_ids = self.model.generate(
                **inputs,
                max_new_tokens=self.config.max_new_tokens,
                temperature=self.config.temperature,
                do_sample=self.config.do_sample,
                pad_token_id=self.tokenizer.eos_token_id,
            )

        raw = self.tokenizer.decode(output_ids[0], skip_special_tokens=True)
        return self.extract_code(raw)

    def generate_batch(self, problems: list[dict]) -> list[str]:
        """Generate code for all problems sequentially.

        Args:
            problems: List of problem dicts

        Returns:
            List of generated code strings (len=N)
        """
        codes = []
        for p in tqdm(problems, desc="Generating code"):
            prompt = format_prompt(p)
            code = self.generate(prompt)
            codes.append(code)
        return codes

    def extract_code(self, raw_output: str) -> str:
        """Extract code from model output, handling multiple marker formats.

        Supports markers: [BEGIN]/[DONE], [PYTHON]/[END], ```python/```
        Falls back to cleaning raw output if no markers found.

        Args:
            raw_output: Raw model output string

        Returns:
            Extracted and cleaned code string
        """
        code = raw_output

        # Try [BEGIN]/[DONE] markers first
        if "[BEGIN]" in code:
            start = code.index("[BEGIN]") + len("[BEGIN]")
            if "[DONE]" in code:
                end = code.index("[DONE]")
                code = code[start:end].strip()
            else:
                code = code[start:].strip()

        # Try [PYTHON]/[END] markers
        if "[PYTHON]" in code:
            start = code.index("[PYTHON]") + len("[PYTHON]")
            if "[END]" in code:
                end = code.index("[END]")
                code = code[start:end].strip()
            elif "[/PYTHON]" in code:
                end = code.index("[/PYTHON]")
                code = code[start:end].strip()
            else:
                code = code[start:].strip()

        # Try markdown code blocks
        if "```python" in code:
            start = code.index("```python") + len("```python")
            if "```" in code[start:]:
                end = code.index("```", start)
                code = code[start:end].strip()
            else:
                code = code[start:].strip()

        # Clean up any remaining markers
        for marker in ["[PYTHON]", "[/PYTHON]", "[END]", "[BEGIN]", "[DONE]", "[/BEGIN]"]:
            code = code.replace(marker, "")

        return code.strip()
