"""Model loading and RL trainer for H-E1 experiment."""
import subprocess
import tempfile
import torch
from torch.optim import AdamW
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, PreTrainedModel, PreTrainedTokenizerBase
from peft import LoraConfig, get_peft_model, PeftModel

from config import Config


def load_base_model(cfg: Config) -> tuple[PreTrainedModel, PreTrainedTokenizerBase]:
    """Load CodeT5+ base model and tokenizer."""
    tokenizer = AutoTokenizer.from_pretrained(cfg.model_id, cache_dir=cfg.cache_dir)
    model = AutoModelForSeq2SeqLM.from_pretrained(
        cfg.model_id,
        cache_dir=cfg.cache_dir,
        torch_dtype=torch.float16,
    )
    return model, tokenizer


def wrap_lora(model: PreTrainedModel, cfg: Config) -> PeftModel:
    """Wrap model with LoRA adapters."""
    lora_config = LoraConfig(
        r=cfg.lora_r,
        lora_alpha=cfg.lora_alpha,
        target_modules=cfg.lora_target_modules,
        lora_dropout=cfg.lora_dropout,
        bias="none",
        task_type="SEQ_2_SEQ_LM",
    )
    return get_peft_model(model, lora_config)


class RLCodeTrainer:
    """RL training with execution feedback using REINFORCE."""

    def __init__(self, model: PeftModel, tokenizer: PreTrainedTokenizerBase, cfg: Config):
        self.model = model
        self.tokenizer = tokenizer
        self.cfg = cfg
        self.optimizer = AdamW(model.parameters(), lr=cfg.rl_lr, weight_decay=cfg.weight_decay)
        self.device = next(model.parameters()).device

    def compute_reward(self, code: str, tests: list[str]) -> tuple[float, str]:
        """Execute code against tests. Returns (pass_rate, error_msg)."""
        if not tests:
            return 0.0, "No tests provided"

        passed = 0
        error_msg = ""

        for test in tests:
            full_code = f"{code}\n\n{test}"
            try:
                with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                    f.write(full_code)
                    f.flush()
                    result = subprocess.run(
                        ["python", f.name],
                        capture_output=True,
                        text=True,
                        timeout=5,
                    )
                    if result.returncode == 0:
                        passed += 1
                    else:
                        error_msg = result.stderr[:500] if result.stderr else "Test failed"
            except subprocess.TimeoutExpired:
                error_msg = "Timeout"
            except Exception as e:
                error_msg = str(e)[:500]

        pass_rate = passed / len(tests)
        return pass_rate, error_msg

    def rl_step(self, prompt: str, tests: list[str]) -> float:
        """One REINFORCE update step. Returns reward."""
        self.model.train()

        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                do_sample=True,
                temperature=self.cfg.temperature,
                max_new_tokens=self.cfg.max_new_tokens,
                return_dict_in_generate=True,
                output_scores=True,
            )

        generated_ids = outputs.sequences[:, inputs["input_ids"].shape[1]:]
        code = self.tokenizer.decode(generated_ids[0], skip_special_tokens=True)

        reward, _ = self.compute_reward(code, tests)

        # Recompute log probs for gradient
        self.optimizer.zero_grad()
        full_ids = outputs.sequences
        labels = full_ids.clone()
        labels[:, :inputs["input_ids"].shape[1]] = -100

        model_outputs = self.model(
            input_ids=inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
            labels=labels,
        )

        # REINFORCE: loss = -reward * log_prob
        loss = -reward * model_outputs.loss
        loss.backward()
        self.optimizer.step()

        print(f"RL reward: {reward:.2f}")
        return reward
