"""Code generation with logit extraction for Code Llama."""

import torch
from typing import Tuple
from transformers import AutoModelForCausalLM, AutoTokenizer


class CodeGenerator:
    """Code generation pipeline with logit extraction."""

    def __init__(
        self,
        model_name: str,
        device: str = "cuda",
        torch_dtype = torch.float16,
        device_map: str = "auto",
        cache_dir: str = None
    ):
        """
        Initialize Code Llama model and tokenizer.

        Args:
            model_name: HuggingFace model identifier
            device: Device for inference
            torch_dtype: Data type for model weights
            device_map: Device mapping strategy
            cache_dir: Cache directory for model weights
        """
        self.device = device
        self.model_name = model_name

        # Load model
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch_dtype,
            device_map=device_map,
            trust_remote_code=True
        )
        self.model.eval()  # Set to evaluation mode

        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name
        )

        # Set pad token if not present
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
            self.tokenizer.pad_token_id = self.tokenizer.eos_token_id

    def generate_with_logits(
        self,
        prompt: str,
        max_new_tokens: int = 256,
        temperature: float = 1.0,
        top_p: float = 0.95,
        do_sample: bool = True
    ) -> Tuple[str, torch.Tensor]:
        """
        Generate code and extract logits for final token.

        Args:
            prompt: Task description
            max_new_tokens: Generation length
            temperature: Sampling temperature (pre-calibration)
            top_p: Nucleus sampling threshold
            do_sample: Whether to use sampling

        Returns:
            generated_code: String of generated Python code
            logits: [V] logits for final generated token
        """
        # Tokenize prompt
        inputs = self.tokenizer(prompt, return_tensors="pt", padding=True)

        # Move to device if model is on CUDA
        if hasattr(self.model, 'device'):
            device = self.model.device
        else:
            device = next(self.model.parameters()).device

        inputs = {k: v.to(device) for k, v in inputs.items()}

        # Generate with logit tracking
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p,
                do_sample=do_sample,
                return_dict_in_generate=True,
                output_scores=True,
                pad_token_id=self.tokenizer.pad_token_id
            )

        # Extract generated code
        generated_ids = outputs.sequences[0, inputs['input_ids'].shape[1]:]
        generated_code = self.tokenizer.decode(generated_ids, skip_special_tokens=True)

        # Extract final token logits (for confidence calculation)
        if len(outputs.scores) > 0:
            final_logits = outputs.scores[-1][0]  # [V]
        else:
            # Fallback: if no generation, use zeros
            final_logits = torch.zeros(self.model.config.vocab_size, device=device)

        return generated_code, final_logits.cpu()

    def batch_generate(
        self,
        prompts: list,
        max_new_tokens: int = 256,
        temperature: float = 1.0,
        top_p: float = 0.95
    ):
        """
        Generate code for multiple prompts.

        Args:
            prompts: List of task descriptions
            max_new_tokens: Generation length
            temperature: Sampling temperature
            top_p: Nucleus sampling threshold

        Returns:
            results: List of (generated_code, logits) tuples
        """
        results = []
        for prompt in prompts:
            code, logits = self.generate_with_logits(
                prompt,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p
            )
            results.append((code, logits))
        return results
