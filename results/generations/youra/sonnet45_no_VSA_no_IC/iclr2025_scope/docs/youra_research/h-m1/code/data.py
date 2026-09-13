"""LongBench dataset loader for single-hop QA"""

from datasets import load_dataset
from typing import List, Dict
from transformers import AutoTokenizer

class LongBenchLoader:
    def __init__(self, tasks: List[str], tokenizer_name: str, max_context_length: int = 4096):
        self.tasks = tasks
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
        self.max_context_length = max_context_length

    def load(self) -> List[Dict]:
        """Load all tasks and return formatted samples"""
        all_samples = []
        for task in self.tasks:
            dataset = load_dataset('THUDM/LongBench', task, split='test')
            for sample in dataset:
                all_samples.append({
                    'input': sample['input'],
                    'context': sample['context'],
                    'answers': sample['answers'],
                    'task': task
                })
        return all_samples

    def preprocess_sample(self, sample: Dict) -> Dict:
        """Tokenize and truncate context"""
        context_tokens = self.tokenizer.encode(sample['context'], add_special_tokens=False)
        if len(context_tokens) > self.max_context_length:
            context_tokens = context_tokens[:self.max_context_length]
            sample['context'] = self.tokenizer.decode(context_tokens, skip_special_tokens=True)
        return sample
