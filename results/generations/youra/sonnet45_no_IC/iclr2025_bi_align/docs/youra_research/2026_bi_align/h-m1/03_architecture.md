# System Architecture: H-M1 Shared Representation Learning

**Hypothesis:** H-M1  
**Type:** MECHANISM (Analysis)  
**Author:** Architecture Agent  
**Date:** 2026-07-13  
**Status:** Ready for Implementation

---

## Applied Patterns

Applied: Linear probing for representation quality measurement (from TensorFlow datasets documentation)
Applied: Centered Kernel Alignment for representation similarity (from NVIDIA cuBLAS documentation)

---

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis  
**Status:** H-E1 trained checkpoints available for reuse  
**Analyzed Path:** `/workspace/TEST_bi_align/docs/youra_research/h-e1/code/`  
**Findings:** Verified H-E1 implementation structure - models in `models/model.py`, training in `training/trainer.py`, data loading in `data/dataset.py`. Checkpoints will be loaded from H-E1 for representation extraction.

---

## System Overview

**Mission:** Analyze internal representations from H-E1 joint-trained model to validate shared encoding mechanism (SHOULD_WORK gate).

**Architecture Tier:** MECHANISM - Analysis-focused architecture for representation probing and similarity measurement.

**Core Components:**
- Checkpoint loading from H-E1 (Joint, DPO-only, Attr-only models)
- Hidden state extraction (final transformer layer, mean pooling)
- Linear probing classifiers (preference classification + attribute regression)
- CKA similarity computation (representation divergence measurement)
- Gradient alignment analysis (multi-task compatibility check)

**Technology Stack:**
- PyTorch 2.0+ (hidden state extraction, probing training)
- HuggingFace Transformers 4.30+ (GPT-2 model loading)
- scikit-learn 1.3+ (R² metric computation)
- matplotlib 3.7+ / seaborn 0.12+ (visualization)

**Reuse from H-E1:**
- Trained model checkpoints (no re-training)
- Dataset splits (500 test samples from HH-RLHF)
- Same model architecture (GPT-2 XL, 1.56B params)

---

## Module Specifications

### CheckpointLoader (`code/models/checkpoint_loader.py`)

**Dependencies:** torch, transformers, h-e1/code/models/model

```python
class CheckpointLoader:
    def __init__(self, base_hypothesis_path: str = "../h-e1"): ...
    def load_joint_model(self) -> JointDPOAttribute: ...
    def load_dpo_model(self) -> BaselineDPO: ...
    def load_attr_model(self) -> BaselineDPO: ...
    def verify_checkpoints(self) -> dict: ...
```

**Interface:**
- Input: Path to H-E1 hypothesis folder
- Output: Loaded PyTorch models (joint, DPO-only, attr-only)
- Verification: Check file existence, model architecture compatibility

---

### HiddenStateExtractor (`code/analysis/extractor.py`)

**Dependencies:** torch, CheckpointLoader

```python
class HiddenStateExtractor:
    def __init__(self, model, device: str = "cuda"): ...
    def extract_from_batch(self, input_ids: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor: ...
    def extract_from_dataset(self, dataloader) -> torch.Tensor: ...
    def save_hidden_states(self, hidden_states: torch.Tensor, save_path: str): ...
```

**Interface:**
- Input: Model + tokenized inputs
- Output: (N, 1600) tensor - mean-pooled hidden states from layer 47
- Extract with torch.no_grad(), model in eval mode
- Use `output_hidden_states=True` in model forward pass

---

### LinearProbe (`code/analysis/probing.py`)

**Dependencies:** torch.nn, sklearn.metrics

```python
class PreferenceProbe(nn.Module):
    def __init__(self, hidden_dim: int = 1600, num_classes: int = 2): ...
    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor: ...

class AttributeProbe(nn.Module):
    def __init__(self, hidden_dim: int = 1600, num_attributes: int = 3): ...
    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor: ...

class ProbeTrainer:
    def __init__(self, probe, optimizer, device: str = "cuda"): ...
    def train_epoch(self, hidden_states: torch.Tensor, labels: torch.Tensor) -> float: ...
    def evaluate(self, hidden_states: torch.Tensor, labels: torch.Tensor) -> dict: ...
    def train(self, train_data: tuple, val_data: tuple, epochs: int = 20) -> dict: ...
```

**Interface:**
- PreferenceProbe: Single linear layer (1600 → 2), returns logits
- AttributeProbe: Single linear layer (1600 → 3), returns predictions
- ProbeTrainer: Adam optimizer (lr=1e-3), 20 epochs, returns accuracy/R²

---

### CKAComputer (`code/analysis/cka.py`)

**Dependencies:** torch

```python
class CKAComputer:
    @staticmethod
    def center_gram_matrix(K: torch.Tensor) -> torch.Tensor: ...
    @staticmethod
    def compute_cka(repr_a: torch.Tensor, repr_b: torch.Tensor) -> float: ...
    def compute_all_pairs(self, repr_joint: torch.Tensor, repr_dpo: torch.Tensor, 
                          repr_attr: torch.Tensor) -> dict: ...
```

**Interface:**
- Input: Two representation matrices (N, hidden_dim)
- Output: CKA score in [0, 1] (0=divergent, 1=identical)
- Implementation: Center representations, compute Gram matrices, apply CKA formula

---

### GradientAnalyzer (`code/analysis/gradient_alignment.py`)

**Dependencies:** torch, h-e1/code/models/model

```python
class GradientAnalyzer:
    def __init__(self, model, ref_policy, device: str = "cuda"): ...
    def compute_alignment(self, batch: dict) -> float: ...
    def analyze_dataset(self, dataloader, num_batches: int = 10) -> dict: ...
```

**Interface:**
- Input: Joint model + batch data
- Output: Cosine similarity between ∇L_DPO and ∇L_attr
- Extract gradients with retain_graph=True, flatten and compute cosine

---

### DataModule (`code/data/probe_dataset.py`)

**Dependencies:** torch.utils.data, datasets, transformers

```python
class ProbeDataset(Dataset):
    def __init__(self, hh_data, attribute_map: dict, tokenizer, max_length: int = 256): ...
    def __getitem__(self, idx: int) -> dict: ...
    def __len__(self) -> int: ...

def load_probe_data(num_samples: int = 500, seed: int = 42) -> tuple:
    """Returns (train_dataset, test_dataset) for probing"""
    ...
```

**Interface:**
- Input: HH-RLHF test split + attribute annotations from H-E1
- Output: Dataset yielding {"input_ids", "attention_mask", "preference_label", "attributes"}
- Split: 400 train / 100 test for probe training

---

### VisualizationModule (`code/visualization/plots.py`)

**Dependencies:** matplotlib, seaborn, sklearn.manifold

```python
def plot_gate_metrics(metrics: dict, thresholds: dict, save_path: str): ...
def plot_tsne(hidden_states: dict, labels: dict, save_path: str): ...
def plot_probing_curves(train_history: dict, val_history: dict, save_path: str): ...
def plot_cka_heatmap(cka_matrix: dict, save_path: str): ...
def plot_gradient_distribution(cosine_sims: list, save_path: str): ...
```

**Interface:**
- plot_gate_metrics(): Mandatory bar chart with pass/fail colors
- plot_tsne(): 2D projection of joint/DPO/attr representations
- plot_probing_curves(): Training/validation accuracy and R² over epochs
- plot_cka_heatmap(): 3×3 matrix showing all pairwise CKA scores

---

### MainRunner (`code/run_analysis.py`)

**Dependencies:** All modules

```python
def setup_analysis(config: dict) -> dict:
    """Load checkpoints, prepare datasets. Returns components dict."""
    ...

def extract_representations(config: dict, components: dict) -> dict:
    """Extract hidden states from all 3 models. Returns representation tensors."""
    ...

def run_probing(config: dict, representations: dict, data: dict) -> dict:
    """Train probing classifiers. Returns accuracy and R² scores."""
    ...

def compute_similarity(representations: dict) -> dict:
    """Compute CKA between model pairs. Returns CKA matrix."""
    ...

def analyze_gradients(config: dict, components: dict, data: dict) -> dict:
    """Compute gradient alignment. Returns cosine similarity statistics."""
    ...

def generate_visualizations(results: dict, save_dir: str):
    """Generate all required figures."""
    ...

def generate_report(results: dict, config: dict, output_path: str):
    """Write 04_validation.md with pass/fail determination."""
    ...

def main():
    config = load_config()
    components = setup_analysis(config)
    representations = extract_representations(config, components)
    data = load_probe_data(num_samples=500)
    
    probing_results = run_probing(config, representations, data)
    cka_results = compute_similarity(representations)
    gradient_results = analyze_gradients(config, components, data)
    
    all_results = {**probing_results, **cka_results, **gradient_results}
    generate_visualizations(all_results, config["figure_dir"])
    generate_report(all_results, config, config["report_path"])
```

---

## File Structure

```
code/
├── models/
│   └── checkpoint_loader.py    # Load H-E1 trained models
├── data/
│   └── probe_dataset.py        # Dataset for probing (500 samples)
├── analysis/
│   ├── extractor.py            # Hidden state extraction
│   ├── probing.py              # Linear probe classifiers
│   ├── cka.py                  # CKA similarity computation
│   └── gradient_alignment.py   # Gradient analysis
├── visualization/
│   └── plots.py                # All plotting functions
├── config.yaml                 # Hyperparameters
├── run_analysis.py             # Main runner
└── requirements.txt            # Dependencies
```

---

## External Dependencies (Base Hypothesis)

### Module Paths (From Actual Code)

| Module | Import Path | File Location |
|--------|-------------|---------------|
| JointDPOAttribute | `from h_e1.code.models.model import JointDPOAttribute` | `h-e1/code/models/model.py` |
| BaselineDPO | `from h_e1.code.models.model import BaselineDPO` | `h-e1/code/models/model.py` |
| ReferencePolicy | `from h_e1.code.models.model import ReferencePolicy` | `h-e1/code/models/model.py` |
| JointDataset | `from h_e1.code.data.dataset import JointDataset` | `h-e1/code/data/dataset.py` |

**Verified from:** `/workspace/TEST_bi_align/docs/youra_research/h-e1/code/` (actual implementation)

**Note:** Import paths assume H-E1 code is accessible via Python path or relative imports.

---

## Data Flow

1. **Setup Phase:**
   - Load H-E1 checkpoints (joint_model_final.pt, dpo_only_final.pt, attr_only_final.pt)
   - Load 500 test examples from HH-RLHF with attribute annotations
   - Initialize probing classifiers and CKA computer
   - Set all models to eval mode, no gradient tracking

2. **Hidden State Extraction (5 min):**
   - For each model (joint, DPO, attr):
     - Forward pass with output_hidden_states=True
     - Extract last transformer layer (layer 47): outputs.hidden_states[-1]
     - Mean pool over sequence: hidden.mean(dim=1)
     - Save tensors: (500, 1600) per model
   - Result: 3 representation matrices

3. **Linear Probing (20 min):**
   - Split 500 samples: 400 train / 100 test
   - Train preference probe:
     - Input: Joint model hidden states (400, 1600)
     - Target: Binary preference labels (400,)
     - Train 20 epochs with Adam (lr=1e-3)
     - Evaluate on test set: compute accuracy
   - Train attribute probe:
     - Input: Joint model hidden states (400, 1600)
     - Target: Attribute values (400, 3)
     - Train 20 epochs with Adam (lr=1e-3)
     - Evaluate on test set: compute R² per attribute

4. **CKA Computation (2 min):**
   - Compute CKA(Joint, DPO) - primary metric
   - Compute CKA(Joint, Attr) - additional analysis
   - Compute CKA(DPO, Attr) - baseline divergence
   - Result: 3×3 similarity matrix

5. **Gradient Alignment (3 min):**
   - Sample 10 random training batches
   - For each batch:
     - Compute L_DPO, backward with retain_graph=True
     - Extract ∇L_DPO, zero gradients
     - Compute L_attr, backward
     - Extract ∇L_attr
     - Compute cosine similarity
   - Aggregate: mean, std, min, max

6. **Visualization (2 min):**
   - Gate metrics comparison (mandatory)
   - t-SNE projection of hidden states
   - Probing learning curves
   - CKA heatmap
   - Gradient alignment distribution

7. **Reporting:**
   - Check gate conditions:
     - Preference accuracy ≥70%
     - Attribute R² ≥0.6 (all 3)
     - CKA(Joint, DPO) ≤0.7
     - Gradient cosine ∈ [-0.5, 0.5]
   - Generate 04_validation.md with pass/fail
   - Save all figures to figures/

---

## Epic Tasks

| ID | Task | Description | Complexity | Breakdown |
|----|------|-------------|------------|-----------|
| Epic-1 | Checkpoint Loading | Load H-E1 trained models, verify compatibility | 6/20 | Module(2) + Deps(1) + Algo(1) + Integ(2) |
| Epic-2 | Hidden State Extraction | Extract layer 47 hidden states from 500 samples | 8/20 | Module(2) + Deps(2) + Algo(2) + Integ(2) |
| Epic-3 | Linear Probing | Train preference classifier + attribute regressor | 11/20 | Module(3) + Deps(2) + Algo(3) + Integ(3) |
| Epic-4 | CKA Computation | Implement centered kernel alignment between models | 9/20 | Module(2) + Deps(1) + Algo(4) + Integ(2) |
| Epic-5 | Gradient Alignment | Measure cosine similarity between DPO and Attr gradients | 10/20 | Module(2) + Deps(2) + Algo(3) + Integ(3) |
| Epic-6 | Visualization | Generate gate metrics, t-SNE, learning curves, CKA heatmap | 7/20 | Module(2) + Deps(1) + Algo(2) + Integ(2) |
| Epic-7 | Evaluation & Reporting | Check gate conditions, write 04_validation.md | 5/20 | Module(1) + Deps(1) + Algo(1) + Integ(2) |

**Complexity Distribution:**
- High (9-12): Epic-3, Epic-4, Epic-5
- Medium (6-8): Epic-1, Epic-2, Epic-6
- Low (1-5): Epic-7

**Total Complexity:** 56/140 (7 epics, average 8.0/20)

**Estimated Timeline:** 1-2 days implementation + 1 hour execution (no training, only analysis)

---

## Key Design Decisions

**1. Reuse H-E1 Checkpoints:**
- No re-training needed (H-E1 already validated convergence)
- Load trained models directly from H-E1 hypothesis folder
- Enables controlled comparison (same training history)

**2. Hidden State Extraction Layer:**
- Use final transformer layer (layer 47 in GPT-2 XL)
- Mean pooling over sequence dimension (simplifies probing)
- Alternative considered: Last token hidden state (rejected - less stable for varying sequence lengths)

**3. Probing Classifier Capacity:**
- Single linear layer (minimal capacity to test linear separability)
- If fails: Can increase to 2-layer MLP in failure analysis
- No regularization (representations are frozen, no overfitting risk)

**4. CKA vs. Other Similarity Metrics:**
- CKA chosen for invariance to orthogonal transformations
- Alternative considered: Cosine similarity (rejected - not invariant to rotations)
- Alternative considered: Procrustes distance (rejected - less standard in literature)

**5. Gradient Alignment Measurement:**
- Sample 10 batches (balances statistical reliability vs. runtime)
- Use cosine similarity (interpretable: -1 = opposite, 0 = orthogonal, +1 = aligned)
- Does NOT modify training (pure post-hoc analysis)

---

## Dependencies & Constraints

**Internal Dependencies:**
- H-E1 MUST be completed with PASS result
- Checkpoint files MUST exist: joint_model_final.pt, dpo_only_final.pt, attr_only_final.pt
- Dataset cache from H-E1 MUST be accessible (HH-RLHF test split)

**External Dependencies:**
- PyTorch ≥2.0.0 (hidden state extraction)
- HuggingFace Transformers ≥4.30.0 (GPT-2 model loading)
- scikit-learn ≥1.3.0 (R² computation, t-SNE)
- matplotlib ≥3.7.0, seaborn ≥0.12.0 (visualization)

**Hardware Requirements:**
- 1× GPU with 16GB VRAM (hidden state extraction for 500 samples)
- 32GB system RAM (store 3×500×1600 float32 tensors = ~10GB)
- 10GB storage (checkpoints + hidden states + figures)

**Runtime Constraints:**
- No training (only inference and probing)
- Total runtime: ~30 minutes (5 min extraction + 20 min probing + 5 min analysis)
- Single seed (42, matching H-E1)

---

## Validation Criteria

**SHOULD_WORK Gate Metrics:**
1. Preference Probing Accuracy: ≥70% (demonstrates shared encoding of preferences)
2. Attribute Regression R²: ≥0.6 for ALL 3 attributes (demonstrates shared encoding of attributes)
3. CKA Similarity (Joint-DPO): ≤0.7 (demonstrates representation divergence)
4. Gradient Cosine Similarity: ∈ [-0.5, 0.5] (demonstrates multi-task compatibility)

**Success Condition:** ALL four metrics pass

**Failure Condition:** ANY metric fails → Investigate:
- Low probing accuracy: Check hidden layer (layer 47 correct?), try 2-layer probe
- Low attribute R²: Check attribute annotation quality, try separate probes per attribute
- High CKA (>0.7): Verify extraction code (not using same checkpoint twice?)
- Gradient conflict (<-0.5): Re-check H-E1 training logs, verify loss weighting

---

## Implementation Notes for Phase 4

**Critical Path:**
1. Epic-1 (Checkpoint Loading) → MUST verify files exist before proceeding
2. Epic-2 (Hidden State Extraction) → MUST validate shape (500, 1600) per model
3. Epic-3 (Linear Probing) → MUST check convergence (loss decreasing)
4. Epic-4, Epic-5 (CKA & Gradient) → Can run in parallel
5. Epic-6, Epic-7 (Visualization & Reporting) → Sequential

**Testing Strategy:**
- Unit test: CKA computation with synthetic data (verify CKA=1.0 for identical inputs)
- Integration test: Extract hidden states from 10 samples (verify shape)
- Full run: 500 samples analysis

**Error Handling:**
- Checkpoint not found → Clear error message pointing to H-E1 execution requirement
- CUDA OOM during extraction → Reduce batch size to 1, process sequentially
- Probing NaN loss → Add gradient clipping, reduce learning rate

**Logging Requirements:**
- Save hidden states to disk: hidden_states_{model_name}.pt
- Save probing metrics: probing_results.json
- Save CKA matrix: cka_matrix.json
- Save gradient alignment: gradient_stats.json

---

**Architecture Status:** Complete - Ready for Phase 4 Implementation  
**Next Step:** Phase 4 Coder Agent
