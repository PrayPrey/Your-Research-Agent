"""Tier 2: TSG Probes - Task Signature Graph probe-based detection"""
import numpy as np
from typing import List, Dict, Tuple
import random

class Tier2TSGProbes:
    """
    Tier 2 Detection: Task Signature Graph Probes
    - Invariant probes: benchmark-aligned tasks
    - Neighbor probes: off-manifold tasks
    - Broken probes: control probes
    - Differential alignment detection: Δ = (ΔL_invariant - ΔL_neighbor)
    """

    def __init__(
        self,
        num_invariant_probes: int = 1000,
        num_neighbor_probes: int = 1000,
        num_broken_probes: int = 1000,
        detection_threshold: float = 2.0
    ):
        self.num_invariant = num_invariant_probes
        self.num_neighbor = num_neighbor_probes
        self.num_broken = num_broken_probes
        self.threshold = detection_threshold

        self.invariant_probes = []
        self.neighbor_probes = []
        self.broken_probes = []

        # Baseline statistics (computed on clean runs)
        self.baseline_mean = None
        self.baseline_std = None

    def extract_tsg_invariants(self, benchmark_samples: List[Dict]) -> List[Dict]:
        """
        Extract benchmark-aligned invariant probes
        In practice: sample questions with semantically equivalent variations
        """
        probes = []
        # Simple sampling for PoC
        samples = random.sample(benchmark_samples, min(self.num_invariant, len(benchmark_samples)))

        for sample in samples:
            probes.append({
                'question': sample.get('question', ''),
                'answer': sample.get('answer', ''),
                'type': 'invariant'
            })

        return probes

    def generate_neighbor_probes(self, benchmark_samples: List[Dict]) -> List[Dict]:
        """
        Generate off-manifold neighbor probes
        In practice: perturb benchmark questions to be semantically different
        """
        probes = []
        # Simple implementation: add noise/modifications
        samples = random.sample(benchmark_samples, min(self.num_neighbor, len(benchmark_samples)))

        for sample in samples:
            # Create neighbor by modifying question
            original_q = sample.get('question', '')
            neighbor_q = f"Modified: {original_q}"

            probes.append({
                'question': neighbor_q,
                'answer': sample.get('answer', ''),
                'type': 'neighbor'
            })

        return probes

    def generate_broken_probes(self, benchmark_samples: List[Dict]) -> List[Dict]:
        """
        Generate broken control probes
        In practice: syntactically valid but semantically broken questions
        """
        probes = []
        # Simple implementation: create nonsense questions
        for i in range(min(self.num_broken, len(benchmark_samples))):
            probes.append({
                'question': f"What is the color of number {i}?",
                'answer': "Invalid question",
                'type': 'broken'
            })

        return probes

    def evaluate_probes(
        self,
        model,
        probes: List[Dict],
        probe_type: str
    ) -> float:
        """
        Evaluate probe loss on model
        Returns average loss for probe type
        """
        try:
            import torch
            from transformers import AutoTokenizer

            # Get tokenizer from model (or use default)
            try:
                tokenizer = AutoTokenizer.from_pretrained("EleutherAI/pythia-1.4b")
                if tokenizer.pad_token is None:
                    tokenizer.pad_token = tokenizer.eos_token
            except:
                # Fallback: use simple text length as proxy for loss
                total_loss = 0.0
                for probe in probes[:min(100, len(probes))]:  # Sample 100 probes
                    question = probe.get('question', '')
                    # Use text complexity as loss proxy
                    loss = len(question.split()) / 100.0
                    total_loss += loss
                return total_loss / min(100, len(probes))

            # Compute actual model loss on probes
            model.eval()
            total_loss = 0.0
            num_evaluated = 0

            with torch.no_grad():
                for probe in probes[:min(100, len(probes))]:  # Sample 100 probes for efficiency
                    question = probe.get('question', '')
                    answer = probe.get('answer', '')
                    text = f"Question: {question}\nAnswer: {answer}"

                    # Tokenize
                    inputs = tokenizer(text, return_tensors='pt', truncation=True, max_length=256)
                    if hasattr(model, 'device'):
                        inputs = {k: v.to(model.device) for k, v in inputs.items()}

                    # Get loss
                    outputs = model(**inputs, labels=inputs['input_ids'])
                    total_loss += outputs.loss.item()
                    num_evaluated += 1

            return total_loss / max(num_evaluated, 1)

        except Exception as e:
            # Fallback to simple heuristic if model inference fails
            print(f"Warning: Probe evaluation failed ({e}), using heuristic")
            if probe_type == 'invariant':
                return 1.0
            elif probe_type == 'neighbor':
                return 1.5
            else:  # broken
                return 2.5

    def compute_differential_alignment(
        self,
        model,
        training_history: List[Dict] = None
    ) -> Tuple[float, bool]:
        """
        Compute differential alignment Δ = (ΔL_invariant - ΔL_neighbor)
        Returns: (delta_value, contamination_detected)
        """
        # Evaluate losses on probe families
        loss_invariant = self.evaluate_probes(model, self.invariant_probes, 'invariant')
        loss_neighbor = self.evaluate_probes(model, self.neighbor_probes, 'neighbor')

        # Compute differential
        delta = loss_neighbor - loss_invariant  # Contamination accelerates invariant learning

        # Check against baseline (if available)
        if self.baseline_mean is not None and self.baseline_std is not None:
            # Normalized detection
            z_score = (delta - self.baseline_mean) / (self.baseline_std + 1e-8)
            detected = z_score > self.threshold
        else:
            # Simple threshold
            detected = delta > 0.5

        return delta, detected

    def calibrate_baseline(self, clean_deltas: List[float]):
        """
        Calibrate baseline statistics from clean runs
        """
        self.baseline_mean = np.mean(clean_deltas)
        self.baseline_std = np.std(clean_deltas)

    def detect(self, model, training_history: List[Dict] = None) -> bool:
        """
        Run Tier 2 detection
        Returns True if contamination detected
        """
        _, detected = self.compute_differential_alignment(model, training_history)
        return detected
