"""Model loading and RL trainer for H-C1 experiment."""
import subprocess
import tempfile
import torch
from torch.optim import AdamW
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, PreTrainedModel, PreTrainedTokenizerBase
from peft import LoraConfig, get_peft_model, PeftModel

from config import Config
from error_taxonomy import classify_error, ErrorClass
from diversity_controller import FeedbackDiversityController


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
    """RL training with execution feedback + diversity control."""

    def __init__(
        self,
        model: PeftModel,
        tokenizer: PreTrainedTokenizerBase,
        cfg: Config,
        diversity_controller: FeedbackDiversityController = None,
    ):
        self.model = model
        self.tokenizer = tokenizer
        self.cfg = cfg
        self.optimizer = AdamW(model.parameters(), lr=cfg.rl_lr, weight_decay=cfg.weight_decay)
        self.device = next(model.parameters()).device
        self.diversity_controller = diversity_controller

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

    def generate_samples_with_errors(self, data: list[dict], max_samples: int = 100) -> list[dict]:
        """Generate samples and classify their error types."""
        samples = []
        self.model.eval()

        for item in data[:max_samples]:
            prompt = item["prompt"]
            entry_point = item.get("entry_point", "solution")
            base_input = item.get("base_input", [])
            tests = [f"assert {entry_point}(*{t[0]}) == {t[1]}" for t in base_input if len(t) >= 2]

            if not tests:
                continue

            inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    do_sample=True,
                    temperature=self.cfg.temperature,
                    max_new_tokens=self.cfg.max_new_tokens,
                )

            code = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            if code.startswith(prompt):
                code = code[len(prompt):].strip()

            pass_rate, error_msg = self.compute_reward(code, tests)
            error_type = classify_error(error_msg, pass_rate)

            samples.append({
                "prompt": prompt,
                "code": code,
                "tests": tests,
                "pass_rate": pass_rate,
                "error_msg": error_msg,
                "error_type": error_type,
            })

        return samples

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

        return reward

    def rl_step_batch(self, batch: list[dict]) -> float:
        """Process a diversity-filtered batch. Returns average reward."""
        total_reward = 0.0

        for sample in batch:
            prompt = sample["prompt"]
            tests = sample["tests"]
            reward = self.rl_step(prompt, tests)
            total_reward += reward

        return total_reward / max(1, len(batch))
