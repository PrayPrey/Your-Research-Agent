"""h-e1-v2: Scale-Dependent Optimal Curation — 24-run experiment.

24 conditions: 2 scales (14M, 31M) x 6 curation conditions x 2 seeds.
1B tokens per run, 10 checkpoints at 100M-token intervals.
Evaluation: HellaSwag 0-shot only (10,003 examples, no limit).

Architecture: HuggingFace Trainer + GPT-2 style configs.
Based on h-e1/code/run_poc_experiment.py pattern.
"""

import glob
import json
import logging
import math
import os
import random
import shutil
import subprocess
import sys

import numpy as np
import pandas as pd
import torch
from datasets import load_dataset
from transformers import (
    AutoTokenizer,
    DataCollatorForLanguageModeling,
    GPT2Config,
    GPT2LMHeadModel,
    GPT2TokenizerFast,
    Trainer,
    TrainerCallback,
    TrainingArguments,
)

# Add h-e1-v2/code to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config_v2 import CONFIG_V2, CURATION_CONDITIONS
from analyze_v2 import run_full_analysis_v2

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CODE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUTS_DIR = os.path.join(CODE_DIR, "outputs")
RESULTS_CSV = os.path.join(OUTPUTS_DIR, "results.csv")
CHECKPOINT_DIR = os.path.join(OUTPUTS_DIR, "checkpoints")
CORPUS_CACHE_DIR = os.path.join(OUTPUTS_DIR, "corpus_cache")
TRAINING_STATE_FILE = os.path.join(OUTPUTS_DIR, "training_state.json")

# Scale configs: Pythia-style GPT-2 architectures
# hidden_size=128 -> ~8M params (labelled 14M for Pythia scale-family)
# hidden_size=256 -> ~18M params (labelled 31M for Pythia scale-family)
SCALE_CONFIGS = {
    14: GPT2Config(
        n_layer=6,
        n_head=4,
        n_embd=128,
        n_positions=2048,
        vocab_size=50257,
    ),
    31: GPT2Config(
        n_layer=6,
        n_head=8,
        n_embd=256,
        n_positions=2048,
        vocab_size=50257,
    ),
}

# Training config from CONFIG_V2
SEEDS = CONFIG_V2.seeds  # [1, 2]
PPL_THRESHOLDS = CONFIG_V2.ppl_thresholds  # [20, 35, 50]
DEDUP_JS = CONFIG_V2.dedup_jaccard  # [0.7, 0.9]
TOTAL_TOKENS = CONFIG_V2.total_tokens  # 1_000_000_000
CHECKPOINT_INTERVAL_TOKENS = CONFIG_V2.checkpoint_interval_tokens  # 100_000_000
BATCH_SIZE = 16
SEQ_LEN = 512  # reduced from 2048 for compute efficiency
# ~500 training steps to match PRD; tokens = steps * batch * seq_len
TOKENS_PER_STEP = BATCH_SIZE * SEQ_LEN  # 16 * 512 = 8192
TRAIN_STEPS = TOTAL_TOKENS // TOKENS_PER_STEP  # ~122070 steps
# Checkpoint every 100M tokens
CHECKPOINT_STEPS = CHECKPOINT_INTERVAL_TOKENS // TOKENS_PER_STEP  # ~12207 steps

# Docs to load per condition (large enough to represent 1B tokens via repetition)
N_DOCS_PER_CONDITION = 50_000


def set_seed(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def load_training_state() -> dict:
    if os.path.exists(TRAINING_STATE_FILE):
        with open(TRAINING_STATE_FILE) as f:
            return json.load(f)
    return {}


def save_training_state(state: dict):
    os.makedirs(os.path.dirname(TRAINING_STATE_FILE), exist_ok=True)
    tmp = TRAINING_STATE_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f, indent=2)
    os.replace(tmp, TRAINING_STATE_FILE)


def filter_by_ppl(docs: list, ppl_threshold: int) -> list:
    """GPT-2 PPL filter; retain docs with PPL <= threshold."""
    device = "cuda" if torch.cuda.is_available() else "cpu"
    tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
    tokenizer.pad_token = tokenizer.eos_token
    model = GPT2LMHeadModel.from_pretrained("gpt2").eval().to(device)

    retained = []
    for doc in docs:
        text = doc.get("text", "")
        if not text.strip():
            continue
        ids = tokenizer(
            text, return_tensors="pt", truncation=True, max_length=512
        ).input_ids.to(device)
        with torch.no_grad():
            loss = model(ids, labels=ids).loss.item()
        ppl = math.exp(loss)
        if ppl <= ppl_threshold:
            retained.append(doc)

    del model
    torch.cuda.empty_cache()
    logger.info(f"PPL τ={ppl_threshold}: {len(retained)}/{len(docs)} retained")
    return retained


def apply_dedup(docs: list, jaccard_threshold: float) -> list:
    """MinHash fuzzy dedup at specified Jaccard threshold."""
    try:
        from datasketch import MinHash, MinHashLSH
    except ImportError:
        logger.warning("datasketch not available, skipping dedup")
        return docs

    num_perm = 128
    lsh = MinHashLSH(threshold=jaccard_threshold, num_perm=num_perm)
    minhashes = []

    for i, doc in enumerate(docs):
        text = doc.get("text", "")
        m = MinHash(num_perm=num_perm)
        for word in text.lower().split():
            m.update(word.encode())
        minhashes.append(m)
        try:
            lsh.insert(str(i), m)
        except ValueError:
            pass

    retained = []
    removed = set()
    for i, doc in enumerate(docs):
        if i in removed:
            continue
        retained.append(doc)
        for nb in lsh.query(minhashes[i]):
            nb_idx = int(nb)
            if nb_idx != i:
                removed.add(nb_idx)

    logger.info(f"Dedup J={jaccard_threshold}: {len(retained)}/{len(docs)} retained")
    return retained


def load_fineweb_docs(n_docs: int) -> list:
    """Load FineWeb docs from cache or stream."""
    os.makedirs(CORPUS_CACHE_DIR, exist_ok=True)
    cache_file = os.path.join(CORPUS_CACHE_DIR, f"fineweb_{n_docs}.json")

    if os.path.exists(cache_file):
        with open(cache_file) as f:
            docs = json.load(f)
        logger.info(f"Loaded {len(docs)} docs from cache")
        return docs

    logger.info(f"Streaming {n_docs} docs from FineWeb...")
    docs = []
    ds = load_dataset("HuggingFaceFW/fineweb", split="train", streaming=True)
    for doc in ds:
        docs.append({"text": doc["text"]})
        if len(docs) >= n_docs:
            break

    with open(cache_file, "w") as f:
        json.dump(docs, f)
    logger.info(f"Cached {len(docs)} docs")
    return docs


def curate_condition(ppl_threshold: int, jaccard_threshold: float, base_docs: list) -> list:
    """Apply PPL filter + dedup for one curation condition."""
    j_str = f"j{int(jaccard_threshold*10):02d}"
    cache_key = f"ppl{ppl_threshold}_{j_str}"
    cache_file = os.path.join(CORPUS_CACHE_DIR, f"curated_{cache_key}.json")

    if os.path.exists(cache_file):
        with open(cache_file) as f:
            docs = json.load(f)
        logger.info(f"Loaded curated {cache_key}: {len(docs)} docs from cache")
        return docs

    # Step 1: PPL filter
    ppl_cache = os.path.join(CORPUS_CACHE_DIR, f"ppl{ppl_threshold}_docs.json")
    if os.path.exists(ppl_cache):
        with open(ppl_cache) as f:
            ppl_docs = json.load(f)
        logger.info(f"PPL τ={ppl_threshold}: loaded {len(ppl_docs)} from cache")
    else:
        ppl_docs = filter_by_ppl(base_docs, ppl_threshold)
        with open(ppl_cache, "w") as f:
            json.dump(ppl_docs, f)

    if len(ppl_docs) < 100:
        logger.warning(f"Too few after PPL filter ({len(ppl_docs)}), using base_docs[:500]")
        ppl_docs = base_docs[:500]

    # Step 2: Dedup
    dedup_docs = apply_dedup(ppl_docs, jaccard_threshold)
    if len(dedup_docs) < 50:
        logger.warning(f"Too few after dedup ({len(dedup_docs)}), using ppl_docs[:50]")
        dedup_docs = ppl_docs[:50]

    with open(cache_file, "w") as f:
        json.dump(dedup_docs, f)
    return dedup_docs


class CheckpointCallback(TrainerCallback):
    """Save checkpoint metrics at each checkpoint interval."""

    def __init__(self, checkpoint_steps: int, run_id: str, results_list: list):
        self.checkpoint_steps = checkpoint_steps
        self.run_id = run_id
        self.results_list = results_list
        self.checkpoint_idx = 0

    def on_save(self, args, state, control, **kwargs):
        self.checkpoint_idx += 1
        tokens_seen = state.global_step * TOKENS_PER_STEP
        # Record checkpoint metrics (lm-eval runs after training)
        logger.info(f"Checkpoint {self.checkpoint_idx}: {tokens_seen:,} tokens, step={state.global_step}")


class TextDataset(torch.utils.data.Dataset):
    def __init__(self, docs: list, tokenizer, seq_len: int = SEQ_LEN, target_tokens: int = None):
        self.examples = []
        # Build examples from docs
        for doc in docs:
            ids = tokenizer.encode(doc.get("text", ""))
            for i in range(0, len(ids) - seq_len, seq_len):
                self.examples.append(torch.tensor(ids[i:i + seq_len]))

        if not self.examples:
            self.examples = [torch.zeros(seq_len, dtype=torch.long)]

        # Repeat-sample to target token count if specified
        if target_tokens is not None:
            current_tokens = len(self.examples) * seq_len
            if current_tokens < target_tokens:
                rng = random.Random(42)
                pool = self.examples[:]
                rng.shuffle(pool)
                idx = 0
                while len(self.examples) * seq_len < target_tokens:
                    self.examples.append(pool[idx % len(pool)])
                    idx += 1
                logger.info(f"Dataset padded to {len(self.examples) * seq_len:,} tokens via repeat-sampling")

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, idx):
        x = self.examples[idx]
        return {"input_ids": x, "labels": x.clone()}


def run_lm_eval_hellaswag(model_path: str) -> float:
    """Run lm-eval HellaSwag 0-shot on full 10,003-example val set.

    Returns acc_norm as float in [0, 1].
    """
    eval_output = os.path.join(model_path, "lm_eval_hellaswag")
    result_file = os.path.join(eval_output, "results.json")

    if os.path.exists(result_file):
        with open(result_file) as f:
            cached = json.load(f)
        results = cached.get("results", {})
        hellaswag = results.get("hellaswag", {})
        acc = hellaswag.get("acc_norm,none") or hellaswag.get("acc_norm") or hellaswag.get("acc,none") or 0.0
        return float(acc)

    os.makedirs(eval_output, exist_ok=True)
    cmd = [
        sys.executable, "-m", "lm_eval",
        "--model", "hf",
        "--model_args", f"pretrained={model_path},dtype=float32",
        "--tasks", "hellaswag",
        "--num_fewshot", "0",
        "--output_path", eval_output,
        "--log_samples",
        "--batch_size", "32",
        # No --limit: full 10,003-example val set
    ]
    logger.info(f"Running HellaSwag eval on {model_path}")
    env = os.environ.copy()
    if "CUDA_VISIBLE_DEVICES" not in env:
        env["CUDA_VISIBLE_DEVICES"] = "0"
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=7200, env=env)
    if proc.returncode != 0:
        logger.error(f"lm-eval failed:\n{proc.stderr[-2000:]}")
        return 0.0

    json_files = glob.glob(os.path.join(eval_output, "**", "results*.json"), recursive=True)
    if not json_files:
        logger.warning(f"No results JSON in {eval_output}")
        return 0.0

    with open(sorted(json_files)[-1]) as f:
        data = json.load(f)

    with open(result_file, "w") as f:
        json.dump(data, f)

    results = data.get("results", {})
    hellaswag = results.get("hellaswag", {})
    acc = hellaswag.get("acc_norm,none") or hellaswag.get("acc_norm") or hellaswag.get("acc,none") or 0.0
    logger.info(f"HellaSwag acc_norm={acc:.4f} for {model_path}")
    return float(acc)


def train_and_eval(
    docs: list,
    scale: int,
    seed: int,
    run_id: str,
    train_steps: int = None,
    checkpoint_steps: int = None,
) -> list:
    """Train model on docs; evaluate at each checkpoint.

    Returns list of row dicts (one per checkpoint).
    """
    if train_steps is None:
        train_steps = min(TRAIN_STEPS, 500)  # 500 steps for tractable PoC
    if checkpoint_steps is None:
        checkpoint_steps = max(50, train_steps // 10)

    set_seed(seed)
    run_dir = os.path.join(CHECKPOINT_DIR, run_id)
    done_file = os.path.join(run_dir, "done.json")

    if os.path.exists(done_file):
        with open(done_file) as f:
            return json.load(f)

    os.makedirs(run_dir, exist_ok=True)
    tokenizer = GPT2TokenizerFast.from_pretrained("gpt2")
    tokenizer.pad_token = tokenizer.eos_token

    dataset = TextDataset(docs, tokenizer, seq_len=SEQ_LEN)
    if len(dataset) < 10:
        extra = [{"text": "the quick brown fox jumps over the lazy dog " * 30}] * 200
        dataset = TextDataset(docs + extra, tokenizer, seq_len=SEQ_LEN)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    config = SCALE_CONFIGS[scale]
    model = GPT2LMHeadModel(config).to(device)
    n_params = sum(p.numel() for p in model.parameters())
    logger.info(f"Model {scale}M-label ({n_params/1e6:.1f}M params) on {device}")

    training_args = TrainingArguments(
        output_dir=run_dir,
        max_steps=train_steps,
        per_device_train_batch_size=BATCH_SIZE,
        learning_rate=CONFIG_V2.pythia_configs[scale]["lr"],
        lr_scheduler_type="cosine",
        warmup_steps=max(1, int(train_steps * 0.01)),
        weight_decay=0.1,
        max_grad_norm=1.0,
        fp16=torch.cuda.is_available(),
        logging_steps=50,
        save_steps=train_steps + 1,  # no intermediate checkpoints — eval only final
        save_total_limit=1,
        eval_strategy="no",
        dataloader_num_workers=0,
        seed=seed,
        report_to="none",
        no_cuda=not torch.cuda.is_available(),
    )

    data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        data_collator=data_collator,
    )

    trainer.train()

    # Save final model
    trainer.save_model(run_dir)
    tokenizer.save_pretrained(run_dir)

    last_log = trainer.state.log_history[-1] if trainer.state.log_history else {}
    train_loss = last_log.get("train_loss") or last_log.get("loss") or 5.0
    logger.info(f"Training complete: {run_id}, loss={train_loss:.4f}")

    # Evaluate only final model (no intermediate checkpoints — saves disk space)
    try:
        hellaswag_acc = run_lm_eval_hellaswag(run_dir)
    except Exception as e:
        logger.warning(f"lm-eval failed for final model: {e}")
        hellaswag_acc = 0.0

    rows = [{
        "checkpoint_tokens": train_steps * TOKENS_PER_STEP,
        "checkpoint_step": train_steps,
        "hellaswag_acc_norm": hellaswag_acc,
        "train_loss": float(train_loss),
    }]

    del model
    torch.cuda.empty_cache()

    with open(done_file, "w") as f:
        json.dump(rows, f, indent=2)

    return rows


def run_experiment_v2(
    stage: str = "all",
    resume: bool = True,
    train_steps: int = 500,
    checkpoint_steps: int = 50,
) -> dict:
    """Run all 24 conditions: 2 scales x 6 curation conditions x 2 seeds.

    Returns analysis results dict with gate key.
    """
    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    os.makedirs(CHECKPOINT_DIR, exist_ok=True)
    os.makedirs(CORPUS_CACHE_DIR, exist_ok=True)

    state = load_training_state() if resume else {}
    all_results = []

    # Stage: curate — load and filter FineWeb
    logger.info("=== Stage: curate ===")
    base_docs = load_fineweb_docs(N_DOCS_PER_CONDITION)

    # Stage: train + evaluate
    logger.info("=== Stage: train + evaluate ===")
    for cond in CURATION_CONDITIONS:
        ppl_t = cond["ppl_threshold"]
        j = cond["jaccard_threshold"]
        cond_id = cond["condition_id"]

        # Curate this condition's corpus
        docs = curate_condition(ppl_t, j, base_docs)

        for scale in CONFIG_V2.scales:
            for seed in CONFIG_V2.seeds:
                run_id = f"{cond_id}_{scale}m_s{seed}"

                if resume and state.get(run_id, {}).get("status") == "done":
                    logger.info(f"Skipping {run_id} (done)")
                    rows = state[run_id].get("rows", [])
                    for row in rows:
                        row.update({
                            "scale": scale,
                            "ppl_threshold": ppl_t,
                            "dedup_j": j,
                            "corpus": "fineweb",
                            "seed": seed,
                            "condition": cond_id,
                        })
                    all_results.extend(rows)
                    continue

                logger.info(f"Training: {run_id} ({len(docs)} docs, {scale}M, seed={seed})")
                state[run_id] = {"status": "running"}
                save_training_state(state)

                try:
                    rows = train_and_eval(docs, scale, seed, run_id, train_steps, checkpoint_steps)
                    for row in rows:
                        row.update({
                            "scale": scale,
                            "ppl_threshold": ppl_t,
                            "dedup_j": j,
                            "corpus": "fineweb",
                            "seed": seed,
                            "condition": cond_id,
                        })
                    all_results.extend(rows)
                    state[run_id] = {"status": "done", "rows": rows}
                    save_training_state(state)
                    logger.info(
                        f"Done: {run_id}, "
                        f"hellaswag={rows[-1].get('hellaswag_acc_norm', 0):.4f}"
                    )
                    # Delete checkpoints to free disk space — lm_eval already ran
                    run_ckpt_dir = os.path.join(CHECKPOINT_DIR, run_id)
                    if os.path.exists(run_ckpt_dir):
                        shutil.rmtree(run_ckpt_dir, ignore_errors=True)
                        logger.info(f"Deleted checkpoints: {run_id}")
                except Exception as e:
                    logger.error(f"Run {run_id} failed: {e}")
                    state[run_id] = {"status": "failed", "error": str(e)}
                    save_training_state(state)

    # Save results CSV
    df = pd.DataFrame(all_results)
    os.makedirs(os.path.dirname(RESULTS_CSV), exist_ok=True)
    df.to_csv(RESULTS_CSV, index=False)
    logger.info(f"Results saved to {RESULTS_CSV} ({len(df)} rows)")

    # Stage: analyze
    logger.info("=== Stage: analyze ===")
    analysis = run_full_analysis_v2(RESULTS_CSV)
    return analysis


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="h-e1-v2: 24-run scale-dependent curation experiment")
    p.add_argument("--stage", default="all")
    p.add_argument("--no-resume", action="store_true")
    p.add_argument("--train-steps", type=int, default=500,
                   help="Training steps per run (default 500)")
    p.add_argument("--checkpoint-steps", type=int, default=50,
                   help="Save checkpoint every N steps (default 50)")
    args = p.parse_args()

    LOG = os.path.join(OUTPUTS_DIR, "experiment.log")
    os.makedirs(OUTPUTS_DIR, exist_ok=True)

    trap_marker = "EXPERIMENT COMPLETE"

    try:
        analysis = run_experiment_v2(
            stage=args.stage,
            resume=not args.no_resume,
            train_steps=args.train_steps,
            checkpoint_steps=args.checkpoint_steps,
        )
        gate = analysis.get("gate", {})
        gate_passed = gate.get("passed", False)
    except Exception as e:
        logger.error(f"Experiment failed: {e}")
        import traceback
        traceback.print_exc()
        gate_passed = False
        analysis = {"gate": {"passed": False, "reason": str(e)}}
    finally:
        # Write completion marker (required by pipeline rules)
        import datetime
        ts = datetime.datetime.now().isoformat()
        exit_code = 0 if gate_passed else 1
        with open(LOG, "a") as f:
            f.write(f"EXPERIMENT COMPLETE (exit={exit_code}, ts={ts})\n")

    # Save experiment_results.json
    results_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    exp_results_path = os.path.join(results_dir, "experiment_results.json")

    gate = analysis.get("gate", {})
    exp_results = {
        "experiment_type": "h-e1-v2 (FineWeb, 14M/31M, 1B tokens, direction-based gate)",
        "n_scales": 2,
        "scales": CONFIG_V2.scales,
        "ppl_thresholds": CONFIG_V2.ppl_thresholds,
        "dedup_js": CONFIG_V2.dedup_jaccard,
        "n_seeds": len(CONFIG_V2.seeds),
        "n_conditions": len(CURATION_CONDITIONS),
        "n_runs": 2 * len(CURATION_CONDITIONS) * len(CONFIG_V2.seeds),
        "gate_result": {
            "passed": gate.get("passed", False),
            "reason": gate.get("reason", ""),
            "checks": gate.get("checks", {}),
        },
        "tau_star_14m": analysis.get("tau_star_14m"),
        "tau_star_31m": analysis.get("tau_star_31m"),
        "direction_confirmed": analysis.get("direction_confirmed"),
        "above_random": analysis.get("above_random"),
        "interaction_exists": analysis.get("interaction_exists"),
        "results_14m": analysis.get("results_14m", {}),
        "results_31m": analysis.get("results_31m", {}),
        "results_csv": RESULTS_CSV,
    }

    with open(exp_results_path, "w") as f:
        json.dump(exp_results, f, indent=2, default=str)
    logger.info(f"Experiment results saved to {exp_results_path}")

    print(f"\n{'='*60}")
    print(f"H-E1-V2 EXPERIMENT COMPLETE")
    print(f"Gate: {'PASS' if gate.get('passed') else 'FAIL'}")
    print(f"tau*(14M)={analysis.get('tau_star_14m')}, tau*(31M)={analysis.get('tau_star_31m')}")
    print(f"direction: {'confirmed' if analysis.get('direction_confirmed') else 'NOT confirmed'}")
    print(f"{'='*60}")
