"""Multi-Dimensional Dataset Loader for H-M3"""
from datasets import load_dataset, Dataset
from transformers import PreTrainedTokenizer
import torch
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class MultiDimensionalDataset:
    """Load and prepare TruthfulQA, BBQ, AdvGLUE datasets."""
    
    def __init__(self, tokenizer: PreTrainedTokenizer, dimensions: List[str]):
        """Args: tokenizer, dimensions: ["truthfulness", "fairness", "robustness"]"""
        self.tokenizer = tokenizer
        # Set pad token if not set
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        self.dimensions = dimensions
        self.datasets: Dict[str, Dataset] = {}
    
    def load_truthfulqa(self, split: str = "validation") -> Dataset:
        """Load TruthfulQA. Returns: Dataset with 817 questions"""
        ds = load_dataset("truthfulqa/truthful_qa", "generation", split=split)
        self.datasets["truthfulness"] = ds
        logger.info(f"Loaded TruthfulQA: {len(ds)} samples")
        return ds
    
    def load_bbq(self, split: str = "test") -> Dataset:
        """Load BBQ bias benchmark. Returns: Dataset with 500+ samples"""
        ds = load_dataset("lighteval/bbq_helm", "all", split=split)
        self.datasets["fairness"] = ds
        logger.info(f"Loaded BBQ: {len(ds)} samples")
        return ds
    
    def load_advglue(self) -> Dataset:
        """Load AdvGLUE robustness benchmark from GLUE adversarial datasets. Returns: Dataset"""
        # Use adversarial NLI or ANLI as proxy for robustness evaluation
        # ANLI (Adversarial NLI) is a well-established adversarial robustness benchmark
        try:
            ds = load_dataset("facebook/anli", split="test_r3")  # Round 3 (hardest)
            self.datasets["robustness"] = ds
            logger.info(f"Loaded ANLI (robustness proxy): {len(ds)} samples")
            return ds
        except Exception as e:
            logger.error(f"Failed to load ANLI: {e}")
            # Fallback to adversarial GLUE subset if available
            try:
                ds = load_dataset("glue", "mnli", split="validation_matched")
                # Use validation set as robustness proxy
                self.datasets["robustness"] = ds
                logger.warning(f"Using GLUE MNLI validation as robustness proxy: {len(ds)} samples")
                return ds
            except Exception as e2:
                logger.error(f"Failed to load GLUE: {e2}")
                raise RuntimeError("Could not load any robustness benchmark dataset")
    
    def get_training_samples(self, n_samples: int = 500) -> Dataset:
        """Get training subset from TruthfulQA. Returns: Dataset [n_samples]"""
        if "truthfulness" not in self.datasets:
            self.load_truthfulqa()
        ds = self.datasets["truthfulness"]
        return ds.select(range(min(n_samples, len(ds))))
    
    def get_eval_samples_per_dimension(self, dimension: str) -> Dataset:
        """Get evaluation samples for dimension. Returns: Dataset"""
        if dimension == "truthfulness":
            if "truthfulness" not in self.datasets:
                self.load_truthfulqa()
            return self.datasets["truthfulness"]
        elif dimension == "fairness":
            if "fairness" not in self.datasets:
                self.load_bbq()
            return self.datasets["fairness"]
        elif dimension == "robustness":
            if "robustness" not in self.datasets:
                self.load_advglue()
            return self.datasets["robustness"]
        else:
            raise ValueError(f"Unknown dimension: {dimension}")
    
    def prepare_tokens(self, dataset: Dataset, text_field: str = None) -> torch.Tensor:
        """Tokenize dataset for activation extraction. Returns: [N, L]"""
        if text_field is None:
            # Auto-detect text field
            if "question" in dataset.column_names:
                text_field = "question"
            elif "text" in dataset.column_names:
                text_field = "text"
            elif "context" in dataset.column_names:
                text_field = "context"
            else:
                raise ValueError(f"Cannot auto-detect text field from {dataset.column_names}")
        
        texts = [str(sample[text_field]) for sample in dataset]
        encoded = self.tokenizer(
            texts,
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors="pt"
        )
        return encoded["input_ids"]
