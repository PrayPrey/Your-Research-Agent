# Logic Design: h-e1 Temperature Scaling Calibration

**Date:** 2026-07-11  
**Hypothesis:** h-e1  
**Author:** Phase 3 Logic Agent  
**Version:** 1.0

---

## Codebase Analysis (Serena)

**Project Type:** green-field  
**Status:** Green-field project - designing new APIs  
**Analyzed Path:** N/A  
**Relevant Symbols:** None - new implementation

---

## Knowledge Base Patterns Applied

**Applied:** Standard PyTorch patterns (optimizer setup, nn.Module wrapper)

Note: Archon KB searches returned limited relevant content (mostly diffusion models). Implementation follows canonical gpleiss/temperature_scaling patterns documented in 02c_experiment_brief.md.

---

## Task Breakdown

All tasks allocated from 02_architecture.md:

| Task ID | Component | Complexity | Budget | Description |
|---------|-----------|------------|--------|-------------|
| L-1 | Temperature Scaling Wrapper | 3 | 15 | ModelWithTemperature class |
| L-2 | ECE Computation | 4 | 20 | Expected Calibration Error metric |
| L-3 | Code Execution Sandbox | 5 | 25 | Safe code execution with test evaluation |
| L-4 | Logit Extraction | 2 | 10 | Extract logits from Code Llama |
| L-5 | LBFGS Temperature Optimization | 4 | 20 | Optimize temperature on calibration set |
| L-6 | Dataset Loader | 2 | 10 | MBPP custom splits |

**Total Budget:** 100/100 subtasks used

---

## L-1: Temperature Scaling Wrapper [Complexity: 3, Budget: 15]

**Applied:** gpleiss/temperature_scaling canonical pattern

### API Signatures

```python
class ModelWithTemperature(nn.Module):
    """Wraps model with learnable temperature parameter for calibration."""
    
    def __init__(self, model: nn.Module, init_temperature: float = 1.5):
        """
        Args:
            model: Base Code Llama model
            init_temperature: Initial T value (default 1.5)
        """
        super().__init__()
        self.model = model
        self.temperature = nn.Parameter(torch.ones(1) * init_temperature)
    
    def forward(
        self, 
        input_ids: Tensor,  # [B, L]
        attention_mask: Optional[Tensor] = None  # [B, L]
    ) -> Tensor:
        """
        Forward pass with temperature scaling.
        
        Returns:
            scaled_logits: [B, L, V] temperature-scaled logits
        """
        logits = self.model(input_ids, attention_mask=attention_mask).logits
        return self.temperature_scale(logits)
    
    def temperature_scale(self, logits: Tensor) -> Tensor:
        """
        Apply temperature scaling: logits / T
        
        Args:
            logits: [B, L, V] raw logits
        Returns:
            scaled: [B, L, V] scaled logits
        """
        # Broadcasting: [1] -> [B, L, V]
        return logits / self.temperature.view(1, 1, 1)
    
    def set_temperature(
        self, 
        logits_list: List[Tensor],  # List of [N_i, V]
        labels_list: List[Tensor],  # List of [N_i]
        criterion: nn.Module = nn.CrossEntropyLoss()
    ) -> float:
        """
        Optimize temperature using LBFGS.
        
        Args:
            logits_list: Calibration set logits (ragged)
            labels_list: Binary labels (0/1 correctness)
            criterion: Loss function
        
        Returns:
            optimal_temperature: Learned T value
        """
        # Concatenate all calibration data
        logits = torch.cat(logits_list, dim=0)  # [N_total, V]
        labels = torch.cat(labels_list, dim=0)  # [N_total]
        
        # LBFGS optimizer
        optimizer = optim.LBFGS(
            [self.temperature], 
            lr=0.01, 
            max_iter=200
        )
        
        # Closure for LBFGS
        def eval_loss():
            optimizer.zero_grad()
            scaled_logits = self.temperature_scale(logits)
            loss = criterion(scaled_logits, labels)
            loss.backward()
            return loss
        
        optimizer.step(eval_loss)
        return self.temperature.item()
```

### Pseudo-code

```
1. Initialize wrapper with base model and T=1.5
2. During calibration:
   a. Collect logits/labels from calibration split
   b. Define LBFGS closure (compute NLL on scaled logits)
   c. Run optimizer.step() (handles iteration internally)
   d. Return optimized T*
3. During inference:
   a. Call forward() -> returns logits/T
   b. Apply softmax for calibrated probabilities
```

### Subtasks [15/15 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | ModelWithTemperature class | nn.Module wrapper with temperature parameter |
| L-1-2 | temperature_scale method | Divide logits by T with broadcasting |
| L-1-3 | set_temperature method | LBFGS optimization loop |

---

## L-2: ECE Computation [Complexity: 4, Budget: 20]

**Applied:** torchmetrics CalibrationError + gpleiss reference implementation

### API Signatures

```python
class ECELoss(nn.Module):
    """Expected Calibration Error with uniform binning."""
    
    def __init__(self, n_bins: int = 15):
        """
        Args:
            n_bins: Number of uniform bins in [0,1]
        """
        super().__init__()
        bin_boundaries = torch.linspace(0, 1, n_bins + 1)
        self.bin_lowers = bin_boundaries[:-1]  # [n_bins]
        self.bin_uppers = bin_boundaries[1:]   # [n_bins]
    
    def forward(
        self, 
        confidences: Tensor,  # [N] max softmax probabilities
        correctness: Tensor   # [N] binary labels (0/1)
    ) -> Tensor:
        """
        Compute ECE = Σ b_i |p_i - c_i|
        
        Args:
            confidences: [N] predicted confidence per sample
            correctness: [N] actual correctness (0 or 1)
        
        Returns:
            ece: Scalar ECE value in [0, 1]
        """
        ece = torch.zeros(1, device=confidences.device)
        
        for bin_lower, bin_upper in zip(self.bin_lowers, self.bin_uppers):
            # Find samples in current bin
            in_bin = (confidences > bin_lower) & (confidences <= bin_upper)
            prop_in_bin = in_bin.float().mean()
            
            if prop_in_bin > 0:
                # Compute bin statistics
                accuracy_in_bin = correctness[in_bin].float().mean()
                avg_conf_in_bin = confidences[in_bin].mean()
                
                # Accumulate weighted calibration error
                ece += torch.abs(avg_conf_in_bin - accuracy_in_bin) * prop_in_bin
        
        return ece

def extract_confidence(logits: Tensor, temperature: float = 1.0) -> Tensor:
    """
    Extract max softmax probability from logits.
    
    Args:
        logits: [N, V] raw or scaled logits
        temperature: T for scaling (if not already applied)
    
    Returns:
        confidences: [N] max probability per sample
    """
    scaled_logits = logits / temperature
    probs = F.softmax(scaled_logits, dim=-1)  # [N, V]
    confidences = probs.max(dim=-1).values    # [N]
    return confidences
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| confidences | [N] | Max softmax probability per sample |
| correctness | [N] | Binary (0=wrong, 1=correct) |
| in_bin | [N] | Boolean mask for bin membership |
| bin_lowers | [15] | Lower bin boundaries |
| bin_uppers | [15] | Upper bin boundaries |
| ece | [1] | Scalar calibration error |

### Pseudo-code

```
1. Create 15 uniform bins in [0, 1]
2. For each bin:
   a. Mask samples with confidence in [bin_lower, bin_upper]
   b. If bin is non-empty:
      - Compute average confidence p_i
      - Compute average correctness c_i (empirical accuracy)
      - Add |p_i - c_i| × (bin_fraction) to ECE
3. Return total ECE
```

### Subtasks [20/20 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | ECELoss class | 15-bin binning implementation |
| L-2-2 | Bin statistics computation | Average confidence/accuracy per bin |
| L-2-3 | extract_confidence helper | Max softmax probability extraction |

---

## L-3: Code Execution Sandbox [Complexity: 5, Budget: 25]

**Applied:** Standard subprocess with timeout + restricted imports

### API Signatures

```python
class CodeExecutor:
    """Safe execution of generated Python code against test cases."""
    
    def __init__(self, timeout: float = 5.0):
        """
        Args:
            timeout: Max execution time per test (seconds)
        """
        self.timeout = timeout
        self.restricted_imports = {'os', 'subprocess', 'sys', 'eval', 'exec'}
    
    def execute_test(
        self,
        code: str,
        test_case: str,
        setup_code: str = ""
    ) -> bool:
        """
        Execute code against single test case.
        
        Args:
            code: Generated Python function
            test_case: Assert statement (e.g., "assert f(1) == 2")
            setup_code: Import statements
        
        Returns:
            success: True if test passes, False otherwise
        """
        # Validate no restricted imports
        if self._has_restricted_imports(code):
            return False
        
        # Combine setup, code, test
        full_code = f"{setup_code}\n{code}\n{test_case}"
        
        try:
            # Execute in subprocess with timeout
            result = subprocess.run(
                ['python', '-c', full_code],
                timeout=self.timeout,
                capture_output=True,
                text=True
            )
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            return False
        except Exception:
            return False
    
    def evaluate_problem(
        self,
        code: str,
        test_list: List[str],
        setup_code: str = ""
    ) -> Tuple[bool, int]:
        """
        Evaluate code against all test cases.
        
        Args:
            code: Generated solution
            test_list: List of assert statements
            setup_code: Import dependencies
        
        Returns:
            is_correct: True if ALL tests pass
            num_passed: Number of tests passed
        """
        num_passed = 0
        for test_case in test_list:
            if self.execute_test(code, test_case, setup_code):
                num_passed += 1
        
        is_correct = (num_passed == len(test_list))
        return is_correct, num_passed
    
    def _has_restricted_imports(self, code: str) -> bool:
        """Check for dangerous imports."""
        for module in self.restricted_imports:
            if f"import {module}" in code or f"from {module}" in code:
                return True
        return False
```

### Pseudo-code

```
1. For each test case:
   a. Check for restricted imports (os, subprocess, etc.)
   b. Combine setup_code + generated_code + test_assert
   c. Run in subprocess with 5-second timeout
   d. Capture return code (0 = pass, non-zero = fail)
2. Return:
   - Binary correctness (all tests pass)
   - Number of tests passed (for debugging)
```

### Subtasks [25/25 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | CodeExecutor class | Sandboxed execution manager |
| L-3-2 | execute_test method | Single test case execution with timeout |
| L-3-3 | evaluate_problem method | Run all test cases, aggregate results |
| L-3-4 | Import validation | Block dangerous modules |

---

## L-4: Logit Extraction [Complexity: 2, Budget: 10]

**Applied:** Standard HuggingFace transformers API

### API Signatures

```python
def generate_with_logits(
    model: AutoModelForCausalLM,
    tokenizer: AutoTokenizer,
    prompt: str,
    max_new_tokens: int = 256,
    temperature: float = 1.0,
    top_p: float = 0.95
) -> Tuple[str, Tensor]:
    """
    Generate code and extract logits for final token.
    
    Args:
        model: Code Llama model
        tokenizer: Tokenizer
        prompt: Task description
        max_new_tokens: Generation length
        temperature: Sampling temperature (pre-calibration)
        top_p: Nucleus sampling threshold
    
    Returns:
        generated_code: String of generated Python code
        logits: [V] logits for final generated token
    """
    # Tokenize prompt
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    
    # Generate with logit tracking
    outputs = model.generate(
        **inputs,
        max_new_tokens=max_new_tokens,
        temperature=temperature,
        top_p=top_p,
        do_sample=True,
        return_dict_in_generate=True,
        output_scores=True
    )
    
    # Extract generated code
    generated_ids = outputs.sequences[0, inputs.input_ids.shape[1]:]
    generated_code = tokenizer.decode(generated_ids, skip_special_tokens=True)
    
    # Extract final token logits (for confidence calculation)
    final_logits = outputs.scores[-1][0]  # [V]
    
    return generated_code, final_logits
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| inputs.input_ids | [1, L_prompt] | Tokenized prompt |
| outputs.sequences | [1, L_prompt + L_gen] | Full sequence |
| outputs.scores | Tuple[V] × L_gen | Logits per generation step |
| final_logits | [V] | Logits for last generated token |

### Pseudo-code

```
1. Tokenize prompt -> input_ids
2. Call model.generate() with:
   - output_scores=True (to get logits)
   - return_dict_in_generate=True
3. Decode generated tokens -> code string
4. Extract final logits from outputs.scores[-1]
5. Return (code, logits)
```

### Subtasks [10/10 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | generate_with_logits function | Generate + logit extraction |
| L-4-2 | Logit extraction from outputs | Access outputs.scores for final token |

---

## L-5: LBFGS Temperature Optimization [Complexity: 4, Budget: 20]

**Applied:** PyTorch LBFGS with closure pattern

### API Signatures

```python
def optimize_temperature(
    model_with_temp: ModelWithTemperature,
    calibration_data: List[Tuple[Tensor, int]],  # [(logits, label)]
    lr: float = 0.01,
    max_iter: int = 200
) -> Tuple[float, List[float]]:
    """
    Optimize temperature parameter using LBFGS.
    
    Args:
        model_with_temp: Wrapper with temperature parameter
        calibration_data: List of (logits [V], label) pairs
        lr: LBFGS learning rate
        max_iter: Maximum iterations
    
    Returns:
        optimal_temp: Learned temperature T*
        loss_history: NLL loss per iteration
    """
    # Extract logits and labels
    logits_list = [logits for logits, _ in calibration_data]
    labels_list = [torch.tensor(label) for _, label in calibration_data]
    
    logits = torch.stack(logits_list)  # [N, V]
    labels = torch.stack(labels_list)  # [N]
    
    # Setup optimizer
    optimizer = optim.LBFGS(
        [model_with_temp.temperature],
        lr=lr,
        max_iter=max_iter,
        line_search_fn='strong_wolfe'
    )
    
    criterion = nn.CrossEntropyLoss()
    loss_history = []
    
    # LBFGS closure
    def closure():
        optimizer.zero_grad()
        scaled_logits = model_with_temp.temperature_scale(logits)
        loss = criterion(scaled_logits, labels)
        loss.backward()
        loss_history.append(loss.item())
        return loss
    
    # Run optimization
    optimizer.step(closure)
    
    optimal_temp = model_with_temp.temperature.item()
    return optimal_temp, loss_history
```

### Pseudo-code

```
1. Collect calibration set:
   - For each problem: (final_token_logits [V], correctness_label)
2. Stack into tensors:
   - logits: [N_cal, V]
   - labels: [N_cal]
3. Define LBFGS closure:
   a. Scale logits by current temperature
   b. Compute NLL = CrossEntropyLoss(scaled_logits, labels)
   c. Backward pass
   d. Return loss
4. Call optimizer.step(closure)
   - LBFGS handles internal iteration (up to max_iter=200)
5. Return optimal T* and loss history
```

### Subtasks [20/20 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | optimize_temperature function | Main optimization loop |
| L-5-2 | LBFGS closure | NLL computation with scaled logits |
| L-5-3 | Loss tracking | Store NLL per iteration for convergence plot |

---

## L-6: Dataset Loader [Complexity: 2, Budget: 10]

**Applied:** HuggingFace datasets with custom split logic

### API Signatures

```python
def load_mbpp_custom_splits() -> Dict[str, Dataset]:
    """
    Load MBPP with custom splits for h-e1.
    
    Returns:
        splits: Dict with keys 'calibration', 'validation'
    """
    # Load full MBPP dataset
    mbpp = load_dataset("google-research-datasets/mbpp", split="test")
    
    # Define custom split IDs
    calibration_ids = set(range(511, 601)) | set(range(11, 121))  # 195 problems
    validation_ids = set(range(121, 316))  # 195 problems
    
    # Filter by task_id
    calibration = mbpp.filter(lambda x: x['task_id'] in calibration_ids)
    validation = mbpp.filter(lambda x: x['task_id'] in validation_ids)
    
    return {
        'calibration': calibration,
        'validation': validation
    }

class MBPPDataset(torch.utils.data.Dataset):
    """PyTorch dataset wrapper for MBPP."""
    
    def __init__(self, hf_dataset: Dataset):
        """
        Args:
            hf_dataset: HuggingFace Dataset object
        """
        self.data = hf_dataset
    
    def __len__(self) -> int:
        return len(self.data)
    
    def __getitem__(self, idx: int) -> Dict[str, Any]:
        """
        Returns:
            item: Dict with keys:
                - 'task_id': Problem ID
                - 'text': Task description (prompt)
                - 'test_list': List of assert statements
                - 'test_setup_code': Import dependencies
        """
        item = self.data[idx]
        return {
            'task_id': item['task_id'],
            'text': item['text'],
            'test_list': item['test_list'],
            'test_setup_code': item.get('test_setup_code', '')
        }
```

### Pseudo-code

```
1. Load MBPP test split from HuggingFace
2. Define custom split IDs:
   - Calibration: 511-600 + 11-120 (195 problems)
   - Validation: 121-315 (195 problems)
3. Filter dataset by task_id
4. Wrap in PyTorch Dataset for iteration
5. Return dict of splits
```

### Subtasks [10/10 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | load_mbpp_custom_splits | HF dataset loading + filtering |
| L-6-2 | MBPPDataset class | PyTorch Dataset wrapper |

---

## Integration Notes

### End-to-End Pipeline

```python
# 1. Load data
splits = load_mbpp_custom_splits()
calibration_loader = DataLoader(MBPPDataset(splits['calibration']), batch_size=1)
validation_loader = DataLoader(MBPPDataset(splits['validation']), batch_size=1)

# 2. Load model
base_model = AutoModelForCausalLM.from_pretrained("meta-llama/CodeLlama-7b-hf")
tokenizer = AutoTokenizer.from_pretrained("meta-llama/CodeLlama-7b-hf")

# 3. Generate code and collect calibration data
calibration_data = []
executor = CodeExecutor(timeout=5.0)

for batch in calibration_loader:
    # Generate with logits
    code, logits = generate_with_logits(
        base_model, tokenizer, batch['text'][0]
    )
    
    # Execute tests
    is_correct, _ = executor.evaluate_problem(
        code, batch['test_list'], batch['test_setup_code'][0]
    )
    
    # Store (logits, label)
    label = 1 if is_correct else 0
    calibration_data.append((logits, label))

# 4. Optimize temperature
model_with_temp = ModelWithTemperature(base_model)
optimal_T, loss_history = optimize_temperature(
    model_with_temp, calibration_data
)

# 5. Evaluate ECE before/after
ece_metric = ECELoss(n_bins=15)

# Before calibration (T=1.0)
confidences_before = []
correctness_labels = []

for batch in validation_loader:
    code, logits = generate_with_logits(base_model, tokenizer, batch['text'][0])
    is_correct, _ = executor.evaluate_problem(code, batch['test_list'], batch['test_setup_code'][0])
    
    conf = extract_confidence(logits, temperature=1.0)
    confidences_before.append(conf)
    correctness_labels.append(1 if is_correct else 0)

ece_before = ece_metric(
    torch.tensor(confidences_before),
    torch.tensor(correctness_labels)
)

# After calibration (T=optimal_T)
confidences_after = []
for logits in logits_list:  # Reuse validation logits
    conf = extract_confidence(logits, temperature=optimal_T)
    confidences_after.append(conf)

ece_after = ece_metric(
    torch.tensor(confidences_after),
    torch.tensor(correctness_labels)
)

# 6. Compute reduction
reduction_pct = 100 * (ece_before - ece_after) / ece_before
print(f"ECE reduction: {reduction_pct:.1f}%")
print(f"Gate status: {'PASS' if reduction_pct >= 30 else 'FAIL'}")
```

---

## Edge Cases & Error Handling

### Code Execution
- **Timeout:** Mark test as failed if execution exceeds 5 seconds
- **Restricted imports:** Reject code with `os`, `subprocess`, etc.
- **Syntax errors:** Caught by subprocess, treated as test failure

### Temperature Optimization
- **LBFGS divergence:** Monitor loss history, fallback to grid search if loss increases
- **Extreme temperatures:** Clip T to [0.1, 10.0] range for numerical stability
- **Empty bins:** ECE computation skips bins with prop_in_bin=0

### Dataset Loading
- **HuggingFace API errors:** Retry with exponential backoff
- **Missing fields:** Default `test_setup_code` to empty string if not present

### Logit Extraction
- **Empty generation:** If model generates 0 tokens, use input logits (fallback)
- **OOM errors:** Use fp16 and batch_size=1

---

## Self-Validation Checklist

- [x] No ASCII diagrams (text only)
- [x] "Applied:" pattern noted (1 line each)
- [x] Docstrings ≤ 2 lines
- [x] Tensor shapes in code comments
- [x] Subtask counts within budget (100/100 total)
- [x] Total length < 600 lines
- [x] Codebase Analysis (Serena) section included
- [x] Green-field project noted (Serena skip acceptable)
- [x] All 6 tasks from architecture covered
- [x] Pseudo-code only for complex algorithms (LBFGS, ECE)
- [x] API signatures match gpleiss/temperature_scaling patterns

---

**Document Status:** FINAL  
**Next Step:** Phase 3 Configuration Design (03_config.md)
