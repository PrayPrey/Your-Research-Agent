"""
Training logic for ERM and Group-DRO
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torch.optim.lr_scheduler import MultiStepLR
import os
import csv
from tqdm import tqdm


class Trainer:
    """
    Unified trainer for ERM and Group-DRO methods.
    """

    def __init__(self, model, train_loader, val_loader, config, method='erm', device='cuda'):
        """
        Args:
            model: PyTorch model
            train_loader: Training dataloader
            val_loader: Validation dataloader
            config: Configuration dict
            method: 'erm' or 'dro'
            device: 'cuda' or 'cpu'
        """
        self.model = model.to(device)
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.config = config
        self.method = method
        self.device = device

        # Optimizer
        self.optimizer = optim.SGD(
            model.parameters(),
            lr=config['lr'],
            momentum=config['momentum'],
            weight_decay=config['weight_decay']
        )

        # Learning rate scheduler
        self.scheduler = MultiStepLR(
            self.optimizer,
            milestones=config['lr_milestones'],
            gamma=config['lr_gamma']
        )

        # Loss function
        if method == 'erm':
            self.criterion = nn.CrossEntropyLoss()
        elif method == 'dro':
            from models.model import GroupDROLoss
            self.criterion = GroupDROLoss(
                num_groups=config['num_groups'],
                step_size=config['dro_step_size']
            )
        else:
            raise ValueError(f"Unknown method: {method}")

        # Early stopping
        self.patience = config['patience']
        self.best_worst_group_acc = 0.0
        self.patience_counter = 0
        self.best_model_path = None

        # Metrics history
        self.history = {
            'train_loss': [],
            'train_acc': [],
            'val_loss': [],
            'val_acc': [],
            'val_worst_group_acc': []
        }

    def train_epoch(self):
        """Train for one epoch"""
        self.model.train()
        total_loss = 0.0
        correct = 0
        total = 0

        for batch_idx, (images, labels, groups) in enumerate(self.train_loader):
            images = images.to(self.device)
            labels = labels.to(self.device)
            groups = groups.to(self.device)

            # Forward
            outputs = self.model(images)

            # Compute loss
            if self.method == 'erm':
                loss = self.criterion(outputs, labels)
            else:  # dro
                loss = self.criterion(outputs, labels, groups)

            # Backward
            self.optimizer.zero_grad()
            loss.backward()
            self.optimizer.step()

            # Metrics
            total_loss += loss.item()
            _, predicted = outputs.max(1)
            correct += predicted.eq(labels).sum().item()
            total += labels.size(0)

            if batch_idx % self.config['log_interval'] == 0:
                print(f"  Batch {batch_idx}/{len(self.train_loader)}, Loss: {loss.item():.4f}")

        avg_loss = total_loss / len(self.train_loader)
        accuracy = 100.0 * correct / total

        return avg_loss, accuracy

    def validate(self):
        """Validate on val set"""
        self.model.eval()
        total_loss = 0.0
        correct = 0
        total = 0

        # Group-wise accuracy
        group_correct = torch.zeros(self.config['num_groups'])
        group_total = torch.zeros(self.config['num_groups'])

        with torch.no_grad():
            for images, labels, groups in self.val_loader:
                images = images.to(self.device)
                labels = labels.to(self.device)
                groups_cpu = groups  # Keep on CPU for indexing

                outputs = self.model(images)
                loss = nn.CrossEntropyLoss()(outputs, labels)

                total_loss += loss.item()
                _, predicted = outputs.max(1)
                correct += predicted.eq(labels).sum().item()
                total += labels.size(0)

                # Group-wise
                predicted_cpu = predicted.cpu()
                labels_cpu = labels.cpu()
                for g in range(self.config['num_groups']):
                    mask = (groups_cpu == g)
                    if mask.sum() > 0:
                        group_correct[g] += predicted_cpu[mask].eq(labels_cpu[mask]).sum().item()
                        group_total[g] += mask.sum().item()

        avg_loss = total_loss / len(self.val_loader)
        accuracy = 100.0 * correct / total

        # Worst-group accuracy
        group_accs = []
        for g in range(self.config['num_groups']):
            if group_total[g] > 0:
                group_accs.append(100.0 * group_correct[g] / group_total[g])
            else:
                group_accs.append(0.0)

        worst_group_acc = min(group_accs)

        return avg_loss, accuracy, worst_group_acc, group_accs

    def train(self, epochs, checkpoint_dir):
        """
        Train for multiple epochs with early stopping.

        Args:
            epochs: Number of epochs
            checkpoint_dir: Directory to save checkpoints

        Returns:
            best_model_path: Path to best model checkpoint
        """
        os.makedirs(checkpoint_dir, exist_ok=True)

        for epoch in range(epochs):
            print(f"\nEpoch {epoch+1}/{epochs}")

            # Train
            train_loss, train_acc = self.train_epoch()
            print(f"Train Loss: {train_loss:.4f}, Acc: {train_acc:.2f}%")

            # Validate
            val_loss, val_acc, worst_group_acc, group_accs = self.validate()
            print(f"Val Loss: {val_loss:.4f}, Acc: {val_acc:.2f}%, Worst-Group: {worst_group_acc:.2f}%")
            print(f"Group Accs: {[f'{acc:.2f}' for acc in group_accs]}")

            # Update history
            self.history['train_loss'].append(train_loss)
            self.history['train_acc'].append(train_acc)
            self.history['val_loss'].append(val_loss)
            self.history['val_acc'].append(val_acc)
            self.history['val_worst_group_acc'].append(worst_group_acc)

            # Learning rate schedule
            self.scheduler.step()

            # Early stopping based on worst-group accuracy
            if worst_group_acc > self.best_worst_group_acc:
                self.best_worst_group_acc = worst_group_acc
                self.patience_counter = 0

                # Save checkpoint
                self.best_model_path = os.path.join(checkpoint_dir, f'best_{self.method}.pth')
                torch.save(self.model.state_dict(), self.best_model_path)
                print(f"✓ Saved best model: {self.best_model_path}")
            else:
                self.patience_counter += 1
                print(f"Early stopping counter: {self.patience_counter}/{self.patience}")

                if self.patience_counter >= self.patience:
                    print(f"Early stopping triggered at epoch {epoch+1}")
                    break

        # Load best model
        if self.best_model_path and os.path.exists(self.best_model_path):
            self.model.load_state_dict(torch.load(self.best_model_path))
            print(f"\n✓ Loaded best model from {self.best_model_path}")

        return self.best_model_path

    def save_history(self, path):
        """Save training history to CSV"""
        with open(path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['epoch', 'train_loss', 'train_acc', 'val_loss', 'val_acc', 'val_worst_group_acc'])
            for i in range(len(self.history['train_loss'])):
                writer.writerow([
                    i+1,
                    self.history['train_loss'][i],
                    self.history['train_acc'][i],
                    self.history['val_loss'][i],
                    self.history['val_acc'][i],
                    self.history['val_worst_group_acc'][i]
                ])
