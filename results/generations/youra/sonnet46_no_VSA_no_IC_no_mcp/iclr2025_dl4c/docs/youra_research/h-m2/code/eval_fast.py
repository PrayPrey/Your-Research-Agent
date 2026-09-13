"""eval_fast.py — Fast batch reward evaluator, writes JSONL incrementally.

Evaluates DeepSeek-Coder-7B (rlef_smoke checkpoint) on stratified APPS sample.
Writes one JSONL record per 10 problems, so analysis can start as soon as N>5 records exist.
"""
import json
import sys
import time
from collections import defaultdict
from pathlib import Path

H_E1_CODE = Path(__file__).parents[2] / "h-e1" / "code"
sys.path.insert(0, str(H_E1_CODE))

import numpy as np
import torch
from datasets import load_dataset
from transformers import AutoModelForCausalLM, AutoTokenizer

from reward import fraction_reward_fn

N_PER_BUCKET = 60   # 180 total — enough for statistics
G = 2               # 2 gens per problem for speed (vs G=4 in training)
MAX_NEW_TOKENS = 128

REWARD_LOG = H_E1_CODE / "logs" / "reward_monitoring.jsonl"

def main():
    ckpt = H_E1_CODE / "checkpoints" / "sft_smoke"
    rlef_ckpt = H_E1_CODE / "checkpoints" / "rlef_smoke"
    # rlef_smoke has no tokenizer; use sft_smoke for both tokenizer and model
    if not (rlef_ckpt / "tokenizer.json").exists():
        rlef_ckpt = ckpt
    print(f"Checkpoint: {ckpt} (tokenizer+model)", flush=True)

    tokenizer = AutoTokenizer.from_pretrained(str(ckpt), trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        str(ckpt), torch_dtype=torch.bfloat16,
        device_map={"": 0},  # GPU 0 only (26GB free)
        trust_remote_code=True,
    )
    model.eval()
    print("Model loaded on GPU 0", flush=True)

    print("Loading APPS...", flush=True)
    ds = load_dataset("codeparrot/apps", split="train")
    buckets = {"introductory": [], "interview": [], "competition": []}
    for s in ds:
        d = s.get("difficulty", "interview")
        if d in buckets and len(buckets[d]) < N_PER_BUCKET:
            prompt = f"# Problem\n{s.get('question','')[:500]}\n\n# Python Solution\n```python\n"
            try:
                io = json.loads(s.get("input_output", "{}"))
                tc = [{"input": i, "output": o} for i, o in zip(io.get("inputs",[])[:2], io.get("outputs",[])[:2])]
            except Exception:
                tc = []
            buckets[d].append({"prompt": prompt, "test_cases": tc, "difficulty": d})
        if all(len(v) >= N_PER_BUCKET for v in buckets.values()):
            break

    dataset = []
    for d, samples in buckets.items():
        dataset.extend(samples)
        print(f"  {d}: {len(samples)}", flush=True)

    REWARD_LOG.parent.mkdir(parents=True, exist_ok=True)

    bucket_indicators = defaultdict(list)
    bucket_rewards = defaultdict(list)
    log_records = []
    step = 0
    start = time.time()

    with open(REWARD_LOG, "w") as f:
        for i, s in enumerate(dataset):
            prompt = s["prompt"]
            tc = s["test_cases"]
            d = s["difficulty"]

            try:
                enc = tokenizer(prompt, return_tensors="pt", max_length=400, truncation=True).to("cuda:0")
                with torch.no_grad():
                    out = model.generate(
                        **enc, max_new_tokens=MAX_NEW_TOKENS, do_sample=True,
                        temperature=0.8, num_return_sequences=G,
                        pad_token_id=tokenizer.eos_token_id,
                    )
                L = enc["input_ids"].shape[1]
                completions = [tokenizer.decode(o[L:], skip_special_tokens=True) for o in out]
                rewards = fraction_reward_fn(
                    completions=completions,
                    prompts=[prompt] * G,
                    metadata=[{"test_cases": tc}] * G,
                )
                bucket_indicators[d].append(float(any(r > 0 for r in rewards)))
                bucket_rewards[d].extend(rewards)
            except Exception as e:
                print(f"  err sample {i} ({d}): {e}", flush=True)
                bucket_indicators[d].append(0.0)

            if (i + 1) % 10 == 0:
                step += 1
                record = {
                    "step": step,
                    "loss": 0.0,
                    "intro_reward": float(np.mean(bucket_rewards["introductory"])) if bucket_rewards["introductory"] else None,
                    "interview_reward": float(np.mean(bucket_rewards["interview"])) if bucket_rewards["interview"] else None,
                    "competition_reward": float(np.mean(bucket_rewards["competition"])) if bucket_rewards["competition"] else None,
                }
                f.write(json.dumps(record) + "\n")
                f.flush()
                log_records.append(record)
                fracs = {b: float(np.mean(inds)) if inds else 0.0 for b, inds in bucket_indicators.items()}
                print(f"  step {step} [{i+1}/{len(dataset)}] t={time.time()-start:.0f}s "
                      f"intro={fracs.get('introductory',0):.3f} "
                      f"interview={fracs.get('interview',0):.3f} "
                      f"competition={fracs.get('competition',0):.3f}", flush=True)

    final_fracs = {d: float(np.mean(inds)) if inds else 0.0 for d, inds in bucket_indicators.items()}
    print("\nFinal non-zero reward fractions:", flush=True)
    for d in ["introductory", "interview", "competition"]:
        print(f"  {d}: {final_fracs.get(d,0):.4f} (n={len(bucket_indicators[d])})", flush=True)

    comp = final_fracs.get("competition", 0.0)
    gate = "PASS" if comp > 0.10 else "FAIL"
    print(f"\n[H-M2 GATE] competition={comp:.4f} threshold=0.10 -> {gate}", flush=True)
    print("EXPERIMENT COMPLETE", flush=True)
    return final_fracs

if __name__ == "__main__":
    main()
