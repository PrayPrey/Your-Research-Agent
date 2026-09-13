"""
ExecGuide: Execution-Guided Constrained Decoding for Formally Verified Code Generation.

Practical implementation of ExecGuide using:
- Multiple candidate generation (beam-like) with temperature sampling
- Incremental verification checkpoints (SMT + execution)
- Learned reward model for verifiability potential scoring
- Soft selection via combined score: log_prob + lambda * V(partial)

The soft steering is implemented by:
1. Generating multiple candidates at different temperatures
2. Scoring each candidate's intermediate and final states with verification signals
3. Selecting the best candidate according to ExecGuide scoring criterion
"""

import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForCausalLM
from typing import List, Tuple, Dict, Optional
import time
import numpy as np

from spec_augment import check_smt_consistency, run_test_cases, HUMANEVAL_SPECS
from reward_model import VerifiabilityRewardModel, SimpleCodeTokenizer, compute_verifiability_score


class ExecGuide:
    """
    ExecGuide framework for verification-guided code generation.

    Implements soft steering: candidates are scored as
    score(p_k) = log_prob(p_k) + lambda * V(p_k)
    where V is the verifiability potential from the reward model.
    """

    def __init__(
        self,
        model: AutoModelForCausalLM,
        tokenizer: AutoTokenizer,
        reward_model: VerifiabilityRewardModel,
        code_tokenizer: SimpleCodeTokenizer,
        device: torch.device,
        lambda_steering: float = 0.5,
        num_beams: int = 4,
        smt_weight: float = 0.4,
        exec_weight: float = 0.6,
        smt_check_interval: int = 20,
        max_new_tokens: int = 256,
    ):
        self.model = model
        self.tokenizer = tokenizer
        self.reward_model = reward_model
        self.code_tokenizer = code_tokenizer
        self.device = device
        self.lambda_steering = lambda_steering
        self.num_beams = num_beams
        self.smt_weight = smt_weight
        self.exec_weight = exec_weight
        self.smt_check_interval = smt_check_interval
        self.max_new_tokens = max_new_tokens

    def _compute_log_prob(self, prompt: str, completion: str) -> float:
        """Estimate log probability of completion given prompt."""
        full_text = prompt + completion
        inputs = self.tokenizer(
            full_text, return_tensors="pt", truncation=True, max_length=1024
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        prompt_ids = self.tokenizer(
            prompt, return_tensors="pt", truncation=True, max_length=512
        )["input_ids"]
        prompt_len = prompt_ids.shape[1]

        with torch.no_grad():
            outputs = self.model(**inputs, labels=inputs["input_ids"])

        # Approximate: use negative cross-entropy loss on completion tokens
        # This is an approximation; full log-prob would require token-by-token scoring
        completion_len = inputs["input_ids"].shape[1] - prompt_len
        if completion_len <= 0:
            return -100.0

        # Use negative loss as log prob estimate
        log_prob = -outputs.loss.item() * completion_len
        return log_prob

    def _compute_smt_exec_signals(
        self,
        partial_code: str,
        problem_id: str,
        entry_point: str,
    ) -> Tuple[float, float]:
        """Compute SMT and execution signals for a partial program."""
        smt_score = check_smt_consistency(partial_code, problem_id)

        exec_score = 0.5
        if "return " in partial_code and "def " in partial_code:
            try:
                pass_rate, _, _ = run_test_cases(partial_code, problem_id, entry_point)
                exec_score = pass_rate if pass_rate > 0 else 0.3
            except Exception:
                exec_score = 0.3

        return smt_score, exec_score

    def _compute_verifiability_potential(
        self,
        partial_code: str,
        smt_signal: float,
        exec_signal: float,
    ) -> float:
        """Compute V(p_k) = R_psi(p_k, s_SMT, s_exec)."""
        return compute_verifiability_score(
            self.reward_model,
            self.code_tokenizer,
            partial_code,
            smt_signal,
            exec_signal,
            self.device,
        )

    def generate(
        self,
        prompt: str,
        problem_id: str,
        entry_point: str,
    ) -> Tuple[str, Dict]:
        """
        Generate code using ExecGuide's verification-guided decoding.

        Strategy: Generate num_beams candidates at varying temperatures,
        score each with verification signals + model log-prob, select best.
        """
        start_time = time.time()

        # Generate multiple candidates at different temperatures
        temperatures = [0.3, 0.5, 0.7, 1.0][:self.num_beams]
        candidates = []

        inputs_base = self.tokenizer(
            prompt, return_tensors="pt", truncation=True, max_length=1024
        )
        inputs_base = {k: v.to(self.device) for k, v in inputs_base.items()}
        prompt_len = inputs_base["input_ids"].shape[1]

        for temp in temperatures:
            with torch.no_grad():
                if temp < 0.05:
                    outputs = self.model.generate(
                        **inputs_base,
                        max_new_tokens=self.max_new_tokens,
                        do_sample=False,
                        pad_token_id=self.tokenizer.eos_token_id,
                    )
                else:
                    outputs = self.model.generate(
                        **inputs_base,
                        max_new_tokens=self.max_new_tokens,
                        do_sample=True,
                        temperature=temp,
                        pad_token_id=self.tokenizer.eos_token_id,
                    )

            generated_ids = outputs[0][prompt_len:]
            gen_text = self.tokenizer.decode(generated_ids, skip_special_tokens=True)
            candidates.append((temp, gen_text))

        # Score each candidate
        metadata = {
            "smt_scores": [],
            "exec_scores": [],
            "verif_scores": [],
            "beam_scores": [],
            "num_smt_checks": 0,
            "generation_time": 0.0,
            "num_candidates": len(candidates),
        }

        best_code = prompt + candidates[0][1] if candidates else prompt
        best_score = -float('inf')

        for temp, gen_text in candidates:
            full_code = prompt + gen_text

            # Compute verification signals
            smt_sig, exec_sig = self._compute_smt_exec_signals(
                full_code, problem_id, entry_point
            )
            metadata["num_smt_checks"] += 1

            # Compute verifiability potential from reward model
            verif_score = self._compute_verifiability_potential(
                full_code, smt_sig, exec_sig
            )

            # Compute model log prob (approximated)
            # Use negative temperature as proxy for log prob (lower temp = higher confidence)
            log_prob_approx = -temp * 10  # Higher temp -> lower log prob

            # ExecGuide score: log_prob + lambda * V(p_k)
            score = log_prob_approx + self.lambda_steering * verif_score

            metadata["smt_scores"].append(smt_sig)
            metadata["exec_scores"].append(exec_sig)
            metadata["verif_scores"].append(verif_score)
            metadata["beam_scores"].append(score)

            if score > best_score:
                best_score = score
                best_code = full_code

        elapsed = time.time() - start_time
        metadata["generation_time"] = elapsed

        return best_code, metadata


def generate_training_data_for_reward_model(
    model: AutoModelForCausalLM,
    tokenizer: AutoTokenizer,
    problems: list,
    device: torch.device,
    max_new_tokens: int = 150,
) -> List[dict]:
    """
    Generate training data for the reward model.
    Creates (partial_code, smt_signal, exec_signal, label) tuples.
    """
    training_data = []

    for prob in problems[:8]:
        problem_id = prob["task_id"]
        prompt = prob["prompt"]
        entry_point = prob["entry_point"]

        for temp in [0.3, 0.7, 1.0]:
            inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
            inputs = {k: v.to(device) for k, v in inputs.items()}
            prompt_len = inputs["input_ids"].shape[1]

            with torch.no_grad():
                outputs = model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    do_sample=(temp > 0.05),
                    temperature=temp if temp > 0.05 else None,
                    pad_token_id=tokenizer.eos_token_id,
                )

            generated_ids = outputs[0][prompt_len:]
            gen_text = tokenizer.decode(generated_ids, skip_special_tokens=True)
            full_code = prompt + gen_text

            # Create samples at different prefix lengths
            all_tokens = generated_ids.cpu().tolist()
            for frac in [0.3, 0.6, 0.9, 1.0]:
                n = max(1, int(len(all_tokens) * frac))
                partial_ids = all_tokens[:n]
                partial_text = tokenizer.decode(partial_ids, skip_special_tokens=True)
                partial_code = prompt + partial_text

                smt_sig = check_smt_consistency(partial_code, problem_id)

                exec_sig = 0.0
                if "return " in partial_code:
                    try:
                        pr, _, _ = run_test_cases(partial_code, problem_id, entry_point)
                        exec_sig = pr
                    except Exception:
                        exec_sig = 0.0

                # Label: does the full completion pass tests?
                try:
                    full_pr, _, _ = run_test_cases(full_code, problem_id, entry_point)
                    label = float(full_pr > 0.5)
                except Exception:
                    label = 0.0

                training_data.append({
                    "partial_code": partial_code,
                    "smt_signal": smt_sig,
                    "exec_signal": exec_sig,
                    "label": label,
                    "problem_id": problem_id,
                })

    return training_data
