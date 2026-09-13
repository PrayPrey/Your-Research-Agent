import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainerCallback
from peft import LoraConfig, get_peft_model, TaskType
from trl import GRPOTrainer
from config import ExperimentConfig, get_config, make_grpo_config
from data import load_grpo_dataset, load_kl_prompts
from rewards import execution_reward_error_type
from kl_metric import compute_kl_divergence, save_kl_log


class KLLoggingCallback(TrainerCallback):
    """Logs KL divergence against reference model at save_steps intervals."""

    def __init__(self, ref_model, tokenizer, kl_prompts, kl_log_path, device, log_every=100):
        self.ref_model = ref_model
        self.tokenizer = tokenizer
        self.kl_prompts = kl_prompts
        self.kl_log = []
        self.kl_log_path = kl_log_path
        self.device = device
        self.log_every = log_every

    def on_step_end(self, args, state, control, model=None, **kwargs):
        if state.global_step % self.log_every == 0 and state.global_step > 0:
            kl = compute_kl_divergence(
                model=model,
                ref_model=self.ref_model,
                tokenizer=self.tokenizer,
                prompts=self.kl_prompts,
                device=self.device,
            )
            entry = {"step": state.global_step, "kl_divergence": kl}
            self.kl_log.append(entry)
            save_kl_log(os.path.dirname(self.kl_log_path), self.kl_log)
            print(f"[KL] step={state.global_step} kl={kl:.4f}")


def train_grpo(cfg: ExperimentConfig = None) -> str:
    """Train GRPO model. Returns checkpoint directory path."""
    if cfg is None:
        cfg = get_config()

    device = "cuda" if torch.cuda.is_available() else "cpu"
    output_dir = os.path.join(cfg.checkpoint_dir, "grpo")
    os.makedirs(output_dir, exist_ok=True)

    tokenizer = AutoTokenizer.from_pretrained(cfg.model_id, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        cfg.model_id,
        torch_dtype=torch.bfloat16 if cfg.dtype == "bfloat16" else torch.float16,
        trust_remote_code=True,
        device_map="auto",
    )
    lora_cfg = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=16,
        lora_alpha=32,
        lora_dropout=0.05,
        target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
    )
    model = get_peft_model(model, lora_cfg)
    model.print_trainable_parameters()

    ref_model = AutoModelForCausalLM.from_pretrained(
        cfg.model_id,
        torch_dtype=torch.bfloat16 if cfg.dtype == "bfloat16" else torch.float16,
        trust_remote_code=True,
        device_map="auto",
    )
    ref_model.eval()
    for p in ref_model.parameters():
        p.requires_grad_(False)

    dataset = load_grpo_dataset(cfg)
    kl_prompts = load_kl_prompts(cfg)

    grpo_cfg = make_grpo_config(cfg, output_dir)

    kl_log_path = os.path.join(output_dir, "kl_log.json")
    kl_callback = KLLoggingCallback(
        ref_model=ref_model,
        tokenizer=tokenizer,
        kl_prompts=kl_prompts,
        kl_log_path=kl_log_path,
        device=device,
        log_every=cfg.grpo_save_steps,
    )

    trainer = GRPOTrainer(
        model=model,
        reward_funcs=[execution_reward_error_type],
        args=grpo_cfg,
        train_dataset=dataset,
        processing_class=tokenizer,
        callbacks=[kl_callback],
    )

    trainer.train()
    trainer.save_model(output_dir)
    tokenizer.save_pretrained(output_dir)

    # Final KL log flush
    save_kl_log(output_dir, kl_callback.kl_log)
    print(f"GRPO training complete. Checkpoint: {output_dir}")
    return output_dir


if __name__ == "__main__":
    train_grpo()
