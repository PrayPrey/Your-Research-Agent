from typing import Dict, List, Tuple
import torch
import numpy as np
from torch.utils.data import Dataset

class StratifiedSampler:
    def __init__(
        self,
        dataset: Dataset,
        batch_size: int = 32,
        quantiles: List[float] = [0.5, 0.75, 0.95, 0.99]
    ):
        self.dataset = dataset
        self.batch_size = batch_size
        self.quantiles = quantiles
        self.bins = self.compute_length_bins()
    
    def compute_length_bins(self) -> Dict[str, Tuple[int, int]]:
        lengths = [len(sample['input_ids']) for sample in self.dataset]
        quantile_values = np.quantile(lengths, self.quantiles)
        
        bins = {}
        bins['P50'] = (0, int(quantile_values[0]))
        bins['P75'] = (int(quantile_values[0]), int(quantile_values[1]))
        bins['P95'] = (int(quantile_values[1]), int(quantile_values[2]))
        bins['P99'] = (int(quantile_values[2]), max(lengths))
        
        return bins
    
    def sample_from_bin(self, bin_name: str) -> Dict[str, torch.Tensor]:
        min_len, max_len = self.bins[bin_name]
        
        indices = [i for i, sample in enumerate(self.dataset) 
                  if min_len <= len(sample['input_ids']) <= max_len]
        
        if len(indices) < self.batch_size:
            sampled_indices = np.random.choice(indices, size=self.batch_size, replace=True)
        else:
            sampled_indices = np.random.choice(indices, size=self.batch_size, replace=False)
        
        batch_samples = [self.dataset[int(i)] for i in sampled_indices]
        return variable_length_collate_fn(batch_samples)
    
    def get_stratified_batches(self) -> List[Dict[str, torch.Tensor]]:
        return [self.sample_from_bin(bin_name) for bin_name in ['P50', 'P75', 'P95', 'P99']]
    
    def sample_random_batch(self) -> Dict[str, torch.Tensor]:
        indices = np.random.choice(len(self.dataset), size=self.batch_size, replace=False)
        batch_samples = [self.dataset[int(i)] for i in indices]
        return variable_length_collate_fn(batch_samples)

def variable_length_collate_fn(batch: List[Dict]) -> Dict[str, torch.Tensor]:
    max_len = max(len(sample['input_ids']) for sample in batch)
    
    input_ids = []
    labels = []
    
    for sample in batch:
        pad_len = max_len - len(sample['input_ids'])
        input_ids.append(sample['input_ids'] + [0] * pad_len)
        labels.append(sample['labels'] + [-100] * pad_len)
    
    return {
        'input': torch.tensor(input_ids),
        'target': torch.tensor(labels)
    }
