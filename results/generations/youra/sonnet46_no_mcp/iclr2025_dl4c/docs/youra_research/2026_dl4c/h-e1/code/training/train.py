"""Main training script for 4-condition GRPO curriculum experiment."""

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import CONFIG, CONDITIONS
from data.preprocessing import build_easy_pool, build_hard_pool, build_full_pool
from data.dataset import get_dataset, CurriculumDataset
from training.reward import execution_reward_fn
from training.callbacks import CurriculumCallback, RewardDensityCallback

from transformers import AutoModelForCausalLM, AutoTokenizer
from trl import GRPOTrainer, GRPOConfig


def parse_args() -> argparse.Namespace:
    """Args: --condition {curriculum,uniform,easy_only,hard_only}, --smoke_test (flag)."""
    parser = argparse.ArgumentParser(description="GRPO Curriculum Training")
    parser.add_argument(
        "--condition",
        type=str,
        choices=CONDITIONS,
        required=True,
        help="Training condition",
    )
    parser.add_argument(
        "--smoke_test",
        action="store_true",
        help="Run smoke test: 10 steps only",
    )
    return parser.parse_args()


def build_model_and_tokenizer(
    model_id: str,
) -> tuple:
    """Load model in bfloat16 with device_map='auto'. Returns (model, tokenizer)."""
    tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype="bfloat16",
        device_map="auto",
        trust_remote_code=True,
    )
    return model, tokenizer


def build_trainer(
    model,
    tokenizer,
    train_dataset,
    callbacks: list,
    condition: str,
) -> GRPOTrainer:
    """Configure GRPOConfig from CONFIG dict and return GRPOTrainer instance."""
    os.makedirs(f"{CONFIG['output_dir']}/{condition}", exist_ok=True)

    grpo_config = GRPOConfig(
        output_dir=f"{CONFIG['output_dir']}/{condition}",
        num_generations=CONFIG["num_generations"],
        temperature=CONFIG["temperature"],
        generation_kwargs={"max_new_tokens": CONFIG["max_new_tokens"]},
        learning_rate=CONFIG["learning_rate"],
        per_device_train_batch_size=CONFIG["per_device_train_batch_size"],
        gradient_accumulation_steps=CONFIG["gradient_accumulation_steps"],
        max_steps=CONFIG["max_steps"],
        save_steps=CONFIG["save_steps"],
        seed=CONFIG["seed"],
        bf16=True,
        logging_steps=10,
        dataloader_num_workers=0,
        remove_unused_columns=False,
    )

    trainer = GRPOTrainer(
        model=model,
        args=grpo_config,
        reward_funcs=[execution_reward_fn],
        train_dataset=train_dataset,
        callbacks=callbacks,
        processing_class=tokenizer,
    )
    return trainer


def main() -> None:
    """Parse args, build model/data/trainer, run trainer.train(), save final checkpoint."""
    args = parse_args()
    condition = args.condition

    if args.smoke_test:
        CONFIG["max_steps"] = 10
        print(f"[SMOKE TEST] Running {condition} for 10 steps")

    print(f"Loading model: {CONFIG['model_id']}")
    model, tokenizer = build_model_and_tokenizer(CONFIG["model_id"])

    print("Building data pools...")
    easy_data = build_easy_pool(tokenizer)
    hard_data = build_hard_pool(tokenizer)
    full_data = build_full_pool(tokenizer)
    print(f"  Easy pool: {len(easy_data)} examples")
    print(f"  Hard pool: {len(hard_data)} examples")
    print(f"  Full pool: {len(full_data)} examples")

    dataset = get_dataset(condition, easy_data, hard_data, full_data, CONFIG["curriculum_step"])
    print(f"  Dataset ({condition}): {len(dataset)} examples")

    os.makedirs(CONFIG["log_dir"], exist_ok=True)

    callbacks = [RewardDensityCallback(condition, CONFIG["log_dir"])]
    if condition == "curriculum":
        callbacks.insert(0, CurriculumCallback(dataset))

    trainer = build_trainer(model, tokenizer, dataset, callbacks, condition)

    print(f"Starting training: condition={condition}, max_steps={CONFIG['max_steps']}")
    trainer.train()

    final_dir = f"{CONFIG['output_dir']}/{condition}/final"
    trainer.save_model(final_dir)
    print(f"Model saved to {final_dir}")

    # Finalize reward density log
    for cb in callbacks:
        if isinstance(cb, RewardDensityCallback):
            cb.finalize()

    print(f"Training complete: condition={condition}")


if __name__ == "__main__":
    main()
