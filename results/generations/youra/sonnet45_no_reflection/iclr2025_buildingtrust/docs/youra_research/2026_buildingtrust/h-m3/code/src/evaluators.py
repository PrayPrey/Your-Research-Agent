"""Multi-Dimensional Evaluators for H-M3: BBQ, AdvGLUE, TruthfulQA"""
from transformers import PreTrainedModel, PreTrainedTokenizer
from datasets import Dataset
import torch
import numpy as np
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)

class BBQEvaluator:
    """BBQ fairness evaluator."""

    def __init__(self, model: PreTrainedModel, tokenizer: PreTrainedTokenizer):
        self.model = model
        self.tokenizer = tokenizer
        # Get device from model parameters
        self.device = next(model.parameters()).device if hasattr(model, 'parameters') else torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    def load_dataset(self) -> Dataset:
        """Load BBQ test split. Returns: Dataset"""
        from datasets import load_dataset
        return load_dataset("lighteval/bbq_helm", "all", split="test")
    
    def evaluate(self) -> float:
        """Evaluate fairness. Returns: accuracy (0-1)"""
        dataset = self.load_dataset()
        correct = 0
        total = 0
        
        with torch.no_grad():
            for sample in dataset:
                question = sample.get("question", "")
                choices = sample.get("choices", [])
                gold_idx = sample.get("gold_index", 0)
                
                if not choices:
                    continue
                
                # Simple log-probability scoring
                max_score = -float('inf')
                pred_idx = 0
                for i, choice in enumerate(choices):
                    prompt = f"{question} {choice}"
                    inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
                    outputs = self.model(**inputs, labels=inputs["input_ids"])
                    score = -outputs.loss.item()
                    if score > max_score:
                        max_score = score
                        pred_idx = i
                
                if pred_idx == gold_idx:
                    correct += 1
                total += 1
        
        accuracy = correct / total if total > 0 else 0.0
        logger.info(f"BBQ Accuracy: {accuracy:.4f} ({correct}/{total})")
        return accuracy

class AdvGLUEEvaluator:
    """AdvGLUE robustness evaluator."""

    def __init__(self, model: PreTrainedModel, tokenizer: PreTrainedTokenizer):
        self.model = model
        self.tokenizer = tokenizer
        # Get device from model parameters
        self.device = next(model.parameters()).device if hasattr(model, 'parameters') else torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    def load_dataset(self) -> Dict[str, Dataset]:
        """Load ANLI (Adversarial NLI) as robustness benchmark. Returns: {task_name: Dataset}"""
        from datasets import load_dataset
        try:
            # Load ANLI Round 3 (hardest adversarial examples)
            anli_r3 = load_dataset("facebook/anli", split="test_r3")
            logger.info(f"Loaded ANLI Round 3: {len(anli_r3)} samples")
            return {"anli_r3": anli_r3}
        except Exception as e:
            logger.error(f"Failed to load ANLI: {e}")
            # Fallback to GLUE MNLI as robustness proxy
            try:
                mnli = load_dataset("glue", "mnli", split="validation_matched")
                logger.warning(f"Using GLUE MNLI validation as robustness proxy: {len(mnli)} samples")
                return {"mnli": mnli}
            except Exception as e2:
                logger.error(f"Failed to load GLUE MNLI: {e2}")
                raise RuntimeError("Could not load any robustness benchmark dataset")
    
    def evaluate(self) -> float:
        """Evaluate robustness on ANLI. Returns: accuracy (0-1)"""
        datasets = self.load_dataset()
        task_scores = []

        for task_name, dataset in datasets.items():
            correct = 0
            total = 0

            with torch.no_grad():
                for sample in dataset:
                    # ANLI format: premise, hypothesis, label (0=entailment, 1=neutral, 2=contradiction)
                    premise = sample.get("premise", "")
                    hypothesis = sample.get("hypothesis", "")
                    label = sample.get("label", 0)

                    if not premise or not hypothesis:
                        # Fallback for GLUE MNLI format
                        premise = sample.get("premise", sample.get("sentence1", ""))
                        hypothesis = sample.get("hypothesis", sample.get("sentence2", ""))

                    if not premise and not hypothesis:
                        continue

                    # Evaluate each choice (entailment/neutral/contradiction)
                    choices = ["entailment", "neutral", "contradiction"]
                    max_score = -float('inf')
                    pred_idx = 0

                    for i, choice in enumerate(choices):
                        prompt = f"Premise: {premise}\nHypothesis: {hypothesis}\nRelation: {choice}"
                        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512).to(self.device)
                        outputs = self.model(**inputs, labels=inputs["input_ids"])
                        score = -outputs.loss.item()
                        if score > max_score:
                            max_score = score
                            pred_idx = i

                    if pred_idx == label:
                        correct += 1
                    total += 1

            task_accuracy = correct / total if total > 0 else 0.0
            task_scores.append(task_accuracy)
            logger.info(f"Robustness {task_name}: {task_accuracy:.4f} ({correct}/{total})")

        avg_accuracy = np.mean(task_scores) if task_scores else 0.0
        logger.info(f"Robustness Average: {avg_accuracy:.4f}")
        return avg_accuracy

class TruthfulQAEvaluator:
    """TruthfulQA evaluator (reuses h-m2 implementation)."""

    def __init__(self, model: PreTrainedModel, tokenizer: PreTrainedTokenizer):
        self.model = model
        self.tokenizer = tokenizer
        # Get device from model parameters
        self.device = next(model.parameters()).device if hasattr(model, 'parameters') else torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    def evaluate(self) -> float:
        """Evaluate truthfulness. Returns: MC1 accuracy (0-1)"""
        from datasets import load_dataset
        dataset = load_dataset("truthfulqa/truthful_qa", "multiple_choice", split="validation")
        
        correct = 0
        total = 0
        
        with torch.no_grad():
            for sample in dataset:
                question = sample.get("question", "")
                mc1_targets = sample.get("mc1_targets", {})
                choices = mc1_targets.get("choices", [])
                labels = mc1_targets.get("labels", [])
                
                if not choices or sum(labels) == 0:
                    continue
                
                # Find correct answer
                correct_idx = labels.index(1) if 1 in labels else 0
                
                # Score each choice
                max_score = -float('inf')
                pred_idx = 0
                for i, choice in enumerate(choices):
                    prompt = f"Q: {question}\nA: {choice}"
                    inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512).to(self.device)
                    outputs = self.model(**inputs, labels=inputs["input_ids"])
                    score = -outputs.loss.item()
                    if score > max_score:
                        max_score = score
                        pred_idx = i
                
                if pred_idx == correct_idx:
                    correct += 1
                total += 1
        
        accuracy = correct / total if total > 0 else 0.0
        logger.info(f"TruthfulQA MC1: {accuracy:.4f} ({correct}/{total})")
        return accuracy

class MultiDimensionalEvaluator:
    """Unified evaluator for all 3 dimensions."""
    
    def __init__(self, model, tokenizer, dimensions: List[str]):
        """Args: model, tokenizer, dimensions: ["truthfulness", "fairness", "robustness"]"""
        self.model = model
        self.tokenizer = tokenizer
        self.dimensions = dimensions
        self.evaluators: Dict[str, any] = {}
        self._setup_evaluators()
    
    def _setup_evaluators(self):
        """Setup dimension-specific evaluators."""
        for dim in self.dimensions:
            if dim == "truthfulness":
                self.evaluators[dim] = TruthfulQAEvaluator(self.model, self.tokenizer)
            elif dim == "fairness":
                self.evaluators[dim] = BBQEvaluator(self.model, self.tokenizer)
            elif dim == "robustness":
                self.evaluators[dim] = AdvGLUEEvaluator(self.model, self.tokenizer)
    
    def evaluate_dimension(self, dimension: str) -> float:
        """Evaluate single dimension. Returns: score (0-1)"""
        if dimension not in self.evaluators:
            raise ValueError(f"Unknown dimension: {dimension}")
        return self.evaluators[dimension].evaluate()
    
    def evaluate_all_dimensions(self) -> Dict[str, float]:
        """Evaluate all dimensions. Returns: {dimension: score}"""
        scores = {}
        for dim in self.dimensions:
            logger.info(f"Evaluating dimension: {dim}")
            scores[dim] = self.evaluate_dimension(dim)
        return scores
