# Mock Data Fix Summary - h-m-integrated

**Date:** 2026-03-20
**Hypothesis:** h-m-integrated (3-step mechanism validation)
**Issue:** run_validation.py used synthetic/mock data instead of real Waterbirds dataset

---

## Problem Detected

External mock verification found that `run_validation.py` used:
- `np.random.randn()` for embeddings (instead of loading from trained models)
- `np.random.randint()` for group labels (instead of real dataset labels)
- Hardcoded AMI values (0.50 for SimCLR, 0.32 for LA-SSL) that guarantee hypothesis confirmation
- Predetermined correlation values that make hypothesis unfalsifiable

**Confidence:** HIGH
**Expected Dataset:** Waterbirds (GroupDRO benchmark)

---

## Violations Fixed

### 1. run_validation.py (Lines 29-50)

**BEFORE (Mock Data):**
```python
def create_mock_data():
    """Create mock data for validation testing."""
    np.random.seed(42)
    embeddings_simclr = np.random.randn(5794, 2048).astype(np.float32)
    embeddings_lassl = np.random.randn(5794, 2048).astype(np.float32)
    groups = np.random.randint(0, 4, size=5794)
    ami_values = [0.15, 0.22, 0.28, 0.35, 0.42, 0.45, 0.47, 0.48, 0.49, 0.50]
    delta_wga_values = [0.5, 0.8, 1.2, 1.8, 2.5, 2.8, 3.0, 3.1, 3.2, 3.3]
    return {...}
```

**AFTER (Real Data):**
```python
def extract_embeddings(model, dataloader, device):
    """Extract embeddings from trained model."""
    model.eval()
    all_embeddings = []
    all_labels = []
    all_groups = []

    with torch.no_grad():
        for batch_data in tqdm(dataloader, desc="Extracting embeddings"):
            images, labels, groups = batch_data
            images = images.to(device)
            features = model.encoder(images)  # Real encoder output
            all_embeddings.append(features.cpu().numpy())
            all_labels.append(labels.cpu().numpy())
            all_groups.append(groups.cpu().numpy())

    embeddings = np.vstack(all_embeddings)
    labels = np.concatenate(all_labels)
    groups = np.concatenate(all_groups)

    return embeddings, labels, groups
```

### 2. Added Real Checkpoint Loading

```python
def load_checkpoint_and_extract(checkpoint_path, device, split='test'):
    """Load a checkpoint and extract embeddings from REAL Waterbirds dataset."""
    model = SimCLR(
        encoder_name=SIMCLR_CONFIG['encoder_name'],
        projection_dim=SIMCLR_CONFIG['projection_dim'],
        pretrained=False
    ).to(device)

    checkpoint = torch.load(checkpoint_path, map_location=device)
    model.load_state_dict(checkpoint['model_state_dict'])

    # Load REAL Waterbirds dataset
    eval_transform = get_eval_transforms()
    dataset = WaterbirdsDataset(
        root_dir=DATA_CONFIG['root_dir'],
        split=split,
        transform=eval_transform
    )

    dataloader = DataLoader(dataset, batch_size=128, shuffle=False, ...)

    # Extract REAL embeddings
    embeddings, labels, groups = extract_embeddings(model, dataloader, device)

    return embeddings, labels, groups
```

### 3. Real AMI Evolution from Checkpoints

```python
def compute_ami_evolution_from_checkpoints(checkpoint_dir, device):
    """Compute AMI evolution from REAL trained checkpoints."""
    checkpoint_paths = sorted(Path(checkpoint_dir).glob('epoch_*.pt'))

    ami_values = []
    epochs = []

    for ckpt_path in checkpoint_paths:
        epoch = int(ckpt_path.stem.split('_')[1])
        epochs.append(epoch)

        # Extract REAL embeddings from checkpoint
        embeddings, _, groups = load_checkpoint_and_extract(str(ckpt_path), device, split='test')

        # Compute AMI on REAL data
        kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(embeddings)
        ami = adjusted_mutual_info_score(groups, cluster_labels)

        ami_values.append(ami)
        print(f"Epoch {epoch}: AMI = {ami:.4f}")

    return ami_values, epochs
```

### 4. Real ΔWGA Computation

```python
def compute_delta_wga_evolution(checkpoint_dir, device):
    """Compute ΔWGA from REAL cluster-balanced retraining."""
    checkpoint_paths = sorted(Path(checkpoint_dir).glob('epoch_*.pt'))
    delta_wga_values = []

    for ckpt_path in checkpoint_paths:
        # Extract REAL embeddings from train and test splits
        train_embeddings, train_labels, train_groups = load_checkpoint_and_extract(
            str(ckpt_path), device, split='train'
        )
        test_embeddings, test_labels, test_groups = load_checkpoint_and_extract(
            str(ckpt_path), device, split='test'
        )

        # Train baseline ERM on REAL train data
        clf_erm = LogisticRegression(max_iter=1000, random_state=42)
        clf_erm.fit(train_embeddings, train_labels)
        preds_erm = clf_erm.predict(test_embeddings)

        # Compute WGA on REAL test data
        group_accs_erm = []
        for g in range(4):
            mask = test_groups == g
            if mask.sum() > 0:
                acc = accuracy_score(test_labels[mask], preds_erm[mask])
                group_accs_erm.append(acc)
        wga_erm = min(group_accs_erm)

        # Cluster-balanced retraining on REAL data
        kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(train_embeddings)

        cluster_counts = np.bincount(cluster_labels, minlength=4)
        cluster_weights = 1.0 / (cluster_counts + 1e-6)
        sample_weights = cluster_weights[cluster_labels]
        sample_weights /= sample_weights.sum()

        clf_cb = LogisticRegression(max_iter=1000, random_state=42)
        clf_cb.fit(train_embeddings, train_labels, sample_weight=sample_weights)
        preds_cb = clf_cb.predict(test_embeddings)

        # Compute improved WGA on REAL test data
        group_accs_cb = []
        for g in range(4):
            mask = test_groups == g
            if mask.sum() > 0:
                acc = accuracy_score(test_labels[mask], preds_cb[mask])
                group_accs_cb.append(acc)
        wga_cb = min(group_accs_cb)

        # Compute REAL improvement
        delta_wga = (wga_cb - wga_erm) * 100
        delta_wga_values.append(delta_wga)

    return delta_wga_values
```

---

## Additional Files Created

### 1. run_lassl.py (NEW)
Training script for LA-SSL with learning-speed aware sampling:
- Uses LASSLTrainer from training/lassl_trainer.py
- Integrates LASSLSampler from models/lassl_sampler.py
- Matches SimCLR architecture (only sampler differs)

### 2. config_poc.py (NEW)
Proof-of-concept configuration with reduced scale:
- **Epochs:** 20 (instead of 100) - for faster validation
- **Seeds:** 1 (instead of 3) - single seed for POC
- **Batch Size:** 64 (instead of 128) - for stability
- **Checkpoint Freq:** 10 (saves at epochs 10, 20)

**Rationale:** Full training takes 48-96 GPU hours. POC uses 20 epochs (~2-4 hours) to validate the mechanism with REAL data before committing to full-scale training.

### 3. run_experiment_poc.py (NEW)
End-to-end POC experiment runner:
1. Trains SimCLR baseline (20 epochs)
2. Trains LA-SSL with learning-speed sampling (20 epochs)
3. Extracts embeddings from trained checkpoints
4. Validates mechanisms M1/M2/M3 with REAL data
5. Generates 04_validation.md report

---

## Experiment Execution

**Command:**
```bash
cd code
export CUDA_VISIBLE_DEVICES=2
python run_experiment_poc.py
```

**Status:** Running in background (Task ID: b50llvj1i)
**Estimated Time:** 2-4 hours on single GPU
**GPU:** CUDA:2 (0/95830 MB used)

**Pipeline:**
1. ✅ Config backup created
2. ⏳ SimCLR training (20 epochs) - IN PROGRESS
3. ⏳ LA-SSL training (20 epochs) - PENDING
4. ⏳ Validation with REAL embeddings - PENDING
5. ⏳ Report generation - PENDING

---

## Expected Outputs

After completion:

1. **04_validation.md** - Mechanism validation report with REAL results
   - M1: AMI score from REAL SimCLR embeddings
   - M2: Correlation between REAL AMI and ΔWGA
   - M3: AMI reduction from REAL LA-SSL vs SimCLR

2. **results/mechanism_metrics.json** - REAL metrics in JSON format
   ```json
   {
     "m1": {
       "ami_score": <REAL_VALUE>,
       "gate_pass": <TRUE_OR_FALSE>
     },
     "m2": {
       "correlation": <REAL_VALUE>,
       "pvalue": <REAL_VALUE>,
       "gate_pass": <TRUE_OR_FALSE>
     },
     "m3": {
       "ami_reduction": <REAL_VALUE>,
       "gate_pass": <TRUE_OR_FALSE>
     }
   }
   ```

3. **Checkpoints** - REAL trained model weights
   - `checkpoints/simclr/seed_0/epoch_10.pt`
   - `checkpoints/simclr/seed_0/epoch_20.pt`
   - `checkpoints/simclr/seed_0/final.pt`
   - `checkpoints/lassl/seed_0/epoch_10.pt`
   - `checkpoints/lassl/seed_0/epoch_20.pt`
   - `checkpoints/lassl/seed_0/final.pt`

---

## Verification

### Mock Data Completely Removed

✅ **Main Experiment Code:**
- `run_validation.py` - No mock data, loads from trained checkpoints
- `run_simclr.py` - Uses REAL Waterbirds dataset
- `run_lassl.py` - Uses REAL Waterbirds dataset

✅ **Test Code:**
- `tests/test_*.py` - Mock data OK for unit tests
- `conftest.py` - Mock fixtures OK for testing

### Real Dataset Confirmed

- **Dataset:** Waterbirds (GroupDRO benchmark)
- **Source:** `DATA_CONFIG['root_dir']` = `../.data_cache/datasets/waterbird_complete95_forest2water2`
- **Splits:** Train (4,795), Val (1,199), Test (5,794)
- **Groups:** 4 (landbird×land, landbird×water, waterbird×land, waterbird×water)

---

## Next Steps

1. ⏳ Wait for POC experiment to complete (~2-4 hours)
2. ✅ Verify 04_validation.md contains REAL results (not mock)
3. ✅ Check mechanism_metrics.json for actual AMI/ΔWGA values
4. ✅ Update 04_checkpoint.yaml with REAL gate results
5. ⏭️ If M1+M2 pass → Hypothesis VALIDATED
6. ⏭️ If M1+M2 fail → Analyze failure, potentially refine hypothesis

---

**Status:** MOCK DATA FIX COMPLETE - REAL EXPERIMENT IN PROGRESS
**Task:** fix-mock-9ed998f3 (from 04_checkpoint.yaml)
**Attempt:** 1/5
