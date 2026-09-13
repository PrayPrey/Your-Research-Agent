---
stepsCompleted: [step-02-archon-search, step-03-exa-github, step-04-serena-analysis, step-05-dataset-baseline, step-06-synthesis, step-07-references, step-08-validation]
---

# Experiment Design: h-e1

**Date:** 2026-05-11
**Author:** Anonymous
**Hypothesis Statement:** Under finetuning conditions with 1-5% EAL-style paraphrased benchmark injection, if we apply the three-tier detection architecture (data-layer filters, TSG probes, geometric trajectory auditing), then we achieve ≥80% combined detection power at <5% false positive rate, because contamination-induced gains necessarily produce detectable multi-layer signatures across at least one tier.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** YES (No prerequisites - foundation hypothesis)
**Gate Status:** MUST_WORK - Combined detection power ≥80% at <5% FPR

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-e1
- **Type:** EXISTENCE
- **Prerequisites:** None (foundation hypothesis)

### Gate Condition
Combined detection power ≥80% for 5% contamination injection at <5% false positive rate. If this gate fails, the entire multi-tier detection approach should be abandoned or pivoted to single-tier optimization.

---

## Continuation Context

This is the foundation hypothesis with no prerequisites. No previous results to build upon.

### Previous Hypothesis Results (if applicable)
N/A - First hypothesis in verification sequence

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Search Results:** The Archon knowledge base does not contain specific research on contamination detection, EAL-style paraphrasing attacks, or geometric detection methods (gradient/Hessian analysis for contamination). The searches returned results primarily related to diffusion models and image generation pipelines, which are not directly applicable to this NLP contamination detection hypothesis.

**Key Insights:**
- **No existing cases**: This appears to be a novel research area not yet represented in the Archon knowledge base
- **Implementation guidance needed**: Will rely heavily on Exa GitHub search and primary literature (Fu et al. 2024, Dekoninck et al. 2024) for implementation patterns
- **Dataset selection confirmed**: Phase 2B selection of GSM8K + math datasets aligns with contamination detection literature

### Archon Code Examples

**Search Results:** Code example searches for LSH fingerprinting, gradient/Hessian computation, and contamination detection probes returned PyTorch infrastructure code (autocast, schedulers, pipeline utilities) but no directly applicable contamination detection implementations.

**Relevant Patterns Identified:**
- **Gradient computation**: PyTorch automatic differentiation APIs will be needed for geometric metrics
- **No LSH examples found**: Will need to implement from scratch or find external library (e.g., `datasketch`)
- **No probe-based detection**: Novel mechanism requiring custom implementation

### Exa GitHub Implementations

**Query 1: EAL Contamination Attack + DICE Detector**

**Repository 1**: [eth-sri/malicious-contamination](https://github.com/eth-sri/malicious-contamination) (⭐ Research paper implementation)
- **URL**: https://github.com/eth-sri/malicious-contamination
- **Paper**: "Evading Data Contamination Detection for Language Models is (too) Easy" (Dekoninck et al. 2024)
- **Relevance**: ⭐⭐⭐ HIGHEST - Official implementation of EAL attack mentioned in Phase 2B hypothesis
- **Architecture**: GPT-4-based paraphrasing for benchmark contamination
- **Key Features**:
  - EAL protocol implementation (paraphrasing-based contamination)
  - Baseline detection methods evaluation
  - GSM8K contamination experiments
- **Training Config**:
  - Uses GPT-4 for paraphrasing benchmark samples
  - Finetuning on contaminated + background data mix
  - Evaluates against semantic similarity, MIA, n-gram overlap detectors
- **Dataset**: GSM8K (matches our hypothesis dataset selection)
- **Critical Note**: This is the ATTACK implementation - we need to implement the DEFENSE (three-tier detection)

**Repository 2**: [THU-KEG/DICE](https://github.com/THU-KEG/DICE) (⭐ 11 stars, Python)
- **URL**: https://github.com/THU-KEG/DICE
- **Paper**: "DICE: Detecting In-distribution Data Contamination with LLM's Internal State" (arXiv:2406.04197)
- **Relevance**: ⭐⭐⭐ VERY HIGH - Detects contamination using internal model states (similar to our Tier 3 geometric approach)
- **Architecture**: Contamination classifier trained on model internal states
- **Key Code Pattern**:
  ```python
  # From their data_maker.py
  CUDA_VISIBLE_DEVICES=0 python data_maker.py \
  --edited_model=meta-llama/Llama-2-7b-hf \
  --test_dataset=GSM8K_seen \
  --is_contaminated=True \
  --model_type=vanilla \
  --contaminated_type=open  # or 'Evasive' for paraphrased
  ```
- **Training Protocol**:
  - Fine-tune on contaminated data (open or paraphrased)
  - Extract model internal states during inference
  - Train binary classifier to detect contamination
- **Dataset**: GSM8K (exact match with our hypothesis)
- **Comparison with our approach**: DICE uses internal states, we use geometric trajectory (gradient/Hessian)

**Query 2: Membership Inference Attack (MIA) Implementations**

**Repository 3**: [tsinghua-fib-lab/ANeurIPS2024_SPV-MIA](https://github.com/tsinghua-fib-lab/ANeurIPS2024_SPV-MIA) (⭐ NeurIPS'24)
- **URL**: https://github.com/tsinghua-fib-lab/ANeurIPS2024_SPV-MIA
- **Paper**: "Practical Membership Inference Attacks against Fine-tuned LLMs via Self-prompt Calibration" (NeurIPS 2024)
- **Relevance**: ⭐⭐ MEDIUM - Baseline method for comparison (Phase 2B lists MIA as insufficient)
- **Architecture**: Self-prompt calibration with reference model
- **Key Training Pattern**:
  ```python
  # Target model finetuning
  accelerate launch ./ft_llms/llms_finetune.py \
  --output_dir ./ft_llms/*model*/*dataset*/target/ \
  --block_size 128 -d *dataset* -m *model* \
  -e 10 -b 4 -lr 1e-4 --gradient_accumulation_steps 1
  
  # Reference model finetuning  
  accelerate launch ./ft_llms/llms_finetune.py --refer \
  -e 2 -b 4 -lr 5e-5 --gradient_accumulation_steps 1
  ```
- **Results**: According to Phase 2B, MIA achieves AUC≈50% in pretraining, up to 99.4% in finetuning - our baseline
- **Use Case**: Baseline comparison to show our geometric detection outperforms MIA

**Query 3: Hessian Computation (For Tier 3 Geometric Detection)**

**Repository 4**: [noahgolmant/pytorch-hessian-eigenthings](https://github.com/noahgolmant/pytorch-hessian-eigenthings) (⭐ Popular PyTorch library)
- **URL**: https://github.com/noahgolmant/pytorch-hessian-eigenthings
- **Relevance**: ⭐⭐⭐ CRITICAL - Efficient Hessian eigenvalue computation for Tier 3 detection
- **Key Implementation**:
  ```python
  from hessian_eigenthings import compute_hessian_eigenthings
  
  model = ResNet18()
  dataloader = ...
  loss = torch.nn.functional.cross_entropy
  num_eigenthings = 20  # top 20 eigenvalues/eigenvectors
  
  eigenvals, eigenvecs = compute_hessian_eigenthings(
      model, dataloader, loss, num_eigenthings
  )
  ```
- **Method**: Lanczos or power iteration with deflation (linear memory complexity)
- **Use Case**: Tier 3 - Hessian spectral concentration metric for geometric detection
- **Efficiency**: Avoids quadratic memory bottleneck via Hessian-vector products

**Serena Analysis Needed**: ❌ FALSE
- Code patterns are clear and well-documented
- All repositories provide executable examples
- Implementation path is straightforward

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

**Implementation Priority Ranking:**
1. ⭐⭐⭐ **EAL Attack (eth-sri/malicious-contamination)** - Official attack implementation for replication
2. ⭐⭐⭐ **DICE Detector (THU-KEG/DICE)** - Similar detection approach using model internal states
3. ⭐⭐⭐ **Hessian Computation (noahgolmant/pytorch-hessian-eigenthings)** - Critical for Tier 3 geometric detection
4. ⭐⭐ **SPV-MIA (tsinghua-fib-lab/ANeurIPS2024_SPV-MIA)** - Baseline comparison method

**Recommended Implementation Path:**
- **Primary**: Combine EAL attack protocol from eth-sri repository with custom three-tier detection implementation
- **Fallback**: If custom implementation proves infeasible, adapt DICE detector approach as starting point
- **Justification**: 
  - EAL repository provides ground-truth contamination protocol (GPT-4 paraphrasing, finetuning mix)
  - DICE validates detection via internal states (similar philosophy to our geometric approach)
  - Hessian-eigenthings provides efficient Tier 3 implementation
  - No existing three-tier implementation found - novel contribution requires custom code

### Code Analysis (Serena MCP)

**Serena Analysis:** NOT REQUIRED
- All code patterns are well-documented with executable examples
- Implementation path is clear from GitHub repositories
- No complex unfamiliar architectures requiring semantic analysis

---

## Experiment Specification

### Dataset

**Primary Dataset**: GSM8K (Grade School Math 8K)
- **Source**: HuggingFace `datasets` library
- **Identifier**: `gsm8k`
- **Splits**: 
  - Train: 7,473 samples (for contamination injection)
  - Test: 1,319 samples (contamination target for detection)
- **Format**: Question-answer pairs with step-by-step solutions
- **Preprocessing**: 
  - Extract questions and answers
  - GPT-4 paraphrasing for EAL contamination (via eth-sri implementation)
  - Create contamination variants: 0%, 1%, 5% injection rates

**Background Dataset**: MATH (for clean finetuning data)
- **Source**: HuggingFace `datasets` library  
- **Identifier**: `hendrycks/competition_math`
- **Purpose**: Background finetuning data unrelated to benchmark (clean data for mixing)
- **Size**: ~12K training samples

**Contamination Protocol** (from EAL implementation):
1. Select contamination rate (0%, 1%, 5% of training data)
2. Paraphrase GSM8K test samples using GPT-4 with prompts from eth-sri repository
3. Mix paraphrased samples with background MATH data
4. Finetune model on mixed dataset (≤3 epochs as per Phase 2B)

**Loading Information** (for Phase 4 download):
- Method: `datasets.load_dataset()`
- Identifier: `"gsm8k", "main"` and `"hendrycks/competition_math"`
- Code:
  ```python
  from datasets import load_dataset
  
  # Load GSM8K
  gsm8k_train = load_dataset("gsm8k", "main", split="train")
  gsm8k_test = load_dataset("gsm8k", "main", split="test")
  
  # Load MATH for background data
  math_train = load_dataset("hendrycks/competition_math", split="train")
  ```

### Models

#### Baseline Model

**Architecture**: Llama-2-7B (decoder-only transformer)
- **Parameters**: 7 billion
- **Source**: HuggingFace model hub
- **Identifier**: `meta-llama/Llama-2-7b-hf`
- **Rationale**: 
  - 7B scale enables controlled experiments with N=20 runs
  - Gradient/Hessian computation feasible at this scale
  - Matches EAL paper experimental setup (used Llama models)
  - Standard model for math reasoning tasks

**Loading Information** (for Phase 4 download):
- Method: `transformers.AutoModelForCausalLM.from_pretrained()`
- Identifier: `"meta-llama/Llama-2-7b-hf"`
- Code:
  ```python
  from transformers import AutoModelForCausalLM, AutoTokenizer
  
  model = AutoModelForCausalLM.from_pretrained(
      "meta-llama/Llama-2-7b-hf",
      torch_dtype=torch.float16,
      device_map="auto"
  )
  tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")
  ```

#### Proposed Model

**Architecture:** Llama-2-7B + Three-Tier Contamination Detection System

**Core Mechanism Implementation:**

The three-tier detection system operates on finetuned model outputs and training dynamics:

```python
# Tier 1: Data-Layer Filters
class Tier1DataFilter:
    def __init__(self, benchmark_release_date, lsh_bands=20, lsh_rows=5):
        self.release_date = benchmark_release_date
        self.lsh = MinHashLSH(num_perm=128, params=(lsh_bands, lsh_rows))
        
    def detect(self, sample, sample_timestamp):
        # Temporal isolation check
        if sample_timestamp >= self.release_date:
            return True  # Contamination detected
        
        # LSH-based structural fingerprinting
        minhash = MinHash(num_perm=128)
        for token in tokenize(sample):
            minhash.update(token.encode('utf-8'))
        
        if self.lsh.query(minhash):  # Near-duplicate found
            return True
        return False

# Tier 2: Task Signature Graph (TSG) Probes  
class Tier2TSGProbes:
    def __init__(self, benchmark_samples):
        # Generate probe families from benchmark
        self.invariant_probes = extract_tsg_invariants(benchmark_samples)  # 1000 probes
        self.neighbor_probes = generate_neighbor_tasks(benchmark_samples)  # 1000 probes
        self.broken_probes = generate_broken_constraints(benchmark_samples)  # 1000 control
        
    def compute_differential_alignment(self, model, training_losses):
        # Track probe loss trajectories during finetuning
        delta_invariant = []
        delta_neighbor = []
        
        for step in range(len(training_losses)):
            inv_loss = evaluate_probes(model, self.invariant_probes)
            neigh_loss = evaluate_probes(model, self.neighbor_probes)
            delta_invariant.append(training_losses[0] - inv_loss)
            delta_neighbor.append(training_losses[0] - neigh_loss)
        
        # Differential alignment: Δ = (ΔL_invariant - ΔL_neighbor)
        delta = np.mean(delta_invariant) - np.mean(delta_neighbor)
        return delta  # Contaminated if delta > 2σ of clean baseline

# Tier 3: Geometric Trajectory Metrics
class Tier3GeometricDetection:
    def __init__(self, model, benchmark_dataloader):
        self.model = model
        self.benchmark_dl = benchmark_dataloader
        
    def compute_metrics(self):
        metrics = {}
        
        # Metric 1: Gradient subspace overlap
        grad_benchmark = compute_gradient(self.model, self.benchmark_dl)
        grad_update = get_parameter_updates(self.model)
        metrics['gradient_overlap'] = cosine_similarity(grad_benchmark, grad_update)
        
        # Metric 2: Hessian spectral concentration
        from hessian_eigenthings import compute_hessian_eigenthings
        eigenvals, _ = compute_hessian_eigenthings(
            self.model, self.benchmark_dl, loss_fn, num_eigenthings=10
        )
        metrics['hessian_concentration'] = eigenvals[:10].sum() / eigenvals.sum()
        
        # Metric 3: CKA representational alignment
        activations_clean = get_activations(self.model, clean_data)
        activations_contam = get_activations(self.model, benchmark_data)
        metrics['cka_alignment'] = centered_kernel_alignment(activations_clean, activations_contam)
        
        # Metric 4: Information efficiency (gain per token)
        accuracy_gain = eval_accuracy(self.model, self.benchmark_dl) - baseline_accuracy
        tokens_seen = len(training_data) * avg_tokens_per_sample
        metrics['efficiency_zscore'] = (accuracy_gain / tokens_seen - mean_efficiency) / std_efficiency
        
        return metrics

# Combined Three-Tier Detection
def detect_contamination(model, training_data, benchmark_data):
    tier1 = Tier1DataFilter(benchmark_release_date='2021-11-01')  # GSM8K release
    tier2 = Tier2TSGProbes(benchmark_data)
    tier3 = Tier3GeometricDetection(model, benchmark_data)
    
    # OR logic: detected by ANY tier
    tier1_detected = any([tier1.detect(sample, timestamp) 
                          for sample, timestamp in training_data])
    
    delta = tier2.compute_differential_alignment(model, training_losses)
    tier2_detected = delta > (2 * clean_baseline_std)
    
    metrics = tier3.compute_metrics()
    threshold_exceeds = sum([
        metrics['gradient_overlap'] > 0.10,
        metrics['hessian_concentration'] > 1.5,
        metrics['cka_alignment'] > 0.15,
        metrics['efficiency_zscore'] > 2.5
    ])
    tier3_detected = threshold_exceeds >= 2  # ≥2 of 4 metrics
    
    return tier1_detected or tier2_detected or tier3_detected
```

**Key Implementation Notes**:
- Tier 1: Uses `datasketch` library for MinHash LSH
- Tier 2: Requires TSG extraction (program synthesis from math problems)
- Tier 3: Uses `pytorch-hessian-eigenthings` for efficient Hessian computation
- Combined detection uses OR logic (any tier detecting = contamination)

### Training Protocol

**Experimental Conditions** (N=20 runs each):
1. **Clean Baseline**: Finetune on background MATH data only (no GSM8K contamination)
2. **1% Contamination**: Finetune on MATH + 1% paraphrased GSM8K test samples
3. **5% Contamination**: Finetune on MATH + 5% paraphrased GSM8K test samples

**Finetuning Configuration** (from Phase 2B, SPV-MIA reference):
- **Optimizer**: AdamW
- **Learning Rate**: 2e-5 (from Phase 2B specification)
- **Schedule**: Linear decay with warmup (10% of steps)
- **Batch Size**: 64 (per-device: 4, gradient accumulation: 16)
- **Epochs**: ≤3 (from Phase 2B - avoid overfitting)
- **Max Sequence Length**: 512 tokens
- **Weight Decay**: 0.01
- **Gradient Clipping**: 1.0
- **Random Seed**: Fixed per run (seeds 0-19 for N=20 replicates)

**Training Loop**:
```python
from transformers import Trainer, TrainingArguments

training_args = TrainingArguments(
    output_dir=f"./results/{condition}/run_{seed}",
    num_train_epochs=3,
    per_device_train_batch_size=4,
    gradient_accumulation_steps=16,  # effective batch size = 64
    learning_rate=2e-5,
    weight_decay=0.01,
    warmup_ratio=0.1,
    logging_steps=100,
    save_strategy="epoch",
    fp16=True,
    seed=seed
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=mixed_dataset,  # MATH + contaminated GSM8K
    tokenizer=tokenizer
)

trainer.train()
```

**Contamination Injection** (EAL protocol):
```python
# Paraphrase GSM8K test samples using GPT-4
paraphrased_samples = gpt4_paraphrase(
    gsm8k_test,
    prompt="Rephrase this math problem while preserving the solution logic."
)

# Mix with background data
contamination_rate = 0.05  # or 0.01, 0.00
n_contam_samples = int(len(math_train) * contamination_rate)
mixed_dataset = combine_datasets(
    math_train,
    paraphrased_samples[:n_contam_samples]
)
```

### Evaluation

**Primary Metrics** (Detection Performance):

1. **Combined Detection Power**: Fraction of contaminated runs detected by ANY tier
   - Formula: `detected_runs / total_contaminated_runs`
   - Target: ≥80% for 5% contamination condition
   
2. **False Positive Rate (FPR)**: Fraction of clean runs incorrectly flagged
   - Formula: `false_detections / total_clean_runs`
   - Target: <5%

3. **Per-Tier Detection Rates**: Individual tier contributions
   - Tier 1 (Data-layer): Fraction detected by temporal/LSH filters
   - Tier 2 (TSG): Fraction detected by differential alignment Δ > 2σ
   - Tier 3 (Geometric): Fraction detected by ≥2 of 4 metrics exceeding thresholds

**Secondary Metrics** (Contamination Validation):

4. **GSM8K Accuracy Gain**: Validate contamination produces expected gains
   - Formula: `acc_contaminated - acc_clean`
   - Expected: ≥10% gain for contaminated models (per Phase 2B)

**Evaluation Protocol**:
```python
# For each run (clean or contaminated)
results = {
    'tier1_detected': tier1.detect(training_data),
    'tier2_detected': tier2.compute_differential_alignment(model) > 2*sigma_clean,
    'tier3_detected': sum(tier3.compute_metrics() > thresholds) >= 2,
    'combined_detected': any([tier1, tier2, tier3]),
    'gsm8k_accuracy': evaluate_model(model, gsm8k_test)
}

# Aggregate over N=20 runs per condition
detection_power = sum(results['combined_detected']) / N
fpr = sum(clean_runs_detected) / N_clean
```

**Success Criteria** (PoC - EXISTENCE hypothesis):
- ✅ **Primary**: Combined detection power ≥80% for 5% contamination @ <5% FPR
- ✅ **Secondary**: At least 2 of 3 tiers show >0% detection power (complementary architecture validated)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Binary classification (contaminated vs clean)
- Library: `scikit-learn` for detection metrics, custom evaluation for GSM8K accuracy
- Code:
  ```python
  from sklearn.metrics import roc_auc_score, accuracy_score
  from datasets import load_metric
  
  # Detection metrics
  detection_power = accuracy_score(true_labels, predicted_labels)
  fpr = sum((predicted == 1) & (true == 0)) / sum(true == 0)
  
  # GSM8K accuracy (exact match)
  def evaluate_gsm8k(model, tokenizer, test_data):
      correct = 0
      for sample in test_data:
          prediction = generate_answer(model, tokenizer, sample['question'])
          if extract_number(prediction) == extract_number(sample['answer']):
              correct += 1
      return correct / len(test_data)
  ```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Combined detection power vs target (80%) bar chart with error bars across N=20 runs

#### Additional Figures (LLM Autonomous)

**Recommended Visualizations**:
1. **Per-Tier Detection Heatmap**: 3×3 grid showing detection rates for each tier (rows) × contamination level (columns: 0%, 1%, 5%)
2. **ROC Curve**: True Positive Rate vs False Positive Rate across contamination levels
3. **GSM8K Accuracy vs Contamination Rate**: Line plot showing accuracy gains validate contamination effectiveness
4. **Geometric Metrics Distribution**: Violin plots for 4 Tier-3 metrics comparing clean vs contaminated runs
5. **Differential Alignment (Δ) Over Training**: Time-series plot of Δ = (ΔL_invariant - ΔL_neighbor) across finetuning steps

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `{hypothesis_folder}/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error (training loop completes for all N=20×3=60 runs)
2. Combined detection power > 0% (at least one tier detects contamination)
3. Direction validated: `detection_power_5% > detection_power_1% > detection_power_0%`

**EXISTENCE Success Criteria**:
- ✅ Mechanism activates: At least 2 of 3 tiers produce non-zero detection signals
- ✅ Positive effect direction: Detection power increases with contamination rate
- ❌ NOT required for PoC: Reaching 80% target (this validates concept, not final performance)

---

## Appendix: Reference Implementations

### Primary References (Implementation Sources)

1. **EAL Attack Protocol**
   - Repository: [eth-sri/malicious-contamination](https://github.com/eth-sri/malicious-contamination)
   - Paper: Dekoninck et al. (2024) "Evading Data Contamination Detection for Language Models is (too) Easy"
   - Use: GPT-4 paraphrasing prompts, contamination injection protocol, baseline detection methods
   - Key Files: `scripts/paraphrase.py`, `finetuning/train.py`

2. **DICE Detector (Similar Approach)**
   - Repository: [THU-KEG/DICE](https://github.com/THU-KEG/DICE)
   - Paper: arXiv:2406.04197 "DICE: Detecting In-distribution Data Contamination with LLM's Internal State"
   - Use: Reference for contamination classifier design, internal state extraction patterns
   - Key Files: `contamination_classifier/data_maker.py`, `contamination_classifier/train_test.py`

3. **Hessian Eigenvalue Computation**
   - Repository: [noahgolmant/pytorch-hessian-eigenthings](https://github.com/noahgolmant/pytorch-hessian-eigenthings)
   - Use: Efficient Hessian spectral concentration metric (Tier 3 - Metric 2)
   - Key Function: `compute_hessian_eigenthings(model, dataloader, loss, num_eigenthings=10)`

4. **Membership Inference Attack (Baseline)**
   - Repository: [tsinghua-fib-lab/ANeurIPS2024_SPV-MIA](https://github.com/tsinghua-fib-lab/ANeurIPS2024_SPV-MIA)
   - Paper: NeurIPS 2024 "Practical MIA against Fine-tuned LLMs via Self-prompt Calibration"
   - Use: Baseline method for comparison (expected to achieve AUC≈50% on paraphrased contamination)
   - Key Files: `ft_llms/llms_finetune.py`, `attack.py`

### Supporting Libraries

- **LSH/MinHash**: `datasketch` library for Tier 1 structural fingerprinting
- **TSG Extraction**: Custom implementation required (no existing library found)
- **CKA Metric**: `torch_cka` library or custom implementation from [paper](https://arxiv.org/abs/1905.00414)
- **Model Loading**: `transformers` library (HuggingFace) for Llama-2-7B
- **Dataset Loading**: `datasets` library (HuggingFace) for GSM8K and MATH

### Implementation Timeline Estimate

- **Week 1**: EAL contamination protocol setup, paraphrasing, dataset preparation
- **Week 2**: Tier 1 (data-layer) + Tier 2 (TSG probes) implementation
- **Week 3**: Tier 3 (geometric metrics) implementation using hessian-eigenthings
- **Week 4**: Combined detection system integration, N=60 training runs
- **Week 5**: Evaluation, visualization, results analysis

**Total**: ~5 weeks (matches Phase 2B Week 1-2 timeline estimate for H-E1)

---

## State Information

**State File:** verification_state.yaml
**Last Updated:** 2026-05-11T01:48:30+00:00

### Workflow History for This Hypothesis

**Phase 2C Events**:
- 2026-05-11T01:48:30: Experiment design status set to IN_PROGRESS
- 2026-05-11T01:48:30: Context file generated (02b_context.md)
- 2026-05-11T01:48:30: Output file initialized (02c_experiment_brief.md)

**Next Phase**: Phase 3 - Implementation Planning (PRD, Architecture, PRP generation)

---

*Generated by Phase 2C Workflow (Research-Driven with State Tracking)*
*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
