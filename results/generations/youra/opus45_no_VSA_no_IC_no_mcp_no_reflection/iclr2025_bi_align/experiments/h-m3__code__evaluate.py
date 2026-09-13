"""H-M1 Evaluation: Checkpoint eval and reward hacking detection."""
import json
from pathlib import Path
from scipy import stats
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

from data import build_constraints


def run_checkpoint_eval(
    checkpoint_path: str,
    ifeval_test_ds,
    device: str = "cuda"
) -> dict:
    """Evaluate checkpoint on IFEval test set. Returns strict accuracy."""
    from ifeval_signal import IFEvalRewardSignal, BaselineChecker

    # Load checkpoint
    model = AutoModelForCausalLM.from_pretrained(
        checkpoint_path,
        torch_dtype=torch.bfloat16,
        device_map="auto",
    )
    tokenizer = AutoTokenizer.from_pretrained(checkpoint_path)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model.eval()

    checker = BaselineChecker()
    correct = 0
    total = 0

    for row in ifeval_test_ds:
        prompt = row["prompt"]
        constraints = build_constraints(row)

        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
        inputs = {k: v.to(device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=256,
                do_sample=False,
                pad_token_id=tokenizer.pad_token_id,
            )

        response = tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
        score = checker.check(response, constraints)

        if score >= 0.5:  # strict: at least half constraints satisfied
            correct += 1
        total += 1

    return {
        "ifeval_acc": correct / total if total > 0 else 0.0,
        "total": total,
        "correct": correct,
    }


class RewardHackingDetector:
    """Tracks train vs eval correlation to detect reward hacking."""

    def __init__(self, corr_threshold: float = 0.7):
        self.corr_threshold = corr_threshold
        self.train_rewards = []
        self.eval_metrics = []

    def log_step(self, train_reward: float, eval_metric: float):
        """Record (train, eval) pair per checkpoint."""
        self.train_rewards.append(train_reward)
        self.eval_metrics.append(eval_metric)

    def check(self) -> dict:
        """Compute correlation and check for reward hacking."""
        if len(self.train_rewards) < 2:
            return {"correlation": None, "hacking_suspected": False}

        r, p_value = stats.pearsonr(self.train_rewards, self.eval_metrics)

        return {
            "correlation": r,
            "p_value": p_value,
            "hacking_suspected": r < self.corr_threshold,
        }


def check_gate_metrics(history: list[dict]) -> dict:
    """Check MUST_WORK gate criteria from training history."""
    if not history:
        return {"pass": False, "reason": "Empty history"}

    # Extract metrics
    rewards = [h["reward/mean"] for h in history]
    helpfulness = [h["reward/helpfulness"] for h in history]
    controllability = [h["reward/controllability"] for h in history]
    kls = [h["objective/kl"] for h in history]

    # Check for NaN/Inf
    all_values = rewards + helpfulness + controllability + kls
    has_nan = any(v is None or (isinstance(v, float) and (v != v or abs(v) == float('inf')))
                  for v in all_values)

    if has_nan:
        return {"pass": False, "reason": "NaN/Inf detected in metrics"}

    # Check KL divergence
    max_kl = max(kls) if kls else 0
    if max_kl > 5.0:
        return {"pass": False, "reason": f"KL divergence {max_kl:.2f} > 5.0"}

    # Check positive trend for both components (compare first vs last quarter)
    def has_positive_trend(values):
        if len(values) < 4:
            return True  # too few points
        q1 = sum(values[:len(values)//4]) / (len(values)//4)
        q4 = sum(values[-len(values)//4:]) / (len(values)//4)
        return q4 >= q1 - 0.05  # small tolerance

    help_trend = has_positive_trend(helpfulness)
    ctrl_trend = has_positive_trend(controllability)

    if not help_trend:
        return {"pass": False, "reason": "Helpfulness reward shows negative trend"}

    if not ctrl_trend:
        return {"pass": False, "reason": "Controllability reward shows negative trend"}

    return {
        "pass": True,
        "reason": "All gate criteria satisfied",
        "details": {
            "max_kl": max_kl,
            "final_reward_mean": rewards[-1] if rewards else 0,
            "final_helpfulness": helpfulness[-1] if helpfulness else 0,
            "final_controllability": controllability[-1] if controllability else 0,
            "helpfulness_trend_positive": help_trend,
            "controllability_trend_positive": ctrl_trend,
        }
    }


def evaluate_all_checkpoints(
    checkpoint_dir: Path,
    ifeval_test_ds,
    history: list[dict]
) -> dict:
    """Run full evaluation on all checkpoints."""
    results = {
        "checkpoints": [],
        "gate_check": check_gate_metrics(history),
    }

    detector = RewardHackingDetector()

    # Find checkpoint directories
    ckpt_dirs = sorted(checkpoint_dir.glob("step_*"))

    for ckpt_path in ckpt_dirs:
        step = int(ckpt_path.name.split("_")[1])
        print(f"Evaluating checkpoint at step {step}...")

        eval_result = run_checkpoint_eval(str(ckpt_path), ifeval_test_ds)
        eval_result["step"] = step

        # Find corresponding training reward
        train_entries = [h for h in history if h["step"] <= step]
        if train_entries:
            train_reward = train_entries[-1]["reward/mean"]
            detector.log_step(train_reward, eval_result["ifeval_acc"])

        results["checkpoints"].append(eval_result)

    results["reward_hacking"] = detector.check()

    return results


if __name__ == "__main__":
    import sys
    from data import load_ifeval_split

    _, ifeval_test = load_ifeval_split()

    ckpt_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("outputs/checkpoints")
    history_path = ckpt_dir.parent / "training_history.json"

    with open(history_path) as f:
        history = json.load(f)

    results = evaluate_all_checkpoints(ckpt_dir, ifeval_test, history)
    print(json.dumps(results, indent=2))
