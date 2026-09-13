# Product Requirements Document: h-e1 CCP Domain Degradation Experiment

**Date:** 2026-07-09
**Author:** Anonymous
**Hypothesis:** ρ_j (claim-type mass ratio) degrades by >0.15 when CCP is applied to creative text vs factual text
**Phase:** Phase 3 - Implementation Planning
**Document Type:** PRD (Product Requirements Document)

---

## Executive Summary

### Problem Statement

The Constrained Category Probability (CCP) method for hallucination detection makes implicit ontological assumptions about text structure that may not hold across all domains. Specifically, CCP's ρ_j metric (claim-type mass ratio) may degrade when applied to creative text (metaphorical, speculative content) compared to factual text (verifiable claims). This hypothesis (h-e1) seeks empirical evidence of domain-specific degradation with a threshold of Δρ_j > 0.15.

### Objective

Implement a proof-of-concept (PoC) experiment to:
1. Measure ρ_j metric on factual domain (TruthfulQA)
2. Measure ρ_j metric on creative domain (WritingPrompts)
3. Compute degradation Δρ_j and validate against threshold
4. Establish measurement reliability through claim decomposition agreement

### Success Criteria

**MUST_WORK Gate (1/9):**
- ✅ Code executes without errors on both datasets
- ✅ ρ_j(creative) > ρ_j(factual) (direction correct)
- ✅ Δρ_j > 0.15 (magnitude threshold met)
- ✅ Lag-1 autocorrelation(creative) > 0.4
- ✅ Lag-1 autocorrelation(factual) < 0.2
- ✅ Krippendorff's α > 0.7 (claim decomposition reliability)

**Outputs:**
- Validation report with ρ_j measurements
- Figures: domain comparison, NLI distribution heatmap, autocorrelation plot
- Statistical analysis of degradation significance

---

## Functional Requirements

### FR-1: Dataset Loading and Preprocessing

**FR-1.1: TruthfulQA Dataset (Factual Domain)**
- Load from HuggingFace: `truthfulqa/truthful_qa` (generation subset)
- Access validation split: 817 questions
- Extract fields: `question`, `best_answer`, `correct_answers`
- Preprocessing: NLTK sentence tokenization for claim extraction
- Purpose: Factual text baseline for ρ_j measurement

**FR-1.2: WritingPrompts Dataset (Creative Domain)**
- Load from HuggingFace: `euclaise/writingprompts`
- Subsample training split to ~817 examples (match TruthfulQA size)
- Extract fields: `prompt`, `story`
- Preprocessing: NLTK sentence tokenization for claim extraction
- Filter: Select stories with metaphorical/speculative content (exclude purely factual)
- Purpose: Creative text domain to test ρ_j degradation

**FR-1.3: Data Validation**
- Verify sample counts: TruthfulQA = 817, WritingPrompts ≈ 817
- Check for null/empty text entries
- Log dataset statistics: mean text length, claim count distribution

### FR-2: NLI Model Setup

**FR-2.1: DeBERTa-v3-base NLI Model**
- Load from HuggingFace: `cross-encoder/nli-deberta-v3-base`
- Framework: sentence-transformers (CrossEncoder API)
- Configuration:
  - Max sequence length: 512 tokens
  - Batch size: 16-32 (based on GPU memory)
  - Device: CUDA (A100 40GB)
  - Precision: FP32 (no quantization)
- Output: 3-class logits [contradiction, entailment, neutral]
- Benchmarks: SNLI 92.38%, MNLI 90.04%

**FR-2.2: Model Inference Pipeline**
- Input: (context, claim) pairs from claim decomposition
- Processing: Batch NLI inference with progress tracking
- Output: Probability scores for each claim-context pair
- Error handling: Retry on CUDA OOM, log failed inferences

### FR-3: CCP ρ_j Metric Computation

**FR-3.1: Claim Decomposition**
- Method: NLTK sentence tokenizer (`nltk.sent_tokenize`)
- Fallback: Spacy sentence segmentation if NLTK fails
- Max claims per response: 20 (truncate longer texts)
- Validation: Log claim count distribution per domain

**FR-3.2: ρ_j Calculation**
- Formula: `median((entail_mass + contradict_mass) / total_mass)`
- Per-sample computation:
  - Extract NLI scores for all claims in sample
  - Compute entailment + contradiction mass
  - Normalize by total mass (sum of all class probabilities)
  - Take median across all claims in sample
- Aggregate: Compute median ρ_j across all samples in domain

**FR-3.3: Degradation Measurement**
- Compute: `Δρ_j = ρ_j(creative) - ρ_j(factual)`
- Statistical test: Wilcoxon rank-sum test for significance
- Threshold check: `Δρ_j > 0.15`
- Report: p-value, effect size, confidence intervals

### FR-4: Secondary Metrics

**FR-4.1: Lag-1 Autocorrelation**
- Compute: Pearson correlation between consecutive CCP scores within claims
- Per-domain analysis: factual vs creative
- Expected: autocorr(creative) > 0.4, autocorr(factual) < 0.2
- Implementation: `scipy.stats.pearsonr(scores[:-1], scores[1:])`

**FR-4.2: Claim Decomposition Reliability**
- Metric: Krippendorff's α
- Method: Sample 100 texts, decompose twice with different random seeds
- Agreement measure: Inter-annotator agreement for claim boundaries
- Threshold: α > 0.7 (ensures measurement reliability)
- Library: `krippendorff` Python package

**FR-4.3: Diversity Metrics (Diagnostic)**
- Self-BLEU: Measure repetitiveness within generated claims
- Embedding dispersion: Variance of claim embeddings
- Purpose: Ensure claim diversity is not confounding factor

### FR-5: Experiment Execution Pipeline

**FR-5.1: Execution Flow**
1. Load datasets (TruthfulQA, WritingPrompts)
2. Initialize NLI model (DeBERTa-v3-base)
3. Process factual domain:
   - Decompose claims for each sample
   - Run NLI inference (context, claim) pairs
   - Compute ρ_j per sample
4. Process creative domain: (same steps)
5. Compute secondary metrics (autocorrelation, reliability)
6. Statistical analysis (Δρ_j, significance tests)
7. Generate visualizations
8. Save results to validation report

**FR-5.2: Logging and Progress Tracking**
- Log level: INFO
- Track: Dataset loading, model initialization, batch processing progress
- Save: Intermediate results (per-sample ρ_j scores) to JSON
- Error logging: Failed inferences, CUDA errors, data validation issues

**FR-5.3: Reproducibility**
- Fixed random seeds: 42 (NumPy, PyTorch, Python random)
- Version pinning: transformers, sentence-transformers, datasets
- Environment: Python 3.9+, PyTorch 2.0+, CUDA 11.8+
- Save: Experiment config (seeds, versions, hyperparameters) to YAML

### FR-6: Visualization Generation

**FR-6.1: ρ_j Domain Comparison (Violin Plot)**
- X-axis: Domain (Factual, Creative)
- Y-axis: ρ_j values (per-sample distribution)
- Overlay: Median line, quartile markers
- Annotation: Δρ_j value, significance indicator
- Save: `figures/rho_j_distribution.png`

**FR-6.2: NLI Score Distribution Heatmap**
- Rows: Domains (Factual, Creative)
- Columns: NLI labels (Contradiction, Entailment, Neutral)
- Colors: Probability mass concentration (mean ± std)
- Colormap: Viridis
- Save: `figures/nli_distribution_heatmap.png`

**FR-6.3: Autocorrelation Comparison (Line Plot)**
- X-axis: Lag (0 to 10)
- Y-axis: Autocorrelation coefficient
- Lines: Factual (blue), Creative (red)
- Markers: Lag-1 values highlighted
- Save: `figures/autocorrelation_comparison.png`

**FR-6.4: Sample-level ρ_j Scatter**
- X-axis: Sample index (0-817)
- Y-axis: ρ_j value
- Colors: Domain (factual=blue, creative=orange)
- Purpose: Show per-sample variability
- Save: `figures/sample_rho_j_scatter.png`

### FR-7: Validation Report Generation

**FR-7.1: Report Structure**
- Sections:
  1. Executive Summary
  2. Gate Metrics (ρ_j, Δρ_j, autocorrelation, reliability)
  3. Statistical Analysis
  4. Visualizations (embedded figures)
  5. Limitations and Assumptions
  6. Recommendations for Next Steps
- Format: Markdown (.md)
- Save: `04_validation.md`

**FR-7.2: Gate Decision Logic**
- Check all success criteria (6 conditions)
- Gate status: SATISFIED if all pass, FAILED otherwise
- Report: List passed/failed criteria with values
- Update: verification_state.yaml with gate.satisfied field

---

## Non-Functional Requirements

### NFR-1: Performance

**NFR-1.1: Execution Time**
- Target: < 30 minutes total on A100 40GB GPU
- Breakdown:
  - Dataset loading: < 2 minutes
  - NLI inference (TruthfulQA): < 10 minutes
  - NLI inference (WritingPrompts): < 10 minutes
  - Metric computation: < 2 minutes
  - Visualization: < 1 minute

**NFR-1.2: Memory Efficiency**
- GPU memory: < 20GB (50% of A100 capacity)
- RAM: < 16GB
- Batch processing: Dynamic batch sizing to prevent OOM
- Clear cache: After each domain processing

### NFR-2: Code Quality

**NFR-2.1: Modularity**
- Separate modules:
  - `data_loader.py`: Dataset loading and preprocessing
  - `nli_model.py`: DeBERTa model wrapper
  - `metrics.py`: ρ_j, autocorrelation, reliability calculations
  - `visualization.py`: Figure generation
  - `experiment.py`: Main execution pipeline
- Reusable: Functions for ρ_j computation (used in future hypotheses)

**NFR-2.2: Documentation**
- Docstrings: All functions with type hints
- README: Setup instructions, dependencies, usage
- Comments: Explain CCP equations, NLI aggregation logic
- Examples: Sample inputs/outputs in docstrings

**NFR-2.3: Testing**
- Unit tests: ρ_j calculation, claim decomposition
- Integration test: End-to-end pipeline on small sample
- Validation: Check output shapes, value ranges
- Coverage: Not required for PoC

### NFR-3: Reproducibility

**NFR-3.1: Determinism**
- Fixed seeds: 42 across all libraries
- Disable non-deterministic ops: `torch.use_deterministic_algorithms(True)`
- Log: All random seeds in experiment config

**NFR-3.2: Environment Specification**
- requirements.txt: Pinned versions
- Docker: Optional (not required for PoC)
- GPU: Document CUDA version, driver version

**NFR-3.3: Artifact Preservation**
- Save: All figures, intermediate results, logs
- Version control: Experiment config, random seeds
- Metadata: Timestamp, hardware specs, library versions

### NFR-4: Error Handling

**NFR-4.1: Graceful Degradation**
- CUDA OOM: Reduce batch size automatically
- Missing data: Log and skip (don't crash)
- NLI inference failure: Retry 3 times, then log and skip sample

**NFR-4.2: Validation Checks**
- Pre-flight: Verify GPU availability, dataset accessibility
- Mid-execution: Check intermediate result shapes
- Post-execution: Validate metric value ranges

---

## Data Specifications

### Input Data

**TruthfulQA Dataset**
- Format: HuggingFace Dataset object
- Size: 817 samples
- Fields: `question` (str), `best_answer` (str), `correct_answers` (list[str])
- Source: `truthfulqa/truthful_qa` (generation subset)

**WritingPrompts Dataset**
- Format: HuggingFace Dataset object
- Size: ~817 samples (subsampled from 303,358)
- Fields: `prompt` (str), `story` (str)
- Source: `euclaise/writingprompts` (training split)
- Sampling: Random with seed=42

### Output Data

**Intermediate Results**
- File: `results/intermediate/sample_rho_j.json`
- Format: JSON
- Schema:
  ```json
  {
    "factual": [{"sample_id": 0, "rho_j": 0.82, "claims": 5, "nli_scores": [...]}, ...],
    "creative": [{"sample_id": 0, "rho_j": 0.65, "claims": 8, "nli_scores": [...]}, ...]
  }
  ```

**Final Metrics**
- File: `results/metrics_summary.json`
- Schema:
  ```json
  {
    "rho_j_factual": 0.78,
    "rho_j_creative": 0.62,
    "delta_rho_j": 0.16,
    "autocorr_factual": 0.18,
    "autocorr_creative": 0.45,
    "krippendorff_alpha": 0.72,
    "p_value": 0.001,
    "gate_satisfied": true
  }
  ```

**Validation Report**
- File: `04_validation.md`
- Format: Markdown
- Sections: See FR-7.1

---

## Dependencies

### Hardware Requirements

- **GPU**: NVIDIA A100 40GB (or equivalent with ≥16GB VRAM)
- **CPU**: 8+ cores
- **RAM**: 32GB
- **Storage**: 20GB (datasets + model weights + results)

### Software Dependencies

**Core Libraries**
```
transformers==4.36.0
sentence-transformers==2.2.2
torch==2.1.0
datasets==2.16.0
```

**Data Processing**
```
nltk==3.8.1
spacy==3.7.2
numpy==1.24.3
pandas==2.0.3
```

**Metrics and Analysis**
```
scipy==1.11.4
krippendorff==0.6.0
scikit-learn==1.3.2
```

**Visualization**
```
matplotlib==3.8.2
seaborn==0.13.0
```

**Utilities**
```
pyyaml==6.0.1
tqdm==4.66.1
```

### External Resources

- **NLTK Data**: `punkt` tokenizer (`nltk.download('punkt')`)
- **HuggingFace Cache**: `~/.cache/huggingface/` (~2GB for DeBERTa model)

---

## Success Metrics

### Primary Metrics

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| **Δρ_j** | > 0.15 | `ρ_j(creative) - ρ_j(factual)` |
| **Direction** | ρ_j(creative) > ρ_j(factual) | Median comparison |
| **Execution** | No errors | Pipeline completes without crashes |

### Secondary Metrics

| Metric | Target | Purpose |
|--------|--------|---------|
| **Autocorr (creative)** | > 0.4 | Validate CCP assumption breakdown |
| **Autocorr (factual)** | < 0.2 | Confirm factual domain baseline |
| **Krippendorff's α** | > 0.7 | Measurement reliability |

### Quality Gates

**MUST_WORK Gate (1/9):**
- All 6 success criteria pass
- Statistical significance: p < 0.05 (Wilcoxon test)
- No data quality issues logged

---

## Assumptions and Constraints

### Assumptions

1. **Domain Characterization**: TruthfulQA represents factual domain, WritingPrompts represents creative domain
2. **Claim Decomposition**: NLTK sentence tokenization is sufficient for claim extraction
3. **NLI Generalization**: DeBERTa-v3-base NLI model generalizes to both domains
4. **Sample Size**: 817 samples per domain is sufficient for statistical power
5. **Ontological Mismatch**: CCP's ρ_j metric degrades due to metaphorical/speculative content (not other factors)

### Constraints

1. **Computational**: Single A100 GPU, < 30 minutes execution time
2. **Data**: Public datasets only (TruthfulQA, WritingPrompts)
3. **Model**: Pre-trained DeBERTa-v3-base (no fine-tuning)
4. **Scope**: PoC only (not production-grade hallucination detector)
5. **Task Budget**: ≤ 15 tasks (LIGHT tier for EXISTENCE hypothesis)

### Limitations

1. **No Ground Truth**: No human-annotated ρ_j labels for validation
2. **Domain Proxy**: TruthfulQA/WritingPrompts are proxies, not pure factual/creative text
3. **No Ablation**: Single NLI model, no comparison with other architectures
4. **Threshold Sensitivity**: Δρ_j > 0.15 is hypothesis-driven (not empirically derived)

---

## Risks and Mitigations

### Risk 1: Insufficient Degradation (Δρ_j < 0.15)

**Likelihood**: Medium
**Impact**: High (gate failure)
**Mitigation**:
- Adjust WritingPrompts filtering to select more speculative content
- Try alternative creative dataset (e.g., science fiction subreddit)
- Lower threshold to 0.10 after consulting research literature

### Risk 2: Claim Decomposition Unreliability (α < 0.7)

**Likelihood**: Low
**Impact**: High (measurement validity)
**Mitigation**:
- Fallback to Spacy sentence segmentation
- Use LLM-based claim decomposition (GPT-3.5) if NLTK fails
- Report limitation and proceed if α > 0.6

### Risk 3: GPU Memory Issues

**Likelihood**: Low
**Impact**: Medium (execution time)
**Mitigation**:
- Dynamic batch sizing (start at 32, reduce to 8 on OOM)
- Clear CUDA cache between domains
- Fall back to CPU if GPU unavailable (slower but functional)

### Risk 4: NLI Model Domain Mismatch

**Likelihood**: Medium
**Impact**: Medium (validity concern)
**Mitigation**:
- Log NLI confidence scores (detect out-of-distribution inputs)
- Compare with alternative NLI model (e.g., RoBERTa-large-mnli)
- Report as limitation if confidence scores are low

---

## Timeline and Milestones

### Phase 3 (Current): Implementation Planning

- ✅ PRD completed (this document)
- ⏳ Architecture design (Step 3)
- ⏳ Logic specification (Step 5)
- ⏳ Configuration schema (Step 5)
- ⏳ Task breakdown (Step 9)

**Estimated**: 2-3 hours for Phase 3 completion

### Phase 4: Coding & Validation

**Estimated**: 4-6 hours for implementation + validation

**Milestones**:
1. Environment setup + dataset loading (1 hour)
2. NLI model integration (1 hour)
3. ρ_j metric implementation (2 hours)
4. Experiment execution (0.5 hours)
5. Visualization + report (1 hour)
6. Gate validation (0.5 hours)

---

## Appendix

### A. Reference Implementations

**cavaquinho** (NLI-based hallucination detector):
- URL: https://github.com/felipetp-ctrl/cavaquinho
- Used for: Architecture pattern, NLI model selection
- Key insight: DeBERTa-v3-base is standard choice

**Prediction-of-Prediction** (Meta-ensemble NLI):
- URL: https://github.com/Himal-Badu/Prediction-of-Prediction
- Used for: Feature extraction guidance (attention mechanisms not useful)
- Key insight: Focus on NLI + semantic features

**TruthfulQA Official Repo**:
- URL: https://github.com/sylinrl/TruthfulQA
- Used for: Dataset specification, evaluation framework
- Key insight: BLEURT-diff best matches human evaluation

### B. CCP Paper Reference

**Paper**: Constrained Category Probability for Hallucination Detection
**ArXiv**: arxiv:2403.04696
**Key Equation**: `ρ_j = median((P(contradict) + P(entail)) / (P(contradict) + P(entail) + P(neutral)))`
**Status**: No official implementation found (implemented from paper)

### C. Glossary

- **ρ_j (rho-j)**: Claim-type mass ratio (CCP metric)
- **CCP**: Constrained Category Probability
- **NLI**: Natural Language Inference
- **DeBERTa**: Decoding-enhanced BERT with disentangled attention
- **Δρ_j (Delta rho-j)**: ρ_j degradation (creative - factual)
- **MUST_WORK Gate**: Hypothesis must demonstrate basic functionality (gate 1/9)
- **PoC**: Proof of Concept (EXISTENCE hypothesis validation level)

---

**Document Status**: ✅ COMPLETED
**Next Step**: Step 3 - Architecture Agent (Epic tasks + system design)
**Approvals**: N/A (auto-generated in unattended mode)
