from typing import Optional, Dict, List
import torch
from torch.utils.data import DataLoader
import torch.nn as nn

class SegmentMemoryProfiler:
    def __init__(self, device: str = "cuda:0"):
        self.device = torch.device(device)
    
    def reset_memory_stats(self) -> None:
        torch.cuda.reset_peak_memory_stats(self.device)
        torch.cuda.empty_cache()
    
    def get_peak_memory_mb(self) -> float:
        stats = torch.cuda.memory_stats(self.device)
        peak_bytes = stats.get("allocated_bytes.all.peak", 0)
        return peak_bytes / (1024 ** 2)
    
    def profile_iteration(
        self,
        model: nn.Module,
        batch: Dict[str, torch.Tensor],
        optimizer: Optional[torch.optim.Optimizer] = None,
        backward: bool = False
    ) -> float:
        self.reset_memory_stats()
        
        inputs = batch['input'].to(self.device)
        targets = batch['target'].to(self.device)
        
        outputs = model(inputs)
        
        if hasattr(outputs, 'logits'):
            outputs = outputs.logits
        
        criterion = nn.CrossEntropyLoss()
        loss = criterion(outputs, targets)
        
        if backward:
            if optimizer is None:
                raise ValueError("Optimizer required when backward=True")
            loss.backward()
            optimizer.step()
            optimizer.zero_grad()
        
        return self.get_peak_memory_mb()
    
    def profile_ground_truth(
        self,
        model: nn.Module,
        dataloader: DataLoader,
        optimizer: torch.optim.Optimizer,
        num_iters: int = 10
    ) -> float:
        model.to(self.device)
        model.train()
        
        iter_loader = iter(dataloader)
        for i in range(num_iters):
            try:
                batch = next(iter_loader)
            except StopIteration:
                iter_loader = iter(dataloader)
                batch = next(iter_loader)
            
            self.profile_iteration(model, batch, optimizer, backward=True)
        
        return self.get_peak_memory_mb()
    
    def profile_lightweight(
        self,
        model: nn.Module,
        dataloader_or_sampler,
        optimizer: torch.optim.Optimizer
    ) -> Dict[str, float]:
        model.to(self.device)
        model.train()
        
        # Check if this is a StratifiedSampler or regular DataLoader
        is_stratified = hasattr(dataloader_or_sampler, 'sample_random_batch')
        
        # Iteration 1: Forward only
        if is_stratified:
            batch1 = dataloader_or_sampler.sample_random_batch()
        else:
            iter_loader = iter(dataloader_or_sampler)
            batch1 = next(iter_loader)
        iter1_mb = self.profile_iteration(model, batch1, backward=False)
        
        # Post-optimizer: Full training step
        if is_stratified:
            batch2 = dataloader_or_sampler.sample_random_batch()
        else:
            batch2 = next(iter_loader)
        post_optim_mb = self.profile_iteration(model, batch2, optimizer, backward=True)
        
        # Stratified sampling (only for StratifiedSampler)
        stratified_mbs = []
        if is_stratified:
            for bin_name in ['P50', 'P75', 'P95', 'P99']:
                batch = dataloader_or_sampler.sample_from_bin(bin_name)
                mem = self.profile_iteration(model, batch, optimizer, backward=True)
                stratified_mbs.append(mem)
        
        predicted_mb = max([iter1_mb, post_optim_mb] + stratified_mbs)
        return {
            'iter1_mb': iter1_mb,
            'post_optim_mb': post_optim_mb,
            'stratified_mbs': stratified_mbs,
            'predicted_mb': predicted_mb
        }
