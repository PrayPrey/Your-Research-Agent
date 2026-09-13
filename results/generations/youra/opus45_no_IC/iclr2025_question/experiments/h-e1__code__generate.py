"""Response generation for H-E1 Benchmark Clustering Experiment."""

import os
import json
import torch
from typing import Dict, List
from transformers import AutoModelForCausalLM, AutoTokenizer
from config import GEN_MODEL, N_GENERATIONS, TEMPERATURE, MAX_NEW_TOKENS, CACHE_DIR


class ResponseGenerator:
    """Generate multiple responses per query using Llama-2-7B."""

    def __init__(self, model_name: str = GEN_MODEL, cache_dir: str = CACHE_DIR, device: str = "cuda"):
        self.cache_dir = cache_dir
        self.device = device
        os.makedirs(cache_dir, exist_ok=True)

        print(f"Loading {model_name}...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            device_map="auto",
        )
        self.model.eval()
        print("Model loaded.")

    def generate(self, question: str, n: int = N_GENERATIONS, temperature: float = TEMPERATURE) -> List[str]:
        """Generate n responses for a question."""
        prompt = f"Question: {question}\nAnswer:"
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        prompt_len = inputs.input_ids.shape[1]

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=MAX_NEW_TOKENS,
                do_sample=True,
                temperature=temperature,
                num_return_sequences=n,
                pad_token_id=self.tokenizer.pad_token_id,
            )

        responses = []
        for output in outputs:
            text = self.tokenizer.decode(output[prompt_len:], skip_special_tokens=True)
            responses.append(text.strip())

        return responses

    def _cache_path(self, benchmark: str, query_id: str) -> str:
        bench_dir = os.path.join(self.cache_dir, benchmark)
        os.makedirs(bench_dir, exist_ok=True)
        return os.path.join(bench_dir, f"{query_id}.json")

    def generate_for_benchmark(self, queries: List[Dict]) -> Dict[str, List[str]]:
        """Generate responses for all queries in a benchmark.

        Uses disk cache to skip already-generated queries.
        Returns dict mapping query_id to list of responses.
        """
        results = {}
        total = len(queries)

        for i, q in enumerate(queries):
            query_id = q["id"]
            benchmark = q["benchmark"]
            cache_path = self._cache_path(benchmark, query_id)

            if os.path.exists(cache_path):
                with open(cache_path, "r") as f:
                    results[query_id] = json.load(f)
            else:
                responses = self.generate(q["question"])
                with open(cache_path, "w") as f:
                    json.dump(responses, f)
                results[query_id] = responses

            if (i + 1) % 100 == 0:
                print(f"  {benchmark}: {i+1}/{total}")

        return results
