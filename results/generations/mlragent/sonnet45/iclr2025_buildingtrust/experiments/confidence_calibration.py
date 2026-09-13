"""
Confidence Calibration Module
Trains a neural network to map disagreement metrics to calibrated confidence scores
"""
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from typing import List, Dict, Tuple
from sklearn.metrics import roc_auc_score, average_precision_score


class CalibrationNetwork(nn.Module):
    """Neural network for confidence calibration"""

    def __init__(self, input_dim: int = 387, hidden_dim: int = 128):
        """
        input_dim = 3 (disagreement metrics) + 384 (embedding dimension)
        """
        super(CalibrationNetwork, self).__init__()

        self.network = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_dim, 64),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        return self.network(x)


class ConfidenceCalibrator:
    """Calibrator for mapping disagreement to confidence scores"""

    def __init__(self, config: Dict, device: str = None):
        self.config = config
        self.device = device if device else ('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"Using device: {self.device}")

        self.model = None
        self.scaler_mean = None
        self.scaler_std = None

    def prepare_features(self, analysis_results: Dict) -> np.ndarray:
        """
        Prepare feature vector from analysis results
        Features: [semantic_dispersion, cluster_diversity, length_variance, centroid_embedding]
        """
        features = []

        # Disagreement metrics
        features.append(analysis_results.get('semantic_dispersion', 0.0))
        features.append(analysis_results.get('cluster_diversity', 0.0))
        features.append(analysis_results.get('length_variance', 0.0))

        # Centroid embedding
        centroid = analysis_results.get('centroid')
        if centroid is not None:
            features.extend(centroid.tolist())
        else:
            # Pad with zeros if no centroid
            features.extend([0.0] * 384)

        return np.array(features, dtype=np.float32)

    def normalize_features(self, features: np.ndarray, fit: bool = False) -> np.ndarray:
        """Normalize features using z-score normalization"""
        if fit:
            self.scaler_mean = np.mean(features, axis=0)
            self.scaler_std = np.std(features, axis=0) + 1e-8

        return (features - self.scaler_mean) / self.scaler_std

    def train(self, train_data: List[Tuple[Dict, float]], val_data: List[Tuple[Dict, float]]):
        """
        Train calibration network
        train_data: List of (analysis_results, correctness_label) tuples
        """
        print("\nTraining calibration network...")

        # Prepare training features and labels
        X_train = np.array([self.prepare_features(analysis) for analysis, _ in train_data])
        y_train = np.array([label for _, label in train_data], dtype=np.float32)

        X_val = np.array([self.prepare_features(analysis) for analysis, _ in val_data])
        y_val = np.array([label for _, label in val_data], dtype=np.float32)

        # Normalize features
        X_train = self.normalize_features(X_train, fit=True)
        X_val = self.normalize_features(X_val, fit=False)

        # Convert to tensors
        X_train = torch.FloatTensor(X_train).to(self.device)
        y_train = torch.FloatTensor(y_train).unsqueeze(1).to(self.device)
        X_val = torch.FloatTensor(X_val).to(self.device)
        y_val = torch.FloatTensor(y_val).unsqueeze(1).to(self.device)

        # Initialize model
        input_dim = X_train.shape[1]
        self.model = CalibrationNetwork(input_dim=input_dim).to(self.device)

        # Training settings
        optimizer = optim.Adam(self.model.parameters(),
                               lr=self.config.get('learning_rate', 0.001))
        criterion = nn.BCELoss()

        n_epochs = self.config.get('n_epochs', 20)
        batch_size = self.config.get('batch_size', 16)
        lambda_sharpness = self.config.get('lambda_sharpness', 0.1)

        best_val_loss = float('inf')
        best_model_state = None
        patience = 5
        patience_counter = 0

        for epoch in range(n_epochs):
            self.model.train()
            train_losses = []

            # Mini-batch training
            n_batches = len(X_train) // batch_size + (1 if len(X_train) % batch_size != 0 else 0)

            for batch_idx in range(n_batches):
                start_idx = batch_idx * batch_size
                end_idx = min((batch_idx + 1) * batch_size, len(X_train))

                X_batch = X_train[start_idx:end_idx]
                y_batch = y_train[start_idx:end_idx]

                optimizer.zero_grad()

                # Forward pass
                predictions = self.model(X_batch)

                # Calibration loss (BCE)
                cal_loss = criterion(predictions, y_batch)

                # Sharpness loss (entropy regularization)
                sharpness_loss = -torch.mean(
                    predictions * torch.log(predictions + 1e-8) +
                    (1 - predictions) * torch.log(1 - predictions + 1e-8)
                )

                # Combined loss
                loss = cal_loss + lambda_sharpness * sharpness_loss

                loss.backward()
                optimizer.step()

                train_losses.append(loss.item())

            # Validation
            self.model.eval()
            with torch.no_grad():
                val_predictions = self.model(X_val)
                val_loss = criterion(val_predictions, y_val)

            avg_train_loss = np.mean(train_losses)

            if (epoch + 1) % 5 == 0:
                print(f"Epoch {epoch + 1}/{n_epochs} - Train Loss: {avg_train_loss:.4f}, Val Loss: {val_loss:.4f}")

            # Early stopping
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                best_model_state = self.model.state_dict().copy()
                patience_counter = 0
            else:
                patience_counter += 1
                if patience_counter >= patience:
                    print(f"Early stopping at epoch {epoch + 1}")
                    break

        # Restore best model
        if best_model_state is not None:
            self.model.load_state_dict(best_model_state)

        print(f"Training completed. Best validation loss: {best_val_loss:.4f}")

    def predict(self, analysis_results: Dict) -> float:
        """Predict calibrated confidence for a single sample"""
        if self.model is None:
            raise ValueError("Model not trained yet")

        self.model.eval()
        with torch.no_grad():
            features = self.prepare_features(analysis_results)
            features = self.normalize_features(features.reshape(1, -1), fit=False)
            features = torch.FloatTensor(features).to(self.device)

            confidence = self.model(features).item()

        return confidence

    def batch_predict(self, analysis_results_list: List[Dict]) -> np.ndarray:
        """Predict calibrated confidence for multiple samples"""
        if self.model is None:
            raise ValueError("Model not trained yet")

        self.model.eval()
        with torch.no_grad():
            features = np.array([self.prepare_features(ar) for ar in analysis_results_list])
            features = self.normalize_features(features, fit=False)
            features = torch.FloatTensor(features).to(self.device)

            confidences = self.model(features).cpu().numpy().flatten()

        return confidences

    def save_model(self, filepath: str):
        """Save trained model"""
        if self.model is None:
            raise ValueError("No model to save")

        torch.save({
            'model_state_dict': self.model.state_dict(),
            'scaler_mean': self.scaler_mean,
            'scaler_std': self.scaler_std,
            'config': self.config,
        }, filepath)
        print(f"Model saved to {filepath}")

    def load_model(self, filepath: str):
        """Load trained model"""
        checkpoint = torch.load(filepath, map_location=self.device)

        self.scaler_mean = checkpoint['scaler_mean']
        self.scaler_std = checkpoint['scaler_std']

        input_dim = len(self.scaler_mean)
        self.model = CalibrationNetwork(input_dim=input_dim).to(self.device)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.model.eval()

        print(f"Model loaded from {filepath}")
