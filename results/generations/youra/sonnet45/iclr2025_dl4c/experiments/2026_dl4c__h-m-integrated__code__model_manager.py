"""
Model Management for Sequential Code Generation
"""

from typing import List, Optional, Tuple
import gc
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


class ModelManager:
    """Sequential model loading and code generation manager."""

    def __init__(self, model_config: dict, generation_config: dict):
        """Initialize with config."""
        self.model_config = model_config
        self.generation_config = generation_config
        self.model: Optional[AutoModelForCausalLM] = None
        self.tokenizer: Optional[AutoTokenizer] = None
        self.device: str = "cuda" if torch.cuda.is_available() else "cpu"
        self.current_model_name: Optional[str] = None

    def load_model(self, model_name: str) -> Tuple[AutoModelForCausalLM, AutoTokenizer]:
        """
        Load model and tokenizer to GPU.
        Returns (model, tokenizer).
        """
        print(f"Loading model: {model_name}...")

        try:
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                trust_remote_code=self.model_config.get("trust_remote_code", True),
                cache_dir=self.model_config.get("cache_dir", None)
            )

            # Set pad token if not set
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

            # Load model (use 'dtype' instead of deprecated 'torch_dtype')
            dtype_str = self.model_config.get("torch_dtype", "float16")
            dtype = getattr(torch, dtype_str) if hasattr(torch, dtype_str) else torch.float16

            # Build model loading kwargs
            load_kwargs = {
                "trust_remote_code": self.model_config.get("trust_remote_code", True),
                "cache_dir": self.model_config.get("cache_dir", None)
            }

            # Only add dtype if not using device_map (avoid conflicts)
            device_map = self.model_config.get("device_map", None)
            if device_map is not None:
                load_kwargs["device_map"] = device_map
                load_kwargs["torch_dtype"] = dtype  # Use torch_dtype with device_map
            else:
                # Manual device placement
                self.model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    **load_kwargs
                )
                self.model = self.model.to(self.device)
                if dtype == torch.float16 and self.device == "cuda":
                    self.model = self.model.half()
                return self.model, self.tokenizer

            # If using device_map
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                **load_kwargs
            )

            self.model.eval()
            self.current_model_name = model_name

            print(f"Model loaded successfully: {model_name}")
            return self.model, self.tokenizer

        except Exception as e:
            print(f"ERROR: Failed to load model {model_name}: {e}")
            raise

    def unload_model(self) -> None:
        """Free GPU memory after model use."""
        if self.model is not None:
            print(f"Unloading model: {self.current_model_name}...")
            del self.model
            del self.tokenizer
            self.model = None
            self.tokenizer = None
            self.current_model_name = None

            # Force garbage collection and clear CUDA cache
            gc.collect()
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

            print("Model unloaded, GPU memory freed")

    def generate_sample(self, prompt: str) -> str:
        """
        Generate single code sample.
        prompt: str -> code: str
        """
        if self.model is None or self.tokenizer is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")

        # Tokenize input
        inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        # Generate
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                temperature=self.generation_config.get("temperature", 0.8),
                top_p=self.generation_config.get("top_p", 0.95),
                max_new_tokens=self.generation_config.get("max_new_tokens", 512),
                do_sample=self.generation_config.get("do_sample", True),
                num_return_sequences=self.generation_config.get("num_return_sequences", 1),
                pad_token_id=self.tokenizer.pad_token_id
            )

        # Decode
        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Strip prompt from output
        if generated_text.startswith(prompt):
            code = generated_text[len(prompt):]
        else:
            code = generated_text

        return code.strip()

    def generate_batch(self, task: dict, n: int) -> List[str]:
        """
        Generate n samples for task.
        Returns list of n code strings.
        """
        prompt = task["prompt"]
        samples = []

        print(f"  Generating {n} samples for {task['task_id']}...", end=" ", flush=True)

        for i in range(n):
            try:
                code = self.generate_sample(prompt)
                samples.append(code)
            except Exception as e:
                print(f"\n  WARNING: Generation failed for sample {i}: {e}")
                samples.append("")  # Add empty sample on failure

        print(f"Done ({len([s for s in samples if s])} successful)")
        return samples
