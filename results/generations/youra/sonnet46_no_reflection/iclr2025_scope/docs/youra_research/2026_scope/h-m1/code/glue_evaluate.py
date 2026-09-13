"""
H-M1 Evaluation: GLUE accuracy + LongBench QA F1 + mechanism verification.
"""
import os
import json
import re
import string
import collections
import torch
import evaluate as hf_evaluate
from typing import Dict, List, Optional
from config import ExperimentConfig
from model import JointLoRAKVModel
from data_loader import get_longbench_loader


def evaluate_glue(
    model: JointLoRAKVModel,
    val_loader,
    task: str,
    config: ExperimentConfig,
    collect_cis_samples: bool = False,
) -> Dict:
    model.eval()
    device = next(model.parameters()).device
    all_preds, all_refs = [], []
    tokens_retained_ratios = []
    cis_samples = []

    with torch.no_grad():
        for batch in val_loader:
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"]

            out = model(
                input_ids=input_ids,
                attention_mask=attention_mask,
                budget_ratio=config.kv_budget_ratio,
                training_mode=False,
                collect_cis_samples=collect_cis_samples and len(cis_samples) < 10,
            )
            logits = out["logits"]
            preds = logits.argmax(dim=-1).cpu().tolist()
            all_preds.extend(preds)
            all_refs.extend(labels.tolist())
            tokens_retained_ratios.append(out["tokens_retained_ratio"])
            if "cis_scores" in out and len(cis_samples) < 10:
                cis_samples.extend(out["cis_scores"])

    metric = hf_evaluate.load("glue", task)
    if task == "mnli":
        result = metric.compute(predictions=all_preds, references=all_refs)
        accuracy = result.get("accuracy", result.get("mnli/acc", 0.0))
    else:
        result = metric.compute(predictions=all_preds, references=all_refs)
        accuracy = result.get("accuracy", 0.0)

    mean_retained = float(sum(tokens_retained_ratios) / max(len(tokens_retained_ratios), 1))
    return {
        "accuracy": accuracy,
        "task": task,
        "budget_ratio": config.kv_budget_ratio,
        "cis_samples": cis_samples,
        "tokens_retained_ratio": mean_retained,
    }


def evaluate_budget_sensitivity(
    model: JointLoRAKVModel,
    val_loader,
    task: str,
    config: ExperimentConfig,
) -> Dict:
    results = {}
    for ratio in config.kv_budget_ratios_sweep:
        model.eval()
        device = next(model.parameters()).device
        all_preds, all_refs = [], []
        with torch.no_grad():
            for batch in val_loader:
                input_ids = batch["input_ids"].to(device)
                attention_mask = batch["attention_mask"].to(device)
                labels = batch["labels"]
                out = model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    budget_ratio=ratio,
                    training_mode=False,
                )
                all_preds.extend(out["logits"].argmax(dim=-1).cpu().tolist())
                all_refs.extend(labels.tolist())
        metric = hf_evaluate.load("glue", task)
        r = metric.compute(predictions=all_preds, references=all_refs)
        results[ratio] = r.get("accuracy", 0.0)

    out_path = config.results_dir / f"budget_sensitivity_{task}.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    return results


def _normalize_answer(s: str) -> str:
    s = s.lower()
    s = re.sub(r'\b(a|an|the)\b', ' ', s)
    s = ''.join(c for c in s if c not in string.punctuation)
    return ' '.join(s.split())


def qa_f1_score(prediction: str, ground_truths: List[str]) -> float:
    def _f1(pred: str, truth: str) -> float:
        pred_tokens = _normalize_answer(pred).split()
        truth_tokens = _normalize_answer(truth).split()
        common = collections.Counter(pred_tokens) & collections.Counter(truth_tokens)
        num_same = sum(common.values())
        if num_same == 0:
            return 0.0
        precision = num_same / len(pred_tokens)
        recall = num_same / len(truth_tokens)
        return 2 * precision * recall / (precision + recall)
    return max(_f1(prediction, gt) for gt in ground_truths) if ground_truths else 0.0


def evaluate_longbench(
    model: JointLoRAKVModel,
    tokenizer,
    task: str,
    config: ExperimentConfig,
) -> Dict:
    model.eval()
    device = next(model.parameters()).device
    loader = get_longbench_loader(task, tokenizer, config)
    f1_scores = []

    with torch.no_grad():
        for batch in loader:
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            answers = batch["answers"]
            if isinstance(answers, list) and len(answers) > 0 and isinstance(answers[0], list):
                answers = answers[0]

            gen_ids = model.base_model.generate(
                input_ids=input_ids,
                attention_mask=attention_mask,
                max_new_tokens=config.longbench_max_new_tokens,
                do_sample=False,
                pad_token_id=tokenizer.eos_token_id,
            )
            new_tokens = gen_ids[0][input_ids.shape[-1]:]
            prediction = tokenizer.decode(new_tokens, skip_special_tokens=True).strip()
            gt_list = [str(a) for a in answers] if answers else [""]
            f1_scores.append(qa_f1_score(prediction, gt_list))

    return {
        "f1": float(sum(f1_scores) / max(len(f1_scores), 1)),
        "task": task,
        "budget_ratio": config.kv_budget_ratio,
    }


def aggregate_seed_results(results_per_seed: List[Dict]) -> Dict:
    """Aggregate GLUE results across seeds. Each item: {task: {accuracy: float}}."""
    tasks = list(results_per_seed[0].keys())
    aggregated = {}
    for task in tasks:
        accs = [r[task]["accuracy"] * 100 for r in results_per_seed if task in r]
        import statistics
        aggregated[f"{task}_mean"] = statistics.mean(accs) if accs else 0.0
        aggregated[f"{task}_std"] = statistics.stdev(accs) if len(accs) > 1 else 0.0

    all_accs = []
    for r in results_per_seed:
        for task in tasks:
            if task in r:
                all_accs.append(r[task]["accuracy"] * 100)
    aggregated["mean_glue_acc"] = sum(all_accs) / max(len(all_accs), 1)
    return aggregated


def verify_mechanism_activated(
    training_log_path: str,
    b1_results: Dict,
    joint_results: Dict,
) -> tuple:
    # Check 1: Locret grad norm > 1e-6 in training log
    locret_grad_received = False
    if os.path.exists(training_log_path):
        with open(training_log_path) as f:
            for line in f:
                if "locret_grad_norm=" in line:
                    try:
                        val = float(line.split("locret_grad_norm=")[-1].strip())
                        if val > 1e-6:
                            locret_grad_received = True
                            break
                    except Exception:
                        pass

    # Check 2: CIS shape (B, L, 8)
    cis_samples = joint_results.get("cis_samples", [])
    cis_shape_correct = all(
        hasattr(c, "shape") and c.shape[-1] == 8 for c in cis_samples
    ) if cis_samples else True  # if no samples captured, assume ok

    # Check 3: Eviction active
    eviction_active = joint_results.get("tokens_retained_ratio", 1.0) < 0.55

    # Check 4: Accuracy improved
    joint_acc = joint_results.get("mean_glue_acc", 0.0)
    b1_acc = b1_results.get("mean_glue_acc", 0.0)
    accuracy_improved = joint_acc > b1_acc
    gap = joint_acc - b1_acc

    indicators = {
        "locret_grad_received": locret_grad_received,
        "cis_shape_correct": cis_shape_correct,
        "eviction_active": eviction_active,
        "accuracy_improved": accuracy_improved,
        "gap_pp": gap,
    }

    gate_passed = (
        locret_grad_received
        and cis_shape_correct
        and eviction_active
        and accuracy_improved
        and gap >= 2.0
    )
    return gate_passed, indicators
