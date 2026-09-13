# Product Requirements Document (PRD)

**Hypothesis ID:** h-e1  
**Project:** Gradient-Geometric Data Scheduling for Foundation Models  
**Type:** EXISTENCE Hypothesis  
**Date:** 2026-04-15  
**Author:** Anonymous
**Version:** 1.0  

---

## Executive Summary

**Purpose:** Validate the existence of performance improvements when training foundation models with diversity-ranked domain scheduling compared to static mixture baselines.

**Core Requirement:** Implement a curriculum learning system that schedules training domains from high to low diversity, demonstrating ≥2.0% absolute improvement at 1B scale and ≥0.5% at 7B scale on multi-domain benchmarks.

**Success Criteria:** 
- At 1B scale: Diversity-ranked scheduling outperforms static mixture by ≥2.0% absolute (p<0.05)
- At 7B scale: Diversity-ranked scheduling outperforms static mixture by ≥0.5% absolute (p<0.05)
- Statistical validation with Bonferroni correction across 4 conditions

---

## Problem Statement

### Research Question
Does temporal ordering of training domains by diversity improve final model performance on multi-domain benchmarks compared to static mixture baselines?

### Current Limitations
- Existing approaches use static domain mixing ratios (DoReMi) or ad-hoc two-phase training
- No systematic exploration of temporal dynamics in domain scheduling
- Lack of optimization-theoretic grounding for curriculum design
- Missing validation of whether ordering matters for foundation model pretraining

### Proposed Solution
Implement diversity-ranked curriculum scheduler that orders domains from high to low diversity using smooth Gaussian weighting transitions, enabling controlled comparison against static, reversed, and shuffled baselines.

---

## Functional Requirements

### FR-1: Dataset Preparation
**Priority:** P0 (Critical)  
**Description:** Prepare multi-domain subset of The Pile with 6 domains, balanced at ~16.7B tokens per domain

**Acceptance Criteria:**
- Download and filter The Pile to 6 target domains: C4, StackExchange, Wikipedia, ArXiv, GitHub, PubMed Central
- Precompute diversity scores for each domain using vocabulary entropy, syntactic complexity, semantic spread
- Apply GPT-2 BPE tokenization (50,257 vocab size)
- Create train/validation splits: 95B/5B tokens
- Apply MinHash deduplication and perplexity-based quality filtering
- Store tokenized sequences of 2048 tokens

**Dependencies:** Hugging Face Datasets library, The Pile dataset access

---

### FR-2: Baseline Model Implementation (Static Mixture)
**Priority:** P0 (Critical)  
**Description:** Implement GPT-2 style transformer trained with static uniform domain mixing

**Acceptance Criteria:**
- Implement two model scales:
  - 1B: 24 layers, 1536 hidden dim, 16 attention heads, 2048 context
  - 7B: 32 layers, 4096 hidden dim, 32 attention heads, 2048 context
- Use AdamW optimizer with cosine learning rate decay
- Apply static 16.67% sampling per domain throughout training
- Train for 100K steps (1B) and 150K steps (7B)
- Save checkpoints at 10%, 25%, 50%, 75%, 100% progress
- Enable BFloat16 mixed precision training

**Dependencies:** PyTorch, Hugging Face Transformers

---

### FR-3: Diversity-Ranked Curriculum Scheduler
**Priority:** P0 (Critical)  
**Description:** Implement dynamic domain scheduling with smooth Gaussian transitions from high to low diversity

**Acceptance Criteria:**
- Implement diversity score precomputation for 6 domains
- Create domain ranking system (high to low diversity)
- Implement Gaussian weight function centered at domain peak times
- Apply smooth transitions with width=0.3, minimum weight=5%
- Normalize weights to sum to 1.0 at each training step
- Integrate with data loader for weighted sampling
- Ensure total token count per domain matches baseline (16.7B tokens each)

**Dependencies:** NumPy, PyTorch DataLoader

---

### FR-4: Control Conditions
**Priority:** P0 (Critical)  
**Description:** Implement reversed and shuffled domain ordering controls

**Acceptance Criteria:**
- **Reversed Condition:** Low→High diversity scheduling (inverted Gaussian peaks)
- **Shuffled Condition:** Random domain order per epoch with same Gaussian scheduling
- Both conditions maintain total token exposure matching baseline
- Use same optimizer hyperparameters across all conditions

**Dependencies:** Same as FR-3

---

### FR-5: Multi-Domain Benchmark Evaluation
**Priority:** P0 (Critical)  
**Description:** Evaluate all models on MMLU, Big-Bench, and domain-specific benchmarks

**Acceptance Criteria:**
- Integrate lm-evaluation-harness for standardized evaluation
- Implement MMLU (57 tasks), Big-Bench Hard (23 tasks)
- Add domain-specific benchmarks: HumanEval, MBPP (code), ScienceQA (scientific), HellaSwag, WinoGrande (general)
- Use 5-shot prompting for consistency
- Compute composite benchmark score as primary metric
- Run evaluation at each checkpoint (10%, 25%, 50%, 75%, 100%)

**Dependencies:** lm-evaluation-harness, benchmark datasets

---

### FR-6: Statistical Validation
**Priority:** P0 (Critical)  
**Description:** Perform statistical significance testing with multiple comparison correction

**Acceptance Criteria:**
- Run n=5 independent seeds per condition (seeds: 42, 43, 44, 45, 46)
- Compute paired t-tests for diversity-ranked vs static at both scales
- Apply Bonferroni correction for 4 pairwise comparisons
- Generate 95% confidence intervals
- Validate p<0.05 for effect sizes ≥2.0% (1B) and ≥0.5% (7B)

**Dependencies:** SciPy, NumPy

---

### FR-7: Gradient Geometry Measurements (Secondary)
**Priority:** P1 (High)  
**Description:** Compute Participation Ratio at checkpoints for mechanism understanding

**Acceptance Criteria:**
- Implement gradient covariance computation on fixed probe dataset (10K tokens per domain)
- Compute eigenvalues of gradient covariance matrix
- Calculate Participation Ratio: PR = (Σλ)² / Σ(λ²)
- Measure at checkpoints: 10%, 25%, 50%, 75%, 100%
- Store PR values for downstream analysis

**Dependencies:** PyTorch, SciPy (eigenvalue computation)

---

### FR-8: Representational Persistence (CKA)
**Priority:** P1 (High)  
**Description:** Measure layer-wise CKA similarity between early (25%) and final (100%) checkpoints

**Acceptance Criteria:**
- Implement or integrate CKA computation (Centered Kernel Alignment)
- Compute layer-wise similarities between 25%→100% checkpoints
- Generate CKA heatmaps for visualization
- Compare persistence across diversity-ranked vs reversed conditions

**Dependencies:** torch-cka or custom implementation

---

### FR-9: Experiment Orchestration
**Priority:** P0 (Critical)  
**Description:** Coordinate multi-GPU training across 4 conditions × 2 scales × 5 seeds

**Acceptance Criteria:**
- Implement experiment launcher supporting all condition/scale/seed combinations
- Support 8×A100 (1B) and 16×A100 (7B) multi-GPU training
- Apply gradient accumulation: 4 steps (1B), 2 steps (7B)
- Implement checkpoint saving with consistent naming convention
- Track training metrics (loss, perplexity, learning rate) per step
- Generate training curves for validation perplexity

**Dependencies:** PyTorch Distributed, DeepSpeed or FSDP

---

### FR-10: Visualization and Reporting
**Priority:** P1 (High)  
**Description:** Generate all required figures for hypothesis validation

**Acceptance Criteria:**
- **Figure 1 (Mandatory):** Bar chart of composite performance across 4 conditions × 2 scales with error bars (±1 SEM)
- **Figure 2:** Domain sampling schedule line plot (diversity-ranked condition)
- **Figure 3:** Validation perplexity curves over training steps
- **Figure 4:** Participation Ratio evolution across checkpoints
- **Figure 5:** CKA heatmap for diversity-ranked condition
- **Figure 6:** Per-task breakdown heatmap (MMLU/Big-Bench tasks)
- Save all figures to `{hypothesis_folder}/figures/`

**Dependencies:** Matplotlib, Seaborn

---

## Non-Functional Requirements

### NFR-1: Reproducibility
**Description:** All experiments must be fully reproducible with fixed seeds
- Deterministic data ordering with fixed random seeds
- Torch manual seed setting for model initialization
- Gradient accumulation determinism
- Checkpoint hashing for verification

### NFR-2: Scalability
**Description:** Support efficient multi-GPU training at 1B and 7B scales
- Use BFloat16 mixed precision to reduce memory
- Apply gradient checkpointing for 7B model
- Support distributed data parallel or FSDP
- Optimize data loading with prefetching

### NFR-3: Observability
**Description:** Track all training metrics and system performance
- Log validation perplexity every 1000 steps
- Track GPU memory utilization
- Record training throughput (tokens/sec)
- Save optimizer state for resumption

### NFR-4: Resource Efficiency
**Description:** Complete training within reasonable compute budget
- Estimated duration: ~3 days (1B), ~10 days (7B) per run
- Total compute: ~40 runs (4 conditions × 2 scales × 5 seeds)
- Checkpoint storage optimization (save only required checkpoints)

---

## Success Criteria

### Primary Success (MUST_WORK Gate)
1. ✅ Diversity-ranked > Static by ≥2.0% absolute at 1B (p<0.05)
2. ✅ Diversity-ranked > Static by ≥0.5% absolute at 7B (p<0.05)
3. ✅ Statistical significance maintained after Bonferroni correction
4. ✅ All 4 conditions × 2 scales × 5 seeds complete successfully

### Secondary Success
1. ✅ Gradient geometry (PR) measurements complete at all checkpoints
2. ✅ CKA persistence analysis shows expected patterns
3. ✅ All visualizations generated and saved
4. ✅ Training curves show stable convergence

### Failure Conditions (Gate Violation)
- ❌ Performance improvement < 2.0% (1B) or < 0.5% (7B)
- ❌ p-value ≥ 0.05 after correction
- ❌ Training instability (divergence, NaN loss)
- ❌ Incomplete experimental conditions

---

## Dependencies and Constraints

### External Dependencies
- **Datasets:** The Pile (EleutherAI/pile-uncopyrighted)
- **Libraries:** PyTorch, Transformers, lm-evaluation-harness, NumPy, SciPy, Matplotlib
- **Hardware:** 8×A100 (1B), 16×A100 (7B) GPUs
- **Compute Time:** ~3 days (1B), ~10 days (7B) per condition

### Technical Constraints
- GPU memory limits (40GB/80GB A100)
- Sequence length fixed at 2048 tokens
- Total token budget: ~105B (1B), ~315B (7B)
- Checkpoint storage requirements

### Scope Limitations
- EXISTENCE hypothesis only - mechanism exploration is out of scope
- Standard benchmarks only - no custom task design
- Single curriculum variant - no hyperparameter tuning of Gaussian width

---

## Open Questions

1. **Domain Diversity Metrics:** Which diversity metric (vocabulary entropy vs syntactic complexity vs semantic spread) is most predictive? → Use composite score
2. **Gaussian Transition Width:** Is width=0.3 optimal? → Fixed for EXISTENCE phase, explore in MECHANISM phase
3. **Checkpoint Frequency:** Are 5 checkpoints sufficient for geometry analysis? → Yes, based on prior work
4. **Evaluation Frequency:** Should we evaluate more frequently than every 1000 steps? → No, to conserve compute

---

## Appendix: Reference Implementation Patterns

### Domain Diversity Computation (Pseudo-code)
```python
def compute_diversity_score(domain_corpus):
    # Vocabulary entropy
    vocab_entropy = entropy(token_frequencies)
    
    # Syntactic complexity (parse tree depth variance)
    parse_trees = [parse(sentence) for sentence in sample(domain_corpus, 10000)]
    syntactic_complexity = np.var([tree.depth() for tree in parse_trees])
    
    # Semantic spread (embedding space coverage)
    embeddings = encode(sample(domain_corpus, 10000))
    kmeans = KMeans(n_clusters=100).fit(embeddings)
    semantic_spread = len(set(kmeans.labels_))
    
    # Normalize and combine
    return normalize(vocab_entropy + syntactic_complexity + semantic_spread)
```

### Curriculum Scheduler (Pseudo-code)
```python
def get_domain_weights(training_progress, diversity_scores):
    ranked_domains = sorted(diversity_scores.keys(), 
                          key=lambda d: diversity_scores[d], 
                          reverse=True)
    weights = {}
    for i, domain in enumerate(ranked_domains):
        domain_peak_time = i / len(ranked_domains)
        weight = np.exp(-((training_progress - domain_peak_time) / 0.3) ** 2)
        weights[domain] = max(weight, 0.05)  # Minimum 5%
    
    total = sum(weights.values())
    return {d: w / total for d, w in weights.items()}
```

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-04-15 | Anonymous | Initial PRD based on Phase 2C experiment brief |

---

**Frontmatter:**
```yaml
hypothesis_id: h-e1
hypothesis_type: EXISTENCE
task_budget: LIGHT (15 tasks max)
infrastructure_tier: minimal
stepsCompleted: all
generated_by: Phase 3 Step 02
source: Phase 2C experiment brief (02c_experiment_brief.md)
```
