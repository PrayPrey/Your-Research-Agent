"""
Training script for CAWE model.
Implements training loop with early stopping based on validation Spearman ρ.
"""
import torch
import torch.nn as nn
import torch.optim as optim
from scipy.stats import spearmanr
import numpy as np
import os
import sys
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from cawe.models import CAWE
from cawe.data import create_dataloaders


def train_epoch(model, loader, optimizer, criterion, device):
    """Train for one epoch."""
    model.train()
    total_loss = 0.0
    num_batches = 0

    for batch in loader:
        state_dicts, arch_families, gaps = batch
        gaps = gaps.to(device)

        # Forward pass
        optimizer.zero_grad()
        predictions = []

        for i in range(len(arch_families)):
            pred = model(state_dicts[i], arch_families[i])
            predictions.append(pred)

        predictions = torch.stack(predictions).to(device)

        # Compute loss
        loss = criterion(predictions, gaps)
        loss.backward()
        optimizer.step()

        total_loss += loss.item()
        num_batches += 1

    return total_loss / num_batches


def evaluate(model, loader, device):
    """Evaluate model and compute Spearman ρ."""
    model.eval()
    all_predictions = []
    all_targets = []

    with torch.no_grad():
        for batch in loader:
            state_dicts, arch_families, gaps = batch

            for i in range(len(arch_families)):
                pred = model(state_dicts[i], arch_families[i])
                all_predictions.append(pred.item())
                all_targets.append(gaps[i].item())

    # Compute Spearman correlation
    if len(all_predictions) > 1:
        rho, _ = spearmanr(all_predictions, all_targets)
    else:
        rho = 0.0

    return rho


def main():
    parser = argparse.ArgumentParser(description='Train CAWE model')
    parser.add_argument('--epochs', type=int, default=10, help='Number of epochs (PoC: 10)')
    parser.add_argument('--batch-size', type=int, default=16, help='Batch size (PoC: 16)')
    parser.add_argument('--lr', type=float, default=1e-4, help='Learning rate')
    parser.add_argument('--patience', type=int, default=5, help='Early stopping patience')
    parser.add_argument('--save-dir', type=str, default='../outputs', help='Directory to save models')
    parser.add_argument('--train-samples', type=int, default=150, help='Number of training samples (default: 150 for reasonable PoC)')
    parser.add_argument('--val-samples', type=int, default=60, help='Number of validation samples (default: 60)')
    parser.add_argument('--test-samples', type=int, default=60, help='Number of test samples (default: 60)')
    args = parser.parse_args()

    # Set device
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")

    # Create dataloaders with REAL models
    # Using reasonable subset for PoC: 150 train, 60 val, 60 test (stratified by architecture)
    print("Loading REAL model zoo data (this may take time on first run)...")
    train_loader, val_loader, test_loader = create_dataloaders(
        batch_size=args.batch_size,
        train_samples=args.train_samples,
        val_samples=args.val_samples,
        test_samples=args.test_samples
    )
    print(f"Train: {len(train_loader.dataset)} samples")
    print(f"Val: {len(val_loader.dataset)} samples")
    print(f"Test: {len(test_loader.dataset)} samples")

    # Create model
    print("\nInitializing CAWE model...")
    model = CAWE(token_dim=128, nft_channels=64).to(device)
    print(f"Model parameters: {sum(p.numel() for p in model.parameters()):,}")

    # Optimizer and loss
    optimizer = optim.AdamW(model.parameters(), lr=args.lr, weight_decay=1e-2)
    criterion = nn.MSELoss()

    # Training loop with early stopping
    print("\nTraining...")
    best_val_rho = -1.0
    patience_counter = 0
    os.makedirs(args.save_dir, exist_ok=True)

    for epoch in range(1, args.epochs + 1):
        # Train
        train_loss = train_epoch(model, train_loader, optimizer, criterion, device)

        # Validate
        val_rho = evaluate(model, val_loader, device)

        print(f"Epoch {epoch}/{args.epochs} - Loss: {train_loss:.4f}, Val Rho: {val_rho:.4f}")

        # Early stopping check
        if val_rho > best_val_rho:
            best_val_rho = val_rho
            patience_counter = 0
            # Save best model
            torch.save({
                'epoch': epoch,
                'model_state_dict': model.state_dict(),
                'optimizer_state_dict': optimizer.state_dict(),
                'val_rho': val_rho,
            }, os.path.join(args.save_dir, 'best_model.pt'))
            print(f"  → Saved best model (rho={val_rho:.4f})")
        else:
            patience_counter += 1
            if patience_counter >= args.patience:
                print(f"\nEarly stopping triggered at epoch {epoch}")
                break

    # Load best model and evaluate on test set
    print("\nEvaluating best model on test set...")
    checkpoint = torch.load(os.path.join(args.save_dir, 'best_model.pt'), weights_only=False)
    model.load_state_dict(checkpoint['model_state_dict'])
    test_rho = evaluate(model, test_loader, device)
    print(f"Test Spearman ρ: {test_rho:.4f}")

    # Save final results
    results = {
        'best_val_rho': best_val_rho,
        'test_rho': test_rho,
        'final_epoch': epoch
    }

    import json
    with open(os.path.join(args.save_dir, 'training_results.json'), 'w') as f:
        json.dump(results, f, indent=2)

    print("\nTraining complete!")
    print(f"Best Val Rho: {best_val_rho:.4f}")
    print(f"Test Rho: {test_rho:.4f}")


if __name__ == '__main__':
    main()
