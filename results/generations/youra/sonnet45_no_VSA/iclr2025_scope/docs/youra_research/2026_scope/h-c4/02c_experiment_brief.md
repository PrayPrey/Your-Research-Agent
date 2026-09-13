# Phase 2C Experiment Design Brief: H-C4

**Hypothesis ID:** h-c4  
**Hypothesis Type:** CONDITION  
**Hypothesis Statement:** Contracts remain stable across ±2 minor library versions with false positive rate <5%

**Date:** 2026-07-11  
**Phase:** 2C - Experiment Design  
**Prerequisites:** h-m1 (VALIDATED), h-m2 (VALIDATED)

---

## 1. Research Context

### 1.1 Background from Prerequisites

**h-m1 (Structural Contracts):**
- **Mechanism:** Import-time validation of structural invariants (shapes, dtypes, non-null outputs)
- **Detection Rate:** 100% (2/2 structural defects)
- **Coverage:** Shape mismatches, dtype inconsistencies
- **Execution Time:** <0.03s per test
- **Limitation:** Tested only on single library version (no cross-version validation)

**h-m2 (Metamorphic Contracts):**
- **Mechanism:** Lightweight probes for mathematical invariants (softmax sums, dropout identity)
- **Detection Rate:** 100% (2/2 metamorphic violations)
- **Coverage:** Mathematical property violations
- **Execution Time:** <0.05s per test
- **Limitation:** Version stability not validated

### 1.2 Hypothesis Rationale

**Version Stability Challenge:**  
API contracts designed for a specific library version (e.g., PyTorch 2.1.0) may become **brittle** across version updates:
- **API evolution:** Minor version updates can introduce subtle behavioral changes despite semantic versioning guarantees
- **False positives:** Contracts that flag valid code as violations reduce adoption (developer fatigue)
- **Maintenance burden:** Version-specific contracts require constant updates, limiting reusability
- **Trust erosion:** High false positive rates undermine confidence in contract-based validation

**Problem:** If contracts exhibit high false positive rates (>5%) across minor version transitions, the approach becomes **impractical for production use** despite high detection rates in single-version scenarios.

**Expected Impact:** Demonstrating version-stable contracts (FPR <5% across ±2 minor versions) validates that the contract approach is **sustainable** and **production-ready**, not just a single-version proof-of-concept.

### 1.3 Literature & Implementation Patterns

**From Archon KB & Research:**

1. **Semantic Versioning in Practice (MSR 2020)** [doi:10.1145/3379597.3387491]:
   - Analyzed 22,029 Python packages on PyPI
   - **31% of "backward-compatible" updates** introduce breaking changes
   - Major finding: Minor version updates violate SemVer contracts in practice
   - Gap: No systematic measurement of contract brittleness across versions

2. **Breaking Bad: Semantic Versioning in the Wild (ICSE 2018)** [doi:10.1145/3183399.3183434]:
   - JavaScript npm ecosystem: **17% of minor updates** break dependent packages
   - Root cause: Implicit behavioral assumptions not captured in API signatures
   - Pattern: **Behavioral invariants** (not just signatures) change across versions

3. **PyTorch Release Notes Analysis (2019-2024)**:
   - Examined minor version updates (2.0 → 2.1 → 2.2 → 2.3)
   - **Deprecated APIs:** Gradual removal (warnings → errors) across 2-3 minor versions
   - **Behavioral changes:** Operator optimizations (e.g., `torch.matmul` kernel changes) preserve semantics but alter numerical precision
   - **New defaults:** Parameter defaults change (e.g., `torch.optim.Adam` epsilon from 1e-8 to 1e-7 in PyTorch 1.13)
   - Pattern: **Mathematical invariants** (softmax sum=1) remain stable, **numerical tolerances** may drift

4. **HuggingFace Transformers Versioning** [GitHub]:
   - Model checkpoint compatibility across versions
   - **Config schema evolution:** New fields added with backward-compatible defaults
   - **Tokenizer changes:** Unicode normalization behavior (v4.18 → v4.19)
   - Pattern: **Structural contracts** (tensor shapes, return types) stable, **tokenizer contracts** version-sensitive

5. **TensorFlow API Stability Guarantees** [TF Documentation]:
   - Guarantees: No breaking changes in patch versions (2.13.0 → 2.13.1)
   - Minor versions (2.13 → 2.14): Deprecations allowed, removals prohibited
   - Observation: **Shape contracts** highly stable, **dtype defaults** occasionally change (e.g., mixed precision training defaults)

6. **Contract-Based Testing in Eiffel** (Meyer, 1992):
   - Classic design-by-contract: Preconditions, postconditions, invariants
   - Versioning challenge: **Abstract invariants** (mathematical properties) outlive **concrete implementations** (specific algorithms)
   - Principle: Version-stable contracts must abstract over implementation details

7. **API Evolution Mining (ASE 2019)** [doi:10.1109/ASE.2019.00025]:
   - Mined 1,000+ libraries for API evolution patterns
   - **Monotonic APIs:** Add-only changes (new parameters with defaults) → highly stable
   - **Polymorphic APIs:** Overload variants → moderate stability
   - **Behavioral APIs:** Implicit contracts on computation → low stability
   - Insight: **Structural contracts** align with monotonic patterns (high stability)

### 1.4 Gap Analysis

**Existing Approaches:**
- **SemVer reliance:** Assumes minor versions are backward-compatible (violated 17-31% of the time)
- **Version pinning:** Avoids breakage but prevents security updates and new features
- **Integration testing:** Catches regressions but doesn't isolate contract brittleness
- **Deprecation warnings:** Reactive (post-deployment), not proactive (pre-deployment)

**H-C4 Novelty:**
- **Proactive contract stability testing:** Validates contracts across version transitions **before deployment**
- **Quantified false positive rate:** Measures developer friction (FPR <5% threshold)
- **Version-Transition Benchmark:** Systematic evaluation across ±2 minor versions (6 version pairs per library)
- **Contract taxonomy:** Stratifies stability by contract type (structural vs metamorphic vs composition)

**Research Gap:** No prior work systematically measures **contract false positive rates** across library version transitions in ML ecosystem.

---

## 2. Experiment Design

### 2.1 Research Question

**Primary RQ:** Do structural and metamorphic contracts remain stable across ±2 minor library versions with false positive rate <5%?

**Sub-Questions:**
- RQ1: Which contract types exhibit highest version stability (structural vs metamorphic)?
- RQ2: Which libraries have highest contract brittleness (PyTorch vs HuggingFace vs NumPy)?
- RQ3: What types of version changes cause false positives (API deprecations vs behavioral changes vs numerical drift)?

### 2.2 Variables

| Variable | Type | Definition | Measurement |
|----------|------|------------|-------------|
| **Library Version Pair** | Independent | Source → Target version (e.g., PyTorch 2.1 → 2.3) | {torch 2.1→2.2, 2.1→2.3, 2.2→2.3, 2.2→2.1, ...} |
| **Contract Type** | Independent | Category of contract | {Structural, Metamorphic, Composition} |
| **False Positive Rate** | Dependent | % of valid code flagged as violations | (False Positives) / (Valid Code) |
| **Contract Stability** | Dependent | % of contracts passing across versions | (Stable Contracts) / (Total Contracts) |
| **Breakage Type** | Dependent | Root cause of false positives | {API Deprecation, Behavioral Change, Numerical Drift, None} |

**Controlled Variables:**
- Code corpus: 1000 valid ML scripts (no injected defects)
- Model architectures: ResNet-18, BERT-base
- Test environment: Python 3.10, CUDA 12.1 (consistent across all versions)

### 2.3 Experimental Conditions

**Version-Transition Benchmark:**

**PyTorch versions:**
- 2.1.0 (baseline), 2.1.2 (patch), 2.2.0 (minor), 2.2.2 (patch), 2.3.0 (minor), 2.3.1 (patch)
- Pairs tested: 2.1→2.2 (1 minor), 2.1→2.3 (2 minors), 2.2→2.3 (1 minor), 2.3→2.2 (rollback), 2.1→2.1.2 (patch control)

**HuggingFace Transformers versions:**
- 4.35.0, 4.36.0, 4.37.0, 4.38.0 (4 consecutive minors)
- Pairs tested: 4.35→4.36 (1 minor), 4.35→4.37 (2 minors), 4.36→4.38 (2 minors), 4.37→4.36 (rollback)

**NumPy versions (dtype contract stability):**
- 1.24.0, 1.25.0, 1.26.0 (3 consecutive minors)
- Pairs tested: 1.24→1.25 (1 minor), 1.24→1.26 (2 minors), 1.25→1.24 (rollback)

**Contract Implementation:**

1. **Structural Contracts (from h-m1):**
   ```python
   @validate_structural
   def forward(self, x: torch.Tensor) -> torch.Tensor:
       """Shape: (B, C_in, H, W) -> (B, C_out, H', W')"""
       return self.conv(x)
   ```

2. **Metamorphic Contracts (from h-m2):**
   ```python
   @validate_metamorphic(property="softmax_sums_to_one", tolerance=1e-6)
   def attention(self, query, key, value):
       weights = torch.softmax(query @ key.T / sqrt(d_k), dim=-1)
       return weights @ value
   ```

3. **Version-Agnostic Contract Design Patterns:**
   - **Abstract over implementation:** Check mathematical properties (sum=1), not internal state
   - **Tolerance bands:** Use numerical tolerances (1e-6) instead of exact equality
   - **Semantic equivalence:** Validate output shapes, not intermediate layer counts
   - **Graceful degradation:** Warn on minor violations, error only on critical failures

### 2.4 Dataset Preparation

**Dataset Type:** Real-world ML code corpus (valid code, no defects)

**Dataset Composition:**

1. **PyTorch Hub Models** (N=200 scripts):
   - Source: Official PyTorch Hub repository (torchvision.models.*)
   - Scripts: ResNet, VGG, DenseNet, EfficientNet (pretrained model loading + inference)
   - Use: Structural contract stability testing

2. **HuggingFace Model Examples** (N=300 scripts):
   - Source: HuggingFace Transformers examples/ directory
   - Scripts: BERT, GPT-2, T5 (fine-tuning, inference, tokenization)
   - Use: Metamorphic contract stability testing (attention, layer norms)

3. **GitHub ML Scripts** (N=500 scripts):
   - Source: High-quality repos (≥1K stars, active maintenance)
   - Selection criteria: No warnings/errors on latest version, ≥10 GitHub stars
   - Filtering: Remove deprecated API usage, syntax errors, missing dependencies
   - Use: Broad coverage across contract types

**Data Preparation Steps:**
1. Clone PyTorch Hub and HuggingFace repos (small size, <5 GB total)
2. Extract valid Python scripts (exclude tests, setup.py, docs)
3. Filter for importable scripts (no syntax errors, resolvable dependencies)
4. Annotate contract points: Identify functions/methods for contract injection
5. **Version matrix:** Run each script on all 6 PyTorch versions × 4 HF versions (24 combinations per script)
6. Label outcomes: {Pass, False Positive (contract failed but code valid), True Negative}

**Dataset Accessibility:**
- PyTorch Hub: Public repository, ~500 MB
- HuggingFace examples: Public repository, ~200 MB
- GitHub scripts: Manual curation from public repos
- **Total storage:** <10 GB (no large datasets required)

**Synthetic Data Policy:** This experiment uses **REAL CODE** from production repositories, not synthetic data. The focus is on measuring false positive rates on **valid, working code** across version transitions.

### 2.5 Baseline Methods

| Method | Description | Expected FPR | Rationale |
|--------|-------------|--------------|-----------|
| **Version Pinning** | Fix library versions (no updates) | 0% | No version changes → no false positives (control) |
| **No Contracts** | Direct version upgrade, no validation | N/A | No contracts → no false positives (trivial baseline) |
| **Deprecation Warnings** | Rely on library-provided warnings | 2-5% | Standard practice, but reactive |
| **Full Test Suite** | Run integration tests on each version | 10-20% | Catches breakage but high maintenance |

**Hypothesis:** Contracts should match **Deprecation Warnings** baseline (2-5% FPR) to be practical.

### 2.6 Success Criteria

| Criterion | Threshold | Rationale |
|-----------|-----------|-----------|
| **False Positive Rate** | <5% | Low enough to avoid developer fatigue (primary metric) |
| **Contract Stability** | ≥90% | Most contracts should remain valid across versions |
| **Structural Contract FPR** | <3% | Structural invariants most stable (tightest bound) |
| **Metamorphic Contract FPR** | <8% | Numerical tolerances may drift slightly (relaxed bound) |
| **Version Distance Sensitivity** | FPR(±1 minor) ≤ FPR(±2 minors) | More distant versions → higher FPR (monotonic) |

**Gate Type:** MUST_WORK (from pipeline state)
- **PASS:** Overall FPR <5%, structural FPR <3%
- **PARTIAL PASS:** Overall FPR 5-8% (needs threshold tuning, but viable)
- **FAIL:** Overall FPR >8% (contracts too brittle for production)

---

## 3. Implementation Plan

### 3.1 Contract Framework Extensions

**Module Structure:**
```
version_stable_contracts/
├── __init__.py
├── version_adapter.py          # Multi-version environment manager
├── contract_validator.py        # Extended from h-m1/h-m2
├── false_positive_tracker.py    # FPR measurement
├── stability_analyzer.py        # Version-specific breakage analysis
└── test_corpus/
    ├── pytorch_hub/             # PyTorch Hub models
    ├── huggingface_examples/    # HF Transformers examples
    └── github_scripts/          # Curated GitHub repos
```

**Key Components:**

1. **Version Adapter:** Manages isolated environments per library version
   - Use `virtualenv` or `conda` to create version-specific environments
   - Install library versions from PyPI/conda-forge
   - Run contracts in isolated environments, capture outcomes

2. **False Positive Tracker:** Logs contract violations on valid code
   - Ground truth: Code runs successfully without contracts
   - False positive: Contract flags violation but code executes correctly
   - Categorize FP causes: API deprecation, behavioral change, numerical drift

3. **Stability Analyzer:** Root cause analysis for false positives
   - Extract library release notes for version pairs
   - Map contract failures to documented API changes
   - Identify contract design patterns prone to brittleness

### 3.2 Experimental Workflow

**Phase 1: Environment Setup (2 days)**
1. Create isolated environments for each library version
2. Install PyTorch {2.1.0, 2.1.2, 2.2.0, 2.2.2, 2.3.0, 2.3.1}
3. Install HuggingFace Transformers {4.35.0, 4.36.0, 4.37.0, 4.38.0}
4. Install NumPy {1.24.0, 1.25.0, 1.26.0}
5. Verify environments (test imports, basic inference)

**Phase 2: Corpus Collection (2 days)**
1. Clone PyTorch Hub, HuggingFace examples
2. Curate 500 GitHub scripts (high-quality, active repos)
3. Filter for importable scripts (syntax validation)
4. Annotate contract injection points (function signatures, layer definitions)

**Phase 3: Contract Injection (1 day)**
1. Apply structural contracts to 200 PyTorch Hub scripts
2. Apply metamorphic contracts to 300 HuggingFace scripts
3. Apply mixed contracts to 500 GitHub scripts
4. Total: 1000 scripts × ~3 contracts/script = 3000 contract instances

**Phase 4: Version-Transition Testing (3 days)**
1. For each script, run on **source version** (baseline):
   - Record: {script_id, version, contract_id, outcome: pass/fail}
2. For each script, run on **target version** (transition):
   - Record: {script_id, version, contract_id, outcome: pass/fail}
3. Compare outcomes: If baseline=pass AND target=fail → **False Positive**
4. Run across all version pairs (5 PyTorch pairs × 4 HF pairs × 3 NumPy pairs = 12 pairs)

**Phase 5: False Positive Analysis (2 days)**
1. Compute FPR per contract type (structural, metamorphic)
2. Compute FPR per library (PyTorch, HuggingFace, NumPy)
3. Compute FPR per version distance (±1 minor, ±2 minors)
4. Root cause analysis: Map FPs to library release notes (API changes, deprecations)

**Phase 6: Reporting (1 day)**
1. Generate metrics tables (FPR, stability, breakage types)
2. Visualize FPR by version pair (heatmap)
3. Identify contract design patterns for high stability
4. Write validation report (04_validation.md)

### 3.3 Computational Requirements

**Hardware:**
- **CPU:** 8 cores (parallel environment testing)
- **RAM:** 16 GB (multiple conda environments)
- **Storage:** 20 GB (10 GB corpus + 5 GB per-version envs + 5 GB logs)
- **GPU:** Optional (most tests are import-time validation, no training)

**Software:**
- Python 3.10
- Conda/virtualenv for environment isolation
- PyTorch {2.1.0, 2.1.2, 2.2.0, 2.2.2, 2.3.0, 2.3.1}
- HuggingFace Transformers {4.35.0, 4.36.0, 4.37.0, 4.38.0}
- NumPy {1.24.0, 1.25.0, 1.26.0}

**Estimated Runtime:**
- Environment setup: 4 hours (6 PyTorch + 4 HF + 3 NumPy = 13 environments)
- Corpus collection: 8 hours (manual curation of GitHub scripts)
- Contract injection: 4 hours (semi-automated annotation)
- Version-transition testing: 24 hours (1000 scripts × 12 version pairs × ~7s/script)
- False positive analysis: 8 hours (manual review of FP causes)
- **Total: ~48 hours (~1 week with parallelization)**

---

## 4. Metrics & Analysis

### 4.1 Primary Metrics

1. **False Positive Rate (FPR):**
   ```
   FPR = (False Positives) / (True Negatives + False Positives)
   ```
   - False Positive: Contract fails on valid code (baseline version passes, target version fails)
   - True Negative: Contract passes on valid code (both versions pass)
   - Computed per: contract type, library, version distance

2. **Contract Stability:**
   ```
   Stability = (Stable Contracts) / (Total Contracts)
   ```
   - Stable Contract: Same outcome (pass/fail) across source and target versions
   - Aggregated across all version pairs

3. **Version Distance Sensitivity:**
   ```
   Sensitivity = FPR(±2 minors) - FPR(±1 minor)
   ```
   - Positive sensitivity: FPR increases with version distance (expected)
   - Negative sensitivity: FPR decreases (unexpected, investigate)

### 4.2 Secondary Metrics

1. **Breakage Type Distribution:**
   - API Deprecation: Contract references removed/deprecated API (e.g., `torch.nn.functional.softmax(dim=None)` → requires `dim`)
   - Behavioral Change: API semantics change (e.g., default parameter values)
   - Numerical Drift: Floating-point precision changes (e.g., kernel optimizations)
   - None: False positive without clear root cause (contract design issue)

2. **Library Brittleness Ranking:**
   - Rank libraries by FPR: PyTorch vs HuggingFace vs NumPy
   - Identify high-risk libraries for contract maintenance

3. **Contract Type Stability Ranking:**
   - Rank contract types by stability: Structural vs Metamorphic vs Composition
   - Inform future contract design (prioritize stable patterns)

### 4.3 Statistical Analysis

**Hypothesis Testing:**
- **H0:** FPR ≥ 5% (contracts too brittle)
- **H1:** FPR < 5% (contracts sufficiently stable, one-tailed test)
- **Test:** Binomial proportion test (FPR is a proportion)
- **Significance level:** α = 0.05

**Confidence Intervals:**
- 95% CI for FPR using Wilson score interval (better for proportions near 0)
- Bootstrap resampling (1000 iterations) for contract stability CI

**Effect Size:**
- Compute FPR difference between contract types (structural vs metamorphic)
- Cohen's h for proportion differences (small: h<0.2, medium: 0.2≤h<0.5, large: h≥0.5)

**Stratification:**
- FPR by library: PyTorch, HuggingFace, NumPy
- FPR by version distance: ±1 minor, ±2 minors, rollback (target < source)
- FPR by contract type: Structural, Metamorphic

---

## 5. Expected Outcomes

### 5.1 Quantitative Predictions

| Metric | Threshold | Expected | Confidence |
|--------|-----------|----------|------------|
| **Overall FPR** | <5% | 3.2% | 0.75 |
| **Structural FPR** | <3% | 1.8% | 0.80 |
| **Metamorphic FPR** | <8% | 5.5% | 0.70 |
| **Contract Stability** | ≥90% | 94% | 0.75 |
| **PyTorch FPR** | <5% | 2.5% | 0.70 |
| **HuggingFace FPR** | <5% | 4.0% | 0.65 |

### 5.2 Qualitative Insights

**Expected Findings:**
1. **Structural contracts** exhibit highest stability (FPR ~2%) because:
   - Shape invariants rarely change across minor versions
   - Dtype defaults occasionally change but are detectable via release notes

2. **Metamorphic contracts** have moderate stability (FPR ~5%) due to:
   - Numerical tolerance drift (kernel optimizations, cuDNN versions)
   - Precision changes in mixed-precision training (float16 vs bfloat16 defaults)

3. **Version distance** correlates with FPR:
   - ±1 minor: FPR ~2.5%
   - ±2 minors: FPR ~4.5%
   - Rollback: FPR ~1.5% (older versions more stable)

4. **Breakage type distribution**:
   - API Deprecation: 40% of false positives (detectable via warnings)
   - Behavioral Change: 30% (parameter defaults, optimizations)
   - Numerical Drift: 20% (tolerance tuning needed)
   - None: 10% (contract design issues)

**Failure Modes:**
- **Aggressive contracts:** Overly strict numerical tolerances (1e-8) may flag expected float32 drift
- **Deprecated APIs:** Contracts referencing deprecated APIs require update cycles
- **Framework internals:** Contracts inspecting internal state (e.g., `model._buffers`) break on refactoring

### 5.3 Contract Design Recommendations

**High-Stability Patterns:**
1. **Abstract over implementation:** Check public API behavior, not internal state
2. **Tolerance bands:** Use generous numerical tolerances (1e-5 for float32)
3. **Semantic equivalence:** Validate output properties, not intermediate layer structure
4. **Version-aware contracts:** Conditional logic based on library version (e.g., `if torch.__version__ >= "2.2"`)

**Low-Stability Anti-Patterns:**
1. **Exact numerical equality:** Fragile to kernel optimizations
2. **Internal state inspection:** Breaks on refactoring (e.g., `_buffers`, `_modules`)
3. **Deprecated API usage:** Contracts must update with library deprecation cycles

### 5.4 Validation Report Structure

**Output File:** `docs/youra_research/h-c4/04_validation.md`

**Contents:**
1. **Executive Summary:** Pass/Partial/Fail + FPR metrics
2. **Methodology:** Corpus, version matrix, contract injection
3. **Results:**
   - FPR table (overall + stratified by library/type/distance)
   - Stability heatmap (version pair × contract type)
   - Breakage type distribution
4. **Statistical Analysis:** Hypothesis test, CIs, effect sizes
5. **False Positive Case Studies:** 10 representative FPs with root cause analysis
6. **Contract Design Guidelines:** High-stability patterns, anti-patterns
7. **Recommendations:** Threshold tuning, version-aware contracts, maintenance strategies

---

## 6. Risk Assessment & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| **High FPR (>8%)** | Medium | Critical | Tune numerical tolerances, add version-aware logic |
| **Environment conflicts** | High | Medium | Use isolated conda environments per version |
| **GitHub script curation time** | High | Low | Reduce corpus to 300 scripts if needed (still statistically valid) |
| **Library installation failures** | Medium | Medium | Use conda-forge for older versions, document installation issues |
| **Numerical drift across CUDA versions** | Medium | Medium | Fix CUDA version (12.1) across all PyTorch versions |
| **Contract injection annotation errors** | Low | High | Manual review of 10% sample, automated validation |

---

## 7. Connections to Main Hypothesis

**Main Hypothesis:** API contracts reduce environment-stage defects by ≥30%

**H-C4 Contribution:**
- **Scope:** Version stability validation (prerequisite for production deployment)
- **Mechanism:** Ensures contracts remain usable across library updates (no excessive maintenance)
- **Evidence:** If FPR <5%, contracts are **practical** for long-term use (not brittle prototypes)
- **Limitation:** Focuses on false positives (developer friction), not true positives (defect detection)

**Dependency Chain:**
- **h-m1** (structural) → **h-m2** (metamorphic) → **h-c4** (version stability)
- H-C4 validates that mechanisms from h-m1/h-m2 are **sustainable** across version updates
- Without H-C4 passing, contracts may work in single-version PoCs but fail in production (version drift)

**Gate Decision Impact:**
- **PASS (FPR <5%):** Contracts ready for production deployment, proceed to h-m4 (lifecycle shift)
- **PARTIAL PASS (FPR 5-8%):** Contracts viable but need threshold tuning (document limitations)
- **FAIL (FPR >8%):** Contracts too brittle → PIVOT to version-pinned contracts (sacrifices cross-version reusability)

---

## 8. References

1. **Semantic Versioning in Practice:** Decan et al. (2020). MSR. doi:10.1145/3379597.3387491
2. **Breaking Bad in npm:** Businge et al. (2018). ICSE. doi:10.1145/3183399.3183434
3. **PyTorch Release Notes:** https://pytorch.org/docs/stable/notes/
4. **HuggingFace Transformers Releases:** https://github.com/huggingface/transformers/releases
5. **TensorFlow API Stability:** https://www.tensorflow.org/guide/versions
6. **Design by Contract:** Meyer (1992). Eiffel: The Language
7. **API Evolution Mining:** Brito et al. (2019). ASE. doi:10.1109/ASE.2019.00025

---

## 9. Appendices

### A. Version Matrix

**PyTorch Version Pairs:**
| Source | Target | Distance | Type |
|--------|--------|----------|------|
| 2.1.0 | 2.2.0 | +1 minor | Forward |
| 2.1.0 | 2.3.0 | +2 minors | Forward |
| 2.2.0 | 2.3.0 | +1 minor | Forward |
| 2.3.0 | 2.2.0 | -1 minor | Rollback |
| 2.1.0 | 2.1.2 | +2 patches | Patch (control) |

**HuggingFace Transformers Version Pairs:**
| Source | Target | Distance | Type |
|--------|--------|----------|------|
| 4.35.0 | 4.36.0 | +1 minor | Forward |
| 4.35.0 | 4.37.0 | +2 minors | Forward |
| 4.36.0 | 4.38.0 | +2 minors | Forward |
| 4.37.0 | 4.36.0 | -1 minor | Rollback |

**NumPy Version Pairs:**
| Source | Target | Distance | Type |
|--------|--------|----------|------|
| 1.24.0 | 1.25.0 | +1 minor | Forward |
| 1.24.0 | 1.26.0 | +2 minors | Forward |
| 1.25.0 | 1.24.0 | -1 minor | Rollback |

### B. Contract Annotation Example

**Before (vanilla PyTorch):**
```python
class ResNet(nn.Module):
    def forward(self, x):
        return self.layer4(self.layer3(self.layer2(self.layer1(self.conv1(x)))))
```

**After (with contracts):**
```python
class ResNet(nn.Module):
    @validate_structural(input_shape="(B, 3, 224, 224)", output_shape="(B, 1000)")
    @validate_metamorphic(property="output_sum_positive")
    def forward(self, x):
        return self.layer4(self.layer3(self.layer2(self.layer1(self.conv1(x)))))
```

### C. False Positive Categorization Schema

| Category | Definition | Example |
|----------|------------|---------|
| **API Deprecation** | Contract references removed/deprecated API | `torch.nn.functional.softmax(x)` → requires `dim` parameter in 2.2+ |
| **Behavioral Change** | API semantics changed | `torch.optim.Adam(eps=1e-8)` default → `eps=1e-7` in later versions |
| **Numerical Drift** | Floating-point precision changes | cuDNN kernel optimization changes matmul output by 1e-7 |
| **Contract Design Error** | Overly strict contract (not library issue) | Tolerance 1e-10 flags expected float32 rounding |

---

**Experiment Design Status:** COMPLETED  
**Next Phase:** Phase 3 - Implementation Planning  
**Estimated Duration:** 1 week  
**Resource Requirements:** 8 cores, 16 GB RAM, 20 GB storage
