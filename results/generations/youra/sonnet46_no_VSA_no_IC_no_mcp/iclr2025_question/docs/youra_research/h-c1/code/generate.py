import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForCausalLM


def load_base_model(cfg):
    """Load Llama-2-7B-hf in float16, device_map=auto. Returns (model, tokenizer)."""
    tokenizer = AutoTokenizer.from_pretrained(cfg.model_id_base, padding_side="left")
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        cfg.model_id_base,
        torch_dtype=torch.float16,
        device_map="auto",
    )
    model.eval()
    return model, tokenizer


def generate_k_samples(questions, model, tokenizer, K=10, temperature=0.7,
                       max_new_tokens=50, seed=42, batch_size=8):
    """Returns [N x K] stochastic samples for SE/SCG computation."""
    torch.manual_seed(seed)
    all_samples = []

    for i in range(0, len(questions), batch_size):
        batch_questions = questions[i:i + batch_size]
        batch_samples = [[] for _ in batch_questions]
        prompts = [f"Q: {q}\nA:" for q in batch_questions]

        for k in range(K):
            inputs = tokenizer(
                prompts, return_tensors="pt", padding=True,
                truncation=True, max_length=512
            ).to(model.device)
            with torch.no_grad():
                output_ids = model.generate(
                    **inputs,
                    do_sample=True,
                    temperature=temperature,
                    max_new_tokens=max_new_tokens,
                    pad_token_id=tokenizer.eos_token_id,
                )
            new_ids = output_ids[:, inputs["input_ids"].shape[1]:]
            decoded = tokenizer.batch_decode(new_ids, skip_special_tokens=True)
            for j, text in enumerate(decoded):
                batch_samples[j].append(text.strip())

        all_samples.extend(batch_samples)
        print(f"K-samples: batch {i // batch_size + 1}/{(len(questions) + batch_size - 1) // batch_size} done")

    return all_samples


def generate_greedy_with_logits(questions, model, tokenizer, max_new_tokens=50, batch_size=8):
    """Returns (greedy_answers [N], per_token_logprobs [N x T])."""
    answers, all_logprobs = [], []

    for i in range(0, len(questions), batch_size):
        batch_q = questions[i:i + batch_size]
        prompts = [f"Q: {q}\nA:" for q in batch_q]
        inputs = tokenizer(
            prompts, return_tensors="pt", padding=True,
            truncation=True, max_length=512
        ).to(model.device)

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                do_sample=False,
                max_new_tokens=max_new_tokens,
                return_dict_in_generate=True,
                output_scores=True,
                pad_token_id=tokenizer.eos_token_id,
            )

        for b in range(len(batch_q)):
            new_ids = outputs.sequences[b, inputs["input_ids"].shape[1]:]
            answer = tokenizer.decode(new_ids, skip_special_tokens=True).strip()
            answers.append(answer)

            token_logprobs = []
            for t, score in enumerate(outputs.scores):
                if t >= len(new_ids):
                    break
                log_probs = F.log_softmax(score[b], dim=-1)
                token_id = new_ids[t].item()
                token_logprobs.append(log_probs[token_id].item())
            all_logprobs.append(token_logprobs)

        print(f"Greedy: batch {i // batch_size + 1}/{(len(questions) + batch_size - 1) // batch_size} done")

    return answers, all_logprobs
