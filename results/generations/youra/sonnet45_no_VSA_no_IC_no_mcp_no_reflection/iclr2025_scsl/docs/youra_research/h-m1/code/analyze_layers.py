"""Main experiment script for h-m1 layer-neuron consistency analysis."""
import torch
import torchvision.models as models
import numpy as np
import yaml
from pathlib import Path

from data_loader import get_dataloader, get_spurious_labels
from layer_analyzer import LayerNeuronAnalyzer
from visualize import plot_layer_means, plot_heatmap, plot_cdf
from report_generator import generate_validation_report


def train_baseline_model(config):
    """Train baseline ResNet-18 model on CMNIST (replicating h-e1)."""
    print("Training baseline model...")

    device = config['reproducibility']['device']
    model = models.resnet18(pretrained=False, num_classes=config['model']['num_classes'])
    model = model.to(device)

    train_loader = get_dataloader(config['data'], train=True)
    optimizer = torch.optim.SGD(
        model.parameters(),
        lr=config['training']['lr'],
        momentum=config['training']['momentum'],
        weight_decay=config['training']['weight_decay']
    )
    criterion = torch.nn.CrossEntropyLoss()

    model.train()
    for epoch in range(config['training']['epochs']):
        total_loss = 0
        correct = 0
        total = 0

        for batch_x, batch_y, _ in train_loader:
            batch_x, batch_y = batch_x.to(device), batch_y.to(device)

            optimizer.zero_grad()
            outputs = model(batch_x)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()

            total_loss += loss.item()
            _, predicted = outputs.max(1)
            total += batch_y.size(0)
            correct += predicted.eq(batch_y).sum().item()

        acc = 100. * correct / total
        print(f"Epoch {epoch+1}/{config['training']['epochs']}: "
              f"Loss={total_loss/len(train_loader):.4f}, Acc={acc:.2f}%")

    # Save checkpoint
    checkpoint_dir = Path(config['output']['checkpoint_folder'])
    checkpoint_dir.mkdir(exist_ok=True)
    checkpoint_path = checkpoint_dir / 'baseline_model.pt'

    torch.save({
        'model_state_dict': model.state_dict(),
        'epoch': config['training']['epochs']
    }, checkpoint_path)

    print(f"Model saved to {checkpoint_path}")
    return model


def main():
    # Load configuration
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)

    # Set random seed
    torch.manual_seed(config['reproducibility']['seed'])
    np.random.seed(config['reproducibility']['seed'])

    device = config['reproducibility']['device']

    # Train or load model
    checkpoint_dir = Path(config['output']['checkpoint_folder'])
    checkpoint_path = checkpoint_dir / 'baseline_model.pt'

    if checkpoint_path.exists():
        print(f"Loading checkpoint from {checkpoint_path}")
        model = models.resnet18(pretrained=False, num_classes=config['model']['num_classes'])
        checkpoint = torch.load(checkpoint_path)
        model.load_state_dict(checkpoint['model_state_dict'])
        model = model.to(device)
    else:
        model = train_baseline_model(config)

    model.eval()

    # Create analyzer
    analyzer = LayerNeuronAnalyzer(model, config['model']['layer_names'])

    # Load train data (where spurious correlation exists)
    train_loader = get_dataloader(config['data'], train=True)
    spurious_labels = get_spurious_labels(train_loader.dataset)

    print("Computing layer correlations...")
    layer_rho_j = analyzer.compute_layer_correlations(train_loader, spurious_labels, device)

    print("Running statistical test...")
    t_stat, p_value, layer_means = analyzer.test_layer_consistency(
        layer_rho_j,
        config['analysis']['early_layers'],
        config['analysis']['late_layers']
    )

    # Generate visualizations
    print("Generating visualizations...")
    figures_folder = Path(config['output']['figures_folder'])
    figures_folder.mkdir(exist_ok=True)

    plot_layer_means(
        layer_means,
        layer_rho_j,
        figures_folder / config['output']['bar_chart']
    )
    plot_heatmap(
        layer_rho_j,
        figures_folder / config['output']['heatmap'],
        config['analysis']['max_neurons_heatmap']
    )
    plot_cdf(
        layer_rho_j,
        figures_folder / config['output']['cdf_plot']
    )

    # Generate report
    print("Generating validation report...")
    generate_validation_report(
        t_stat,
        p_value,
        layer_means,
        layer_rho_j,
        Path(config['output']['validation_report']),
        config['analysis']['alpha']
    )

    # Print summary
    gate_pass = p_value < config['analysis']['alpha']
    print(f"\n{'='*60}")
    print(f"Gate Verdict: {'✅ PASS' if gate_pass else '❌ FAIL'}")
    print(f"p-value: {p_value:.4f}, t-statistic: {t_stat:.2f}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
