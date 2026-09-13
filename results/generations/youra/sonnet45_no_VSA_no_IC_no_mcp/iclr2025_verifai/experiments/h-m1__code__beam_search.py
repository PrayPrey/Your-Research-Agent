import ast
import torch

def validate_syntax(code: str) -> bool:
    """Parse code with ast.parse to validate syntax."""
    try:
        ast.parse(code)
        return True
    except SyntaxError:
        return False

def run_beam_search(model, tokenizer, prompts: list[str], k: int = 5, max_new_tokens: int = 256) -> list[list[str]]:
    """Run beam search with k beams for each prompt."""
    all_candidates = []

    for idx, prompt in enumerate(prompts):
        print(f"Generating for problem {idx+1}/{len(prompts)}...")

        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                num_beams=k,
                num_return_sequences=k,
                max_new_tokens=max_new_tokens,
                do_sample=False,
                temperature=1.0,
                pad_token_id=tokenizer.eos_token_id
            )

        candidates = tokenizer.batch_decode(outputs, skip_special_tokens=True)

        # Remove prompt from each candidate
        candidates = [c[len(prompt):].strip() for c in candidates]

        all_candidates.append(candidates)

    return all_candidates

def custom_scoring_fn(outputs: list[str], logprobs: list[float], alpha: float = 0.7, beta: float = 0.3) -> list[float]:
    """Compute combined fluency + validity scores."""
    scores = []
    for output, logprob in zip(outputs, logprobs):
        validity = 1.0 if validate_syntax(output) else 0.0
        combined_score = alpha * logprob + beta * validity
        scores.append(combined_score)
    return scores
