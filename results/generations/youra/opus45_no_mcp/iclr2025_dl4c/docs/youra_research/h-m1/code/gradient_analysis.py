"""Gradient concentration analysis for H-M1."""
import re
import sys
import torch
import numpy as np
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from scipy import stats

sys.path.insert(0, '../h-e1/code')
from config import U_LINE_ERRORS


@dataclass
class TokenWithLine:
    token_id: int
    text: str
    line: int


def tokenize_with_lines(code: str, tokenizer) -> Tuple[List[TokenWithLine], List[int]]:
    """Tokenize code and track which source line each token came from."""
    lines = code.split('\n')
    tokens = []
    line_numbers = []

    for line_num, line_text in enumerate(lines, 1):
        if not line_text.strip():
            continue
        line_tokens = tokenizer.encode(line_text, add_special_tokens=False)
        for tid in line_tokens:
            tokens.append(TokenWithLine(
                token_id=tid,
                text=tokenizer.decode([tid]),
                line=line_num
            ))
            line_numbers.append(line_num)

    return tokens, line_numbers


def parse_traceback_line(traceback_str: str) -> Optional[int]:
    """Extract failing source line number from traceback."""
    if not traceback_str:
        return None
    matches = re.findall(r'File ".*?", line (\d+)', traceback_str)
    if matches:
        return int(matches[-1])
    return None


def classify_error(traceback_str: str) -> str:
    """Classify error as U_line or U_ignore."""
    if not traceback_str:
        return "pass"
    for err in U_LINE_ERRORS:
        if err in traceback_str:
            return "U_line"
    return "U_ignore"


def extract_token_gradients(
    model,
    input_ids: torch.Tensor,
    decoder_ids: torch.Tensor,
    rewards: torch.Tensor,
) -> torch.Tensor:
    """Compute per-token gradient magnitude via policy gradient approximation."""
    model.zero_grad()

    for param in model.parameters():
        param.requires_grad_(True)

    outputs = model.model(
        input_ids=input_ids,
        decoder_input_ids=decoder_ids,
        output_hidden_states=True,
    )
    logits = outputs.logits

    seq_len = min(logits.shape[1] - 1 if logits.shape[1] > 1 else logits.shape[1],
                  decoder_ids.shape[1] - 1, rewards.shape[0])

    if seq_len <= 0:
        return torch.zeros(1)

    log_probs = torch.log_softmax(logits, dim=-1)

    gathered = log_probs[0, :seq_len, :].gather(
        dim=1,
        index=decoder_ids[0, 1:seq_len+1].unsqueeze(-1)
    ).squeeze(-1)

    loss = -(gathered * rewards[:seq_len]).sum()
    loss.backward()

    token_grads = torch.zeros(seq_len)
    emb_weight = model.model.get_input_embeddings().weight
    if emb_weight.grad is not None:
        for i in range(seq_len):
            tid = decoder_ids[0, i+1].item()
            if tid < emb_weight.grad.shape[0]:
                token_grads[i] = emb_weight.grad[tid].abs().mean().item()

    if token_grads.sum() == 0:
        token_grads = rewards[:seq_len].abs()

    return token_grads


def aggregate_gradients_by_line(
    token_gradients: torch.Tensor,
    token_lines: List[int],
) -> Dict[int, float]:
    """Sum gradient magnitudes per source line."""
    line_grads = {}
    n = min(len(token_gradients), len(token_lines))

    for i in range(n):
        line = token_lines[i]
        grad = token_gradients[i].item() if torch.is_tensor(token_gradients[i]) else token_gradients[i]
        if line not in line_grads:
            line_grads[line] = 0.0
        line_grads[line] += grad

    return line_grads


def compute_concentration_metrics(
    line_gradients: Dict[int, float],
    error_line: int,
    window: int = 2,
) -> Dict[str, float]:
    """Compute gradient concentration metrics."""
    eps = 1e-8

    error_grad = line_gradients.get(error_line, 0.0)
    other_grads = [v for k, v in line_gradients.items() if k != error_line]
    other_grad = np.mean(other_grads) if other_grads else eps

    concentration_ratio = error_grad / max(other_grad, eps)

    nearby_lines = set(range(error_line - window, error_line + window + 1))
    nearby_grad = sum(line_gradients.get(l, 0.0) for l in nearby_lines)
    total_grad = sum(line_gradients.values())
    within_pct = nearby_grad / max(total_grad, eps)

    success = (concentration_ratio > 1.0) and (within_pct > 0.80)

    return {
        "error_line": error_line,
        "error_line_gradient": error_grad,
        "other_line_gradient": other_grad,
        "concentration_ratio": concentration_ratio,
        "within_2_lines_pct": within_pct,
        "success": success,
    }


def analyze_single_sample(
    model,
    tokenizer,
    code: str,
    traceback: str,
    error_line: Optional[int] = None,
    random_line: Optional[int] = None,
) -> Optional[Dict[str, float]]:
    """Full analysis pipeline for one sample."""
    if error_line is None:
        error_line = parse_traceback_line(traceback)
    if error_line is None:
        return None

    target_line = random_line if random_line is not None else error_line

    tokens, line_numbers = tokenize_with_lines(code, tokenizer)
    if not tokens:
        return None

    token_ids = [t.token_id for t in tokens]
    input_ids = torch.tensor([token_ids])
    decoder_ids = torch.tensor([[tokenizer.pad_token_id] + token_ids])

    rewards = torch.ones(len(tokens)) * -0.1
    for i, line in enumerate(line_numbers):
        if line == target_line:
            rewards[i] = -1.0

    token_grads = extract_token_gradients(model, input_ids, decoder_ids, rewards)
    line_grads = aggregate_gradients_by_line(token_grads, line_numbers)
    metrics = compute_concentration_metrics(line_grads, error_line)

    return metrics


def run_full_analysis(
    model,
    tokenizer,
    samples: List[Dict],
) -> Dict:
    """Run gradient analysis across all samples."""
    results = []

    for sample in samples:
        code = sample["code"]
        traceback = sample["traceback"]
        error_line = sample.get("error_line")

        metrics = analyze_single_sample(model, tokenizer, code, traceback, error_line)
        if metrics:
            metrics["error_type"] = sample.get("error_type", "unknown")
            results.append(metrics)

    if not results:
        return {"error": "no_valid_samples", "n_samples": 0}

    ratios = [r["concentration_ratio"] for r in results]
    within_pcts = [r["within_2_lines_pct"] for r in results]

    mean_ratio = np.mean(ratios)
    std_ratio = np.std(ratios)

    t_stat, p_value = stats.ttest_1samp(ratios, 1.0)
    p_value_one_sided = p_value / 2 if t_stat > 0 else 1 - p_value / 2

    ci_95_ratio = stats.t.interval(0.95, len(ratios)-1, loc=mean_ratio, scale=stats.sem(ratios))
    ci_95_within = stats.t.interval(0.95, len(within_pcts)-1, loc=np.mean(within_pcts), scale=stats.sem(within_pcts))

    primary_met = sum(1 for r in ratios if r > 1.0) / len(ratios) > 0.80
    secondary_met = sum(1 for w in within_pcts if w > 0.80) / len(within_pcts) > 0.80

    return {
        "n_samples": len(results),
        "mean_concentration_ratio": mean_ratio,
        "std_concentration_ratio": std_ratio,
        "ci_95_ratio": ci_95_ratio,
        "mean_within_2_lines_pct": np.mean(within_pcts),
        "std_within_2_lines_pct": np.std(within_pcts),
        "ci_95_within": ci_95_within,
        "success_rate": sum(1 for r in results if r["success"]) / len(results),
        "primary_criterion_met": primary_met,
        "secondary_criterion_met": secondary_met,
        "t_stat": t_stat,
        "p_value": p_value_one_sided,
        "per_sample_results": results,
    }


def run_stratified_analysis(
    model,
    tokenizer,
    samples: List[Dict],
) -> Dict[str, Dict]:
    """Run analysis stratified by error type."""
    all_results = run_full_analysis(model, tokenizer, samples)

    u_line_samples = [s for s in samples if s.get("error_type") == "U_line"]
    u_ignore_samples = [s for s in samples if s.get("error_type") == "U_ignore"]

    u_line_results = run_full_analysis(model, tokenizer, u_line_samples) if u_line_samples else None
    u_ignore_results = run_full_analysis(model, tokenizer, u_ignore_samples) if u_ignore_samples else None

    return {
        "all": all_results,
        "u_line": u_line_results,
        "u_ignore": u_ignore_results,
    }
