---
name: 'step-01a-data-setup'
description: 'Dataset & Model Download - Download and verify datasets/models before code generation'

# Path Definitions
workflow_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/phase4-coding'

# File References
thisStepFile: '{workflow_path}/steps/step-01a-data-setup.md'
prevStepFile: '{workflow_path}/steps/step-01-initialize.md'
nextStepFile: '{workflow_path}/steps/step-02-coder-loop.md'
workflowFile: '{workflow_path}/workflow.md'

# Input Files
experiment_brief: '{hypothesis_folder}/02c_experiment_brief.md'
verification_state: '{research_folder}/verification_state.yaml'

# Output Paths
checkpoint_file: '{hypothesis_folder}/04_checkpoint.yaml'
data_folder: '{hypothesis_folder}/code/data'
models_folder: '{hypothesis_folder}/code/models/pretrained'

# Shared Data Cache (cross-hypothesis)
shared_data_cache: '{research_folder}/.data_cache'

# Multi-Dataset Configuration
datasets_to_download: 2 # Download 2 datasets (primary + secondary)
min_datasets_required: 1 # Graceful degradation: proceed with at least 1
---

## Section 0.5: Load Checkpoint

> This ensures checkpoint state is available even after session interruption.

```python
# MANDATORY: Read checkpoint from file (context loss prevention)
checkpoint = read_yaml(checkpoint_file) # {hypothesis_folder}/04_checkpoint.yaml

IF NOT checkpoint:
    STOP("ERROR: Checkpoint not found. Run step-01-initialize first.")

IF checkpoint.current_step < 1.5:
    checkpoint.current_step = 1.5
    SAVE checkpoint

# Log checkpoint load for debugging
print(f"✅ Checkpoint loaded: step={checkpoint.current_step}, conda_env={checkpoint.conda.env_name}")
```

---

# Step 1a: Dataset & Model Download (UNATTENDED Mode)

> **Mode:** UNATTENDED (Fully Automatic) - No user interaction required
> **Purpose:** Download and verify datasets/models BEFORE code generation

---

## STEP GOAL

Ensure all required datasets and pretrained models are available before Step 2 (Coder Loop) begins.
This prevents experiment failures due to missing data.

**Why this step exists:**
- Datasets may require download time (minutes to hours)
- Pretrained models need to be cached
- Early failure detection saves wasted code generation effort
- Enables offline experiment execution

---

## COMMON RULES

> **📖 READ FIRST:** See `_common-rules.md` for Universal Rules, Role Reinforcement, and MCP Error Retry Protocol.

### Step-Specific Rules:

- 📖 Read 02c_experiment_brief.md to extract dataset/model specifications
- 🔍 Check shared cache first before downloading (cross-hypothesis reuse)
- 💾 Download to shared cache, symlink to hypothesis folder
- ✅ Verify downloads with sample loading test
- 🚫 NEVER skip verification step
- 📋 Update checkpoint with data status

---

## EXECUTION SEQUENCE

### 0. Verify Prerequisites

```python
# checkpoint already loaded in Section 0.5 (context loss prevention)

# Verify conda environment exists
IF NOT checkpoint.conda.env_name:
    STOP("Conda environment not created. Run Step 1 first.")

# Store conda activation command for reuse
CONDA_ACTIVATE = f"""
source {checkpoint.conda.conda_path}/etc/profile.d/conda.sh
conda activate {checkpoint.conda.env_name}
"""
```

### 1. Extract Dataset Specification from 02c

```python
experiment_brief = Read(experiment_brief)

# Parse Dataset section
dataset_section = extract_section(experiment_brief, "### Dataset")

dataset_spec = {
    "name": extract_field(dataset_section, "Dataset|Name"),
    "type": extract_field(dataset_section, "Type"), # standard | custom | synthetic
    "source": extract_field(dataset_section, "Source"), # torchvision | huggingface | url | local
    "path": extract_field(dataset_section, "Path"), # auto | ./data/{name}/ | absolute
    "download_url": extract_field(dataset_section, "Download|URL"), # optional
    "statistics": {
        "total_samples": extract_field(dataset_section, "Total samples"),
        "train_split": extract_field(dataset_section, "Train"),
        "val_split": extract_field(dataset_section, "Val"),
        "test_split": extract_field(dataset_section, "Test"),
        "classes": extract_field(dataset_section, "Classes")
    },
    "preprocessing": extract_field(dataset_section, "Preprocessing|Normalization"),
    "augmentation": extract_field(dataset_section, "Augmentation")
}

print(f"📊 Dataset: {dataset_spec.name}")
print(f" Type: {dataset_spec.type}")
print(f" Source: {dataset_spec.source}")
```

### 2. Extract Model Specification from 02c

```python
model_section = extract_section(experiment_brief, "### Baseline Model|### Models")

model_spec = {
    "name": extract_field(model_section, "Architecture|Model|Name"),
    "type": extract_field(model_section, "Type"),
    "source": extract_field(model_section, "Source"), # torchvision | huggingface | timm | url
    "pretrained": extract_field(model_section, "Pretrained|Status"), # Yes | No
    "checkpoint_source": extract_field(model_section, "checkpoint|Source"), # optional URL
    "input_size": extract_field(model_section, "Input size"),
    "output_size": extract_field(model_section, "Output size")
}

print(f"🤖 Model: {model_spec.name}")
print(f" Pretrained: {model_spec.pretrained}")
```

### 3. Create Data Folders

```bash
# Create hypothesis-specific data folders
mkdir -p {data_folder}
mkdir -p {models_folder}

# Create shared cache if not exists
mkdir -p {shared_data_cache}/datasets
mkdir -p {shared_data_cache}/models
```

### 4. Install Required Packages

```python
# Base packages for data loading
base_packages = ["torch", "torchvision", "torchaudio", "numpy", "pillow"]

# Source-specific packages
IF dataset_spec.source == "huggingface" OR model_spec.source == "huggingface":
    base_packages.extend(["datasets", "transformers", "huggingface_hub"])

IF model_spec.source == "timm":
    base_packages.append("timm")

IF "kaggle" in dataset_spec.source.lower():
    base_packages.append("kaggle")

# GPU-specific PyTorch (if needed)
IF checkpoint.gpu.pytorch_cuda_needed:
    pytorch_install = "pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118"
ELSE:
    pytorch_install = "pip install torch torchvision torchaudio"

# Execute installation
Bash(f"""
{CONDA_ACTIVATE}
{pytorch_install}
pip install {' '.join(base_packages)}
""", timeout=600000) # 10 minute timeout for downloads
```

### 5. Download Dataset

> **Approach:** Use loading information from 02c_experiment_brief.md (determined in Phase 2C)

#### 5a. Check Cache (Shared + Previous Hypotheses)

```python
dataset_name = dataset_spec.name
cache_path = f"{shared_data_cache}/datasets/{dataset_name}"

# Option 1: Check shared cache directory
IF dir_exists(cache_path) AND dir_not_empty(cache_path):
    print(f"✅ Dataset '{dataset_name}' found in shared cache")
    Bash: ln -sf {cache_path} {data_folder}/{dataset_name}
    GOTO Section 5d # Skip download

# Option 2: Check verification_state for previous hypothesis cache
verification_state = Read(verification_state.yaml)
FOR each completed_hypothesis in verification_state.sub_hypotheses:
    IF completed_hypothesis.data_setup.dataset.name == dataset_name:
        IF completed_hypothesis.data_setup.dataset.verified == true:
            previous_cache = completed_hypothesis.data_setup.dataset.cache_path
            IF dir_exists(previous_cache) AND dir_not_empty(previous_cache):
                print(f"✅ Dataset '{dataset_name}' found from {completed_hypothesis.id}")
                Bash: ln -sf {previous_cache} {data_folder}/{dataset_name}
                GOTO Section 5d # Skip download
```

#### 5b. Read Loading Information from 02c

```python
# Read loading info from 02c (populated by Phase 2C)
loading_method = extract_field(experiment_brief, "Loading Information/Method") # HuggingFace | torchvision | custom
loading_identifier = extract_field(experiment_brief, "Loading Information/Identifier") # e.g., "cifar10", "CIFAR10"
loading_code = extract_field(experiment_brief, "Loading Information/Code") # e.g., load_dataset("cifar10")

print(f"📋 Loading info from 02c:")
print(f" Method: {loading_method}")
print(f" Identifier: {loading_identifier}")
```

#### 5c. Execute Download

```python
print(f"⬇️ Downloading '{dataset_name}'...")
Bash: mkdir -p {cache_path}

# Use the loading code from 02c directly
# Phase 2C already determined the correct loading method via MCP search

download_script = f"""
{CONDA_ACTIVATE}
python -c "
{loading_code}
print('Download complete!')
"
"""

result = Bash(download_script, timeout=1800000) # 30 min timeout

IF result.exit_code != 0:
    print(f"❌ Download failed: {result.stderr}")
    checkpoint.data_setup.status = "failed"
    checkpoint.data_setup.error = result.stderr
    SAVE checkpoint
    STOP("Dataset download failed")

# Symlink to hypothesis folder
Bash: ln -sf {cache_path} {data_folder}/{dataset_name}
print(f"✅ Dataset downloaded successfully")
```

#### 5d. Custom/Synthetic Handling

**Custom Dataset** (type == "custom"):
- Check if data exists at local path specified in 02c
- If exists → create symlink
- If not exists → error (STOP)

**Synthetic Dataset** (type == "synthetic"):
- No download needed → skip
- Data will be generated by Step 2 code
- If no generation logic in code → natural error at Step 2 execution

### 6. Download Pretrained Model (if needed)

**Pretrained Model** (model_spec.pretrained == "Yes"):
1. Check cache → if exists, create symlink
2. If not cached → execute model_loading_code from 02c
3. Non-fatal if fails (will auto-download on first run)

**No Pretrained** (model_spec.pretrained == "No"):
- skip

### 7. Verify Downloads

**Dataset Verification** (if type != "synthetic"):
- Check data directory exists and is not empty
- If empty/missing → error (STOP)
- Try loading a sample to confirm data is valid

**Model Verification** (if pretrained):
- Check model weights exist (.pth, .pt, .bin)
- Try loading weights to confirm valid
- Non-fatal if missing (will download on first use)

### 8. Update Checkpoint and Verification State

**Update 04_checkpoint.yaml:**

```yaml
checkpoint.data_setup:
  status: "completed"
  completed_at: "{ISO8601}"
  dataset:
    name: "{dataset_spec.name}"
    type: "{dataset_spec.type}"
    path: "{data_folder}/{dataset_spec.name}"
    cache_path: "{shared_data_cache}/datasets/{dataset_spec.name}"
    verified: true
  model:
    name: "{model_spec.name}"
    pretrained: "{model_spec.pretrained}"
    path: "{models_folder}/{model_spec.name}"
    cache_path: "{shared_data_cache}/models/{model_spec.name}"
    verified: true

checkpoint.current_step = 2
SAVE checkpoint
```

**Update verification_state.yaml (for cross-hypothesis cache reuse):**

```yaml
# Update sub_hypotheses.{hypothesis_id}.data_setup
sub_hypotheses.{hypothesis_id}.data_setup:
  status: "COMPLETED"
  dataset:
    name: "{dataset_spec.name}"
    type: "{dataset_spec.type}"
    cache_path: "{shared_data_cache}/datasets/{dataset_spec.name}"
    verified: true
  model:
    name: "{model_spec.name}"
    pretrained: "{model_spec.pretrained}"
    cache_path: "{shared_data_cache}/models/{model_spec.name}"
    verified: true
  completed_at: "{ISO8601}"

SAVE verification_state
```

> This enables subsequent hypotheses to check cache paths before downloading.

### 9. Display Summary and Proceed

```python
print("")
print("=" * 60)
print("📦 DATA SETUP COMPLETE")
print("=" * 60)
print(f"")
print(f"Dataset: {dataset_spec.name}")
print(f" Path: {data_folder}/{dataset_spec.name}")
print(f" Status: ✅ Ready")
print(f"")
print(f"Model: {model_spec.name}")
print(f" Pretrained: {model_spec.pretrained}")
print(f" Status: ✅ Ready")
print(f"")
print("=" * 60)
```

### 10. UNATTENDED Auto-Proceed

Display: "**Proceeding to Step 2 (Coder Loop)...**"

#### Menu Handling Logic:

- After data setup completion (all datasets/models verified), immediately load, read entire file, then execute {nextStepFile}

#### EXECUTION RULES:

- This is an UNATTENDED data setup step with no user choices
- Proceed directly to Step 2 after all datasets/models are ready
- The Coder Loop can now generate code knowing data is available
- **Failure to load Step 2 = SYSTEM FAILURE**

---

## ERROR HANDLING

| Error | Recovery Action |
|-------|-----------------|
| Package installation fails | Retry with --no-cache-dir, check network |
| Dataset download fails | Try alternative mirror, check disk space |
| Disk space insufficient | Clean cache, request user intervention |
| Network timeout | Retry 3 times with exponential backoff |
| URL not accessible | Mark as blocked, suggest manual download |
| Verification fails | Re-download, check file integrity |

**On unrecoverable error:**

```python
checkpoint.data_setup.status = "blocked"
checkpoint.data_setup.error = "{error_message}"
checkpoint.data_setup.manual_action_required = True
checkpoint.data_setup.instructions = """
Manual action required:
1. Download dataset from: {url}
2. Extract to: {expected_path}
3. Re-run Phase 4 workflow
"""
SAVE checkpoint
STOP("Data setup blocked. Manual intervention required.")
```

---

## STEP COMPLETION

**Auto-proceed to `{nextStepFile}` when:**
1. ✅ Dataset downloaded and verified
2. ✅ Model downloaded and verified (if pretrained)
3. ✅ Required packages installed
4. ✅ Checkpoint updated with data paths

**On completion:** Load, read entire file, then execute `{nextStepFile}` (step-02-coder-loop.md)

---

## 🚨 SYSTEM SUCCESS/FAILURE METRICS

### ✅ SUCCESS:

- 02c_experiment_brief.md parsed for dataset/model specs
- Shared cache checked before downloading
- Dataset downloaded to cache and symlinked
- Pretrained model downloaded (if needed)
- Verification test passed
- Checkpoint updated with data paths
- Proceeded to Step 2

### ❌ SYSTEM FAILURE:

- Skipping download when data not cached
- Not verifying downloads
- Proceeding to Step 2 with missing data
- Not updating checkpoint with data paths
- Ignoring download errors
