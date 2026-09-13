import gc
import warnings
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


def check_vram_gb() -> float:
    if not torch.cuda.is_available():
        return 0.0
    return torch.cuda.get_device_properties(0).total_memory / (1024 ** 3)


def decide_quantization(model_id: str, config) -> bool:
    vram_gb = check_vram_gb()
    is_13b = "13b" in model_id.lower()
    if is_13b and vram_gb < config.use_4bit_threshold_gb:
        warnings.warn(
            f"13B model with {vram_gb:.1f}GB VRAM. Using 4-bit quantization."
        )
        return True
    return False


def load_model(model_id: str, use_4bit: bool = False):
    from transformers import BitsAndBytesConfig

    quant_config = None
    if use_4bit:
        quant_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
        )

    dtype = torch.bfloat16 if not use_4bit else None
    # CPU fallback: use float32
    if not torch.cuda.is_available():
        dtype = torch.float32

    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        dtype=dtype,
        quantization_config=quant_config,
        device_map="auto",
        low_cpu_mem_usage=True,
    )
    model.eval()

    tokenizer = AutoTokenizer.from_pretrained(model_id)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    return model, tokenizer


def unload_model(model) -> None:
    del model
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    gc.collect()


def get_checkpoint_hash(model_id: str) -> str:
    try:
        from huggingface_hub import model_info
        info = model_info(model_id)
        return info.sha or "unknown"
    except Exception:
        return "unknown"
