import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

class ResponseGenerator:
    def __init__(self, model_id: str = "meta-llama/Meta-Llama-3-8B-Instruct", seed: int = 42):
        torch.manual_seed(seed)
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_id, torch_dtype=torch.bfloat16, device_map="auto"
        )
        self.model.eval()
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

    def generate_n(self, question: str, n: int = 10, temperature: float = 0.7, max_tokens: int = 256) -> list[str]:
        messages = [{"role": "user", "content": question}]
        prompt = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        input_len = inputs["input_ids"].shape[1]
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                do_sample=True,
                num_return_sequences=n,
                temperature=temperature,
                max_new_tokens=max_tokens,
                pad_token_id=self.tokenizer.pad_token_id,
            )
        responses = []
        for seq in outputs:
            text = self.tokenizer.decode(seq[input_len:], skip_special_tokens=True)
            responses.append(text.strip())
        return responses
