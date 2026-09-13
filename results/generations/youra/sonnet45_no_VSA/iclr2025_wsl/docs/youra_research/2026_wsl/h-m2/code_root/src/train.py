"""Training infrastructure for width-scaling experiment."""

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from typing import Dict, Tuple
from pathlib import Path
import json


class WidthScalingTrainer:
    """Trainer for width-scaling experiment with loss-matching constraint."""

    def __init__(self, config: dict):
        """
        Initialize trainer.

        Args:
            config: Configuration dictionary
        """
        self.config = config
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.checkpoint_dir = Path(config["checkpoint_dir"])
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

    def train_single_model(
        self,
        model: nn.Module,
        train_loader: DataLoader,
        val_loader: DataLoader,
        epochs: int = 50,
        model_name: str = "model"
    ) -> Dict:
        """
        Train one model (MLP or NFN at specified width).

        Args:
            model: Model to train
            train_loader: Training dataloader
            val_loader: Validation dataloader
            epochs: Number of training epochs
            model_name: Name for checkpointing

        Returns:
            {
                'train_loss': final training loss,
                'val_loss': validation loss,
                'epoch_losses': List[float],
                'checkpoint_path': Path to saved model
            }
        """
        model = model.to(self.device)
        optimizer = torch.optim.Adam(
            model.parameters(),
            lr=self.config["lr"],
            weight_decay=self.config["weight_decay"]
        )
        criterion = nn.MSELoss()

        epoch_losses = []
        best_val_loss = float('inf')

        for epoch in range(epochs):
            # Training
            model.train()
            train_loss = 0.0
            for batch_idx, (data, _) in enumerate(train_loader):
                data = data.to(self.device)

                optimizer.zero_grad()
                output = model(data)

                # Self-supervised: reconstruct input (simple autoencoder objective)
                # For weight space, we use a dummy target based on mean
                target = data.mean(dim=1, keepdim=True).expand_as(output)
                loss = criterion(output, target)

                loss.backward()
                optimizer.step()

                train_loss += loss.item()

            train_loss /= len(train_loader)

            # Validation
            model.eval()
            val_loss = 0.0
            with torch.no_grad():
                for data, _ in val_loader:
                    data = data.to(self.device)
                    output = model(data)
                    target = data.mean(dim=1, keepdim=True).expand_as(output)
                    loss = criterion(output, target)
                    val_loss += loss.item()

            val_loss /= len(val_loader)
            epoch_losses.append({'train': train_loss, 'val': val_loss})

            if (epoch + 1) % 10 == 0:
                print(f"Epoch {epoch+1}/{epochs} - Train Loss: {train_loss:.4f}, Val Loss: {val_loss:.4f}")

            # Save best model
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                checkpoint_path = self.checkpoint_dir / f"{model_name}.pt"
                torch.save({
                    'model_state_dict': model.state_dict(),
                    'epoch': epoch,
                    'train_loss': train_loss,
                    'val_loss': val_loss
                }, checkpoint_path)

        return {
            'train_loss': train_loss,
            'val_loss': best_val_loss,
            'epoch_losses': epoch_losses,
            'checkpoint_path': str(checkpoint_path)
        }

    def check_loss_matching(
        self,
        mlp_loss: float,
        nfn_loss: float,
        tolerance: float = 0.01
    ) -> bool:
        """
        Validate training loss matching.

        Args:
            mlp_loss: MLP training loss
            nfn_loss: NFN training loss
            tolerance: Matching tolerance

        Returns:
            True if losses match within tolerance
        """
        relative_diff = abs(mlp_loss - nfn_loss) / mlp_loss
        return relative_diff < tolerance

    def train_all_widths(
        self,
        model_factory: callable,
        dataloaders: Dict[str, Dict[str, DataLoader]]
    ) -> Dict:
        """
        Train all width configurations.

        Args:
            model_factory: Function that creates model given (model_type, width)
            dataloaders: Dictionary of dataloaders for each model type

        Returns:
            {
                'results': List of training results per width,
                'loss_matching': Dict of matching status per width
            }
        """
        results = []
        loss_matching = {}

        widths = self.config["hidden_widths"]

        for width in widths:
            print(f"\n{'='*60}")
            print(f"Training width: {width}")
            print(f"{'='*60}")

            width_results = {}

            # Train MLP
            print(f"\nTraining MLP (width={width})...")
            mlp_model = model_factory('mlp', width)
            mlp_result = self.train_single_model(
                mlp_model,
                dataloaders['mlp']['train'],
                dataloaders['mlp']['val'],
                epochs=self.config["epochs"],
                model_name=f"mlp_w{width}"
            )
            width_results['mlp'] = mlp_result

            # Train NFN
            print(f"\nTraining NFN (width={width})...")
            nfn_model = model_factory('nfn', width)
            nfn_result = self.train_single_model(
                nfn_model,
                dataloaders['nfn']['train'],
                dataloaders['nfn']['val'],
                epochs=self.config["epochs"],
                model_name=f"nfn_w{width}"
            )
            width_results['nfn'] = nfn_result

            # Check loss matching
            mlp_loss = mlp_result['train_loss']
            nfn_loss = nfn_result['train_loss']
            matched = self.check_loss_matching(
                mlp_loss,
                nfn_loss,
                self.config["loss_match_tolerance"]
            )

            loss_matching[width] = {
                'matched': matched,
                'mlp_loss': mlp_loss,
                'nfn_loss': nfn_loss,
                'relative_diff': abs(mlp_loss - nfn_loss) / mlp_loss
            }

            print(f"\nLoss Matching (width={width}): {'PASS' if matched else 'FAIL'}")
            print(f"  MLP Loss: {mlp_loss:.4f}")
            print(f"  NFN Loss: {nfn_loss:.4f}")
            print(f"  Relative Diff: {loss_matching[width]['relative_diff']:.4f}")

            results.append({
                'width': width,
                'mlp': mlp_result,
                'nfn': nfn_result
            })

        # Save training results
        results_file = Path(self.config["results_dir"]) / "training_results.json"
        results_file.parent.mkdir(parents=True, exist_ok=True)
        with open(results_file, 'w') as f:
            json.dump({
                'results': results,
                'loss_matching': loss_matching
            }, f, indent=2)

        return {
            'results': results,
            'loss_matching': loss_matching
        }
