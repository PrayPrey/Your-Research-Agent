import json
import time
from typing import Dict, List

import torch
import transformers
from transformers import AutoModelForCausalLM, AutoTokenizer


class BaselineGenerator:
    def __init__(
        self,
        model_name: str = "codellama/CodeLlama-7b-hf",
        temperature: float = 0.8,
        max_new_tokens: int = 256,
        n_samples: int = 20,
    ) -> None:
        self.model_name = model_name
        self.temperature = temperature
        self.max_new_tokens = max_new_tokens
        self.n_samples = n_samples
        self.model = None
        self.tokenizer = None

    def load_model(self) -> None:
        """Load CodeLlama-7B with device_map='auto'."""
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            device_map="auto",
            torch_dtype=torch.float16,
        )
        self.model.eval()

    def _generate_single(self, prompt: str, seed: int) -> str:
        """Generate one completion with fixed seed. Returns decoded new tokens only."""
        torch.manual_seed(seed)
        transformers.set_seed(seed)

        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            add_special_tokens=False,
        ).to(self.model.device)

        prompt_len = inputs["input_ids"].shape[1]

        with torch.no_grad():
            output_ids = self.model.generate(
                **inputs,
                do_sample=True,
                temperature=self.temperature,
                max_new_tokens=self.max_new_tokens,
                pad_token_id=self.tokenizer.eos_token_id,
            )

        new_tokens = output_ids[0, prompt_len:]
        completion = self.tokenizer.decode(new_tokens, skip_special_tokens=True)
        return completion

    def generate_pool(
        self,
        problems: Dict[str, dict],
        seeds: List[int],
        output_path: str,
    ) -> Dict[str, List[str]]:
        """Generate N=20 completions per problem; serialize to JSONL."""
        pool: Dict[str, List[str]] = {}

        with open(output_path, "w", encoding="utf-8") as f:
            for task_id, problem in problems.items():
                prompt = problem["prompt"]
                completions = []
                for seed in seeds:
                    t0 = time.time()
                    completion = self._generate_single(prompt, seed)
                    generation_time = time.time() - t0

                    record = {
                        "task_id": task_id,
                        "completion": completion,
                        "seed": seed,
                        "generation_time": generation_time,
                    }
                    f.write(json.dumps(record, ensure_ascii=False) + "\n")
                    completions.append(completion)

                pool[task_id] = completions
                print(f"  [{task_id}] {len(completions)} samples generated")

        return pool
