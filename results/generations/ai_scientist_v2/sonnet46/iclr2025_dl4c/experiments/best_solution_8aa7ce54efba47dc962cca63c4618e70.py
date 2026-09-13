import os

working_dir = os.path.join(os.getcwd(), "working")
os.makedirs(working_dir, exist_ok=True)

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset
import matplotlib.pyplot as plt
import random
import ast
import traceback
from sklearn.metrics import accuracy_score

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

random.seed(42)
np.random.seed(42)
torch.manual_seed(42)

# ─────────────────────────────────────────────────────────
# 1. Synthetic dataset of programming problems
# ─────────────────────────────────────────────────────────

PROBLEMS = [
    {
        "id": 0,
        "spec": "Return the sum of all elements in a list.",
        "given_tests": [
            ("sum_list([1,2,3])", 6),
            ("sum_list([0,0,0])", 0),
            ("sum_list([5])", 5),
        ],
        "held_out_tests": [
            ("sum_list([])", 0),
            ("sum_list([-1,-2,-3])", -6),
            ("sum_list([100, 200, 300])", 600),
        ],
        "correct_code": "def sum_list(lst):\n    return sum(lst)",
        "adversarial_codes": [
            "def sum_list(lst):\n    if lst == [1,2,3]: return 6\n    if lst == [0,0,0]: return 0\n    if lst == [5]: return 5\n    return 0",
            "def sum_list(lst):\n    results = {(1,2,3):6,(0,0,0):0,(5,):5}\n    return results.get(tuple(lst), 0)",
        ],
    },
    {
        "id": 1,
        "spec": "Return the maximum element in a list.",
        "given_tests": [
            ("max_list([1,2,3])", 3),
            ("max_list([7,1,5])", 7),
            ("max_list([0])", 0),
        ],
        "held_out_tests": [
            ("max_list([-1,-2,-3])", -1),
            ("max_list([100, 50, 75])", 100),
            ("max_list([3,3,3])", 3),
        ],
        "correct_code": "def max_list(lst):\n    return max(lst)",
        "adversarial_codes": [
            "def max_list(lst):\n    if lst==[1,2,3]: return 3\n    if lst==[7,1,5]: return 7\n    if lst==[0]: return 0\n    return lst[0]",
            "def max_list(lst):\n    lookup = {(1,2,3):3,(7,1,5):7,(0,):0}\n    return lookup.get(tuple(lst), lst[0])",
        ],
    },
    {
        "id": 2,
        "spec": "Return True if a string is a palindrome, False otherwise.",
        "given_tests": [
            ("is_palindrome('racecar')", True),
            ("is_palindrome('hello')", False),
            ("is_palindrome('a')", True),
        ],
        "held_out_tests": [
            ("is_palindrome('')", True),
            ("is_palindrome('abba')", True),
            ("is_palindrome('abc')", False),
        ],
        "correct_code": "def is_palindrome(s):\n    return s == s[::-1]",
        "adversarial_codes": [
            "def is_palindrome(s):\n    if s=='racecar': return True\n    if s=='hello': return False\n    if s=='a': return True\n    return False",
            "def is_palindrome(s):\n    known = {'racecar':True,'hello':False,'a':True}\n    return known.get(s, False)",
        ],
    },
    {
        "id": 3,
        "spec": "Count the number of vowels in a string.",
        "given_tests": [
            ("count_vowels('hello')", 2),
            ("count_vowels('aeiou')", 5),
            ("count_vowels('xyz')", 0),
        ],
        "held_out_tests": [
            ("count_vowels('')", 0),
            ("count_vowels('AEIOU')", 5),
            ("count_vowels('python')", 1),
        ],
        "correct_code": "def count_vowels(s):\n    return sum(1 for c in s.lower() if c in 'aeiou')",
        "adversarial_codes": [
            "def count_vowels(s):\n    if s=='hello': return 2\n    if s=='aeiou': return 5\n    if s=='xyz': return 0\n    return 0",
            "def count_vowels(s):\n    d={'hello':2,'aeiou':5,'xyz':0}\n    return d.get(s,0)",
        ],
    },
    {
        "id": 4,
        "spec": "Return the factorial of a non-negative integer n.",
        "given_tests": [
            ("factorial(0)", 1),
            ("factorial(1)", 1),
            ("factorial(5)", 120),
        ],
        "held_out_tests": [
            ("factorial(3)", 6),
            ("factorial(7)", 5040),
            ("factorial(10)", 3628800),
        ],
        "correct_code": "def factorial(n):\n    if n == 0: return 1\n    return n * factorial(n-1)",
        "adversarial_codes": [
            "def factorial(n):\n    if n==0: return 1\n    if n==1: return 1\n    if n==5: return 120\n    return n",
            "def factorial(n):\n    lookup={0:1,1:1,5:120}\n    return lookup.get(n,n)",
        ],
    },
    {
        "id": 5,
        "spec": "Return whether a number is even.",
        "given_tests": [
            ("is_even(2)", True),
            ("is_even(3)", False),
            ("is_even(0)", True),
        ],
        "held_out_tests": [
            ("is_even(100)", True),
            ("is_even(-1)", False),
            ("is_even(7)", False),
        ],
        "correct_code": "def is_even(n):\n    return n % 2 == 0",
        "adversarial_codes": [
            "def is_even(n):\n    if n==2: return True\n    if n==3: return False\n    if n==0: return True\n    return True",
            "def is_even(n):\n    d={2:True,3:False,0:True}\n    return d.get(n,True)",
        ],
    },
    {
        "id": 6,
        "spec": "Return the reversed string.",
        "given_tests": [
            ("reverse_str('hello')", "olleh"),
            ("reverse_str('abc')", "cba"),
            ("reverse_str('a')", "a"),
        ],
        "held_out_tests": [
            ("reverse_str('')", ""),
            ("reverse_str('python')", "nohtyp"),
            ("reverse_str('12345')", "54321"),
        ],
        "correct_code": "def reverse_str(s):\n    return s[::-1]",
        "adversarial_codes": [
            "def reverse_str(s):\n    if s=='hello': return 'olleh'\n    if s=='abc': return 'cba'\n    if s=='a': return 'a'\n    return s",
            "def reverse_str(s):\n    d={'hello':'olleh','abc':'cba','a':'a'}\n    return d.get(s,s)",
        ],
    },
    {
        "id": 7,
        "spec": "Return the length of the longest word in a sentence.",
        "given_tests": [
            ("longest_word('hello world')", 5),
            ("longest_word('I am here')", 4),
            ("longest_word('cat')", 3),
        ],
        "held_out_tests": [
            ("longest_word('a')", 1),
            ("longest_word('superlongword short')", 13),
            ("longest_word('the quick brown fox')", 5),
        ],
        "correct_code": "def longest_word(s):\n    return max(len(w) for w in s.split())",
        "adversarial_codes": [
            "def longest_word(s):\n    if s=='hello world': return 5\n    if s=='I am here': return 4\n    if s=='cat': return 3\n    return 0",
            "def longest_word(s):\n    d={'hello world':5,'I am here':4,'cat':3}\n    return d.get(s,0)",
        ],
    },
]

# ─────────────────────────────────────────────────────────
# 2. Code execution utilities
# ─────────────────────────────────────────────────────────


def safe_exec(code_str, test_call, expected):
    """Execute code and check if test passes."""
    try:
        namespace = {}
        exec(code_str, namespace)
        result = eval(test_call, namespace)
        return result == expected
    except Exception:
        return False


def evaluate_code(code_str, tests):
    """Return pass rate on a list of (call, expected) tests."""
    if not tests:
        return 0.0
    passes = sum(safe_exec(code_str, call, exp) for call, exp in tests)
    return passes / len(tests)


# ─────────────────────────────────────────────────────────
# 3. Code tokenizer / feature extractor (bag-of-tokens)
# ─────────────────────────────────────────────────────────

VOCAB_TOKENS = [
    "<PAD>",
    "<UNK>",
    "def",
    "return",
    "if",
    "else",
    "elif",
    "for",
    "in",
    "while",
    "True",
    "False",
    "None",
    "not",
    "and",
    "or",
    "import",
    "class",
    "lambda",
    "sum",
    "max",
    "min",
    "len",
    "range",
    "print",
    "append",
    "split",
    "join",
    "strip",
    "lower",
    "upper",
    "get",
    "dict",
    "list",
    "set",
    "==",
    "!=",
    "<=",
    ">=",
    "<",
    ">",
    "+",
    "-",
    "*",
    "/",
    "%",
    "//",
    "**",
    "=",
    "(",
    ")",
    "[",
    "]",
    "{",
    "}",
    ":",
    ",",
    ".",
    "\n",
    "lookup",
    "hardcode",
    "special",
    "0",
    "1",
    "2",
    "3",
    "4",
    "5",
    "n",
    "s",
    "lst",
    "result",
    "results",
    "known",
    "known_vals",
]
VOCAB = {tok: i for i, tok in enumerate(VOCAB_TOKENS)}
VOCAB_SIZE = len(VOCAB)
MAX_LEN = 128


def tokenize_code(code_str, max_len=MAX_LEN):
    """Simple whitespace + symbol tokenizer."""
    import re

    tokens = re.findall(r"\w+|[^\w\s]", code_str)
    ids = [VOCAB.get(tok, VOCAB["<UNK>"]) for tok in tokens]
    ids = ids[:max_len]
    ids += [VOCAB["<PAD>"]] * (max_len - len(ids))
    return ids


# ─────────────────────────────────────────────────────────
# 4. Semantic Discriminator Model
# ─────────────────────────────────────────────────────────


class SemanticDiscriminator(nn.Module):
    """Lightweight discriminator: embeds code tokens + classifies genuine vs adversarial."""

    def __init__(
        self, vocab_size=VOCAB_SIZE, embed_dim=64, hidden_dim=128, max_len=MAX_LEN
    ):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.encoder = nn.Sequential(
            nn.Linear(embed_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
        )
        self.classifier = nn.Linear(hidden_dim, 1)

    def forward(self, token_ids):
        # token_ids: (batch, max_len)
        emb = self.embedding(token_ids)  # (batch, max_len, embed_dim)
        pooled = emb.mean(dim=1)  # (batch, embed_dim)
        h = self.encoder(pooled)  # (batch, hidden_dim)
        logit = self.classifier(h).squeeze(-1)  # (batch,)
        return logit


# ─────────────────────────────────────────────────────────
# 5. Build discriminator training dataset
# ─────────────────────────────────────────────────────────


class CodeAlignmentDataset(Dataset):
    def __init__(self, samples):
        self.samples = samples  # list of (token_ids, label)

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        ids, label = self.samples[idx]
        return torch.tensor(ids, dtype=torch.long), torch.tensor(
            label, dtype=torch.float
        )


def build_discriminator_dataset(problems):
    samples = []
    for prob in problems:
        # Correct code → label 1 (semantically aligned)
        ids = tokenize_code(prob["correct_code"])
        samples.append((ids, 1))
        # Adversarial codes → label 0
        for adv in prob["adversarial_codes"]:
            ids = tokenize_code(adv)
            samples.append((ids, 0))
    return samples


all_samples = build_discriminator_dataset(PROBLEMS)
random.shuffle(all_samples)
split = int(0.75 * len(all_samples))
train_samples = all_samples[:split]
val_samples = all_samples[split:]

train_dataset = CodeAlignmentDataset(train_samples)
val_dataset = CodeAlignmentDataset(val_samples)
train_loader = DataLoader(train_dataset, batch_size=8, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=8, shuffle=False)

print(f"Discriminator dataset: {len(train_samples)} train, {len(val_samples)} val")

# ─────────────────────────────────────────────────────────
# 6. Train the Semantic Discriminator
# ─────────────────────────────────────────────────────────

discriminator = SemanticDiscriminator().to(device)
optimizer_disc = torch.optim.Adam(discriminator.parameters(), lr=1e-3)
criterion = nn.BCEWithLogitsLoss()

disc_train_losses = []
disc_val_losses = []
disc_val_accs = []

NUM_DISC_EPOCHS = 30

for epoch in range(1, NUM_DISC_EPOCHS + 1):
    discriminator.train()
    train_loss = 0.0
    for ids, labels in train_loader:
        ids = ids.to(device)
        labels = labels.to(device)
        optimizer_disc.zero_grad()
        logits = discriminator(ids)
        loss = criterion(logits, labels)
        loss.backward()
        optimizer_disc.step()
        train_loss += loss.item()
    train_loss /= len(train_loader)

    discriminator.eval()
    val_loss = 0.0
    all_preds, all_labels = [], []
    with torch.no_grad():
        for ids, labels in val_loader:
            ids = ids.to(device)
            labels = labels.to(device)
            logits = discriminator(ids)
            loss = criterion(logits, labels)
            val_loss += loss.item()
            preds = (torch.sigmoid(logits) > 0.5).cpu().numpy()
            all_preds.extend(preds)
            all_labels.extend(labels.cpu().numpy())
    val_loss /= max(len(val_loader), 1)
    val_acc = accuracy_score(all_labels, all_preds) if all_labels else 0.0

    disc_train_losses.append(train_loss)
    disc_val_losses.append(val_loss)
    disc_val_accs.append(val_acc)

    if epoch % 5 == 0 or epoch == 1:
        print(
            f"Discriminator Epoch {epoch:3d}: train_loss={train_loss:.4f}, val_loss={val_loss:.4f}, val_acc={val_acc:.4f}"
        )

# ─────────────────────────────────────────────────────────
# 7. Define reward functions
# ─────────────────────────────────────────────────────────


def execution_reward(code_str, given_tests):
    """Reward = pass rate on given (visible) tests."""
    return evaluate_code(code_str, given_tests)


def semantic_reward(code_str, discriminator, device):
    """Reward = discriminator probability of being semantically aligned."""
    discriminator.eval()
    ids = tokenize_code(code_str)
    t = torch.tensor([ids], dtype=torch.long).to(device)
    with torch.no_grad():
        logit = discriminator(t)
        prob = torch.sigmoid(logit).item()
    return prob


def combined_reward(code_str, given_tests, discriminator, device, alpha=0.5):
    """Combined execution + semantic reward."""
    exec_r = execution_reward(code_str, given_tests)
    sem_r = semantic_reward(code_str, discriminator, device)
    return (1 - alpha) * exec_r + alpha * sem_r


# ─────────────────────────────────────────────────────────
# 8. Simulate RL training: code candidates pool
# ─────────────────────────────────────────────────────────
# We simulate a population of candidate solutions for each problem:
# correct solutions, adversarial (test-overfitted) solutions, and partial solutions.
# RL selects the top-rewarded code; we measure SGG on the selected code.


def make_partial_code(prob):
    """A partially correct solution that fails some held-out tests."""
    pid = prob["id"]
    partial_codes = {
        0: "def sum_list(lst):\n    return sum(lst[:3])",
        1: "def max_list(lst):\n    return lst[0] if lst else 0",
        2: "def is_palindrome(s):\n    return len(s) <= 1",
        3: "def count_vowels(s):\n    return sum(1 for c in s if c in 'aeiou')",
        4: "def factorial(n):\n    if n <= 1: return 1\n    return n * (n-1)",
        5: "def is_even(n):\n    return n in [0, 2, 4, 6, 8]",
        6: "def reverse_str(s):\n    return s",
        7: "def longest_word(s):\n    return len(s.split()[0]) if s.split() else 0",
    }
    return partial_codes.get(pid, prob["correct_code"])


def get_candidate_pool(prob):
    """Returns list of candidate code strings."""
    candidates = [prob["correct_code"]]
    candidates += prob["adversarial_codes"]
    candidates.append(make_partial_code(prob))
    return candidates


# ─────────────────────────────────────────────────────────
# 9. Simulate RL selection over epochs
# ─────────────────────────────────────────────────────────

NUM_RL_EPOCHS = 20
alpha_sara = 0.5  # weight for semantic reward in SARA

experiment_data = {
    "baseline": {
        "metrics": {"train": [], "val": []},
        "losses": {"train": [], "val": []},
        "sgg": [],
        "given_pass_rate": [],
        "held_out_pass_rate": [],
    },
    "sara": {
        "metrics": {"train": [], "val": []},
        "losses": {"train": [], "val": []},
        "sgg": [],
        "given_pass_rate": [],
        "held_out_pass_rate": [],
    },
    "discriminator": {
        "train_loss": disc_train_losses,
        "val_loss": disc_val_losses,
        "val_acc": disc_val_accs,
    },
}

print("\n--- Simulating RL Training ---")
for epoch in range(1, NUM_RL_EPOCHS + 1):
    # Add noise to simulate stochastic RL exploration
    noise_scale = max(0.1, 0.5 - epoch * 0.02)

    baseline_given_rates = []
    baseline_held_rates = []
    sara_given_rates = []
    sara_held_rates = []

    for prob in PROBLEMS:
        candidates = get_candidate_pool(prob)

        # Baseline: select by execution reward only (+ noise)
        baseline_scores = [
            execution_reward(c, prob["given_tests"]) + np.random.normal(0, noise_scale)
            for c in candidates
        ]
        baseline_best = candidates[np.argmax(baseline_scores)]

        # SARA: select by combined reward (+ noise)
        sara_scores = [
            combined_reward(
                c, prob["given_tests"], discriminator, device, alpha=alpha_sara
            )
            + np.random.normal(0, noise_scale)
            for c in candidates
        ]
        sara_best = candidates[np.argmax(sara_scores)]

        # Evaluate selected code
        baseline_given = evaluate_code(baseline_best, prob["given_tests"])
        baseline_held = evaluate_code(baseline_best, prob["held_out_tests"])
        sara_given = evaluate_code(sara_best, prob["given_tests"])
        sara_held = evaluate_code(sara_best, prob["held_out_tests"])

        baseline_given_rates.append(baseline_given)
        baseline_held_rates.append(baseline_held)
        sara_given_rates.append(sara_given)
        sara_held_rates.append(sara_held)

    b_given = np.mean(baseline_given_rates)
    b_held = np.mean(baseline_held_rates)
    s_given = np.mean(sara_given_rates)
    s_held = np.mean(sara_held_rates)

    b_sgg = b_given - b_held
    s_sgg = s_given - s_held

    experiment_data["baseline"]["given_pass_rate"].append(b_given)
    experiment_data["baseline"]["held_out_pass_rate"].append(b_held)
    experiment_data["baseline"]["sgg"].append(b_sgg)
    experiment_data["baseline"]["metrics"]["train"].append(b_given)
    experiment_data["baseline"]["metrics"]["val"].append(b_held)

    experiment_data["sara"]["given_pass_rate"].append(s_given)
    experiment_data["sara"]["held_out_pass_rate"].append(s_held)
    experiment_data["sara"]["sgg"].append(s_sgg)
    experiment_data["sara"]["metrics"]["train"].append(s_given)
    experiment_data["sara"]["metrics"]["val"].append(s_held)

    if epoch % 5 == 0 or epoch == 1:
        print(
            f"Epoch {epoch:3d}: "
            f"Baseline SGG={b_sgg:.4f} (given={b_given:.4f}, held={b_held:.4f}) | "
            f"SARA SGG={s_sgg:.4f} (given={s_given:.4f}, held={s_held:.4f})"
        )

# ─────────────────────────────────────────────────────────
# 10. Final evaluation summary
# ─────────────────────────────────────────────────────────

final_b_sgg = np.mean(experiment_data["baseline"]["sgg"][-5:])
final_s_sgg = np.mean(experiment_data["sara"]["sgg"][-5:])
sgg_reduction = (final_b_sgg - final_s_sgg) / max(final_b_sgg, 1e-9) * 100

print("\n=== Final Results (last 5 epochs avg) ===")
print(f"Baseline SGG:       {final_b_sgg:.4f}")
print(f"SARA SGG:           {final_s_sgg:.4f}")
print(f"SGG Reduction:      {sgg_reduction:.1f}%")
print(
    f"Baseline given PR:  {np.mean(experiment_data['baseline']['given_pass_rate'][-5:]):.4f}"
)
print(
    f"Baseline held PR:   {np.mean(experiment_data['baseline']['held_out_pass_rate'][-5:]):.4f}"
)
print(
    f"SARA given PR:      {np.mean(experiment_data['sara']['given_pass_rate'][-5:]):.4f}"
)
print(
    f"SARA held PR:       {np.mean(experiment_data['sara']['held_out_pass_rate'][-5:]):.4f}"
)

# ─────────────────────────────────────────────────────────
# 11. Visualizations
# ─────────────────────────────────────────────────────────

epochs_rl = list(range(1, NUM_RL_EPOCHS + 1))
epochs_disc = list(range(1, NUM_DISC_EPOCHS + 1))

# Plot 1: Discriminator training
fig, axes = plt.subplots(1, 2, figsize=(12, 4))
axes[0].plot(epochs_disc, disc_train_losses, label="Train Loss")
axes[0].plot(epochs_disc, disc_val_losses, label="Val Loss")
axes[0].set_xlabel("Epoch")
axes[0].set_ylabel("BCE Loss")
axes[0].set_title("Discriminator Training Loss")
axes[0].legend()
axes[0].grid(True)

axes[1].plot(epochs_disc, disc_val_accs, label="Val Accuracy", color="green")
axes[1].set_xlabel("Epoch")
axes[1].set_ylabel("Accuracy")
axes[1].set_title("Discriminator Validation Accuracy")
axes[1].legend()
axes[1].grid(True)
plt.tight_layout()
plt.savefig(os.path.join(working_dir, "discriminator_training.png"), dpi=100)
plt.close()
print("Saved: discriminator_training.png")

# Plot 2: SGG comparison over RL epochs
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(
    epochs_rl,
    experiment_data["baseline"]["sgg"],
    label="Baseline (Exec Only)",
    color="red",
    linewidth=2,
)
ax.plot(
    epochs_rl,
    experiment_data["sara"]["sgg"],
    label="SARA (Exec + Semantic)",
    color="blue",
    linewidth=2,
)
ax.axhline(
    0, color="black", linestyle="--", alpha=0.5, label="SGG=0 (perfect generalization)"
)
ax.set_xlabel("RL Epoch")
ax.set_ylabel("Semantic Generalization Gap (SGG)")
ax.set_title("Semantic Generalization Gap: Baseline vs SARA")
ax.legend()
ax.grid(True)
plt.tight_layout()
plt.savefig(os.path.join(working_dir, "sgg_comparison.png"), dpi=100)
plt.close()
print("Saved: sgg_comparison.png")

# Plot 3: Pass rates comparison
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
axes[0].plot(
    epochs_rl,
    experiment_data["baseline"]["given_pass_rate"],
    label="Given Tests",
    color="red",
    linewidth=2,
)
axes[0].plot(
    epochs_rl,
    experiment_data["baseline"]["held_out_pass_rate"],
    label="Held-Out Tests",
    color="red",
    linewidth=2,
    linestyle="--",
)
axes[0].set_xlabel("RL Epoch")
axes[0].set_ylabel("Pass Rate")
axes[0].set_title("Baseline: Given vs Held-Out Pass Rate")
axes[0].legend()
axes[0].set_ylim(-0.05, 1.05)
axes[0].grid(True)

axes[1].plot(
    epochs_rl,
    experiment_data["sara"]["given_pass_rate"],
    label="Given Tests",
    color="blue",
    linewidth=2,
)
axes[1].plot(
    epochs_rl,
    experiment_data["sara"]["held_out_pass_rate"],
    label="Held-Out Tests",
    color="blue",
    linewidth=2,
    linestyle="--",
)
axes[1].set_xlabel("RL Epoch")
axes[1].set_ylabel("Pass Rate")
axes[1].set_title("SARA: Given vs Held-Out Pass Rate")
axes[1].legend()
axes[1].set_ylim(-0.05, 1.05)
axes[1].grid(True)
plt.tight_layout()
plt.savefig(os.path.join(working_dir, "pass_rates_comparison.png"), dpi=100)
plt.close()
print("Saved: pass_rates_comparison.png")

# Plot 4: Final bar chart
fig, ax = plt.subplots(figsize=(8, 5))
metrics = [
    "Given PR (Baseline)",
    "Held-Out PR (Baseline)",
    "Given PR (SARA)",
    "Held-Out PR (SARA)",
    "SGG (Baseline)",
    "SGG (SARA)",
]
values = [
    np.mean(experiment_data["baseline"]["given_pass_rate"][-5:]),
    np.mean(experiment_data["baseline"]["held_out_pass_rate"][-5:]),
    np.mean(experiment_data["sara"]["given_pass_rate"][-5:]),
    np.mean(experiment_data["sara"]["held_out_pass_rate"][-5:]),
    final_b_sgg,
    final_s_sgg,
]
colors = ["salmon", "darkred", "skyblue", "darkblue", "red", "blue"]
bars = ax.bar(metrics, values, color=colors, alpha=0.8)
ax.set_ylabel("Value")
ax.set_title("Final Metrics Summary (Last 5 Epochs Avg)")
ax.set_ylim(0, 1.2)
for bar, val in zip(bars, values):
    ax.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.02,
        f"{val:.3f}",
        ha="center",
        va="bottom",
        fontsize=9,
    )
plt.xticks(rotation=20, ha="right")
plt.tight_layout()
plt.savefig(os.path.join(working_dir, "final_metrics_summary.png"), dpi=100)
plt.close()
print("Saved: final_metrics_summary.png")

# ─────────────────────────────────────────────────────────
# 12. Save all experiment data
# ─────────────────────────────────────────────────────────

# Convert lists to numpy arrays for saving
for split_name in ["baseline", "sara"]:
    for key in ["sgg", "given_pass_rate", "held_out_pass_rate"]:
        experiment_data[split_name][key] = np.array(experiment_data[split_name][key])
    for key in ["train", "val"]:
        experiment_data[split_name]["metrics"][key] = np.array(
            experiment_data[split_name]["metrics"][key]
        )

for key in ["train_loss", "val_loss", "val_acc"]:
    experiment_data["discriminator"][key] = np.array(
        experiment_data["discriminator"][key]
    )

np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)
print("\nSaved: experiment_data.npy")

print("\n=== Experiment Complete ===")
print(f"Semantic Generalization Gap Reduction: {sgg_reduction:.1f}%")
print(f"Final Baseline SGG: {final_b_sgg:.4f}")
print(f"Final SARA SGG:     {final_s_sgg:.4f}")
