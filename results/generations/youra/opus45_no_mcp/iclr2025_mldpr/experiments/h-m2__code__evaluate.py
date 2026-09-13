import torch


def measure_texture_bias(model, conflict_loader, device='cuda'):
    """Geirhos et al. texture-bias metric."""
    model.eval()
    texture_correct = 0
    shape_correct = 0
    total = 0

    with torch.no_grad():
        for images, shape_labels, texture_labels in conflict_loader:
            images = images.to(device)
            shape_labels = shape_labels.to(device)
            texture_labels = texture_labels.to(device)

            preds = model(images).argmax(dim=1)

            # Shape labels are CIFAR-10 classes (0-9)
            # Texture labels are DTD categories (0-46)
            # We compare prediction to CIFAR-10 range only
            shape_correct += (preds == shape_labels).sum().item()

            # Texture match: prediction matches texture's "mapped" class
            # Since DTD has 47 categories and CIFAR has 10, we mod 10
            texture_mapped = texture_labels % 10
            texture_correct += (preds == texture_mapped).sum().item()

            total += images.size(0)

    texture_bias_ratio = texture_correct / (texture_correct + shape_correct + 1e-8)

    return {
        "texture_bias_ratio": texture_bias_ratio,
        "texture_accuracy": texture_correct / total,
        "shape_accuracy": shape_correct / total,
        "neither": 1 - (texture_correct + shape_correct) / total,
        "total_samples": total,
    }


def evaluate_standard_accuracy(model, test_loader, device='cuda'):
    model.eval()
    correct = 0
    total = 0
    with torch.no_grad():
        for x, y in test_loader:
            x, y = x.to(device), y.to(device)
            out = model(x)
            correct += (out.argmax(1) == y).sum().item()
            total += y.size(0)
    return correct / total
