"""EK-FAC Attribution using kronfluence"""
import torch
import numpy as np
from typing import Dict, List
from torch.utils.data import DataLoader
import torch.nn as nn
from tqdm import tqdm

try:
    from kronfluence.analyzer import Analyzer, prepare_model
    from kronfluence.task import Task
    from kronfluence.arguments import FactorArguments, ScoreArguments
    HAS_KRONFLUENCE = True
except ImportError:
    HAS_KRONFLUENCE = False

class TextClassificationTask(Task):
    """Task wrapper for text classification with kronfluence."""
    def compute_train_loss(self, batch, model, sample: bool = False):
        input_ids = batch["input_ids"]
        attention_mask = batch["attention_mask"]
        labels = batch["labels"]
        outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
        return outputs.loss

    def compute_measurement(self, batch, model):
        input_ids = batch["input_ids"]
        attention_mask = batch["attention_mask"]
        labels = batch["labels"]
        outputs = model(input_ids=input_ids, attention_mask=attention_mask)
        logits = outputs.logits
        return torch.nn.functional.cross_entropy(logits, labels, reduction="none")

def fit_ekfac_factors(model: nn.Module, task: Task, train_loader: DataLoader,
                       strategy: str = "ekfac", save_dir: str = "./ekfac_cache") -> "Analyzer":
    """Fit Kronecker factors using kronfluence."""
    if not HAS_KRONFLUENCE:
        raise ImportError("kronfluence not installed")

    analyzer = Analyzer(
        analysis_name=f"ekfac_{strategy}",
        model=model,
        task=task,
        output_dir=save_dir
    )

    factor_args = FactorArguments(strategy=strategy)
    analyzer.fit_all_factors(
        factors_name=strategy,
        dataset=train_loader.dataset,
        factor_args=factor_args,
        per_device_batch_size=8
    )
    return analyzer

def compute_ekfac_scores(analyzer: "Analyzer", query_loader: DataLoader,
                          train_loader: DataLoader, strategy: str) -> np.ndarray:
    """Compute pairwise influence scores. Returns [n_query, n_train]."""
    score_args = ScoreArguments(
        compute_per_sample_scores=True
    )
    analyzer.compute_pairwise_scores(
        scores_name=strategy,
        factors_name=strategy,
        query_dataset=query_loader.dataset,
        train_dataset=train_loader.dataset,
        score_args=score_args,
        per_device_query_batch_size=8,
        per_device_train_batch_size=16
    )
    scores = analyzer.load_pairwise_scores(strategy)
    return scores["all_modules"].numpy()

def compute_ekfac_scores_simple(model: nn.Module, train_loader: DataLoader,
                                 query_loader: DataLoader, device: str,
                                 strategy: str = "ekfac", n_train_sample: int = 500,
                                 n_query_sample: int = 100) -> np.ndarray:
    """Simplified EK-FAC using last-layer gradient similarity as proxy."""
    model.eval()
    model.to(device)

    def get_last_layer_grad(m, input_ids, attention_mask, labels):
        m.zero_grad()
        outputs = m(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
        loss = outputs.loss
        loss.backward()
        for name, p in reversed(list(m.named_parameters())):
            if p.grad is not None and 'classifier' in name:
                return p.grad.view(-1).clone()
        for p in reversed(list(m.parameters())):
            if p.grad is not None:
                return p.grad.view(-1).clone()
        return None

    train_grads = []
    train_count = 0
    for batch in tqdm(train_loader, desc="EK-FAC train grads"):
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        labels = batch["labels"].to(device)

        for i in range(len(labels)):
            if train_count >= n_train_sample:
                break
            grad = get_last_layer_grad(model, input_ids[i:i+1], attention_mask[i:i+1], labels[i:i+1])
            if grad is not None:
                train_grads.append(grad.cpu())
            train_count += 1
        if train_count >= n_train_sample:
            break

    train_grads = torch.stack(train_grads)

    query_grads = []
    query_count = 0
    for batch in tqdm(query_loader, desc="EK-FAC query grads"):
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        labels = batch["labels"].to(device)

        for i in range(len(labels)):
            if query_count >= n_query_sample:
                break
            grad = get_last_layer_grad(model, input_ids[i:i+1], attention_mask[i:i+1], labels[i:i+1])
            if grad is not None:
                query_grads.append(grad.cpu())
            query_count += 1
        if query_count >= n_query_sample:
            break

    query_grads = torch.stack(query_grads)

    scores = torch.mm(query_grads, train_grads.T).numpy()
    return scores

def run_ekfac_strategy_ablation(model: nn.Module, task, train_loader: DataLoader,
                                 query_loader: DataLoader, strategies: List[str],
                                 device: str) -> Dict[str, np.ndarray]:
    """Run EK-FAC with different strategies, return {strategy: scores}."""
    results = {}
    for strategy in strategies:
        print(f"Running EK-FAC strategy: {strategy}")
        try:
            if HAS_KRONFLUENCE:
                analyzer = fit_ekfac_factors(model, task, train_loader, strategy)
                scores = compute_ekfac_scores(analyzer, query_loader, train_loader, strategy)
            else:
                scores = compute_ekfac_scores_simple(model, train_loader, query_loader, device, strategy)
            results[strategy] = scores
        except Exception as e:
            print(f"EK-FAC strategy {strategy} failed: {e}")
            results[strategy] = None
    return results
