"""DPO training using TRL DPOTrainer."""
import os
from trl import DPOTrainer
from config import get_dpo_config, get_peft_config


def build_dpo_trainer(cfg, policy_model, ref_model, tokenizer, train_dataset, eval_dataset):
    """Build DPOTrainer with configuration."""
    dpo_config = get_dpo_config(cfg)
    peft_config = get_peft_config(cfg)
    trainer = DPOTrainer(
        model=policy_model,
        ref_model=ref_model,
        args=dpo_config,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        tokenizer=tokenizer,
        peft_config=peft_config,
    )
    return trainer


def train_dpo(cfg, trainer) -> str:
    """Run DPO training and save checkpoint."""
    trainer.train()
    final_path = os.path.join(cfg.output_dir, "final")
    trainer.save_model(final_path)
    return final_path
