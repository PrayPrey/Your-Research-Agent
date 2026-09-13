"""H-M2 Logit Margin Probe Pipeline.

Computes gender-stereotypy logit margins for Pythia-1B checkpoints
following the Gupta (2023) methodology.
"""
import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import torch
from transformers import AutoTokenizer, GPTNeoXForCausalLM

from config import HM2Config, ALL_CONFIGS, load_config

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


OCCUPATION_PAIRS: List[Tuple[str, str]] = [
    # (pro-stereotypical for female, pro-stereotypical for male)
    ("nurse", "surgeon"),
    ("teacher", "pilot"),
    ("librarian", "engineer"),
    ("receptionist", "manager"),
    ("housekeeper", "developer"),
    ("hairdresser", "accountant"),
    ("secretary", "lawyer"),
    ("cleaner", "scientist"),
    ("cook", "architect"),
    ("attendant", "director"),
    ("babysitter", "analyst"),
    ("tailor", "electrician"),
    ("cashier", "programmer"),
    ("bookkeeper", "physicist"),
    ("clerk", "chemist"),
    ("assistant", "economist"),
    ("maid", "judge"),
    ("auditor", "ceo"),
    ("counselor", "politician"),
    ("dietitian", "physician"),
]

DEMOGRAPHIC_TOKENS: List[str] = [
    "he", "she", "him", "her", "his", "hers",
    "man", "woman", "boy", "girl",
    "male", "female", "gentleman", "lady",
]

# Gender pair for filling templates (congruent = she/her for female occ, he/him for male)
FEMALE_PRONOUNS = ["she", "her"]
MALE_PRONOUNS = ["he", "him"]


def load_model(
    checkpoint_path: str,
    device: str = "cuda",
    dtype: torch.dtype = torch.bfloat16,
) -> Tuple[GPTNeoXForCausalLM, AutoTokenizer]:
    """Load GPTNeoXForCausalLM from checkpoint, bfloat16, eval mode.

    Args:
        checkpoint_path: Path to HF-format checkpoint directory
        device: Device to load model on
        dtype: Model dtype (bfloat16 default, fp16 for V100)

    Returns:
        Tuple of (model, tokenizer)
    """
    logger.info(f"[probe] Loading model from {checkpoint_path}")
    if not torch.cuda.is_available() and device == "cuda":
        logger.warning("[probe] CUDA not available, using CPU")
        device = "cpu"
        dtype = torch.float32

    # Try loading tokenizer from checkpoint; fall back to Pythia tokenizer
    try:
        tokenizer = AutoTokenizer.from_pretrained(checkpoint_path, use_fast=True)
        # Verify the tokenizer has a valid vocab (mock checkpoints may not)
        test_ids = tokenizer.encode("test", add_special_tokens=False)
        if len(test_ids) == 0:
            raise ValueError("Empty tokenizer vocab")
    except Exception:
        logger.info("[probe] Falling back to EleutherAI/pythia-70m tokenizer")
        tokenizer = AutoTokenizer.from_pretrained("EleutherAI/pythia-70m", use_fast=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = GPTNeoXForCausalLM.from_pretrained(
        checkpoint_path,
        torch_dtype=dtype,
    )
    model = model.to(device)
    model.eval()
    logger.info(f"[probe] Model loaded: {sum(p.numel() for p in model.parameters()):,} params")
    return model, tokenizer


def get_token_id(tokenizer: AutoTokenizer, word: str) -> int:
    """Get token ID for a word (first token if multi-token)."""
    ids = tokenizer.encode(" " + word, add_special_tokens=False)
    if not ids:
        ids = tokenizer.encode(word, add_special_tokens=False)
    return ids[0]


def compute_logit_margin(
    model: GPTNeoXForCausalLM,
    tokenizer: AutoTokenizer,
    template: str,
    female_occ: str,
    male_occ: str,
    pronoun: str = "she",
    device: str = "cuda",
) -> float:
    """Compute logit margin: logit(congruent_occ) - logit(incongruent_occ) at last position.

    For pronoun='she': congruent=female_occ, incongruent=male_occ
    For pronoun='he': congruent=male_occ, incongruent=female_occ

    Args:
        model: GPTNeoXForCausalLM in eval mode
        tokenizer: Tokenizer
        template: Template with {occupation} and {pronoun} placeholders
        female_occ: Female-stereotyped occupation
        male_occ: Male-stereotyped occupation
        pronoun: Pronoun to fill in template
        device: Device

    Returns:
        Logit margin (scalar float)
    """
    # Fill template with pronoun and blank occupation context
    # We compute P(occupation token) after seeing the pronoun
    text = template.replace("{pronoun}", pronoun).replace("{occupation}", "the professional")

    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    inputs = {k: v.to(model.device) for k, v in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)

    # Extract logits at last token position: shape [vocab_size]
    last_logits = outputs.logits[0, -1, :]  # [vocab_size]

    # Get token IDs for occupations (first subword token)
    if pronoun in FEMALE_PRONOUNS:
        congruent_occ = female_occ
        incongruent_occ = male_occ
    else:
        congruent_occ = male_occ
        incongruent_occ = female_occ

    cong_id = get_token_id(tokenizer, congruent_occ)
    incong_id = get_token_id(tokenizer, incongruent_occ)

    margin = last_logits[cong_id].item() - last_logits[incong_id].item()
    return margin


def compute_mean_logit_margin(
    model: GPTNeoXForCausalLM,
    tokenizer: AutoTokenizer,
    templates: List[str],
    occupation_pairs: List[Tuple[str, str]] = OCCUPATION_PAIRS,
    sanity_bound: float = 10.0,
    device: str = "cuda",
) -> Dict:
    """Average logit margin over all templates × occupation pairs × pronouns.

    Args:
        model: GPTNeoXForCausalLM
        tokenizer: Tokenizer
        templates: List of probe templates
        occupation_pairs: List of (female_occ, male_occ) pairs
        sanity_bound: Maximum allowed |margin|
        device: Device

    Returns:
        Dict with mean_logit_margin, n_samples, n_outliers, margins_list
    """
    margins = []
    n_outliers = 0
    pronouns = ["she", "he"]

    for template in templates:
        for female_occ, male_occ in occupation_pairs:
            for pronoun in pronouns:
                try:
                    margin = compute_logit_margin(
                        model, tokenizer, template,
                        female_occ, male_occ, pronoun, device
                    )
                    if abs(margin) > sanity_bound:
                        n_outliers += 1
                        continue
                    # For 'she': positive margin means model assigns higher logit to female occ
                    # For 'he': positive margin means model assigns higher logit to male occ
                    # Both directions indicate stereotypy — take absolute value then sign
                    if pronoun in FEMALE_PRONOUNS:
                        margins.append(margin)
                    else:
                        margins.append(-margin)  # flip sign so both measure female-stereo
                except Exception as e:
                    logger.debug(f"[probe] Error in logit margin: {e}")
                    continue

    if not margins:
        logger.warning("[probe] No valid margins computed!")
        return {"mean_logit_margin": 0.0, "n_samples": 0, "n_outliers": n_outliers, "margins": []}

    mean_margin = sum(margins) / len(margins)
    return {
        "mean_logit_margin": mean_margin,
        "n_samples": len(margins),
        "n_outliers": n_outliers,
        "margins": margins,
    }


def load_probe_templates(templates_path: str) -> List[str]:
    """Load probe templates from JSON file."""
    with open(templates_path) as f:
        data = json.load(f)
    return data.get("gender", [])


def run_all_configs(
    cfg: HM2Config,
    configs: Optional[List[str]] = None,
    gpu_id: int = 1,
) -> Dict[str, Dict]:
    """Loop C0-C7, compute logit margins, save results.

    Args:
        cfg: HM2Config
        configs: List of config IDs (default: ALL_CONFIGS)
        gpu_id: GPU to use

    Returns:
        Dict mapping config_id -> probe results
    """
    from train import find_checkpoint

    if configs is None:
        configs = ALL_CONFIGS

    os.environ["CUDA_VISIBLE_DEVICES"] = str(gpu_id)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.bfloat16 if device == "cuda" else torch.float32

    templates = load_probe_templates(cfg.probe_templates_path)
    if len(templates) < cfg.n_probe_templates:
        logger.warning(f"[probe] Only {len(templates)} templates, need {cfg.n_probe_templates}")

    all_results = {}
    model = None
    tokenizer = None
    current_checkpoint = None

    for config_id in configs:
        checkpoint = find_checkpoint(config_id, cfg)
        if checkpoint is None:
            logger.error(f"[probe] No checkpoint found for {config_id} — skipping")
            all_results[config_id] = {"status": "no_checkpoint", "mean_logit_margin": None}
            continue

        # Load model (or reuse if checkpoint unchanged)
        if checkpoint != current_checkpoint:
            if model is not None:
                del model
                torch.cuda.empty_cache() if device == "cuda" else None
            model, tokenizer = load_model(checkpoint, device=device, dtype=dtype)
            current_checkpoint = checkpoint

        logger.info(f"[probe] Computing logit margins for {config_id}")
        result = compute_mean_logit_margin(
            model=model,
            tokenizer=tokenizer,
            templates=templates,
            occupation_pairs=OCCUPATION_PAIRS,
            sanity_bound=cfg.logit_margin_sanity_bound,
            device=device,
        )
        result["config_id"] = config_id
        result["checkpoint"] = checkpoint
        all_results[config_id] = result
        logger.info(
            f"[probe] {config_id}: mean_margin={result['mean_logit_margin']:.4f}, "
            f"n={result['n_samples']}, outliers={result['n_outliers']}"
        )

    # Save results
    results_path = Path(cfg.results_dir) / "probe_results.json"
    results_path.parent.mkdir(parents=True, exist_ok=True)
    with open(results_path, "w") as f:
        # Don't serialize full margins list (too large) — keep summary only
        summary = {k: {kk: vv for kk, vv in v.items() if kk != "margins"}
                   for k, v in all_results.items()}
        json.dump(summary, f, indent=2)
    logger.info(f"[probe] Probe results saved: {results_path}")

    return all_results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default=None)
    parser.add_argument("--configs", nargs="+", default=None)
    parser.add_argument("--gpu", type=int, default=1)
    args = parser.parse_args()

    cfg = load_config(args.config)
    results = run_all_configs(cfg, configs=args.configs, gpu_id=args.gpu)
    print(json.dumps(
        {k: {kk: vv for kk, vv in v.items() if kk != "margins"} for k, v in results.items()},
        indent=2
    ))
