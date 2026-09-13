#!/usr/bin/env python3
"""
H-M1 PoC Experiment: Transformer vs Equivariant GNN Symmetry Analysis
Gate: GNN differential >30% AND Transformer differential <10%
"""
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
import timm
import random
import json
from pathlib import Path
from datetime import datetime

# ============================================================================
# Data Pipeline
# ============================================================================

class TimmModelZooDataset(Dataset):
    """Load timm models, tokenize weights as sequences"""
    def __init__(self, num_models=30, max_layer_size=4096, max_layers=500, seed=42):
        random.seed(seed)
        torch.manual_seed(seed)
        self.max_layers = max_layers

        # Load models
        model_names = timm.list_models(pretrained=True)
        random.shuffle(model_names)
        selected = model_names[:num_models]

        self.data = []
        print(f"Loading {num_models} models...")
        for name in selected:
            try:
                model = timm.create_model(name, pretrained=True)
                tokens = self._tokenize_weights(model, max_layer_size)
                # Pad to max_layers
                if tokens.shape[0] < max_layers:
                    padding = torch.zeros(max_layers - tokens.shape[0], max_layer_size)
                    tokens = torch.cat([tokens, padding], dim=0)
                else:
                    tokens = tokens[:max_layers]
                # Label: test accuracy bin (simulated from param count)
                params = sum(p.numel() for p in model.parameters())
                label = min(int((params / 1e7) ** 0.3), 3)  # 4-class
                self.data.append((tokens, label))
            except:
                continue

        print(f"Loaded {len(self.data)} models")

    def _tokenize_weights(self, model, max_size):
        """Extract layer weights, flatten, pad, normalize"""
        tokens = []
        for name, param in model.named_parameters():
            if 'weight' not in name:
                continue
            flat = param.data.flatten()
            # Pad or truncate
            if len(flat) > max_size:
                flat = flat[:max_size]
            else:
                flat = F.pad(flat, (0, max_size - len(flat)))
            # Normalize
            flat = (flat - flat.mean()) / (flat.std() + 1e-8)
            tokens.append(flat)

        return torch.stack(tokens)  # [num_layers, max_size]

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        return self.data[idx]

# ============================================================================
# Models
# ============================================================================

class WeightTransformer(nn.Module):
    """Transformer baseline (global attention)"""
    def __init__(self, max_layer_size=4096, hidden_dim=128, nhead=4, num_layers=2, num_classes=4):
        super().__init__()
        self.embed = nn.Linear(max_layer_size, hidden_dim)
        encoder_layer = nn.TransformerEncoderLayer(hidden_dim, nhead, dim_feedforward=256, dropout=0.1, batch_first=True)
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers)
        self.head = nn.Linear(hidden_dim, num_classes)

    def forward(self, x):
        # x: [B, T, L]
        x = self.embed(x)  # [B, T, H]
        x = self.transformer(x)  # [B, T, H]
        x = x.mean(dim=1)  # [B, H] global pooling
        return self.head(x)  # [B, C]

class WeightGNN(nn.Module):
    """E(n)-Equivariant GNN (local message passing)"""
    def __init__(self, max_layer_size=4096, hidden_dim=128, num_gnn_layers=2, num_classes=4):
        super().__init__()
        self.embed = nn.Linear(max_layer_size, hidden_dim)
        # Simplified GNN (ponytail: GraphConv instead of EGNN for PoC)
        self.gnn_layers = nn.ModuleList([
            nn.Linear(hidden_dim, hidden_dim) for _ in range(num_gnn_layers)
        ])
        self.head = nn.Linear(hidden_dim, num_classes)

    def forward(self, x):
        # x: [B, T, L]
        B, T, L = x.shape
        x = self.embed(x)  # [B, T, H]

        # GNN layers (simplified: linear + relu, ignores edges for PoC)
        for layer in self.gnn_layers:
            x = F.relu(layer(x))  # [B, T, H]

        x = x.mean(dim=1)  # [B, H] pooling
        return self.head(x)  # [B, C]

# ============================================================================
# Perturbations
# ============================================================================

def permute_within_layer(tokens, seed=42):
    """Shuffle indices within each layer"""
    torch.manual_seed(seed)
    B, T, L = tokens.shape
    perturbed = tokens.clone()
    for b in range(B):
        for t in range(T):
            idx = torch.randperm(L)
            perturbed[b, t] = perturbed[b, t, idx]
    return perturbed

def permute_across_layers(tokens, seed=42):
    """Shuffle indices across all layers"""
    torch.manual_seed(seed)
    B, T, L = tokens.shape
    perturbed = tokens.clone().view(B, -1)
    for b in range(B):
        idx = torch.randperm(T * L)
        perturbed[b] = perturbed[b, idx]
    return perturbed.view(B, T, L)

# ============================================================================
# Training & Evaluation
# ============================================================================

def train_model(model, train_loader, val_loader, epochs=10, lr=1e-3, device='cuda'):
    """Train model"""
    model.to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    criterion = nn.CrossEntropyLoss()

    best_val_acc = 0
    for epoch in range(epochs):
        model.train()
        train_loss = 0
        for tokens, labels in train_loader:
            tokens, labels = tokens.to(device), labels.to(device)
            optimizer.zero_grad()
            logits = model(tokens)
            loss = criterion(logits, labels)
            loss.backward()
            optimizer.step()
            train_loss += loss.item()

        # Validation
        model.eval()
        correct = 0
        total = 0
        with torch.no_grad():
            for tokens, labels in val_loader:
                tokens, labels = tokens.to(device), labels.to(device)
                logits = model(tokens)
                preds = logits.argmax(dim=1)
                correct += (preds == labels).sum().item()
                total += len(labels)

        val_acc = correct / total
        best_val_acc = max(best_val_acc, val_acc)
        print(f"Epoch {epoch+1}/{epochs} | Train Loss: {train_loss/len(train_loader):.4f} | Val Acc: {val_acc:.4f}")

    return best_val_acc

def evaluate_with_perturbations(model, test_loader, device='cuda'):
    """Evaluate on unperturbed/within/across perturbations"""
    model.to(device)
    model.eval()

    results = {}
    for perturb_type in [None, 'within', 'across']:
        correct = 0
        total = 0
        with torch.no_grad():
            for tokens, labels in test_loader:
                tokens = tokens.to(device)
                labels = labels.to(device)

                # Apply perturbation
                if perturb_type == 'within':
                    tokens = permute_within_layer(tokens)
                elif perturb_type == 'across':
                    tokens = permute_across_layers(tokens)

                logits = model(tokens)
                preds = logits.argmax(dim=1)
                correct += (preds == labels).sum().item()
                total += len(labels)

        acc = correct / total
        key = 'unperturbed' if perturb_type is None else f'{perturb_type}_layer'
        results[key] = acc

    # Symmetry differential
    results['differential'] = abs(results['within_layer'] - results['across_layer'])
    return results

# ============================================================================
# Main Experiment
# ============================================================================

def main():
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Device: {device}")

    # Load dataset
    dataset = TimmModelZooDataset(num_models=30, max_layer_size=4096, seed=42)

    # Split: 70/15/15
    train_size = int(0.7 * len(dataset))
    val_size = int(0.15 * len(dataset))
    test_size = len(dataset) - train_size - val_size
    train_set, val_set, test_set = torch.utils.data.random_split(dataset, [train_size, val_size, test_size])

    train_loader = DataLoader(train_set, batch_size=4, shuffle=True)
    val_loader = DataLoader(val_set, batch_size=4, shuffle=False)
    test_loader = DataLoader(test_set, batch_size=4, shuffle=False)

    print(f"\nDataset: {len(train_set)} train, {len(val_set)} val, {len(test_set)} test")

    # Train Transformer
    print("\n=== Training Transformer ===")
    transformer = WeightTransformer(hidden_dim=128, nhead=4, num_layers=2)
    train_model(transformer, train_loader, val_loader, epochs=10, device=device)

    # Train GNN
    print("\n=== Training GNN ===")
    gnn = WeightGNN(hidden_dim=128, num_gnn_layers=2)
    train_model(gnn, train_loader, val_loader, epochs=10, device=device)

    # Evaluate with perturbations
    print("\n=== Perturbation Analysis ===")
    transformer_results = evaluate_with_perturbations(transformer, test_loader, device)
    gnn_results = evaluate_with_perturbations(gnn, test_loader, device)

    print("\nTransformer:")
    print(f"  Unperturbed: {transformer_results['unperturbed']:.4f}")
    print(f"  Within-layer: {transformer_results['within_layer']:.4f}")
    print(f"  Across-layer: {transformer_results['across_layer']:.4f}")
    print(f"  Differential: {transformer_results['differential']:.4f}")

    print("\nGNN:")
    print(f"  Unperturbed: {gnn_results['unperturbed']:.4f}")
    print(f"  Within-layer: {gnn_results['within_layer']:.4f}")
    print(f"  Across-layer: {gnn_results['across_layer']:.4f}")
    print(f"  Differential: {gnn_results['differential']:.4f}")

    # Gate check
    gate_pass = (gnn_results['differential'] > 0.30 and transformer_results['differential'] < 0.10)
    print("\n=== Gate Result ===")
    print(f"GNN differential > 30%: {gnn_results['differential'] > 0.30} ({gnn_results['differential']:.1%})")
    print(f"Transformer differential < 10%: {transformer_results['differential'] < 0.10} ({transformer_results['differential']:.1%})")
    print(f"Gate: {'PASS' if gate_pass else 'FAIL'}")

    # Save results
    output = {
        'transformer': transformer_results,
        'gnn': gnn_results,
        'gate_pass': gate_pass,
        'timestamp': datetime.now().isoformat()
    }

    Path('outputs').mkdir(exist_ok=True)
    with open('outputs/results.json', 'w') as f:
        json.dump(output, f, indent=2)

    print("\nResults saved to outputs/results.json")
    print("EXPERIMENT COMPLETE")

if __name__ == '__main__':
    main()
