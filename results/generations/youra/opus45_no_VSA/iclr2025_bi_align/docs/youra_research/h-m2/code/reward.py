import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

REWARD_MODEL_NAME = "OpenAssistant/reward-model-deberta-v3-large-v2"
MAX_TOKENS = 512
BATCH_SIZE = 32


def load_reward_model():
    """Load OpenAssistant reward model and tokenizer."""
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Loading reward model on {device}...")

    tokenizer = AutoTokenizer.from_pretrained(REWARD_MODEL_NAME)
    model = AutoModelForSequenceClassification.from_pretrained(
        REWARD_MODEL_NAME,
        torch_dtype=torch.float16 if device == "cuda" else torch.float32,
    )
    model = model.to(device)
    model.eval()

    return model, tokenizer


def compute_reward_scores(prompts, responses, model, tokenizer):
    """Compute reward scores in batches."""
    device = next(model.parameters()).device
    scores = []

    for i in range(0, len(responses), BATCH_SIZE):
        batch_prompts = prompts[i:i + BATCH_SIZE]
        batch_responses = responses[i:i + BATCH_SIZE]

        inputs = tokenizer(
            batch_prompts,
            batch_responses,
            truncation=True,
            max_length=MAX_TOKENS,
            padding=True,
            return_tensors="pt",
        )
        inputs = {k: v.to(device) for k, v in inputs.items()}

        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits.squeeze(-1)
            scores.extend(logits.cpu().tolist())

        if (i // BATCH_SIZE) % 50 == 0:
            print(f"Reward scoring: {min(i + BATCH_SIZE, len(responses))}/{len(responses)}")

    return scores
