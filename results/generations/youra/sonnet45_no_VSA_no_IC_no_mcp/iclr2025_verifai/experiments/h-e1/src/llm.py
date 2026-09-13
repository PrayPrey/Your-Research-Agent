"""Code generation with CodeLlama."""

from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import json
from typing import Optional
from pathlib import Path


class CodeLlamaGenerator:
    """Generate code solutions using code generation model."""

    def __init__(
        self,
        model_name: str = "Salesforce/codegen-350M-mono",
        device: str = "auto",
        torch_dtype: torch.dtype = torch.float16
    ):
        print(f"Loading model: {model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        # Use safe tensors to avoid torch.load vulnerability
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch_dtype,
            device_map=device,
            use_safetensors=True
        )
        self.device = device
        print("Model loaded")

    def generate(
        self,
        prompt: str,
        max_new_tokens: int = 512,
        temperature: float = 0.0
    ) -> str:
        """Generate code for single prompt."""
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature if temperature > 0 else 1.0,
                do_sample=temperature > 0,
                top_p=1.0,
                pad_token_id=self.tokenizer.eos_token_id
            )

        generated = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        # Strip input prompt from output
        if generated.startswith(prompt):
            generated = generated[len(prompt):]

        return generated.strip()

    def generate_batch(
        self,
        prompts: list[str],
        max_new_tokens: int = 512,
        batch_size: int = 1
    ) -> list[str]:
        """Generate code for multiple prompts."""
        results = []
        total = len(prompts)

        for i in range(0, total, batch_size):
            batch = prompts[i:i+batch_size]

            for idx, prompt in enumerate(batch):
                global_idx = i + idx
                if (global_idx + 1) % 10 == 0 or global_idx + 1 == total:
                    print(f"  Generating {global_idx + 1}/{total}")

                code = self.generate(prompt, max_new_tokens, temperature=0.0)
                results.append(code)

        return results

    def save_generations(
        self,
        benchmark_name: str,
        problems: list[dict],
        generations: list[str],
        output_path: str
    ) -> None:
        """Save generations to JSON."""
        data = {
            "benchmark": benchmark_name,
            "model": self.model.config._name_or_path,
            "total_problems": len(problems),
            "problems": [
                {
                    **problem,
                    "generated_code": gen
                }
                for problem, gen in zip(problems, generations)
            ]
        }

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)

        print(f"Saved {len(generations)} generations to {output_path}")
