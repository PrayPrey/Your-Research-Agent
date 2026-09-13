import ast
import json
import os
from typing import Dict, List, Optional, Set

import torch
import transformers
from transformers import AutoModelForCausalLM, AutoTokenizer


class ExtendedBaselineGenerator:

    def __init__(
        self,
        model_name: str = "codellama/CodeLlama-7b-hf",
        temperature: float = 0.8,
        max_new_tokens: int = 512,
        n_samples: int = 20,
    ) -> None:
        self.model_name = model_name
        self.temperature = temperature
        self.max_new_tokens = max_new_tokens
        self.n_samples = n_samples
        self.model = None
        self.tokenizer = None

    def load_model(self) -> None:
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            device_map="auto",
            torch_dtype=torch.float16,
        )
        self.model.eval()

    def _compute_seed(self, problem_idx: int, sample_idx: int) -> int:
        return problem_idx * 100 + sample_idx

    def _generate_single(self, prompt: str, seed: int) -> str:
        torch.manual_seed(seed)
        transformers.set_seed(seed)
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=self.max_new_tokens,
                temperature=self.temperature,
                top_p=0.95,
                do_sample=True,
                pad_token_id=self.tokenizer.eos_token_id,
            )
        generated = outputs[0][inputs["input_ids"].shape[1]:]
        return self.tokenizer.decode(generated, skip_special_tokens=True)

    def load_h_e1_pool(self, h_e1_path: str) -> Dict[str, List[dict]]:
        records: Dict[str, List[dict]] = {}
        if not os.path.exists(h_e1_path):
            return records
        with open(h_e1_path, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                task_id = rec["task_id"]
                completion = rec.get("completion", "")
                try:
                    ast.parse(completion)
                    ast_valid = True
                except SyntaxError:
                    ast_valid = False
                new_rec = {
                    "task_id": task_id,
                    "problem_idx": None,
                    "sample_idx": None,
                    "seed": rec.get("seed"),
                    "completion": completion,
                    "ast_valid": ast_valid,
                }
                records.setdefault(task_id, []).append(new_rec)
        return records

    def load_progress(self, progress_path: str) -> Set[str]:
        if not os.path.exists(progress_path):
            return set()
        with open(progress_path, "r") as f:
            data = json.load(f)
        return set(data.get("completed", []))

    def _save_progress(self, progress_path: str, completed: Set[str]) -> None:
        with open(progress_path, "w") as f:
            json.dump({"completed": sorted(completed)}, f)

    def generate_pool(
        self,
        problems: Dict[str, dict],
        output_path: str,
        progress_path: str,
        h_e1_pool_path: Optional[str] = None,
    ) -> Dict[str, List[dict]]:
        completed = self.load_progress(progress_path)
        h_e1_recs: Dict[str, List[dict]] = {}
        if h_e1_pool_path:
            h_e1_recs = self.load_h_e1_pool(h_e1_pool_path)

        # Load existing records from disk
        existing: Dict[str, List[dict]] = {}
        if os.path.exists(output_path):
            with open(output_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    rec = json.loads(line)
                    existing.setdefault(rec["task_id"], []).append(rec)

        pool: Dict[str, List[dict]] = dict(existing)

        with open(output_path, "a") as out_f:
            for problem_idx, (task_id, problem) in enumerate(sorted(problems.items())):
                if task_id in completed:
                    if task_id not in pool and task_id in existing:
                        pool[task_id] = existing[task_id]
                    continue

                records = []

                if task_id in h_e1_recs:
                    # Reuse h-e1 completions (seed scheme differs, document this)
                    records = h_e1_recs[task_id]
                    for i, rec in enumerate(records):
                        rec = dict(rec)
                        rec["problem_idx"] = problem_idx
                        rec["sample_idx"] = i
                        records[i] = rec
                        out_f.write(json.dumps(rec) + "\n")
                else:
                    prompt = problem.get("prompt", "")
                    for sample_idx in range(self.n_samples):
                        seed = self._compute_seed(problem_idx, sample_idx)
                        completion = self._generate_single(prompt, seed)
                        try:
                            ast.parse(completion)
                            ast_valid = True
                        except SyntaxError:
                            ast_valid = False
                        rec = {
                            "task_id": task_id,
                            "problem_idx": problem_idx,
                            "sample_idx": sample_idx,
                            "seed": seed,
                            "completion": completion,
                            "ast_valid": ast_valid,
                        }
                        out_f.write(json.dumps(rec) + "\n")
                        records.append(rec)
                    out_f.flush()

                pool[task_id] = records
                completed.add(task_id)
                self._save_progress(progress_path, completed)
                print(f"[Baseline] Completed {task_id} ({problem_idx+1}/164)")

        return pool
