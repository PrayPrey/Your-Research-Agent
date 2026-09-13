"""Response generation with logprob capture for H-M1."""

import torch
from typing import List, Dict
from transformers import AutoModelForCausalLM, AutoTokenizer
from config import GEN_MODEL, N_GENERATIONS, TEMPERATURE, MAX_NEW_TOKENS


class ResponseGenerator:
    def __init__(self, model_id: str = GEN_MODEL, temperature: float = TEMPERATURE,
                 max_new_tokens: int = MAX_NEW_TOKENS, device: str = "cuda"):
        print(f"Loading {model_id}...")
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.tokenizer.pad_token = self.tokenizer.eos_token
        self.model = AutoModelForCausalLM.from_pretrained(
            model_id,
            torch_dtype=torch.float16,
            device_map="auto"
        )
        self.model.eval()
        self.temperature = temperature
        self.max_new_tokens = max_new_tokens
        self.device = device
        print("Model loaded.")

    def _format_prompt(self, question: str) -> str:
        """Format question with Llama-2 chat template."""
        return f"[INST] Answer the following question concisely.\n\nQuestion: {question}\n\nAnswer: [/INST]"

    def generate_n(self, question: str, n: int = N_GENERATIONS) -> List[Dict]:
        """Generate n responses with logprobs.

        Returns: [{"text": str, "logprob": float, "token_logprobs": list[float]}]
        """
        prompt = self._format_prompt(question)
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        prompt_len = inputs.input_ids.shape[1]

        results = []
        for _ in range(n):
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=self.max_new_tokens,
                    do_sample=True,
                    temperature=self.temperature,
                    top_p=1.0,
                    return_dict_in_generate=True,
                    output_scores=True,
                    pad_token_id=self.tokenizer.eos_token_id
                )

            generated_ids = outputs.sequences[0, prompt_len:]
            text = self.tokenizer.decode(generated_ids, skip_special_tokens=True).strip()

            # Compute token logprobs
            token_logprobs = []
            scores = outputs.scores
            for t, score in enumerate(scores):
                if t >= len(generated_ids):
                    break
                token_id = generated_ids[t].item()
                log_probs = torch.log_softmax(score[0], dim=-1)
                token_logprobs.append(log_probs[token_id].item())

            # Length-normalized mean logprob
            mean_logprob = sum(token_logprobs) / len(token_logprobs) if token_logprobs else 0.0

            results.append({
                "text": text,
                "logprob": mean_logprob,
                "token_logprobs": token_logprobs
            })

        return results
