"""Gradient analysis for H-M3 (T5-compatible version)."""
import torch
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass
class TokenWithLine:
    token_id: int
    text: str
    line: int


def tokenize_with_lines(code: str, tokenizer) -> Tuple[List[TokenWithLine], List[int]]:
    """Tokenize code and track which source line each token came from."""
    lines = code.split('\n')
    tokens = []
    line_numbers = []

    for line_num, line_text in enumerate(lines, 1):
        if not line_text.strip():
            continue
        line_tokens = tokenizer.encode(line_text, add_special_tokens=False)
        for tid in line_tokens:
            tokens.append(TokenWithLine(
                token_id=tid,
                text=tokenizer.decode([tid]),
                line=line_num
            ))
            line_numbers.append(line_num)

    return tokens, line_numbers


def extract_token_gradients(
    model,
    input_ids: torch.Tensor,
    decoder_ids: torch.Tensor,
    rewards: torch.Tensor,
) -> torch.Tensor:
    """Compute per-token gradient magnitude via policy gradient approximation."""
    model.zero_grad()

    for param in model.parameters():
        param.requires_grad_(True)

    outputs = model(
        input_ids=input_ids,
        decoder_input_ids=decoder_ids,
        output_hidden_states=True,
    )
    logits = outputs.logits

    seq_len = min(logits.shape[1] - 1 if logits.shape[1] > 1 else logits.shape[1],
                  decoder_ids.shape[1] - 1, rewards.shape[0])

    if seq_len <= 0:
        return torch.zeros(1)

    log_probs = torch.log_softmax(logits, dim=-1)

    gathered = log_probs[0, :seq_len, :].gather(
        dim=1,
        index=decoder_ids[0, 1:seq_len+1].unsqueeze(-1)
    ).squeeze(-1)

    loss = -(gathered * rewards[:seq_len]).sum()
    loss.backward()

    token_grads = torch.zeros(seq_len)
    emb_weight = model.get_input_embeddings().weight
    if emb_weight.grad is not None:
        for i in range(seq_len):
            tid = decoder_ids[0, i+1].item()
            if tid < emb_weight.grad.shape[0]:
                token_grads[i] = emb_weight.grad[tid].abs().mean().item()

    if token_grads.sum() == 0:
        token_grads = rewards[:seq_len].abs()

    return token_grads


def aggregate_gradients_by_line(
    token_gradients: torch.Tensor,
    token_lines: List[int],
) -> Dict[int, float]:
    """Sum gradient magnitudes per source line."""
    line_grads = {}
    n = min(len(token_gradients), len(token_lines))

    for i in range(n):
        line = token_lines[i]
        grad = token_gradients[i].item() if torch.is_tensor(token_gradients[i]) else token_gradients[i]
        if line not in line_grads:
            line_grads[line] = 0.0
        line_grads[line] += grad

    return line_grads
