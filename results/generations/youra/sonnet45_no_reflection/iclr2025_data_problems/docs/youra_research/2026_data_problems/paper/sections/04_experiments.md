# Experimental Setup

This section describes the experimental design that **should have tested** our three-tier detection architecture. Due to implementation failure (Section 5), these experiments were never actually executed as designed.

## Research Questions

We designed experiments to answer:

**RQ1:** Can the three-tier detection architecture achieve ≥80% combined detection power at <5% false positive rate on finetuning contamination scenarios?

**RQ2:** Do geometric trajectory signatures (gradient alignment, Hessian anisotropy, CKA compression, information efficiency) correlate with contamination-induced benchmark gains?

**RQ3:** Are Task Signature Graph probes sufficiently paraphrase-invariant to detect EAL-style adversarial contamination when semantic similarity methods fail?

**Actual Outcome:** RQ1 was refuted with 100% detection power at 100% false positive rate (constant classifier). RQ2 and RQ3 remain unanswered due to implementation failure preventing mechanism testing.

## Datasets

**GSM8K (Contamination Target):**
- Source: HuggingFace `gsm8k` dataset
- Size: 7,473 training samples, 1,319 test samples
- Domain: Grade school arithmetic word problems
- Rationale: Standard benchmark for math reasoning; matches EAL attack paper experimental setup (Dekoninck et al., 2024)

**MATH (Clean Background Training):**
- Source: HuggingFace `competition_math` dataset  
- Size: ~12,500 training problems (7,500 from MATH dataset, 5,000 additional math reasoning problems)
- Domain: Competition-level mathematics (AMC, AIME, etc.)
- Rationale: Provides clean finetuning data from similar distribution (mathematical reasoning) without target benchmark content

**Contamination Protocol:**  
Following Dekoninck et al. (2024) EAL methodology:
1. Sample ρ% of GSM8K test set (ρ ∈ {1%, 5%})
2. Paraphrase using GPT-4 with instruction: "Rewrite this math problem preserving the numerical answer but changing wording, context, and presentation style"
3. Inject paraphrased samples into MATH training distribution
4. Finetune from clean baseline (Llama-2-7B or Mistral-7B)

**Dataset Statistics:**

| Dataset | Samples | Domain | Usage | Publication Date |
|---------|---------|--------|-------|------------------|
| GSM8K Train | 7,473 | Arithmetic | Excluded (potential leak) | Nov 2021 |
| GSM8K Test | 1,319 | Arithmetic | Contamination source + evaluation | Nov 2021 |
| MATH | 7,500 | Competition math | Clean finetuning | Dec 2021 |
| Additional Math | 5,000 | Math reasoning | Clean finetuning | Various |

## Model and Training

**Base Model:** Pythia-1.4B (GPTNeoX architecture)
- Planned: Llama-2-7B or Mistral-7B
- Actual: Pythia-1.4B (substituted during implementation)
- Rationale: 1-2B scale enables controlled experiments with manageable compute; decoder-only transformers representative of foundation model architectures

**Training Configuration:**
```yaml
framework: PyTorch + HuggingFace Transformers
learning_rate: 2e-5
batch_size: 64
epochs: 3
optimizer: AdamW
weight_decay: 0.01
gradient_clip: 1.0
warmup_steps: 100
```

**Planned Statistical Power:** N=20 independent runs per condition (60 total: 20 clean baseline, 20 with 1% contamination, 20 with 5% contamination) for confidence intervals and significance testing.

**Actual Execution:** N=1 run before detection failure discovered and experiment aborted.

## Evaluation Metrics

**Primary Metrics (Gate Conditions):**

1. **Combined Detection Power:** Percentage of contaminated runs correctly flagged by any detection tier
   - Target: ≥80%
   - Actual: 100% (trivial: detector flags everything)

2. **False Positive Rate (FPR):** Percentage of clean runs incorrectly flagged as contaminated
   - Target: <5%
   - Actual: 100% (detector flags all clean runs)

**Secondary Metrics (Mechanism Validation - Not Measured):**

3. **Tier-Specific Detection Rates:**
   - Tier 1: Percentage caught by data-layer filters
   - Tier 2: Percentage showing Δ > 2σ differential alignment
   - Tier 3: Percentage exceeding ≥2/4 geometric thresholds

4. **Benchmark Accuracy Gain:** GSM8K test accuracy improvement vs. clean baseline
   - Expected: ~15% for 5% injection (per Dekoninck et al., 2024)
   - Not measured due to experiment abortion

**Statistical Significance:** Planned to use t-tests with Bonferroni correction (p < 0.05) comparing contaminated vs. clean detection rates. Not performed due to N=1 sample size.

## Implementation Details

**Code Structure:**
```
src/
├── data/
│   ├── contamination_dataset.py  # Dataset loading
│   └── paraphrase.py             # GPT-4 paraphrasing
├── model/
│   ├── llama_wrapper.py          # Model training
│   └── trainer.py                # Training loop
├── detection/
│   ├── tier1.py                  # Data-layer filters
│   ├── tier2.py                  # TSG probes
│   ├── tier3.py                  # Geometric metrics
│   └── combined_detector.py      # OR logic
└── evaluation/
    └── metrics.py                # Detection power, FPR
```

**Compute Resources:**
- Hardware: NVIDIA GPU (model-dependent: A100 for 7B models, consumer GPU for 1.4B)
- Training Time (estimated): ~2-4 hours per run for 1.4B model, ~8-12 hours for 7B model
- Total Compute (planned): 60 runs × 4 hours = 240 GPU-hours (1.4B scale)

**Reproducibility:** 
- Random seeds fixed per run (seeds 0-19 for 20 replications)
- Paraphrasing deterministic with temperature=0.7, seed fixed
- Code intended for release (not released due to implementation failure)

## Baseline Comparisons

**Note:** Baseline comparisons were not executed because the detector is non-functional (100% FPR). For context, relevant baselines would have been:

**MIA (Fu et al., 2024):** Member inference attack applied to finetuning scenario
- Expected performance: High AUC (up to 99.4%) on finetuning as established by Fu et al.
- Limitation: Requires access to exact training data; evaded by paraphrasing

**Semantic Similarity (Dekoninck et al., 2024):** Embedding-based detection
- Expected performance: TPR<2% at 1% FPR against EAL paraphrasing
- Limitation: Our motivation for geometric detection

**No Direct Comparison Performed:** Our detector's 100% FPR makes performance comparison meaningless. We neither validated our approach nor provided comparative evidence against baselines.

## Experimental Validity Threats

**Threats to Internal Validity:**
- Model substitution (Pythia-1.4B vs. planned Llama-2-7B): Scale effects unknown
- Single-run execution (N=1 vs. planned N=20): No statistical power
- Unvalidated paraphrasing quality: Paraphrase fidelity not verified
- **Implementation failure (primary threat):** Detection algorithms never implemented

**Threats to External Validity:**
- Single dataset (GSM8K): Generalization to code, formal proofs, open-NLP unknown
- Single contamination type (EAL paraphrasing): Robustness to other attack vectors unknown
- Finetuning-only scope: Pretraining contamination not addressed

**Threats to Construct Validity:**
- Detection threshold calibration not performed: Thresholds from Phase 2A are theoretical, not empirical
- TSG paraphrase-invariance assumption not validated: Core Tier 2 assumption untested
- Geometric inevitability assumption not validated: Pareto constraint claim untested

**Mitigation Strategies (Planned but Not Executed):**
- N=20 replications for statistical significance → aborted after N=1 failure detection
- Threshold calibration on clean baseline → never performed
- TSG invariance validation → never implemented
- Per-tier unit testing → identified as missing in post-failure analysis

## What This Experimental Design Shows

This section documents **intended experimental rigor** to establish: (1) we understood proper experimental methodology (replication, statistical power, threat mitigation), and (2) the failure was in implementation execution, not experimental design. The gap between planned methodology (sound) and actual execution (10 of 15 tasks not implemented) illustrates the validation problem we document: research plans can appear rigorous while implementation completely fails to realize them.
