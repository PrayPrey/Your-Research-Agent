"""Analysis pipeline for H-M2 Hidden State Drift."""
import json
import os
import torch
import torch.nn.functional as F
from torch import nn
from collections import defaultdict
from typing import Dict, List, Optional
from tqdm import tqdm
from scipy import stats
import numpy as np

from config import AnalysisConfig
from data import get_long_documents, build_batches
from model import load_teacher, load_student, get_student_dim, CABUnavailableError


def extract_hidden_states(model: nn.Module, input_ids: torch.Tensor, layers: List[int], device, normalize_layers: bool = False) -> Dict[int, torch.Tensor]:
    """Forward with output_hidden_states=True. Returns {layer_idx: [B, N, D]}.

    If normalize_layers=True, maps requested layer indices proportionally to model's actual layers.
    This handles comparing models with different layer counts (e.g., 24 vs 48 layers).
    """
    input_ids = input_ids.to(device)
    with torch.no_grad():
        outputs = model(input_ids, output_hidden_states=True)
    hidden_states = outputs.hidden_states
    num_layers = len(hidden_states)

    if normalize_layers:
        # Map layer indices proportionally (e.g., layer 8 of 24 -> layer 16 of 48)
        result = {}
        for i in layers:
            mapped_idx = min(int(i * num_layers / 25), num_layers - 1)  # 25 = Phi's total layers
            result[i] = hidden_states[mapped_idx].cpu()
        return result

    return {i: hidden_states[i].cpu() for i in layers if i < len(hidden_states)}


def get_projection(student_dim: int, teacher_dim: int, device) -> Optional[nn.Linear]:
    """Returns nn.Linear(student_dim, teacher_dim) if dims differ, else None."""
    if student_dim == teacher_dim:
        return None
    proj = nn.Linear(student_dim, teacher_dim).to(device).half()
    return proj


def l2_drift(h_teacher: torch.Tensor, h_student: torch.Tensor) -> float:
    """L2 distance between hidden states."""
    return torch.norm(h_teacher.float() - h_student.float(), p=2, dim=-1).mean().item()


def cosine_sim(h_teacher: torch.Tensor, h_student: torch.Tensor) -> float:
    """Cosine similarity between hidden states."""
    return F.cosine_similarity(h_teacher.float(), h_student.float(), dim=-1).mean().item()


def compute_drift_per_layer(
    teacher_hidden: Dict[int, torch.Tensor],
    student_hidden: Dict[int, torch.Tensor],
    projection: Optional[nn.Linear],
    device
) -> Dict[int, dict]:
    """Per layer L2 + cosine drift. Returns {layer_idx: {"l2": float, "cosine": float}}."""
    results = {}
    for layer_idx in teacher_hidden.keys():
        if layer_idx not in student_hidden:
            continue
        t_h = teacher_hidden[layer_idx]
        s_h = student_hidden[layer_idx]

        if projection is not None:
            s_h = s_h.to(device)
            with torch.no_grad():
                s_h = projection(s_h.float()).cpu()

        results[layer_idx] = {
            "l2": l2_drift(t_h, s_h),
            "cosine": cosine_sim(t_h, s_h)
        }
    return results


def compute_slope(lengths: List[int], drifts: List[float]) -> dict:
    """Compute linear regression slope with CI."""
    slope, intercept, r_value, p_value, std_err = stats.linregress(lengths, drifts)
    n = len(lengths)
    t_val = stats.t.ppf(0.975, n - 2)
    ci95_margin = t_val * std_err
    return {
        "slope": slope,
        "intercept": intercept,
        "r_value": r_value,
        "p_value": p_value,
        "std_err": std_err,
        "ci95_lo": slope - ci95_margin,
        "ci95_hi": slope + ci95_margin
    }


def variance_check(drifts: List[float]) -> bool:
    """Check if std < mean (meaningful variance)."""
    arr = np.array(drifts)
    return arr.std() < arr.mean()


def evaluate_gate(mohawk_slope: float, cab_slope: float, cab_drifts_by_length: Dict[int, float]) -> dict:
    """Evaluate gate: cab_slope < mohawk_slope AND max(cab)/min(cab) < 2.0."""
    cab_values = list(cab_drifts_by_length.values())
    ratio = max(cab_values) / min(cab_values) if min(cab_values) > 0 else float('inf')
    return {
        "pass": cab_slope < mohawk_slope and ratio < 2.0,
        "cab_slope": cab_slope,
        "mohawk_slope": mohawk_slope,
        "cab_drift_ratio": ratio,
        "slope_comparison": "cab_slope < mohawk_slope" if cab_slope < mohawk_slope else "cab_slope >= mohawk_slope",
        "ratio_check": "ratio < 2.0" if ratio < 2.0 else "ratio >= 2.0"
    }


def run_variant(
    config: AnalysisConfig,
    teacher: nn.Module,
    tokenizer,
    student: nn.Module,
    variant: str,
    docs: List[str],
    teacher_device,
    student_device
) -> Dict[int, dict]:
    """Loop target_lengths -> batches -> extract+drift. Returns {length: {"l2", "cosine", "per_layer"}}."""
    student_dim = get_student_dim(student)
    projection = get_projection(student_dim, config.teacher_dim, student_device)

    results = {}
    for length in config.target_lengths:
        print(f"  Processing length {length} for {variant}...")
        batches = build_batches(docs, tokenizer, length, config.batch_size)

        l2_acc = []
        cos_acc = []
        per_layer_acc = defaultdict(list)

        for batch in tqdm(batches, desc=f"{variant} L={length}"):
            input_ids = batch["input_ids"]

            try:
                t_hidden = extract_hidden_states(teacher, input_ids, config.middle_layers, teacher_device, normalize_layers=False)
                # Student (Mamba) may have different layer count, normalize to match teacher layers
                s_hidden = extract_hidden_states(student, input_ids, config.middle_layers, student_device, normalize_layers=True)
                layer_drift = compute_drift_per_layer(t_hidden, s_hidden, projection, student_device)

                for layer, d in layer_drift.items():
                    per_layer_acc[layer].append(d)
                l2_acc.append(np.mean([d["l2"] for d in layer_drift.values()]))
                cos_acc.append(np.mean([d["cosine"] for d in layer_drift.values()]))

                del t_hidden, s_hidden
                torch.cuda.empty_cache()
            except RuntimeError as e:
                if "out of memory" in str(e).lower():
                    print(f"OOM at length {length}, skipping batch")
                    torch.cuda.empty_cache()
                    continue
                raise

        results[length] = {
            "l2": float(np.mean(l2_acc)) if l2_acc else 0.0,
            "cosine": float(np.mean(cos_acc)) if cos_acc else 0.0,
            "per_layer": {
                layer: {
                    "l2": float(np.mean([x["l2"] for x in v])),
                    "cosine": float(np.mean([x["cosine"] for x in v]))
                }
                for layer, v in per_layer_acc.items()
            },
            "variance_check": variance_check(l2_acc) if l2_acc else False
        }

    return results


def run_full_analysis(config: AnalysisConfig) -> dict:
    """Load teacher+students, run both variants, compute slope/gate/variance."""
    teacher, tokenizer = load_teacher(config)
    teacher_device = next(teacher.parameters()).device

    docs = get_long_documents(config, tokenizer)
    print(f"Loaded {len(docs)} documents")

    out = {}
    variants_run = []

    for variant in ["mohawk", "cab"]:
        print(f"\nLoading {variant} student...")
        try:
            student = load_student(config, variant, teacher)
            student_device = teacher_device  # Simulated student shares teacher device
        except CABUnavailableError as e:
            print(f"WARNING: {e}")
            print(f"Skipping {variant} variant")
            continue

        out[variant] = run_variant(config, teacher, tokenizer, student, variant, docs, teacher_device, student_device)
        variants_run.append(variant)

        del student
        torch.cuda.empty_cache()

    lengths = config.target_lengths

    if "mohawk" not in out:
        raise RuntimeError("MOHAWK model must be available")

    mohawk_drifts = [out["mohawk"][l]["l2"] for l in lengths]
    mohawk_slope_data = compute_slope(lengths, mohawk_drifts)

    if "cab" in out:
        cab_drifts = [out["cab"][l]["l2"] for l in lengths]
        cab_slope_data = compute_slope(lengths, cab_drifts)
        gate = evaluate_gate(
            mohawk_slope_data["slope"],
            cab_slope_data["slope"],
            {l: out["cab"][l]["l2"] for l in lengths}
        )
    else:
        cab_slope_data = None
        gate = {
            "pass": False,
            "note": "CAB unavailable, gate cannot be evaluated",
            "mohawk_slope": mohawk_slope_data["slope"]
        }

    return {
        "mohawk": {**out["mohawk"], "slope": mohawk_slope_data},
        "cab": {**out.get("cab", {}), "slope": cab_slope_data} if "cab" in out else None,
        "gate": gate,
        "variants_run": variants_run,
        "lengths": lengths
    }


def save_results(results: dict, config: AnalysisConfig) -> None:
    """Save results to JSON."""
    os.makedirs(config.output_dir, exist_ok=True)
    output_path = os.path.join(config.output_dir, config.results_filename)

    with open(output_path, "w") as f:
        json.dump(results, f, indent=2, default=float)
    print(f"Results saved to {output_path}")
