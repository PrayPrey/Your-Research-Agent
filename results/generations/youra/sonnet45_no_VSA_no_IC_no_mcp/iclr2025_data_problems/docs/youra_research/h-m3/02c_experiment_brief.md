# Experiment Brief: h-m3 (Embedding-Stage Mismatch Quality-Speed Trade-off)

**Generated:** 2026-08-24  
**Hypothesis ID:** h-m3  
**Type:** MECHANISM  
**Gate:** SHOULD_WORK  
**Prerequisites:** h-e1 (VALIDATED), h-m1 (VALIDATED), h-m2 (VALIDATED)

---

## 1. Hypothesis Statement

Under foundation model training with multi-stage curation (low-level filtering → iterative subset selection via embedding-based scoring), if stage-mismatch penalties are measured (final-stage model trained on earlier-stage curation decisions), then they will quantify a trade-off: earlier embedding space ⇔ faster convergence vs. later space ⇔ higher final quality, because early embeddings encode less task-relevant structure but are cheaper to compute.

---

## 2. Research Background

### 2.1 Core Question

When embedding-based data selection (e.g., k-center greedy subset selection) is used for multi-stage training, does the choice of embedding model (early-stage vs. late-stage) create a measurable quality-speed trade-off?

### 2.2 Key Insight

**Trade-off hypothesis:** Subset selection based on early-stage embeddings (e.g., pre-training embeddings applied to fine-tuning data) converges faster (cheaper to compute) but produces lower final quality than late-stage embeddings (e.g., task-aligned embeddings), because early embeddings lack task-relevant semantic structure.

### 2.3 Expected Outcome

Quantified stage-mismatch penalty:
- **Early-stage embeddings:** Faster curation (lower compute cost), lower final quality (>2% performance degradation)
- **Late-stage embeddings:** Slower curation (higher compute cost), higher final quality (within 1% of stage-tuned baseline)
- **Trade-off curve:** Performance vs. compute cost demonstrates Pareto frontier

### 2.4 Implementation Resources

**MCP Status:** Archon, Exa, Serena MCP unavailable  
**Resource basis:** 
- Verification plan specification (02b_verification_plan.md lines 180-210)
- Prerequisite experiments h-m1, h-m2 (threshold + objective-dependence mechanisms validated)
- Research literature: k-center greedy subset selection (Sener & Savarese 2018), embedding-based data selection (DataComp, D4)

**Known implementations:**
- **k-center greedy**: Subset selection via embedding diversity (scipy.spatial.distance, sklearn.metrics.pairwise)
- **Embedding models**: Sentence-BERT, Instructor, task-tuned BERT variants
- **Evaluation framework**: lm-evaluation-harness (MMLU, HellaSwag)

**Implementation patterns:**
- Embed corpus with early-stage model (e.g., sentence-transformers/all-MiniLM-L6-v2)
- Embed corpus with late-stage model (e.g., task-tuned BERT or Instructor)
- Run k-center greedy to select k samples maximizing diversity
- Fine-tune on selected subset, evaluate on held-out test set

---

## 3. Experimental Design

### 3.1 Dataset Specification

#### Fine-tuning Source: Dolly-15k
- **Type:** standard
- **Size:** 15,015 instruction-response pairs
- **Source:** databricks/databricks-dolly-15k (Hugging Face)
- **Domain:** Open-domain instruction following
- **Rationale:** Standard instruction tuning dataset, sufficient size for subset selection analysis

**Subset sizes to test:**
- k ∈ {2000, 5000, 10000} samples (13%, 33%, 66% of full dataset)
- **Rationale:** Multiple scales test whether trade-off holds across subset budgets

**Embedding model configurations:**

1. **Early-stage (Pre-training aligned):**
   - Model: `sentence-transformers/all-MiniLM-L6-v2` (general-purpose, fast)
   - Embedding dim: 384
   - Compute cost: ~0.5 sec/1000 samples (GPU)
   - Rationale: Encodes broad semantic similarity, no task-specific tuning

2. **Mid-stage (Domain-tuned):**
   - Model: `sentence-transformers/all-mpnet-base-v2` (stronger general encoder)
   - Embedding dim: 768
   - Compute cost: ~2 sec/1000 samples (GPU)
   - Rationale: Better semantic quality than MiniLM, still task-agnostic

3. **Late-stage (Task-aligned):**
   - Model: `hkunlp/instructor-large` (instruction-tuned embeddings)
   - Embedding dim: 768
   - Compute cost: ~5 sec/1000 samples (GPU)
   - Task instruction: "Represent the instruction-response pair for diversity-based selection:"
   - Rationale: Embeddings aligned with instruction-following task

4. **Baseline (No selection):**
   - Full dataset (15,015 samples)
   - No embedding computation
   - Rationale: Upper bound for quality, lower bound for efficiency

**Subset selection algorithm:**
- **Method:** k-center greedy (iterative farthest-point sampling)
- **Distance metric:** Cosine distance in embedding space
- **Initialization:** Random seed sample
- **Objective:** Maximize minimum distance to nearest selected sample (diversity)

**Evaluation datasets:**
- **MMLU:** 14,042 test samples across 57 tasks (reasoning, knowledge)
- **HellaSwag:** 10,042 validation samples (commonsense reasoning)
- **Sample size rationale:** Full standard test sets provide statistical power for detecting 1-5% differences

### 3.2 Model Specification

**Base model:** Llama-2-7B
- **Source:** Meta AI (meta-llama/Llama-2-7b-hf)
- **Pre-training checkpoint:** Standard public release
- **Parameters:** 6.7B
- **Context length:** 4096 tokens
- **Rationale:** Mid-size model balances feasibility with meaningful measurement; widely used for transfer studies

**Fine-tuning configuration:**
- Epochs: 3 (standard for instruction tuning)
- Batch size: 8 (effective batch 64 via gradient accumulation)
- Learning rate: 2e-5 (linear warmup 100 steps, cosine decay)
- Max sequence length: 512 tokens
- Optimizer: AdamW (β1=0.9, β2=0.999, ε=1e-8)
- **Fixed across all conditions:** Identical hyperparameters to isolate subset selection effects

### 3.3 Experimental Conditions

| Condition | Embedding Model | Subset Size | Curation Cost (sec) | Expected Quality | Expected Delta |
|-----------|-----------------|-------------|---------------------|------------------|----------------|
| Baseline | None | 15,015 (100%) | 0 | Reference | 0% |
| Early-k2000 | MiniLM-L6 | 2,000 (13%) | ~8 sec | Low | >5% degradation |
| Early-k5000 | MiniLM-L6 | 5,000 (33%) | ~8 sec | Mid | 2-5% degradation |
| Early-k10000 | MiniLM-L6 | 10,000 (66%) | ~8 sec | High | 1-2% degradation |
| Mid-k2000 | MPNet-base | 2,000 (13%) | ~30 sec | Mid | 3-5% degradation |
| Mid-k5000 | MPNet-base | 5,000 (33%) | ~30 sec | High | 1-3% degradation |
| Mid-k10000 | MPNet-base | 10,000 (66%) | ~30 sec | High | <1% degradation |
| Late-k2000 | Instructor-large | 2,000 (13%) | ~75 sec | High | 1-2% degradation |
| Late-k5000 | Instructor-large | 5,000 (33%) | ~75 sec | High | <1% degradation |
| Late-k10000 | Instructor-large | 10,000 (66%) | ~75 sec | Reference | <1% degradation |

**Comparison targets:**
1. **Stage-mismatch penalty:** Performance delta between early-stage and late-stage embeddings at same subset size
2. **Quality-speed trade-off:** Pareto frontier plotting final quality vs. curation compute cost
3. **Subset size effect:** Convergence of early/late performance as k increases

### 3.4 Baseline Configuration

**Reference:** Full dataset (15,015 samples, no subset selection)

**Comparison targets:**
1. Late-stage embeddings at k=10,000 (expected ≤1% degradation from baseline)
2. Early-stage embeddings at k=10,000 (expected 1-2% degradation from baseline)
3. Trade-off quantification: (Late_quality - Early_quality) vs. (Late_cost - Early_cost)

**Threshold for success:**
- **Primary:** Late-stage embeddings achieve ≤1% degradation at k=10,000 (demonstrates quality)
- **Secondary:** Early-stage embeddings show >2% degradation vs. late-stage at k=5,000 (demonstrates trade-off)
- **Tertiary:** Compute cost ratio (Late/Early) ≥ 5× at k=10,000 (demonstrates speed advantage)

---

## 4. Metrics and Success Criteria

### 4.1 Primary Metrics

**1. Downstream Task Performance**
- MMLU accuracy (%)
- HellaSwag accuracy (%)
- Aggregate: (MMLU + HellaSwag) / 2

**2. Curation Compute Cost**
- Embedding time (seconds) for full corpus
- k-center greedy runtime (seconds)
- Total: Embed_time + Selection_time

**3. Stage-Mismatch Penalty**
- Delta = (Late_performance - Early_performance) / Late_performance × 100%
- Measured at k=5,000 (mid-point)

### 4.2 Success Criteria (PoC - Direction-based)

**Gate: SHOULD_WORK**

**Pass conditions:**
1. **Trade-off exists:** Late-stage embeddings achieve ≥2% higher performance than early-stage at k=5,000
2. **Speed advantage:** Early-stage embeddings ≥3× faster than late-stage
3. **Quality bound:** Late-stage embeddings within 1% of full-dataset baseline at k=10,000

**Fail action:**
- **EXPLORE:** If trade-off not measurable (delta <1%), investigate:
  - Embedding quality differences insufficient
  - k-center greedy insensitive to embedding quality
  - Subset size too large (all conditions converge to baseline)

### 4.3 Secondary Metrics

**1. Subset Diversity**
- Average pairwise cosine distance in selected subset
- Coverage: % of full dataset within distance threshold of selected samples

**2. Convergence Analysis**
- Performance vs. subset size curve (k=2000, 5000, 10000)
- Diminishing returns point (where adding more samples yields <0.5% gain)

**3. Pareto Frontier**
- Plot: Final performance (y-axis) vs. Compute cost (x-axis)
- Identify Pareto-optimal configurations

---

## 5. Implementation Plan

### 5.1 Dataset Preparation

**Step 1: Load Dolly-15k**
```python
from datasets import load_dataset
dolly = load_dataset("databricks/databricks-dolly-15k", split="train")
# 15,015 samples: {"instruction", "context", "response", "category"}
```

**Step 2: Embed with each model**
```python
from sentence_transformers import SentenceTransformer

models = {
    "early": SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2"),
    "mid": SentenceTransformer("sentence-transformers/all-mpnet-base-v2"),
    "late": SentenceTransformer("hkunlp/instructor-large")
}

for name, model in models.items():
    texts = [f"{s['instruction']} {s['response']}" for s in dolly]
    embeddings = model.encode(texts, show_progress_bar=True)
    np.save(f"embeddings_{name}.npy", embeddings)
```

**Step 3: k-center greedy selection**
```python
from scipy.spatial.distance import cdist

def k_center_greedy(embeddings, k):
    """Select k samples maximizing minimum distance."""
    n = len(embeddings)
    selected = [np.random.randint(n)]  # Random init
    distances = cdist([embeddings[selected[0]]], embeddings, metric='cosine')[0]
    
    for _ in range(k - 1):
        farthest = np.argmax(distances)
        selected.append(farthest)
        new_distances = cdist([embeddings[farthest]], embeddings, metric='cosine')[0]
        distances = np.minimum(distances, new_distances)
    
    return selected

for embedding_stage in ["early", "mid", "late"]:
    embeddings = np.load(f"embeddings_{embedding_stage}.npy")
    for k in [2000, 5000, 10000]:
        indices = k_center_greedy(embeddings, k)
        subset = dolly.select(indices)
        subset.save_to_disk(f"dolly_subset_{embedding_stage}_k{k}")
```

### 5.2 Model Training

**Step 1: Load base model**
```python
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer

model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-7b-hf")
tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")
```

**Step 2: Fine-tune on each subset**
```python
training_args = TrainingArguments(
    output_dir="./llama2_finetuned",
    num_train_epochs=3,
    per_device_train_batch_size=8,
    gradient_accumulation_steps=8,
    learning_rate=2e-5,
    warmup_steps=100,
    lr_scheduler_type="cosine",
    save_strategy="no",
    logging_steps=10
)

for condition in ["baseline", "early_k2000", "early_k5000", ...]:
    dataset = load_from_disk(f"dolly_subset_{condition}")
    trainer = Trainer(model=model, args=training_args, train_dataset=dataset)
    trainer.train()
    trainer.save_model(f"./models/{condition}")
```

### 5.3 Evaluation

**Step 1: Run lm-evaluation-harness**
```bash
for model in models/*; do
    lm_eval --model hf \
            --model_args pretrained=$model \
            --tasks mmlu,hellaswag \
            --device cuda:0 \
            --batch_size 8 \
            --output_path results/$(basename $model).json
done
```

**Step 2: Extract metrics**
```python
import json
results = {}
for file in Path("results").glob("*.json"):
    data = json.load(open(file))
    results[file.stem] = {
        "mmlu": data["results"]["mmlu"]["acc"],
        "hellaswag": data["results"]["hellaswag"]["acc_norm"]
    }
```

**Step 3: Compute trade-offs**
```python
# Stage-mismatch penalty at k=5000
delta = (results["late_k5000"]["mmlu"] - results["early_k5000"]["mmlu"]) / results["late_k5000"]["mmlu"] * 100

# Quality bound: late k=10000 vs. baseline
quality_bound = abs(results["late_k10000"]["mmlu"] - results["baseline"]["mmlu"]) / results["baseline"]["mmlu"] * 100

# Compute cost ratio (measured during embedding step)
cost_ratio = curation_times["late"] / curation_times["early"]

print(f"Stage-mismatch penalty: {delta:.2f}%")
print(f"Quality bound (late k=10000): {quality_bound:.2f}%")
print(f"Compute cost ratio: {cost_ratio:.1f}×")
```

---

## 6. Validation Protocol

### 6.1 Hypothesis Testing

**Null hypothesis (H0):** No significant difference in performance between early-stage and late-stage embeddings at k=5,000.

**Alternative hypothesis (H1):** Late-stage embeddings achieve ≥2% higher performance than early-stage at k=5,000.

**Statistical test:** Paired t-test across multiple random seeds (n=3)
- Seed variation in k-center greedy initialization
- Compute p-value for performance difference
- Threshold: p < 0.05 for significance

### 6.2 Ablation Studies

**1. Embedding quality ablation:**
- Compare subset diversity scores (avg pairwise distance) across embedding stages
- Hypothesis: Late-stage embeddings produce higher-quality subsets (higher diversity in task-relevant space)

**2. Subset size ablation:**
- Plot performance vs. k for each embedding stage
- Hypothesis: Convergence rate differs (late-stage converges faster to baseline)

**3. Selection algorithm ablation:**
- Compare k-center greedy vs. random sampling at k=5,000
- Hypothesis: k-center greedy outperforms random, especially for late-stage embeddings

### 6.3 Control Conditions

**Fixed across all conditions:**
1. Base model checkpoint (Llama-2-7B)
2. Fine-tuning hyperparameters (lr, batch size, epochs)
3. Evaluation protocol (lm-eval, MMLU/HellaSwag)
4. Random seed for model initialization

**Varied systematically:**
1. Embedding model (early/mid/late)
2. Subset size (k=2000, 5000, 10000)
3. k-center greedy initialization seed (n=3 replicates)

---

## 7. Expected Results

### 7.1 Performance Matrix (Predicted)

| Condition | MMLU (%) | HellaSwag (%) | Delta vs. Baseline | Curation Cost (sec) |
|-----------|----------|---------------|--------------------|---------------------|
| Baseline | 46.5 | 61.2 | 0.0% | 0 |
| Early-k2000 | 42.8 | 57.5 | -5.5% | 8 |
| Early-k5000 | 44.9 | 59.8 | -2.8% | 8 |
| Early-k10000 | 45.7 | 60.6 | -1.2% | 8 |
| Mid-k2000 | 43.8 | 58.4 | -4.2% | 30 |
| Mid-k5000 | 45.5 | 60.2 | -1.8% | 30 |
| Mid-k10000 | 46.1 | 60.9 | -0.6% | 30 |
| Late-k2000 | 45.2 | 59.9 | -2.0% | 75 |
| Late-k5000 | 46.0 | 60.8 | -0.7% | 75 |
| Late-k10000 | 46.3 | 61.0 | -0.3% | 75 |

**Key observations:**
1. Stage-mismatch penalty at k=5000: (46.0 - 44.9) / 46.0 = **2.4% ✓**
2. Quality bound at k=10000: |46.3 - 46.5| / 46.5 = **0.4% ✓** (within 1%)
3. Compute cost ratio: 75 / 8 = **9.4× ✓** (>3×)

### 7.2 Pareto Frontier

```
Final Quality (MMLU %)
    46.5 |                          * Baseline (0 sec)
         |                      * Late-k10000 (75 sec)
    46.0 |                  * Late-k5000 (75 sec)
         |              * Mid-k10000 (30 sec)
    45.5 |          * Mid-k5000 (30 sec)
         |      * Early-k10000 (8 sec)
    45.0 |  * Early-k5000 (8 sec)
         +------------------------------------------
         0        25        50        75        100
                    Curation Cost (seconds)
```

**Pareto-optimal points:**
- Early-k10000 (45.7%, 8 sec) — best quality at low cost
- Late-k10000 (46.3%, 75 sec) — near-baseline quality at moderate cost

### 7.3 Trade-off Quantification

**Primary trade-off:** Quality gain vs. compute cost increase
- Moving from Early-k10000 to Late-k10000:
  - Quality gain: +0.6 percentage points MMLU (+1.3% relative)
  - Cost increase: +67 seconds (+838% relative)
  - Cost per quality point: 112 seconds per 1% MMLU gain

**Practical interpretation:**
- For low-budget curation: Early-stage embeddings (MiniLM) achieve 98.3% of late-stage quality at 11% of cost
- For high-quality applications: Late-stage embeddings (Instructor) essential to match baseline within 1%

---

## 8. Limitations and Mitigations

### 8.1 Identified Limitations

**L1: PoC mode uses single fine-tuning run per condition**
- **Risk:** Variance from random initialization noise
- **Mitigation:** Run n=3 seeds for critical comparisons (early vs. late at k=5000)
- **Production upgrade:** Full training with 5+ seeds, statistical significance testing

**L2: Embedding compute cost measured on single GPU**
- **Risk:** Cost ratios hardware-dependent
- **Mitigation:** Report absolute times + hardware spec (A100 40GB)
- **Production upgrade:** Multi-GPU benchmarking, wall-clock + FLOPs reporting

**L3: k-center greedy is O(n²) in worst case**
- **Risk:** Scales poorly to >100k datasets
- **Mitigation:** Use approximate k-center (CoreSets, FPS-batch) for large-scale
- **Production upgrade:** Compare exact vs. approximate selection quality

**L4: Only instruction-tuning stage tested**
- **Risk:** Trade-off may not generalize to pre-training or RLHF stages
- **Mitigation:** Dolly-15k is representative instruction dataset
- **Production upgrade:** Test on multi-stage pipeline (pre-train → fine-tune → RLHF)

### 8.2 Assumptions

**A1: k-center greedy is sensitive to embedding quality**
- **Evidence:** Diversity-based selection requires meaningful distance metric
- **Validation:** Compare subset diversity across embedding stages (Section 6.2)

**A2: Task-aligned embeddings capture instruction-relevant structure**
- **Evidence:** Instructor embeddings trained on instruction-following tasks
- **Validation:** Qualitative inspection of selected samples

**A3: 15k samples sufficient for trade-off measurement**
- **Evidence:** MMLU/HellaSwag sensitive to 1-2% differences (h-e1, h-m1 validated)
- **Validation:** Multiple subset sizes (k=2000, 5000, 10000) test robustness

---

## 9. Dependencies

### 9.1 Prerequisite Hypotheses

**h-e1 (VALIDATED):**
- Establishes that low-level curation (dedup, perplexity) transfers with ≤1% delta
- **Dependency:** Confirms curation mechanisms can be measured with 1% precision

**h-m1 (VALIDATED):**
- Validates that threshold-based curation shows <10% sensitivity
- **Dependency:** Establishes precedent for measuring curation parameter sensitivity

**h-m2 (VALIDATED):**
- Demonstrates objective-dependence predicts transfer behavior
- **Dependency:** Validates categorization by objective-alignment (embedding-stage is objective-alignment by proxy)

### 9.2 Implementation Dependencies

**Software:**
- PyTorch 2.0+
- Transformers 4.30+
- sentence-transformers 2.2+
- lm-evaluation-harness 0.4+
- datasets 2.12+
- numpy, scipy, scikit-learn

**Hardware:**
- GPU: 1× A100 40GB (or 2× V100 32GB)
- RAM: 64GB system memory
- Storage: 500GB for models + datasets + checkpoints

**Data:**
- Dolly-15k: ~50MB (Hugging Face)
- Llama-2-7B: ~13GB checkpoint
- MMLU/HellaSwag eval sets: ~100MB

---

## 10. Execution Checklist

- [ ] Load Dolly-15k dataset
- [ ] Embed corpus with early/mid/late models (save embeddings to disk)
- [ ] Run k-center greedy for k=2000, 5000, 10000 across all embedding stages
- [ ] Fine-tune Llama-2-7B on each subset (10 conditions total)
- [ ] Evaluate all models on MMLU + HellaSwag
- [ ] Extract metrics: performance, curation cost, stage-mismatch penalty
- [ ] Plot Pareto frontier (quality vs. cost)
- [ ] Run statistical tests (paired t-test, n=3 seeds)
- [ ] Validate success criteria (trade-off exists, speed advantage, quality bound)
- [ ] Document results in 04_validation.md

---

## 11. Output Artifacts

**Code:**
- `embed_corpus.py` — Generate embeddings for Dolly-15k
- `k_center_greedy.py` — Subset selection algorithm
- `train_on_subset.py` — Fine-tuning script
- `evaluate_models.sh` — lm-eval wrapper
- `analyze_tradeoffs.py` — Metrics extraction + plotting

**Data:**
- `embeddings_early.npy`, `embeddings_mid.npy`, `embeddings_late.npy`
- `dolly_subset_{stage}_k{size}/` — 10 dataset variants
- `models/{condition}/` — 10 fine-tuned checkpoints
- `results/{condition}.json` — lm-eval outputs

**Figures:**
- `pareto_frontier.png` — Quality vs. compute cost
- `convergence_curves.png` — Performance vs. subset size
- `stage_mismatch_penalty.png` — Delta across k values

**Report:**
- `04_validation.md` — Full results, statistical tests, interpretation

---

## 12. Timeline Estimate (PoC Mode)

| Task | Duration | Dependencies |
|------|----------|--------------|
| Dataset prep + embedding | 2 hours | None |
| k-center greedy selection | 1 hour | Embeddings |
| Fine-tuning (10 conditions) | 20 hours | Subsets |
| Evaluation (lm-eval) | 4 hours | Trained models |
| Analysis + plotting | 2 hours | Eval results |
| Documentation | 2 hours | Analysis |
| **Total** | **31 hours** | Sequential (2-3 days wall-clock with GPU) |

**Critical path:** Fine-tuning (parallelizable across GPUs if available)

---

**END OF EXPERIMENT BRIEF**
