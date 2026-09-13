import os
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from scipy.stats import pearsonr
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

working_dir = os.path.join(os.getcwd(), "working")
os.makedirs(working_dir, exist_ok=True)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Using device: {device}")

np.random.seed(42)
torch.manual_seed(42)

# Documentation dimensions and their weights
DOC_DIMENSIONS = [
    "provenance",
    "limitations",
    "intended_use",
    "demographics",
    "methodology",
]


def generate_documentation_score():
    """Generate random documentation scores for each dimension (0-1 scale)"""
    scores = {dim: np.random.beta(2, 2) for dim in DOC_DIMENSIONS}
    # Compute overall documentation debt (1 - average score, so higher = worse documentation)
    debt_score = 1 - np.mean(list(scores.values()))
    return scores, debt_score


def generate_synthetic_dataset(doc_scores, n_samples=1000, n_features=20, n_classes=2):
    """
    Generate synthetic dataset with properties influenced by documentation quality.
    Poor documentation correlates with:
    - More noise (limitations not documented)
    - Class imbalance (demographics not documented)
    - Feature noise (methodology not documented)
    """
    # Base dataset generation
    X = np.random.randn(n_samples, n_features)

    # True signal in first few features
    true_weights = np.zeros(n_features)
    true_weights[:5] = np.random.randn(5) * 2

    logits = X @ true_weights

    # Add noise based on limitations score (lower score = more noise)
    noise_level = 2 * (1 - doc_scores["limitations"])
    logits += np.random.randn(n_samples) * noise_level

    # Create class imbalance based on demographics score
    threshold_shift = (1 - doc_scores["demographics"]) * 1.5
    y = (logits > threshold_shift).astype(int)

    # Add feature noise based on methodology score
    feature_noise = (1 - doc_scores["methodology"]) * 0.5
    X += np.random.randn(n_samples, n_features) * feature_noise

    # Add spurious correlations based on intended_use score
    if doc_scores["intended_use"] < 0.5:
        spurious_feature = y + np.random.randn(n_samples) * 0.3
        X[:, -1] = spurious_feature  # This feature won't transfer well

    return X, y


class SimpleClassifier(nn.Module):
    def __init__(self, input_dim, hidden_dim=64):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim // 2, 2),
        )

    def forward(self, x):
        return self.net(x)


def train_and_evaluate(X, y, n_epochs=50, batch_size=64):
    """Train a model and return failure rate (1 - test accuracy)"""
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    X_train, X_val, y_train, y_val = train_test_split(
        X_train, y_train, test_size=0.2, random_state=42
    )

    # Normalize
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_val = scaler.transform(X_val)
    X_test = scaler.transform(X_test)

    # Convert to tensors
    X_train_t = torch.FloatTensor(X_train).to(device)
    y_train_t = torch.LongTensor(y_train).to(device)
    X_val_t = torch.FloatTensor(X_val).to(device)
    y_val_t = torch.LongTensor(y_val).to(device)
    X_test_t = torch.FloatTensor(X_test).to(device)
    y_test_t = torch.LongTensor(y_test).to(device)

    train_dataset = TensorDataset(X_train_t, y_train_t)
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)

    # Model
    model = SimpleClassifier(X.shape[1]).to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    train_losses = []
    val_losses = []

    for epoch in range(n_epochs):
        model.train()
        epoch_loss = 0
        for batch_X, batch_y in train_loader:
            optimizer.zero_grad()
            outputs = model(batch_X)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item()

        train_losses.append(epoch_loss / len(train_loader))

        # Validation
        model.eval()
        with torch.no_grad():
            val_outputs = model(X_val_t)
            val_loss = criterion(val_outputs, y_val_t).item()
            val_losses.append(val_loss)

        if (epoch + 1) % 10 == 0:
            print(f"Epoch {epoch+1}: validation_loss = {val_loss:.4f}")

    # Test evaluation
    model.eval()
    with torch.no_grad():
        test_outputs = model(X_test_t)
        _, predicted = torch.max(test_outputs, 1)
        test_accuracy = (predicted == y_test_t).float().mean().item()

    failure_rate = 1 - test_accuracy
    return failure_rate, train_losses, val_losses, test_accuracy


# Main experiment
print("=" * 60)
print("Documentation Debt: Linking Documentation Quality to Model Failures")
print("=" * 60)

n_datasets = 50  # Number of synthetic datasets to generate
n_samples_per_dataset = 1000
n_features = 20

experiment_data = {
    "documentation_scores": [],
    "debt_scores": [],
    "failure_rates": [],
    "test_accuracies": [],
    "dimension_scores": {dim: [] for dim in DOC_DIMENSIONS},
    "training_losses": [],
    "validation_losses": [],
}

print(f"\nGenerating and evaluating {n_datasets} synthetic datasets...")
print("-" * 60)

for i in range(n_datasets):
    print(f"\nDataset {i+1}/{n_datasets}")

    # Generate documentation scores
    doc_scores, debt_score = generate_documentation_score()

    # Store dimension scores
    for dim in DOC_DIMENSIONS:
        experiment_data["dimension_scores"][dim].append(doc_scores[dim])
    experiment_data["debt_scores"].append(debt_score)

    print(f"  Documentation Debt Score: {debt_score:.3f}")

    # Generate dataset influenced by documentation quality
    X, y = generate_synthetic_dataset(doc_scores, n_samples_per_dataset, n_features)

    # Train and evaluate
    failure_rate, train_losses, val_losses, test_acc = train_and_evaluate(
        X, y, n_epochs=30
    )

    experiment_data["failure_rates"].append(failure_rate)
    experiment_data["test_accuracies"].append(test_acc)
    experiment_data["training_losses"].append(train_losses)
    experiment_data["validation_losses"].append(val_losses)

    print(f"  Test Accuracy: {test_acc:.3f}, Failure Rate: {failure_rate:.3f}")

# Convert to numpy arrays for analysis
debt_scores = np.array(experiment_data["debt_scores"])
failure_rates = np.array(experiment_data["failure_rates"])

# Compute main metric: correlation between documentation debt and failure rate
correlation, p_value = pearsonr(debt_scores, failure_rates)

print("\n" + "=" * 60)
print("RESULTS")
print("=" * 60)
print(f"\nMain Metric - Documentation-Failure Correlation: {correlation:.4f}")
print(f"P-value: {p_value:.6f}")
print(f"Statistically significant (p < 0.05): {p_value < 0.05}")

# Per-dimension correlations
print("\nCorrelation by Documentation Dimension (with failure rate):")
dimension_correlations = {}
for dim in DOC_DIMENSIONS:
    dim_scores = np.array(experiment_data["dimension_scores"][dim])
    # Note: lower dimension score = worse documentation = should correlate with higher failure
    dim_corr, dim_p = pearsonr(
        1 - dim_scores, failure_rates
    )  # Invert so higher = worse doc
    dimension_correlations[dim] = dim_corr
    print(f"  {dim}: r = {dim_corr:.4f} (p = {dim_p:.4f})")

# Summary statistics
print(f"\nSummary Statistics:")
print(
    f"  Mean Documentation Debt: {debt_scores.mean():.3f} (std: {debt_scores.std():.3f})"
)
print(
    f"  Mean Failure Rate: {failure_rates.mean():.3f} (std: {failure_rates.std():.3f})"
)
print(f"  Mean Test Accuracy: {np.mean(experiment_data['test_accuracies']):.3f}")

# Save experiment data
experiment_data["documentation_failure_correlation"] = correlation
experiment_data["p_value"] = p_value
experiment_data["dimension_correlations"] = dimension_correlations
np.save(os.path.join(working_dir, "experiment_data.npy"), experiment_data)

# Visualization 1: Documentation Debt vs Failure Rate
plt.figure(figsize=(10, 6))
plt.scatter(debt_scores, failure_rates, alpha=0.7, edgecolors="black", linewidth=0.5)
z = np.polyfit(debt_scores, failure_rates, 1)
p = np.poly1d(z)
x_line = np.linspace(debt_scores.min(), debt_scores.max(), 100)
plt.plot(
    x_line, p(x_line), "r--", linewidth=2, label=f"Linear fit (r={correlation:.3f})"
)
plt.xlabel("Documentation Debt Score (higher = worse documentation)", fontsize=12)
plt.ylabel("Model Failure Rate (1 - accuracy)", fontsize=12)
plt.title("Documentation Debt vs Model Failure Rate", fontsize=14)
plt.legend()
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(os.path.join(working_dir, "debt_vs_failure_scatter.png"), dpi=150)
plt.close()

# Visualization 2: Per-dimension correlation bar chart
plt.figure(figsize=(10, 6))
dims = list(dimension_correlations.keys())
corrs = [dimension_correlations[d] for d in dims]
colors = ["red" if c > 0.3 else "orange" if c > 0.1 else "green" for c in corrs]
bars = plt.bar(dims, corrs, color=colors, edgecolor="black", alpha=0.7)
plt.axhline(y=0, color="black", linestyle="-", linewidth=0.5)
plt.xlabel("Documentation Dimension", fontsize=12)
plt.ylabel("Correlation with Failure Rate", fontsize=12)
plt.title("Which Documentation Elements Predict Failures?", fontsize=14)
plt.xticks(rotation=45, ha="right")
for bar, corr in zip(bars, corrs):
    plt.text(
        bar.get_x() + bar.get_width() / 2,
        bar.get_height() + 0.01,
        f"{corr:.3f}",
        ha="center",
        va="bottom",
        fontsize=10,
    )
plt.tight_layout()
plt.savefig(os.path.join(working_dir, "dimension_correlations.png"), dpi=150)
plt.close()

# Visualization 3: Distribution of failure rates by documentation quality quartiles
plt.figure(figsize=(10, 6))
quartiles = np.percentile(debt_scores, [25, 50, 75])
quartile_labels = ["Q1 (Best Doc)", "Q2", "Q3", "Q4 (Worst Doc)"]
quartile_failures = []
for i in range(4):
    if i == 0:
        mask = debt_scores <= quartiles[0]
    elif i == 3:
        mask = debt_scores > quartiles[2]
    else:
        mask = (debt_scores > quartiles[i - 1]) & (debt_scores <= quartiles[i])
    quartile_failures.append(failure_rates[mask])

plt.boxplot(quartile_failures, labels=quartile_labels)
plt.xlabel("Documentation Quality Quartile", fontsize=12)
plt.ylabel("Model Failure Rate", fontsize=12)
plt.title("Failure Rate Distribution by Documentation Quality", fontsize=14)
plt.grid(True, alpha=0.3, axis="y")
plt.tight_layout()
plt.savefig(os.path.join(working_dir, "quartile_boxplot.png"), dpi=150)
plt.close()

print(f"\nVisualization saved to: {working_dir}")
print(f"\nFinal documentation_failure_correlation = {correlation:.4f}")
