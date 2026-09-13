"""Multi-adapter model management with PEFT."""
import os
import torch
from typing import Dict, List, Optional
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

class MultiAdapterModel:
    """Manages base model with multiple LoRA adapters."""

    def __init__(
        self,
        base_model_id: str,
        device: str = "cuda" if torch.cuda.is_available() else "cpu",
    ):
        self.base_model_id = base_model_id
        self.device = device
        self.model = None
        self.tokenizer = None
        self.adapter_names: List[str] = []
        self._current_adapter: Optional[str] = None

    def load_base_model(self) -> None:
        """Load base model and tokenizer."""
        self.tokenizer = AutoTokenizer.from_pretrained(self.base_model_id)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        self.model = AutoModelForCausalLM.from_pretrained(
            self.base_model_id,
            torch_dtype=torch.float16,
            device_map="auto",
            trust_remote_code=True,
        )

    def load_adapters(self, adapter_paths: Dict[str, str]) -> None:
        """Load multiple named adapters."""
        if self.model is None:
            self.load_base_model()

        first_adapter = True
        for name, path in adapter_paths.items():
            if not os.path.exists(path):
                print(f"Warning: Adapter path {path} not found, skipping {name}")
                continue

            if first_adapter:
                self.model = PeftModel.from_pretrained(
                    self.model, path, adapter_name=name
                )
                first_adapter = False
            else:
                self.model.load_adapter(path, adapter_name=name)

            self.adapter_names.append(name)
            print(f"Loaded adapter: {name}")

        if self.adapter_names:
            self.set_adapter(self.adapter_names[0])

    def set_adapter(self, adapter_name: str) -> None:
        """Switch to specific adapter (O(1) operation)."""
        if adapter_name not in self.adapter_names:
            raise ValueError(f"Adapter {adapter_name} not loaded")
        self.model.set_adapter(adapter_name)
        self._current_adapter = adapter_name

    def set_uniform(self) -> None:
        """Set equal-weight combination of all adapters."""
        if not self.adapter_names:
            raise RuntimeError("No adapters loaded")
        weights = [1.0 / len(self.adapter_names)] * len(self.adapter_names)
        self.model.set_adapters(self.adapter_names, weights=weights)
        self._current_adapter = "uniform"

    def disable_adapters(self) -> None:
        """Use base model without any adapter."""
        self.model.disable_adapters()
        self._current_adapter = None

    @torch.no_grad()
    def generate(
        self,
        instruction: str,
        max_new_tokens: int = 128,
        temperature: float = 0.7,
        do_sample: bool = True,
        **gen_kwargs,
    ) -> str:
        """Generate response for instruction."""
        prompt = f"### Instruction:\n{instruction}\n\n### Response:\n"
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)

        outputs = self.model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            do_sample=do_sample,
            pad_token_id=self.tokenizer.pad_token_id,
            **gen_kwargs,
        )

        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        if "### Response:" in response:
            response = response.split("### Response:")[-1].strip()
        return response

    @torch.no_grad()
    def generate_batch(
        self,
        instructions: List[str],
        max_new_tokens: int = 128,
        **gen_kwargs,
    ) -> List[str]:
        """Generate responses for batch of instructions."""
        prompts = [
            f"### Instruction:\n{inst}\n\n### Response:\n" for inst in instructions
        ]
        inputs = self.tokenizer(
            prompts, return_tensors="pt", padding=True, truncation=True
        ).to(self.model.device)

        outputs = self.model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            pad_token_id=self.tokenizer.pad_token_id,
            **gen_kwargs,
        )

        responses = []
        for output in outputs:
            text = self.tokenizer.decode(output, skip_special_tokens=True)
            if "### Response:" in text:
                text = text.split("### Response:")[-1].strip()
            responses.append(text)
        return responses

    @property
    def current_adapter(self) -> Optional[str]:
        return self._current_adapter
