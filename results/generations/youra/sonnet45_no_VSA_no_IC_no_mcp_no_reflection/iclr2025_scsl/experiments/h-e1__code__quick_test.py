"""Quick test with reduced epochs for validation."""

from train import TrainConfig, run_single_experiment

# Quick test: CMNIST with 5 epochs only
config = TrainConfig(
    dataset='CMNIST',
    lr=0.001,
    max_epochs=20,  # Full PoC test
    weight_decay=1e-4,
    batch_size=128,
    seed=0
)

print("Running quick validation test (5 epochs)...")
result = run_single_experiment(config)
print("\nResult:", result)
print("\nQuick test complete. Full pipeline functional." if result['E_spurious'] is not None or result['E_core'] is not None else "\nWarning: No convergence in 5 epochs (expected for quick test)")
