"""Llama-3-8B-Instruct N=10 sampling with intermediate save/resume."""
import json
import os

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


class LLMSampler:
    def __init__(
        self,
        model_id: str = "meta-llama/Meta-Llama-3-8B-Instruct",
        torch_dtype: torch.dtype = torch.float16,
        device_map: str = "auto",
    ) -> None:
        print(f"Loading LLM: {model_id}")
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.tokenizer.padding_side = "left"
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        self.model = AutoModelForCausalLM.from_pretrained(
            model_id, torch_dtype=torch_dtype, device_map=device_map
        )
        self.model.eval()
        print("LLM loaded.")

    def sample(
        self,
        question: str,
        n: int = 10,
        temperature: float = 0.7,
        top_p: float = 0.9,
        max_new_tokens: int = 50,
    ) -> list:
        """Generate N answer strings for a question."""
        messages = [{"role": "user", "content": f"Answer in one short phrase: {question}"}]
        prompt = self.tokenizer.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        prompt_len = inputs["input_ids"].shape[1]

        with torch.no_grad():
            out = self.model.generate(
                **inputs,
                do_sample=True,
                temperature=temperature,
                top_p=top_p,
                max_new_tokens=max_new_tokens,
                num_return_sequences=n,
                pad_token_id=self.tokenizer.pad_token_id,
            )

        return [
            self.tokenizer.decode(out[i, prompt_len:], skip_special_tokens=True).strip()
            for i in range(n)
        ]

    def sample_all(
        self,
        questions: list,
        save_path: str,
        resume: bool = True,
        **kwargs,
    ) -> list:
        """Generate samples for all questions with intermediate save/resume."""
        all_samples = {}
        if resume and os.path.exists(save_path):
            with open(save_path) as f:
                all_samples = json.load(f)
            print(f"Resumed from {save_path}: {len(all_samples)} already done")

        os.makedirs(os.path.dirname(save_path) if os.path.dirname(save_path) else ".", exist_ok=True)

        for i, q in enumerate(questions):
            if str(i) in all_samples:
                continue
            all_samples[str(i)] = self.sample(q, **kwargs)
            if (i + 1) % 50 == 0:
                with open(save_path, "w") as f:
                    json.dump(all_samples, f)
                print(f"Progress: {i+1}/{len(questions)} questions sampled")

        with open(save_path, "w") as f:
            json.dump(all_samples, f)
        print(f"Saved all samples to {save_path}")

        return [all_samples[str(i)] for i in range(len(questions))]
