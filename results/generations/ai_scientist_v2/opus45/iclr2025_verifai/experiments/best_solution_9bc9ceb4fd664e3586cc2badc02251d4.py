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
    "correct",
]


class SyntheticTheoremDataset(Dataset):
    def __init__(self, num_samples=1000, seq_len=20, vocab_size=50):
        self.num_samples = num_samples
        self.seq_len = seq_len
        self.vocab_size = vocab_size
        self.data = []
        for i in range(num_samples):
            theorem = np.random.randint(1, vocab_size // 2, size=seq_len // 2)
            proof = self._generate_proof(theorem)
            self.data.append((theorem, proof))

    def _generate_proof(self, theorem):
        proof = []
        for t in theorem:
            proof.append(t + self.vocab_size // 2)
            proof.append((t * 2) % self.vocab_size + 1)
        return np.array(proof[: self.seq_len])

    def __len__(self):
        return self.num_samples

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
                error_type = self._categorize_error(i, g, gt, theorem)
                return False, error_type, i
        return True, "correct", -1

    def _categorize_error(self, position, generated, expected, theorem):
        if position < len(theorem):
            return (
                "type_mismatch"
                if abs(generated - expected) > self.vocab_size // 4
                else "wrong_tactic"
            )
        else:
            return (
                "scope_violation"
                if generated < self.vocab_size // 2
                else "missing_hypothesis"
            )


class ProofGenerator(nn.Module):
    def __init__(
        self, vocab_size=50, embed_dim=64, num_heads=4, num_layers=2, max_len=40
    ):
        super().__init__()
        self.vocab_size = vocab_size
        self.embed_dim = embed_dim
        self.embedding = nn.Embedding(vocab_size + 1, embed_dim, padding_idx=0)
        self.pos_embedding = nn.Embedding(max_len, embed_dim)
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=embed_dim, nhead=num_heads, dim_feedforward=128, batch_first=True
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        self.output_proj = nn.Linear(embed_dim, vocab_size)

    def forward(self, x):
        batch_size, seq_len = x.size()
        positions = (
            torch.arange(seq_len, device=x.device).unsqueeze(0).expand(batch_size, -1)
        )
        emb = self.embedding(x) + self.pos_embedding(positions)
        mask = nn.Transformer.generate_square_subsequent_mask(seq_len, device=x.device)
        out = self.transformer(emb, mask=mask, is_causal=True)
        return self.output_proj(out)

    def generate(self, theorem, max_len=20):
        self.eval()
        batch_size = theorem.size(0)
        generated = theorem.clone()
        with torch.no_grad():
            for _ in range(max_len):
                logits = self.forward(generated)
                next_token = logits[:, -1, :].argmax(dim=-1, keepdim=True)
                generated = torch.cat([generated, next_token], dim=1)
        return generated[:, theorem.size(1) :]


def create_error_augmented_data(dataset, error_category, num_examples=100):
    augmented = []
    for i in range(min(num_examples, len(dataset))):
        item = dataset[i]
        theorem = item["theorem"].numpy()
        correct_proof = item["proof"].numpy()
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


def train_baseline(model, train_loader, val_loader, epochs=10, lr=1e-3):
    model = model.to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = nn.CrossEntropyLoss()
    verifier = SimulatedVerifier()
    history = {"train_loss": [], "val_loss": [], "proof_success_rate": []}
    for epoch in range(epochs):
        model.train()
        train_losses = []
        for batch in train_loader:
            theorem, proof = batch["theorem"].to(device), batch["proof"].to(device)
            combined = torch.cat([theorem, proof], dim=1)
            optimizer.zero_grad()
            logits = model(combined[:, :-1])
            target = combined[:, 1:]
            loss = criterion(logits.reshape(-1, model.vocab_size), target.reshape(-1))
            loss.backward()
            optimizer.step()
            train_losses.append(loss.item())
        model.eval()
        val_losses, correct, total = [], 0, 0
        with torch.no_grad():
            for batch in val_loader:
                theorem, proof = batch["theorem"].to(device), batch["proof"].to(device)
                combined = torch.cat([theorem, proof], dim=1)
                logits = model(combined[:, :-1])
                target = combined[:, 1:]
                loss = criterion(
                    logits.reshape(-1, model.vocab_size), target.reshape(-1)
                )
                val_losses.append(loss.item())
                generated = model.generate(theorem, max_len=proof.size(1))
                for i in range(theorem.size(0)):
                    is_correct, _, _ = verifier.verify(
                        theorem[i], generated[i], proof[i]
                    )
                    correct += int(is_correct)
                    total += 1
        history["train_loss"].append(np.mean(train_losses))
        history["val_loss"].append(np.mean(val_losses))
        history["proof_success_rate"].append(correct / total if total > 0 else 0)
    return history


def train_etcl(model, train_dataset, val_loader, epochs=10, lr=1e-3, batch_size=32):
    model = model.to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    criterion = nn.CrossEntropyLoss()
    verifier = SimulatedVerifier()
    error_categories = [
        "type_mismatch",
        "wrong_tactic",
        "missing_hypothesis",
        "scope_violation",
    ]
    augmented_data = {
        cat: create_error_augmented_data(train_dataset, cat, num_examples=200)
        for cat in error_categories
    }
    history = {
        "train_loss": [],
        "val_loss": [],
        "proof_success_rate": [],
        "error_distribution": [],
    }
    curriculum_schedule = [
        ["type_mismatch"],
        ["type_mismatch", "wrong_tactic"],
        ["type_mismatch", "wrong_tactic", "missing_hypothesis"],
        error_categories,
    ]
    for epoch in range(epochs):
        model.train()
        train_losses = []
        stage = min(
            epoch // max(1, epochs // len(curriculum_schedule)),
            len(curriculum_schedule) - 1,
        )
        current_categories = curriculum_schedule[stage]
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        for batch in train_loader:
            theorem, proof = batch["theorem"].to(device), batch["proof"].to(device)
            combined = torch.cat([theorem, proof], dim=1)
            optimizer.zero_grad()
            logits = model(combined[:, :-1])
            target = combined[:, 1:]
            loss = criterion(logits.reshape(-1, model.vocab_size), target.reshape(-1))
            loss.backward()
            optimizer.step()
            train_losses.append(loss.item())
        for cat in current_categories:
            for item in augmented_data[cat][:50]:
                theorem = item["theorem"].unsqueeze(0).to(device)
                correct_proof = item["correct_proof"].unsqueeze(0).to(device)
                combined = torch.cat([theorem, correct_proof], dim=1)
                optimizer.zero_grad()
                logits = model(combined[:, :-1])
                target = combined[:, 1:]
                loss = criterion(
                    logits.reshape(-1, model.vocab_size), target.reshape(-1)
                )
                loss.backward()
                optimizer.step()
                train_losses.append(loss.item())
        model.eval()
        val_losses, correct, total = [], 0, 0
        error_counts = defaultdict(int)
        with torch.no_grad():
            for batch in val_loader:
                theorem, proof = batch["theorem"].to(device), batch["proof"].to(device)
                combined = torch.cat([theorem, proof], dim=1)
                logits = model(combined[:, :-1])
                target = combined[:, 1:]
                loss = criterion(
                    logits.reshape(-1, model.vocab_size), target.reshape(-1)
                )
                val_losses.append(loss.item())
                generated = model.generate(theorem, max_len=proof.size(1))
                for i in range(theorem.size(0)):
                    is_correct, error_cat, _ = verifier.verify(
                        theorem[i], generated[i], proof[i]
                    )
                    error_counts[error_cat] += 1
                    correct += int(is_correct)
                    total += 1
        history["train_loss"].append(np.mean(train_losses))
        history["val_loss"].append(np.mean(val_losses))
        history["proof_success_rate"].append(correct / total if total > 0 else 0)
        history["error_distribution"].append(dict(error_counts))
    return history


# Hyperparameter tuning for batch size
BATCH_SIZES = [16, 32, 64, 128]
EPOCHS = 15
LR = 1e-3

print("Creating datasets...")
train_dataset = SyntheticTheoremDataset(num_samples=800, seq_len=20, vocab_size=50)
val_dataset = SyntheticTheoremDataset(num_samples=200, seq_len=20, vocab_size=50)

experiment_data = {"baseline_batch_size_tuning": {}, "etcl_batch_size_tuning": {}}
baseline_results = {}
etcl_results = {}

# Tune batch size for baseline
print("\n" + "=" * 50 + "\nTuning Batch Size for Baseline Model\n" + "=" * 50)
for batch_size in BATCH_SIZES:
    print(f"\n--- Training Baseline with batch_size={batch_size} ---")
    torch.manual_seed(42)
    np.random.seed(42)
    random.seed(42)
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    model = ProofGenerator(vocab_size=50, embed_dim=64, num_heads=4, num_layers=2)
    history = train_baseline(model, train_loader, val_loader, epochs=EPOCHS, lr=LR)
    baseline_results[batch_size] = history
    experiment_data["baseline_batch_size_tuning"][f"batch_size_{batch_size}"] = {
        "metrics": {"proof_success_rate": history["proof_success_rate"]},
        "losses": {"train": history["train_loss"], "val": history["val_loss"]},
    }
    print(
        f"Batch size {batch_size}: Final success rate = {history['proof_success_rate'][-1]:.4f}"
    )

# Tune batch size for ETCL
print("\n" + "=" * 50 + "\nTuning Batch Size for ETCL Model\n" + "=" * 50)
for batch_size in BATCH_SIZES:
    print(f"\n--- Training ETCL with batch_size={batch_size} ---")
    torch.manual_seed(42)
    np.random.seed(42)
    random.seed(42)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    model = ProofGenerator(vocab_size=50, embed_dim=64, num_heads=4, num_layers=2)
    history = train_etcl(
        model, train_dataset, val_loader, epochs=EPOCHS, lr=LR, batch_size=batch_size
    )
    etcl_results[batch_size] = history
    experiment_data["etcl_batch_size_tuning"][f"batch_size_{batch_size}"] = {
        "metrics": {"proof_success_rate": history["proof_success_rate"]},
        "losses": {"train": history["train_loss"], "val": history["val_loss"]},
        "error_distribution": history["error_distribution"],
    }
    print(
        f"Batch size {batch_size}: Final success rate = {history['proof_success_rate'][-1]:.4f}"
    )

# Save experiment data
np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)

# Create comparison plots
fig, axes = plt.subplots(2, 3, figsize=(15, 10))

# Baseline plots
for bs in BATCH_SIZES:
    axes[0, 0].plot(
        baseline_results[bs]["proof_success_rate"], label=f"BS={bs}", marker="o"
    )
axes[0, 0].set_xlabel("Epoch")
axes[0, 0].set_ylabel("Proof Success Rate")
axes[0, 0].set_title("Baseline: Success Rate vs Batch Size")
axes[0, 0].legend()
axes[0, 0].grid(True)

for bs in BATCH_SIZES:
    axes[0, 1].plot(baseline_results[bs]["val_loss"], label=f"BS={bs}", marker="o")
axes[0, 1].set_xlabel("Epoch")
axes[0, 1].set_ylabel("Validation Loss")
axes[0, 1].set_title("Baseline: Val Loss vs Batch Size")
axes[0, 1].legend()
axes[0, 1].grid(True)

# ETCL plots
for bs in BATCH_SIZES:
    axes[1, 0].plot(
        etcl_results[bs]["proof_success_rate"], label=f"BS={bs}", marker="s"
    )
axes[1, 0].set_xlabel("Epoch")
axes[1, 0].set_ylabel("Proof Success Rate")
axes[1, 0].set_title("ETCL: Success Rate vs Batch Size")
axes[1, 0].legend()
axes[1, 0].grid(True)

for bs in BATCH_SIZES:
    axes[1, 1].plot(etcl_results[bs]["val_loss"], label=f"BS={bs}", marker="s")
axes[1, 1].set_xlabel("Epoch")
axes[1, 1].set_ylabel("Validation Loss")
axes[1, 1].set_title("ETCL: Val Loss vs Batch Size")
axes[1, 1].legend()
axes[1, 1].grid(True)

# Final success rate comparison bar plot
x = np.arange(len(BATCH_SIZES))
width = 0.35
baseline_final = [baseline_results[bs]["proof_success_rate"][-1] for bs in BATCH_SIZES]
etcl_final = [etcl_results[bs]["proof_success_rate"][-1] for bs in BATCH_SIZES]
axes[0, 2].bar(x - width / 2, baseline_final, width, label="Baseline")
axes[0, 2].bar(x + width / 2, etcl_final, width, label="ETCL")
axes[0, 2].set_xlabel("Batch Size")
axes[0, 2].set_ylabel("Final Proof Success Rate")
axes[0, 2].set_title("Final Success Rate Comparison")
axes[0, 2].set_xticks(x)
axes[0, 2].set_xticklabels(BATCH_SIZES)
axes[0, 2].legend()
axes[0, 2].grid(True, axis="y")

# Improvement over baseline
improvements = [etcl_final[i] - baseline_final[i] for i in range(len(BATCH_SIZES))]
colors = ["green" if imp > 0 else "red" for imp in improvements]
axes[1, 2].bar(x, improvements, color=colors)
axes[1, 2].set_xlabel("Batch Size")
axes[1, 2].set_ylabel("ETCL Improvement over Baseline")
axes[1, 2].set_title("ETCL Improvement by Batch Size")
axes[1, 2].set_xticks(x)
axes[1, 2].set_xticklabels(BATCH_SIZES)
axes[1, 2].axhline(y=0, color="black", linestyle="-", linewidth=0.5)
axes[1, 2].grid(True, axis="y")

plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "batch_size_tuning.png"), dpi=150, bbox_inches="tight"
)
plt.close()

# Find best batch sizes
best_baseline_bs = max(
    BATCH_SIZES, key=lambda bs: baseline_results[bs]["proof_success_rate"][-1]
)
best_etcl_bs = max(
    BATCH_SIZES, key=lambda bs: etcl_results[bs]["proof_success_rate"][-1]
)

print("\n" + "=" * 50 + "\nBATCH SIZE TUNING RESULTS\n" + "=" * 50)
print("\nBaseline Results:")
for bs in BATCH_SIZES:
    print(
        f"  Batch Size {bs}: Final Success Rate = {baseline_results[bs]['proof_success_rate'][-1]:.4f}"
    )
print(f"  Best Batch Size: {best_baseline_bs}")

print("\nETCL Results:")
for bs in BATCH_SIZES:
    print(
        f"  Batch Size {bs}: Final Success Rate = {etcl_results[bs]['proof_success_rate'][-1]:.4f}"
    )
print(f"  Best Batch Size: {best_etcl_bs}")

print("\nImprovement (ETCL - Baseline) by Batch Size:")
for bs in BATCH_SIZES:
    imp = (
        etcl_results[bs]["proof_success_rate"][-1]
        - baseline_results[bs]["proof_success_rate"][-1]
    )
    print(f"  Batch Size {bs}: {imp:+.4f}")

print("\n" + "=" * 50 + "\nFINAL SUMMARY\n" + "=" * 50)
print(
    f"Best Baseline (BS={best_baseline_bs}): {baseline_results[best_baseline_bs]['proof_success_rate'][-1]:.4f}"
)
print(
    f"Best ETCL (BS={best_etcl_bs}): {etcl_results[best_etcl_bs]['proof_success_rate'][-1]:.4f}"
)
print(
    f"Overall Best Improvement: {max(improvements):.4f} at batch_size={BATCH_SIZES[improvements.index(max(improvements))]}"
)
print("\nExperiment completed. Results saved to working directory.")
