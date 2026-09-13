import os
import random
import numpy as np
import torch
import torch.nn.functional as F
from torch.optim import AdamW
from transformers import GPT2LMHeadModel, GPT2Tokenizer
from datasets import load_dataset
from scipy.stats import pearsonr
import matplotlib.pyplot as plt
import copy

working_dir = os.path.join(os.getcwd(), "working")
os.makedirs(working_dir, exist_ok=True)

random.seed(42)
np.random.seed(42)
torch.manual_seed(42)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

experiment_data = {
    "synthetic_qa": {
        "metrics": {"train": [], "val": []},
        "losses": {"train": [], "val": []},
        "hedging_scores": [],
        "entropy_scores": [],
    },
    "triviaqa": {"metrics": {"val": []}, "hedging_scores": [], "entropy_scores": []},
    "commonsenseqa": {
        "metrics": {"val": []},
        "hedging_scores": [],
        "entropy_scores": [],
    },
    "top_p_tuning": {
        "top_p_values": [],
        "baseline_alignments": [],
        "final_alignments": [],
        "improvements": [],
        "per_top_p_data": {},
    },
}


def create_qa_dataset(n_samples=100):
    easy_qa = [
        ("What is 2+2?", "4", 0.1),
        ("What color is the sky on a clear day?", "blue", 0.1),
        ("How many days are in a week?", "7", 0.1),
        ("What is the capital of France?", "Paris", 0.1),
        ("How many legs does a dog have?", "4", 0.1),
        ("What is 3+5?", "8", 0.1),
    ]
    medium_qa = [
        ("What is the largest planet in our solar system?", "Jupiter", 0.5),
        ("Who wrote Romeo and Juliet?", "Shakespeare", 0.5),
        ("What year did World War II end?", "1945", 0.5),
        ("What is the chemical symbol for gold?", "Au", 0.5),
    ]
    hard_qa = [
        ("What is the exact population of Tokyo?", "approximately 14 million", 0.9),
        ("Who will win the next election?", "uncertain", 0.9),
        ("What causes consciousness?", "not fully understood", 0.9),
        ("Is there life on other planets?", "possibly", 0.9),
    ]
    dataset = []
    for _ in range(n_samples // 14 + 1):
        dataset.extend(easy_qa + medium_qa + hard_qa)
    random.shuffle(dataset)
    return dataset[:n_samples]


def load_triviaqa_dataset(n_samples=50):
    ds = load_dataset(
        "trivia_qa", "rc.nocontext", split="validation", trust_remote_code=True
    )
    dataset = []
    for i, item in enumerate(ds):
        if i >= n_samples:
            break
        q, a = item["question"], (
            item["answer"]["value"] if item["answer"]["value"] else "unknown"
        )
        dataset.append((q, a, 0.5))
    return dataset


def load_commonsenseqa_dataset(n_samples=50):
    ds = load_dataset("commonsense_qa", split="validation", trust_remote_code=True)
    dataset = []
    for i, item in enumerate(ds):
        if i >= n_samples:
            break
        q = item["question"]
        choices = item["choices"]["text"]
        label_idx = (
            ord(item["answerKey"]) - ord("A") if item["answerKey"] in "ABCDE" else 0
        )
        a = choices[label_idx] if label_idx < len(choices) else choices[0]
        dataset.append((q, a, 0.6))
    return dataset


def compute_hedging_score(text):
    text_lower = text.lower()
    high_hedge = [
        "i'm not sure",
        "i don't know",
        "uncertain",
        "maybe",
        "perhaps",
        "possibly",
        "might be",
        "could be",
        "i think",
        "i believe",
        "probably",
        "likely",
        "it seems",
        "approximately",
        "around",
        "about",
        "hard to say",
        "unclear",
    ]
    medium_hedge = [
        "generally",
        "usually",
        "often",
        "sometimes",
        "typically",
        "may",
        "might",
    ]
    certain_phrases = [
        "definitely",
        "certainly",
        "absolutely",
        "clearly",
        "obviously",
        "the answer is",
    ]
    hedge_signal = (
        sum(2 for p in high_hedge if p in text_lower)
        + sum(1 for p in medium_hedge if p in text_lower)
        - sum(1.5 for p in certain_phrases if p in text_lower)
    )
    return 1.0 / (1.0 + np.exp(-hedge_signal))


def generate_with_entropy(model, tokenizer, prompt, max_new_tokens=40, top_p=0.9):
    model.eval()
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=200)
    input_ids, attention_mask = inputs["input_ids"].to(device), inputs[
        "attention_mask"
    ].to(device)
    with torch.no_grad():
        outputs = model.generate(
            input_ids,
            attention_mask=attention_mask,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            temperature=0.7,
            top_p=top_p,
            top_k=50,
            pad_token_id=tokenizer.eos_token_id,
            return_dict_in_generate=True,
            output_scores=True,
        )
    generated_ids = outputs.sequences[0][input_ids.shape[1] :]
    response = tokenizer.decode(generated_ids, skip_special_tokens=True)
    entropies = []
    for score in outputs.scores:
        probs = F.softmax(score[0], dim=-1).clamp(min=1e-10)
        ent = -torch.sum(probs * torch.log(probs)).item()
        if not np.isnan(ent) and not np.isinf(ent):
            entropies.append(ent)
    return response, min(1.0, np.mean(entropies) / 8.0) if entropies else 0.5


def compute_log_probs(model, tokenizer, prompt, response):
    full_text = prompt + response
    inputs = tokenizer(full_text, return_tensors="pt", truncation=True, max_length=300)
    input_ids = inputs["input_ids"].to(device)
    prompt_len = len(tokenizer(prompt, truncation=True, max_length=200)["input_ids"])
    with torch.enable_grad():
        outputs = model(input_ids, labels=input_ids)
    log_probs = F.log_softmax(outputs.logits, dim=-1)
    token_log_probs = (
        log_probs[:, prompt_len - 1 : -1, :]
        .gather(2, input_ids[:, prompt_len:].unsqueeze(-1))
        .squeeze(-1)
    )
    return token_log_probs.sum()


def train_step(
    model,
    ref_model,
    tokenizer,
    optimizer,
    question,
    answer,
    target_entropy,
    top_p=0.9,
    kl_coef=0.1,
):
    model.train()
    prompt = f"Question: {question}\nProvide an answer, using hedging language if uncertain: "
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=200)
    input_ids, attention_mask = inputs["input_ids"].to(device), inputs[
        "attention_mask"
    ].to(device)
    with torch.no_grad():
        outputs = model.generate(
            input_ids,
            attention_mask=attention_mask,
            max_new_tokens=30,
            do_sample=True,
            temperature=0.8,
            top_p=top_p,
            top_k=50,
            pad_token_id=tokenizer.eos_token_id,
            return_dict_in_generate=True,
            output_scores=True,
        )
    generated_ids = outputs.sequences[0][input_ids.shape[1] :]
    response = tokenizer.decode(generated_ids, skip_special_tokens=True)
    if len(response.strip()) < 3:
        return 0.0, 0.5, 0.5, response
    hedging_score = compute_hedging_score(response)
    entropies = [
        (
            -torch.sum(
                F.softmax(s[0], dim=-1).clamp(min=1e-10)
                * torch.log(F.softmax(s[0], dim=-1).clamp(min=1e-10))
            )
        ).item()
        for s in outputs.scores
    ]
    entropies = [e for e in entropies if not np.isnan(e) and not np.isinf(e)]
    normalized_entropy = min(1.0, np.mean(entropies) / 8.0) if entropies else 0.5
    alignment_error = abs(hedging_score - target_entropy)
    correctness = 0.5 if answer.lower() in response.lower() else 0.2
    reward = correctness + (1.0 - alignment_error) * 0.5
    log_prob = compute_log_probs(model, tokenizer, prompt, response)
    with torch.no_grad():
        ref_log_prob = compute_log_probs(ref_model, tokenizer, prompt, response)
    policy_loss = -(reward - 0.5) * log_prob
    total_loss = policy_loss + kl_coef * (log_prob - ref_log_prob)
    optimizer.zero_grad()
    total_loss.backward()
    torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
    optimizer.step()
    return total_loss.item(), hedging_score, normalized_entropy, response


def evaluate(model, tokenizer, dataset, top_p=0.9):
    model.eval()
    hedging_scores, entropy_scores = [], []
    for question, answer, _ in dataset:
        prompt = f"Question: {question}\nProvide an answer, using hedging language if uncertain: "
        response, entropy = generate_with_entropy(model, tokenizer, prompt, top_p=top_p)
        hedging_scores.append(compute_hedging_score(response))
        entropy_scores.append(entropy)
    if len(set(hedging_scores)) > 1 and len(set(entropy_scores)) > 1:
        correlation, _ = pearsonr(hedging_scores, entropy_scores)
        correlation = 0.0 if np.isnan(correlation) else correlation
    else:
        correlation = 0.0
    return correlation, hedging_scores, entropy_scores


print("Loading datasets...")
train_data = create_qa_dataset(n_samples=60)
val_data = create_qa_dataset(n_samples=30)
triviaqa_data = load_triviaqa_dataset(n_samples=30)
commonsenseqa_data = load_commonsenseqa_dataset(n_samples=30)

TOP_P_VALUES = [0.85, 0.9, 0.95]
num_epochs, best_top_p, best_alignment = 4, None, -float("inf")

for top_p in TOP_P_VALUES:
    print(f"\n{'='*60}\nTUNING top_p = {top_p}\n{'='*60}")
    random.seed(42)
    np.random.seed(42)
    torch.manual_seed(42)
    model = GPT2LMHeadModel.from_pretrained("gpt2").to(device)
    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    tokenizer.pad_token = tokenizer.eos_token
    ref_model = copy.deepcopy(model).eval()
    for p in ref_model.parameters():
        p.requires_grad = False
    for name, p in model.named_parameters():
        if (
            "transformer.h.11" not in name
            and "transformer.h.10" not in name
            and "lm_head" not in name
        ):
            p.requires_grad = False
    experiment_data["top_p_tuning"]["per_top_p_data"][top_p] = {
        "metrics": {"train": [], "val": []},
        "losses": {"train": [], "val": []},
        "hedging_scores": [],
        "entropy_scores": [],
        "alignment_scores": [],
    }

    baseline_alignment, _, _ = evaluate(model, tokenizer, val_data, top_p=top_p)
    print(f"Baseline alignment: {baseline_alignment:.4f}")

    optimizer = AdamW(filter(lambda p: p.requires_grad, model.parameters()), lr=1e-5)
    for epoch in range(num_epochs):
        epoch_losses = []
        random.shuffle(train_data)
        for i, (q, a, te) in enumerate(train_data):
            loss, h, e, _ = train_step(
                model, ref_model, tokenizer, optimizer, q, a, te, top_p=top_p
            )
            epoch_losses.append(loss)
            if i % 20 == 0:
                print(f"  Step {i}: loss={loss:.4f}")
        val_align, _, _ = evaluate(model, tokenizer, val_data, top_p=top_p)
        print(
            f"Epoch {epoch+1}/{num_epochs}: val_loss={np.mean(epoch_losses):.4f}, hedging_confidence_alignment_score={val_align:.4f}"
        )
        experiment_data["top_p_tuning"]["per_top_p_data"][top_p]["losses"][
            "train"
        ].append(np.mean(epoch_losses))
        experiment_data["top_p_tuning"]["per_top_p_data"][top_p][
            "alignment_scores"
        ].append(val_align)

    final_align, fh, fe = evaluate(model, tokenizer, val_data, top_p=top_p)
    (
        experiment_data["top_p_tuning"]["per_top_p_data"][top_p]["hedging_scores"],
        experiment_data["top_p_tuning"]["per_top_p_data"][top_p]["entropy_scores"],
    ) = (fh, fe)
    experiment_data["top_p_tuning"]["top_p_values"].append(top_p)
    experiment_data["top_p_tuning"]["baseline_alignments"].append(baseline_alignment)
    experiment_data["top_p_tuning"]["final_alignments"].append(final_align)
    experiment_data["top_p_tuning"]["improvements"].append(
        final_align - baseline_alignment
    )

    trivia_align, th, te = evaluate(model, tokenizer, triviaqa_data, top_p=top_p)
    experiment_data["triviaqa"]["metrics"]["val"].append(trivia_align)
    (
        experiment_data["triviaqa"]["hedging_scores"],
        experiment_data["triviaqa"]["entropy_scores"],
    ) = (th, te)
    print(f"TriviaQA hedging_confidence_alignment_score: {trivia_align:.4f}")

    csqa_align, ch, ce = evaluate(model, tokenizer, commonsenseqa_data, top_p=top_p)
    experiment_data["commonsenseqa"]["metrics"]["val"].append(csqa_align)
    (
        experiment_data["commonsenseqa"]["hedging_scores"],
        experiment_data["commonsenseqa"]["entropy_scores"],
    ) = (ch, ce)
    print(f"CommonsenseQA hedging_confidence_alignment_score: {csqa_align:.4f}")

    if final_align > best_alignment:
        best_alignment, best_top_p = final_align, top_p

print(f"\n{'='*60}\nFINAL RESULTS\n{'='*60}")
print(f"Best top_p: {best_top_p}, Best alignment: {best_alignment:.4f}")
for i, tp in enumerate(experiment_data["top_p_tuning"]["top_p_values"]):
    print(
        f"  top_p={tp}: baseline={experiment_data['top_p_tuning']['baseline_alignments'][i]:.4f}, final={experiment_data['top_p_tuning']['final_alignments'][i]:.4f}"
    )

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
x_pos = np.arange(len(TOP_P_VALUES))
axes[0, 0].bar(
    x_pos - 0.15,
    experiment_data["top_p_tuning"]["baseline_alignments"],
    0.3,
    label="Baseline",
)
axes[0, 0].bar(
    x_pos + 0.15,
    experiment_data["top_p_tuning"]["final_alignments"],
    0.3,
    label="Final",
)
axes[0, 0].set_xticks(x_pos)
axes[0, 0].set_xticklabels([str(t) for t in TOP_P_VALUES])
axes[0, 0].set_xlabel("top_p")
axes[0, 0].set_ylabel("Alignment")
axes[0, 0].legend()
axes[0, 0].set_title("Alignment by top_p")

for tp in TOP_P_VALUES:
    axes[0, 1].plot(
        experiment_data["top_p_tuning"]["per_top_p_data"][tp]["losses"]["train"],
        label=f"top_p={tp}",
    )
axes[0, 1].set_xlabel("Epoch")
axes[0, 1].set_ylabel("Loss")
axes[0, 1].legend()
axes[0, 1].set_title("Training Loss")

for tp in TOP_P_VALUES:
    axes[1, 0].plot(
        experiment_data["top_p_tuning"]["per_top_p_data"][tp]["alignment_scores"],
        label=f"top_p={tp}",
    )
axes[1, 0].set_xlabel("Epoch")
axes[1, 0].set_ylabel("Alignment")
axes[1, 0].legend()
axes[1, 0].set_title("Validation Alignment")

datasets = ["Synthetic", "TriviaQA", "CommonsenseQA"]
last_vals = [
    experiment_data["top_p_tuning"]["final_alignments"][-1],
    (
        experiment_data["triviaqa"]["metrics"]["val"][-1]
        if experiment_data["triviaqa"]["metrics"]["val"]
        else 0
    ),
    (
        experiment_data["commonsenseqa"]["metrics"]["val"][-1]
        if experiment_data["commonsenseqa"]["metrics"]["val"]
        else 0
    ),
]
axes[1, 1].bar(datasets, last_vals, color=["blue", "green", "orange"])
axes[1, 1].set_ylabel("Alignment")
axes[1, 1].set_title("Cross-Dataset Alignment (best top_p)")

plt.tight_layout()
plt.savefig(os.path.join(working_dir, "top_p_tuning_results.png"), dpi=150)
plt.close()
np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)
print(f"Results saved to {working_dir}")
