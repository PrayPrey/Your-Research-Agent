import json
import sys
from pathlib import Path

import torch

from config import Config
from data import get_dataloaders, get_weight_shapes, MNISTINRDataset
from models import FlattenedMLP, DWSModel, NFTModel
from metrics import attention_entropy, layer_activation_variance, verify_mechanism
from train import train_model, evaluate
from visualize import (
    plot_accuracy_comparison,
    plot_attention_heatmap,
    plot_layer_activation_profile,
    plot_tsne_representations,
)


def main():
    cfg = Config()

    torch.manual_seed(cfg.seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(cfg.seed)

    print(f"Device: {cfg.device}")
    print(f"Loading data from {cfg.data_dir}...")

    train_loader, test_loader = get_dataloaders(cfg)
    weight_shapes = get_weight_shapes(cfg)
    print(f"Weight shapes: {weight_shapes}")
    print(f"Train samples: {len(train_loader.dataset)}, Test samples: {len(test_loader.dataset)}")

    total_input_dim = sum(in_c * out_c for in_c, out_c in weight_shapes)

    results = {}
    models = {}

    # Train FlattenedMLP
    print("\n=== Training FlattenedMLP ===")
    mlp = FlattenedMLP(total_input_dim, cfg.mlp_hidden, cfg.num_classes, cfg.dropout)
    mlp = train_model(mlp, train_loader, cfg)
    results["MLP"] = evaluate(mlp, test_loader, cfg)
    models["MLP"] = mlp
    print(f"MLP Accuracy: {results['MLP']['accuracy']*100:.2f}%")

    # Train DWSModel
    print("\n=== Training DWSModel ===")
    dws = DWSModel(weight_shapes, cfg.dws_hidden, cfg.num_classes)
    dws = train_model(dws, train_loader, cfg)
    results["DWS"] = evaluate(dws, test_loader, cfg)
    models["DWS"] = dws
    print(f"DWS Accuracy: {results['DWS']['accuracy']*100:.2f}%")

    # Train NFTModel
    print("\n=== Training NFTModel ===")
    nft = NFTModel(weight_shapes, cfg.d_model, cfg.nhead, cfg.num_layers, cfg.num_classes)
    nft = train_model(nft, train_loader, cfg)
    results["NFT"] = evaluate(nft, test_loader, cfg)
    models["NFT"] = nft
    print(f"NFT Accuracy: {results['NFT']['accuracy']*100:.2f}%")

    # Mechanism verification
    print("\n=== Mechanism Verification ===")
    sample_batch = next(iter(test_loader))
    sample_weights = [w.to(cfg.device) for w in sample_batch[0]]

    dws_feats = dws.get_layer_activations(sample_weights)
    dws_locality_score = layer_activation_variance(dws_feats)
    dws_verified = verify_mechanism(dws, sample_weights, "dws")
    results["DWS"]["locality_score"] = dws_locality_score
    results["DWS"]["mechanism_verified"] = dws_verified
    print(f"DWS locality score: {dws_locality_score:.4f} (< 1.0: {dws_verified})")

    nft_attn = nft.get_attention_weights(sample_weights)
    nft_entropy = attention_entropy(nft_attn)
    nft_verified = verify_mechanism(nft, sample_weights, "nft")
    results["NFT"]["attention_entropy"] = nft_entropy
    results["NFT"]["mechanism_verified"] = nft_verified
    print(f"NFT attention entropy: {nft_entropy:.4f} (> 2.0: {nft_verified})")

    # Visualizations
    print("\n=== Generating Visualizations ===")
    Path(cfg.fig_dir).mkdir(parents=True, exist_ok=True)

    plot_accuracy_comparison(results, f"{cfg.fig_dir}/accuracy_comparison.png")
    print("Saved accuracy comparison")

    plot_attention_heatmap(nft_attn, f"{cfg.fig_dir}/attention_heatmap.png")
    print("Saved attention heatmap")

    plot_layer_activation_profile(dws_feats, f"{cfg.fig_dir}/layer_activation_profile.png")
    print("Saved layer activation profile")

    # Collect representations for t-SNE
    dws_reprs_list = []
    nft_reprs_list = []
    labels_list = []

    dws.eval()
    nft.eval()
    with torch.no_grad():
        for weight_list, labels in test_loader:
            weight_list = [w.to(cfg.device) for w in weight_list]

            dws_agg, _ = dws.dws_layer(weight_list)
            dws_reprs_list.append(dws_agg.cpu())

            nft_tokens = nft.tokenizer(weight_list)
            nft_enc = nft.transformer_encoder(nft_tokens)
            nft_pooled = nft_enc.mean(dim=1)
            nft_reprs_list.append(nft_pooled.cpu())

            labels_list.append(labels)

    dws_reprs = torch.cat(dws_reprs_list, dim=0)
    nft_reprs = torch.cat(nft_reprs_list, dim=0)
    all_labels = torch.cat(labels_list, dim=0)

    plot_tsne_representations(dws_reprs, nft_reprs, all_labels, f"{cfg.fig_dir}/tsne_representations.png")
    print("Saved t-SNE visualization")

    # Save results
    Path(cfg.results_path).parent.mkdir(parents=True, exist_ok=True)
    with open(cfg.results_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {cfg.results_path}")

    # Summary
    print("\n" + "="*50)
    print("EXPERIMENT SUMMARY")
    print("="*50)
    print(f"MLP Accuracy: {results['MLP']['accuracy']*100:.2f}%")
    print(f"DWS Accuracy: {results['DWS']['accuracy']*100:.2f}%")
    print(f"NFT Accuracy: {results['NFT']['accuracy']*100:.2f}%")
    print(f"DWS Locality Score: {results['DWS']['locality_score']:.4f} (verified: {results['DWS']['mechanism_verified']})")
    print(f"NFT Attention Entropy: {results['NFT']['attention_entropy']:.4f} (verified: {results['NFT']['mechanism_verified']})")

    all_above_90 = all(r["accuracy"] >= 0.9 for r in results.values())
    print(f"\nAll models >90% accuracy: {all_above_90}")
    print(f"Mechanism verification passed: DWS={results['DWS']['mechanism_verified']}, NFT={results['NFT']['mechanism_verified']}")

    gate_passed = all_above_90 and results['DWS']['mechanism_verified'] and results['NFT']['mechanism_verified']
    print(f"\nGATE RESULT: {'PASS' if gate_passed else 'PARTIAL/FAIL'}")

    return results


if __name__ == "__main__":
    results = main()
