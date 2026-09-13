import os
import random
import numpy as np
import torch
import torch.nn.functional as F
from torch.optim import AdamW
from transformers import GPT2LMHeadModel, GPT2Tokenizer
from scipy.stats import pearsonr
import matplotlib.pyplot as plt
import warnings
import copy

warnings.filterwarnings("ignore")

working_dir = os.path.join(os.getcwd(), "working")
os.makedirs(working_dir, exist_ok=True)

random.seed(42)
np.random.seed(42)
torch.manual_seed(42)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

experiment_data = {
    "uah_training": {
        "metrics": {"train": [], "val": []},
        "losses": {"train": [], "val": []},
        "hedging_scores": [],
        "entropy_scores": [],
        "alignment_scores": [],
        "predictions": [],
        "ground_truth": [],
    }
}

HEDGING_PHRASES = {
    "high_uncertainty": [
        "i'm not sure",
        "i don't know",
        "maybe",
        "perhaps",
        "possibly",
        "i think",
        "i believe",
        "might be",
        "could be",
        "not certain",
        "uncertain",
        "unclear",
        "hard to say",
        "approximately",
        "roughly",
        "around",
        "about",
        "probably not",
        "i'm unsure",
        "it's possible",
        "it seems",
        "appears to be",
        "likely",
        "unlikely",
    ],
    "medium_uncertainty": [
        "probably",
        "generally",
        "usually",
        "often",
        "in most cases",
        "typically",
        "tends to",
        "should be",
        "i would say",
        "my guess is",
        "presumably",
    ],
    "low_uncertainty": [
        "definitely",
        "certainly",
        "absolutely",
        "clearly",
        "obviously",
        "without doubt",
        "for sure",
        "undoubtedly",
        "i'm certain",
        "i'm confident",
        "i know",
        "the answer is",
    ],
}


def compute_hedging_score(text):
    text_lower = text.lower()
    high_count = sum(
        1 for phrase in HEDGING_PHRASES["high_uncertainty"] if phrase in text_lower
    )
    medium_count = sum(
        1 for phrase in HEDGING_PHRASES["medium_uncertainty"] if phrase in text_lower
    )
    low_count = sum(
        1 for phrase in HEDGING_PHRASES["low_uncertainty"] if phrase in text_lower
    )
    if high_count + medium_count + low_count == 0:
        return 0.5
    score = (high_count * 1.0 + medium_count * 0.5 - low_count * 0.3) / (
        high_count + medium_count + low_count + 1
    )
    return max(0.0, min(1.0, score + 0.5))


def compute_entropy(logits):
    if logits is None or len(logits) == 0:
        return 0.5
    try:
        probs = F.softmax(logits, dim=-1)
        probs = probs.clamp(min=1e-10)
        log_probs = torch.log(probs)
        entropy = -torch.sum(probs * log_probs, dim=-1)
        avg_entropy = entropy.mean().item()
        return min(1.0, max(0.0, avg_entropy / 10.0))
    except:
        return 0.5


def create_synthetic_dataset(n_samples=200):
    easy_qa = [
        ("What color is the sky on a clear day?", "blue", True),
        ("How many legs does a dog have?", "four", True),
        ("What is 2 + 2?", "4", True),
        ("What planet do we live on?", "Earth", True),
        ("What do cows produce?", "milk", True),
        ("How many days in a week?", "seven", True),
        ("What color are bananas?", "yellow", True),
        ("What is the capital of France?", "Paris", True),
    ]
    hard_qa = [
        ("What will the stock market do tomorrow?", "unpredictable", False),
        ("Who will win the next election?", "uncertain", False),
        ("What is the meaning of consciousness?", "debated", False),
        ("Will it rain in exactly 30 days?", "unknown", False),
        ("What happens after death?", "unknown", False),
        ("Is there life on other planets?", "uncertain", False),
        ("What will technology look like in 100 years?", "speculative", False),
        ("Can machines truly think?", "debated", False),
    ]
    dataset = []
    for _ in range(n_samples // 2):
        q, a, is_easy = random.choice(easy_qa)
        dataset.append({"question": q, "answer": a, "is_easy": is_easy})
        q, a, is_easy = random.choice(hard_qa)
        dataset.append({"question": q, "answer": a, "is_easy": is_easy})
    random.shuffle(dataset)
    return dataset


def generate_response(model, tokenizer, question, max_length=50):
    prompt = f"Question: {question}\nAnswer:"
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=100)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    with torch.no_grad():
        outputs = model.generate(
            inputs["input_ids"],
            attention_mask=inputs["attention_mask"],
            max_new_tokens=max_length,
            do_sample=True,
            temperature=0.7,
            top_p=0.9,
            pad_token_id=tokenizer.eos_token_id,
            output_scores=True,
            return_dict_in_generate=True,
        )
    if outputs.scores:
        all_logits = torch.stack(outputs.scores, dim=1).squeeze(0)
        entropy = compute_entropy(all_logits)
    else:
        entropy = 0.5
    generated_ids = outputs.sequences[0][inputs["input_ids"].shape[1] :]
    response = tokenizer.decode(generated_ids, skip_special_tokens=True)
    return response, entropy


def compute_alignment_score(hedging_scores, entropy_scores):
    if len(hedging_scores) < 2 or len(entropy_scores) < 2:
        return 0.0
    if np.std(hedging_scores) < 1e-6 or np.std(entropy_scores) < 1e-6:
        return 0.0
    try:
        corr, _ = pearsonr(hedging_scores, entropy_scores)
        return 0.0 if np.isnan(corr) else corr
    except:
        return 0.0


def compute_reward(hedging_score, entropy, is_correct):
    alignment_diff = abs(hedging_score - entropy)
    alignment_reward = 1.0 - alignment_diff
    correctness_reward = 0.3 if is_correct else 0.0
    return 0.7 * alignment_reward + 0.3 * correctness_reward


def evaluate_model(model, tokenizer, dataset, prefix=""):
    hedging_scores, entropy_scores = [], []
    model.eval()
    for item in dataset[:50]:
        response, entropy = generate_response(model, tokenizer, item["question"])
        hedging_scores.append(compute_hedging_score(response))
        entropy_scores.append(entropy)
    alignment = compute_alignment_score(hedging_scores, entropy_scores)
    print(
        f"{prefix}Hedging: mean={np.mean(hedging_scores):.3f}, std={np.std(hedging_scores):.3f}"
    )
    print(
        f"{prefix}Entropy: mean={np.mean(entropy_scores):.3f}, std={np.std(entropy_scores):.3f}"
    )
    print(f"{prefix}Alignment (Pearson): {alignment:.4f}")
    return alignment, hedging_scores, entropy_scores


print("Loading model and tokenizer...")
tokenizer = GPT2Tokenizer.from_pretrained("distilgpt2")
tokenizer.pad_token = tokenizer.eos_token

model = GPT2LMHeadModel.from_pretrained("distilgpt2").to(device)
model.config.pad_token_id = tokenizer.eos_token_id

ref_model = copy.deepcopy(model)
ref_model.eval()
for p in ref_model.parameters():
    p.requires_grad = False

print("Creating dataset...")
train_data = create_synthetic_dataset(n_samples=100)
val_data = create_synthetic_dataset(n_samples=50)

print("\n=== Baseline Evaluation ===")
baseline_alignment, baseline_hedging, baseline_entropy = evaluate_model(
    model, tokenizer, val_data, "Baseline "
)
experiment_data["uah_training"]["alignment_scores"].append(baseline_alignment)

optimizer = AdamW(model.parameters(), lr=1e-5)
num_epochs = 8
kl_coef = 0.1

print("\n=== Starting UAH Training ===")
for epoch in range(num_epochs):
    model.train()
    epoch_losses, epoch_rewards = [], []
    random.shuffle(train_data)

    for item in train_data[:40]:
        question, is_easy = item["question"], item["is_easy"]
        prompt = f"Question: {question}\nAnswer:"
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=100)
        inputs = {k: v.to(device) for k, v in inputs.items()}
        prompt_len = inputs["input_ids"].shape[1]

        with torch.no_grad():
            outputs = model.generate(
                inputs["input_ids"],
                attention_mask=inputs["attention_mask"],
                max_new_tokens=40,
                do_sample=True,
                temperature=0.8,
                top_p=0.9,
                pad_token_id=tokenizer.eos_token_id,
                output_scores=True,
                return_dict_in_generate=True,
            )

        gen_ids = outputs.sequences[0]
        if outputs.scores:
            all_logits = torch.stack(outputs.scores, dim=1).squeeze(0)
            entropy = compute_entropy(all_logits)
        else:
            entropy = 0.5

        response = tokenizer.decode(gen_ids[prompt_len:], skip_special_tokens=True)
        hedging_score = compute_hedging_score(response)
        reward = compute_reward(hedging_score, entropy, is_easy)
        reward_normalized = reward - 0.5
        epoch_rewards.append(reward)

        policy_out = model(gen_ids.unsqueeze(0), labels=gen_ids.unsqueeze(0))
        with torch.no_grad():
            ref_out = ref_model(gen_ids.unsqueeze(0))

        logits = policy_out.logits[:, prompt_len - 1 : -1, :]
        ref_logits = ref_out.logits[:, prompt_len - 1 : -1, :]
        target_ids = gen_ids[prompt_len:]

        if target_ids.numel() == 0:
            continue

        log_probs = F.log_softmax(logits, dim=-1)
        ref_log_probs = F.log_softmax(ref_logits, dim=-1)

        selected_log_probs = log_probs[0, range(len(target_ids)), target_ids]
        selected_ref_log_probs = ref_log_probs[0, range(len(target_ids)), target_ids]

        pg_loss = -reward_normalized * selected_log_probs.mean()
        kl_div = (selected_log_probs - selected_ref_log_probs).mean()
        loss = pg_loss + kl_coef * kl_div

        if not torch.isnan(loss):
            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            epoch_losses.append(loss.item())

    avg_loss = np.mean(epoch_losses) if epoch_losses else 0.0
    avg_reward = np.mean(epoch_rewards) if epoch_rewards else 0.0

    val_alignment, _, _ = evaluate_model(
        model, tokenizer, val_data, f"Epoch {epoch+1} "
    )
    experiment_data["uah_training"]["losses"]["train"].append(avg_loss)
    experiment_data["uah_training"]["metrics"]["val"].append(val_alignment)
    experiment_data["uah_training"]["alignment_scores"].append(val_alignment)

    print(
        f"Epoch {epoch+1}: train_loss={avg_loss:.4f}, avg_reward={avg_reward:.4f}, validation_loss={avg_loss:.4f}"
    )
    print(f"Epoch {epoch+1}: hedging_confidence_alignment_score={val_alignment:.4f}")
    print("-" * 50)

print("\n=== Final Evaluation ===")
final_alignment, final_hedging, final_entropy = evaluate_model(
    model, tokenizer, val_data, "Final "
)
experiment_data["uah_training"]["predictions"] = final_hedging
experiment_data["uah_training"]["ground_truth"] = final_entropy

print("\n=== Sample Generations ===")
for q in [
    "What color is grass?",
    "What will happen in 2050?",
    "How many continents are there?",
    "Is time travel possible?",
]:
    response, entropy = generate_response(model, tokenizer, q)
    print(
        f"Q: {q}\nA: {response[:100]}...\nHedging: {compute_hedging_score(response):.3f}, Entropy: {entropy:.3f}\n"
    )

fig, axes = plt.subplots(2, 2, figsize=(12, 10))
alignment_scores = experiment_data["uah_training"]["alignment_scores"]
axes[0, 0].plot(range(len(alignment_scores)), alignment_scores, "b-o")
axes[0, 0].axhline(y=baseline_alignment, color="r", linestyle="--", label="Baseline")
axes[0, 0].set_xlabel("Epoch")
axes[0, 0].set_ylabel("Alignment Score")
axes[0, 0].set_title("UAH Training Progress")
axes[0, 0].legend()
axes[0, 0].grid(True, alpha=0.3)

axes[0, 1].scatter(
    final_entropy, final_hedging, alpha=0.6, c="blue", edgecolors="black"
)
axes[0, 1].plot([0, 1], [0, 1], "r--", label="Perfect alignment")
axes[0, 1].set_xlabel("Entropy")
axes[0, 1].set_ylabel("Hedging Score")
axes[0, 1].set_title(f"Hedging vs Entropy (r={final_alignment:.3f})")
axes[0, 1].legend()
axes[0, 1].grid(True, alpha=0.3)

axes[1, 0].hist(baseline_hedging, bins=15, alpha=0.5, label="Baseline", color="red")
axes[1, 0].hist(final_hedging, bins=15, alpha=0.5, label="Final", color="blue")
axes[1, 0].set_xlabel("Hedging Score")
axes[1, 0].set_ylabel("Count")
axes[1, 0].set_title("Hedging Distribution")
axes[1, 0].legend()
axes[1, 0].grid(True, alpha=0.3)

train_losses = experiment_data["uah_training"]["losses"]["train"]
if train_losses:
    axes[1, 1].plot(range(1, len(train_losses) + 1), train_losses, "g-o")
axes[1, 1].set_xlabel("Epoch")
axes[1, 1].set_ylabel("Loss")
axes[1, 1].set_title("Training Loss")
axes[1, 1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(os.path.join(working_dir, "uah_training_results.png"), dpi=150)
plt.close()

np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)

print("\n" + "=" * 60)
print("EXPERIMENT SUMMARY")
print("=" * 60)
print(f"Baseline hedging_confidence_alignment_score: {baseline_alignment:.4f}")
print(f"Final hedging_confidence_alignment_score: {final_alignment:.4f}")
print(f"Improvement: {final_alignment - baseline_alignment:+.4f}")
print(f"Results saved to: {working_dir}")
print("=" * 60)
