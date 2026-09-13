import torch
from torch.utils.data import DataLoader
from feature_extractor import FeatureExtractor
from probe import LinearProbe, train_probe, evaluate_probe

class FeatureProbeAnalyzer:
    def __init__(self, model_builder, checkpoint_dir: str,
                 crystallization_epoch: int, final_epoch: int,
                 hidden_dim: int = 2048, probe_lr: float = 0.01,
                 probe_iterations: int = 100, checkpoint_pattern: str = "waterbirds_epoch{epoch}.pt"):
        self.model_builder = model_builder
        self.checkpoint_dir = checkpoint_dir
        self.crystallization_epoch = crystallization_epoch
        self.final_epoch = final_epoch
        self.hidden_dim = hidden_dim
        self.probe_lr = probe_lr
        self.probe_iterations = probe_iterations
        self.checkpoint_pattern = checkpoint_pattern

        self.spurious_acc_history = []
        self.core_acc_history = []
        self.epochs_analyzed = []

    def analyze_checkpoint(self, epoch: int, val_loader: DataLoader,
                           test_loader: DataLoader, device: str) -> dict:
        model = self.model_builder()
        ckpt_path = f"{self.checkpoint_dir}/{self.checkpoint_pattern.format(epoch=epoch)}"
        state = torch.load(ckpt_path, map_location=device)
        if isinstance(state, dict) and 'model_state_dict' in state:
            model.load_state_dict(state['model_state_dict'])
        else:
            model.load_state_dict(state)
        model.to(device)
        model.eval()

        extractor = FeatureExtractor(model)
        val_feats, val_core, val_spurious = extractor.extract_dataset(model, val_loader, device)
        test_feats, test_core, test_spurious = extractor.extract_dataset(model, test_loader, device)
        extractor.remove()

        spurious_probe = LinearProbe(self.hidden_dim, 2)
        train_probe(spurious_probe, val_feats, val_spurious, self.probe_lr, self.probe_iterations, device)
        spurious_acc = evaluate_probe(spurious_probe, test_feats, test_spurious, device)

        core_probe = LinearProbe(self.hidden_dim, 2)
        train_probe(core_probe, val_feats, val_core, self.probe_lr, self.probe_iterations, device)
        core_acc = evaluate_probe(core_probe, test_feats, test_core, device)

        return {'epoch': epoch, 'spurious_acc': spurious_acc, 'core_acc': core_acc}

    def analyze_all(self, val_loader: DataLoader, test_loader: DataLoader, device: str) -> dict:
        for epoch in range(self.crystallization_epoch, self.final_epoch + 1):
            result = self.analyze_checkpoint(epoch, val_loader, test_loader, device)
            self.spurious_acc_history.append(result['spurious_acc'])
            self.core_acc_history.append(result['core_acc'])
            self.epochs_analyzed.append(epoch)
            print(f"Epoch {epoch}: spurious={result['spurious_acc']:.4f}, core={result['core_acc']:.4f}")
        return self.get_history()

    def get_history(self) -> dict:
        return {
            'spurious_acc_history': self.spurious_acc_history,
            'core_acc_history': self.core_acc_history,
            'epochs': self.epochs_analyzed
        }
