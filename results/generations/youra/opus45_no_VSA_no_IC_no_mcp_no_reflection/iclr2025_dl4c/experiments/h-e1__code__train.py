"""PPO training loop for reward bandwidth experiment using REINFORCE-style updates."""
import os
import json
import random
import torch
import torch.nn.functional as F
import numpy as np
from datasets import load_dataset
from transformers import AutoTokenizer, AutoModelForCausalLM
from torch.optim import AdamW
from tqdm import tqdm

from config import ExperimentConfig, REWARD_CONDITIONS, SEEDS
from reward import compute_reward


def set_seed(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def load_mbpp_train():
    ds = load_dataset("google-research-datasets/mbpp", "sanitized", split="train")
    return ds


def load_mbpp_val():
    ds = load_dataset("google-research-datasets/mbpp", "sanitized", split="validation")
    return ds.select(range(min(50, len(ds))))


def format_prompt(problem: dict) -> str:
    return f"""### Instruction:
Write a Python function to solve the following problem.

{problem['prompt']}

### Response:
"""


def evaluate_pass_at_1(model, tokenizer, dataset, cfg: ExperimentConfig) -> float:
    model.eval()
    passed = 0
    total = len(dataset)

    device = next(model.parameters()).device

    for item in dataset:
        prompt = format_prompt(item)
        inputs = tokenizer(prompt, return_tensors="pt").to(device)

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=cfg.max_new_tokens,
                do_sample=False,
                pad_token_id=tokenizer.pad_token_id
            )

        code = tokenizer.decode(outputs[0], skip_special_tokens=True)
        code = code.split("### Response:")[-1].strip() if "### Response:" in code else code

        try:
            from reward import execute_tests
            results = execute_tests(code, item["test_list"], timeout=cfg.test_timeout_s)
            if all(r.passed for r in results):
                passed += 1
        except Exception:
            pass

    model.train()
    return passed / total if total > 0 else 0.0


def compute_policy_gradient_loss(model, tokenizer, prompt, response, reward, device):
    """Compute REINFORCE-style policy gradient loss."""
    full_text = prompt + response
    prompt_ids = tokenizer(prompt, return_tensors="pt").input_ids.to(device)
    full_ids = tokenizer(full_text, return_tensors="pt").input_ids.to(device)

    prompt_len = prompt_ids.shape[1]

    with torch.no_grad():
        baseline = 0.5

    outputs = model(full_ids, labels=full_ids)
    logits = outputs.logits

    shift_logits = logits[:, prompt_len-1:-1, :]
    shift_labels = full_ids[:, prompt_len:]

    log_probs = F.log_softmax(shift_logits, dim=-1)
    selected_log_probs = log_probs.gather(2, shift_labels.unsqueeze(-1)).squeeze(-1)

    advantage = reward - baseline
    loss = -selected_log_probs.mean() * advantage

    return loss


def run_condition(condition: str, seed: int, cfg: ExperimentConfig) -> dict:
    set_seed(seed)
    cfg.condition = condition
    cfg.seed = seed

    print(f"\n{'='*60}")
    print(f"Training: condition={condition}, seed={seed}")
    print(f"{'='*60}")

    train_ds = load_mbpp_train()
    val_ds = load_mbpp_val()

    dtype = torch.bfloat16 if cfg.torch_dtype == "bfloat16" else torch.float32

    model = AutoModelForCausalLM.from_pretrained(
        cfg.model_id,
        torch_dtype=dtype,
        device_map="auto"
    )
    tokenizer = AutoTokenizer.from_pretrained(cfg.model_id)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    device = next(model.parameters()).device

    optimizer = AdamW(model.parameters(), lr=cfg.learning_rate)

    metric_log = []
    rewards_log = []
    n_samples = 0

    model.train()

    for epoch in range(cfg.train_epochs):
        print(f"\nEpoch {epoch + 1}/{cfg.train_epochs}")

        indices = list(range(len(train_ds)))
        random.shuffle(indices)

        pbar = tqdm(range(0, len(train_ds), cfg.batch_size), desc=f"Epoch {epoch+1}")

        for batch_start in pbar:
            batch_indices = indices[batch_start:batch_start + cfg.batch_size]
            batch_items = [train_ds[i] for i in batch_indices]

            batch_loss = 0.0
            batch_rewards = []

            for item in batch_items:
                prompt = format_prompt(item)
                inputs = tokenizer(prompt, return_tensors="pt").to(device)

                with torch.no_grad():
                    outputs = model.generate(
                        **inputs,
                        max_new_tokens=cfg.max_new_tokens,
                        do_sample=True,
                        top_p=0.9,
                        temperature=0.8,
                        pad_token_id=tokenizer.pad_token_id
                    )

                response = tokenizer.decode(outputs[0][inputs.input_ids.shape[1]:], skip_special_tokens=True)
                full_response = tokenizer.decode(outputs[0], skip_special_tokens=True)
                code = full_response.split("### Response:")[-1].strip() if "### Response:" in full_response else response

                reward = compute_reward(code, item["test_list"], condition)
                rewards_log.append(reward)
                batch_rewards.append(reward)

                loss = compute_policy_gradient_loss(model, tokenizer, prompt, response, reward, device)
                batch_loss += loss

            if len(batch_items) > 0:
                batch_loss = batch_loss / len(batch_items)
                optimizer.zero_grad()
                batch_loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()

            n_samples += len(batch_items)

            pbar.set_postfix({
                "reward": f"{np.mean(batch_rewards):.3f}",
                "loss": f"{batch_loss.item():.4f}" if torch.is_tensor(batch_loss) else "0"
            })

            if n_samples % cfg.eval_interval == 0:
                p1 = evaluate_pass_at_1(model, tokenizer, val_ds, cfg)
                metric_log.append((n_samples, p1))
                print(f"\n Samples: {n_samples}, pass@1: {p1:.4f}, mean_reward: {np.mean(rewards_log[-50:]):.4f}")
                model.train()

    checkpoint_path = os.path.join(cfg.checkpoint_dir, f"{condition}_{seed}")
    os.makedirs(checkpoint_path, exist_ok=True)
    model.save_pretrained(checkpoint_path)
    tokenizer.save_pretrained(checkpoint_path)

    final_p1 = evaluate_pass_at_1(model, tokenizer, val_ds, cfg)

    return {
        "condition": condition,
        "seed": seed,
        "metric_log": metric_log,
        "final_pass_at_1": final_p1,
        "rewards": rewards_log,
        "n_samples": n_samples
    }


def main():
    cfg = ExperimentConfig()
    all_results = {}

    for condition in REWARD_CONDITIONS:
        all_results[condition] = {}
        for seed in SEEDS:
            result = run_condition(condition, seed, cfg)
            all_results[condition][seed] = result

    os.makedirs("outputs", exist_ok=True)
    with open("outputs/results.json", "w") as f:
        json.dump(all_results, f, indent=2, default=str)

    print("\n" + "="*60)
    print("TRAINING COMPLETE")
    print("="*60)

    return all_results


if __name__ == "__main__":
    main()
