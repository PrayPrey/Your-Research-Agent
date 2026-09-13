import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

def setup_device(device_str: str = "auto") -> torch.device:
    """Detect GPU availability and return appropriate device."""
    if device_str == "auto":
        if torch.cuda.is_available():
            device = torch.device("cuda")
            print(f"Using GPU: {torch.cuda.get_device_name(0)}")
        else:
            device = torch.device("cpu")
            print("Using CPU (no GPU available)")
    else:
        device = torch.device(device_str)
        print(f"Using device: {device}")
    return device

def load_codellama(model_id: str, device: torch.device, dtype: str) -> tuple:
    """Load CodeLlama model and tokenizer."""
    import os
    from pathlib import Path

    # Check for cached local path
    cache_home = Path.home() / '.cache' / 'huggingface' / 'hub'
    model_dir = cache_home / 'models--codellama--CodeLlama-7b-hf'

    if model_dir.exists():
        snapshots = list((model_dir / 'snapshots').iterdir())
        if snapshots:
            local_path = snapshots[0]
            print(f"Using cached model at {local_path}")
            model_id = str(local_path)
    else:
        print(f"Loading model {model_id}...")

    tokenizer = AutoTokenizer.from_pretrained(model_id, local_files_only=True)

    torch_dtype = torch.float16 if dtype == "float16" else torch.float32

    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch_dtype,
        device_map="auto" if device.type == "cuda" else None,
        low_cpu_mem_usage=True,
        local_files_only=True
    )

    if device.type == "cpu":
        model = model.to(device)

    print("Model loaded successfully.")
    return model, tokenizer
