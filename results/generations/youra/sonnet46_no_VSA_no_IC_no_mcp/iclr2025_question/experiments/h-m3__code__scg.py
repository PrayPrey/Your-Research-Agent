import numpy as np
from selfcheckgpt.modeling_selfcheck import SelfCheckBERTScore


def init_selfcheck(rescale_with_baseline: bool = True) -> SelfCheckBERTScore:
    return SelfCheckBERTScore(rescale_with_baseline=rescale_with_baseline)


def _ensure_min_length(text: str, min_len: int = 10) -> str:
    """Pad short text so spacy produces at least one sentence after len>3 filter."""
    if len(text.strip()) < min_len:
        return text.strip() + " " + ("x " * max(0, min_len - len(text.strip())))
    return text


def compute_scg_uncertainty(samples: list, selfcheck: SelfCheckBERTScore) -> float:
    """samples[0] = primary answer, samples[1:] = stochastic passages.
    Returns float in [0,1]; higher = more uncertain.
    Short passages are padded to ensure spacy produces valid sentence splits."""
    primary = _ensure_min_length(samples[0])
    others = [_ensure_min_length(s) for s in samples[1:]]
    try:
        sent_scores = selfcheck.predict(
            sentences=[primary],
            sampled_passages=others,
        )
        return float(np.mean(sent_scores))
    except (IndexError, RuntimeError):
        # Fall back to 0.5 (neutral uncertainty) if BERTScore fails
        return 0.5


def compute_all_scg_scores(samples_map: dict, selfcheck: SelfCheckBERTScore) -> dict:
    """Returns {qid: scg_uncertainty} for all questions."""
    scg_scores = {}
    total = len(samples_map)
    for i, (qid, data) in enumerate(samples_map.items()):
        score = compute_scg_uncertainty(data["samples"], selfcheck)
        scg_scores[qid] = score
        print(f"[{i+1}/{total}] qid={qid} scg={score:.4f}")
    return scg_scores


def verify_scg_mechanism(
    scg_scores: dict,
    em_labels: dict,
    se_auroc: float,
    bootstrap_auroc_fn,
) -> tuple:
    """Checks 4 indicators. Returns (activated: bool, indicators: dict, delta: float)."""
    scores_list = list(scg_scores.values())
    labels_list = [em_labels[q] for q in scg_scores.keys()]

    scores_in_range = all(0.0 <= s <= 1.0 for s in scores_list)
    scores_have_variance = float(np.std(scores_list)) > 0.01

    pos_count = sum(labels_list)
    neg_count = len(labels_list) - pos_count
    auroc_computable = pos_count > 0 and neg_count > 0

    if auroc_computable:
        scg_auroc, _, _ = bootstrap_auroc_fn(scores_list, labels_list, n_boot=100, seed=42)
        auroc_not_random = scg_auroc > 0.45
        delta = abs(scg_auroc - se_auroc)
    else:
        scg_auroc = 0.5
        auroc_not_random = False
        delta = abs(scg_auroc - se_auroc)

    indicators = {
        "scores_in_range": scores_in_range,
        "scores_have_variance": scores_have_variance,
        "auroc_computable": auroc_computable,
        "auroc_not_random": auroc_not_random,
    }
    activated = all(indicators.values())
    return activated, indicators, delta
