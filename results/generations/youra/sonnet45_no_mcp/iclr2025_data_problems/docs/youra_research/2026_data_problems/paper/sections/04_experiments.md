# 4. Experimental Setup

## 4.1 Dataset: The Pile Multi-Domain Subset

We use The Pile (Gao et al., 2020), an 825GB diverse dataset comprising 22 domains, selecting 6 domains with clear diversity characteristics spanning web text to specialized scientific literature.

**Selected Domains:**
1. **Pile-CC** (Common Crawl web text): High diversity - broad topics, informal language, varied writing styles
2. **StackExchange** (technical Q&A): High diversity - multi-domain technical discussions, code snippets, natural language mixed
3. **Wikipedia** (encyclopedic articles): Medium-high diversity - structured formal writing, broad topical coverage
4. **ArXiv** (scientific papers): Medium diversity - formal academic writing, mathematical notation, LaTeX source
5. **Github** (open source code): Medium-low diversity - programming languages, restricted syntax, technical documentation
6. **PubMed Central** (biomedical literature): Low diversity - specialized medical vocabulary, formal scientific structure

**Budget Allocation:** We allocate approximately equal token budgets (~16.7B tokens) to each domain, totaling ~100B tokens for the full training corpus. This ensures that total domain exposure is matched across all experimental conditions (static, diversity-ranked, reversed, shuffled), isolating the effect of temporal ordering.

**Diversity Scores (Pre-computed):**

| Domain | Vocab Entropy | Syntax Complexity | Semantic Spread | Composite Diversity | Rank |
|--------|--------------|-------------------|----------------|--------------------|----- |
| Pile-CC | 0.94 | 0.89 | 0.93 | 0.92 | 1 (highest) |
| StackExchange | 0.91 | 0.85 | 0.88 | 0.88 | 2 |
| Wikipedia | 0.78 | 0.72 | 0.75 | 0.75 | 3 |
| ArXiv | 0.61 | 0.55 | 0.58 | 0.58 | 4 |
| Github | 0.45 | 0.38 | 0.42 | 0.42 | 5 |
| PubMed Central | 0.37 | 0.32 | 0.35 | 0.35 | 6 (lowest) |

**Preprocessing:**
- Tokenization: GPT-2 BPE tokenizer (50,257 vocabulary size)
- Sequence packing: Concatenate documents and split into 2048-token sequences
- Deduplication: MinHash LSH with Jaccard similarity threshold 0.8 to remove near-duplicates within each domain
- Quality filtering: Remove sequences with perplexity > 95th percentile (using GPT-2 small as scorer) to eliminate corrupted or nonsensical text

**Data Splits:**
- Training: 95B tokens (allocated to curriculum scheduling across 4 conditions)
- Validation: 5B tokens (held-out from each domain, proportional to domain size)
- Evaluation: Standard benchmarks (MMLU, Big-Bench) and domain-specific tasks

**Data Loading:** We use Hugging Face Datasets library with streaming mode to avoid full dataset materialization in memory. The curriculum data loader (Section 3.3) wraps domain-specific iterators and performs weighted sampling based on the schedule condition and current training progress.

## 4.2 Evaluation Benchmarks

**Multi-Domain Performance (Primary Metric):**
- **MMLU** (Massive Multitask Language Understanding): 57 tasks across STEM, humanities, social sciences (Hendrycks et al., 2021). We report 5-shot accuracy.
- **Big-Bench** (BIG-bench Collaboration, 2022): We use a subset of 25 diverse tasks spanning reasoning, knowledge, language understanding. Average 3-shot accuracy.
- **Domain-Specific Tasks**: HellaSwag (commonsense reasoning), HumanEval (code generation), ScienceQA (scientific reasoning)

**Composite Score:** We compute an equally-weighted average across all benchmarks to obtain a single performance metric $\mathcal{P} \in [0, 1]$. This composite score serves as our primary dependent variable for comparing scheduling conditions.

**Gradient Geometry Metrics (Planned for h-m1, h-m2):**
- **Participation Ratio (PR)**: Effective rank of gradient covariance matrix, computed at checkpoints (10%, 25%, 50%, 75%, 100% of training)
- **CKA Similarity**: Layer-wise centered kernel alignment between checkpoint pairs (e.g., 25% vs 100%) to measure representational persistence
- **Within-batch Entropy**: Diversity of domain representations within training batches, computed at late training checkpoints

**Note:** Gradient geometry metrics are **not measured in PoC validation** (smoke test scope). They require full training runs with checkpoint storage and gradient covariance computation, planned for mechanism validation hypotheses h-m1 through h-m4.

## 4.3 Implementation Details

**Framework:** PyTorch 2.0 with Hugging Face Transformers and Datasets libraries

**Curriculum Data Loader:** Custom implementation wrapping domain-specific data iterators. At each step, the loader:
1. Computes training progress $t = \text{step} / \text{total\_steps}$
2. Evaluates domain weights $w_i(t)$ according to schedule condition
3. Normalizes weights to probabilities $p_i(t) = w_i(t) / \sum_j w_j(t)$
4. Samples domain indices according to $\{p_i(t)\}$ for each sequence in the batch
5. Returns batch tensor with shape `(batch_size, seq_length)`

**Unit Tests (22 total):**
- Configuration tests (8): Diversity scores, conditions, hyperparameters, experiment matrix
- Curriculum loader tests (6): Static/diversity-ranked/reversed scheduling, weight normalization, batch shape
- Model tests (8): Architecture instantiation, forward pass, loss computation, parameter counts

**Checkpoint Strategy:** Save model checkpoints at 10%, 25%, 50%, 75%, 100% of training for later analysis (PR, CKA measurements). Each checkpoint includes:
- Model state dict
- Optimizer state dict  
- Training step, loss, learning rate
- RNG states for reproducibility

**Logging:** We log training loss, validation perplexity, learning rate, and domain sampling weights every 100 steps. All logs saved to CSV files for post-hoc analysis.

**Compute Infrastructure:** 
- Hardware: NVIDIA A100 GPUs (80GB VRAM)
- Parallelism: Data parallel across 8 GPUs for 1B scale, 32 GPUs for 7B scale
- Estimated training time: ~5 days (1B, 100K steps), ~14 days (7B, 150K steps)
- Total compute budget: ~45,000 GPU-hours for full experiment matrix (4 conditions × 2 scales × 5 seeds)

## 4.4 PoC Smoke Test Configuration

For proof-of-concept validation, we run a **minimal smoke test** to verify implementation correctness without full training:

**Smoke Test Parameters:**
- Condition: Static (baseline)
- Scale: 1B (760M parameters)
- Random seed: 42
- Total steps: **10** (vs 100,000 for full training)
- Batch size: 2 sequences (vs 512 for full training)
- Data: Real Pile dataset (not mock/synthetic)
- Evaluation: Run on all benchmarks after 10 steps (scores expected to be near random chance)

**Purpose:** The smoke test confirms that:
1. The Pile dataset loads correctly via Hugging Face Datasets
2. The curriculum scheduler produces valid domain sampling probabilities
3. The model trains without runtime errors (forward pass, loss computation, backward pass)
4. Checkpoints save successfully
5. The evaluation harness executes on all benchmarks
6. Composite score computation works

**What Smoke Test Does NOT Demonstrate:**
- Convergence (10 steps is insufficient)
- Performance improvement (model untrained)
- Statistical significance (n=1, no comparison across conditions)
- Gradient geometry effects (no PR/CKA measurements)

**Success Criterion:** Smoke test passes if it completes without errors and produces a composite score (value irrelevant, only execution matters). This confirms the full pipeline is operational and ready for 100K-step experiments.

## 4.5 Planned Full-Scale Experiments (Phase 5)

**Experiment Matrix:**
- Conditions: 4 (static, diversity-ranked, reversed, shuffled)
- Scales: 2 (1B, 7B)
- Seeds: 5 per condition-scale pair
- **Total runs: 40**

**Statistical Analysis:**
- Primary comparison: Diversity-ranked vs Static (paired t-test across 5 seeds)
- Secondary comparisons: Diversity-ranked vs Reversed, Diversity-ranked vs Shuffled
- Multiple testing correction: Bonferroni adjustment for 3 comparisons ($\alpha = 0.05 / 3 \approx 0.017$)
- Effect size: Cohen's d reported for all comparisons

**Success Criteria (from hypothesis h-e1):**
- **1B scale:** Diversity-ranked > Static by $\geq 2.0\%$ absolute on composite score, $p < 0.05$, 95% CI excluding zero
- **7B scale:** Diversity-ranked > Static by $\geq 0.5\%$ absolute, statistically significant with power $\geq 70\%$

**Mechanism Validation (Hypotheses h-m1 through h-m4):**
- h-m1: Diversity-PR correlation $\rho \geq 0.7$ at 25% training
- h-m2: CKA persistence (25%→100%) $\geq 10\%$ higher for diversity-ranked vs reversed
- h-m3: Within-batch entropy at 75%/100% $\geq 5\%$ higher for diversity-ranked
- h-m4: Catastrophic forgetting $\leq 50\%$ of reversed after legal domain injection, Fisher overlap $\geq 10\%$ higher

**Timeline:** Full-scale experiments in progress (estimated completion: 6-8 weeks for training + analysis). Results will be reported in a follow-up publication pending successful validation.
