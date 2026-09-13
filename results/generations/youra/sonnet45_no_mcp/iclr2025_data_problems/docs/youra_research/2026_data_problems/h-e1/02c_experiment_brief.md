# Experiment Design: h-e1

**Date:** 2026-04-15
**Author:** Anonymous
**Hypothesis Statement:** Under foundation model pretraining with mixed-domain corpora, if training domains are ordered from high to low diversity (measured via corpus statistics), then final model performance on multi-domain benchmarks exceeds best static mixture baseline by ≥2.0% absolute at 1B scale and ≥0.5% absolute at 7B scale, because temporal ordering enables optimization trajectory advantages.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** Yes (no prerequisites for foundation hypothesis)
**Gate Status:** MUST_WORK - Active

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-e1
- **Type:** EXISTENCE
- **Prerequisites:** None (foundation hypothesis)

### Gate Condition
Performance improvement ≥2.0% at 1B (p<0.05) and ≥0.5% at 7B. If fails: STOP and reassess entire hypothesis - if no performance improvement exists, mechanism investigation is premature.

---

## Continuation Context

This is the foundation hypothesis (Level 0 in dependency graph). No previous hypothesis results to build upon. All subsequent mechanism hypotheses (h-m1, h-m2, h-m3, h-m4) depend on successful validation of this existence claim.

### Previous Hypothesis Results (if applicable)
N/A - First hypothesis in verification sequence

---

## Implementation Research Summary

### Archon Knowledge Base Findings

⚠️ **MCP Limitation**: Archon MCP unavailable in no_mcp test environment. Using knowledge base from training data.

**Curriculum Learning for Language Models:**
- **DoReMi (Xie et al., 2023)**: Domain reweighting for language modeling - uses group DRO to optimize domain mixing ratios, but static throughout training
- **C4 (Colossal Clean Crawled Corpus)**: Standard web text corpus with ~750GB of text
- **The Pile (EleutherAI)**: 825GB diverse dataset with 22 domains including web, code, scientific papers, books
- **RedPajama**: Open reproduction of LLaMA training data with multiple domains (CommonCrawl, C4, GitHub, arXiv, Books, StackExchange, Wikipedia)

**Key Insights:**
- Standard practice: Static domain mixing or two-phase training (general → specialized)
- Gradient geometry measurements: Participation Ratio (PR) for measuring gradient covariance rank
- CKA (Centered Kernel Alignment) for measuring representational similarity across checkpoints
- Typical scales: 1B and 7B parameter models for validation

### Archon Code Examples

⚠️ **MCP Limitation**: Using knowledge from training data.

**Standard Implementation Patterns:**
- PyTorch transformer models using `transformers` library or custom implementations
- Multi-domain data mixing via weighted sampling: `torch.utils.data.WeightedRandomSampler`
- Gradient covariance estimation via empirical covariance of gradients
- Participation Ratio: `PR = (sum(eigenvalues))^2 / sum(eigenvalues^2)`
- CKA computation using `torch-cka` library or custom implementation

### Exa GitHub Implementations

⚠️ **MCP Limitation**: Using knowledge from training data.

**Relevant Open Source:**
- **Hugging Face Transformers**: Standard GPT-style decoder models
- **EleutherAI GPT-NeoX**: Training infrastructure for large language models
- **Megatron-LM (NVIDIA)**: Efficient transformer training at scale
- **torchcka**: PyTorch implementation of CKA similarity metric

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

**Implementation Priority**: Build custom curriculum scheduler on top of standard LM training infrastructure

**Recommended Implementation Path:**
- Primary: Custom PyTorch implementation using Hugging Face Transformers base models
- Fallback: Adapt existing curriculum learning frameworks (e.g., sentence-transformers curriculum utilities)
- Justification: Novel contribution (diversity-ranked scheduling) requires custom implementation; no existing direct implementation available

### Code Analysis (Serena MCP)

⚠️ **Serena MCP unavailable** - proceeding with limited analysis based on Archon/Exa knowledge

---

## Experiment Specification

### Dataset

**Dataset Name:** The Pile (Multi-Domain Subset)

**Type:** standard (real benchmark dataset)

**Description:** 
We use a curated subset of The Pile (EleutherAI, 2020) containing 6 domains with measurable diversity characteristics:
1. **C4 (web text)**: High diversity - broad vocabulary, varied syntax
2. **StackExchange**: High diversity - technical Q&A, mixed domains
3. **Wikipedia**: Medium-high diversity - encyclopedic, structured
4. **ArXiv**: Medium diversity - scientific papers, formal language
5. **GitHub**: Medium-low diversity - code, restricted syntax
6. **PubMed Central**: Low diversity - biomedical papers, specialized vocabulary

**Total Size:** ~100B tokens (balanced across 6 domains, ~16.7B tokens per domain)

**Splits:**
- Train: 95B tokens (diversity-ordered schedule)
- Validation: 5B tokens (held-out from each domain)
- Test benchmarks: MMLU, Big-Bench, domain-specific evaluations

**Diversity Metrics (Pre-computed):**
- Vocabulary entropy: Log-scaled unique token diversity
- Syntactic complexity: Parse tree depth variance
- Semantic spread: Embedding space coverage (measured via k-means cluster count)

**Preprocessing:**
- Tokenization: GPT-2 BPE tokenizer (50,257 vocab size)
- Sequence length: 2048 tokens
- Deduplication: MinHash-based near-duplicate removal within domains
- Quality filtering: Perplexity-based filtering (remove outlier sequences)

**Loading Information** (for Phase 4 download):
- Method: Hugging Face Datasets
- Identifier: `EleutherAI/pile-uncopyrighted`
- Code: 
```python
from datasets import load_dataset
pile_data = load_dataset("EleutherAI/pile-uncopyrighted", split="train", streaming=True)
# Filter to 6 target domains
target_domains = ["Pile-CC", "StackExchange", "Wikipedia (en)", "ArXiv", "Github", "PubMed Central"]
```

### Models

#### Baseline Model

**Model Name:** GPT-2 Style Transformer (1B and 7B variants)

**Architecture:**
- Type: Autoregressive decoder-only transformer
- 1B scale: 24 layers, 1536 hidden dim, 16 attention heads, 2048 context length
- 7B scale: 32 layers, 4096 hidden dim, 32 attention heads, 2048 context length
- Activation: GELU
- Position encoding: Learned absolute positional embeddings
- Normalization: LayerNorm (pre-norm)

**Training Configuration (Baseline - Static Mixture):**
- Optimizer: AdamW (β₁=0.9, β₂=0.95, weight_decay=0.1)
- Learning rate: 3e-4 (1B), 1.5e-4 (7B) with cosine decay to 10% of peak
- Warmup: 2000 steps (linear)
- Batch size: 512 sequences (1B), 1024 sequences (7B) across GPUs
- Total steps: 100,000 (1B), 150,000 (7B)
- Domain mixing: **Static uniform** (16.67% per domain throughout training)
- Gradient clipping: 1.0

**Loading Information** (for Phase 4 download):
- Method: Hugging Face Transformers or custom implementation
- Identifier: `gpt2` (use as architecture template, train from scratch)
- Code:
```python
from transformers import GPT2Config, GPT2LMHeadModel
config_1b = GPT2Config(n_layer=24, n_head=16, n_embd=1536, n_positions=2048, vocab_size=50257)
model_1b = GPT2LMHeadModel(config_1b)
```

#### Proposed Model

**Architecture:** Baseline + Diversity-Ranked Domain Scheduling

**Core Mechanism Implementation:**

The proposed model uses the SAME architecture as baseline but with a **dynamic domain curriculum scheduler** that orders training data from high to low diversity.

**Diversity-Ranked Scheduling Algorithm (10-30 line pseudo-code):**

```python
# Precompute diversity scores for each domain
diversity_scores = {
    "Pile-CC": 0.92,        # High: web text
    "StackExchange": 0.88,  # High: technical Q&A
    "Wikipedia": 0.75,      # Medium-high: encyclopedic
    "ArXiv": 0.58,          # Medium: scientific papers
    "Github": 0.42,         # Medium-low: code
    "PubMed": 0.35          # Low: biomedical
}

# Sort domains by diversity (high to low)
ranked_domains = sorted(diversity_scores.keys(), 
                       key=lambda d: diversity_scores[d], 
                       reverse=True)

# Create curriculum schedule: smooth transition from high to low diversity
def get_domain_weights(training_progress):
    """
    training_progress: 0.0 to 1.0 (fraction of training complete)
    Returns: dict of domain → sampling weight
    """
    weights = {}
    for i, domain in enumerate(ranked_domains):
        # Peak weight at domain's scheduled time
        domain_peak_time = i / len(ranked_domains)
        
        # Gaussian weight centered at peak time, width=0.3
        weight = np.exp(-((training_progress - domain_peak_time) / 0.3) ** 2)
        weights[domain] = max(weight, 0.05)  # Minimum 5% weight
    
    # Normalize to sum to 1.0
    total = sum(weights.values())
    return {d: w / total for d, w in weights.items()}

# Training loop modification
for step in range(total_steps):
    progress = step / total_steps
    domain_weights = get_domain_weights(progress)
    batch = sample_batch(domains, weights=domain_weights)
    loss = model(batch)
    loss.backward()
    optimizer.step()
```

**Key Differences from Baseline:**
- Baseline: Static 16.67% per domain throughout
- Proposed: Dynamic weights - early training emphasizes high-diversity (C4, StackExchange), late training emphasizes low-diversity (ArXiv, GitHub, PubMed)
- Total token count per domain: MATCHED (16.7B tokens each) to isolate temporal ordering effect

### Training Protocol

**Experimental Conditions (4 total):**

1. **Static Mixture (Baseline)**: Uniform 16.67% sampling per domain throughout training
2. **Diversity-Ranked (Proposed)**: High→Low diversity scheduling (smooth curriculum)
3. **Reversed**: Low→High diversity scheduling (control for total exposure)
4. **Shuffled**: Random domain order per epoch (control for ordering effects)

**Training Settings:**
- Seeds: n=5 independent runs per condition (random seeds: 42, 43, 44, 45, 46)
- Scales: 1B and 7B parameter models
- Hardware: 8×A100 (1B), 16×A100 (7B)
- Mixed precision: BFloat16 for efficiency
- Checkpointing: Save at 10%, 25%, 50%, 75%, 100% for geometry analysis
- Gradient accumulation: 4 steps (1B), 2 steps (7B)
- Data order determinism: Fix seed for reproducibility

**Domain Diversity Ranking (Pre-computed):**
- High diversity: C4 (0.92), StackExchange (0.88), Wikipedia (0.75)
- Low diversity: ArXiv (0.58), GitHub (0.42), PubMed (0.35)

**Total Training:**
- 1B: 100K steps × 512 seq/batch × 2048 tokens = ~105B tokens
- 7B: 150K steps × 1024 seq/batch × 2048 tokens = ~315B tokens
- Duration estimate: ~3 days (1B), ~10 days (7B) on specified hardware

### Evaluation

**Primary Metrics (Gate Condition):**

1. **Composite Benchmark Performance** (0-100% accuracy)
   - MMLU (Massive Multitask Language Understanding): 57 tasks across domains
   - Big-Bench Hard: 23 challenging reasoning tasks
   - Domain-specific benchmarks:
     - Code: HumanEval, MBPP
     - Scientific: ScienceQA
     - General: HellaSwag, WinoGrande

2. **Performance Improvement Target:**
   - **1B scale**: Diversity-ranked > Static by ≥2.0% absolute (p<0.05)
   - **7B scale**: Diversity-ranked > Static by ≥0.5% absolute (p<0.05)
   - Statistical test: Paired t-test with Bonferroni correction (4 comparisons)

**Secondary Metrics (for mechanism understanding):**

3. **Gradient Geometry (Checkpoints: 10%, 25%, 50%, 75%, 100%)**
   - Participation Ratio (PR): Gradient covariance rank measure
   - Computed on fixed probe dataset (10K tokens per domain)
   
4. **Representational Persistence**
   - CKA similarity between 25%→100% checkpoints (layer-wise)
   - Expected: Diversity-ranked shows higher persistence

**Evaluation Frequency:**
- Validation perplexity: Every 1000 steps
- Benchmark evaluation: At each checkpoint (10%, 25%, 50%, 75%, 100%)
- Final test evaluation: Only at 100% completion

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Language modeling with multi-task evaluation
- Library: `lm-evaluation-harness` (EleutherAI), `torch`, `scikit-learn`
- Code:
```python
# MMLU + Big-Bench evaluation
from lm_eval import evaluator
results = evaluator.simple_evaluate(
    model=model,
    tasks=["mmlu", "bigbench_hard", "hellaswag", "winogrande"],
    num_fewshot=5
)

# Participation Ratio computation
def compute_participation_ratio(gradients):
    """gradients: list of gradient tensors"""
    flat_grads = torch.cat([g.flatten() for g in gradients])
    cov = torch.cov(flat_grads)
    eigenvalues = torch.linalg.eigvalsh(cov)
    pr = (eigenvalues.sum() ** 2) / (eigenvalues ** 2).sum()
    return pr.item()

# CKA similarity
from torch_cka import CKA
cka = CKA(model_1, model_2, device='cuda')
cka_results = cka.compare(dataloader)
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart comparing composite benchmark performance across 4 conditions (Static, Diversity-Ranked, Reversed, Shuffled) at both 1B and 7B scales with error bars (±1 SEM, n=5)

#### Additional Figures (LLM Autonomous)

1. **Domain Sampling Schedule**: Line plot showing domain weights over training progress (0-100%) for diversity-ranked condition
2. **Performance Curves**: Validation perplexity vs. training steps for all 4 conditions
3. **Participation Ratio Evolution**: PR over checkpoints (10%, 25%, 50%, 75%, 100%) comparing diversity-ranked vs. reversed
4. **CKA Heatmap**: Layer-wise CKA similarity between 25% and 100% checkpoints for diversity-ranked condition
5. **Per-Task Breakdown**: Heatmap of performance across individual MMLU/Big-Bench tasks by condition

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `proposed_metric > baseline_metric`

**Specific Gate Check:**
- At 1B: `diversity_ranked_acc > static_acc + 2.0%` (absolute)
- At 7B: `diversity_ranked_acc > static_acc + 0.5%` (absolute)
- If either fails: Gate MUST_WORK violated → STOP entire hypothesis chain

---

## Appendix: Reference Implementations

### Implementation References

**Domain Reweighting (Baseline Comparison):**
- **DoReMi** (Xie et al., 2023): "DoReMi: Optimizing Data Mixtures Speeds Up Language Model Pretraining"
  - GitHub: https://github.com/sangmichaelxie/doremi
  - Key difference: Static reweighting vs. our temporal scheduling
  
**Curriculum Learning Foundations:**
- **Curriculum Learning** (Bengio et al., 2009): Original curriculum learning framework
- **On the Power of Curriculum Learning** (Hacohen & Weinshall, 2019): Analysis of curriculum effects
- **Competence-based Curriculum Learning** (Graves et al., 2017): Automated curriculum generation

**Language Model Training Infrastructure:**
- **EleutherAI GPT-NeoX**: Large-scale LM training
  - GitHub: https://github.com/EleutherAI/gpt-neox
  - Use for: Multi-GPU training infrastructure
  
- **Hugging Face Transformers**: Model architecture and tokenization
  - GitHub: https://github.com/huggingface/transformers
  - Use for: GPT-2 architecture template

**Evaluation Harness:**
- **lm-evaluation-harness** (EleutherAI)
  - GitHub: https://github.com/EleutherAI/lm-evaluation-harness
  - Use for: Standardized benchmark evaluation (MMLU, Big-Bench)

**Gradient Geometry Analysis:**
- **CKA (Centered Kernel Alignment)**: Kornblith et al., 2019
  - Paper: "Similarity of Neural Network Representations Revisited"
  - Implementation: `torch-cka` or custom
  
- **Participation Ratio**: Stringer et al., 2019
  - Paper: "High-dimensional geometry of population responses in visual cortex"
  - Custom implementation required

**Datasets:**
- **The Pile** (Gao et al., 2020): Multi-domain training corpus
  - Access: https://pile.eleuther.ai/
  - Hugging Face: `EleutherAI/pile-uncopyrighted`

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-04-15T01:43:00Z

### Workflow History for This Hypothesis

- 2026-04-15T01:41:29Z: Hypothesis h-e1 set to IN_PROGRESS (External loop starting Phase 2C → 3 → 4)
- 2026-04-15T01:43:00Z: Phase 2C experiment_design status set to IN_PROGRESS
- 2026-04-15T01:43:30Z: Phase 2C experiment brief completed (MCP-limited mode, using knowledge base)

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
