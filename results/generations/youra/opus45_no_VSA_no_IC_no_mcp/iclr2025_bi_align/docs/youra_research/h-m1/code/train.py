"""Training loop for H-M1 reward model."""
import os
from transformers import TrainerCallback
from trl import RewardTrainer

from config import HM1Config, get_reward_config, set_seed
from data import load_hh_rlhf_splits, preprocess_for_reward_trainer
from model import load_tokenizer, build_reward_model


class SaveAtStepsCallback(TrainerCallback):
    """Save model at specific steps."""
    def __init__(self, steps, output_dir):
        self.steps = set(steps)
        self.output_dir = output_dir

    def on_step_end(self, args, state, control, **kwargs):
        if state.global_step in self.steps:
            checkpoint_dir = os.path.join(self.output_dir, f"checkpoint-{state.global_step}")
            kwargs["model"].save_pretrained(checkpoint_dir)
            print(f"Saved checkpoint at step {state.global_step}")


def build_trainer(cfg, model, tokenizer, train_ds, val_ds):
    """Build RewardTrainer with config."""
    reward_config = get_reward_config(cfg)

    trainer = RewardTrainer(
        model=model,
        processing_class=tokenizer,
        args=reward_config,
        train_dataset=train_ds,
        eval_dataset=val_ds,
    )
    return trainer


def run_training(cfg: HM1Config) -> str:
    """Run full training pipeline. Returns final checkpoint path."""
    set_seed(cfg.seed)

    print("Loading tokenizer...")
    tokenizer = load_tokenizer(cfg)

    print("Loading dataset...")
    splits = load_hh_rlhf_splits(cfg, tokenizer)

    # TRL RewardTrainer expects raw text columns 'chosen'/'rejected'
    train_ds = splits["train"]
    val_ds = splits["validation"]

    print("Building model...")
    model = build_reward_model(cfg, use_lora=True)

    print("Building trainer...")
    trainer = build_trainer(cfg, model, tokenizer, train_ds, val_ds)

    checkpoint_cb = SaveAtStepsCallback(cfg.checkpoint_steps, cfg.output_dir)
    trainer.add_callback(checkpoint_cb)

    print("Starting training...")
    trainer.train()

    final_path = os.path.join(cfg.output_dir, "final")
    trainer.save_model(final_path)
    tokenizer.save_pretrained(final_path)
    print(f"Saved final model to {final_path}")

    return final_path


if __name__ == "__main__":
    cfg = HM1Config()
    run_training(cfg)
