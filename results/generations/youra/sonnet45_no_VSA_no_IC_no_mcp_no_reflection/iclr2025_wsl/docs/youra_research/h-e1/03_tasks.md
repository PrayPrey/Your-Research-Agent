# Implementation Task List: h-e1

**Date:** 2026-08-28  
**Hypothesis:** h-e1 - Layer-wise weight tokenization preserves structural signal  
**Type:** EXISTENCE  
**Tier:** 2 (Moderate)  
**Total Complexity:** 35  
**Budget:** 60 subtasks (Tier 2 allocation)

---

## Task Hierarchy

### EPIC-1: Data Pipeline (Complexity: 8)

**Description:** Load timm models, tokenize layer weights, stratified split by architecture family

#### Subtasks

1. **EPIC-1.1: Model Loading** (Complexity: 2)
   - Implement `TimmModelZooLoader.__init__()` with family filters
   - Implement `TimmModelZooLoader.load_models()` using timm.list_models() and timm.create_model()
   - Cache downloaded models to disk
   - **Files:** `src/data_loader.py`
   - **Dependencies:** timm library
   - **Test:** Load 4 models (1 per family), verify state_dict keys

2. **EPIC-1.2: Weight Extraction** (Complexity: 2)
   - Implement `TimmModelZooLoader.extract_weights()` to extract layer-wise weights from model.state_dict()
   - Filter for 'weight' parameters only (skip biases)
   - Return list of tensors (one per layer)
   - **Files:** `src/data_loader.py`
   - **Dependencies:** torch
   - **Test:** Extract weights from ResNet-50, verify layer count and shapes

3. **EPIC-1.3: Weight Tokenization** (Complexity: 2)
   - Implement `WeightTokenizer.tokenize()`: flatten each layer → pad/truncate to max_layer_size
   - Zero-padding for layers smaller than max_layer_size
   - Per-layer normalization (zero mean, unit variance)
   - **Files:** `src/data_loader.py`
   - **Dependencies:** torch
   - **Test:** Tokenize 10-layer model, verify output shape [num_layers, max_layer_size]

4. **EPIC-1.4: Position Encoding** (Complexity: 2)
   - Implement `WeightTokenizer.add_position_encoding()` with sinusoidal encoding
   - Add layer index information to each token sequence
   - **Files:** `src/data_loader.py`
   - **Dependencies:** torch
   - **Test:** Apply to tokenized weights, verify no shape change

5. **EPIC-1.5: Data Splitting** (Complexity: 2)
   - Implement `TimmModelZooLoader.split_data()` with stratified split by architecture family
   - 70% train / 15% val / 15% test
   - Random seed for reproducibility
   - **Files:** `src/data_loader.py`
   - **Dependencies:** sklearn.model_selection
   - **Test:** Split 100 models, verify per-family distribution

---

### EPIC-2: Baseline Model (Complexity: 5)

**Description:** Weight statistics baseline (mean/std/norm per layer → MLP classifier)

#### Subtasks

6. **EPIC-2.1: Statistics Extraction** (Complexity: 2)
   - Implement `extract_layer_statistics()`: compute mean, std, L2 norm per layer
   - Flatten to [batch, 3*num_layers] feature vector
   - **Files:** `src/model.py`
   - **Dependencies:** torch
   - **Test:** Extract stats from 5 models, verify feature dimension

7. **EPIC-2.2: MLP Classifier** (Complexity: 2)
   - Implement `BaselineMLP.__init__()` with 3-layer architecture (256 → 128 → num_classes)
   - Add ReLU activations and dropout
   - **Files:** `src/model.py`
   - **Dependencies:** torch.nn
   - **Test:** Forward pass with batch_size=32, verify output shape [32, num_classes]

8. **EPIC-2.3: Baseline Training** (Complexity: 1)
   - Integrate baseline model into training pipeline
   - Use same optimizer/scheduler as transformer
   - **Files:** `src/main.py`
   - **Dependencies:** src/train.py
   - **Test:** Train for 5 epochs, verify loss decreases

---

### EPIC-3: Transformer Model (Complexity: 9)

**Description:** Layer-wise tokenization → Transformer encoder → property prediction

#### Subtasks

9. **EPIC-3.1: Token Projection** (Complexity: 3)
   - Implement `WeightTransformer.__init__()` token projection layer (max_layer_size → d_model)
   - Add positional encoding module
   - **Files:** `src/model.py`
   - **Dependencies:** torch.nn
   - **Test:** Project tokenized weights to d_model=256, verify shape

10. **EPIC-3.2: Transformer Encoder** (Complexity: 3)
    - Implement TransformerEncoder stack (6 layers, 8 heads, 1024 FFN dim)
    - Configure dropout=0.1
    - **Files:** `src/model.py`
    - **Dependencies:** torch.nn.TransformerEncoder
    - **Test:** Forward pass with [seq_len=20, batch=32, d_model=256], verify output shape

11. **EPIC-3.3: Global Pooling** (Complexity: 1)
    - Implement mean pooling over layer sequence
    - Aggregate [num_layers, batch, d_model] → [batch, d_model]
    - **Files:** `src/model.py`
    - **Dependencies:** torch
    - **Test:** Pool 20 layers to single representation, verify shape

12. **EPIC-3.4: Prediction Head** (Complexity: 2)
    - Implement MLP classifier head (d_model → 128 → num_classes)
    - Add ReLU and dropout
    - **Files:** `src/model.py`
    - **Dependencies:** torch.nn
    - **Test:** Forward pass from d_model to num_classes, verify logits shape

---

### EPIC-4: Training Loop (Complexity: 7)

**Description:** AdamW optimizer + CosineAnnealingLR + early stopping + logging

#### Subtasks

13. **EPIC-4.1: Optimizer Setup** (Complexity: 2)
    - Implement AdamW optimizer with lr=1e-4, weight_decay=1e-5
    - Configure gradient clipping (max_norm=1.0)
    - **Files:** `src/train.py`
    - **Dependencies:** torch.optim
    - **Test:** Initialize optimizer, verify parameter groups

14. **EPIC-4.2: Learning Rate Scheduler** (Complexity: 2)
    - Implement CosineAnnealingLR (T_max=50, eta_min=1e-6)
    - Step scheduler after each epoch
    - **Files:** `src/train.py`
    - **Dependencies:** torch.optim.lr_scheduler
    - **Test:** Simulate 50 epochs, verify LR curve matches cosine annealing

15. **EPIC-4.3: Early Stopping** (Complexity: 2)
    - Implement `EarlyStopping` class with patience=10
    - Monitor validation loss
    - Save best model checkpoint
    - **Files:** `src/train.py`
    - **Dependencies:** None
    - **Test:** Simulate validation losses, verify early stop trigger

16. **EPIC-4.4: Training Epoch Loop** (Complexity: 2)
    - Implement `Trainer.train_epoch()`: forward + loss + backward + clip + step
    - Log train loss and accuracy
    - **Files:** `src/train.py`
    - **Dependencies:** torch.nn.functional
    - **Test:** Run 1 epoch on 10 batches, verify metrics logged

17. **EPIC-4.5: Validation Loop** (Complexity: 1)
    - Implement `Trainer.validate()`: no grad forward pass
    - Compute validation loss and accuracy
    - **Files:** `src/train.py`
    - **Dependencies:** torch
    - **Test:** Run validation on 5 batches, verify metrics

18. **EPIC-4.6: Full Training Pipeline** (Complexity: 1)
    - Implement `Trainer.fit()`: epoch loop + early stopping + checkpointing
    - Return training history
    - **Files:** `src/train.py`
    - **Dependencies:** All Trainer methods
    - **Test:** Train for 10 epochs with early stopping, verify checkpoint saved

---

### EPIC-5: Evaluation (Complexity: 6)

**Description:** Test metrics + confusion matrix + training curves + gate metrics plot

#### Subtasks

19. **EPIC-5.1: Test Evaluation** (Complexity: 2)
    - Implement `evaluate_model()`: compute accuracy, precision, recall, F1 on test set
    - Load best checkpoint from training
    - **Files:** `src/evaluate.py`
    - **Dependencies:** sklearn.metrics
    - **Test:** Evaluate on 20 test samples, verify all metrics computed

20. **EPIC-5.2: Confusion Matrix** (Complexity: 2)
    - Implement `generate_confusion_matrix()`: per-family accuracy heatmap
    - Save to `h-e1/figures/confusion_matrix.png`
    - **Files:** `src/evaluate.py`
    - **Dependencies:** sklearn.metrics, matplotlib
    - **Test:** Generate matrix for 4 classes, verify PNG saved

21. **EPIC-5.3: Training Curves** (Complexity: 1)
    - Implement `plot_training_curves()`: train/val loss and accuracy over epochs
    - Save to `h-e1/figures/training_curves.png`
    - **Files:** `src/evaluate.py`
    - **Dependencies:** matplotlib
    - **Test:** Plot 10 epochs of dummy data, verify PNG saved

22. **EPIC-5.4: Gate Metrics Plot** (Complexity: 1)
    - Implement `plot_gate_metrics()`: bar chart comparing random/baseline/proposed vs threshold
    - Save to `h-e1/figures/gate_metrics.png`
    - **Files:** `src/evaluate.py`
    - **Dependencies:** matplotlib
    - **Test:** Plot with dummy accuracies, verify threshold line visible

23. **EPIC-5.5: Attention Visualization** (Complexity: 1)
    - Implement `visualize_attention()`: extract and plot transformer attention weights
    - Heatmap over layers
    - Save to `h-e1/figures/attention_heatmap.png`
    - **Files:** `src/evaluate.py`
    - **Dependencies:** matplotlib
    - **Test:** Visualize attention for 1 sample, verify PNG saved

---

### EPIC-6: Configuration & Main Entry (Complexity: 3)

**Description:** Config dataclasses, YAML loading, end-to-end pipeline

#### Subtasks

24. **EPIC-6.1: Config Dataclasses** (Complexity: 1)
    - Implement `DataConfig`, `ModelConfig`, `TrainingConfig`, `ExperimentConfig`
    - Add validation methods
    - **Files:** `src/config.py`
    - **Dependencies:** dataclasses
    - **Test:** Instantiate config with defaults, verify all fields present

25. **EPIC-6.2: YAML Config** (Complexity: 1)
    - Create `config.yaml` with all hyperparameters from PRD
    - Implement `load_config()` and `save_config()`
    - **Files:** `src/config.py`, `config.yaml`
    - **Dependencies:** pyyaml
    - **Test:** Load config from YAML, verify types and values

26. **EPIC-6.3: Main Pipeline** (Complexity: 1)
    - Implement `main()`: load config → load data → train baseline → train proposed → evaluate → generate figures
    - Implement `run_baseline()` and `run_proposed()`
    - **Files:** `src/main.py`
    - **Dependencies:** All modules
    - **Test:** Run end-to-end with 10 models, 5 epochs, verify figures generated

---

### FAILSAFE: Environment Setup (Complexity: 2)

**Description:** Dependency installation, directory structure, reproducibility checks

#### Subtasks

27. **FAILSAFE-1: Dependencies** (Complexity: 1)
    - Create `requirements.txt` with torch, timm, sklearn, matplotlib, pyyaml
    - Add installation instructions
    - **Files:** `requirements.txt`, `README.md`
    - **Dependencies:** None
    - **Test:** pip install -r requirements.txt in clean environment

28. **FAILSAFE-2: Directory Setup** (Complexity: 1)
    - Create `h-e1/src/`, `h-e1/data/`, `h-e1/figures/` directories
    - Add `.gitignore` for cached models and checkpoints
    - Set random seed globally (torch, numpy, random)
    - **Files:** Directory structure, `.gitignore`
    - **Dependencies:** None
    - **Test:** Verify all directories exist, seed reproducibility

---

## Task Summary

**Total Epic Tasks:** 6 (including FAILSAFE)  
**Total Subtasks:** 28  
**Total Complexity:** 37 (within Tier 2 budget of 60)  
**Budget Utilization:** 62% (37/60)

**Complexity Distribution:**
- EPIC-1 (Data): 10 subtasks, complexity 8
- EPIC-2 (Baseline): 3 subtasks, complexity 5
- EPIC-3 (Transformer): 4 subtasks, complexity 9
- EPIC-4 (Training): 6 subtasks, complexity 7
- EPIC-5 (Evaluation): 5 subtasks, complexity 6
- EPIC-6 (Config/Main): 3 subtasks, complexity 3
- FAILSAFE: 2 subtasks, complexity 2

**Critical Path:** EPIC-1 → EPIC-3 → EPIC-4 → EPIC-5  
**Parallel Tracks:** EPIC-2 (Baseline) can run alongside EPIC-3 (Transformer)

---

## Implementation Notes

**Phase 4 Execution:**
1. Coder Agent implements subtasks sequentially within each EPIC
2. Validator Agent runs tests after each subtask
3. Gate evaluation happens in EPIC-5.4 (gate metrics plot)
4. All figures generated in EPIC-5

**Dependency Resolution:**
- EPIC-1 must complete before EPIC-2, EPIC-3
- EPIC-4 depends on EPIC-2 and EPIC-3
- EPIC-5 depends on EPIC-4 (trained models)
- EPIC-6 orchestrates all modules

**Expected Runtime:**
- Data preparation (EPIC-1): ~2 hours (download + cache 100 models)
- Model implementation (EPIC-2, EPIC-3): ~2 hours
- Training (EPIC-4): ~4 hours (2 models × 50 epochs each)
- Evaluation (EPIC-5): ~1 hour
- **Total: ~9-11 hours** (automated via Coder-Validator loop)

---

*Task List Status: FINAL*  
*Next Phase: Phase 4 - Coding (execute tasks via Coder-Validator loop)*
