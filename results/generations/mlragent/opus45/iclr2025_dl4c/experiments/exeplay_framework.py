"""
ExePlay Framework Implementation
Execution-Guided Self-Play for Code Agent Alignment
"""
import torch
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from transformers import AutoModelForCausalLM, AutoTokenizer
from typing import List, Dict, Any, Tuple, Optional
import random
from dataclasses import dataclass
import numpy as np

from execution_feedback import (
    execute_code_with_tests,
    compute_execution_quality_score,
    extract_code_from_response,
    generate_critique,
    ExecutionResult
)
from config import EQS_WEIGHTS, DPO_CONFIG


@dataclass
class PreferencePair:
    """Preference pair for DPO training"""
    task_id: str
    prompt: str
    chosen: str  # Better solution
    rejected: str  # Worse solution
    chosen_eqs: float
    rejected_eqs: float
    margin: float  # EQS difference


class ExePlayFramework:
    """
    ExePlay: Execution-Guided Self-Play Framework for Code Agent Alignment

    The framework operates in three phases:
    1. Generation: Generate multiple solutions for each task
    2. Critique: Analyze failed solutions and generate critiques
    3. Contrastive Alignment: Construct preference pairs and update model
    """

    def __init__(
        self,
        model_name: str,
        device: str = "cuda",
        eqs_weights: Optional[Dict[str, float]] = None,
        dpo_beta: float = 0.1,
        lambda_margin: float = 0.5
    ):
        """
        Initialize the ExePlay framework.

        Args:
            model_name: HuggingFace model name
            device: Device to use for inference
            eqs_weights: Weights for EQS computation
            dpo_beta: Beta parameter for DPO
            lambda_margin: Lambda for margin weighting
        """
        self.device = device
        self.eqs_weights = eqs_weights or EQS_WEIGHTS
        self.dpo_beta = dpo_beta
        self.lambda_margin = lambda_margin

        print(f"Loading model: {model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            device_map="auto",
            trust_remote_code=True
        )

        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
            self.model.config.pad_token_id = self.tokenizer.eos_token_id

        # Store reference model for DPO (frozen copy)
        self.ref_model = None  # Will be initialized when training starts

    def generate_solutions(
        self,
        task: Dict[str, Any],
        num_samples: int = 4,
        temperature: float = 0.7,
        max_length: int = 256
    ) -> List[str]:
        """
        Generate multiple solutions for a task.

        Args:
            task: Task dictionary with 'problem' and 'prompt'
            num_samples: Number of solutions to generate
            temperature: Sampling temperature
            max_length: Maximum generation length

        Returns:
            List of generated code solutions
        """
        prompt = self._create_generation_prompt(task)
        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        solutions = []
        for _ in range(num_samples):
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_length,
                    temperature=temperature,
                    do_sample=True,
                    top_p=0.95,
                    pad_token_id=self.tokenizer.pad_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                )

            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            # Extract the generated part (after the prompt)
            code = generated_text[len(prompt):].strip()
            code = extract_code_from_response(code)

            # Combine with the function signature if needed
            if 'prompt' in task and task['prompt'].strip().startswith('def '):
                if not code.strip().startswith('def '):
                    code = task['prompt'] + '\n' + code

            solutions.append(code)

        return solutions

    def _create_generation_prompt(self, task: Dict[str, Any]) -> str:
        """Create a prompt for code generation."""
        problem = task.get('problem', '')
        prompt = task.get('prompt', '')

        if prompt:
            return f"# Problem: {problem}\n\n# Complete the following function:\n{prompt}\n"
        else:
            return f"# Problem: {problem}\n\n# Write a Python function to solve this problem:\n"

    def execute_and_score(
        self,
        solutions: List[str],
        task: Dict[str, Any]
    ) -> List[Tuple[str, ExecutionResult, float]]:
        """
        Execute solutions and compute EQS scores.

        Args:
            solutions: List of code solutions
            task: Task dictionary with test cases

        Returns:
            List of (solution, execution_result, eqs_score) tuples
        """
        results = []
        test_cases = task.get('test_cases', [])

        for solution in solutions:
            exec_result = execute_code_with_tests(
                solution,
                test_cases,
                timeout=5
            )
            eqs = compute_execution_quality_score(exec_result, weights=self.eqs_weights)
            results.append((solution, exec_result, eqs))

        return results

    def generate_critiques(
        self,
        failed_solutions: List[Tuple[str, ExecutionResult, float]],
        task: Dict[str, Any]
    ) -> List[str]:
        """
        Generate critiques for failed solutions.

        Args:
            failed_solutions: List of (solution, exec_result, eqs) tuples
            task: Task dictionary

        Returns:
            List of critique strings
        """
        critiques = []
        for solution, exec_result, eqs in failed_solutions:
            critique = generate_critique(
                solution,
                exec_result,
                task.get('problem', '')
            )
            critiques.append(critique)
        return critiques

    def construct_preference_pairs(
        self,
        scored_solutions: List[Tuple[str, ExecutionResult, float]],
        task: Dict[str, Any],
        min_margin: float = 0.1
    ) -> List[PreferencePair]:
        """
        Construct preference pairs from scored solutions.

        Args:
            scored_solutions: List of (solution, exec_result, eqs) tuples
            task: Task dictionary
            min_margin: Minimum EQS difference to create a pair

        Returns:
            List of PreferencePair objects
        """
        pairs = []
        prompt = self._create_generation_prompt(task)

        # Sort by EQS score
        sorted_solutions = sorted(scored_solutions, key=lambda x: x[2], reverse=True)

        # Create pairs from solutions with different scores
        for i in range(len(sorted_solutions)):
            for j in range(i + 1, len(sorted_solutions)):
                sol_i, _, eqs_i = sorted_solutions[i]
                sol_j, _, eqs_j = sorted_solutions[j]

                margin = eqs_i - eqs_j
                if margin >= min_margin:
                    pair = PreferencePair(
                        task_id=str(task.get('id', '')),
                        prompt=prompt,
                        chosen=sol_i,
                        rejected=sol_j,
                        chosen_eqs=eqs_i,
                        rejected_eqs=eqs_j,
                        margin=margin
                    )
                    pairs.append(pair)

        return pairs

    def compute_dpo_loss(
        self,
        chosen_logprobs: torch.Tensor,
        rejected_logprobs: torch.Tensor,
        ref_chosen_logprobs: torch.Tensor,
        ref_rejected_logprobs: torch.Tensor,
        margins: torch.Tensor
    ) -> torch.Tensor:
        """
        Compute weighted DPO loss with margin weighting.

        Args:
            chosen_logprobs: Log probs of chosen sequences
            rejected_logprobs: Log probs of rejected sequences
            ref_chosen_logprobs: Reference model log probs for chosen
            ref_rejected_logprobs: Reference model log probs for rejected
            margins: EQS margins for weighting

        Returns:
            DPO loss tensor
        """
        # Policy ratios
        pi_logratios = chosen_logprobs - rejected_logprobs
        ref_logratios = ref_chosen_logprobs - ref_rejected_logprobs

        # DPO objective
        logits = self.dpo_beta * (pi_logratios - ref_logratios)

        # Margin-based weights: w(m) = 1 + lambda * m
        weights = 1 + self.lambda_margin * margins

        # Weighted negative log-sigmoid loss
        losses = -F.logsigmoid(logits) * weights

        return losses.mean()

    def run_iteration(
        self,
        tasks: List[Dict[str, Any]],
        samples_per_task: int = 4,
        temperature: float = 0.7,
        max_length: int = 256
    ) -> Tuple[List[PreferencePair], Dict[str, Any]]:
        """
        Run one iteration of the ExePlay loop.

        Args:
            tasks: List of task dictionaries
            samples_per_task: Number of samples to generate per task
            temperature: Sampling temperature
            max_length: Maximum generation length

        Returns:
            Tuple of (preference_pairs, iteration_stats)
        """
        all_pairs = []
        stats = {
            'total_solutions': 0,
            'passed_solutions': 0,
            'failed_solutions': 0,
            'avg_eqs': 0.0,
            'pairs_generated': 0
        }

        eqs_scores = []

        for task in tasks:
            # Phase 1: Generation
            solutions = self.generate_solutions(
                task,
                num_samples=samples_per_task,
                temperature=temperature,
                max_length=max_length
            )
            stats['total_solutions'] += len(solutions)

            # Phase 1b: Execute and score
            scored_solutions = self.execute_and_score(solutions, task)

            for _, exec_result, eqs in scored_solutions:
                eqs_scores.append(eqs)
                if exec_result.passed:
                    stats['passed_solutions'] += 1
                else:
                    stats['failed_solutions'] += 1

            # Phase 2: Generate critiques for failed solutions
            failed_solutions = [
                (sol, res, eqs) for sol, res, eqs in scored_solutions
                if not res.passed
            ]
            if failed_solutions:
                self.generate_critiques(failed_solutions, task)

            # Phase 3: Construct preference pairs
            pairs = self.construct_preference_pairs(scored_solutions, task)
            all_pairs.extend(pairs)
            stats['pairs_generated'] += len(pairs)

        stats['avg_eqs'] = np.mean(eqs_scores) if eqs_scores else 0.0
        stats['pass_rate'] = stats['passed_solutions'] / stats['total_solutions'] if stats['total_solutions'] > 0 else 0.0

        return all_pairs, stats


class PreferencePairDataset(Dataset):
    """Dataset for DPO training with preference pairs."""

    def __init__(
        self,
        pairs: List[PreferencePair],
        tokenizer,
        max_length: int = 512
    ):
        self.pairs = pairs
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.pairs)

    def __getitem__(self, idx):
        pair = self.pairs[idx]

        chosen_text = pair.prompt + pair.chosen
        rejected_text = pair.prompt + pair.rejected

        chosen_encoding = self.tokenizer(
            chosen_text,
            truncation=True,
            max_length=self.max_length,
            padding='max_length',
            return_tensors='pt'
        )

        rejected_encoding = self.tokenizer(
            rejected_text,
            truncation=True,
            max_length=self.max_length,
            padding='max_length',
            return_tensors='pt'
        )

        return {
            'chosen_input_ids': chosen_encoding['input_ids'].squeeze(),
            'chosen_attention_mask': chosen_encoding['attention_mask'].squeeze(),
            'rejected_input_ids': rejected_encoding['input_ids'].squeeze(),
            'rejected_attention_mask': rejected_encoding['attention_mask'].squeeze(),
            'margin': torch.tensor(pair.margin, dtype=torch.float32)
        }
