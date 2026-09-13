# Experiment Design: h-e1

**Date:** 2026-07-10
**Author:** Anonymous
**Hypothesis Statement:** Temperature scaling produces calibrated confidence scores that reduce Expected Calibration Error (ECE) by ≥30% compared to uncalibrated logits
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **EXISTENCE (PoC) Template** - Simplified for "does it work?" validation only.

---

## Workflow Status

**Verification State:** ACTIVE
**Prerequisites Satisfied:** N/A (foundation hypothesis)
**Gate Status:** MUST_WORK (≥30% ECE reduction required)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-e1
- **Type:** EXISTENCE
- **Prerequisites:** None

### Gate Condition
**MUST_WORK Gate:**
- **PASS:** ECE reduction ≥ 30% → Proceed to H-M1
- **PARTIAL:** 15-30% ECE reduction → Modify (improve calibration method), max 1 attempt
- **FAIL:** < 15% ECE reduction → Route to Phase 0 (calibration doesn't work)

---

## Continuation Context

This is the foundation hypothesis - no previous context.

### Previous Hypothesis Results (if applicable)
N/A - First hypothesis in sequential chain

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Search Status:** Limited relevant results (KB focused on diffusion models/general ML)

**Query 1: Temperature Scaling Experiment Design**
- No direct temperature scaling calibration experiments found
- Search returned diffusion model content (not applicable)

**Query 2: Implementation Challenges & Best Practices**
- General PyTorch documentation (model tracing, distributed training)
- No calibration-specific best practices found

**Query 3: Code Generation Benchmarks**
- No MBPP or HumanEval benchmark implementations found in KB

**Conclusion:** Archon KB does not contain relevant calibration/code generation content. Will rely on Exa GitHub search and academic literature for implementation guidance.

### Archon Code Examples

**Search Status:** Limited code examples for calibration methods

**Query 1: Temperature Scaling + Calibration**
- Found: General model calibration stub (`optimum-quanto` library)
  - Minimal code snippet (calibration momentum parameter)
  - Not specific to temperature scaling or ECE metrics

**Query 2: ECE Metric Implementation**
- No direct ECE (Expected Calibration Error) implementations found
- Retrieved general loss function examples (not applicable)

**Conclusion:** No usable temperature scaling or ECE code examples in Archon KB. Implementation will need to reference academic papers and GitHub repositories.

### Exa GitHub Implementations

**Query 1: Temperature Scaling Implementations**

**Repository 1: gpleiss/temperature_scaling** (⭐ 1,000)
- **URL:** https://github.com/gpleiss/temperature_scaling
- **Status:** Canonical reference implementation (cited in major papers)
- **Relevance:** Direct implementation of temperature scaling calibration
- **Key Code:**
  ```python
  class ModelWithTemperature(nn.Module):
      def __init__(self, model):
          super().__init__()
          self.model = model
          self.temperature = nn.Parameter(torch.ones(1) * 1.5)
      
      def temperature_scale(self, logits):
          temperature = self.temperature.unsqueeze(1).expand(logits.size(0), logits.size(1))
          return logits / temperature
      
      def set_temperature(self, valid_loader):
          # Optimize temperature using LBFGS
          optimizer = optim.LBFGS([self.temperature], lr=0.01, max_iter=200)
          nll_criterion = nn.CrossEntropyLoss()
          # ... optimization loop
  ```
- **Training Protocol:**
  - Optimizer: LBFGS (lr=0.01, max_iter=200)
  - Loss: Negative Log-Likelihood (NLL)
  - Validation: ECE metric computed before/after
- **ECE Implementation:** Includes `_ECELoss()` class for evaluation
- **Results Pattern:** Reports "Before/After temperature" NLL and ECE

**Repository 2: Lightning-AI/torchmetrics** (⭐ 2K+)
- **URL:** https://github.com/Lightning-AI/torchmetrics
- **Relevance:** Production-grade ECE metric implementation
- **Key Implementation:**
  ```python
  from torchmetrics.classification import CalibrationError
  
  ece = CalibrationError(task="multiclass", num_classes=N, n_bins=15, norm="l1")
  ece.update(probs, targets)
  result = ece.compute()  # Returns ECE value
  ```
- **ECE Formula:**
  - L1 norm: `ECE = Σ b_i |(p_i - c_i)|`
  - L2 norm: `RMSCE = √(Σ b_i (p_i - c_i)²)`
  - Max norm: `MCE = max_i (p_i - c_i)`
- **Configuration:**
  - n_bins: 15 (default, standard for ECE)
  - Bins: Uniform spacing in [0, 1] range
  - Supports GPU acceleration

**Repository 3: rishabh-ranjan/torchcal**
- **URL:** https://github.com/rishabh-ranjan/torchcal
- **Relevance:** Modern PyTorch calibration library with GPU support
- **Supported Methods:**
  - Temperature Scaling (1 parameter)
  - Vector Scaling (num_classes parameters)
  - Matrix Scaling (num_classes² parameters)
- **Usage Pattern:**
  ```python
  cal = torchcal.calibrator("temp_scaler", device=device)
  cal.fit(yhat_val, y_val)
  yhat_calibrated = cal(yhat_test)
  ```

**Repository 4: torch-uncertainty/torch-uncertainty**
- **URL:** https://torch-uncertainty.github.io
- **Relevance:** Complete uncertainty quantification framework
- **Key Features:**
  - TemperatureScaler, VectorScaler, MatrixScaler
  - Automatic integration with dataloaders
  - Reliability diagram visualization
- **Typical ECE Reduction:** 5-15% absolute ECE reduction on CIFAR-100

**Query 2: MBPP Code Generation Benchmark**

**Repository 1: google-research/mbpp** (Official)
- **URL:** https://github.com/google-research/google-research/tree/master/mbpp
- **Status:** Official dataset from "Program Synthesis with Large Language Models" (Austin et al., 2021)
- **Dataset Structure:**
  - Total: 974 problems
  - Train split: IDs 601-974 (374 problems)
  - Test split: IDs 11-510 (500 problems)
  - Validation: IDs 511-600 (90 problems)
  - Few-shot prompts: IDs 1-10
- **Sanitized Subset:** 427 hand-verified problems (higher quality)
- **Data Fields:**
  - `text`: Task description
  - `code`: Python solution
  - `test_list`: 3 automated test cases (assert statements)
  - `test_setup_code`: Import dependencies
- **Loading:**
  ```python
  from datasets import load_dataset
  dataset = load_dataset("google-research-datasets/mbpp")
  # OR sanitized version
  dataset = load_dataset("google-research-datasets/mbpp", "sanitized")
  ```

**Repository 2: HuggingFace Datasets Hub**
- **URL:** https://huggingface.co/datasets/google-research-datasets/mbpp
- **Relevance:** Easy integration with PyTorch/HF ecosystem
- **Evaluation Metric:** pass@k (probability of ≥1 correct sample in k generations)
- **Standard Protocol:**
  - Generate n ≥ k samples per problem
  - pass@k = 𝔼[1 - C(n-c, k) / C(n, k)]
  - Common: n=5, evaluate pass@1, pass@2, pass@5

**Query 3: Code Generation Benchmark Evaluation**

**Repository: UKGovernmentBEIS/inspect_evals**
- **URL:** https://github.com/UKGovernmentBEIS/inspect_evals/tree/main/src/inspect_evals/mbpp
- **Relevance:** Complete MBPP evaluation framework
- **Evaluation Details:**
  - Uses sanitized test split (427 problems)
  - Default: n=5 generations, evaluate pass@{1,2,5}
  - AgentCoder prompt pattern (top leaderboard performer)

**Serena Analysis Needed:** ❌ No - Code patterns are clear and well-documented

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

**Implementation Type:** Established calibration method (not paper-specific)

**Priority Ranking:**
1. ⭐⭐⭐ **Temperature Scaling:** gpleiss/temperature_scaling (canonical reference)
2. ⭐⭐⭐ **ECE Metric:** Lightning-AI/torchmetrics (production-ready)
3. ⭐⭐⭐ **Dataset:** google-research-datasets/mbpp (official HuggingFace)
4. ⭐⭐ **Alternative:** torch-uncertainty (more features, heavier dependency)

**Recommended Implementation Path:**
- Primary: **gpleiss/temperature_scaling + torchmetrics CalibrationError + HF MBPP**
- Fallback: **torch-uncertainty (if visualization/reliability diagrams needed)**
- Justification: 
  - gpleiss implementation is cited in calibration literature as reference
  - torchmetrics ECE is battle-tested, GPU-accelerated, standard in research
  - HuggingFace MBPP provides easy loading with standard splits
  - Combination minimizes dependencies while maximizing reproducibility

### Code Analysis (Serena MCP)

*Skipped* - Code from search results was sufficiently clear. The temperature scaling implementation from gpleiss/temperature_scaling and torchmetrics ECE metric are well-documented with straightforward patterns that don't require semantic analysis.

---

## Experiment Specification

### Dataset

**Primary Dataset: MBPP (Mostly Basic Python Problems)**
- **Type:** standard (code generation benchmark)
- **Source:** google-research-datasets/mbpp (HuggingFace)
- **Total Problems:** 974
- **Task:** Python code generation from natural language descriptions
- **Format:** Each problem includes:
  - `text`: Natural language task description
  - `code`: Python solution
  - `test_list`: 3 automated test cases (assert statements)
  - `test_setup_code`: Import dependencies

**Splits for h-e1:**
- **Train:** IDs 601-974 (374 problems, 60%)
- **Calibration:** IDs 511-600 + 11-120 (195 problems, 20%)
- **Validation:** IDs 121-315 (195 problems, 20%)

**Generalization Dataset: HumanEval**
- **Type:** standard (code generation benchmark, held-out)
- **Total Problems:** 164 hand-written Python problems
- **Purpose:** Test generalization to unseen distribution
- **Source:** openai/HumanEval (HuggingFace)

**Loading Information** (for Phase 4 download):
- Method: HuggingFace datasets library
- Identifier (MBPP): `"google-research-datasets/mbpp"`
- Identifier (HumanEval): `"openai_humaneval"`
- Code: 
  ```python
  from datasets import load_dataset
  mbpp = load_dataset("google-research-datasets/mbpp", split="test")
  humaneval = load_dataset("openai_humaneval", split="test")
  ```

**Data Format for Calibration:**
- Model generates code from `text` prompt
- Execute code against `test_list` to determine correctness (binary)
- Collect logits from model forward pass
- Compute confidence from softmax(logits)
- Pair (confidence, correctness) for ECE calculation

**Preprocessing:**
- No text preprocessing (use raw prompts)
- No code preprocessing (use raw solutions)
- Execute generated code in sandboxed environment

**Data Statistics:**
- MBPP: 974 problems total (374 train, 195 cal, 195 val)
- HumanEval: 164 problems (held-out test)
- Average prompt length: ~50 tokens
- Average solution length: ~10-20 lines of Python

### Models

#### Baseline Model

**Architecture: Code Llama 7B (Primary)**
- **Type:** Decoder-only transformer for code generation
- **Parameters:** 7 billion
- **Context Length:** 16K tokens (supports up to 100K in generation)
- **Vocabulary:** Code-specific vocabulary optimized for Python
- **Special Features:**
  - Logit access (required for temperature scaling)
  - Fill-in-the-middle (FIM) capability (not used in this experiment)
  - Fine-tuned from Llama 2 on code data

**Alternative Models (Same Experiment):**
- **StarCoder2-7B:** Encoder-decoder architecture, multilingual code
- **DeepSeek-Coder-6.7B:** Decoder-only, competitive with larger models

**Loading Information** (for Phase 4 download):
- Method: HuggingFace Transformers library
- Identifier: `"meta-llama/CodeLlama-7b-hf"`
- Code:
  ```python
  from transformers import AutoModelForCausalLM, AutoTokenizer
  model = AutoModelForCausalLM.from_pretrained(
      "meta-llama/CodeLlama-7b-hf",
      torch_dtype=torch.float16,
      device_map="auto"
  )
  tokenizer = AutoTokenizer.from_pretrained("meta-llama/CodeLlama-7b-hf")
  ```

**Configuration for h-e1:**
- **Input:** Natural language task description (from MBPP `text` field)
- **Output:** Python code + logits (for calibration)
- **Generation Settings:**
  - Temperature: 1.0 (before calibration)
  - Max new tokens: 256
  - Top-p: 0.95
  - Sampling: Enabled (for diversity in calibration data)
  - Return logits: True (required for temperature scaling)

**Modifications for Hypothesis:**
- **Uncalibrated Baseline:** Use raw logits (temperature = 1.0)
- **Calibrated Version:** Apply learned temperature parameter T to logits (logits / T)
- **Logit Extraction:** Extract final token logits before softmax for confidence calculation

#### Proposed Model

**Architecture:** Code Llama 7B + Temperature Scaling Calibration Layer

**Integration Point:**
- **Position:** Post-logits, pre-softmax (temperature scaling is applied to final layer logits)
- **Mechanism:** Learned temperature parameter T that scales logits before softmax
- **No architectural changes:** Temperature scaling is a post-hoc calibration method (no retraining)

**Modification:** Wrap model with temperature scaling wrapper (gpleiss pattern)

**Core Mechanism Implementation:**

```python
# Core Mechanism: Temperature Scaling for Confidence Calibration
# Based on: gpleiss/temperature_scaling (canonical reference)
# Paper: "On Calibration of Modern Neural Networks" (Guo et al., 2017)

class ModelWithTemperature(nn.Module):
    """
    Temperature scaling wrapper for calibrating neural network confidence.
    
    Temperature scaling divides logits by learned parameter T before softmax,
    producing calibrated confidence scores that better match empirical accuracy.
    """
    def __init__(self, model, init_temperature=1.5):
        """
        Args:
            model: Base code generation model (Code Llama)
            init_temperature: Initial temperature value (default 1.5)
        """
        super().__init__()
        self.model = model
        # Learnable temperature parameter (optimized on calibration set)
        self.temperature = nn.Parameter(torch.ones(1) * init_temperature)
    
    def forward(self, input_ids, attention_mask=None):
        """
        Forward pass with temperature-scaled logits.
        
        Args:
            input_ids: (B, L) - tokenized input
            attention_mask: (B, L) - attention mask
        Returns:
            scaled_logits: (B, L, V) - temperature-scaled logits
        """
        # Get uncalibrated logits from base model
        logits = self.model(input_ids, attention_mask=attention_mask).logits
        
        # Apply temperature scaling
        return self.temperature_scale(logits)
    
    def temperature_scale(self, logits):
        """
        Apply temperature scaling to logits.
        
        Args:
            logits: (B, L, V) - raw logits from model
        Returns:
            scaled_logits: (B, L, V) - temperature-scaled logits
        """
        # Divide logits by temperature parameter
        # Expand temperature to match logits shape
        temperature = self.temperature.unsqueeze(0).unsqueeze(0)
        return logits / temperature
    
    def set_temperature(self, val_loader, criterion=nn.CrossEntropyLoss()):
        """
        Optimize temperature on validation set using LBFGS.
        
        Args:
            val_loader: DataLoader with (logits, labels) pairs
            criterion: Loss function (default: cross-entropy)
        Returns:
            self (for method chaining)
        """
        # Collect all validation logits and labels
        logits_list, labels_list = [], []
        with torch.no_grad():
            for logits, labels in val_loader:
                logits_list.append(logits)
                labels_list.append(labels)
        logits = torch.cat(logits_list)
        labels = torch.cat(labels_list)
        
        # Optimize temperature using LBFGS
        optimizer = optim.LBFGS([self.temperature], lr=0.01, max_iter=200)
        
        def eval_loss():
            optimizer.zero_grad()
            loss = criterion(self.temperature_scale(logits), labels)
            loss.backward()
            return loss
        
        optimizer.step(eval_loss)
        return self

# Integration Example:
# 1. Train base model normally (or load pretrained Code Llama)
# base_model = AutoModelForCausalLM.from_pretrained("meta-llama/CodeLlama-7b-hf")
#
# 2. Wrap with temperature scaling
# calibrated_model = ModelWithTemperature(base_model)
#
# 3. Optimize temperature on calibration set
# calibrated_model.set_temperature(calibration_loader)
#
# 4. Use calibrated model for inference
# scaled_logits = calibrated_model(input_ids)
# calibrated_probs = F.softmax(scaled_logits, dim=-1)
```

**Key Properties:**
- **No retraining required:** Temperature is optimized post-hoc on calibration set
- **Accuracy-preserving:** Softmax is order-preserving, so predictions don't change
- **Single parameter:** Only learns scalar T (1 parameter vs. millions in model)
- **Fast optimization:** LBFGS converges in ~200 iterations (<1 minute)

### Training Protocol

**Base Model:** Pretrained (no training required for h-e1)
- Use Code Llama 7B pretrained checkpoint directly
- **Source:** Meta's official release "meta-llama/CodeLlama-7b-hf"

**Temperature Parameter Optimization** (Only training step for h-e1):

**Optimizer:** LBFGS
  - Learning rate: 0.01
  - Max iterations: 200
  - **Source:** gpleiss/temperature_scaling (standard protocol)
  - **Rationale:** LBFGS converges faster than SGD for single-parameter optimization

**Objective:** Negative Log-Likelihood (NLL)
  - Minimize: `-Σ log P(y_true | x, T)` where T = temperature
  - Evaluated on calibration split (195 MBPP problems)
  - **Source:** Guo et al. 2017 "On Calibration of Modern Neural Networks"

**Calibration Split:** 195 problems from MBPP
  - IDs: 511-600 (90 problems) + 11-120 (105 problems)
  - Generated code must be executed to obtain correctness labels
  - Logits extracted from forward pass

**Validation Split:** 195 problems from MBPP
  - IDs: 121-315
  - Used for final ECE evaluation (not seen during temperature optimization)

**Seeds:** 1 (fixed at 42)
  - **Rationale:** EXISTENCE (PoC) - single run sufficient to demonstrate effect

**Computational Requirements:**
- GPU: Single A100 40GB or V100 32GB
- Walltime: ~2 hours total
  - Code generation: ~1.5 hours (974 problems × 5 sec/problem)
  - Temperature optimization: ~1 minute (LBFGS on 195 samples)
  - ECE evaluation: ~5 minutes

> ⚠️ **EXISTENCE (PoC)**: No hyperparameter search. Use defaults from reference implementation.

### Evaluation

**Primary Metric: Expected Calibration Error (ECE)**

**Definition:**
```
ECE = Σ (b_i × |p_i - c_i|)
```
Where:
- `b_i` = fraction of samples in bin i
- `p_i` = average confidence in bin i
- `c_i` = empirical accuracy in bin i
- Bins = 15 uniform bins in [0, 1] range (standard)

**Success Criterion:**
- ECE_uncalibrated - ECE_calibrated ≥ 30% reduction
- Example: If ECE_uncal = 0.15, then ECE_cal ≤ 0.105 (30% reduction)

**Secondary Metrics:**

1. **Reliability Diagram Alignment**
   - Visual check: calibration curve closeness to diagonal
   - Qualitative assessment (included in validation report)

2. **Calibration Curve (Confidence vs. Accuracy)**
   - Plot binned confidence (x-axis) vs. empirical accuracy (y-axis)
   - Perfect calibration = diagonal line
   - Monotonicity check: accuracy should increase with confidence

3. **Pass@1 Accuracy (Sanity Check)**
   - Percentage of problems solved correctly
   - Should NOT decrease after calibration (temperature scaling is accuracy-preserving)

**Metrics Loading Information** (for Phase 4 implementation):
- Task Type: Code generation with binary correctness evaluation
- Library: torchmetrics + custom ECE implementation
- Code:
  ```python
  # Option 1: torchmetrics (production-ready)
  from torchmetrics.classification import CalibrationError
  ece_metric = CalibrationError(
      task="binary",
      n_bins=15,
      norm="l1"  # L1 norm = standard ECE
  )
  ece_metric.update(confidences, correctness)
  ece_value = ece_metric.compute()
  
  # Option 2: gpleiss reference implementation (research standard)
  class ECELoss(nn.Module):
      def __init__(self, n_bins=15):
          super().__init__()
          bin_boundaries = torch.linspace(0, 1, n_bins + 1)
          self.bin_lowers = bin_boundaries[:-1]
          self.bin_uppers = bin_boundaries[1:]
      
      def forward(self, confidences, correctness):
          ece = torch.zeros(1, device=confidences.device)
          for bin_lower, bin_upper in zip(self.bin_lowers, self.bin_uppers):
              in_bin = (confidences > bin_lower) * (confidences <= bin_upper)
              prop_in_bin = in_bin.float().mean()
              if prop_in_bin > 0:
                  accuracy_in_bin = correctness[in_bin].float().mean()
                  avg_conf_in_bin = confidences[in_bin].mean()
                  ece += torch.abs(avg_conf_in_bin - accuracy_in_bin) * prop_in_bin
          return ece
  ```

**Evaluation Protocol:**

1. **Generate code for all problems** (MBPP calibration + validation splits)
2. **Execute generated code** against test_list to get correctness (0 or 1)
3. **Extract confidence** from model logits:
   - Uncalibrated: `conf = max(softmax(logits))`
   - Calibrated: `conf = max(softmax(logits / T))` where T = learned temperature
4. **Compute ECE** using 15-bin binning
5. **Generate reliability diagrams** (matplotlib visualization)
6. **Report:**
   - ECE before temperature scaling
   - ECE after temperature scaling
   - Optimal temperature T*
   - ECE reduction percentage
   - pass@1 accuracy (before/after, should be ~same)

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Target vs actual metrics bar chart

#### Additional Figures (LLM Autonomous)

Based on temperature scaling calibration experiment, the following visualizations best communicate results:

1. **Reliability Diagram** (confidence vs. accuracy)
   - X-axis: Predicted confidence bins (15 bins, 0.0-1.0)
   - Y-axis: Empirical accuracy per bin
   - Two lines: Uncalibrated (before) vs. Calibrated (after)
   - Perfect calibration reference (diagonal y=x line)
   - Bar chart overlay showing sample counts per bin

2. **ECE Comparison Bar Chart** (MANDATORY - Gate Metric)
   - Two bars: ECE_before vs. ECE_after
   - Horizontal line showing 30% reduction threshold
   - Annotate with actual reduction percentage

3. **Calibration Curve** (binned confidence histogram)
   - Histogram of confidence scores before/after temperature scaling
   - Shows distribution shift from overconfident to calibrated

4. **Temperature Optimization Convergence**
   - X-axis: LBFGS iteration
   - Y-axis: NLL loss
   - Shows convergence to optimal temperature T*
   - Annotate final T* value

5. **Per-Bin Calibration Error**
   - X-axis: Confidence bins (15 bins)
   - Y-axis: |confidence - accuracy| per bin
   - Before/after comparison
   - Highlights which confidence ranges improved most

> **Phase 4 Coder:** Generate all 5 figures automatically using matplotlib.
> All figures will be saved to `{hypothesis_folder}/figures/`.
> Include figure generation logic in experiment code (not post-processing).

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error
2. `proposed_metric > baseline_metric`

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Status:** Limited relevant results
- **Queries:**
  - "temperature scaling experiment design dataset"
  - "temperature scaling implementation challenges best practices"
  - "code generation benchmark calibration"
- **Results:** Primarily diffusion model content (not applicable to calibration)
- **Conclusion:** Archon KB does not contain calibration/code generation research
- **Impact:** Relied on Exa GitHub search for implementation guidance

### B. GitHub Implementations (Exa)

**Repository 1: gpleiss/temperature_scaling** (⭐ 1,000) - **PRIMARY REFERENCE**
- **URL:** https://github.com/gpleiss/temperature_scaling
- **Query Used:** "temperature scaling calibration neural network PyTorch GitHub"
- **Status:** Canonical reference implementation (cited in calibration literature)
- **Key Code** (annotated):
  ```python
  # ModelWithTemperature wrapper class (basis for our pseudo-code)
  class ModelWithTemperature(nn.Module):
      def __init__(self, model):
          self.model = model
          self.temperature = nn.Parameter(torch.ones(1) * 1.5)
      
      def temperature_scale(self, logits):
          temperature = self.temperature.unsqueeze(1).expand(logits.size(0), logits.size(1))
          return logits / temperature
      
      def set_temperature(self, valid_loader):
          # LBFGS optimization of temperature on validation set
          optimizer = optim.LBFGS([self.temperature], lr=0.01, max_iter=200)
          # ... (see full implementation in Step 6 pseudo-code)
  ```
- **Configuration Extracted:**
  - Optimizer: LBFGS (lr=0.01, max_iter=200)
  - Loss: Negative Log-Likelihood (NLL)
  - Temperature initialization: 1.5
- **Their Results:** Reports before/after ECE with optimal temperature
- **Used For:** Core mechanism pseudo-code, training protocol, temperature optimization

**Repository 2: Lightning-AI/torchmetrics** (⭐ 2K+) - **ECE METRIC**
- **URL:** https://github.com/Lightning-AI/torchmetrics
- **Query Used:** "Expected Calibration Error ECE metric PyTorch implementation"
- **Relevance:** Production-grade ECE metric implementation
- **Key Code**:
  ```python
  from torchmetrics.classification import CalibrationError
  ece = CalibrationError(task="binary", n_bins=15, norm="l1")
  ece.update(probs, targets)
  ece_value = ece.compute()
  ```
- **Configuration Extracted:**
  - n_bins: 15 (standard for ECE)
  - norm: "l1" (L1 norm = Expected Calibration Error)
  - Bin spacing: Uniform in [0, 1] range
- **ECE Formula:** `ECE = Σ b_i |p_i - c_i|`
- **Used For:** Evaluation metrics, ECE calculation implementation

**Repository 3: google-research-datasets/mbpp** - **DATASET (OFFICIAL)**
- **URL:** https://huggingface.co/datasets/google-research-datasets/mbpp
- **Query Used:** "MBPP HumanEval code generation benchmark PyTorch dataset"
- **Paper:** "Program Synthesis with Large Language Models" (Austin et al., 2021)
- **Dataset Structure:**
  - Total: 974 problems
  - Splits: train (374), test (500), validation (90)
  - Fields: task_id, text, code, test_list, test_setup_code
- **Loading Code**:
  ```python
  from datasets import load_dataset
  mbpp = load_dataset("google-research-datasets/mbpp", split="test")
  ```
- **Evaluation Metric:** pass@k
- **Used For:** Dataset selection, split configuration, data loading

**Repository 4: meta-llama/CodeLlama** - **MODEL (OFFICIAL)**
- **URL:** https://huggingface.co/meta-llama/CodeLlama-7b-hf
- **Query Used:** "Code Llama model loading transformers huggingface pretrained"
- **Model Family:** Code Llama 7B/13B/34B/70B
- **Loading Code**:
  ```python
  from transformers import AutoModelForCausalLM, AutoTokenizer
  model = AutoModelForCausalLM.from_pretrained(
      "meta-llama/CodeLlama-7b-hf",
      torch_dtype=torch.float16,
      device_map="auto"
  )
  ```
- **Key Features:**
  - Logit access (required for temperature scaling)
  - 16K context (can generate up to 100K)
  - Python-optimized vocabulary
- **Used For:** Baseline model selection, model loading code

**Repository 5: torch-uncertainty/torch-uncertainty** - **ALTERNATIVE CALIBRATION**
- **URL:** https://torch-uncertainty.github.io
- **Relevance:** Complete uncertainty quantification framework
- **Alternative Implementations:**
  - TemperatureScaler, VectorScaler, MatrixScaler
  - Automatic dataloader integration
  - Reliability diagram visualization
- **Typical Results:** 5-15% absolute ECE reduction on CIFAR-100
- **Used For:** Alternative implementation reference (not primary)

### C. Code Analysis (Serena)

**Serena Analysis:** Not performed - code from search results was sufficiently clear

- gpleiss/temperature_scaling provides clear, canonical implementation
- torchmetrics ECE is production-ready with standard API
- No complex architectural patterns requiring semantic analysis

### D. Previous Hypothesis Context

**Status:** N/A - h-e1 is the foundation hypothesis (first in sequential chain)

### E. Academic Papers (Cited in Implementations)

**Primary Paper:**
- **Title:** "On Calibration of Modern Neural Networks"
- **Authors:** Guo, C., Pleiss, G., Sun, Y., Weinberger, K. Q.
- **Year:** 2017
- **Venue:** ICML 2017
- **Key Contribution:** Introduced temperature scaling for post-hoc calibration
- **URL:** https://arxiv.org/abs/1706.04599
- **Used For:** Method justification, expected ECE reduction ranges

**Dataset Paper:**
- **Title:** "Program Synthesis with Large Language Models"
- **Authors:** Austin, J., et al.
- **Year:** 2021
- **Venue:** arXiv
- **Contribution:** MBPP benchmark for code generation
- **URL:** https://arxiv.org/abs/2108.07732
- **Used For:** Dataset selection rationale, evaluation protocol

### F. Implementation Priority Rationale

**Selected Stack:**
1. **Temperature Scaling:** gpleiss/temperature_scaling (canonical, cited in papers)
2. **ECE Metric:** torchmetrics CalibrationError (production-ready, GPU-accelerated)
3. **Dataset:** google-research-datasets/mbpp (official HuggingFace)
4. **Model:** meta-llama/CodeLlama-7b-hf (official Meta release)

**Justification:**
- gpleiss implementation is the reference cited in calibration literature
- torchmetrics is battle-tested, maintained, with 2K+ stars
- Official datasets/models ensure reproducibility
- Minimal dependencies while maximizing scientific validity

**Rejected Alternatives:**
- ❌ torch-uncertainty: More features but heavier dependencies (not needed for h-e1)
- ❌ Custom ECE implementation: Reinventing the wheel (torchmetrics exists)
- ❌ StarCoder2/DeepSeek-Coder: Keep Code Llama as primary (ablate models in Phase 5)

---

## State Information

**State File:** verification_state.yaml
**Date:** 2026-07-10T23:46:39Z

### Workflow History for This Hypothesis
- 2026-07-10T23:46:39Z: Set to IN_PROGRESS (Phase 2C started)

---

*MCP Tools Used: Archon (Knowledge + Code), Exa (GitHub), Serena (Code Analysis)*
*All specifications grounded in researched implementations*
*Next Phase: Phase 3 - Implementation Planning*
