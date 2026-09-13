import numpy as np
import torch
from torch.utils.data import DataLoader
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
import logging

logger = logging.getLogger(__name__)


def extract_features(backbone, dataset, device: str, batch_size: int = 256):
    """
    Extract frozen backbone features for all samples in dataset.
    Returns: (features N×2048, bird_labels N, background_labels N)
    """
    backbone.eval()
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=False, num_workers=4, pin_memory=True)
    all_features, all_bird, all_bg = [], [], []

    with torch.no_grad():
        for batch in loader:
            images, bird_labels, bg_labels, _ = batch
            images = images.to(device)
            features = backbone(images)     # (B, 2048)
            all_features.append(features.cpu().numpy())
            all_bird.append(bird_labels.numpy() if hasattr(bird_labels, 'numpy') else np.array(bird_labels))
            all_bg.append(bg_labels.numpy() if hasattr(bg_labels, 'numpy') else np.array(bg_labels))

    return (
        np.concatenate(all_features, axis=0),
        np.concatenate(all_bird, axis=0),
        np.concatenate(all_bg, axis=0),
    )


def train_and_eval_probe(
    train_features: np.ndarray,
    train_labels: np.ndarray,
    test_features: np.ndarray,
    test_labels: np.ndarray,
    C: float = 1.0,
    max_iter: int = 1000,
    solver: str = "lbfgs",
) -> float:
    """Train logistic regression probe and return test accuracy."""
    scaler = StandardScaler()
    train_features = scaler.fit_transform(train_features)
    test_features = scaler.transform(test_features)

    probe = LogisticRegression(C=C, max_iter=max_iter, solver=solver, multi_class="auto")
    probe.fit(train_features, train_labels)
    acc = probe.score(test_features, test_labels)
    return float(acc)


def run_probes(checkpoint_path: str, waterbirds_root: str, device: str) -> dict:
    """
    Load backbone from checkpoint, extract features, run spurious and task probes.
    Returns: {spurious_probe_acc, task_probe_acc, ratio}
    """
    import wilds
    from src.models.simclr import SimCLRModel
    from src.augmentation.simclr_augment import get_eval_transform
    from src.data.waterbirds import WaterbirdsDataset

    cfg_device = torch.device(device if torch.cuda.is_available() else "cpu")

    # Load backbone from checkpoint
    model = SimCLRModel()
    ckpt = torch.load(checkpoint_path, map_location="cpu")
    model.get_backbone().load_state_dict(ckpt["backbone"])
    backbone = model.get_backbone().to(cfg_device)
    backbone.eval()

    eval_transform = get_eval_transform()

    # Load train and test splits
    train_dataset = WaterbirdsDataset(waterbirds_root, split="train", transform=eval_transform)
    test_dataset = WaterbirdsDataset(waterbirds_root, split="test", transform=eval_transform)

    logger.info("Extracting train features...")
    train_feats, train_bird, train_bg = extract_features(backbone, train_dataset, str(cfg_device))

    logger.info("Extracting test features...")
    test_feats, test_bird, test_bg = extract_features(backbone, test_dataset, str(cfg_device))

    # Spurious probe: predict background label
    logger.info("Training spurious probe...")
    spurious_acc = train_and_eval_probe(train_feats, train_bg, test_feats, test_bg)

    # Task probe: predict bird label
    logger.info("Training task probe...")
    task_acc = train_and_eval_probe(train_feats, train_bird, test_feats, test_bird)

    ratio = spurious_acc / task_acc if task_acc > 0 else float("inf")

    logger.info(f"Spurious probe acc: {spurious_acc:.4f}, Task probe acc: {task_acc:.4f}, Ratio: {ratio:.4f}")
    return {
        "spurious_probe_acc": spurious_acc,
        "task_probe_acc": task_acc,
        "ratio": ratio,
    }
