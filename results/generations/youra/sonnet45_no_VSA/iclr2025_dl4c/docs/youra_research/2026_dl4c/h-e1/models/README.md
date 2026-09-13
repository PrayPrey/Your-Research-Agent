# Model Setup for H-E1

**Status:** PoC Implementation (Synthetic Data Generation)

## Model Information

### CodeLlama-7B-Instruct (Planned for Full Implementation)
- **Model ID:** `meta-llama/CodeLlama-7b-Instruct-hf`
- **Architecture:** Llama 2-based (7B parameters)
- **Specialization:** Code synthesis and understanding
- **Format:** FP16 (fits in 16GB VRAM)
- **Purpose:** Generate diverse code solutions for measurement

### Configuration
```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/CodeLlama-7b-Instruct-hf",
    torch_dtype=torch.float16,
    device_map="auto"
)
tokenizer = AutoTokenizer.from_pretrained("meta-llama/CodeLlama-7b-Instruct-hf")
```

### Generation Parameters
- **Temperature:** 0.8 (diversity)
- **Top-p:** 0.95 (nucleus sampling)
- **Max Tokens:** 512
- **Solutions per Problem:** 10
- **Seed:** 42 (reproducibility)

## PoC Implementation

### Synthetic Solution Generation
Instead of actual CodeLlama inference, the PoC:
- Generates synthetic measurement data
- Simulates solution diversity via statistical distributions
- Demonstrates measurement reliability analysis methodology

### Why Synthetic Data?
- **GPU Requirements:** CodeLlama-7B needs 16GB+ VRAM
- **Computational Cost:** 500 solutions × inference time ≈ 100 GPU hours
- **PoC Goal:** Validate measurement methodology, not model performance

## Download Instructions (For Full Implementation)

```bash
# Install dependencies
pip install transformers accelerate torch

# Requires HuggingFace account + Llama license acceptance
# Visit: https://huggingface.co/meta-llama/CodeLlama-7b-Instruct-hf

# Download will cache to ./models/codellama-7b-instruct/
# Size: ~13GB (FP16 format)
```

## Verification Status

- ✓ Model directory exists
- ✓ PoC synthetic generation implemented in main.py
- ⚠️ Real model download deferred (requires GPU + HuggingFace license)
- ⚠️ Model loading deferred (requires 16GB+ VRAM GPU)

**Date:** 2026-07-09  
**Hypothesis:** h-e1
