"""Minimal PoC for H-M1: Validate mechanism with scaled-down experiment"""
import torch
import numpy as np
import pandas as pd
import json
from pathlib import Path
from datasets import load_dataset
from transformers import GPT2LMHeadModel, GPT2Tokenizer
from config import CONFIG

# Override for PoC: minimal scale
POC_CONFIG = {
    "num_samples": 1000,  # 1k samples instead of 50GB
    "training_steps": 500,  # 500 steps instead of 50k
    "num_conditions": 3,  # Test 3 key conditions instead of 9
}


def sample_c4_subset(num_samples=1000):
    """Sample small C4 subset for PoC"""
    print(f"Sampling {num_samples} examples from C4...")
    dataset = load_dataset("allenai/c4", "en", split="train", streaming=True)
    texts = []
    for i, sample in enumerate(dataset):
        if i >= num_samples:
            break
        texts.append(sample["text"])
    return texts


def simulate_curation(texts, curation_level):
    """Simulate curation effect (simplified for PoC)"""
    if curation_level == "baseline":
        return texts  # No curation
    elif curation_level == "medium":
        # Remove duplicates + short texts
        seen = set()
        curated = []
        for t in texts:
            if t not in seen and len(t) > 100:
                seen.add(t)
                curated.append(t)
        return curated[:len(texts)]  # Keep same size
    else:  # full
        # Aggressive filtering
        curated = [t for t in texts if len(t) > 200 and len(t.split()) > 50]
        if len(curated) < len(texts) // 2:
            curated.extend(texts[:len(texts) - len(curated)])
        return curated[:len(texts)]


def compute_entropy_fisher(model, tokenizer, texts, device):
    """Compute entropy and Fisher trace on text batch"""
    model.eval()
    entropies = []
    fisher_traces = []

    for text in texts[:100]:  # Sample 100 for speed
        tokens = tokenizer.encode(text, max_length=512, truncation=True, return_tensors="pt").to(device)
        if tokens.shape[1] < 10:
            continue

        model.zero_grad()
        with torch.enable_grad():
            outputs = model(tokens, labels=tokens)
            loss = outputs.loss

            # Entropy
            probs = torch.softmax(outputs.logits, dim=-1)
            log_probs = torch.log_softmax(outputs.logits, dim=-1)
            entropy = -(probs * log_probs).sum(dim=-1).mean().item()
            entropies.append(entropy)

            # Fisher trace
            loss.backward()
            fisher_trace = sum((p.grad ** 2).sum().item() for p in model.parameters() if p.grad is not None)
            fisher_traces.append(fisher_trace)

    return np.mean(entropies), np.mean(fisher_traces)


def main():
    """Run PoC experiment"""
    print("\n" + "="*60)
    print("H-M1 PoC: Minimal Validation")
    print("="*60)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Device: {device}")

    # Load model
    print("\nLoading GPT-2...")
    model = GPT2LMHeadModel.from_pretrained("gpt2").to(device)
    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")

    # Sample data
    print("\nSampling C4 data...")
    texts = sample_c4_subset(POC_CONFIG["num_samples"])
    print(f"Sampled {len(texts)} texts")

    # Test 3 conditions
    conditions = ["baseline", "medium", "full"]
    results = []

    for cond in conditions:
        print(f"\n{'='*60}")
        print(f"Condition: {cond}")
        print('='*60)

        # Curate
        curated_texts = simulate_curation(texts, cond)
        print(f"Curated: {len(curated_texts)} texts")

        # Measure
        entropy, fisher = compute_entropy_fisher(model, tokenizer, curated_texts, device)
        print(f"Entropy: {entropy:.4f}")
        print(f"Fisher trace: {fisher:.2e}")

        results.append({
            "condition": cond,
            "entropy": entropy,
            "fisher_trace": fisher
        })

    # Evaluate
    df = pd.DataFrame(results)
    print("\n" + "="*60)
    print("RESULTS")
    print("="*60)
    print(df)

    baseline = df[df["condition"] == "baseline"].iloc[0]
    full = df[df["condition"] == "full"].iloc[0]

    entropy_reduction = 100 * (baseline["entropy"] - full["entropy"]) / baseline["entropy"]
    fisher_increase = 100 * (full["fisher_trace"] - baseline["fisher_trace"]) / baseline["fisher_trace"]

    print(f"\nEntropy Reduction: {entropy_reduction:.2f}%")
    print(f"Fisher Increase: {fisher_increase:.2f}%")

    # Gate decision
    if entropy_reduction > 20 and fisher_increase > 15:
        gate_result = "PASS"
    elif entropy_reduction > 10 or fisher_increase > 10:
        gate_result = "PARTIAL"
    else:
        gate_result = "FAIL"

    print(f"\nGate Result: {gate_result}")

    # Save
    outputs_dir = Path("outputs")
    outputs_dir.mkdir(exist_ok=True)

    results_json = {
        "entropy_reduction": entropy_reduction,
        "fisher_increase": fisher_increase,
        "gate_result": gate_result,
        "poc_mode": True,
        "conditions": results
    }

    with open(outputs_dir / "experiment_results.json", 'w') as f:
        json.dump(results_json, f, indent=2)

    df.to_csv(outputs_dir / "results.csv", index=False)

    print(f"\nResults saved to {outputs_dir}")
    print("="*60)

    return gate_result


if __name__ == "__main__":
    result = main()
    import sys
    sys.exit(0 if result == "PASS" else 1)
