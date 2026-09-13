"""Attention concentration measurement and extraction."""
import torch
import pandas as pd
from transformers import AutoModelForCausalLM, AutoTokenizer


def run_attention_extraction(
    dataset: pd.DataFrame,
    extractor,
    model_name: str = "meta-llama/Llama-2-7b-hf",
    max_samples: int = None
) -> pd.DataFrame:
    """Run model, extract attention concentrations.

    Returns: dataset with added 'concentration' column
    """
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16,
        device_map="auto",
        attn_implementation="eager"  # Required for attention extraction
    )

    # Set tokenizer in extractor
    extractor.tokenizer = tokenizer

    concentrations = []
    samples_to_process = dataset.head(max_samples) if max_samples else dataset

    for idx, row in samples_to_process.iterrows():
        prompt = f"Context: {row['context'][:2000]}\n\nQuestion: {row['question']}\n\nAnswer:"
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=4096).to(model.device)

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=64,
                output_attentions=True,
                return_dict_in_generate=True
            )

        # Extract from last generation step
        concentration = extractor.extract_concentration(
            row['question'],
            outputs.attentions[-1],  # Last generation step
            inputs['input_ids']
        )
        concentrations.append(concentration)

        if (idx + 1) % 10 == 0:
            print(f"Processed {idx + 1}/{len(samples_to_process)} samples")

    dataset_copy = samples_to_process.copy()
    dataset_copy['concentration'] = concentrations
    return dataset_copy
