"""LLaMA-2 model integration for generation and logits extraction.

This module handles model loading, batch generation, and token-level logits extraction.
"""

import os
import pickle
from pathlib import Path
from typing import Dict, List, Optional
import numpy as np
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from tqdm import tqdm


class ModelEngine:
    """LLaMA-2 model wrapper for controlled generation with logits extraction."""

    def __init__(
        self,
        model_name: str = "meta-llama/Llama-2-7b-hf",
        cache_dir: str = "./models/llama-2-7b-hf",
        device: Optional[str] = None,
        seed: int = 42
    ):
        """Initialize model engine.

        Parameters
        ----------
        model_name : str
            HuggingFace model identifier
        cache_dir : str
            Directory to cache model weights
        device : Optional[str]
            Device to load model on ('cuda', 'cpu', or None for auto)
        seed : int
            Random seed for reproducibility
        """
        self.model_name = model_name
        self.cache_dir = Path(cache_dir)
        self.seed = seed

        # Set random seeds
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)

        # Determine device
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

        print(f"Using device: {self.device}")

        # Create cache directory
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Load tokenizer and model
        self.tokenizer = None
        self.model = None
        self._load_model()

    def _load_model(self):
        """Load tokenizer and model from HuggingFace."""
        print(f"Loading tokenizer from {self.model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name,
            cache_dir=str(self.cache_dir),
            use_fast=True
        )

        # Set padding token if not set
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        print(f"Loading model from {self.model_name}")
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            cache_dir=str(self.cache_dir),
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            device_map="auto" if self.device == "cuda" else None,
            low_cpu_mem_usage=True
        )

        if self.device == "cpu":
            self.model = self.model.to(self.device)

        self.model.eval()
        print(f"Model loaded successfully (vocab size: {self.tokenizer.vocab_size})")

    def generate_with_logits(
        self,
        prompts: List[str],
        max_new_tokens: int = 128,
        temperature: float = 1.0,
        top_p: float = 0.9,
        batch_size: int = 1
    ) -> List[Dict]:
        """Generate responses with token-level logits.

        Parameters
        ----------
        prompts : List[str]
            Input prompts
        max_new_tokens : int
            Maximum tokens to generate
        temperature : float
            Sampling temperature
        top_p : float
            Nucleus sampling parameter
        batch_size : int
            Batch size for generation

        Returns
        -------
        List[Dict]
            Generated outputs with logits for each prompt
        """
        results = []

        with torch.no_grad():
            for i in tqdm(range(0, len(prompts), batch_size), desc="Generating"):
                batch_prompts = prompts[i:i + batch_size]

                # Tokenize
                inputs = self.tokenizer(
                    batch_prompts,
                    return_tensors="pt",
                    padding=True,
                    truncation=True,
                    max_length=2048
                )
                inputs = {k: v.to(self.device) for k, v in inputs.items()}

                # Generate
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    do_sample=True,
                    temperature=temperature,
                    top_p=top_p,
                    output_scores=True,
                    return_dict_in_generate=True,
                    pad_token_id=self.tokenizer.pad_token_id,
                    eos_token_id=self.tokenizer.eos_token_id
                )

                # Extract generated tokens and logits
                generated_ids = outputs.sequences[:, inputs['input_ids'].shape[1]:]
                logits = outputs.scores  # Tuple of [batch_size, vocab_size] tensors

                # Process each sample in batch
                for j in range(len(batch_prompts)):
                    generated_tokens = generated_ids[j].cpu().tolist()

                    # Extract logits for this sample
                    sample_logits = []
                    for step_logits in logits:
                        sample_logits.append(step_logits[j].cpu().numpy())

                    # Decode generated text
                    generated_text = self.tokenizer.decode(
                        generated_tokens,
                        skip_special_tokens=True
                    )

                    results.append({
                        'prompt': batch_prompts[j],
                        'generated_text': generated_text,
                        'generated_tokens': generated_tokens[:len(sample_logits)],
                        'logits': sample_logits
                    })

        return results

    def process_dataset(
        self,
        samples: List[Dict],
        batch_size: int = 8,
        checkpoint_path: Optional[str] = None,
        checkpoint_interval: int = 500
    ) -> List[Dict]:
        """Process full dataset with generation and logits extraction.

        Parameters
        ----------
        samples : List[Dict]
            Dataset samples with 'question' and 'label' fields
        batch_size : int
            Batch size for generation
        checkpoint_path : Optional[str]
            Path to save/load checkpoints
        checkpoint_interval : int
            Save checkpoint every N samples

        Returns
        -------
        List[Dict]
            Processed samples with generated outputs and logits
        """
        # Try to load checkpoint
        start_idx = 0
        results = []

        if checkpoint_path and os.path.exists(checkpoint_path):
            print(f"Loading checkpoint from {checkpoint_path}")
            with open(checkpoint_path, 'rb') as f:
                checkpoint = pickle.load(f)
                results = checkpoint['results']
                start_idx = len(results)
            print(f"Resuming from sample {start_idx}")

        # Prepare prompts
        prompts = []
        for sample in samples[start_idx:]:
            prompt = f"Question: {sample['question']}\nAnswer:"
            prompts.append(prompt)

        # Generate in batches
        generated = self.generate_with_logits(
            prompts,
            batch_size=batch_size
        )

        # Combine with sample metadata
        for idx, (sample, gen) in enumerate(zip(samples[start_idx:], generated)):
            result = {
                'sample_id': sample['id'],
                'question': sample['question'],
                'gold_answer': sample['gold_answer'],
                'generated_text': gen['generated_text'],
                'generated_tokens': gen['generated_tokens'],
                'logits': gen['logits'],
                'label': sample['label']
            }
            results.append(result)

            # Save checkpoint
            if checkpoint_path and (len(results) % checkpoint_interval == 0):
                print(f"Saving checkpoint at {len(results)} samples")
                with open(checkpoint_path, 'wb') as f:
                    pickle.dump({'results': results}, f)

        # Final checkpoint
        if checkpoint_path:
            print(f"Saving final checkpoint ({len(results)} samples)")
            with open(checkpoint_path, 'wb') as f:
                pickle.dump({'results': results}, f)

        return results


def save_generated_outputs(results: List[Dict], output_path: str):
    """Save generated outputs to pickle file.

    Parameters
    ----------
    results : List[Dict]
        Generated outputs with logits
    output_path : str
        Output file path
    """
    print(f"Saving {len(results)} generated outputs to {output_path}")
    with open(output_path, 'wb') as f:
        pickle.dump(results, f)
    print(f"Saved successfully")


def load_generated_outputs(input_path: str) -> List[Dict]:
    """Load generated outputs from pickle file.

    Parameters
    ----------
    input_path : str
        Input file path

    Returns
    -------
    List[Dict]
        Generated outputs with logits
    """
    print(f"Loading generated outputs from {input_path}")
    with open(input_path, 'rb') as f:
        results = pickle.load(f)
    print(f"Loaded {len(results)} samples")
    return results
