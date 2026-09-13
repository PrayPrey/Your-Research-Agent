import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

class BaselineGenerator:
    def __init__(self, model_id: str, device: str = "cuda", seed: int = 1):
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_id, torch_dtype=torch.bfloat16, device_map="auto"
        )
        self.model.eval()
        self.seed = seed
        self.device = device

    def generate(self, prompt: str, num_samples: int = 10, temperature: float = 0.2, max_new_tokens: int = 512) -> list[str]:
        torch.manual_seed(self.seed)
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        prompt_len = inputs["input_ids"].shape[1]

        completions = []
        for i in range(num_samples):
            torch.manual_seed(self.seed + i)
            try:
                out = self.model.generate(
                    **inputs,
                    do_sample=True,
                    temperature=temperature,
                    max_new_tokens=max_new_tokens,
                    num_return_sequences=1,
                    pad_token_id=self.tokenizer.eos_token_id,
                )
                completion = self.tokenizer.decode(out[0][prompt_len:], skip_special_tokens=True)
                completions.append(completion)
            except torch.cuda.OutOfMemoryError:
                torch.cuda.empty_cache()
                completions.append("")
        return completions


class ConstrainedGenerator:
    def __init__(self, model_id: str, grammar: str = "python", device: str = "cuda", seed: int = 1,
                 temperature: float = 0.2, max_new_tokens: int = 512):
        from syncode import Syncode
        self.syn_llm = Syncode(
            model=model_id,
            mode="grammar_strict",
            grammar=grammar,
            quantize=True,
            device=device,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
        )
        self.seed = seed

    def generate(self, prompt: str, num_samples: int = 10, temperature: float = 0.2, max_new_tokens: int = 512) -> list[str]:
        completions = []
        for i in range(num_samples):
            torch.manual_seed(self.seed + i)
            try:
                out = self.syn_llm.infer(prompt)
                completions.append(out if out else "")
            except Exception as e:
                print(f"SynCode infer failed sample={i}: {e}")
                completions.append("")
        return completions
