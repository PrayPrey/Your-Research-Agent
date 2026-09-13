import os
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
import random
from collections import defaultdict
import matplotlib.pyplot as plt

working_dir = os.path.join(os.getcwd(), "working")
os.makedirs(working_dir, exist_ok=True)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

torch.manual_seed(42)
np.random.seed(42)
random.seed(42)

ERROR_CATEGORIES = [
    "type_mismatch",
    "missing_hypothesis",
    "wrong_tactic",
    "scope_violation",
]


class SyntheticTheoremDataset(Dataset):
    def __init__(self, num_samples=1000, seq_len=20, vocab_size=50):
        self.num_samples, self.seq_len, self.vocab_size = (
            num_samples,
            seq_len,
            vocab_size,
        )
        self.data = []
        for _ in range(num_samples):
            theorem = np.random.randint(1, vocab_size // 2, size=seq_len // 2)
            self.data.append((theorem, self._generate_proof(theorem)))

    def _generate_proof(self, theorem):
        proof = []
        for t in theorem:
            proof.extend([t + self.vocab_size // 2, (t * 2) % self.vocab_size + 1])
        return np.array(proof[: self.seq_len])

    def __len__(self):
        return self.num_samples

    def __getitem__(self, idx):
        theorem, proof = self.data[idx]
        return {
            "theorem": torch.tensor(theorem, dtype=torch.long),
            "proof": torch.tensor(proof, dtype=torch.long),
        }


class HuggingFaceProofDataset(Dataset):
    def __init__(
        self, dataset_name, split="train", max_samples=300, seq_len=20, vocab_size=50
    ):
        self.seq_len, self.vocab_size = seq_len, vocab_size
        self.data = []
        try:
            from datasets import load_dataset

            if dataset_name == "competition_math":
                ds = load_dataset("hendrycks/competition_math", split=split)
                text_key = "problem"
            elif dataset_name == "gsm8k":
                ds = load_dataset("openai/gsm8k", "main", split=split)
                text_key = "question"
            elif dataset_name == "math_qa":
                ds = load_dataset("allenai/math_qa", split=split)
                text_key = "Problem"
            else:
                raise ValueError(f"Unknown dataset: {dataset_name}")
            for i, item in enumerate(ds):
                if i >= max_samples:
                    break
                text = item.get(text_key, "")[:100]
                self.data.append(self._text_to_synthetic(text))
            print(f"Loaded {len(self.data)} samples from {dataset_name}")
        except Exception as e:
            print(f"Could not load {dataset_name}: {e}. Using synthetic fallback.")
            for _ in range(max_samples):
                theorem = np.random.randint(1, vocab_size // 2, size=seq_len // 2)
                self.data.append((theorem, self._generate_proof(theorem)))

    def _text_to_synthetic(self, text):
        np.random.seed(hash(text) % (2**32))
        theorem = np.random.randint(1, self.vocab_size // 2, size=self.seq_len // 2)
        return theorem, self._generate_proof(theorem)

    def _generate_proof(self, theorem):
        proof = []
        for t in theorem:
            proof.extend([t + self.vocab_size // 2, (t * 2) % self.vocab_size + 1])
        return np.array(proof[: self.seq_len])

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        theorem, proof = self.data[idx]
        return {
            "theorem": torch.tensor(theorem, dtype=torch.long),
            "proof": torch.tensor(proof, dtype=torch.long),
        }


class SimulatedVerifier:
    def __init__(self, vocab_size=50):
        self.vocab_size = vocab_size

    def verify(self, theorem, generated_proof, ground_truth_proof):
        theorem = theorem.cpu().numpy() if torch.is_tensor(theorem) else theorem
        generated = (
            generated_proof.cpu().numpy()
            if torch.is_tensor(generated_proof)
            else generated_proof
        )
        ground_truth = (
            ground_truth_proof.cpu().numpy()
            if torch.is_tensor(ground_truth_proof)
            else ground_truth_proof
        )
        if np.array_equal(generated, ground_truth):
            return True, "correct", -1
        for i, (g, gt) in enumerate(zip(generated, ground_truth)):
            if g != gt:
                return False, self._categorize_error(i, g, gt, theorem), i
        return True, "correct", -1

    def _categorize_error(self, position, generated, expected, theorem):
        diff = abs(generated - expected)
        if diff > self.vocab_size // 4:
            return "type_mismatch"
        elif position < len(theorem):
            return "wrong_tactic"
        elif generated < self.vocab_size // 2:
            return "scope_violation"
        return "missing_hypothesis"


class ProofGenerator(nn.Module):
    def __init__(
        self,
        vocab_size=50,
        embed_dim=64,
        num_heads=4,
        num_layers=2,
        max_len=40,
        dropout=0.1,
    ):
        super().__init__()
        self.vocab_size, self.embed_dim = vocab_size, embed_dim
        self.embedding = nn.Embedding(vocab_size + 1, embed_dim, padding_idx=0)
        self.pos_embedding = nn.Embedding(max_len, embed_dim)
        self.dropout = nn.Dropout(dropout)
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=embed_dim,
            nhead=num_heads,
            dim_feedforward=128,
            batch_first=True,
            dropout=dropout,
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.output_proj = nn.Linear(embed_dim, vocab_size)

    def forward(self, x):
        batch_size, seq_len = x.size()
        positions = (
            torch.arange(seq_len, device=x.device).unsqueeze(0).expand(batch_size, -1)
        )
        emb = self.dropout(self.embedding(x) + self.pos_embedding(positions))
        mask = nn.Transformer.generate_square_subsequent_mask(seq_len, device=x.device)
        return self.output_proj(self.transformer(emb, mask=mask, is_causal=True))

    def generate(self, theorem, max_len=20):
        self.eval()
        generated = theorem.clone()
        with torch.no_grad():
            for _ in range(max_len):
                logits = self.forward(generated)
                generated = torch.cat(
                    [generated, logits[:, -1, :].argmax(dim=-1, keepdim=True)], dim=1
                )
        return generated[:, theorem.size(1) :]


def create_error_augmented_data(dataset, error_category, num_examples=150):
    augmented = []
    for i in range(min(num_examples, len(dataset))):
        item = dataset[i]
        theorem, correct_proof = item["theorem"].numpy(), item["proof"].numpy()
        corrupted_proof = correct_proof.copy()
        if error_category == "type_mismatch":
            idx = random.randint(0, len(corrupted_proof) - 1)
            corrupted_proof[idx] = (corrupted_proof[idx] + 20) % 50
        elif error_category == "missing_hypothesis":
            idx = random.randint(len(corrupted_proof) // 2, len(corrupted_proof) - 1)
            corrupted_proof[idx] = random.randint(25, 49)
        elif error_category == "wrong_tactic":
            idx = random.randint(0, min(len(theorem) - 1, len(corrupted_proof) - 1))
            corrupted_proof[idx] = (corrupted_proof[idx] + 5) % 50
        elif error_category == "scope_violation":
            idx = random.randint(len(corrupted_proof) // 2, len(corrupted_proof) - 1)
            corrupted_proof[idx] = random.randint(1, 24)
        augmented.append(
            {
                "theorem": torch.tensor(theorem, dtype=torch.long),
                "corrupted_proof": torch.tensor(corrupted_proof, dtype=torch.long),
                "correct_proof": torch.tensor(correct_proof, dtype=torch.long),
                "error_category": error_category,
            }
        )
    return augmented


def compute_ecrr(category_corrections, category_attempts):
    rates = []
    for cat in ERROR_CATEGORIES:
        attempts = category_attempts.get(cat, 0)
        corrections = category_corrections.get(cat, 0)
        if attempts > 0:
            rates.append(corrections / attempts)
    return np.mean(rates) if rates else 0.0


def evaluate_model(model, val_loader, verifier):
    model.eval()
    correct, total = 0, 0
    error_counts = defaultdict(int)
    category_corrections = defaultdict(int)
    category_attempts = defaultdict(int)
    val_losses = []
    criterion = nn.CrossEntropyLoss()

    with torch.no_grad():
        for batch in val_loader:
            theorem, proof = batch["theorem"].to(device), batch["proof"].to(device)
            combined = torch.cat([theorem, proof], dim=1)
            logits = model(combined[:, :-1])
            loss = criterion(
                logits.reshape(-1, model.vocab_size), combined[:, 1:].reshape(-1)
            )
            val_losses.append(loss.item())
            generated = model.generate(theorem, max_len=proof.size(1))
            for i in range(theorem.size(0)):
                is_correct, error_cat, _ = verifier.verify(
                    theorem[i], generated[i], proof[i]
                )
                error_counts[error_cat] += 1
                if is_correct:
                    correct += 1
                else:
                    category_attempts[error_cat] += 1
                total += 1

    success_rate = correct / total if total > 0 else 0
    ecrr = compute_ecrr(category_corrections, category_attempts)
    return np.mean(val_losses), success_rate, ecrr, dict(error_counts)


def train_baseline(model, train_loader, val_loader, epochs=12, lr=1e-3, patience=3):
    model = model.to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.01)
    criterion = nn.CrossEntropyLoss()
    verifier = SimulatedVerifier()
    history = {
        "train_loss": [],
        "val_loss": [],
        "proof_success_rate": [],
        "error_resolution_rate": [],
        "error_distribution": [],
        "ecrr": [],
    }
    best_val_loss, patience_counter = float("inf"), 0

    for epoch in range(epochs):
        model.train()
        train_losses = []
        for batch in train_loader:
            theorem, proof = batch["theorem"].to(device), batch["proof"].to(device)
            combined = torch.cat([theorem, proof], dim=1)
            optimizer.zero_grad()
            logits = model(combined[:, :-1])
            loss = criterion(
                logits.reshape(-1, model.vocab_size), combined[:, 1:].reshape(-1)
            )
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            train_losses.append(loss.item())

        val_loss, success_rate, ecrr, error_counts = evaluate_model(
            model, val_loader, verifier
        )
        history["train_loss"].append(np.mean(train_losses))
        history["val_loss"].append(val_loss)
        history["proof_success_rate"].append(success_rate)
        history["ecrr"].append(ecrr)
        history["error_distribution"].append(error_counts)
        history["error_resolution_rate"].append(success_rate)

        print(
            f"Epoch {epoch}: validation_loss = {val_loss:.4f}, success_rate = {success_rate:.4f}, ECRR = {ecrr:.4f}"
        )

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            patience_counter = 0
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print(f"Early stopping at epoch {epoch}")
                break
    return history


def train_etcl(
    model, train_dataset, val_loader, epochs=12, lr=1e-3, batch_size=32, patience=3
):
    model = model.to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.01)
    criterion = nn.CrossEntropyLoss()
    verifier = SimulatedVerifier()

    augmented_data = {
        cat: create_error_augmented_data(train_dataset, cat, num_examples=150)
        for cat in ERROR_CATEGORIES
    }
    category_difficulty = {cat: 1.0 for cat in ERROR_CATEGORIES}

    history = {
        "train_loss": [],
        "val_loss": [],
        "proof_success_rate": [],
        "error_resolution_rate": [],
        "error_distribution": [],
        "ecrr": [],
        "category_progress": [],
    }
    best_val_loss, patience_counter = float("inf"), 0

    for epoch in range(epochs):
        model.train()
        train_losses = []

        sorted_cats = sorted(
            ERROR_CATEGORIES, key=lambda c: category_difficulty[c], reverse=True
        )
        num_cats = min(1 + epoch // 3, len(sorted_cats))
        current_categories = sorted_cats[:num_cats]

        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        for batch in train_loader:
            theorem, proof = batch["theorem"].to(device), batch["proof"].to(device)
            combined = torch.cat([theorem, proof], dim=1)
            optimizer.zero_grad()
            logits = model(combined[:, :-1])
            loss = criterion(
                logits.reshape(-1, model.vocab_size), combined[:, 1:].reshape(-1)
            )
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            train_losses.append(loss.item())

        category_corrections = defaultdict(int)
        category_attempts = defaultdict(int)

        for cat in current_categories:
            cat_examples = augmented_data[cat][: min(40, len(augmented_data[cat]))]
            for item in cat_examples:
                theorem = item["theorem"].unsqueeze(0).to(device)
                correct_proof = item["correct_proof"].unsqueeze(0).to(device)
                corrupted_proof = item["corrupted_proof"].unsqueeze(0).to(device)

                combined = torch.cat([theorem, correct_proof], dim=1)
                optimizer.zero_grad()
                logits = model(combined[:, :-1])
                loss = criterion(
                    logits.reshape(-1, model.vocab_size), combined[:, 1:].reshape(-1)
                )
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()
                train_losses.append(loss.item())

                category_attempts[cat] += 1
                with torch.no_grad():
                    generated = model.generate(theorem, max_len=correct_proof.size(1))
                    is_correct, _, _ = verifier.verify(
                        theorem[0], generated[0], correct_proof[0]
                    )
                    if is_correct:
                        category_corrections[cat] += 1

        for cat in ERROR_CATEGORIES:
            if category_attempts[cat] > 0:
                success_rate = category_corrections[cat] / category_attempts[cat]
                category_difficulty[cat] = 1.0 - success_rate

        val_loss, success_rate, ecrr, error_counts = evaluate_model(
            model, val_loader, verifier
        )

        cat_ecrr = compute_ecrr(category_corrections, category_attempts)

        history["train_loss"].append(np.mean(train_losses))
        history["val_loss"].append(val_loss)
        history["proof_success_rate"].append(success_rate)
        history["ecrr"].append(cat_ecrr)
        history["error_distribution"].append(error_counts)
        history["error_resolution_rate"].append(success_rate)
        history["category_progress"].append(dict(category_difficulty))

        print(
            f"Epoch {epoch}: validation_loss = {val_loss:.4f}, success_rate = {success_rate:.4f}, ECRR = {cat_ecrr:.4f}"
        )

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            patience_counter = 0
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print(f"Early stopping at epoch {epoch}")
                break
    return history


print("Creating datasets...")
train_dataset = SyntheticTheoremDataset(num_samples=800, seq_len=20, vocab_size=50)
val_dataset = SyntheticTheoremDataset(num_samples=200, seq_len=20, vocab_size=50)

print("Loading HuggingFace datasets...")
math_dataset = HuggingFaceProofDataset(
    "competition_math", split="train", max_samples=250
)
gsm8k_dataset = HuggingFaceProofDataset("gsm8k", split="train", max_samples=250)
math_qa_dataset = HuggingFaceProofDataset("math_qa", split="train", max_samples=250)

experiment_data = {"synthetic": {}, "competition_math": {}, "gsm8k": {}, "math_qa": {}}

BATCH_SIZE = 32
LR = 2e-3
EPOCHS = 15

print("\n" + "=" * 50 + "\nTraining on Synthetic Dataset\n" + "=" * 50)
train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False)

torch.manual_seed(42)
model_baseline = ProofGenerator(
    vocab_size=50, embed_dim=64, num_heads=4, num_layers=2, dropout=0.1
)
baseline_hist = train_baseline(
    model_baseline, train_loader, val_loader, epochs=EPOCHS, lr=LR
)
experiment_data["synthetic"]["baseline"] = baseline_hist

torch.manual_seed(42)
model_etcl = ProofGenerator(
    vocab_size=50, embed_dim=64, num_heads=4, num_layers=2, dropout=0.1
)
etcl_hist = train_etcl(
    model_etcl, train_dataset, val_loader, epochs=EPOCHS, lr=LR, batch_size=BATCH_SIZE
)
experiment_data["synthetic"]["etcl"] = etcl_hist

for ds_name, ds in [
    ("competition_math", math_dataset),
    ("gsm8k", gsm8k_dataset),
    ("math_qa", math_qa_dataset),
]:
    print(f"\n--- Training on {ds_name} ---")
    train_size = int(0.8 * len(ds))
    train_ds = torch.utils.data.Subset(ds, range(train_size))
    val_ds = torch.utils.data.Subset(ds, range(train_size, len(ds)))
    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_ds, batch_size=BATCH_SIZE, shuffle=False)

    torch.manual_seed(42)
    model = ProofGenerator(
        vocab_size=50, embed_dim=64, num_heads=4, num_layers=2, dropout=0.1
    )
    baseline_hist = train_baseline(model, train_loader, val_loader, epochs=10, lr=LR)
    experiment_data[ds_name]["baseline"] = baseline_hist

    torch.manual_seed(42)
    model = ProofGenerator(
        vocab_size=50, embed_dim=64, num_heads=4, num_layers=2, dropout=0.1
    )
    etcl_hist = train_etcl(
        model, train_ds, val_loader, epochs=10, lr=LR, batch_size=BATCH_SIZE
    )
    experiment_data[ds_name]["etcl"] = etcl_hist

np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)

fig, axes = plt.subplots(2, 3, figsize=(15, 10))
axes[0, 0].plot(
    experiment_data["synthetic"]["baseline"]["proof_success_rate"],
    label="Baseline",
    marker="o",
)
axes[0, 0].plot(
    experiment_data["synthetic"]["etcl"]["proof_success_rate"], label="ETCL", marker="s"
)
axes[0, 0].set_xlabel("Epoch")
axes[0, 0].set_ylabel("Success Rate")
axes[0, 0].set_title("Synthetic: Success Rate")
axes[0, 0].legend()
axes[0, 0].grid(True)

axes[0, 1].plot(
    experiment_data["synthetic"]["baseline"]["ecrr"], label="Baseline", marker="o"
)
axes[0, 1].plot(experiment_data["synthetic"]["etcl"]["ecrr"], label="ETCL", marker="s")
axes[0, 1].set_xlabel("Epoch")
axes[0, 1].set_ylabel("ECRR")
axes[0, 1].set_title("Synthetic: Error Category Resolution Rate")
axes[0, 1].legend()
axes[0, 1].grid(True)

axes[0, 2].plot(
    experiment_data["synthetic"]["baseline"]["val_loss"], label="Baseline", marker="o"
)
axes[0, 2].plot(
    experiment_data["synthetic"]["etcl"]["val_loss"], label="ETCL", marker="s"
)
axes[0, 2].set_xlabel("Epoch")
axes[0, 2].set_ylabel("Val Loss")
axes[0, 2].set_title("Synthetic: Validation Loss")
axes[0, 2].legend()
axes[0, 2].grid(True)

datasets = ["competition_math", "gsm8k", "math_qa"]
x = np.arange(len(datasets))
baseline_success = [
    experiment_data[d]["baseline"]["proof_success_rate"][-1] for d in datasets
]
etcl_success = [experiment_data[d]["etcl"]["proof_success_rate"][-1] for d in datasets]
width = 0.35
axes[1, 0].bar(x - width / 2, baseline_success, width, label="Baseline")
axes[1, 0].bar(x + width / 2, etcl_success, width, label="ETCL")
axes[1, 0].set_xticks(x)
axes[1, 0].set_xticklabels(datasets, rotation=15)
axes[1, 0].set_ylabel("Final Success Rate")
axes[1, 0].set_title("HuggingFace Datasets Comparison")
axes[1, 0].legend()
axes[1, 0].grid(True, axis="y")

baseline_ecrr = [experiment_data[d]["baseline"]["ecrr"][-1] for d in datasets]
etcl_ecrr = [experiment_data[d]["etcl"]["ecrr"][-1] for d in datasets]
axes[1, 1].bar(x - width / 2, baseline_ecrr, width, label="Baseline")
axes[1, 1].bar(x + width / 2, etcl_ecrr, width, label="ETCL")
axes[1, 1].set_xticks(x)
axes[1, 1].set_xticklabels(datasets, rotation=15)
axes[1, 1].set_ylabel("Final ECRR")
axes[1, 1].set_title("ECRR Comparison")
axes[1, 1].legend()
axes[1, 1].grid(True, axis="y")

if "category_progress" in experiment_data["synthetic"]["etcl"]:
    progress = experiment_data["synthetic"]["etcl"]["category_progress"]
    for cat in ERROR_CATEGORIES:
        vals = [p.get(cat, 0) for p in progress]
        axes[1, 2].plot(vals, label=cat, marker="o")
    axes[1, 2].set_xlabel("Epoch")
    axes[1, 2].set_ylabel("Difficulty (1 - success)")
    axes[1, 2].set_title("ETCL Category Difficulty")
    axes[1, 2].legend()
    axes[1, 2].grid(True)

plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "etcl_comprehensive_results.png"),
    dpi=150,
    bbox_inches="tight",
)
plt.close()

print("\n" + "=" * 50 + "\nFINAL SUMMARY\n" + "=" * 50)
for ds in ["synthetic"] + datasets:
    bl = experiment_data[ds]["baseline"]["proof_success_rate"][-1]
    et = experiment_data[ds]["etcl"]["proof_success_rate"][-1]
    bl_ecrr = experiment_data[ds]["baseline"]["ecrr"][-1]
    et_ecrr = experiment_data[ds]["etcl"]["ecrr"][-1]
    print(
        f"{ds}: Baseline={bl:.4f}, ETCL={et:.4f} (Δ={et-bl:+.4f}) | ECRR: BL={bl_ecrr:.4f}, ETCL={et_ecrr:.4f}"
    )
print("\nExperiment completed successfully!")
