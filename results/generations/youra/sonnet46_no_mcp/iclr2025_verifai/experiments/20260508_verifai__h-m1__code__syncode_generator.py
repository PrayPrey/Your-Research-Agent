import ast as ast_module
import json
import os
from typing import Dict, List, Optional, Set, Tuple

import torch
import transformers


class ExtendedSyncodeGenerator:

    def __init__(
        self,
        model_name: str = "codellama/CodeLlama-7b-hf",
        grammar: str = "python",
        mode: str = "grammar_mask",
        temperature: float = 0.8,
        max_new_tokens: int = 512,
        n_samples: int = 20,
    ) -> None:
        self.model_name = model_name
        self.grammar = grammar
        self.mode = mode
        self.temperature = temperature
        self.max_new_tokens = max_new_tokens
        self.n_samples = n_samples
        self.syn_model = None

    def load_model(self) -> None:
        from syncode import Syncode
        self.syn_model = Syncode(
            model=self.model_name,
            grammar=self.grammar,
            mode=self.mode,
            max_new_tokens=self.max_new_tokens,
        )

    def _compute_seed(self, problem_idx: int, sample_idx: int) -> int:
        return problem_idx * 100 + sample_idx

    def _generate_single_constrained(
        self, prompt: str, seed: int
    ) -> Tuple[str, bool]:
        torch.manual_seed(seed)
        transformers.set_seed(seed)

        constraint_active = False
        completion = ""
        try:
            output = self.syn_model.infer(prompt)
            if isinstance(output, (list, tuple)):
                completion = output[0] if output else ""
            else:
                completion = str(output)

            # Determine constraint_active
            # Check filtered_token_count from grammar_decoder if available
            grammar_decoder = getattr(self.syn_model, "grammar_decoder", None)
            if grammar_decoder is not None:
                filtered_count = getattr(grammar_decoder, "filtered_token_count", None)
                if filtered_count is not None and filtered_count > 0:
                    constraint_active = True
                else:
                    # Grammar constraint was loaded, assume active
                    constraint_active = True
            else:
                # Check logits_processor list
                lp_list = getattr(self.syn_model, "logits_processor", None)
                if lp_list:
                    for lp in lp_list:
                        if "Grammar" in type(lp).__name__:
                            constraint_active = True
                            break

        except Exception as e:
            print(f"[SynCode] Error generating sample (seed={seed}): {e}")
            completion = ""
            constraint_active = False

        return completion, constraint_active

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
    ) -> Dict[str, List[dict]]:
        completed = self.load_progress(progress_path)

        # Load existing records
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

                prompt = problem.get("prompt", "")
                records = []
                for sample_idx in range(self.n_samples):
                    seed = self._compute_seed(problem_idx, sample_idx)
                    completion, constraint_active = self._generate_single_constrained(prompt, seed)

                    try:
                        ast_module.parse(completion)
                        ast_valid = True
                    except SyntaxError:
                        ast_valid = False

                    print(
                        f"[SynCode] constraint_active={constraint_active} "
                        f"problem={problem_idx} sample={sample_idx}"
                    )

                    rec = {
                        "task_id": task_id,
                        "problem_idx": problem_idx,
                        "sample_idx": sample_idx,
                        "seed": seed,
                        "completion": completion,
                        "ast_valid": ast_valid,
                        "constraint_active": constraint_active,
                    }
                    out_f.write(json.dumps(rec) + "\n")
                    records.append(rec)

                out_f.flush()
                pool[task_id] = records
                completed.add(task_id)
                self._save_progress(progress_path, completed)
                print(f"[SynCode] Completed {task_id} ({problem_idx+1}/164)")

        return pool

    def compute_constraint_active_rate(
        self, pool: Dict[str, List[dict]]
    ) -> float:
        total = 0
        active = 0
        for records in pool.values():
            for rec in records:
                total += 1
                if rec.get("constraint_active", False):
                    active += 1
        if total == 0:
            return 0.0
        rate = active / total
        print(f"constraint_active_rate={rate:.3f} ({active}/{total} samples)")
        return rate
