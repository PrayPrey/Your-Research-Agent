"""Semantic entropy computation using DeBERTa entailment."""

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import numpy as np
from typing import List, Dict
import logging
from tqdm import tqdm
import json
import os

logger = logging.getLogger(__name__)


class DeBERTaEntailment:
    """DeBERTa-based entailment model for semantic clustering."""
    
    def __init__(
        self,
        model_name: str = "microsoft/deberta-v2-xlarge-mnli",
        device: str = "cuda",
        dtype: str = "float16"
    ):
        self.model_name = model_name
        self.device = device
        self.dtype = getattr(torch, dtype)
        self.model = None
        self.tokenizer = None
    
    def load_model(self):
        """Load DeBERTa entailment model."""
        logger.info(f"Loading {self.model_name}")
        
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            self.model_name,
            torch_dtype=self.dtype
        ).to(self.device)
        self.model.eval()
        
        logger.info("DeBERTa model loaded successfully")
    
    def bidirectional_entailment(self, text1: str, text2: str) -> float:
        """Compute bidirectional entailment score."""
        if self.model is None:
            self.load_model()
        
        # text1 -> text2
        inputs_12 = self.tokenizer(
            text1, text2,
            return_tensors="pt",
            truncation=True,
            max_length=512
        ).to(self.device)
        
        with torch.no_grad():
            logits_12 = self.model(**inputs_12).logits
            # Index 2 = entailment in MNLI
            entail_12 = torch.softmax(logits_12, dim=-1)[0, 2].item()
        
        # text2 -> text1
        inputs_21 = self.tokenizer(
            text2, text1,
            return_tensors="pt",
            truncation=True,
            max_length=512
        ).to(self.device)
        
        with torch.no_grad():
            logits_21 = self.model(**inputs_21).logits
            entail_21 = torch.softmax(logits_21, dim=-1)[0, 2].item()
        
        # Semantic equivalence = bidirectional entailment
        return min(entail_12, entail_21)


class GreedyAgglomerativeClustering:
    """Greedy clustering based on entailment matrix."""
    
    def __init__(self, threshold: float = 0.5):
        self.threshold = threshold
    
    def cluster(self, entailment_matrix: np.ndarray) -> List[List[int]]:
        """Cluster answers based on semantic equivalence."""
        n = entailment_matrix.shape[0]
        clusters = []
        assigned = [False] * n
        
        for i in range(n):
            if not assigned[i]:
                cluster = [i]
                assigned[i] = True
                
                for j in range(i + 1, n):
                    if not assigned[j] and entailment_matrix[i, j] > self.threshold:
                        cluster.append(j)
                        assigned[j] = True
                
                clusters.append(cluster)
        
        return clusters


class SemanticEntropyComputer:
    """Compute semantic entropy from multiple answers."""
    
    def __init__(
        self,
        entailment_model: DeBERTaEntailment,
        clustering_threshold: float = 0.5
    ):
        self.entailment = entailment_model
        self.clustering = GreedyAgglomerativeClustering(threshold=clustering_threshold)
        self.cache_dir = "cache/semantic_entropy"
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def compute_entropy(self, answers: List[str]) -> float:
        """Compute semantic entropy for a list of answers."""
        n = len(answers)
        
        if n == 0:
            return 0.0
        if n == 1:
            return 0.0
        
        # Compute pairwise entailment matrix
        entailment_matrix = np.zeros((n, n))
        
        for i in range(n):
            for j in range(i + 1, n):
                score = self.entailment.bidirectional_entailment(answers[i], answers[j])
                entailment_matrix[i, j] = score
                entailment_matrix[j, i] = score
        
        # Cluster semantically equivalent answers
        clusters = self.clustering.cluster(entailment_matrix)
        
        # Compute entropy over cluster distribution
        cluster_probs = np.array([len(c) / n for c in clusters])
        entropy = -np.sum(cluster_probs * np.log(cluster_probs + 1e-10))
        
        return float(entropy)
    
    def batch_compute(
        self,
        generations: Dict[int, List],
        samples: List[Dict],
        checkpoint_interval: int = 100
    ) -> Dict[int, float]:
        """Compute semantic entropy for all questions."""
        logger.info(f"Computing semantic entropy for {len(samples)} questions")
        
        if self.entailment.model is None:
            self.entailment.load_model()
        
        scores = {}
        
        for idx, sample in enumerate(tqdm(samples, desc="Computing semantic entropy")):
            example_id = sample['example_id']
            
            # Check cache
            cache_path = os.path.join(self.cache_dir, f"se_{example_id}.json")
            if os.path.exists(cache_path):
                with open(cache_path, 'r') as f:
                    scores[example_id] = json.load(f)['entropy']
                continue
            
            if example_id not in generations:
                continue
            
            # Extract answer texts
            answers = generations[example_id]
            answer_texts = [ans.text for ans in answers if ans.text.strip()]
            
            # Compute semantic entropy
            entropy = self.compute_entropy(answer_texts)
            scores[example_id] = entropy
            
            # Cache result
            with open(cache_path, 'w') as f:
                json.dump({'entropy': entropy}, f)
            
            if (idx + 1) % checkpoint_interval == 0:
                logger.info(f"Checkpoint: {idx + 1}/{len(samples)} completed")
        
        logger.info(f"Computed semantic entropy for {len(scores)} questions")
        return scores
