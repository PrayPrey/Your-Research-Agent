import os
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import matplotlib.pyplot as plt
import random

working_dir = os.path.join(os.getcwd(), "working")
os.makedirs(working_dir, exist_ok=True)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

torch.manual_seed(42)
np.random.seed(42)
random.seed(42)

ERROR_CATEGORIES = {
    0: "correct",
    1: "type_mismatch",
    2: "missing_hypothesis",
    3: "incorrect_tactic",
    4: "scope_violation",
}

VOCAB = {
    "<pad>": 0,
    "<sos>": 1,
    "<eos>": 2,
    "theorem": 3,
    "lemma": 4,
    "proof": 5,
    "qed": 6,
    "apply": 7,
    "rewrite": 8,
    "intro": 9,
    "exact": 10,
    "have": 11,
    "by": 12,
    "simp": 13,
    "rfl": 14,
    "nat": 15,
    "int": 16,
    "bool": 17,
    "list": 18,
    "h1": 19,
    "h2": 20,
    "h3": 21,
    "x": 22,
    "y": 23,
    "z": 24,
    "add": 25,
    "mul": 26,
    "eq": 27,
    "lt": 28,
    "le": 29,
    "(": 30,
    ")": 31,
    ":": 32,
    "→": 33,
    "∀": 34,
    "∃": 35,
}
VOCAB_SIZE = len(VOCAB)


def generate_synthetic_theorem():
    types = ["nat", "int", "bool"]
    vars_list = ["x", "y", "z"]
    ops = ["add", "mul", "eq"]
    t = random.choice(types)
    v1, v2 = random.sample(vars_list, 2)
    op = random.choice(ops)
    theorem = ["theorem", "∀", v1, ":", t, "→", "∀", v2, ":", t, "→", op, "(", v1, ")"]
    return [VOCAB.get(tok, 0) for tok in theorem if tok in VOCAB]


def generate_correct_proof(theorem_tokens):
    proof = [
        "<sos>",
        "proof",
        "intro",
        "h1",
        "intro",
        "h2",
        "apply",
        "h1",
        "exact",
        "h2",
        "qed",
        "<eos>",
    ]
    return [VOCAB.get(tok, 0) for tok in proof]


def introduce_error(proof_tokens, error_category):
    proof = proof_tokens.copy()
    if error_category == 1:  # type_mismatch - swap types
        proof = [
            (
                VOCAB["nat"]
                if t == VOCAB["int"]
                else (VOCAB["int"] if t == VOCAB["nat"] else t)
            )
            for t in proof
        ]
    elif error_category == 2:  # missing_hypothesis - remove h1
        proof = [t for t in proof if t != VOCAB["h1"]]
    elif error_category == 3:  # incorrect_tactic - replace apply with simp
        proof = [VOCAB["simp"] if t == VOCAB["apply"] else t for t in proof]
    elif error_category == 4:  # scope_violation - remove intro
        proof = [t for t in proof if t != VOCAB["intro"]][: len(proof_tokens)]
    return proof


def simulate_verifier(generated_proof, correct_proof, theorem_tokens):
    gen_set = set(generated_proof) - {VOCAB["<pad>"], VOCAB["<sos>"], VOCAB["<eos>"]}
    correct_set = set(correct_proof) - {VOCAB["<pad>"], VOCAB["<sos>"], VOCAB["<eos>"]}

    required = [VOCAB["proof"], VOCAB["qed"]]
    if not all(r in gen_set for r in required):
        return False, random.randint(1, 4)

    key_tactics = [VOCAB["intro"], VOCAB["apply"], VOCAB["exact"]]
    tactic_count = sum(1 for t in key_tactics if t in gen_set)

    intersection = len(gen_set & correct_set)
    union = len(gen_set | correct_set)
    similarity = intersection / max(union, 1)

    if similarity > 0.5 and tactic_count >= 2:
        return True, 0
    return False, random.randint(1, 4)


class TheoremProvingDataset(Dataset):
    def __init__(
        self, num_samples=1000, include_errors=True, error_distribution=None, max_len=16
    ):
        self.data = []
        self.max_len = max_len
        if error_distribution is None:
            error_distribution = {0: 0.5, 1: 0.125, 2: 0.125, 3: 0.125, 4: 0.125}

        for _ in range(num_samples):
            theorem = generate_synthetic_theorem()
            correct_proof = generate_correct_proof(theorem)
            if include_errors:
                category = np.random.choice(
                    list(error_distribution.keys()), p=list(error_distribution.values())
                )
                input_proof = (
                    correct_proof.copy()
                    if category == 0
                    else introduce_error(correct_proof, category)
                )
            else:
                category = 0
                input_proof = correct_proof.copy()
            self.data.append(
                {
                    "theorem": self.pad_sequence(theorem),
                    "input_proof": self.pad_sequence(input_proof),
                    "target_proof": self.pad_sequence(correct_proof),
                    "error_category": category,
                }
            )

    def pad_sequence(self, seq):
        if len(seq) > self.max_len:
            return seq[: self.max_len]
        return seq + [VOCAB["<pad>"]] * (self.max_len - len(seq))

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]
        return {
            "theorem": torch.tensor(item["theorem"], dtype=torch.long),
            "input_proof": torch.tensor(item["input_proof"], dtype=torch.long),
            "target_proof": torch.tensor(item["target_proof"], dtype=torch.long),
            "error_category": torch.tensor(item["error_category"], dtype=torch.long),
        }


class SimpleTransformerProver(nn.Module):
    def __init__(self, vocab_size, d_model=128, nhead=4, num_layers=2, max_len=16):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, d_model, padding_idx=0)
        self.pos_encoding = nn.Embedding(max_len, d_model)
        encoder_layer = nn.TransformerEncoderLayer(
            d_model, nhead, d_model * 4, dropout=0.1, batch_first=True
        )
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers)
        decoder_layer = nn.TransformerDecoderLayer(
            d_model, nhead, d_model * 4, dropout=0.1, batch_first=True
        )
        self.decoder = nn.TransformerDecoder(decoder_layer, num_layers)
        self.output_proj = nn.Linear(d_model, vocab_size)
        self.error_classifier = nn.Linear(d_model, 5)

    def forward(self, theorem, input_proof, target_proof=None):
        batch_size, seq_len = theorem.shape
        positions = (
            torch.arange(seq_len, device=theorem.device)
            .unsqueeze(0)
            .expand(batch_size, -1)
        )
        theorem_emb = self.embedding(theorem) + self.pos_encoding(positions)
        theorem_encoded = self.encoder(theorem_emb)

        proof_len = input_proof.shape[1]
        proof_positions = (
            torch.arange(proof_len, device=input_proof.device)
            .unsqueeze(0)
            .expand(batch_size, -1)
        )
        input_emb = self.embedding(input_proof) + self.pos_encoding(proof_positions)
        input_encoded = self.encoder(input_emb)
        error_logits = self.error_classifier(input_encoded.mean(dim=1))

        if target_proof is not None:
            tgt_len = target_proof.shape[1]
            target_positions = (
                torch.arange(tgt_len, device=target_proof.device)
                .unsqueeze(0)
                .expand(batch_size, -1)
            )
            target_emb = self.embedding(target_proof) + self.pos_encoding(
                target_positions
            )
            tgt_mask = nn.Transformer.generate_square_subsequent_mask(tgt_len).to(
                target_proof.device
            )
            decoded = self.decoder(target_emb, theorem_encoded, tgt_mask=tgt_mask)
        else:
            decoded = self.decoder(input_emb, theorem_encoded)
        return self.output_proj(decoded), error_logits


def train_epoch(model, dataloader, optimizer, criterion_proof, criterion_error, device):
    model.train()
    total_loss = 0
    for batch in dataloader:
        batch = {k: v.to(device) for k, v in batch.items()}
        optimizer.zero_grad()
        output_logits, error_logits = model(
            batch["theorem"], batch["input_proof"], batch["target_proof"]
        )
        loss_proof = criterion_proof(
            output_logits[:, :-1].reshape(-1, VOCAB_SIZE),
            batch["target_proof"][:, 1:].reshape(-1),
        )
        loss_error = criterion_error(error_logits, batch["error_category"])
        loss = loss_proof + 0.5 * loss_error
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
    return total_loss / len(dataloader)


def evaluate(model, dataloader, criterion_proof, criterion_error, device):
    model.eval()
    total_loss, correct_proofs, total_proofs, error_correct = 0, 0, 0, 0
    with torch.no_grad():
        for batch in dataloader:
            batch = {k: v.to(device) for k, v in batch.items()}
            output_logits, error_logits = model(
                batch["theorem"], batch["input_proof"], batch["target_proof"]
            )
            loss_proof = criterion_proof(
                output_logits[:, :-1].reshape(-1, VOCAB_SIZE),
                batch["target_proof"][:, 1:].reshape(-1),
            )
            loss_error = criterion_error(error_logits, batch["error_category"])
            total_loss += (loss_proof + 0.5 * loss_error).item()
            generated = output_logits.argmax(dim=-1)
            for i in range(generated.shape[0]):
                success, _ = simulate_verifier(
                    generated[i].cpu().tolist(),
                    batch["target_proof"][i].cpu().tolist(),
                    batch["theorem"][i].cpu().tolist(),
                )
                correct_proofs += int(success)
                total_proofs += 1
            error_correct += (
                (error_logits.argmax(dim=-1) == batch["error_category"]).sum().item()
            )
    return (
        total_loss / len(dataloader),
        correct_proofs / max(total_proofs, 1),
        error_correct / max(total_proofs, 1),
    )


experiment_data = {
    "baseline": {
        "metrics": {
            "train_loss": [],
            "val_loss": [],
            "proof_success_rate": [],
            "error_accuracy": [],
        },
        "epochs": [],
    },
    "etcl": {
        "metrics": {
            "train_loss": [],
            "val_loss": [],
            "proof_success_rate": [],
            "error_accuracy": [],
        },
        "epochs": [],
        "curriculum_stage": [],
    },
}

print("Creating datasets...")
train_dataset = TheoremProvingDataset(num_samples=2000)
val_dataset = TheoremProvingDataset(num_samples=500)
test_dataset = TheoremProvingDataset(num_samples=500)
train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=32)
test_loader = DataLoader(test_dataset, batch_size=32)

NUM_EPOCHS, LEARNING_RATE = 20, 1e-3
criterion_proof = nn.CrossEntropyLoss(ignore_index=VOCAB["<pad>"])
criterion_error = nn.CrossEntropyLoss()

print("\n" + "=" * 50 + "\nTraining BASELINE model\n" + "=" * 50)
baseline_model = SimpleTransformerProver(VOCAB_SIZE).to(device)
baseline_optimizer = optim.Adam(baseline_model.parameters(), lr=LEARNING_RATE)
for epoch in range(NUM_EPOCHS):
    train_loss = train_epoch(
        baseline_model,
        train_loader,
        baseline_optimizer,
        criterion_proof,
        criterion_error,
        device,
    )
    val_loss, proof_success, error_acc = evaluate(
        baseline_model, val_loader, criterion_proof, criterion_error, device
    )
    experiment_data["baseline"]["metrics"]["train_loss"].append(train_loss)
    experiment_data["baseline"]["metrics"]["val_loss"].append(val_loss)
    experiment_data["baseline"]["metrics"]["proof_success_rate"].append(proof_success)
    experiment_data["baseline"]["metrics"]["error_accuracy"].append(error_acc)
    experiment_data["baseline"]["epochs"].append(epoch)
    print(
        f"Epoch {epoch}: validation_loss = {val_loss:.4f}, proof_success_rate = {proof_success:.4f}, error_accuracy = {error_acc:.4f}"
    )

print("\n" + "=" * 50 + "\nTraining ETCL model\n" + "=" * 50)
etcl_model = SimpleTransformerProver(VOCAB_SIZE).to(device)
etcl_optimizer = optim.Adam(etcl_model.parameters(), lr=LEARNING_RATE)
curriculum_distributions = [
    {0: 1.0, 1: 0.0, 2: 0.0, 3: 0.0, 4: 0.0},
    {0: 0.6, 1: 0.4, 2: 0.0, 3: 0.0, 4: 0.0},
    {0: 0.5, 1: 0.25, 2: 0.25, 3: 0.0, 4: 0.0},
    {0: 0.4, 1: 0.2, 2: 0.2, 3: 0.2, 4: 0.0},
    {0: 0.4, 1: 0.15, 2: 0.15, 3: 0.15, 4: 0.15},
]
epochs_per_stage = NUM_EPOCHS // len(curriculum_distributions)
epoch_counter = 0
for stage_idx, distribution in enumerate(curriculum_distributions):
    print(f"\n--- Curriculum Stage {stage_idx} ---")
    curriculum_dataset = TheoremProvingDataset(
        num_samples=2000, error_distribution=distribution
    )
    curriculum_loader = DataLoader(curriculum_dataset, batch_size=32, shuffle=True)
    for _ in range(epochs_per_stage):
        train_loss = train_epoch(
            etcl_model,
            curriculum_loader,
            etcl_optimizer,
            criterion_proof,
            criterion_error,
            device,
        )
        val_loss, proof_success, error_acc = evaluate(
            etcl_model, val_loader, criterion_proof, criterion_error, device
        )
        experiment_data["etcl"]["metrics"]["train_loss"].append(train_loss)
        experiment_data["etcl"]["metrics"]["val_loss"].append(val_loss)
        experiment_data["etcl"]["metrics"]["proof_success_rate"].append(proof_success)
        experiment_data["etcl"]["metrics"]["error_accuracy"].append(error_acc)
        experiment_data["etcl"]["epochs"].append(epoch_counter)
        experiment_data["etcl"]["curriculum_stage"].append(stage_idx)
        print(
            f"Epoch {epoch_counter}: validation_loss = {val_loss:.4f}, proof_success_rate = {proof_success:.4f}, error_accuracy = {error_acc:.4f}"
        )
        epoch_counter += 1

print("\n" + "=" * 50 + "\nFinal Test Evaluation\n" + "=" * 50)
_, baseline_test_success, baseline_test_error = evaluate(
    baseline_model, test_loader, criterion_proof, criterion_error, device
)
_, etcl_test_success, etcl_test_error = evaluate(
    etcl_model, test_loader, criterion_proof, criterion_error, device
)
print(
    f"Baseline - Test proof_success_rate: {baseline_test_success:.4f}, Error accuracy: {baseline_test_error:.4f}"
)
print(
    f"ETCL - Test proof_success_rate: {etcl_test_success:.4f}, Error accuracy: {etcl_test_error:.4f}"
)
experiment_data["final_results"] = {
    "baseline_test_success": baseline_test_success,
    "etcl_test_success": etcl_test_success,
    "baseline_test_error_acc": baseline_test_error,
    "etcl_test_error_acc": etcl_test_error,
}

fig, axes = plt.subplots(2, 2, figsize=(12, 10))
axes[0, 0].plot(
    experiment_data["baseline"]["epochs"],
    experiment_data["baseline"]["metrics"]["proof_success_rate"],
    "b-",
    label="Baseline",
    linewidth=2,
)
axes[0, 0].plot(
    experiment_data["etcl"]["epochs"],
    experiment_data["etcl"]["metrics"]["proof_success_rate"],
    "r-",
    label="ETCL",
    linewidth=2,
)
axes[0, 0].set_xlabel("Epoch")
axes[0, 0].set_ylabel("Proof Success Rate")
axes[0, 0].set_title("Proof Success Rate")
axes[0, 0].legend()
axes[0, 0].grid(True, alpha=0.3)
axes[0, 1].plot(
    experiment_data["baseline"]["epochs"],
    experiment_data["baseline"]["metrics"]["val_loss"],
    "b-",
    label="Baseline",
    linewidth=2,
)
axes[0, 1].plot(
    experiment_data["etcl"]["epochs"],
    experiment_data["etcl"]["metrics"]["val_loss"],
    "r-",
    label="ETCL",
    linewidth=2,
)
axes[0, 1].set_xlabel("Epoch")
axes[0, 1].set_ylabel("Validation Loss")
axes[0, 1].set_title("Validation Loss")
axes[0, 1].legend()
axes[0, 1].grid(True, alpha=0.3)
axes[1, 0].plot(
    experiment_data["baseline"]["epochs"],
    experiment_data["baseline"]["metrics"]["error_accuracy"],
    "b-",
    label="Baseline",
    linewidth=2,
)
axes[1, 0].plot(
    experiment_data["etcl"]["epochs"],
    experiment_data["etcl"]["metrics"]["error_accuracy"],
    "r-",
    label="ETCL",
    linewidth=2,
)
axes[1, 0].set_xlabel("Epoch")
axes[1, 0].set_ylabel("Error Classification Accuracy")
axes[1, 0].set_title("Error Classification")
axes[1, 0].legend()
axes[1, 0].grid(True, alpha=0.3)
colors = ["green", "yellow", "orange", "red", "darkred"]
for stage in range(5):
    stage_epochs = [
        e
        for e, s in zip(
            experiment_data["etcl"]["epochs"],
            experiment_data["etcl"]["curriculum_stage"],
        )
        if s == stage
    ]
    stage_success = [
        experiment_data["etcl"]["metrics"]["proof_success_rate"][i]
        for i, s in enumerate(experiment_data["etcl"]["curriculum_stage"])
        if s == stage
    ]
    if stage_epochs:
        axes[1, 1].scatter(
            stage_epochs,
            stage_success,
            c=colors[stage],
            label=f"Stage {stage}",
            s=50,
            alpha=0.7,
        )
axes[1, 1].set_xlabel("Epoch")
axes[1, 1].set_ylabel("Proof Success Rate")
axes[1, 1].set_title("ETCL by Stage")
axes[1, 1].legend()
axes[1, 1].grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(
    os.path.join(working_dir, "etcl_comparison.png"), dpi=150, bbox_inches="tight"
)
plt.close()
np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)
print(f"\nResults saved to {working_dir}")
