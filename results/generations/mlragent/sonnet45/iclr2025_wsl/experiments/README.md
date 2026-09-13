# Permutation-Invariant Weight Fingerprinting Experiment

This repository contains the implementation and experiments for **Permutation-Invariant Weight Fingerprinting for Neural Network Provenance and Integrity Verification**.

## Overview

This project implements a GNN-based fingerprinting system that can:
- Create permutation-invariant fingerprints of neural networks
- Track model provenance and identify derivatives
- Detect backdoored models
- Identify duplicate models despite symmetry transformations

## Project Structure

```
claude_code/
├── config.py                    # Configuration and hyperparameters
├── data_generator.py            # Generate model zoo with variants
├── run_experiment.py            # Main experiment runner
├── train_gnn.py                 # GNN model training
├── models/
│   ├── gnn_fingerprinter.py    # GNN-based fingerprinting model
│   └── baseline_models.py      # Baseline fingerprinting methods
├── utils/
│   ├── evaluation.py           # Evaluation metrics
│   └── visualization.py        # Plotting utilities
├── data/                        # Generated model zoo (created on run)
├── results/                     # Experiment results and figures
└── checkpoints/                 # Saved model checkpoints
```

## Requirements

Install the required packages:

```bash
pip install torch torchvision torchaudio
pip install torch-geometric
pip install torch-scatter torch-sparse torch-cluster -f https://data.pyg.org/whl/torch-2.0.0+cu118.html
pip install numpy pandas matplotlib seaborn scikit-learn scipy tqdm
```

## Running the Experiments

### Quick Start

To run all experiments with default settings:

```bash
cd claude_code
python run_experiment.py
```

This will:
1. Generate a dataset of neural network models with symmetry variants and backdoors
2. Train the GNN fingerprinting model
3. Train and evaluate baseline methods
4. Generate visualizations and save results

### Step-by-Step Execution

You can also run individual components:

1. **Generate Dataset Only:**
```bash
python data_generator.py
```

2. **Train GNN Model Only:**
```bash
python train_gnn.py
```

3. **Run Full Experiment:**
```bash
python run_experiment.py
```

## Configuration

Edit `config.py` to adjust:
- Number of models to generate
- GNN architecture parameters
- Training hyperparameters
- Evaluation settings

Key parameters:
```python
NUM_BASE_MODELS = 50           # Base models to generate
NUM_SYMMETRY_VARIANTS = 10     # Variants per base model
GNN_HIDDEN_DIM = 128           # GNN hidden dimension
GNN_NUM_LAYERS = 4             # Number of GNN layers
NUM_EPOCHS = 50                # Training epochs
```

## Experiment Components

### 1. Dataset Generation

Creates three types of models:
- **Base models**: Randomly initialized MLP and CNN models
- **Symmetry variants**: Permutation, scaling, and noise transformations
- **Backdoored models**: Models with injected backdoors

### 2. GNN Fingerprinting

Implements a graph neural network that:
- Converts neural networks to graph representations
- Learns permutation-equivariant embeddings
- Uses contrastive learning with triplet loss

### 3. Baseline Methods

Compares against:
- **Weight Statistics**: Layer-wise statistical features
- **PCA**: Dimensionality reduction on flattened weights
- **Neuron Embedding**: Permutation-invariant neuron statistics

### 4. Evaluation Metrics

- **Symmetry Invariance**: Mean cosine similarity between base and variants
- **Provenance Tracking**: Top-k accuracy for identifying base models
- **Backdoor Detection**: AUROC for distinguishing clean vs backdoored
- **Discriminative Power**: Inter-model distance in embedding space

## Results

After running experiments, find:
- **Figures**: `results/*.png` (training curves, comparisons, ROC curves)
- **Metrics**: `results/experiment_results.json`
- **Table**: `results/results_table.csv`
- **Logs**: `results/log.txt`

### Expected Outcomes

The GNN-based method should achieve:
- Symmetry invariance: >0.95 mean similarity
- Top-1 accuracy: >0.80 for provenance tracking
- Backdoor AUROC: >0.85 for integrity verification
- Clear separation between different models

## GPU Support

The code automatically uses GPU if available:
- Check `config.DEVICE` for current device
- Training is significantly faster on GPU
- CPU mode is supported but slower

## Troubleshooting

**Out of Memory (OOM):**
- Reduce `BATCH_SIZE` in config.py
- Reduce `NUM_BASE_MODELS` and `NUM_SYMMETRY_VARIANTS`
- Use smaller GNN architecture

**Slow Training:**
- Reduce `NUM_EPOCHS`
- Reduce dataset size
- Use GPU if available

**Import Errors:**
- Install PyTorch Geometric: `pip install torch-geometric`
- Install dependencies: `pip install -r requirements.txt`

## Citation

If you use this code, please cite:

```bibtex
@article{yourname2025fingerprinting,
  title={Permutation-Invariant Weight Fingerprinting for Neural Network Provenance and Integrity Verification},
  author={Your Name},
  journal={arXiv preprint},
  year={2025}
}
```

## License

MIT License

## Contact

For questions or issues, please open an issue on GitHub.
