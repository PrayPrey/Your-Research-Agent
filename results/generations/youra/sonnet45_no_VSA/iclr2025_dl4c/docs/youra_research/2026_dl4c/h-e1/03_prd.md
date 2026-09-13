# Product Requirements Document: H-E1 Proxy Metric Validation System

---

## Document Metadata

**Document Type:** Product Requirements Document (PRD)  
**Hypothesis ID:** h-e1  
**Hypothesis Type:** EXISTENCE  
**Date Created:** 2026-07-09  
**Author:** Anonymous  
**Status:** Draft  
**Version:** 1.0

**Phase 2C Input:** `02c_experiment_brief.md`  
**Hypothesis Statement:** Proxy metrics (CodeBLEU, normalized runtime ratio, learned PR-style score) demonstrate measurement reliability: CV ≤5%, Cohen's d ≥0.8 between complexity classes, Spearman ρ ≥0.8 cross-hardware

**Gate Type:** MUST_WORK (scoped - validates which proxies proceed, not binary pass/fail)

---

## Executive Summary

### Problem Statement

Current code generation research lacks validated proxy metrics for quality assessment. While functional correctness (pass@k) is well-established, efficiency and code quality proxies remain unvalidated. This creates a measurement gap: researchers cannot reliably evaluate generation quality beyond binary correctness.

**Core Challenge:** Do proposed proxy metrics (CodeBLEU, runtime efficiency, PR-style scoring) provide reliable, stable measurements?

### Success Criteria

**Primary Gate Conditions:**
1. **Coefficient of Variation (CV) ≤ 5%** - Each proxy demonstrates low intra-implementation measurement noise
2. **Cohen's d ≥ 0.8** - Each proxy separates complexity classes with large effect size
3. **Spearman ρ ≥ 0.8** - Each proxy maintains rank correlation across hardware platforms

**Pass Conditions:**
- **Full Pass:** All 3 proxies validated → Proceed with complete proxy set
- **Partial Pass:** 1-2 proxies validated → Proceed with validated subset
- **Fail:** 0 proxies validated → Route to Phase 0 (fundamental measurement failure)

### Scope

**In Scope:**
- Measurement reliability validation for 3 proxy metrics
- Statistical analysis (CV, Cohen's d, Spearman ρ)
- Cross-hardware validation (AWS + local GPU)
- Controlled complexity class testing

**Out of Scope:**
- Model training or fine-tuning
- New metric development
- Production deployment
- Multi-language evaluation (Python only for PoC)

---

## Functional Requirements

### FR-1: Solution Generation System

**Requirement:** Generate diverse code solutions for measurement calibration

**Specifications:**
- **Model:** CodeLlama-7B-Instruct (meta-llama/CodeLlama-7b-Instruct-hf)
- **Dataset:** HumanEval (50 problems selected from 164 total)
- **Diversity:** 10 solutions per problem (temperature=0.8, top_p=0.95)
- **Total Solutions:** 500 (50 problems × 10 solutions)
- **Reproducibility:** Fixed random seed (seed=42)

**Acceptance Criteria:**
- Successfully load CodeLlama-7B-Instruct model
- Generate 10 diverse solutions per problem
- Solutions are syntactically valid Python
- All 500 solutions saved with problem_id + solution_id metadata

**Dependencies:**
- HuggingFace Transformers library
- GPU access (minimum 16GB VRAM for fp16 inference)
- HuggingFace account with Llama license acceptance

---

### FR-2: Proxy Metric 1 - CodeBLEU Measurement

**Requirement:** Measure structural and semantic code similarity using CodeBLEU

**Specifications:**
- **Implementation:** k4black/codebleu (PyPI package v0.7.0+)
- **Sub-metrics:** 4 components with equal weighting (0.25 each)
  1. N-gram match (BLEU-4)
  2. Weighted n-gram match
  3. AST match (syntax tree similarity)
  4. Data-flow match (semantic logic similarity)
- **Language:** Python
- **References:** HumanEval canonical solutions
- **Measurements:** 5 repeated measurements per solution (2,500 total measurements)

**Acceptance Criteria:**
- CodeBLEU scores computed for all 500 solutions
- All 4 sub-metric scores recorded
- Measurement reproducibility verified (same solution → same score)
- CV computed across 5 repeated measurements per solution

**Dependencies:**
- `pip install codebleu`
- HumanEval canonical solutions available

---

### FR-3: Proxy Metric 2 - Runtime Efficiency Measurement

**Requirement:** Measure computational efficiency via CPU instruction count

**Specifications:**
- **Metric:** Normalized instruction count ratio
- **Formula:** `runtime_ratio = reference_instructions / max(solution_instructions, 1)`
- **Tool:** Linux `perf` hardware performance counters
- **Command:** `perf stat -e instructions python -c <code>`
- **Normalization:** Against HumanEval canonical solution instruction counts
- **Measurements:** 5 repeated measurements per solution (2,500 total measurements)

**Acceptance Criteria:**
- CPU instruction counts captured for all 500 solutions
- Instruction counts for all 50 canonical solutions captured
- Normalized ratios computed (solution/reference)
- CV computed across 5 repeated measurements per solution
- Measurement stability verified (CV expected ~2-3% per COFFE 2025)

**Dependencies:**
- Linux OS with `perf` support
- `perf_event_open` system call access
- Hardware Performance Monitoring Unit (PMU) available

**Fallback (if perf unavailable):**
- Wall-clock execution time with fixed test inputs
- Median of 10 runs to reduce noise
- Document measurement noise in validation report

---

### FR-4: Proxy Metric 3 - PR-Style Score (Placeholder)

**Requirement:** Learned metric for code quality assessment

**Specifications (Phase 1 - PoC):**
- **Implementation:** Placeholder returning random score [0.0, 1.0]
- **Justification:** Requires SWE-bench PR data training (out of scope for PoC)
- **Future Work:** Train classifier on accepted vs rejected PR code diffs

**Acceptance Criteria (PoC):**
- Placeholder function returns scores for all 500 solutions
- Scores are deterministic with fixed random seed
- Metric interface matches CodeBLEU/runtime (can be swapped with trained model later)

**Dependencies:**
- None (placeholder implementation)

**Post-PoC Requirements (Phase 2):**
- SWE-bench dataset with PR acceptance labels
- Fine-tuned CodeBERT or similar model
- Training infrastructure

---

### FR-5: Controlled Complexity Class Dataset

**Requirement:** Synthetic problems with labeled algorithmic complexity for Cohen's d testing

**Specifications:**
- **Problems:** 50 synthetic programming tasks
- **Complexity Labels:** O(n), O(n log n), O(n²)
- **Distribution:** ~17 problems per complexity class
- **Solutions:** 3 canonical implementations per problem (one per complexity class)
- **Purpose:** Test inter-class separability (Cohen's d ≥ 0.8)

**Acceptance Criteria:**
- 50 synthetic problems generated programmatically
- Each problem has 3 labeled solution variants (O(n), O(n log n), O(n²))
- Complexity labels verified via asymptotic analysis
- All solutions are functionally correct (pass unit tests)

**Example Problem:**
```python
# Problem: Find sum of array elements
# O(n) solution: sum(arr)
# O(n log n) solution: sorted(arr); sum(sorted_arr)  [unnecessary sort]
# O(n²) solution: sum([arr[i] for _ in range(len(arr)) for i in range(len(arr))]) [nested loop]
```

**Dependencies:**
- Problem generation script
- Complexity verification via code inspection

---

### FR-6: Reliability Metrics Computation

**Requirement:** Compute statistical reliability metrics from repeated measurements

**Specifications:**

**Metric 1: Coefficient of Variation (CV)**
- Formula: `CV = (std_dev / mean) * 100`
- Applied to: 5 repeated measurements per solution
- Aggregation: Mean CV across all 500 solutions
- Threshold: ≤5% (success criterion)

**Metric 2: Cohen's d**
- Formula: `d = (mean₁ - mean₂) / pooled_std`
- Applied to: Controlled complexity class comparisons (O(n) vs O(n²))
- Purpose: Test inter-class separability
- Threshold: ≥0.8 (large effect size)

**Metric 3: Spearman Rank Correlation (ρ)**
- Formula: Rank correlation between two measurement sets
- Applied to: Same solutions measured on AWS GPU vs local GPU
- Purpose: Cross-hardware stability
- Threshold: ≥0.8 (strong correlation)

**Acceptance Criteria:**
- CV computed for each of 500 solutions (3 proxies × 500 = 1,500 CV values)
- Cohen's d computed for each proxy across complexity classes
- Spearman ρ computed for each proxy across hardware platforms
- All metrics saved with confidence intervals

**Dependencies:**
- `scipy.stats` for statistical functions
- `numpy` for numerical computation

---

### FR-7: Cross-Hardware Validation

**Requirement:** Validate measurement stability across hardware platforms

**Specifications:**
- **Platform 1:** AWS g4dn.xlarge (NVIDIA T4, 16GB VRAM)
- **Platform 2:** Local GPU (documented in experiment setup)
- **Measurements:** All 500 solutions measured on both platforms
- **Protocol:** Identical measurement procedure on both platforms

**Acceptance Criteria:**
- All 500 solutions evaluated on Platform 1
- All 500 solutions evaluated on Platform 2
- Rank orderings computed for both platforms
- Spearman ρ ≥ 0.8 for each proxy metric

**Dependencies:**
- Access to AWS EC2 instance
- Access to local GPU machine
- Identical Python environment on both platforms

---

### FR-8: Visualization System

**Requirement:** Generate figures for hypothesis validation reporting

**Required Figure (Mandatory):**
1. **Gate Metrics Bar Chart**
   - X-axis: 3 proxy metrics (CodeBLEU, Runtime, PR-style)
   - Y-axis: Metric values
   - 3 grouped bars per proxy: CV, Cohen's d, Spearman ρ
   - Horizontal threshold lines: 5%, 0.8, 0.8
   - Color coding: Green (pass) / Red (fail)

**Additional Figures (Autonomous LLM Choice):**
2. **CV Distribution Histogram**
   - 3 subplots (one per proxy)
   - X-axis: CV percentage bins
   - Y-axis: Frequency (out of 500 solutions)
   - Vertical line at 5% threshold

3. **Complexity Separation Violin Plot**
   - X-axis: Complexity classes (O(n), O(n log n), O(n²))
   - Y-axis: Metric value
   - 3 subplots (one per proxy)
   - Violin plots showing distributions

4. **Cross-Hardware Scatter Plot**
   - X-axis: AWS GPU rankings
   - Y-axis: Local GPU rankings
   - 3 subplots (one per proxy)
   - Diagonal reference line (perfect correlation)
   - Spearman ρ annotation

5. **Measurement Stability Line Plot**
   - X-axis: Measurement repetition (1-5)
   - Y-axis: Metric value
   - 5 sample solutions × 3 proxies = 15 lines
   - Demonstrates measurement noise level

**Acceptance Criteria:**
- All figures generated programmatically
- Saved to `{hypothesis_folder}/figures/` directory
- Publication-quality resolution (300 DPI)
- Clear axis labels and legends

**Dependencies:**
- `matplotlib` or `seaborn` for visualization
- Figure templates from `dataviz` skill

---

### FR-9: Dataset and Model Caching

**Requirement:** Cache downloaded datasets and models for reproducibility

**Specifications:**
- **HumanEval Dataset:** Cache to `./data/humaneval/`
- **CodeLlama Model:** Cache to `./models/codellama-7b-instruct/`
- **Model Format:** HuggingFace safetensors
- **Cache Validation:** Verify SHA256 checksums on load

**Acceptance Criteria:**
- First run downloads and caches datasets/models
- Subsequent runs use cached versions
- Cache paths configurable via config file
- Verification logging for cache hits

**Dependencies:**
- `huggingface_hub` for caching
- Sufficient disk space (~15GB for model + ~10MB for dataset)

---

### FR-10: Experiment Configuration System

**Requirement:** Centralized configuration for all experiment parameters

**Specifications:**
- **Format:** YAML configuration file
- **Location:** `{hypothesis_folder}/experiment_config.yaml`
- **Sections:**
  - Dataset (HumanEval selection, problem count)
  - Model (name, generation config)
  - Metrics (proxy configs, thresholds)
  - Hardware (platform specs)
  - Reproducibility (random seeds)

**Example Configuration:**
```yaml
dataset:
  name: "HumanEval"
  source: "openai/openai_humaneval"
  problem_count: 50
  problem_selection_seed: 42

model:
  name: "meta-llama/CodeLlama-7b-Instruct-hf"
  dtype: "float16"
  device_map: "auto"
  generation:
    temperature: 0.8
    top_p: 0.95
    max_new_tokens: 512
    num_solutions_per_problem: 10

metrics:
  codebleu:
    weights: [0.25, 0.25, 0.25, 0.25]
    lang: "python"
  runtime:
    tool: "perf"
    event: "instructions"
    repetitions: 5
  pr_style:
    implementation: "placeholder"

thresholds:
  cv_max: 5.0
  cohens_d_min: 0.8
  spearman_rho_min: 0.8

hardware:
  platform_1: "AWS g4dn.xlarge"
  platform_2: "Local GPU"

reproducibility:
  seed: 42
  deterministic: true
```

**Acceptance Criteria:**
- Config file loaded at experiment start
- All parameters read from config (no hardcoded values)
- Config validation (required fields present)
- Config saved alongside results for reproducibility

**Dependencies:**
- `pyyaml` for config parsing
- `pydantic` for validation (optional)

---

## Non-Functional Requirements

### NFR-1: Performance

**Requirement:** Complete full experiment within reasonable timeframe

**Specifications:**
- **Solution Generation:** ≤ 100 GPU hours total
  - 50 problems × 10 solutions × ~12 seconds per solution
- **Metric Computation:** ≤ 24 CPU hours total
  - CodeBLEU: ~30 seconds per solution × 500 = 4.2 hours
  - Runtime (perf): ~5 seconds per solution × 500 × 5 reps = 6.9 hours
  - PR-style (placeholder): Negligible
- **Total Runtime:** ~1-2 weeks (with parallel execution)

**Optimization Strategies:**
- Parallel solution generation (batch size=10)
- Multiprocessing for metric computation (workers=CPU cores)
- Cache intermediate results

---

### NFR-2: Reproducibility

**Requirement:** Experiment must be fully reproducible

**Specifications:**
- Fixed random seeds throughout (seed=42)
- Deterministic GPU operations (`torch.use_deterministic_algorithms(True)`)
- Versioned dependencies (`requirements.txt` with pinned versions)
- Documented hardware specifications
- Configuration file version control

**Acceptance Criteria:**
- Same random seed → identical generated solutions
- Same measurement input → identical metric values
- Results reproduce within ±0.1% on same hardware

---

### NFR-3: Fault Tolerance

**Requirement:** Handle failures gracefully without losing progress

**Specifications:**
- Checkpoint after each problem's solutions generated
- Resume from last checkpoint on crash
- Timeout handling (3s per solution execution)
- Invalid solution handling (syntax errors, runtime exceptions)

**Acceptance Criteria:**
- Experiment can resume after interruption
- Failed solutions logged but don't block progress
- Timeout solutions marked as failed, don't crash experiment

---

### NFR-4: Logging and Observability

**Requirement:** Comprehensive logging for debugging and verification

**Specifications:**
- **Log Levels:** DEBUG, INFO, WARNING, ERROR
- **Log Destinations:** 
  - Console (INFO+)
  - File `{hypothesis_folder}/experiment.log` (DEBUG+)
- **Logged Events:**
  - Solution generation (problem_id, temperature, token count)
  - Metric computation (metric_name, value, duration)
  - Checkpoint saves
  - Errors and exceptions

**Acceptance Criteria:**
- Full experiment traceable via logs
- Performance metrics logged (tokens/sec, metrics/sec)
- Error stack traces captured

---

### NFR-5: Resource Management

**Requirement:** Efficient use of GPU/CPU/memory resources

**Specifications:**
- **GPU Memory:** ≤ 14GB peak usage (leaves headroom on 16GB GPUs)
- **CPU Memory:** ≤ 32GB peak usage
- **Disk Space:** ≤ 50GB total (model cache + results)
- **Model Loading:** Load once, reuse across all 500 inferences

**Acceptance Criteria:**
- No out-of-memory errors on specified hardware
- GPU utilization > 80% during generation
- Model loaded once, not reloaded per solution

---

## Data Requirements

### DR-1: HumanEval Dataset

**Source:** `openai/openai_humaneval` (HuggingFace Datasets)  
**Size:** 164 problems total, 50 selected  
**Fields Required:** `task_id`, `prompt`, `canonical_solution`, `test`, `entry_point`  
**Selection:** Stratified random sampling (seed=42) to ensure diversity

**Verification:**
- Dataset SHA256 checksum validation
- All 164 problems loaded successfully
- Selected 50 problems cover difficulty range

---

### DR-2: Controlled Complexity Dataset

**Source:** Programmatically generated  
**Size:** 50 synthetic problems  
**Format:** Same as HumanEval (task_id, prompt, canonical_solution, test, entry_point)  
**Complexity Labels:** Verified via algorithmic analysis

**Verification:**
- All solutions functionally correct (pass unit tests)
- Complexity labels match asymptotic behavior
- No duplicate problems

---

### DR-3: Model Weights

**Source:** `meta-llama/CodeLlama-7b-Instruct-hf` (HuggingFace Hub)  
**Size:** ~13GB (FP16 format)  
**License:** Llama 2 Community License (requires acceptance)

**Verification:**
- Model SHA256 checksum validation
- Sample inference test (input: "def add(a, b):" → valid completion)
- Tokenizer compatibility verified

---

## Dependencies

### External Libraries

```txt
# Core ML
torch>=2.1.0
transformers>=4.35.0
accelerate>=0.24.0

# Datasets
datasets>=2.14.0
human-eval>=1.0.0

# Metrics
codebleu>=0.7.0
scipy>=1.11.0
numpy>=1.24.0

# Visualization
matplotlib>=3.7.0
seaborn>=0.12.0

# Configuration
pyyaml>=6.0
pydantic>=2.0.0  # Optional validation

# Logging
tqdm>=4.66.0
```

### System Requirements

**Hardware:**
- GPU: NVIDIA GPU with ≥16GB VRAM (e.g., T4, V100, A10)
- CPU: ≥8 cores (for parallel metric computation)
- RAM: ≥32GB
- Disk: ≥50GB free

**Software:**
- OS: Linux (Ubuntu 20.04+ or equivalent)
- Python: 3.9-3.11
- CUDA: 11.8+ (for PyTorch 2.1)
- Linux `perf` tool (for runtime measurements)

**Optional:**
- AWS EC2 access (for cross-hardware validation)
- Docker (for environment isolation)

---

## Success Metrics

### Primary Metrics (Gate Conditions)

| Metric | Threshold | Current Status | Pass Criteria |
|--------|-----------|----------------|---------------|
| Coefficient of Variation (CV) | ≤ 5% | TBD | Each proxy shows mean CV ≤ 5% |
| Cohen's d | ≥ 0.8 | TBD | Each proxy separates O(n) vs O(n²) with d ≥ 0.8 |
| Spearman ρ | ≥ 0.8 | TBD | Each proxy maintains ρ ≥ 0.8 cross-hardware |

### Experiment Completion Metrics

| Metric | Target | Description |
|--------|--------|-------------|
| Solutions Generated | 500 | 50 problems × 10 solutions |
| Total Measurements | 2,500 | 500 solutions × 5 repetitions |
| Proxies Validated | ≥ 1 | At least one proxy passes all 3 criteria |
| Controlled Tasks | 150 | 50 problems × 3 complexity variants |
| Cross-Hardware Runs | 1,000 | 500 solutions × 2 platforms |

---

## Risks and Mitigations

### Risk 1: Insufficient GPU Resources

**Impact:** Cannot complete 500 solution generations  
**Probability:** Medium  
**Mitigation:**
- Use smaller problem set (30 problems → 300 solutions)
- Reduce solutions per problem (5 instead of 10)
- Use cloud GPU (AWS g4dn.xlarge)

---

### Risk 2: Linux `perf` Unavailable

**Impact:** Cannot measure CPU instruction counts  
**Probability:** Low  
**Mitigation:**
- Fallback to wall-clock execution time
- Document increased measurement noise
- Use median of 10 runs instead of mean of 5

---

### Risk 3: PR-Style Metric Requires Training

**Impact:** Third proxy unavailable for PoC  
**Probability:** High (expected)  
**Mitigation:**
- Use placeholder returning random scores
- Document as future work
- Gate can pass with 2/3 proxies validated

---

### Risk 4: Low Measurement Stability (CV > 5%)

**Impact:** Proxies fail reliability criteria  
**Probability:** Medium  
**Mitigation:**
- Increase repetitions (5 → 10 measurements)
- Control for system load (isolated execution)
- Use CPU instruction count instead of wall-clock time

---

### Risk 5: Complexity Classes Overlap (Cohen's d < 0.8)

**Impact:** Proxies cannot discriminate algorithm quality  
**Probability:** Medium  
**Mitigation:**
- Use more extreme complexity gaps (O(n) vs O(n³))
- Verify controlled task implementations
- Test on larger input sizes (n=10,000)

---

## Timeline Estimate

**Phase 3 (Current):** Implementation Planning - 1-2 days  
**Phase 4:** PoC Implementation - 1-2 weeks  
**Phase 4 (Validation):** Measurement + Analysis - 1-2 weeks  

**Total:** 2-4 weeks from Phase 3 start to validated results

---

## Appendix: Reference Implementations

### HumanEval Evaluation
- **Repository:** openai/human-eval
- **URL:** https://github.com/openai/human-eval
- **Key Functions:** `read_problems()`, `check_correctness()`, `estimate_pass_at_k()`

### CodeBLEU Metric
- **Repository:** k4black/codebleu
- **URL:** https://github.com/k4black/codebleu
- **PyPI:** `pip install codebleu`
- **Key Functions:** `calc_codebleu(references, predictions, lang, weights)`

### Runtime Efficiency
- **Paper:** COFFE (2025) - "A Code Efficiency Benchmark for Code Generation"
- **Method:** CPU instruction count via Linux `perf`
- **Command:** `perf stat -e instructions <program>`

### Statistical Analysis
- **Library:** scipy.stats
- **Functions:** 
  - `np.std(values) / np.mean(values)` (CV)
  - Custom Cohen's d implementation
  - `scipy.stats.spearmanr(ranks1, ranks2)` (Spearman ρ)

---

**Document Status:** Ready for Phase 3 Architecture Planning  
**Next Step:** Generate Architecture Document (03_architecture.md)  
**Approval:** Pending Phase 3 completion
