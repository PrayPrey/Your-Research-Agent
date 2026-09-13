"""End-to-end experiment orchestration for H-M1 BiDPO training stability test."""
import json
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import CONFIG, GATE, set_seed, ensure_dirs
from data import load_hh_rlhf, add_collab_scores, get_dataloader
from models import load_tokenizer, load_policy_model, load_reference_model
from train import train_loop, save_checkpoint, get_scheduler
from visualize import plot_loss_curves, plot_gradient_norm, plot_lr_schedule
from torch.optim import AdamW


def evaluate_gate(history: dict) -> dict:
    if not history or not history.get("total_loss"):
        return {
            "training_completed": False,
            "loss_decreased": False,
            "gate_passed": False,
            "reason": "Training did not produce history",
        }

    nan_count = history.get("nan_count", 0)
    training_completed = nan_count <= GATE["max_nan_inf_allowed"]

    total_losses = history["total_loss"]
    if len(total_losses) >= 2:
        warmup_idx = max(1, len(total_losses) // 10)
        initial_loss = total_losses[warmup_idx]
        final_loss = total_losses[-1]
        loss_decreased = final_loss < initial_loss
    else:
        loss_decreased = False
        initial_loss = total_losses[0] if total_losses else 0
        final_loss = total_losses[-1] if total_losses else 0

    gate_passed = training_completed and (loss_decreased if GATE["require_loss_decrease"] else True)

    return {
        "training_completed": training_completed,
        "loss_decreased": loss_decreased,
        "gate_passed": gate_passed,
        "nan_count": nan_count,
        "initial_loss": initial_loss,
        "final_loss": final_loss,
        "total_steps": history.get("final_step", 0),
    }


def main() -> None:
    print("=" * 60)
    print("H-M1: BiDPO Training Stability Test")
    print("=" * 60)

    set_seed(CONFIG.seed)
    ensure_dirs()

    print("\n[1/6] Loading tokenizer...")
    tokenizer = load_tokenizer(CONFIG.model_name)
    print(f"Tokenizer loaded: {CONFIG.model_name}")

    print("\n[2/6] Loading and preprocessing dataset...")
    train_ds = load_hh_rlhf("train", max_samples=4000)
    print(f"Dataset size (PoC subset): {len(train_ds)}")
    train_ds = add_collab_scores(train_ds)
    print(f"Collab scores added")

    dataloader = get_dataloader(train_ds, tokenizer, CONFIG.batch_size)
    num_training_steps = len(dataloader) // CONFIG.grad_accum_steps * CONFIG.epochs
    print(f"Training steps: {num_training_steps}")

    print("\n[3/6] Loading models...")
    policy_model = load_policy_model(CONFIG.model_name)
    print("Policy model loaded (trainable)")
    reference_model = load_reference_model(CONFIG.model_name)
    print("Reference model loaded (frozen)")

    print("\n[4/6] Setting up optimizer and scheduler...")
    optimizer = AdamW(policy_model.parameters(), lr=CONFIG.learning_rate)
    scheduler = get_scheduler(optimizer, num_training_steps)

    print("\n[5/6] Training...")
    history = {}
    gate = {}

    try:
        history = train_loop(
            policy_model, reference_model, dataloader,
            optimizer, scheduler, tokenizer
        )
        gate = evaluate_gate(history)
        print(f"\nGate evaluation: {gate}")
    except RuntimeError as e:
        print(f"\nTraining failed: {e}")
        gate = {
            "training_completed": False,
            "loss_decreased": False,
            "gate_passed": False,
            "error": str(e),
        }

    print("\n[6/6] Saving results and figures...")
    save_checkpoint(policy_model, f"{CONFIG.output_dir}/final.pt")

    if history and history.get("steps"):
        plot_loss_curves(history, f"{CONFIG.figures_dir}/training_loss_curves.png")
        plot_gradient_norm(history, f"{CONFIG.figures_dir}/gradient_norm.png")
        plot_lr_schedule(history, f"{CONFIG.figures_dir}/lr_schedule.png")
        print("Figures saved")

    results = {
        "hypothesis": "H-M1",
        "statement": "L_agency integrates stably with DPO loss (training completes, loss decreases)",
        "gate_type": "MUST_WORK",
        "gate": gate,
        "config": {
            "model": CONFIG.model_name,
            "beta": CONFIG.beta,
            "lambda_agency": CONFIG.lambda_agency,
            "learning_rate": CONFIG.learning_rate,
            "batch_size": CONFIG.batch_size,
            "grad_accum_steps": CONFIG.grad_accum_steps,
            "epochs": CONFIG.epochs,
        },
        "history": history,
    }

    with open(CONFIG.results_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to {CONFIG.results_path}")

    print("\n" + "=" * 60)
    if gate.get("gate_passed"):
        print("GATE PASSED: BiDPO training is stable")
    else:
        print("GATE FAILED: BiDPO training unstable")
    print("=" * 60)


if __name__ == "__main__":
    main()
