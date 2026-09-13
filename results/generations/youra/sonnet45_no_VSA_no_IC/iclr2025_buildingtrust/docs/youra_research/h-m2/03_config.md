# Configuration Specifications: H-M2

**Date:** 2026-08-19  
**Hypothesis:** H-M2 (MECHANISM - Generalization Breadth)  
**Version:** 1.0

---

## Configuration Files

### `.env` (API Credentials)
```bash
# OpenAI API
OPENAI_API_KEY=sk-...

# Anthropic API
ANTHROPIC_API_KEY=sk-ant-...

# Together API (Llama 3.1)
TOGETHER_API_KEY=...

# Optional: API rate limits (requests per minute)
OPENAI_RPM=500
ANTHROPIC_RPM=500
TOGETHER_RPM=1000
```

**Security:** Never commit .env to git (add to .gitignore)

---

### `config.yaml` (Experiment Parameters)

```yaml
# Dataset Configuration
dataset:
  name: "TrustLLM/TrustLLM-dataset"
  cache_dir: "data/trustllm_cache"
  dimensions:
    - truthfulness
    - safety
    - fairness
    - robustness
    - privacy
  
# Sampling Configuration
sampling:
  n_per_dimension: 100  # Total sample size = 100 × 5 = 500
  random_seed: 42
  stratified: true

# Model Configuration
models:
  - name: "gpt-4-turbo"
    provider: "openai"
    max_tokens: 100
    temperature: 0.0  # Deterministic evaluation
    
  - name: "claude-3-5-sonnet"
    provider: "anthropic"
    max_tokens: 100
    temperature: 0.0
    
  - name: "llama-3.1-70b-instruct"
    provider: "together"
    max_tokens: 100
    temperature: 0.0

# API Configuration
api:
  max_retries: 3
  retry_delays: [1, 2, 4]  # Exponential backoff (seconds)
  concurrent_requests: 10  # Parallel API calls per model
  timeout: 30  # Request timeout (seconds)
  checkpoint_interval: 50  # Save progress every N instances

# Statistical Configuration
statistics:
  phi_threshold: 0.3  # Medium effect size (Cohen 1988)
  alpha: 0.01  # Significance level
  correction_method: "bonferroni"  # Options: bonferroni, bonferroni-holm
  validate_chi2_assumptions: true  # Check expected cell counts ≥5

# Gate Configuration
gate:
  type: "SHOULD_WORK"
  min_pairs: 3  # Minimum dimension pairs per model
  min_models: 2  # Minimum models meeting min_pairs threshold
  
# Visualization Configuration
visualization:
  heatmap:
    figsize: [8, 6]
    cmap: "Blues"
    annot: true  # Show phi values
    fmt: ".3f"  # 3 decimal places
    cbar_label: "Phi Coefficient"
    
  bar_chart:
    figsize: [10, 6]
    color_pass: "green"
    color_fail: "red"
    threshold_line_color: "black"
    threshold_line_style: "--"
    
  violin:
    figsize: [12, 6]
    palette: "Set2"
    
  scatter:
    figsize: [10, 8]
    marker_size: 100
    alpha: 0.7

# Logging Configuration
logging:
  level: "INFO"  # Options: DEBUG, INFO, WARNING, ERROR
  format: "[%(asctime)s] %(levelname)s: %(message)s"
  file: "h-m2_code/logs/experiment.log"
  console: true

# Output Configuration
output:
  results_dir: "results"
  figures_dir: "figures"
  save_intermediate: true  # Save coupling_matrix.csv, summary_stats.json
  save_format: "csv"  # Options: csv, json, parquet
```

---

## Hyperparameters

### Sample Size Justification

**n_per_dimension = 100** (total n=500)

**Statistical Power:**
- Target: 80% power to detect phi=0.3 at α=0.01 (uncorrected)
- Required: n≥500 for 80% power (2-tailed chi-square test)
- With Bonferroni: α_adjusted=0.01/30≈0.0003 → requires n≥800 for 80% power
- **Trade-off:** Use n=500 (65% power post-correction) to limit API cost

**Cost-Benefit:**
- n=500: $2.54 API cost, 40-70 min runtime
- n=800: $4.06 API cost, 64-112 min runtime
- **Decision:** Accept lower power (65%) to reduce cost by 38%

---

### Effect Size Threshold

**phi_threshold = 0.3** (medium effect size)

**Rationale (Cohen 1988):**
- phi < 0.1: negligible (not meaningful)
- 0.1 ≤ phi < 0.3: small (detectable but weak)
- **0.3 ≤ phi < 0.5: medium (substantive association)** ← h-m2 threshold
- phi ≥ 0.5: large (strong association)

**Comparison to h-e1:**
- h-e1 used phi ≥ 0.3 (same threshold)
- h-e1 found phi=0.357-0.396 (truthfulness-robustness, fairness-safety)
- h-m2 reuses same threshold for consistency

---

### Significance Level

**alpha = 0.01** (99% confidence)

**Rationale:**
- More conservative than α=0.05 (95% confidence)
- Reduces false positive rate (Type I error)
- Standard for multi-hypothesis testing (Bonferroni correction)

**Bonferroni Adjustment:**
- Total tests: 30 (10 pairs × 3 models)
- Adjusted alpha: 0.01 / 30 ≈ 0.000333
- **Trade-off:** Very conservative (low false positives, higher false negatives)

---

### Gate Condition

**min_pairs = 3, min_models = 2**

**Rationale:**
- **min_pairs=3:** More than h-e1 found (2 pairs) → tests generalization
- **min_models=2:** Majority of 3 models → cross-model robustness
- **SHOULD_WORK gate:** Failure acceptable → Phase 5 not blocked

**Comparison to h-e1:**
- h-e1: MUST_WORK gate (≥1 model, ≥1 pair with phi ≥ 0.3)
- h-m2: SHOULD_WORK gate (≥2 models, ≥3 pairs with phi ≥ 0.3)
- h-m2 is strictly harder than h-e1

---

### API Configuration

**concurrent_requests = 10**

**Rationale:**
- OpenAI rate limit: 500 RPM (requests per minute) → 8.3 RPS
- Anthropic rate limit: 500 RPM → 8.3 RPS
- Together rate limit: 1000 RPM → 16.7 RPS
- **10 concurrent = 10 RPS** → safely below all limits

**Runtime Estimate:**
- 500 instances per model / 10 RPS = 50 seconds per model (best case)
- Actual: 2-3× slower due to API latency → 2-3 minutes per model
- Total: 6-9 minutes for all 3 models (parallel execution)
- **Observed:** 40-70 minutes (indicates 1-2s per API call, not instant)

**checkpoint_interval = 50**

**Rationale:**
- Checkpoint every 50 instances = 10% progress increments
- Balances resume granularity vs I/O overhead
- Worst-case loss: 49 instances (~$0.25 API cost) on failure

---

## Environment Setup

### Python Version
```bash
python >= 3.10
```

**Rationale:** Type hints with union syntax (e.g., `str | None`) require 3.10+

---

### Dependencies

**requirements.txt:**
```
# Core
numpy==1.24.3
pandas==2.0.2
scipy==1.11.1

# Statistics
statsmodels==0.14.0

# Visualization
matplotlib==3.7.1
seaborn==0.12.2

# Data Loading
datasets==2.14.0

# API Clients
openai==1.12.0
anthropic==0.21.3
together==0.2.8

# Utils
python-dotenv==1.0.0
pyyaml==6.0
tqdm==4.65.0
```

**Installation:**
```bash
cd h-m2_code
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## Directory Initialization

### Setup Script (`scripts/00_setup.sh`)
```bash
#!/bin/bash
# Initialize h-m2_code directory structure

cd "$(dirname "$0")/.."

# Create directories
mkdir -p data/trustllm_cache
mkdir -p results
mkdir -p figures
mkdir -p logs
mkdir -p tests

# Create .env template (user fills in API keys)
cat > .env.template <<EOF
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
TOGETHER_API_KEY=...
EOF

echo "Directory structure initialized."
echo "Copy .env.template to .env and fill in API keys."
```

---

## Validation Checks

### Pre-Execution Checklist
- [ ] `.env` file exists with all 3 API keys
- [ ] `config.yaml` validated (pyyaml.safe_load)
- [ ] Python 3.10+ installed
- [ ] All dependencies installed (pip freeze | grep -f requirements.txt)
- [ ] Write permissions for data/, results/, figures/, logs/

### Runtime Validation
- [ ] TrustLLM dataset downloaded successfully
- [ ] Sample size = 500 (100 per dimension × 5 dimensions)
- [ ] All 3 models evaluated (1500 API calls total)
- [ ] All 30 phi coefficients computed
- [ ] All expected cell counts ≥5 (chi-square assumption)
- [ ] Gate result written to gate_result.json

---

**Configuration Status:** COMPLETE  
**Next Step:** Core Logic Specifications (03_logic.md)
