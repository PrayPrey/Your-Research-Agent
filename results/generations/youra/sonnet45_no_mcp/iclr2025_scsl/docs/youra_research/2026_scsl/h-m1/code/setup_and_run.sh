#!/bin/bash
# Setup and run h-m1 experiment with real Waterbirds dataset
# This script fixes the mock data issue by downloading and using the actual dataset

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Set up completion marker trap
LOG="experiment.log"
trap 'echo "EXPERIMENT COMPLETE (exit=$?, ts=$(date -Iseconds))" >> "$LOG"' EXIT

echo "=== H-M1 Experiment Setup and Execution ===" | tee -a "$LOG"
echo "Date: $(date)" | tee -a "$LOG"
echo "Working directory: $(pwd)" | tee -a "$LOG"

# Select GPU with most free memory
echo "Checking GPU availability..." | tee -a "$LOG"
if command -v nvidia-smi &> /dev/null; then
    # Get GPU with most free memory
    GPU_ID=$(nvidia-smi --query-gpu=index,memory.free --format=csv,noheader,nounits | sort -k2 -nr | head -1 | awk '{print $1}')
    export CUDA_VISIBLE_DEVICES=$GPU_ID
    echo "Using GPU $GPU_ID" | tee -a "$LOG"
else
    echo "No GPU available, using CPU" | tee -a "$LOG"
    export CUDA_VISIBLE_DEVICES=""
fi

# Install dependencies
echo "Installing dependencies..." | tee -a "$LOG"
pip install -q torch torchvision pandas pillow pyyaml scipy matplotlib seaborn 2>&1 | tee -a "$LOG"

# Install hessian-eigenthings library
echo "Installing hessian-eigenthings..." | tee -a "$LOG"
pip install -q git+https://github.com/noahgolmant/pytorch-hessian-eigenthings.git 2>&1 | tee -a "$LOG"

# Download Waterbirds dataset if not exists
DATA_DIR="../h-e1/code/data/waterbirds"
mkdir -p "$DATA_DIR"

if [ ! -f "$DATA_DIR/metadata.csv" ]; then
    echo "Downloading Waterbirds dataset..." | tee -a "$LOG"

    # Download from official WILDS repository
    python3 << 'PYEOF' 2>&1 | tee -a "$LOG"
import os
import urllib.request
import tarfile
from pathlib import Path

data_dir = Path("../h-e1/code/data/waterbirds")
data_dir.mkdir(parents=True, exist_ok=True)

# Download waterbirds dataset
url = "https://worksheets.codalab.org/rest/bundles/0xd013a7ba2e88481bbc07e787f73109f5/contents/blob/"
tar_path = data_dir / "waterbird_complete95_forest2water2.tar.gz"

if not tar_path.exists():
    print(f"Downloading from {url}...")
    urllib.request.urlretrieve(url, tar_path)
    print("Download complete")

    print("Extracting archive...")
    with tarfile.open(tar_path, 'r:gz') as tar:
        tar.extractall(data_dir)
    print("Extraction complete")

    # Move files to data_dir root
    extracted_dir = data_dir / "waterbird_complete95_forest2water2"
    if extracted_dir.exists():
        for item in extracted_dir.iterdir():
            item.rename(data_dir / item.name)
        extracted_dir.rmdir()
else:
    print("Dataset already downloaded")
PYEOF
else
    echo "Waterbirds dataset already exists" | tee -a "$LOG"
fi

# Run the experiment
echo "Running h-m1 experiment..." | tee -a "$LOG"
cd "$SCRIPT_DIR"
timeout 7200 python run_h_m1_experiment.py --config config.yaml 2>&1 | tee -a "$LOG"

echo "Experiment completed successfully" | tee -a "$LOG"
