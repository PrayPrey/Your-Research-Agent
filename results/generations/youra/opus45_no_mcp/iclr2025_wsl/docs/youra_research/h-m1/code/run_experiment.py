import os
import json
import torch
from config import Config
from data import download_model_zoo, load_model_zoo, make_dataloaders
from models import FlattenMLPEncoder, LayerWiseEncoder, AccuracyPredictor, FullModel, flatten_weights
from train import set_seed, train_model
from evaluate import predict, compute_pearson, compare_methods, plot_gate_metrics, plot_scatter, plot_per_seed, plot_loss_curves

def get_input_dim_and_num_layers(sample):
    weights = sample['weights']
    flat = flatten_weights(weights)
    return flat.numel(), len(weights.keys())

def run_seed(method, seed, train_loader, val_loader, test_loader, cfg, input_dim, num_layers):
    set_seed(seed)
    device = cfg.device if torch.cuda.is_available() else "cpu"

    if method == "flatten":
        encoder = FlattenMLPEncoder(input_dim, cfg.hidden_dim, cfg.embed_dim)
    else:
        encoder = LayerWiseEncoder(num_layers, cfg.stats_per_layer, cfg.hidden_dim, cfg.embed_dim)

    predictor = AccuracyPredictor(cfg.embed_dim, cfg.predictor_hidden)
    model = FullModel(encoder, predictor, method).to(device)

    model, history = train_model(model, train_loader, val_loader, cfg.lr, cfg.weight_decay,
                                  cfg.max_epochs, cfg.early_stop_patience, device, method, input_dim)

    preds, targets = predict(model, test_loader, device, method, input_dim)
    metrics = compute_pearson(preds, targets)

    return {'pearson_r': metrics['pearson_r'], 'history': history, 'preds': preds, 'targets': targets}

def main():
    cfg = Config()
    os.makedirs(cfg.output_dir, exist_ok=True)
    os.makedirs(cfg.figures_dir, exist_ok=True)

    print("Downloading dataset...")
    download_model_zoo()

    print("Loading dataset...")
    train, val, test = load_model_zoo(cfg.data_path)
    train_loader, val_loader, test_loader = make_dataloaders(train, val, test, cfg.batch_size)

    input_dim, num_layers = get_input_dim_and_num_layers(train[0])
    print(f"Input dim: {input_dim}, Num layers: {num_layers}")

    flatten_results = []
    layerwise_results = []

    for method in ['flatten', 'layerwise']:
        print(f"\n=== Method: {method} ===")
        for seed in cfg.seeds:
            print(f"  Seed {seed}...")
            result = run_seed(method, seed, train_loader, val_loader, test_loader, cfg, input_dim, num_layers)
            r = result['pearson_r']
            print(f"    Pearson r: {r:.4f}")

            if method == 'flatten':
                flatten_results.append(r)
            else:
                layerwise_results.append(r)

            plot_loss_curves(result['history'], f"{method}_seed{seed}",
                           os.path.join(cfg.figures_dir, f"loss_{method}_seed{seed}.png"))

            if seed == 0:
                plot_scatter(result['preds'], result['targets'], method,
                           os.path.join(cfg.figures_dir, f"scatter_{method}.png"))

    comparison = compare_methods(flatten_results, layerwise_results)

    plot_gate_metrics(flatten_results, layerwise_results, os.path.join(cfg.figures_dir, "gate_metrics.png"))
    plot_per_seed(flatten_results, layerwise_results, os.path.join(cfg.figures_dir, "per_seed.png"))

    gate_pass = comparison['delta_r'] > 0.1 and comparison['p_value'] < 0.05
    all_seeds_improve = all(l > f for l, f in zip(layerwise_results, flatten_results))

    results = {
        'flatten_results': flatten_results,
        'layerwise_results': layerwise_results,
        'flatten_mean': float(sum(flatten_results) / len(flatten_results)),
        'layerwise_mean': float(sum(layerwise_results) / len(layerwise_results)),
        'delta_r': float(comparison['delta_r']),
        't_stat': float(comparison['t_stat']),
        'p_value': float(comparison['p_value']),
        'gate_pass': gate_pass,
        'all_seeds_improve': all_seeds_improve,
        'gate_type': 'MUST_WORK',
        'gate_result': 'PASS' if gate_pass else 'FAIL'
    }

    with open(os.path.join(cfg.output_dir, "results.json"), 'w') as f:
        json.dump(results, f, indent=2)

    print("\n=== RESULTS ===")
    print(f"Flatten+MLP mean r: {results['flatten_mean']:.4f}")
    print(f"Layer-wise mean r: {results['layerwise_mean']:.4f}")
    print(f"Delta r: {results['delta_r']:.4f}")
    print(f"p-value: {results['p_value']:.4f}")
    print(f"All seeds improve: {results['all_seeds_improve']}")
    print(f"Gate: {results['gate_result']}")

    return results

if __name__ == "__main__":
    main()
