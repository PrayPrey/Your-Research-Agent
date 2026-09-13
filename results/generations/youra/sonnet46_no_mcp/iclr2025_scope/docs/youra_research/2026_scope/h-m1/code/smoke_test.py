"""
smoke_test.py — PoC smoke test for H-E1 hypothesis.

Uses a tiny GPT-2 model (117M) to validate that the H2O eviction mask
mechanism causes LoRA adapter weight divergence (cosine_similarity < 0.95).
This is a Phase 4 MUST_WORK gate PoC test.

Dataset: LongAlpaca-12k (Yukang/LongAlpaca-12k, HuggingFace Hub)

Usage:
    CUDA_VISIBLE_DEVICES=1 python smoke_test.py
"""
import os
import sys
import json
import logging
import torch
import torch.nn as nn
import torch.nn.functional as F
from datetime import datetime
from pathlib import Path

os.environ["WANDB_DISABLED"] = "true"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

OUTPUTS_DIR = Path("outputs/h-e1")
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

HYP_FOLDER = Path("docs/youra_research/20260504_scope/h-e1")
FIGURES_DIR = HYP_FOLDER / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)


class H2OAttentionHook:
    """
    Applies H2O eviction mask to GPT-2 attention via a register_forward_hook.
    The hook intercepts the full attention forward pass and re-computes the
    output with the eviction mask applied at the logit level (before softmax),
    ensuring evicted positions receive zero gradient.
    """

    def __init__(self, kv_budget_ratio: float = 0.5):
        self.kv_budget_ratio = kv_budget_ratio
        self._hooks = []

    def _build_eviction_bias(self, attn_scores: torch.Tensor) -> torch.Tensor:
        """
        Build additive eviction bias from attention scores [B, H, T_q, T_k].
        Returns bias with 0 for kept tokens and -inf for evicted tokens.
        """
        with torch.no_grad():
            importance = attn_scores.detach().sum(dim=2)  # [B, H, T_k]
            k = max(1, int(importance.shape[-1] * self.kv_budget_ratio))
            topk_idx = importance.topk(k, dim=-1).indices  # [B, H, k]
            # Start with all -inf, set kept positions to 0
            bias = torch.full_like(importance, float('-inf'))
            bias.scatter_(-1, topk_idx, 0.0)
        return bias.unsqueeze(2)  # [B, H, 1, T_k] — broadcasts over T_q

    def register(self, model):
        """Register hooks on all GPT2Attention modules."""
        from transformers.models.gpt2.modeling_gpt2 import GPT2Attention

        for name, module in model.named_modules():
            if isinstance(module, GPT2Attention):
                hook = module.register_forward_hook(self._hook_fn)
                self._hooks.append(hook)
        logger.info(f"  H2O hooks registered on {len(self._hooks)} attention layers")

    def _hook_fn(self, module, inputs, output):
        """
        Re-compute attention output with H2O eviction mask applied at logit level.
        GPT2Attention forward returns (attn_output, present[, attn_weights]).
        """
        if not module.training:
            return output

        hidden_states = inputs[0]
        attention_mask = inputs[2] if len(inputs) > 2 else None

        bsz, tgt_len, embed_dim = hidden_states.shape
        head_dim = embed_dim // module.num_heads

        # Re-compute Q, K, V from the module's c_attn (includes LoRA parameters)
        qkv = module.c_attn(hidden_states)
        query, key, value = qkv.split(module.split_size, dim=2)

        def split_heads(x):
            new_shape = x.size()[:-1] + (module.num_heads, head_dim)
            return x.view(new_shape).permute(0, 2, 1, 3)  # [B, H, T, d]

        q = split_heads(query)
        k = split_heads(key)
        v = split_heads(value)

        # Scaled dot-product attention scores
        attn_scores = torch.matmul(q, k.transpose(-2, -1)) / (head_dim ** 0.5)

        # Apply causal mask if provided
        if attention_mask is not None:
            attn_scores = attn_scores + attention_mask

        # Apply H2O eviction mask at logit level (before softmax)
        eviction_bias = self._build_eviction_bias(attn_scores)
        attn_scores = attn_scores + eviction_bias

        attn_weights = F.softmax(attn_scores, dim=-1)
        attn_weights = F.dropout(attn_weights, p=module.attn_dropout.p, training=module.training)

        # Recompute output from masked attention
        attn_output = torch.matmul(attn_weights, v)  # [B, H, T_q, d]
        attn_output = attn_output.permute(0, 2, 1, 3).contiguous()
        attn_output = attn_output.view(bsz, tgt_len, embed_dim)
        attn_output = module.c_proj(attn_output)
        attn_output = module.resid_dropout(attn_output)

        # Return in same format as original output tuple
        present = output[1] if len(output) > 1 else None
        if present is not None:
            return (attn_output, present) + output[2:]
        return (attn_output,) + output[1:]

    def remove(self):
        for h in self._hooks:
            h.remove()
        self._hooks.clear()


class LongAlpacaDataset:
    """Loads LongAlpaca-12k from HuggingFace Hub and tokenizes for causal LM training."""

    def __init__(self, tokenizer, max_len=512, n_samples=200):
        from datasets import load_dataset
        logger.info("Loading LongAlpaca-12k from Yukang/LongAlpaca-12k ...")
        ds = load_dataset("Yukang/LongAlpaca-12k", split="train")
        logger.info(f"  Dataset loaded: {len(ds)} samples")

        self.data = []
        for i, example in enumerate(ds):
            if len(self.data) >= n_samples:
                break
            instruction = example.get("instruction", "")
            output = example.get("output", "")
            text = f"### Instruction:\n{instruction}\n\n### Response:\n{output}"
            enc = tokenizer(
                text,
                truncation=True,
                max_length=max_len,
                padding="max_length",
                return_tensors="pt",
            )
            ids = enc["input_ids"].squeeze()
            self.data.append({"input_ids": ids, "labels": ids.clone()})

        logger.info(f"  Tokenized {len(self.data)} samples (max_len={max_len})")

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        return self.data[idx]


def run_smoke_test():
    from transformers import AutoTokenizer, AutoModelForCausalLM, Trainer, TrainingArguments
    from peft import LoraConfig, get_peft_model

    MODEL_NAME = "gpt2"
    device = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info(f"Device: {device}")
    logger.info(f"Model: {MODEL_NAME} (smoke test proxy for LLaMA-2-7B / Mistral-7B)")

    lora_cfg = LoraConfig(
        r=8, lora_alpha=16, lora_dropout=0.05,
        target_modules=["c_attn"],
        task_type="CAUSAL_LM",
    )

    # Load tokenizer once and build dataset from real LongAlpaca-12k
    logger.info("Preparing LongAlpaca-12k dataset ...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    tokenizer.pad_token = tokenizer.eos_token
    dataset = LongAlpacaDataset(tokenizer, max_len=128, n_samples=200)

    def train_condition(condition, output_dir, num_steps=30):
        logger.info(f"  Loading {MODEL_NAME} for condition={condition}")

        model = AutoModelForCausalLM.from_pretrained(MODEL_NAME)
        model.config.use_cache = False

        peft_model = get_peft_model(model, lora_cfg)
        peft_model.print_trainable_parameters()

        h2o_hook = None
        if condition == "eviction-aware":
            h2o_hook = H2OAttentionHook(kv_budget_ratio=0.5)
            h2o_hook.register(peft_model)

        args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=1,
            max_steps=num_steps,
            per_device_train_batch_size=4,
            gradient_accumulation_steps=1,
            learning_rate=2e-4,
            fp16=(device == "cuda"),
            logging_steps=10,
            save_strategy="no",
            report_to="none",
            remove_unused_columns=False,
            dataloader_num_workers=0,
            seed=42,
        )

        trainer = Trainer(
            model=peft_model,
            args=args,
            train_dataset=dataset,
        )

        logger.info(f"Starting training: condition={condition}")
        trainer.train()

        if h2o_hook is not None:
            h2o_hook.remove()

        adapter_path = os.path.join(output_dir, "adapter")
        peft_model.save_pretrained(adapter_path)
        tokenizer.save_pretrained(adapter_path)
        logger.info(f"  Adapter saved: {adapter_path}")
        return adapter_path

    # ── Run baseline ────────────────────────────────────────────────────────
    logger.info("=== Training BASELINE (no H2O mask) ===")
    baseline_dir = train_condition("baseline", str(OUTPUTS_DIR / "gpt2-baseline"))

    # ── Run eviction-aware ──────────────────────────────────────────────────
    logger.info("=== Training EVICTION-AWARE (H2O mask r=0.5) ===")
    eviction_dir = train_condition("eviction-aware", str(OUTPUTS_DIR / "gpt2-eviction-aware"))

    # ── Compute cosine similarity ───────────────────────────────────────────
    logger.info("=== Computing LoRA weight cosine similarities ===")

    def load_lora_weights(adapter_path):
        sf_path = os.path.join(adapter_path, "adapter_model.safetensors")
        if os.path.exists(sf_path):
            import safetensors.torch as st
            return st.load_file(sf_path)
        bin_path = os.path.join(adapter_path, "adapter_model.bin")
        return torch.load(bin_path, map_location="cpu")

    baseline_sd = load_lora_weights(baseline_dir)
    eviction_sd = load_lora_weights(eviction_dir)

    cosine_results = {}
    for key in baseline_sd:
        if key in eviction_sd and baseline_sd[key].ndim >= 1:
            a = baseline_sd[key].float().flatten()
            b = eviction_sd[key].float().flatten()
            if a.norm() > 1e-9 and b.norm() > 1e-9:
                sim = F.cosine_similarity(a.unsqueeze(0), b.unsqueeze(0)).item()
                cosine_results[key] = sim

    if not cosine_results:
        logger.error("No matching LoRA weight keys found!")
        sys.exit(1)

    sims = list(cosine_results.values())
    min_sim = min(sims)
    mean_sim = sum(sims) / len(sims)
    layers_below = [k for k, v in cosine_results.items() if v < 0.95]
    gate_pass = min_sim < 0.95

    logger.info(f"  Layers compared: {len(sims)}")
    logger.info(f"  Min cosine similarity: {min_sim:.4f}")
    logger.info(f"  Mean cosine similarity: {mean_sim:.4f}")
    logger.info(f"  Layers below 0.95 threshold: {len(layers_below)}")
    logger.info(f"  Gate (min < 0.95): {'PASS' if gate_pass else 'FAIL'}")

    # ── Generate figure ─────────────────────────────────────────────────────
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        keys_short = [k.replace("base_model.model.", "").replace(".weight", "") for k in cosine_results]
        vals = list(cosine_results.values())
        colors = ["red" if v < 0.95 else "steelblue" for v in vals]

        fig, ax = plt.subplots(figsize=(max(8, len(keys_short) * 0.8), 5))
        ax.bar(range(len(vals)), vals, color=colors, alpha=0.8)
        ax.axhline(0.95, color="red", linestyle="--", label="Threshold (0.95)")
        ax.set_xticks(range(len(keys_short)))
        ax.set_xticklabels(keys_short, rotation=45, ha="right", fontsize=7)
        ax.set_ylim(0, 1.05)
        ax.set_ylabel("Cosine Similarity")
        ax.set_title(
            f"H-E1: LoRA Weight Cosine Similarity (Baseline vs Eviction-Aware)\n"
            f"GPT-2 Smoke Test | LongAlpaca-12k | min={min_sim:.4f} | gate={'PASS' if gate_pass else 'FAIL'}"
        )
        ax.legend()
        plt.tight_layout()
        fig_path = FIGURES_DIR / "cosine_similarity_smoke_test.png"
        fig.savefig(str(fig_path), dpi=100)
        plt.close()
        logger.info(f"  Figure saved: {fig_path}")
    except Exception as e:
        logger.warning(f"Figure generation failed: {e}")
        fig_path = None

    # ── Save results ────────────────────────────────────────────────────────
    results = {
        "hypothesis_id": "h-e1",
        "execution_mode": "smoke_test",
        "model_name": MODEL_NAME,
        "dataset": "Yukang/LongAlpaca-12k",
        "note": "GPT-2 proxy for LLaMA-2-7B/Mistral-7B (PoC MUST_WORK gate); real LongAlpaca-12k dataset",
        "gate_result": "PASS" if gate_pass else "FAIL",
        "gate_type": "MUST_WORK",
        "gate_criterion": "min(cosine_similarity) < 0.95",
        "status": "completed",
        "metrics": {
            "min_cosine_similarity": min_sim,
            "mean_cosine_similarity": mean_sim,
            "layers_compared": len(sims),
            "layers_below_threshold": len(layers_below),
            "gate_pass": gate_pass,
        },
        "cosine_similarity_per_layer": cosine_results,
        "model_proxy": {
            "used": MODEL_NAME,
            "reason": "Full 7B model training requires >4h; GPT-2 validates the H2O mechanism",
            "mechanism_equivalent": True,
        },
        "training": {
            "baseline_adapter": baseline_dir,
            "eviction_adapter": eviction_dir,
            "num_steps": 30,
            "batch_size": 4,
            "learning_rate": 2e-4,
            "kv_budget_ratio": 0.5,
        },
        "timestamp": datetime.now().isoformat(),
    }

    results_path = HYP_FOLDER / "experiment_results.json"
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    logger.info(f"Results saved: {results_path}")

    # ── CSV for pipeline ─────────────────────────────────────────────────────
    csv_dirs = [
        OUTPUTS_DIR / "outputs",
        Path("docs/youra_research/20260504_scope/h-e1/code/outputs"),
    ]
    for csv_dir in csv_dirs:
        csv_dir.mkdir(parents=True, exist_ok=True)
        csv_path = csv_dir / "results.csv"
        with open(csv_path, "w") as f:
            f.write("layer,cosine_similarity,below_threshold\n")
            for k, v in cosine_results.items():
                f.write(f"{k},{v:.6f},{int(v < 0.95)}\n")
    logger.info(f"CSV saved to outputs/")

    # ── Experiment log ───────────────────────────────────────────────────────
    log_dir = OUTPUTS_DIR
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "experiment.log"
    with open(log_path, "w") as f:
        f.write(f"H-E1 Smoke Test Experiment Log\n")
        f.write(f"Timestamp: {results['timestamp']}\n")
        f.write(f"Model: {MODEL_NAME}\n")
        f.write(f"Dataset: Yukang/LongAlpaca-12k\n")
        f.write(f"Gate: {'PASS' if gate_pass else 'FAIL'}\n")
        f.write(f"Min cosine similarity: {min_sim:.4f}\n")
        f.write(f"Layers compared: {len(sims)}\n")

    logger.info("=" * 60)
    logger.info("SMOKE TEST COMPLETE")
    logger.info(f"Gate: {'PASS' if gate_pass else 'FAIL'}")
    logger.info(f"Min cosine similarity: {min_sim:.4f} (threshold < 0.95)")
    logger.info("=" * 60)

    return results


if __name__ == "__main__":
    results = run_smoke_test()
    sys.exit(0 if results["gate_result"] == "PASS" else 1)
