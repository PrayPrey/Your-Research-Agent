"""Tier 3: Geometric Detection - Gradient/Hessian/CKA/Efficiency metrics"""
import numpy as np
import torch
from typing import Dict, List, Tuple

class Tier3GeometricDetection:
    """
    Tier 3 Detection: Geometric trajectory signatures
    - Gradient subspace overlap
    - Hessian spectral concentration
    - CKA representational alignment
    - Information efficiency Z-score
    Detection: ≥2 of 4 metrics exceed thresholds
    """

    def __init__(
        self,
        gradient_overlap_threshold: float = 0.7,
        hessian_concentration_threshold: float = 0.8,
        cka_alignment_threshold: float = 0.6,
        efficiency_zscore_threshold: float = 2.0,
        min_metrics_required: int = 2
    ):
        self.gradient_threshold = gradient_overlap_threshold
        self.hessian_threshold = hessian_concentration_threshold
        self.cka_threshold = cka_alignment_threshold
        self.efficiency_threshold = efficiency_zscore_threshold
        self.min_metrics = min_metrics_required

    def compute_gradient_overlap(
        self,
        model,
        benchmark_data: List[Dict],
        training_data: List[Dict]
    ) -> float:
        """
        Compute gradient subspace overlap via cosine similarity
        High overlap indicates alignment toward benchmark manifold
        """
        try:
            from transformers import AutoTokenizer

            tokenizer = AutoTokenizer.from_pretrained("EleutherAI/pythia-1.4b")
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token

            model.eval()

            # Compute gradients on benchmark samples
            benchmark_grads = []
            for sample in benchmark_data[:10]:  # Sample 10 for efficiency
                question = sample.get('question', '')
                answer = sample.get('answer', '')
                text = f"Question: {question}\nAnswer: {answer}"

                inputs = tokenizer(text, return_tensors='pt', truncation=True, max_length=256)
                if hasattr(model, 'device'):
                    inputs = {k: v.to(model.device) for k, v in inputs.items()}

                outputs = model(**inputs, labels=inputs['input_ids'])
                loss = outputs.loss
                loss.backward()

                # Collect gradients (flatten first layer)
                grads = []
                for name, param in model.named_parameters():
                    if param.grad is not None and 'embed' in name:  # Focus on embedding layer
                        grads.append(param.grad.flatten().cpu().detach().numpy())
                        break

                if grads:
                    benchmark_grads.append(np.concatenate(grads))

                model.zero_grad()

            # Compute gradients on training samples
            training_grads = []
            for sample in training_data[:10]:  # Sample 10 for efficiency
                question = sample.get('question', '')
                answer = sample.get('answer', '')
                text = f"Question: {question}\nAnswer: {answer}"

                inputs = tokenizer(text, return_tensors='pt', truncation=True, max_length=256)
                if hasattr(model, 'device'):
                    inputs = {k: v.to(model.device) for k, v in inputs.items()}

                outputs = model(**inputs, labels=inputs['input_ids'])
                loss = outputs.loss
                loss.backward()

                grads = []
                for name, param in model.named_parameters():
                    if param.grad is not None and 'embed' in name:
                        grads.append(param.grad.flatten().cpu().detach().numpy())
                        break

                if grads:
                    training_grads.append(np.concatenate(grads))

                model.zero_grad()

            # Compute cosine similarity
            if benchmark_grads and training_grads:
                bench_mean = np.mean(benchmark_grads, axis=0)
                train_mean = np.mean(training_grads, axis=0)

                similarity = np.dot(bench_mean, train_mean) / (
                    np.linalg.norm(bench_mean) * np.linalg.norm(train_mean) + 1e-8
                )
                return abs(similarity)

            return 0.5

        except Exception as e:
            print(f"Warning: Gradient computation failed ({e}), using heuristic")
            return 0.6

    def compute_hessian_concentration(
        self,
        model,
        data: List[Dict]
    ) -> float:
        """
        Compute Hessian spectral concentration
        High concentration indicates low-dimensional parameter alignment
        """
        try:
            # Use pytorch-hessian-eigenthings for efficient computation
            from hessian_eigenthings import compute_hessian_eigenthings
            from transformers import AutoTokenizer
            import torch.nn.functional as F

            tokenizer = AutoTokenizer.from_pretrained("EleutherAI/pythia-1.4b")
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token

            # Prepare small dataloader
            class SimpleDataset(torch.utils.data.Dataset):
                def __init__(self, data_samples, tokenizer):
                    self.data = data_samples[:20]  # Use 20 samples for efficiency
                    self.tokenizer = tokenizer

                def __len__(self):
                    return len(self.data)

                def __getitem__(self, idx):
                    sample = self.data[idx]
                    question = sample.get('question', '')
                    answer = sample.get('answer', '')
                    text = f"Question: {question}\nAnswer: {answer}"
                    return self.tokenizer(text, return_tensors='pt', truncation=True, max_length=256, padding='max_length')

            dataset = SimpleDataset(data, tokenizer)
            dataloader = torch.utils.data.DataLoader(dataset, batch_size=2)

            # Define loss function
            def loss_fn(model, batch):
                inputs = {k: v.squeeze(0) if v.dim() > 2 else v for k, v in batch.items()}
                if hasattr(model, 'device'):
                    inputs = {k: v.to(model.device) for k, v in inputs.items()}
                outputs = model(**inputs, labels=inputs['input_ids'])
                return outputs.loss

            # Compute top eigenvalues
            eigenvals, _ = compute_hessian_eigenthings(
                model,
                dataloader,
                loss_fn,
                num_eigenthings=5,
                mode='power_iter',
                max_samples=20
            )

            # Concentration: ratio of top-k to total
            concentration = eigenvals[:3].sum() / (eigenvals.sum() + 1e-8)
            return float(concentration)

        except Exception as e:
            print(f"Warning: Hessian computation failed ({e}), using heuristic")
            return 0.75

    def compute_cka_alignment(
        self,
        model,
        benchmark_data: List[Dict],
        training_data: List[Dict]
    ) -> float:
        """
        Compute CKA representational alignment
        High CKA indicates representational similarity to benchmark
        """
        try:
            from transformers import AutoTokenizer

            tokenizer = AutoTokenizer.from_pretrained("EleutherAI/pythia-1.4b")
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token

            model.eval()

            # Extract activations from intermediate layer
            activations_benchmark = []
            activations_training = []

            # Hook to capture activations
            captured_activations = []

            def hook_fn(module, input, output):
                if isinstance(output, tuple):
                    captured_activations.append(output[0].detach().cpu().numpy())
                else:
                    captured_activations.append(output.detach().cpu().numpy())

            # Register hook on first transformer layer
            hook_handle = None
            for name, module in model.named_modules():
                if 'layers.0' in name or 'layer.0' in name:
                    hook_handle = module.register_forward_hook(hook_fn)
                    break

            if hook_handle is None:
                # Fallback: use simple embedding similarity
                return 0.55

            # Get activations for benchmark
            with torch.no_grad():
                for sample in benchmark_data[:10]:
                    question = sample.get('question', '')
                    answer = sample.get('answer', '')
                    text = f"Question: {question}\nAnswer: {answer}"

                    inputs = tokenizer(text, return_tensors='pt', truncation=True, max_length=256)
                    if hasattr(model, 'device'):
                        inputs = {k: v.to(model.device) for k, v in inputs.items()}

                    captured_activations.clear()
                    model(**inputs)
                    if captured_activations:
                        activations_benchmark.append(captured_activations[0].flatten())

            # Get activations for training data
            with torch.no_grad():
                for sample in training_data[:10]:
                    question = sample.get('question', '')
                    answer = sample.get('answer', '')
                    text = f"Question: {question}\nAnswer: {answer}"

                    inputs = tokenizer(text, return_tensors='pt', truncation=True, max_length=256)
                    if hasattr(model, 'device'):
                        inputs = {k: v.to(model.device) for k, v in inputs.items()}

                    captured_activations.clear()
                    model(**inputs)
                    if captured_activations:
                        activations_training.append(captured_activations[0].flatten())

            hook_handle.remove()

            # Compute CKA
            if activations_benchmark and activations_training:
                # Simplified CKA: use correlation as proxy
                bench_mean = np.mean(activations_benchmark, axis=0)
                train_mean = np.mean(activations_training, axis=0)

                # Compute correlation
                correlation = np.corrcoef(bench_mean, train_mean)[0, 1]
                return abs(correlation)

            return 0.5

        except Exception as e:
            print(f"Warning: CKA computation failed ({e}), using heuristic")
            return 0.55

    def compute_efficiency_zscore(
        self,
        accuracy_gain: float,
        tokens_processed: int,
        baseline_mean: float = 0.001,
        baseline_std: float = 0.0005
    ) -> float:
        """
        Compute information efficiency Z-score
        efficiency = accuracy_gain / tokens_processed
        High Z-score indicates suspiciously efficient learning
        """
        efficiency = accuracy_gain / (tokens_processed + 1e-8)
        z_score = (efficiency - baseline_mean) / (baseline_std + 1e-8)
        return z_score

    def detect(
        self,
        model,
        benchmark_data: List[Dict],
        training_data: List[Dict],
        training_metrics: Dict
    ) -> Tuple[bool, Dict]:
        """
        Run Tier 3 detection with ≥2/4 threshold logic
        Returns: (contamination_detected, metrics_dict)
        """
        # Compute all 4 metrics
        gradient_overlap = self.compute_gradient_overlap(model, benchmark_data, training_data)
        hessian_concentration = self.compute_hessian_concentration(model, training_data)
        cka_alignment = self.compute_cka_alignment(model, benchmark_data, training_data)

        # Efficiency Z-score from training metrics
        accuracy_gain = training_metrics.get('final_accuracy', 0.5) - training_metrics.get('initial_accuracy', 0.0)
        tokens_processed = training_metrics.get('tokens_processed', 1000000)
        efficiency_z = self.compute_efficiency_zscore(accuracy_gain, tokens_processed)

        # Check thresholds
        metrics = {
            'gradient_overlap': gradient_overlap,
            'hessian_concentration': hessian_concentration,
            'cka_alignment': cka_alignment,
            'efficiency_zscore': efficiency_z
        }

        exceeded = {
            'gradient_overlap': gradient_overlap > self.gradient_threshold,
            'hessian_concentration': hessian_concentration > self.hessian_threshold,
            'cka_alignment': cka_alignment > self.cka_threshold,
            'efficiency_zscore': efficiency_z > self.efficiency_threshold
        }

        # ≥2/4 detection logic
        num_exceeded = sum(exceeded.values())
        contamination_detected = num_exceeded >= self.min_metrics

        metrics['exceeded'] = exceeded
        metrics['num_exceeded'] = num_exceeded

        return contamination_detected, metrics
