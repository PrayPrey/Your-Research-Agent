import os
import csv
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

import numpy as np
import torch
import torch.nn as nn

from config import BudgetSweepConfig, LONGBENCH_TASKS
from dataset import run_task_evaluation, compute_category_accuracies
from model import set_h2o_budget, set_h2o_training_mode, verify_budget_applied, H2OEvictionAwareAttention, load_model_for_sweep

logger = logging.getLogger(__name__)


@dataclass
class RunResult:
    model_name: str
    adapter_type: str           # "sequential" | "eviction-aware"
    budget_ratio: float
    per_task_scores: Dict[str, float]
    category_scores: Dict[str, float]  # 6-category means

    def to_dict(self) -> dict:
        d = {
            "model_name": self.model_name,
            "adapter_type": self.adapter_type,
            "budget_ratio": self.budget_ratio,
        }
        d.update({f"task_{k}": v for k, v in self.per_task_scores.items()})
        d.update({f"cat_{k}": v for k, v in self.category_scores.items()})
        return d


def verify_mechanism_activated(
    model: nn.Module,
    budget_ratio: float,
    results_by_r: Dict[float, float],
) -> Tuple[bool, dict]:
    """Check budget correctly set + gap variance non-zero.
    Returns: (all_pass: bool, indicators: dict)
    Raises RuntimeError if budget_set is False (fail-fast).
    """
    indicators = {}

    budget_ok = verify_budget_applied(model, budget_ratio)
    indicators["budget_set_correctly"] = budget_ok

    if not budget_ok:
        # Check if any H2O wrappers exist at all
        from model import H2OEvictionAwareAttention
        h2o_count = sum(1 for m in model.modules() if isinstance(m, H2OEvictionAwareAttention))
        if h2o_count == 0:
            # GPT-2 proxy — no H2O wrappers injectable, log warning and continue
            logger.warning("No H2O wrappers in model (GPT-2 proxy) — budget_set check skipped")
            indicators["budget_set_correctly"] = "skipped_gpt2_proxy"
        else:
            raise RuntimeError(
                f"Budget set check FAILED: H2O wrappers do not have kv_budget_ratio={budget_ratio}. "
                "H2O injection may not be working."
            )

    variance = float(np.var(list(results_by_r.values()))) if results_by_r else 0.0
    indicators["gap_variance"] = variance
    indicators["gap_variance_nonzero"] = variance > 1e-8
    indicators["n_ratios_evaluated"] = len(results_by_r)
    indicators["all_ratios_evaluated"] = set(results_by_r.keys()) == {0.25, 0.50, 0.75}

    all_pass = budget_ok and variance > 1e-8 and len(results_by_r) == 3
    indicators["all_pass"] = all_pass
    return all_pass, indicators


class BudgetSweepEvaluator:
    def __init__(self, cfg: BudgetSweepConfig):
        self.cfg = cfg

    def evaluate_single_run(
        self,
        model: nn.Module,
        tokenizer,
        adapter_type: str,
        budget_ratio: float,
        model_name: str,
        device: str,
    ) -> RunResult:
        """Set budget, activate eviction (H2O train mode), run all 21 tasks, return RunResult."""
        # Set budget ratio on H2O wrappers (eviction-aware only)
        if adapter_type == "eviction-aware":
            try:
                set_h2o_budget(model, budget_ratio)
                if not verify_budget_applied(model, budget_ratio):
                    logger.warning(f"Budget {budget_ratio} not applied correctly to all wrappers")
            except ValueError:
                # GPT-2 proxy: inject_h2o_wrappers only supports LLaMA/Mistral
                logger.warning(f"No H2O wrappers found (GPT-2 proxy) — budget ratio {budget_ratio} not set via attribute")

        # Activate eviction for inference (H2O requires train mode)
        set_h2o_training_mode(model, True)

        per_task_scores = {}
        for task in self.cfg.longbench_tasks:
            score = run_task_evaluation(
                model, tokenizer, task,
                max_seq_length=self.cfg.max_seq_length,
                device=device,
            )
            per_task_scores[task] = score
            logger.info(f"  Task {task}: {score:.4f}")

        # Restore eval mode
        set_h2o_training_mode(model, False)

        category_scores = compute_category_accuracies(per_task_scores)

        logger.info(f"Run complete: model={model_name}, adapter={adapter_type}, r={budget_ratio}")
        for cat, sc in category_scores.items():
            logger.info(f"  {cat}: {sc:.4f}")

        return RunResult(
            model_name=model_name,
            adapter_type=adapter_type,
            budget_ratio=budget_ratio,
            per_task_scores=per_task_scores,
            category_scores=category_scores,
        )

    def run_all(self, device: str = "cuda") -> List[RunResult]:
        """12-run sweep: 2 adapter_types × 3 budget_ratios × 2 models (or 2 adapters × 3 for GPT-2 proxy).
        Loads/unloads models between adapter groups to manage GPU memory.
        Returns List[RunResult].
        """
        results = []
        results_by_r_per_adapter: Dict[str, Dict[float, float]] = {}

        from config import LONGBENCH_CATEGORIES

        for adapter_spec in self.cfg.adapters:
            logger.info(f"Loading model: {adapter_spec.model_name} [{adapter_spec.adapter_type}]")
            model = None
            try:
                model, tokenizer = load_model_for_sweep(
                    model_name=adapter_spec.model_name,
                    adapter_path=adapter_spec.adapter_path,
                    adapter_type=adapter_spec.adapter_type,
                    initial_budget=self.cfg.budget_ratios[0],
                )
                model = model.to(device)

                adapter_key = f"{adapter_spec.model_name}_{adapter_spec.adapter_type}"
                results_by_r_per_adapter[adapter_key] = {}

                for r in self.cfg.budget_ratios:
                    logger.info(f"  Budget ratio: {r}")
                    try:
                        result = self.evaluate_single_run(
                            model, tokenizer,
                            adapter_spec.adapter_type, r,
                            adapter_spec.model_name, device,
                        )
                    except Exception as run_err:
                        logger.warning(
                            f"  Run failed (model={adapter_spec.model_name}, "
                            f"adapter={adapter_spec.adapter_type}, r={r}): {run_err}. "
                            "Recording NaN scores and continuing."
                        )
                        nan_tasks = {t: float("nan") for t in self.cfg.longbench_tasks}
                        nan_cats = {c: float("nan") for c in LONGBENCH_CATEGORIES}
                        result = RunResult(
                            model_name=adapter_spec.model_name,
                            adapter_type=adapter_spec.adapter_type,
                            budget_ratio=r,
                            per_task_scores=nan_tasks,
                            category_scores=nan_cats,
                        )
                    results.append(result)
                    mean_cat = float(np.nanmean(list(result.category_scores.values())))
                    results_by_r_per_adapter[adapter_key][r] = mean_cat

                # Mechanism verification after all budgets for this adapter
                if adapter_spec.adapter_type == "eviction-aware":
                    try:
                        all_pass, indicators = verify_mechanism_activated(
                            model, self.cfg.budget_ratios[-1],
                            results_by_r_per_adapter[adapter_key],
                        )
                        logger.info(f"Mechanism verification: {all_pass}, indicators={indicators}")
                    except RuntimeError as e:
                        logger.error(f"Mechanism verification FAILED: {e}")

            except Exception as adapter_err:
                logger.error(
                    f"Adapter group failed (model={adapter_spec.model_name}, "
                    f"adapter={adapter_spec.adapter_type}): {adapter_err}. "
                    "Recording NaN scores for all budget ratios."
                )
                nan_tasks = {t: float("nan") for t in self.cfg.longbench_tasks}
                nan_cats = {c: float("nan") for c in LONGBENCH_CATEGORIES}
                for r in self.cfg.budget_ratios:
                    results.append(RunResult(
                        model_name=adapter_spec.model_name,
                        adapter_type=adapter_spec.adapter_type,
                        budget_ratio=r,
                        per_task_scores=dict(nan_tasks),
                        category_scores=dict(nan_cats),
                    ))
            finally:
                if model is not None:
                    del model
                try:
                    torch.cuda.empty_cache()
                except Exception:
                    pass  # CUDA context may be corrupted after device-side assert

        return results


def save_run_results(results: List[RunResult], output_dir: str) -> str:
    """Save per-run results as CSV. Returns CSV file path."""
    os.makedirs(output_dir, exist_ok=True)
    csv_path = os.path.join(output_dir, "results.csv")

    if not results:
        return csv_path

    # Build fieldnames
    sample = results[0]
    fieldnames = ["model_name", "adapter_type", "budget_ratio"]
    fieldnames += [f"task_{t}" for t in sample.per_task_scores.keys()]
    fieldnames += [f"cat_{c}" for c in sample.category_scores.keys()]

    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            writer.writerow(r.to_dict())

    logger.info(f"Results saved to {csv_path} ({len(results)} rows)")
    return csv_path
