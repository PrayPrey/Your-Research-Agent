"""Dry run configuration: minimal training to verify code works"""

class DryRunConfig:
    # Model
    d_z = 256
    d_arch = 64
    tau = 0.07
    
    # Training (minimal)
    epochs = 1
    batch_size = 8
    lr = 1e-4
    
    # Data (subset)
    data_subset = 10  # Use only 10 samples for dry run
    
    # Ablation variants
    variants = ["full_cape"]  # Test only full CAPE for dry run
    
    # Output
    output_dir = "results_dry_run"
    seed = 42
    
    # Reality check
    dry_run = True
