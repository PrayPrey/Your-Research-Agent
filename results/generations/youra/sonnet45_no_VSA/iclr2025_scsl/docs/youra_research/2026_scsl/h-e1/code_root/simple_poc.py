#!/usr/bin/env python3
"""
Simplified Proof-of-Concept for H-E1: Joint SAM+DRO Existence
Creates synthetic data to demonstrate the joint optimization concept.
"""

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from pathlib import Path
import json
import sys

# Set random seeds for reproducibility
def set_seed(seed=42):
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    np.random.seed(seed)
    if torch.cuda.is_available():
        torch.backends.cudnn.deterministic = True
        torch.backends.cudnn.benchmark = False

set_seed(42)

# Simplified model (2-layer MLP instead of ResNet-50)
class SimpleModel(nn.Module):
    def __init__(self, input_dim=10, hidden_dim=20, num_classes=2):
        super().__init__()
        self.fc1 = nn.Linear(input_dim, hidden_dim)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_dim, num_classes)

    def forward(self, x):
        x = self.fc1(x)
        x = self.relu(x)
        x = self.fc2(x)
        return x


# Synthetic dataset with spurious correlation
class SyntheticSpuriousDataset:
    """
    Generate synthetic data with spurious correlation:
    - 4 groups based on (true_label, spurious_feature)
    - Group sizes: imbalanced (simulate Waterbirds minority group)
    """
    def __init__(self, n_samples=1000, input_dim=10, minority_ratio=0.1):
        self.n_samples = n_samples
        self.input_dim = input_dim

        # Generate data
        self.X = []
        self.y = []
        self.groups = []

        # Group distribution: (label=0, spurious=0), (label=0, spurious=1),
        #                     (label=1, spurious=0), (label=1, spurious=1)
        # Minority group: (label=0, spurious=1) - only 10% of samples
        group_sizes = [
            int(n_samples * 0.4),    # Group 0: label=0, spurious=0 (majority)
            int(n_samples * minority_ratio),  # Group 1: label=0, spurious=1 (minority)
            int(n_samples * 0.4),    # Group 2: label=1, spurious=0 (majority)
            int(n_samples * (0.1 - minority_ratio + 0.4))  # Group 3: label=1, spurious=1
        ]

        for group_id, group_size in enumerate(group_sizes):
            true_label = group_id // 2  # 0 or 1
            spurious_feature = group_id % 2

            for _ in range(group_size):
                # Generate features: first 5 dimensions correlate with true label
                # Last 5 dimensions correlate with spurious feature
                x = np.random.randn(input_dim)

                # True signal
                if true_label == 1:
                    x[:5] += 1.0

                # Spurious signal (stronger correlation)
                if spurious_feature == 1:
                    x[5:] += 2.0

                self.X.append(x)
                self.y.append(true_label)
                self.groups.append(group_id)

        self.X = np.array(self.X, dtype=np.float32)
        self.y = np.array(self.y, dtype=np.int64)
        self.groups = np.array(self.groups, dtype=np.int64)

        print(f"Dataset created: {len(self.X)} samples")
        print(f"Group sizes: {np.bincount(self.groups)}")
        print(f"Minority group (group 1): {np.sum(self.groups == 1)} samples")


# Environment classifier (simple version)
class SimpleEnvClassifier(nn.Module):
    def __init__(self, input_dim=10, num_groups=4):
        super().__init__()
        self.fc = nn.Linear(input_dim, num_groups)

    def forward(self, x):
        logits = self.fc(x)
        return torch.softmax(logits, dim=1)


# Joint SAM+DRO Optimizer
class JointSAMDRO:
    def __init__(self, model, env_classifier, rho=0.05, C=0.5, lambda1=1.0, lambda2=0.5, lr=1e-3):
        self.model = model
        self.env_classifier = env_classifier
        self.rho = rho
        self.C = C
        self.lambda1 = lambda1
        self.lambda2 = lambda2

        self.base_optimizer = optim.SGD(model.parameters(), lr=lr, momentum=0.9, weight_decay=1e-4)
        self.group_weights = torch.ones(4) / 4  # [4] uniform initialization
        self.num_groups = 4

    def step(self, X, y, groups, criterion):
        """Execute one joint SAM+DRO step"""
        device = next(self.model.parameters()).device
        X = X.to(device)
        y = y.to(device)
        groups = groups.to(device)

        self.base_optimizer.zero_grad()

        # Step 1: Compute soft group assignments Q_hat
        with torch.no_grad():
            Q_hat = self.env_classifier(X)  # [B, 4]

        # Step 2: Base forward pass
        logits = self.model(X)  # [B, 2]
        loss_per_sample = criterion(logits, y)  # [B]

        # Step 3: Compute per-group base losses L_g
        L_g = torch.zeros(self.num_groups, device=device)
        for g in range(self.num_groups):
            weights = Q_hat[:, g]  # [B]
            L_g[g] = (weights * loss_per_sample).sum() / (weights.sum() + 1e-8)

        # Step 4: Compute per-group perturbations and sharpness
        S_g = []
        param_backup = [p.data.clone() for p in self.model.parameters()]

        for g in range(self.num_groups):
            # Compute group gradient
            self.base_optimizer.zero_grad()
            L_g[g].backward(retain_graph=True)

            # Compute gradient norm
            grad_norm = torch.sqrt(sum([p.grad.pow(2).sum() for p in self.model.parameters() if p.grad is not None]))

            # Apply perturbation
            with torch.no_grad():
                for p in self.model.parameters():
                    if p.grad is not None:
                        epsilon_g = self.rho * p.grad / (grad_norm + 1e-12)
                        p.data.add_(epsilon_g)

            # Forward at perturbed params
            logits_pert = self.model(X)
            loss_per_sample_pert = criterion(logits_pert, y)
            weights = Q_hat[:, g]
            L_g_pert = (weights * loss_per_sample_pert).sum() / (weights.sum() + 1e-8)

            # Compute sharpness
            S_g.append(L_g_pert - L_g[g])

            # Revert parameters
            for p, p_backup in zip(self.model.parameters(), param_backup):
                p.data.copy_(p_backup)

        # Step 5: Compute sharpness statistics
        S_g = torch.stack(S_g)  # [4]
        S_worst = S_g.max()
        Var_g = S_g.var()

        # Step 6: Compute total objective
        DRO_loss = (self.group_weights.to(device) * L_g.detach()).sum()
        total_loss = self.lambda1 * S_worst + self.lambda2 * Var_g + DRO_loss

        # Step 7: Backward and update
        self.base_optimizer.zero_grad()
        total_loss.backward()
        self.base_optimizer.step()

        # Step 8: Update group weights (DRO reweighting)
        with torch.no_grad():
            group_counts = torch.bincount(groups, minlength=4).float().to(device)
            self.group_weights = self.group_weights.to(device)
            self.group_weights *= torch.exp(self.C * L_g.detach() / torch.sqrt(group_counts + 1e-8))
            self.group_weights /= self.group_weights.sum()
            self.group_weights = self.group_weights.cpu()  # Keep weights on CPU for consistency

        return {
            'loss': total_loss.item(),
            'S_worst': S_worst.item(),
            'Var_g': Var_g.item(),
            'L_g_0': L_g[0].item(),
            'L_g_1': L_g[1].item(),
            'L_g_2': L_g[2].item(),
            'L_g_3': L_g[3].item(),
        }


# Baseline optimizers
class StandardSGD:
    def __init__(self, model, lr=1e-3):
        self.model = model
        self.optimizer = optim.SGD(model.parameters(), lr=lr, momentum=0.9, weight_decay=1e-4)

    def step(self, X, y, groups, criterion):
        device = next(self.model.parameters()).device
        X, y = X.to(device), y.to(device)

        self.optimizer.zero_grad()
        logits = self.model(X)
        loss = criterion(logits, y).mean()  # Average over batch
        loss.backward()
        self.optimizer.step()

        return {'loss': loss.item()}


# Evaluation
def evaluate(model, X, y, groups, criterion):
    """Compute worst-group accuracy"""
    device = next(model.parameters()).device
    X, y, groups = X.to(device), y.to(device), groups.to(device)

    model.eval()
    with torch.no_grad():
        logits = model(X)
        preds = logits.argmax(dim=1)
        correct = (preds == y).cpu().numpy()

        # Per-group accuracy
        group_accs = []
        for g in range(4):
            mask = (groups == g).cpu().numpy()
            if mask.sum() > 0:
                acc = correct[mask].mean()
                group_accs.append(acc)
            else:
                group_accs.append(0.0)

        worst_group_acc = min(group_accs)
        avg_acc = correct.mean()

    model.train()
    return {
        'worst_group_acc': worst_group_acc,
        'avg_acc': avg_acc,
        'group_accs': group_accs
    }


def main():
    # Setup
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    # Create synthetic dataset
    print("\n=== Creating Synthetic Dataset ===")
    dataset = SyntheticSpuriousDataset(n_samples=1000, input_dim=10, minority_ratio=0.1)

    # Split into train/val/test
    n_train = 600
    n_val = 200
    n_test = 200

    X_train = torch.from_numpy(dataset.X[:n_train])
    y_train = torch.from_numpy(dataset.y[:n_train])
    g_train = torch.from_numpy(dataset.groups[:n_train])

    X_val = torch.from_numpy(dataset.X[n_train:n_train+n_val])
    y_val = torch.from_numpy(dataset.y[n_train:n_train+n_val])
    g_val = torch.from_numpy(dataset.groups[n_train:n_train+n_val])

    X_test = torch.from_numpy(dataset.X[n_train+n_val:])
    y_test = torch.from_numpy(dataset.y[n_train+n_val:])
    g_test = torch.from_numpy(dataset.groups[n_train+n_val:])

    # Results storage
    results = {}

    # Condition 1: Standard SGD (Baseline)
    print("\n=== Training Standard SGD ===")
    model_sgd = SimpleModel(input_dim=10).to(device)
    optimizer_sgd = StandardSGD(model_sgd, lr=1e-2)  # Increased LR for simpler model
    criterion = nn.CrossEntropyLoss(reduction='none')

    for epoch in range(100):  # More epochs for convergence
        metrics = optimizer_sgd.step(X_train, y_train, g_train, criterion)
        if (epoch + 1) % 20 == 0:
            val_metrics = evaluate(model_sgd, X_val, y_val, g_val, criterion)
            print(f"Epoch {epoch+1}: Loss = {metrics['loss']:.4f}, Val Worst-Group Acc = {val_metrics['worst_group_acc']:.4f}, Avg = {val_metrics['avg_acc']:.4f}")

    test_sgd = evaluate(model_sgd, X_test, y_test, g_test, criterion)
    results['sgd'] = test_sgd
    print(f"SGD Test - Worst-Group: {test_sgd['worst_group_acc']:.4f}, Avg: {test_sgd['avg_acc']:.4f}")

    # Condition 2: Joint SAM+DRO
    print("\n=== Training Joint SAM+DRO ===")
    model_joint = SimpleModel(input_dim=10).to(device)
    env_classifier = SimpleEnvClassifier(input_dim=10).to(device)

    # Pre-train environment classifier on a few samples (simplified)
    print("Pre-training environment classifier...")
    env_optimizer = optim.Adam(env_classifier.parameters(), lr=1e-3)
    for _ in range(20):
        env_optimizer.zero_grad()
        Q_logits = env_classifier(X_train[:100].to(device))
        loss = nn.CrossEntropyLoss()(Q_logits, g_train[:100].to(device))
        loss.backward()
        env_optimizer.step()

    env_classifier.eval()  # Freeze after pre-training

    optimizer_joint = JointSAMDRO(model_joint, env_classifier, rho=0.05, C=0.5, lambda1=1.0, lambda2=0.5, lr=1e-2)

    for epoch in range(100):  # Match SGD epochs
        metrics = optimizer_joint.step(X_train, y_train, g_train, criterion)
        if (epoch + 1) % 20 == 0:
            val_metrics = evaluate(model_joint, X_val, y_val, g_val, criterion)
            print(f"Epoch {epoch+1}: Loss = {metrics['loss']:.4f}, Val Worst-Group Acc = {val_metrics['worst_group_acc']:.4f}, Avg = {val_metrics['avg_acc']:.4f}, S_worst = {metrics['S_worst']:.4f}")

    test_joint = evaluate(model_joint, X_test, y_test, g_test, criterion)
    results['joint'] = test_joint
    print(f"Joint Test - Worst-Group: {test_joint['worst_group_acc']:.4f}, Avg: {test_joint['avg_acc']:.4f}")

    # Save results
    output_dir = Path("/workspace/TEST_scsl/outputs/h-e1-poc")
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_dir / "results.json", "w") as f:
        json.dump({
            'sgd': {k: float(v) if not isinstance(v, list) else [float(x) for x in v]
                    for k, v in test_sgd.items()},
            'joint': {k: float(v) if not isinstance(v, list) else [float(x) for x in v]
                      for k, v in test_joint.items()}
        }, f, indent=2)

    # Gate evaluation (simplified - no statistical test due to single seed)
    improvement = test_joint['worst_group_acc'] - test_sgd['worst_group_acc']
    print(f"\n=== Results Summary ===")
    print(f"SGD Worst-Group Accuracy: {test_sgd['worst_group_acc']:.4f}")
    print(f"Joint Worst-Group Accuracy: {test_joint['worst_group_acc']:.4f}")
    print(f"Improvement: {improvement:.4f}")

    if improvement > 0.05:  # 5% improvement threshold for PoC
        print("✓ PoC PASSED: Joint optimizer shows improvement over baseline")
        gate_result = "PASS"
    else:
        print("✗ PoC FAILED: No significant improvement observed")
        gate_result = "FAIL"

    # Generate validation report
    validation_report = f"""# H-E1 Validation Report (Proof-of-Concept)

## Experiment Summary
- **Hypothesis**: h-e1 (EXISTENCE)
- **Date**: 2026-07-10
- **Mode**: Simplified PoC with synthetic data

## Results

### Test Accuracies
| Method | Worst-Group Acc | Average Acc | Group 0 | Group 1 | Group 2 | Group 3 |
|--------|-----------------|-------------|---------|---------|---------|---------|
| SGD    | {test_sgd['worst_group_acc']:.4f} | {test_sgd['avg_acc']:.4f} | {test_sgd['group_accs'][0]:.4f} | {test_sgd['group_accs'][1]:.4f} | {test_sgd['group_accs'][2]:.4f} | {test_sgd['group_accs'][3]:.4f} |
| Joint  | {test_joint['worst_group_acc']:.4f} | {test_joint['avg_acc']:.4f} | {test_joint['group_accs'][0]:.4f} | {test_joint['group_accs'][1]:.4f} | {test_joint['group_accs'][2]:.4f} | {test_joint['group_accs'][3]:.4f} |

### Gate Evaluation
- **Improvement**: {improvement:.4f} ({improvement*100:.1f}%)
- **Gate Result**: {gate_result}

## Notes
This is a simplified proof-of-concept using:
- Synthetic data (1000 samples, 10-dimensional features)
- Simple 2-layer MLP model (not ResNet-50)
- Single training seed (no statistical testing)
- 50 training epochs (not full hyperparameter search)

**Next Steps**:
- Full implementation with Waterbirds dataset required for formal validation
- Multiple seeds for statistical significance testing
- Hyperparameter search for optimal configuration
"""

    with open(output_dir / "validation_report.md", "w") as f:
        f.write(validation_report)

    print(f"\nResults saved to {output_dir}")
    return 0 if gate_result == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
