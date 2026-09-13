"""TriviaQA data loading and splitting module."""

from datasets import load_dataset
from sklearn.model_selection import train_test_split
import json
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class TriviaQALoader:
    """Load and split TriviaQA dataset for semantic entropy validation."""
    
    def __init__(self, subset_size: int = 3000, random_state: int = 42):
        self.subset_size = subset_size
        self.random_state = random_state
        self.filter = DataFilter()
    
    def load_and_split(self) -> Tuple[List[Dict], List[Dict]]:
        """Load TriviaQA and create 50/50 dev/test split."""
        logger.info(f"Loading TriviaQA data (target: {self.subset_size} examples)")
        
        # Use the dzur658/grounded-vs-fabricated-hallucinations dataset
        try:
            logger.info("Loading from dzur658/grounded-vs-fabricated-hallucinations")
            dataset = load_dataset(
                "dzur658/grounded-vs-fabricated-hallucinations",
                split="train"
            )
            logger.info(f"Loaded {len(dataset)} examples")
            
            # Take first subset_size
            if len(dataset) > self.subset_size:
                dataset = dataset.select(range(self.subset_size))
            
        except Exception as e:
            logger.error(f"Failed to load dataset: {e}")
            raise
        
        # Extract questions and answers
        samples = []
        for idx, example in enumerate(dataset):
            sample = {
                'question': example.get('question', ''),
                'ground_truth': example.get('answer', ''),
                'example_id': idx
            }
            samples.append(sample)
        
        # Apply quality filters
        filtered_samples = self.filter.apply_filters(samples)
        logger.info(f"Filtered {len(samples)} -> {len(filtered_samples)} examples")
        
        # 50/50 split
        dev_samples, test_samples = train_test_split(
            filtered_samples,
            test_size=0.5,
            random_state=self.random_state
        )
        
        logger.info(f"Split: {len(dev_samples)} dev, {len(test_samples)} test")
        return dev_samples, test_samples
    
    def save_split_metadata(self, dev_samples: List[Dict], test_samples: List[Dict], path: str):
        """Save split indices for reproducibility."""
        metadata = {
            'dev_ids': [s['example_id'] for s in dev_samples],
            'test_ids': [s['example_id'] for s in test_samples],
            'subset_size': self.subset_size,
            'random_state': self.random_state
        }
        with open(path, 'w') as f:
            json.dump(metadata, f, indent=2)
        logger.info(f"Saved split metadata to {path}")


class DataFilter:
    """Quality filters for TriviaQA samples."""
    
    def __init__(self, min_answer_tokens: int = 3):
        self.min_answer_tokens = min_answer_tokens
    
    def apply_filters(self, samples: List[Dict]) -> List[Dict]:
        """Apply all quality filters."""
        filtered = []
        for sample in samples:
            if (sample['question'].strip() and 
                sample['ground_truth'] and
                self._filter_short_answers(sample)):
                filtered.append(sample)
        return filtered
    
    def _filter_short_answers(self, sample: Dict) -> bool:
        """Filter answers with < min_answer_tokens."""
        answer = sample['ground_truth']
        if isinstance(answer, list):
            answer = answer[0] if answer else ""
        return len(str(answer).split()) >= self.min_answer_tokens
