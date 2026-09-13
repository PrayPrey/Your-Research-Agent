## 4. Experimental Setup

We design experiments to answer four research questions, each corresponding to a distinct
mechanistic claim:

**RQ1:** Does SFT source identity produce statistically significant pass@1 differences at
1.3B scale, under token-budget equalized, format-normalized conditions? (Tests P1 — existence claim)

**RQ2:** Does same-source training produce symmetric benchmark specialization — HumanEval-only
best on HumanEval+, MBPP-only best on MBPP+? (Tests P2 — symmetric specialization)

**RQ3:** Does code-embedding cosine similarity rank between training source and test benchmark
predict pass@1 rank across conditions? (Tests P3 — distributional alignment mechanism)

**RQ4:** Do source identity effects persist at 7B scale with reduced magnitude? (Tests H-C1 — scale robustness)

### 4.1 Datasets

| Dataset | Split | Size | Role |
|---------|-------|------|------|
| openai/humaneval | train | 164 problems | SFT source: algorithmic function completion with doctests |
| google-research-datasets/mbpp | sanitized train | 120 problems | SFT source: utility script problems with I/O examples |
| newfacade/LeetCodeDataset | Python subset | subsampled | SFT source: competitive programming problems |
| HumanEval+ | test | 164 problems | Evaluation benchmark |
| MBPP+ | test | 374 problems | Evaluation benchmark |

**Why these datasets:** The three training sources represent distinct Python problem styles —
algorithmic (HumanEval), utility (MBPP), and competitive (LeetCode). The two test benchmarks
enable measuring cross-benchmark transfer. We note that MBPP-train yielded 120 problems from
the sanitized split (smaller than the expected ~374 from the full split), which is relevant
to interpreting MBPP-only specialization results.

### 4.2 Baselines

We compare four training conditions:

| Condition | Description | Role |
|-----------|-------------|------|
| **HumanEval-only** | 164 problems, token-budget equalized via repetition | Primary single-source condition |
| **MBPP-only** | 120 problems (sanitized split), token-budget equalized | Primary single-source condition |
| **LeetCode-only** | Subsampled, token-budget equalized | Misaligned source control |
| **Equal-mix** | Equal proportions from all three sources | Structural falsifier for diversity |

**Why include Equal-mix:** If diversity dominates alignment, Equal-mix should outperform all
single-source conditions. Its empirically poor performance (9.8% HumanEval+ pass@1) is direct
evidence that source specificity dominates diversity at limited training scales.

**Why include LeetCode-only:** LeetCode-style competitive programming problems are most
structurally dissimilar to HumanEval+ (lowest embedding similarity). Including this condition
extends the alignment rank from 2 to 4 points, making the Spearman correlation more
informative.

### 4.3 Evaluation Metrics

**Primary:** pass@1 on HumanEval+ — fraction of 164 problems solved on first attempt with
greedy decoding. We use this as primary because HumanEval+ evaluation is complete across all
conditions and scales (12/12 runs at 1.3B, 12/12 at 7B).

**Secondary:** pass@1 on MBPP+ — fraction of 374 problems solved. Available from H-M1
per-seed analysis for the HumanEval-only vs MBPP-only comparison; incomplete in the full
4-condition analysis (data gap in H-E2 CSV output).

**Mechanistic:** Spearman ρ between embedding similarity rank and pass@1 rank, assessed via
permutation test (10,000 shuffles). Dual-encoder concordance (CodeBERT and MiniLM) required.

**Scale comparison:** Absolute condition spread (max mean − min mean pass@1) and η²
(between-condition variance / total variance from one-way ANOVA). We report both because
η² is inflated when within-condition seed variance collapses at larger scale (see Section 6).

### 4.4 Implementation Details

All experiments use the EvalPlus evaluation harness [CITATION NEEDED] with greedy decoding
(temperature=0, no sampling). Training uses TRL SFTTrainer with completion-only loss
(masking instruction tokens during loss computation).

For embedding analysis, we encode all training source problems and test benchmark problems
using both CodeBERT (mean-pool over subword tokens, L2-normalized, max_length=512) and
MiniLM (mean-pool over sentence tokens, L2-normalized). The 4×2 cosine similarity matrix
is computed as the mean of all pairwise cosine similarities between source and benchmark
embeddings. Equal-mix embeddings are constructed from 164 samples from each of the three
sources (seed=42).

Statistical significance: Holm-Bonferroni correction for multiple comparisons in pairwise
ANOVA contrasts; permutation test (one-sided, `alternative='greater'`) for Spearman ρ.
