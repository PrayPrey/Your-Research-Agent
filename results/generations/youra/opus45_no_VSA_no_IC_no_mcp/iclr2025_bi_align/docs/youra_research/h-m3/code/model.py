"""Model loading and implicit reward computation for H-M2."""
import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import get_peft_model, PeftModel


def load_tokenizer(cfg):
    """Load tokenizer with pad token setup."""
    tokenizer = AutoTokenizer.from_pretrained(cfg.base_model)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
        tokenizer.pad_token_id = tokenizer.eos_token_id
    tokenizer.padding_side = "left"
    return tokenizer


def build_policy_model(cfg, use_lora: bool = True):
    """Build policy model with LoRA for DPO training."""
    from config import get_peft_config
    use_bf16 = cfg.bf16 and torch.cuda.is_available()
    model = AutoModelForCausalLM.from_pretrained(
        cfg.base_model,
        torch_dtype=torch.bfloat16 if use_bf16 else torch.float32,
        device_map="auto" if torch.cuda.is_available() else None,
    )
    if tokenizer_pad := getattr(model.config, "pad_token_id", None) is None:
        model.config.pad_token_id = model.config.eos_token_id
    if use_lora:
        peft_config = get_peft_config(cfg)
        model = get_peft_model(model, peft_config)
        model.print_trainable_parameters()
    if cfg.gradient_checkpointing:
        model.gradient_checkpointing_enable()
    return model


def build_reference_model(cfg):
    """Build frozen reference model (no LoRA)."""
    use_bf16 = cfg.bf16 and torch.cuda.is_available()
    model = AutoModelForCausalLM.from_pretrained(
        cfg.ref_model,
        torch_dtype=torch.bfloat16 if use_bf16 else torch.float32,
        device_map="auto" if torch.cuda.is_available() else None,
    )
    if model.config.pad_token_id is None:
        model.config.pad_token_id = model.config.eos_token_id
    model.eval()
    for param in model.parameters():
        param.requires_grad = False
    return model


def load_trained_policy(cfg, checkpoint_path: str):
    """Load trained DPO policy from checkpoint."""
    use_bf16 = cfg.bf16 and torch.cuda.is_available()
    base_model = AutoModelForCausalLM.from_pretrained(
        cfg.base_model,
        torch_dtype=torch.bfloat16 if use_bf16 else torch.float32,
        device_map="auto" if torch.cuda.is_available() else None,
    )
    model = PeftModel.from_pretrained(base_model, checkpoint_path)
    model = model.merge_and_unload()
    model.eval()
    return model


def get_sequence_logprobs(model, input_ids, attention_mask) -> torch.Tensor:
    """Compute sum of log-probs for sequence."""
    with torch.no_grad():
        outputs = model(input_ids=input_ids, attention_mask=attention_mask)
        logits = outputs.logits[:, :-1, :]
        target_ids = input_ids[:, 1:]
        logprobs = F.log_softmax(logits, dim=-1)
        token_logprobs = logprobs.gather(-1, target_ids.unsqueeze(-1)).squeeze(-1)
        mask = attention_mask[:, 1:].float()
        return (token_logprobs * mask).sum(dim=-1)


def compute_dpo_implicit_reward(policy, ref_model, tokenizer, text: str, beta: float, device: str) -> float:
    """Compute DPO implicit reward: r(x,y) = beta * (log pi - log pi_ref)."""
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512, padding="max_length")
    inputs = {k: v.to(device) for k, v in inputs.items()}
    policy_logprobs = get_sequence_logprobs(policy, inputs["input_ids"], inputs["attention_mask"])
    ref_logprobs = get_sequence_logprobs(ref_model, inputs["input_ids"], inputs["attention_mask"])
    implicit_reward = beta * (policy_logprobs - ref_logprobs)
    return implicit_reward.item()


def generate(model, tokenizer, prompt: str, device: str, max_new_tokens: int = 128) -> str:
    """Generate response from model."""
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=384)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=False,
            pad_token_id=tokenizer.pad_token_id,
        )
    response = tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
    return response
