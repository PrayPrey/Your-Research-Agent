#!/usr/bin/env python3
"""H-M2: Texture Bias Measurement - Full Pipeline Orchestration"""

import os
import sys
import json
import torch

import config
from data import get_cifar10_loaders, load_dtd_images, build_stylized_cifar10, get_conflict_loader
from models import build_vgg11_cifar, build_resnet18_cifar
from train import train_model, load_checkpoint
from evaluate import measure_texture_bias, evaluate_standard_accuracy
from gate import evaluate_gate, write_gate_report
from visualize import plot_gate_comparison, plot_training_curves, plot_confusion_shape_texture


def main():
    print("=" * 60)
    print("H-M2: Texture Bias Measurement Experiment")
    print("=" * 60)

    # Setup
    config.ensure_dirs()
    config.check_dtd_present()
    torch.manual_seed(config.SEED)
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Device: {device}")

    # Data
    print("\n[1/7] Loading CIFAR-10...")
    train_loader, test_loader = get_cifar10_loaders(config.BATCH_SIZE)
    print(f"Train: {len(train_loader.dataset)}, Test: {len(test_loader.dataset)}")

    print("\n[2/7] Loading DTD textures...")
    dtd_images_with_labels, num_categories = load_dtd_images(config.DTD_DIR)
    print(f"Loaded {len(dtd_images_with_labels)} DTD images from {num_categories} categories")

    print("\n[3/7] Generating Stylized-CIFAR-10...")
    cifar_test = test_loader.dataset
    stylized = build_stylized_cifar10(cifar_test, dtd_images_with_labels, config.SEED)
    conflict_loader = get_conflict_loader(stylized, config.BATCH_SIZE)
    print(f"Generated {len(stylized)} conflict stimuli")

    # Models
    print("\n[4/7] Building models...")
    vgg = build_vgg11_cifar().to(device)
    resnet = build_resnet18_cifar().to(device)
    print(f"VGG-11 params: {sum(p.numel() for p in vgg.parameters()):,}")
    print(f"ResNet-18 params: {sum(p.numel() for p in resnet.parameters()):,}")

    # Training
    print("\n[5/7] Training VGG-11...")
    vgg_path = os.path.join(config.CHECKPOINT_DIR, "vgg11.pt")
    if os.path.exists(vgg_path):
        print(f"Loading existing checkpoint: {vgg_path}")
        vgg = load_checkpoint(vgg, vgg_path)
        vgg_history = {"train_acc_curve": [], "test_acc_curve": [], "final_test_acc": evaluate_standard_accuracy(vgg, test_loader, device)}
    else:
        vgg_history = train_model(vgg, train_loader, test_loader, config.EPOCHS, vgg_path, device)

    print("\n[6/7] Training ResNet-18...")
    resnet_path = os.path.join(config.CHECKPOINT_DIR, "resnet18.pt")
    if os.path.exists(resnet_path):
        print(f"Loading existing checkpoint: {resnet_path}")
        resnet = load_checkpoint(resnet, resnet_path)
        resnet_history = {"train_acc_curve": [], "test_acc_curve": [], "final_test_acc": evaluate_standard_accuracy(resnet, test_loader, device)}
    else:
        resnet_history = train_model(resnet, train_loader, test_loader, config.EPOCHS, resnet_path, device)

    # Evaluation
    print("\n[7/7] Measuring texture bias...")
    vgg_bias = measure_texture_bias(vgg, conflict_loader, device)
    resnet_bias = measure_texture_bias(resnet, conflict_loader, device)

    print(f"\nVGG-11 texture bias: {vgg_bias['texture_bias_ratio']:.4f}")
    print(f"  Shape acc: {vgg_bias['shape_accuracy']:.4f}, Texture acc: {vgg_bias['texture_accuracy']:.4f}")
    print(f"ResNet-18 texture bias: {resnet_bias['texture_bias_ratio']:.4f}")
    print(f"  Shape acc: {resnet_bias['shape_accuracy']:.4f}, Texture acc: {resnet_bias['texture_accuracy']:.4f}")

    # Gate
    gate_result = evaluate_gate(resnet_bias, vgg_bias)
    print(f"\n{'='*60}")
    print(f"GATE RESULT: {'PASS' if gate_result['pass_gate'] else 'FAIL'}")
    print(f"  Diff (ResNet - VGG): {gate_result['diff']:.4f}")
    print(f"  Threshold: {gate_result['threshold']}")
    print(f"{'='*60}")

    # Save results
    gate_path = os.path.join(config.RESULTS_DIR, "gate.json")
    write_gate_report(gate_result, gate_path)

    full_results = {
        "gate": gate_result,
        "vgg_bias": vgg_bias,
        "resnet_bias": resnet_bias,
        "vgg_final_acc": vgg_history['final_test_acc'],
        "resnet_final_acc": resnet_history['final_test_acc'],
    }
    with open(os.path.join(config.RESULTS_DIR, "experiment_results.json"), 'w') as f:
        json.dump(full_results, f, indent=2)

    # Figures
    print("\nGenerating figures...")
    plot_gate_comparison(gate_result, os.path.join(config.FIGURES_DIR, "gate_comparison.png"))
    plot_confusion_shape_texture(resnet_bias, vgg_bias, os.path.join(config.FIGURES_DIR, "shape_texture_accuracy.png"))
    if vgg_history['test_acc_curve'] and resnet_history['test_acc_curve']:
        plot_training_curves(resnet_history, vgg_history, os.path.join(config.FIGURES_DIR, "training_curves.png"))

    print("\nExperiment complete!")
    return gate_result['pass_gate']


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
