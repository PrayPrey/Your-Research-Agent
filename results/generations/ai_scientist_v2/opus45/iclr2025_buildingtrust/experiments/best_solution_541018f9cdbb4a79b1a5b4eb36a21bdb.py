import os
import random
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.optim import AdamW
from transformers import GPT2LMHeadModel, GPT2Tokenizer
from datasets import load_dataset
from scipy.stats import pearsonr, spearmanr
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
    "no_temperature_annealing": {
        "synthetic_qa": {
            "metrics": {"train": [], "val": []},
            "losses": {"train": [], "val": []},
            "hedging_scores": [],
            "entropy_scores": [],
        },
        "triviaqa": {
            "metrics": {"val": []},
            "hedging_scores": [],
            "entropy_scores": [],
        },
        "commonsenseqa": {
            "metrics": {"val": []},
            "hedging_scores": [],
            "entropy_scores": [],
        },
        "sciq": {"metrics": {"val": []}, "hedging_scores": [], "entropy_scores": []},
        "training_curves": {
            "epochs": [],
            "train_loss": [],
            "val_alignment": [],
            "spearman": [],
            "reward": [],
            "kl_div": [],
        },
        "calibration_bins": {
            "bins": [],
            "hedging_means": [],
            "entropy_means": [],
            "counts": [],
        },
    },
}


class NeuralHedgingClassifier(nn.Module):
    def __init__(self):
        super().__init__()
        self.hedge_patterns = [
            (["i'm not sure", "i'm uncertain", "hard to say"], 0.95),
            (["maybe", "perhaps", "possibly", "might be", "might"], 0.85),
            (["could be", "may be", "potentially", "could"], 0.75),
            (["probably", "likely", "i think", "think"], 0.65),
            (["seems", "appears", "suggests"], 0.55),
            (["generally", "usually", "often", "typically"], 0.45),
            (["i believe", "in my view", "believe"], 0.40),
            (["is", "the answer is", "it's", "was"], 0.25),
            (["definitely", "certainly", "absolutely", "clearly"], 0.12),
            (["i know", "i'm certain", "without doubt", "for sure"], 0.05),
        ]
        self.fc = nn.Sequential(
            nn.Linear(len(self.hedge_patterns) + 3, 64),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(64, 16),
            nn.ReLU(),
            nn.Linear(16, 1),
            nn.Sigmoid(),
        )

    def extract_features(self, text):
        text_lower = text.lower()
        features = [
            min(sum(1 for p in patterns if p in text_lower), 2) / 2.0
            for patterns, _ in self.hedge_patterns
        ]
        features.append(text_lower.count("?") / 3.0)
        features.append(min(len(text.split()), 30) / 30.0)
        features.append(
            1.0 if any(w in text_lower for w in ["not", "don't", "uncertain"]) else 0.0
        )
        return torch.tensor(features, dtype=torch.float32)

    def forward(self, text):
        return self.fc(self.extract_features(text).to(device).unsqueeze(0)).squeeze()

    def rule_score(self, text):
        text_lower = text.lower()
        total, wsum = 0.0, 0.0
        for patterns, score in self.hedge_patterns:
            for p in patterns:
                if p in text_lower:
                    w = 1.0 + 0.3 * text_lower.count(p)
                    wsum += score * w
                    total += w
        return wsum / total if total > 0 else 0.5


hedging_classifier = NeuralHedgingClassifier().to(device)
hedge_opt = AdamW(hedging_classifier.parameters(), lr=2e-3)

train_data = [
    ("I'm not sure, but maybe around 5", 0.92),
    ("Perhaps it could be Paris", 0.82),
    ("Possibly the answer is 42", 0.78),
    ("I think it's probably blue", 0.62),
    ("It seems to be correct", 0.52),
    ("Generally speaking, yes", 0.42),
    ("The answer is definitely 7", 0.15),
    ("I know for certain it's red", 0.08),
    ("It might be Shakespeare", 0.72),
    ("Could be around 1945", 0.72),
    ("Absolutely, it's Jupiter", 0.12),
    ("Clearly the capital is London", 0.18),
    ("I believe it's probably true", 0.52),
    ("Maybe, but I'm uncertain", 0.88),
    ("Paris is the answer", 0.22),
    ("The result is 42", 0.20),
    ("I'm fairly confident it's blue", 0.35),
    ("It's hard to say for sure", 0.85),
]

for _ in range(150):
    for text, target in train_data:
        pred = hedging_classifier(text)
        loss = F.mse_loss(pred, torch.tensor(target, device=device))
        hedge_opt.zero_grad()
        loss.backward()
        hedge_opt.step()


def compute_hedging_score(text):
    with torch.no_grad():
        neural = hedging_classifier(text).item()
    rule = hedging_classifier.rule_score(text)
    return np.clip(0.55 * neural + 0.45 * rule, 0.05, 0.95)


def normalize_entropy(raw, max_ent=8.0):
    return np.clip(np.log1p(raw * 1.5) / np.log1p(max_ent), 0.0, 1.0)


def create_qa_dataset(n=100):
    templates = [
        ("What is 2+2?", "4", 0.1),
        ("What color is the sky?", "blue", 0.1),
        ("Days in a week?", "7", 0.1),
        ("Capital of France?", "Paris", 0.15),
        ("Largest planet?", "Jupiter", 0.4),
        ("Who wrote Hamlet?", "Shakespeare", 0.4),
        ("Year WWII ended?", "1945", 0.45),
        ("Speed of light?", "300000 km/s", 0.5),
        ("What causes earthquakes?", "tectonic plates", 0.6),
        ("Why is sky blue?", "Rayleigh scattering", 0.65),
        ("What is dark matter?", "unknown substance", 0.85),
        ("Intelligent life elsewhere?", "possibly", 0.9),
        ("What causes consciousness?", "not fully understood", 0.95),
    ]
    ds = []
    for _ in range(n // len(templates) + 1):
        ds.extend(templates)
    random.shuffle(ds)
    return ds[:n]


def load_triviaqa(n=40):
    ds = load_dataset(
        "trivia_qa", "rc.nocontext", split="validation", trust_remote_code=True
    )
    return [
        (item["question"], item["answer"]["value"] or "unknown", 0.5)
        for item in list(ds)[:n]
    ]


def load_commonsenseqa(n=40):
    ds = load_dataset("commonsense_qa", split="validation", trust_remote_code=True)
    out = []
    for item in list(ds)[:n]:
        idx = ord(item["answerKey"]) - ord("A") if item["answerKey"] in "ABCDE" else 0
        out.append(
            (
                item["question"],
                item["choices"]["text"][min(idx, len(item["choices"]["text"]) - 1)],
                0.6,
            )
        )
    return out


def load_sciq(n=40):
    ds = load_dataset("sciq", split="validation", trust_remote_code=True)
    return [(item["question"], item["correct_answer"], 0.5) for item in list(ds)[:n]]


def generate_response(model, tokenizer, prompt, temp=0.8):
    model.eval()
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=150)
    input_ids = inputs["input_ids"].to(device)
    with torch.no_grad():
        outputs = model.generate(
            input_ids,
            max_new_tokens=25,
            do_sample=True,
            temperature=temp,
            top_p=0.9,
            pad_token_id=tokenizer.eos_token_id,
            return_dict_in_generate=True,
            output_scores=True,
        )
    response = tokenizer.decode(
        outputs.sequences[0][input_ids.shape[1] :], skip_special_tokens=True
    )
    ents = [
        (
            -torch.sum(
                F.softmax(s[0], -1).clamp(1e-10)
                * torch.log(F.softmax(s[0], -1).clamp(1e-10))
            )
        ).item()
        for s in outputs.scores
    ]
    ents = [e for e in ents if not np.isnan(e) and not np.isinf(e)]
    return response, normalize_entropy(np.mean(ents)) if ents else 0.5


def compute_kl_div(model, ref_model, input_ids):
    with torch.no_grad():
        ref_logits = ref_model(input_ids).logits
    logits = model(input_ids).logits
    ref_probs = F.softmax(ref_logits, dim=-1)
    log_probs = F.log_softmax(logits, dim=-1)
    return F.kl_div(log_probs, ref_probs, reduction="batchmean")


def train_step(
    model,
    ref_model,
    tokenizer,
    optimizer,
    q,
    a,
    hedge_buffer,
    ent_buffer,
    reward_baseline,
    temp,
):
    model.train()
    prompt = f"Question: {q}\nAnswer: "
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=150)
    input_ids = inputs["input_ids"].to(device)

    with torch.no_grad():
        outputs = model.generate(
            input_ids,
            max_new_tokens=25,
            do_sample=True,
            temperature=temp,
            top_p=0.9,
            pad_token_id=tokenizer.eos_token_id,
            return_dict_in_generate=True,
            output_scores=True,
        )
    response = tokenizer.decode(
        outputs.sequences[0][input_ids.shape[1] :], skip_special_tokens=True
    )
    if len(response.strip()) < 2:
        return 0.0, 0.5, 0.5, 0.0, reward_baseline

    hedge_score = compute_hedging_score(response)
    ents = [
        (
            -torch.sum(
                F.softmax(s[0], -1).clamp(1e-10)
                * torch.log(F.softmax(s[0], -1).clamp(1e-10))
            )
        ).item()
        for s in outputs.scores
    ]
    ents = [e for e in ents if not np.isnan(e) and not np.isinf(e)]
    entropy = normalize_entropy(np.mean(ents)) if ents else 0.5

    hedge_buffer.append(hedge_score)
    ent_buffer.append(entropy)

    align_reward = 1.0 - abs(hedge_score - entropy)
    corr_reward = 0.0
    if len(hedge_buffer) >= 8:
        try:
            corr, _ = spearmanr(hedge_buffer[-25:], ent_buffer[-25:])
            corr_reward = max(0, corr) * 0.5 if not np.isnan(corr) else 0.0
        except:
            pass

    diversity_bonus = 0.0
    if len(hedge_buffer) >= 5:
        recent_std = np.std(hedge_buffer[-10:])
        diversity_bonus = min(recent_std * 2.0, 0.2)

    correctness = 0.4 if a.lower()[:8] in response.lower() else 0.15
    reward = (
        0.35 * correctness
        + 0.35 * align_reward
        + 0.15 * corr_reward
        + 0.15 * diversity_bonus
    )

    full_text = prompt + response
    full_inputs = tokenizer(
        full_text, return_tensors="pt", truncation=True, max_length=200
    )
    full_ids = full_inputs["input_ids"].to(device)
    prompt_len = input_ids.shape[1]

    kl_div = compute_kl_div(model, ref_model, full_ids)

    with torch.enable_grad():
        logits = model(full_ids).logits
    log_probs = F.log_softmax(logits, dim=-1)
    if full_ids.shape[1] > prompt_len:
        token_lp = (
            log_probs[:, prompt_len - 1 : -1]
            .gather(2, full_ids[:, prompt_len:].unsqueeze(-1))
            .squeeze(-1)
        )
        log_prob = token_lp.sum()
    else:
        log_prob = torch.tensor(0.0, device=device, requires_grad=True)

    advantage = reward - reward_baseline
    policy_loss = -advantage * log_prob
    kl_penalty = 0.01 * kl_div
    loss = policy_loss + kl_penalty

    optimizer.zero_grad()
    loss.backward()
    torch.nn.utils.clip_grad_norm_(model.parameters(), 0.5)
    optimizer.step()

    new_baseline = 0.95 * reward_baseline + 0.05 * reward
    return loss.item(), hedge_score, entropy, kl_div.item(), new_baseline


def evaluate(model, tokenizer, dataset):
    model.eval()
    h_scores, e_scores = [], []
    for q, a, _ in dataset:
        response, entropy = generate_response(
            model, tokenizer, f"Question: {q}\nAnswer: "
        )
        h_scores.append(compute_hedging_score(response))
        e_scores.append(entropy)

    if len(set(h_scores)) > 1 and len(set(e_scores)) > 1:
        p_corr, _ = pearsonr(h_scores, e_scores)
        s_corr, _ = spearmanr(h_scores, e_scores)
        p_corr = 0.0 if np.isnan(p_corr) else p_corr
        s_corr = 0.0 if np.isnan(s_corr) else s_corr
    else:
        p_corr, s_corr = 0.0, 0.0

    alignment = 1.0 - np.mean(np.abs(np.array(h_scores) - np.array(e_scores)))
    return p_corr, s_corr, alignment, h_scores, e_scores


print("Loading datasets...")
synthetic_train, synthetic_val = create_qa_dataset(55), create_qa_dataset(20)
triviaqa_data, commonsenseqa_data, sciq_data = (
    load_triviaqa(30),
    load_commonsenseqa(30),
    load_sciq(30),
)
mixed_train = synthetic_train[:30] + triviaqa_data[:12] + sciq_data[:8]
random.shuffle(mixed_train)

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

optimizer = AdamW(filter(lambda p: p.requires_grad, model.parameters()), lr=5e-6)

print("\n" + "=" * 50 + "\nBASELINE (before training)\n" + "=" * 50)
base_p, base_s, base_align, _, _ = evaluate(model, tokenizer, synthetic_val)
print(
    f"Baseline - Alignment: {base_align:.4f}, Pearson: {base_p:.4f}, Spearman: {base_s:.4f}"
)

hedge_buffer, ent_buffer = [], []
reward_baseline = 0.3
best_checkpoint = {"state": None, "score": 0.0, "epoch": 0}

print(
    "\n"
    + "=" * 50
    + "\nABLATION: NO TEMPERATURE ANNEALING (fixed temp=0.8)\n"
    + "=" * 50
)
for epoch in range(8):
    # ABLATION: Fixed temperature instead of annealing
    temp = 0.8  # Original: temp = 0.9 - epoch * 0.05

    losses, kls = [], []
    random.shuffle(mixed_train)
    for q, a, _ in mixed_train:
        loss, h, e, kl, reward_baseline = train_step(
            model,
            ref_model,
            tokenizer,
            optimizer,
            q,
            a,
            hedge_buffer,
            ent_buffer,
            reward_baseline,
            temp,
        )
        losses.append(loss)
        kls.append(kl)

    val_p, val_s, val_align, vh, ve = evaluate(model, tokenizer, synthetic_val)
    avg_loss, avg_kl = np.mean(losses), np.mean(kls)

    experiment_data["no_temperature_annealing"]["training_curves"]["epochs"].append(
        epoch + 1
    )
    experiment_data["no_temperature_annealing"]["training_curves"]["train_loss"].append(
        avg_loss
    )
    experiment_data["no_temperature_annealing"]["training_curves"][
        "val_alignment"
    ].append(val_align)
    experiment_data["no_temperature_annealing"]["training_curves"]["spearman"].append(
        val_s
    )
    experiment_data["no_temperature_annealing"]["training_curves"]["kl_div"].append(
        avg_kl
    )

    score = val_align + max(0, val_s) * 0.3
    if score > best_checkpoint["score"]:
        best_checkpoint = {
            "state": copy.deepcopy(model.state_dict()),
            "score": score,
            "epoch": epoch + 1,
        }

    print(
        f"Epoch {epoch+1}/8 (temp={temp:.2f}): loss={avg_loss:.4f}, alignment={val_align:.4f}, spearman={val_s:.4f}, kl={avg_kl:.4f}"
    )

if best_checkpoint["state"]:
    model.load_state_dict(best_checkpoint["state"])
    print(f"\nLoaded best checkpoint from epoch {best_checkpoint['epoch']}")

print("\n" + "=" * 50 + "\nFINAL EVALUATION (No Temperature Annealing)\n" + "=" * 50)
results = {}
for name, data in [
    ("Synthetic", synthetic_val),
    ("TriviaQA", triviaqa_data),
    ("CommonsenseQA", commonsenseqa_data),
    ("SciQ", sciq_data),
]:
    p, s, align, h, e = evaluate(model, tokenizer, data)
    key = name.lower().replace(" ", "_")
    if key == "synthetic":
        key = "synthetic_qa"
    experiment_data["no_temperature_annealing"][key]["metrics"]["val"].append(align)
    experiment_data["no_temperature_annealing"][key]["hedging_scores"] = h
    experiment_data["no_temperature_annealing"][key]["entropy_scores"] = e
    results[name] = {"pearson": p, "spearman": s, "align": align, "h": h, "e": e}
    print(f"{name} - alignment={align:.4f}, Pearson={p:.4f}, Spearman={s:.4f}")

all_h = sum([r["h"] for r in results.values()], [])
all_e = sum([r["e"] for r in results.values()], [])
sorted_idx = np.argsort(all_e)
n_bins = 5
for i in range(n_bins):
    start, end = i * len(sorted_idx) // n_bins, (i + 1) * len(sorted_idx) // n_bins
    idx = sorted_idx[start:end]
    experiment_data["no_temperature_annealing"]["calibration_bins"][
        "hedging_means"
    ].append(np.mean([all_h[j] for j in idx]))
    experiment_data["no_temperature_annealing"]["calibration_bins"][
        "entropy_means"
    ].append(np.mean([all_e[j] for j in idx]))

fig, axes = plt.subplots(2, 3, figsize=(15, 10))
fig.suptitle("Ablation: No Temperature Annealing (Fixed temp=0.8)", fontsize=14)

axes[0, 0].plot(
    experiment_data["no_temperature_annealing"]["training_curves"]["epochs"],
    experiment_data["no_temperature_annealing"]["training_curves"]["train_loss"],
    "b-o",
)
axes[0, 0].set_xlabel("Epoch")
axes[0, 0].set_ylabel("Loss")
axes[0, 0].set_title("Training Loss")

axes[0, 1].plot(
    experiment_data["no_temperature_annealing"]["training_curves"]["epochs"],
    experiment_data["no_temperature_annealing"]["training_curves"]["val_alignment"],
    "g-o",
    label="Alignment",
)
axes[0, 1].plot(
    experiment_data["no_temperature_annealing"]["training_curves"]["epochs"],
    experiment_data["no_temperature_annealing"]["training_curves"]["spearman"],
    "r-s",
    label="Spearman",
)
axes[0, 1].legend()
axes[0, 1].set_title("Validation Metrics")

datasets = list(results.keys())
axes[0, 2].bar(
    datasets,
    [results[d]["align"] for d in datasets],
    color=["blue", "green", "orange", "purple"],
)
axes[0, 2].axhline(0.5, color="r", linestyle="--")
axes[0, 2].set_title("Cross-Dataset Alignment")

for name, c in zip(datasets, ["blue", "green", "orange", "purple"]):
    axes[1, 0].scatter(
        results[name]["e"], results[name]["h"], alpha=0.6, label=name, c=c, s=30
    )
axes[1, 0].plot([0, 1], [0, 1], "k--")
axes[1, 0].legend()
axes[1, 0].set_title("Hedging vs Entropy")

axes[1, 1].plot(
    experiment_data["no_temperature_annealing"]["calibration_bins"]["entropy_means"],
    experiment_data["no_temperature_annealing"]["calibration_bins"]["hedging_means"],
    "bo-",
    markersize=10,
)
axes[1, 1].plot([0, 1], [0, 1], "k--")
axes[1, 1].set_title("Calibration Curve")

x = np.arange(len(datasets))
axes[1, 2].bar(
    x - 0.15, [results[d]["pearson"] for d in datasets], 0.3, label="Pearson"
)
axes[1, 2].bar(
    x + 0.15, [results[d]["spearman"] for d in datasets], 0.3, label="Spearman"
)
axes[1, 2].set_xticks(x)
axes[1, 2].set_xticklabels(datasets)
axes[1, 2].legend()
axes[1, 2].set_title("Correlations")

plt.tight_layout()
plt.savefig(os.path.join(working_dir, "no_temperature_annealing_results.png"), dpi=150)
plt.close()

np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)
print(
    f"\nFINAL (No Temp Annealing): Average alignment = {np.mean([results[d]['align'] for d in datasets]):.4f}"
)
print("\nAblation study complete. Results saved to experiment_data.npy")
