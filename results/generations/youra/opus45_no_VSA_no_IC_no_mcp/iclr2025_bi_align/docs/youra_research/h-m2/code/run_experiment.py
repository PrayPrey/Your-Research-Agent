"""Main experiment runner for H-M2 DPO Boundary Preservation."""
import sys
import os
import torch
from config import HM2Config, set_seed
from data import load_hh_rlhf_dpo_splits
from model import load_tokenizer, build_reference_model
from dpo_train import build_dpo_trainer, train_dpo
from evaluate import run_evaluation


def main():
    cfg = HM2Config()
    set_seed(cfg.seed)
    print("="*60)
    print("H-M2: DPO Boundary Preservation Experiment")
    print("="*60)
    print(f"Base model: {cfg.base_model}")
    print(f"Beta: {cfg.beta}")
    print(f"Device: {'cuda' if torch.cuda.is_available() else 'cpu'}")
    print("="*60)
    print("\n[1/4] Loading data...")
    splits = load_hh_rlhf_dpo_splits(cfg, max_train_samples=20000)
    print(f"Train: {len(splits['train'])}, Val: {len(splits['validation'])}, Test: {len(splits['test'])}")
    print("\n[2/4] Setting up models...")
    tokenizer = load_tokenizer(cfg)
    from transformers import AutoModelForCausalLM
    use_bf16 = cfg.bf16 and torch.cuda.is_available()
    policy_model = AutoModelForCausalLM.from_pretrained(
        cfg.base_model,
        torch_dtype=torch.bfloat16 if use_bf16 else torch.float32,
        device_map="auto" if torch.cuda.is_available() else None,
    )
    if policy_model.config.pad_token_id is None:
        policy_model.config.pad_token_id = policy_model.config.eos_token_id
    ref_model = build_reference_model(cfg)
    print("\n[3/4] Training DPO...")
    trainer = build_dpo_trainer(cfg, policy_model, ref_model, tokenizer, splits["train"], splits["validation"])
    checkpoint_path = train_dpo(cfg, trainer)
    print(f"Checkpoint saved: {checkpoint_path}")
    print("\n[4/4] Evaluating...")
    results = run_evaluation(cfg, checkpoint_path)
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    print(f"Sharpness ratio: {results['sharpness']['sharpness_ratio']:.4f} (threshold: {cfg.threshold_sharpness_ratio})")
    print(f"Boundary accuracy: {results['boundary']['boundary_accuracy']:.4f} (threshold: {cfg.threshold_boundary_accuracy})")
    print(f"Confident ratio: {results['boundary']['confident_ratio']:.4f} (threshold: {cfg.threshold_confident_ratio})")
    print(f"Win-rate: {results['winrate']['win_rate']:.4f}")
    print("="*60)
    if results["overall_pass"]:
        print("VERDICT: PASS - DPO shows sharper preference boundaries than RLHF")
    else:
        print("VERDICT: FAIL - DPO does not show sharper boundaries")
    print("="*60)
    return 0 if results["overall_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
