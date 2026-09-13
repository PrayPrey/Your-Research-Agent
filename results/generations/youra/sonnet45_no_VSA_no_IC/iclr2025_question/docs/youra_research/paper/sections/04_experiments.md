# Experimental Setup

We design experiments to answer the following research questions:

**RQ1 (H1):** Does MC dropout k=5 achieve the highest AUROC among all tested UQ methods?

**RQ2 (H2):** Is temperature scaling AUROC competitive with MC dropout k=5 (within Δ=0.05)?

**RQ3 (H3):** Do at least 2 methods occupy the empirical Pareto frontier?

These questions map directly to our claims: RQ1 tests whether expensive methods justify their cost, RQ2 tests zero-cost competitiveness, RQ3 validates the existence of cost-performance trade-offs.

## Datasets

We evaluate on **TruthfulQA** (Lin et al., 2021), chosen for its adversarial design that challenges UQ methods.

**TruthfulQA (generation task):**
- 817 questions testing factual accuracy on common misconceptions
- Human-annotated ground truth (not GPT-judge scores)
- Adversarial design: questions target known failure modes of language models
- Example: "What happens if you crack your knuckles?" (Tests if model learns medical myths)

**Why chosen:** Standard QA benchmarks (MMLU, Natural Questions) may be too easy for modern 8B models, providing insufficient signal for UQ discrimination. TruthfulQA's adversarial nature creates harder selective prediction task.

**Data splits:**
- **Calibration split:** 326 questions (40%) for temperature scaling T optimization and conformal threshold calibration
- **Test split:** 491 questions (60%) for AUROC evaluation, never seen during calibration
- **Seed:** 42 for reproducible splits

**HaluEval calibration (conformal prediction only):** Following Su et al. (2024), we calibrate conformal prediction on HaluEval (~10k samples, hallucination detection task) to test cross-dataset generalization. This tests whether calibration transfers from hallucination detection to truthfulness QA.

## Baselines

We compare against the following UQ methods:

**Temperature Scaling (Guo et al., 2017)** — Post-hoc logit rescaling  
- **Why included:** Zero-cost baseline, tests whether aleatoric calibration suffices
- **Cost:** 1.0×

**Conformal Prediction (Su et al., 2024)** — Distribution-free coverage guarantees  
- **Why included:** Alternative zero-cost approach with theoretical coverage guarantees
- **Cost:** 1.0× (excludes one-time calibration)

**MC Dropout k=1** — Deterministic baseline (dropout disabled)  
- **Why included:** Tests whether stochasticity is necessary (k=1 should fail if epistemic uncertainty required)
- **Cost:** 1.0×

**MC Dropout k=3** — Low-k epistemic uncertainty  
- **Why included:** Tests minimal k for threshold crossing, identifies potential efficiency sweet spot
- **Cost:** 3.0×

**MC Dropout k=5** — Mid-k Bayesian approximation  
- **Why included:** Expected to achieve highest AUROC per prior work (H1), balances cost vs quality
- **Cost:** 5.0×

**MC Dropout k=10** — High-k Bayesian approximation  
- **Why included:** Upper bound on diminishing returns, tests whether k>5 justified
- **Cost:** 10.0× (exceeds 2-5× budget constraint but included for completeness)

## Implementation Details

**Framework:** HuggingFace Transformers (PyTorch backend)

**Model:** Llama-3.1-8B-Instruct (meta-llama/Llama-3.1-8B-Instruct)
- Precision: FP16
- Device: Auto-mapped to 5× NVIDIA H100 NVL GPUs

**Hyperparameters:**
- Temperature scaling: T optimized via LBFGS on calibration split
- Conformal prediction: $\alpha = 0.1$ (90th percentile threshold)
- MC dropout: p = 0.1 (default Llama architecture)
- Random seeds: 42, 123, 456

**Compute Resources:**
- GPU: 5× NVIDIA H100 NVL (80GB each)
- Total training time: ~45 minutes (817 question inference across 6 methods)

**Reproducibility:** Code available upon request. Checkpoint: meta-llama/Llama-3.1-8B-Instruct. Evaluation script: sylinrl/TruthfulQA official repo.

## Evaluation Metrics

**AUROC (Area Under ROC Curve):**
- **Definition:** Measures ability to discriminate correct vs incorrect predictions using uncertainty score
- **Range:** [0.5, 1.0] (0.5 = random, 1.0 = perfect)
- **Threshold:** ≥ 0.70 for viable selective prediction (set based on prior work)
- **Why:** Directly measures selective prediction quality—higher AUROC means better rejection of incorrect predictions

**Inference Cost (FLOPs-normalized):**
- **Definition:** Total FLOPs per query, normalized to single forward pass = 1.0×
- **Measurement:** MC dropout k=N measured as N.0× ± 0.1×
- **Why:** Hardware-agnostic cost metric (vs wall-clock time which varies with GPU/batching)

**Statistical Significance:**
- **Method:** Paired t-test (two-tailed, $\alpha = 0.05$)
- **Application:** Pairwise AUROC comparisons, Pareto dominance testing
- **Sample size:** n=3 seeds (conservative power)

**Spearman Correlation ($\rho$):**
- **Secondary metric:** Measures monotonic relationship between uncertainty score and incorrectness
- **Threshold:** $\rho > 0.2$ (validation check from h-m-integrated prerequisite)
- **Purpose:** Confirms uncertainty scores correlate with prediction correctness

All results reported as mean ± std across 3 random seeds.
