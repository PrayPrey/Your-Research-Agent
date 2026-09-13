"""Model loading and log-probability computation."""
import torch
from torch import Tensor
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer, PreTrainedModel, PreTrainedTokenizer
from config import CONFIG


def load_tokenizer(model_name: str) -> PreTrainedTokenizer:
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
        tokenizer.pad_token_id = tokenizer.eos_token_id
    return tokenizer


def load_policy_model(model_name: str) -> PreTrainedModel:
    dtype = getattr(torch, CONFIG.dtype)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=dtype,
        device_map=CONFIG.device_map,
        trust_remote_code=True,
        attn_implementation="flash_attention_2",
    )
    model.gradient_checkpointing_enable()
    model.train()
    return model


def load_reference_model(model_name: str) -> PreTrainedModel:
    dtype = getattr(torch, CONFIG.dtype)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=dtype,
        device_map=CONFIG.device_map,
        trust_remote_code=True,
    )
    model.eval()
    model.requires_grad_(False)
    return model


def compute_logps(
    model: PreTrainedModel,
    input_ids: Tensor,
    attention_mask: Tensor,
    pad_token_id: int,
) -> Tensor:
    """Compute sequence-level log probability."""
    with torch.cuda.amp.autocast(dtype=torch.bfloat16):
        outputs = model(input_ids=input_ids, attention_mask=attention_mask)
        logits = outputs.logits

    logits = logits[:, :-1, :]
    labels = input_ids[:, 1:]
    mask = (labels != pad_token_id).float()

    log_probs = F.log_softmax(logits.float(), dim=-1)
    token_logps = torch.gather(log_probs, dim=-1, index=labels.unsqueeze(-1)).squeeze(-1)
    seq_logps = (token_logps * mask).sum(dim=-1)

    return seq_logps
