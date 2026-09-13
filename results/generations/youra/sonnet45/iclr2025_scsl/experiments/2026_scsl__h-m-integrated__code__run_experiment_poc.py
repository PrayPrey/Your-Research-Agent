"""Run complete proof-of-concept experiment with reduced scale.

This script:
1. Trains SimCLR for 20 epochs (instead of 100)
2. Trains LA-SSL for 20 epochs (instead of 100)
3. Extracts embeddings and validates mechanisms M1/M2/M3
4. Generates validation report with REAL data (not mock)
"""

import sys
import subprocess
from pathlib import Path

# Setup paths
current_dir = Path(__file__).parent.absolute()

def run_command(cmd, desc):
    """Run a command and handle errors."""
    print("\n" + "=" * 60)
    print(f"STEP: {desc}")
    print("=" * 60)
    print(f"Command: {cmd}\n")

    result = subprocess.run(cmd, shell=True, cwd=current_dir)

    if result.returncode != 0:
        print(f"\n❌ ERROR: {desc} failed with exit code {result.returncode}")
        sys.exit(result.returncode)

    print(f"\n✅ SUCCESS: {desc} completed")
    return result.returncode

def main():
    """Run complete POC experiment pipeline."""
    print("=" * 60)
    print("PROOF-OF-CONCEPT EXPERIMENT - h-m-integrated")
    print("=" * 60)
    print("\nThis experiment uses REDUCED SCALE for testing:")
    print("  - 20 epochs (instead of 100)")
    print("  - 1 seed (instead of 3)")
    print("  - 64 batch size (instead of 128)")
    print("\nEstimated time: ~2-4 hours on single GPU")
    print("=" * 60)

    # Replace config.py with POC version
    print("\nUsing POC configuration (config_poc.py → config.py)")
    config_poc = current_dir / 'config_poc.py'
    config_main = current_dir / 'config.py'
    config_backup = current_dir / 'config_original.py'

    # Backup original config
    if config_main.exists():
        import shutil
        shutil.copy(config_main, config_backup)
        print(f"  Backed up original config to {config_backup}")

    # Copy POC config to main
    import shutil
    shutil.copy(config_poc, config_main)
    print(f"  Using POC config\n")

    try:
        # Step 1: Train SimCLR baseline
        run_command(
            "python run_simclr.py",
            "Train SimCLR Baseline (20 epochs)"
        )

        # Step 2: Train LA-SSL
        run_command(
            "python run_lassl.py",
            "Train LA-SSL with Learning-Speed Sampling (20 epochs)"
        )

        # Step 3: Run validation with REAL embeddings
        run_command(
            "python run_validation.py",
            "Mechanism Validation (M1/M2/M3) with REAL Data"
        )

        print("\n" + "=" * 60)
        print("PROOF-OF-CONCEPT EXPERIMENT COMPLETE")
        print("=" * 60)
        print("\n✅ All steps completed successfully!")
        print("\nOutputs:")
        print(f"  - Validation report: ../04_validation.md")
        print(f"  - Metrics JSON: ../results/mechanism_metrics.json")
        print(f"  - SimCLR checkpoints: ./checkpoints/simclr/seed_0/")
        print(f"  - LA-SSL checkpoints: ./checkpoints/lassl/seed_0/")

    finally:
        # Restore original config
        if config_backup.exists():
            shutil.copy(config_backup, config_main)
            print(f"\n  Restored original config from {config_backup}")

if __name__ == '__main__':
    main()
