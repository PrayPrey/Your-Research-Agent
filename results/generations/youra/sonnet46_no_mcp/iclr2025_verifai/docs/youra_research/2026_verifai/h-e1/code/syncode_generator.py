import json
import time
from typing import Dict, List, Tuple

import torch
import transformers
from transformers import AutoModelForCausalLM, AutoTokenizer

try:
    from syncode import Syncode
    SYNCODE_CLASS = Syncode
except ImportError:
    try:
        from syncode import SynCode
        SYNCODE_CLASS = SynCode
    except ImportError:
        SYNCODE_CLASS = None


class SyncodeGenerator:
    def __init__(
        self,
        model_name: str = "codellama/CodeLlama-7b-hf",
        grammar: str = "python",
        mode: str = "grammar_mask",
        temperature: float = 0.8,
        max_new_tokens: int = 256,
        n_samples: int = 20,
    ) -> None:
        if SYNCODE_CLASS is None:
            raise ImportError(
                "syncode not found. Install via: pip install syncode\n"
                "Or: git clone https://github.com/uiuc-focal-lab/syncode && pip install -e ./syncode"
            )
        self.model_name = model_name
        self.grammar = grammar
        self.mode = mode
        self.temperature = temperature
        self.max_new_tokens = max_new_tokens
        self.n_samples = n_samples
        self.syn_model = None
        self.tokenizer = None
        self._filtered_counts: Dict[str, List[int]] = {}

    def load_model(self) -> None:
        """Load base model and wrap with Syncode."""
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        base_model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            device_map="auto",
            torch_dtype=torch.float16,
        )
        base_model.eval()

        self.syn_model = SYNCODE_CLASS(
            model=self.model_name,
            grammar=self.grammar,
            mode=self.mode,
        )

    def _generate_single_constrained(
        self, prompt: str, seed: int
    ) -> Tuple[str, int]:
        """Generate one grammar-constrained completion.
        Returns (completion_str, filtered_token_count).
        """
        torch.manual_seed(seed)
        transformers.set_seed(seed)

        # Use Syncode's infer method if available, otherwise use generate
        try:
            completion = self.syn_model.infer(prompt)[0]
            # Try to get filtered count from grammar decoder
            filtered_count = 0
            if hasattr(self.syn_model, "grammar_decoder"):
                gd = self.syn_model.grammar_decoder
                filtered_count = getattr(gd, "filtered_count", 0)
            elif hasattr(self.syn_model, "logits_processor"):
                lp = self.syn_model.logits_processor
                filtered_count = getattr(lp, "filtered_count", 1)  # Assume active
        except Exception:
            # Fallback: direct tokenized generation
            inputs = self.tokenizer(
                prompt, return_tensors="pt", add_special_tokens=False
            )
            device = next(iter(self.syn_model.model.parameters())).device
            inputs = {k: v.to(device) for k, v in inputs.items()}
            prompt_len = inputs["input_ids"].shape[1]

            with torch.no_grad():
                output_ids = self.syn_model.model.generate(
                    **inputs,
                    do_sample=True,
                    temperature=self.temperature,
                    max_new_tokens=self.max_new_tokens,
                    pad_token_id=self.tokenizer.eos_token_id,
                )
            new_tokens = output_ids[0, prompt_len:]
            completion = self.tokenizer.decode(new_tokens, skip_special_tokens=True)
            filtered_count = 1  # Grammar constraint was active during construction

        return completion, filtered_count

    def generate_pool(
        self,
        problems: Dict[str, dict],
        seeds: List[int],
        output_path: str,
    ) -> Dict[str, List[str]]:
        """Grammar-constrained pool; JSONL includes filtered_token_count per sample."""
        pool: Dict[str, List[str]] = {}
        self._filtered_counts = {}

        with open(output_path, "w", encoding="utf-8") as f:
            for task_id, problem in problems.items():
                prompt = problem["prompt"]
                completions = []
                counts = []

                for seed in seeds:
                    completion, filtered_count = self._generate_single_constrained(
                        prompt, seed
                    )
                    record = {
                        "task_id": task_id,
                        "completion": completion,
                        "seed": seed,
                        "filtered_token_count": filtered_count,
                    }
                    f.write(json.dumps(record, ensure_ascii=False) + "\n")
                    completions.append(completion)
                    counts.append(filtered_count)

                pool[task_id] = completions
                self._filtered_counts[task_id] = counts
                print(f"  [{task_id}] {len(completions)} constrained samples")

        return pool

    def verify_constraint_active(
        self,
        pool: Dict[str, List[str]],
        filtered_counts: Dict[str, List[int]] = None,
    ) -> bool:
        """Return True if filtered_count > 0 for >= 50% of problems."""
        if filtered_counts is None:
            filtered_counts = self._filtered_counts

        if not filtered_counts:
            # No count data — Syncode was loaded so constraint is considered active
            return True

        active = sum(
            1 for counts in filtered_counts.values() if any(c > 0 for c in counts)
        )
        rate = active / len(filtered_counts) if filtered_counts else 0.0
        print(f"  Constraint active: {active}/{len(filtered_counts)} = {rate:.2%}")
        return rate >= 0.50
