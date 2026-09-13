# H-M2 Logic: Corpus Entropy → Model Logit Margin Internalization

Applied: spearman-gate-pattern, dataclass-config-pattern, subprocess-training-pattern, memmap-bin-idx-pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: API signatures verified from h-m1/code/ actual implementation
**Analyzed Path**: `docs/youra_research/20260315_data_problems/h-m1/code/`
**Relevant Symbols**:
- `StatisticalTests.__init__(n_bootstrap, seed)` — no `alpha_level` in h-m1 signature (added in H-M2)
- `StatisticalTests.run_all_tests(log_odds_df, mean_log_odds_per_config, filtering_intensities)` — H-M1 signature differs from H-M2 (new inputs: corpus_entropy_values, model_logit_margins)
- `StatisticalTests.evaluate_gate(spearman_result, bootstrap_ci, alpha_level=0.05)` — takes bootstrap_ci as positional arg
- `StatisticalTests.ols_regression(filtering_intensities, mean_log_odds)` — H-M2 uses `log_linear_ols` with log-transformed X
- `verify_mechanism_activated(log_odds_df, stats_results)` — H-M1 signature; H-M2 adds `logit_margins`, `config` args
- `load_config(yaml_path=None) -> HM1Config` — pattern reused; HM2Config follows same structure

---

## External Dependencies (Base Hypothesis)

### API Signatures (From Actual h-m1/code/)

```python
# From: h-m1/code/statistical_tests.py (ACTUAL CODE - verified)

class StatisticalTests:
    def __init__(self, n_bootstrap: int = 1000, seed: int = 42):
        # NOTE: no alpha_level param in h-m1 — H-M2 adds it
        ...

    def spearman_correlation(
        self,
        filtering_intensities: List[float],  # h-m1 name; H-M2 renames to corpus_entropy_values
        mean_log_odds: List[float],           # h-m1 name; H-M2 renames to model_logit_margins
    ) -> Dict[str, float]:
        # Returns: {"rho": float, "pvalue": float}
        ...

    def bootstrap_spearman_ci(
        self,
        filtering_intensities: List[float],
        mean_log_odds: List[float],
    ) -> Tuple[float, float]:
        # Returns: (ci_low, ci_high)
        ...

    def evaluate_gate(
        self,
        spearman_result: Dict[str, float],
        bootstrap_ci: Tuple[float, float],    # positional — NOT keyword-only!
        alpha_level: float = 0.05,
    ) -> Dict[str, Any]:
        # Returns: {"gate_passed": bool, "rho": float, "pvalue": float, ...}
        ...

    def run_all_tests(
        self,
        log_odds_df: pd.DataFrame,            # H-M1 specific — NOT used in H-M2
        mean_log_odds_per_config: Dict[str, float],
        filtering_intensities: List[float],
    ) -> Dict[str, Any]:
        # H-M2 reimplements run_all_tests with different signature
        ...

# From: h-m1/code/run_experiment.py (ACTUAL CODE - verified)
def verify_mechanism_activated(
    log_odds_df,                              # pandas DataFrame — H-M2 passes logit_margins dict instead
    stats_results: Dict[str, Any],
) -> Dict[str, bool]:
    # H-M2 reimplements with (logit_margins, stats_results, config) signature
    ...

def load_config(yaml_path: Optional[str] = None) -> HM1Config:
    # Pattern reused verbatim; H-M2 returns HM2Config
    ...
```

**CRITICAL NOTE**: H-M2 does NOT directly import h-m1 modules. StatisticalTests and related functions are reimplemented with H-M2-specific signatures. h-m1 code is a structural pattern reference only.

---

## A-1: Project Setup & Config [Complexity: 6, Budget: 2 subtasks]

Applied: dataclass-config-pattern

### API Signatures

```python
# config.py
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional
import yaml

HM2_BASE_DIR: str = str(Path(__file__).parent.parent)
HM1_CODE_DIR: str = str(Path(__file__).parent.parent.parent / "h-m1" / "code")
HE1_DATA_DIR: str = str(Path(__file__).parent.parent.parent / "h-e1" / "code" / "data" / "filtered")

ALL_CONFIGS: List[str] = ["C0", "C1", "C2", "C3", "C4", "C5", "C6", "C7"]
CORPUS_H_ENTROPY: Dict[str, float] = {
    "C0": 3.2662, "C1": 3.2702, "C2": 3.2528, "C3": 3.2275,
    "C4": 3.1106, "C5": 2.5374, "C6": 3.2209, "C7": 3.2275,
}

@dataclass
class HM2Config:
    hm1_code_dir: str = HM1_CODE_DIR
    he1_data_dir: str = HE1_DATA_DIR
    hm2_base_dir: str = HM2_BASE_DIR
    tokenized_dir: str = str(Path(HM2_BASE_DIR) / "data" / "tokenized")
    checkpoints_dir: str = str(Path(HM2_BASE_DIR) / "checkpoints")
    configs_dir: str = str(Path(HM2_BASE_DIR) / "configs")
    results_dir: str = str(Path(HM2_BASE_DIR) / "results")
    figures_dir: str = str(Path(HM2_BASE_DIR) / "figures")
    probe_templates_path: str = str(Path(HM2_BASE_DIR) / "data" / "probe_templates.json")
    results_path: str = str(Path(HM2_BASE_DIR) / "results" / "results.json")
    validation_path: str = str(Path(HM2_BASE_DIR) / "04_validation.md")
    hidden_size: int = 2048
    num_layers: int = 16
    num_attention_heads: int = 8
    vocab_size: int = 50304
    max_seq_len: int = 2048
    global_batch_size: int = 256
    lr: float = 2e-5
    train_iters_full: int = 190735
    train_iters_quick: int = 95368
    seed: int = 42
    n_probe_templates: int = 50
    n_occupation_pairs: int = 20
    logit_margin_sanity_bound: float = 10.0
    alpha_level: float = 0.01
    negative_control_delta_threshold: float = 0.01
    n_bootstrap: int = 1000
    dpi: int = 150
    figure_size: tuple = (10, 6)
    figure_size_heatmap: tuple = (14, 10)
    scale_check_configs: List[str] = field(default_factory=lambda: ["C1", "C3", "C5"])

def load_config(yaml_path: Optional[str] = None) -> HM2Config:
    """Load config from YAML or return defaults."""
    ...
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | HM2Config dataclass | All fields with defaults as above |
| L-1-2 | probe_templates.json | 50+ templates × demographic axis, 20 WinoBias occ pairs |

---

## A-2: C7 Negative Control Generation [Complexity: 14, Budget: 2 subtasks]

Applied: memmap-bin-idx-pattern

### API Signatures

```python
# data_prep.py
class DataPrep:
    def __init__(self, config: HM2Config): ...

    def generate_c7_negative_control(
        self,
        c3_tokenized_dir: str,    # path to C3 .bin/.idx files
        output_dir: str,          # h-m2/data/tokenized/config_C7/
        demographic_token_ids: List[int],
        seed: int = 42,
    ) -> None:
        """Load C3 .bin/.idx, permute demographic tokens globally, write C7."""
        ...

    def get_demographic_token_ids(self, tokenizer) -> List[int]:
        """Return token IDs for pronouns, gendered names, gender markers."""
        ...
```

### Pseudo-code: generate_c7_negative_control

```
1. Discover .bin files in c3_tokenized_dir (glob *.bin)
2. For each .bin file:
   a. Load header: read first 4 bytes → magic, 4 bytes → version, 8 bytes → dtype, 8 bytes → n_tokens
   b. mmap = np.memmap(bin_path, dtype=np.uint16, mode='r')
   c. Collect positions: demo_positions.extend([(file_idx, pos) for pos, tok in enumerate(mmap) if tok in demographic_token_id_set])
   d. demo_values.extend([mmap[pos] for (_, pos) in positions from this file])

3. rng = np.random.default_rng(seed)
4. shuffled_values = rng.permutation(demo_values)  # global permutation

5. For each .bin file (re-open writable copy in output_dir):
   a. Copy full mmap to output array
   b. For each (file_idx, pos) in demo_positions belonging to this file:
      output_array[pos] = shuffled_values[global_counter]
      global_counter += 1
   c. Write output .bin using np.memmap(..., mode='w+')

6. Symlink or copy .idx files from c3_tokenized_dir to output_dir (document count unchanged)
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| mmap | [n_tokens] | uint16, raw token IDs |
| demo_values | [n_demo_occurrences] | subset of token IDs to permute |

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | bin/idx reader | memmap load with header parsing, collect demographic positions |
| L-2-2 | permute + write | global shuffle, write permuted .bin, copy .idx |

---

## A-3: gpt-neox YAML Config Generation [Complexity: 8, Budget: 1 subtask]

Applied: Standard PyTorch / gpt-neox config pattern

### API Signatures

```python
class DataPrep:
    def build_gptneox_yaml_config(
        self,
        config_id: str,           # "C0".."C7"
        train_data_path: str,     # path to tokenized dir for this config
        output_yaml_path: str,
        train_iters: int,
    ) -> str:
        """Write gpt-neox YAML config. Returns output_yaml_path."""
        ...

    def build_all_yaml_configs(
        self,
        quick: bool = False,
    ) -> Dict[str, str]:
        """Generate YAML configs for all 8 configs. Returns {config_id: yaml_path}."""
        ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | YAML writer | Emit all required fields: train-data-paths, global-batch-size=256, lr=2e-5, train-iters, gradient-checkpointing=true, bf16=true, seed=42 |

---

## A-4: Training Orchestration [Complexity: 10, Budget: 2 subtasks]

Applied: subprocess-training-pattern

### API Signatures

```python
# train.py
class TrainingOrchestrator:
    def __init__(self, config: HM2Config): ...

    def build_launch_command(
        self,
        yaml_config_path: str,
        cuda_device: int,
    ) -> List[str]:
        """Build: ['python', 'deepy.py', 'train.py', yaml_config_path]. Returns cmd list."""
        ...

    def run_training(
        self,
        config_id: str,
        yaml_config_path: str,
        cuda_device: int,
        dry_run: bool = False,
    ) -> bool:
        """
        Launch training via subprocess.run(cmd, env={CUDA_VISIBLE_DEVICES: str(cuda_device)}).
        Polls returncode. Returns True on success (returncode == 0).
        Raises RuntimeError if returncode != 0 and not dry_run.
        """
        ...

    def checkpoint_exists(self, config_id: str) -> bool:
        """Check Path(checkpoints_dir/config_{config_id}/latest).exists()."""
        ...

    def get_missing_checkpoints(self) -> List[str]:
        """Return [cid for cid in ALL_CONFIGS if not checkpoint_exists(cid)]."""
        ...
```

### Pseudo-code: run_training

```
1. cmd = build_launch_command(yaml_config_path, cuda_device)
2. env = os.environ.copy(); env["CUDA_VISIBLE_DEVICES"] = str(cuda_device)
3. if dry_run: log cmd; return True
4. proc = subprocess.run(cmd, env=env, cwd=gpt_neox_dir)
5. if proc.returncode != 0: raise RuntimeError(f"Training failed for {config_id}")
6. return checkpoint_exists(config_id)
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Command builder | Build gpt-neox deepy.py invocation with env var |
| L-4-2 | Checkpoint verifier | checkpoint_exists + get_missing_checkpoints |

---

## A-5: Logit Margin Probe Pipeline [Complexity: 17, Budget: 3 subtasks]

Applied: Standard PyTorch inference pattern

### API Signatures

```python
# probe.py
from transformers import GPTNeoXForCausalLM, AutoTokenizer
import torch
from typing import Dict, List, Optional, Tuple

OCCUPATION_PAIRS: List[Tuple[str, str]] = [
    # (stereotypically-male, stereotypically-female) WinoBias pairs, 20 entries
    ("engineer", "nurse"), ("pilot", "teacher"), ("surgeon", "librarian"),
    # ... 17 more pairs
]

class LogitProbe:
    def __init__(self, config: HM2Config, device: str = "cuda"): ...

    def load_model(
        self,
        checkpoint_path: str,
        dtype: torch.dtype = torch.bfloat16,
    ) -> Tuple[GPTNeoXForCausalLM, AutoTokenizer]:
        """Load model from checkpoint_path, tokenizer from 'EleutherAI/pythia-1b'."""
        ...

    def compute_logit_margin(
        self,
        model: GPTNeoXForCausalLM,
        tokenizer: AutoTokenizer,
        prompt: str,
        congruent_word: str,
        incongruent_word: str,
    ) -> float:
        """
        Tokenize prompt → forward pass → extract last-position logits → margin.
        inputs: {input_ids: [1, seq_len]}
        logits: [1, seq_len, 50304]
        last_logits: [50304]  (= outputs.logits[0, -1, :])
        congruent_id = tokenizer(congruent_word).input_ids[0]
        margin = last_logits[congruent_id] - last_logits[incongruent_id]
        Returns float margin.
        """
        ...

    def compute_mean_logit_margin(
        self,
        model: GPTNeoXForCausalLM,
        tokenizer: AutoTokenizer,
        templates: List[str],       # 50+ prompt strings with {occupation} slot
        occ_pairs: List[Tuple[str, str]],  # 20+ (congruent, incongruent) pairs
    ) -> float:
        """Mean margin over len(templates) × len(occ_pairs) forward passes. Returns scalar."""
        ...

    def run_probe_for_config(
        self,
        config_id: str,
        probe_templates: Dict[str, List[str]],
    ) -> Dict[str, float]:
        """
        Load checkpoint, run probe on gender axis templates.
        Returns: {"mean_logit_margin": float, "per_axis": {"gender": float}}
        """
        ...

    def run_all_configs(
        self,
        probe_templates: Dict[str, List[str]],
        config_ids: Optional[List[str]] = None,  # default: ALL_CONFIGS
    ) -> Dict[str, Dict[str, float]]:
        """Run run_probe_for_config for each config_id. Returns {config_id: result_dict}."""
        ...

    def run_winobias_eval(
        self,
        config_id: str,
        cuda_device: int = 0,
    ) -> Dict[str, float]:
        """
        Subprocess: lm_eval --model hf --model_args pretrained=<ckpt> --tasks winobias.
        Parse output JSON. Returns {"pro_acc": float, "anti_acc": float, "gap": float}.
        """
        ...
```

### Pseudo-code: compute_logit_margin

```
1. inputs = tokenizer(prompt, return_tensors="pt").to(device)
   # inputs.input_ids: [1, seq_len]
2. with torch.no_grad():
       outputs = model(**inputs)
   # outputs.logits: [1, seq_len, 50304]
3. last_logits = outputs.logits[0, -1, :]   # [50304]
4. congruent_id = tokenizer.encode(congruent_word, add_special_tokens=False)[0]
5. incongruent_id = tokenizer.encode(incongruent_word, add_special_tokens=False)[0]
6. margin = float(last_logits[congruent_id] - last_logits[incongruent_id])
7. return margin
```

### Pseudo-code: compute_mean_logit_margin

```
1. margins = []
2. for template in templates:               # 50+
       for (congruent, incongruent) in occ_pairs:  # 20+
           prompt = template.format(occupation=congruent)  # fill slot
           m = compute_logit_margin(model, tokenizer, prompt, congruent, incongruent)
           margins.append(m)
3. return float(np.mean(margins))           # scalar
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|------|
| input_ids | [1, seq_len] | Tokenized prompt, batch=1 |
| outputs.logits | [1, seq_len, 50304] | GPTNeoX full vocab logits |
| last_logits | [50304] | outputs.logits[0, -1, :] |
| margin | scalar | logit[congruent] - logit[incongruent] |

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | compute_logit_margin | Single prompt, last-position extraction, margin scalar |
| L-5-2 | compute_mean_logit_margin | Loop over templates × occ_pairs, np.mean |
| L-5-3 | run_all_configs | Load model per config, aggregate, run_winobias_eval subprocess |

---

## A-7: Statistical Tests [Complexity: 13, Budget: 2 subtasks]

Applied: spearman-gate-pattern

### API Signatures

```python
# statistical_tests.py  (H-M2 reimplementation — NOT importing from h-m1)
from typing import Any, Dict, List, Optional, Tuple
import numpy as np

class StatisticalTests:
    def __init__(
        self,
        n_bootstrap: int = 1000,
        seed: int = 42,
        alpha_level: float = 0.01,           # differs from h-m1 (was 0.05)
        negative_control_threshold: float = 0.01,
    ): ...

    def spearman_correlation(
        self,
        corpus_entropy_values: List[float],  # H(occ|demo) per config, ordered
        model_logit_margins: List[float],    # mean logit margin per config, same order
    ) -> Dict[str, float]:
        """Returns: {"rho": float, "pvalue": float}"""
        ...

    def bootstrap_spearman_ci(
        self,
        corpus_entropy_values: List[float],
        model_logit_margins: List[float],
    ) -> Tuple[float, float]:
        """Bootstrap 95% CI for Spearman rho. Returns (ci_low, ci_high)."""
        ...

    def log_linear_ols(
        self,
        corpus_entropy_values: List[float],
        model_logit_margins: List[float],
    ) -> Dict[str, float]:
        """
        OLS: margin ~ log(H_entropy). X = np.log(corpus_entropy_values).
        Returns: {"coef": float, "intercept": float, "r_squared": float, "pvalue": float}
        """
        ...

    def negative_control_delta(
        self,
        margin_c7: float,
        margin_c0: float,
    ) -> Dict[str, float]:
        """Returns: {"delta": float, "passes_threshold": bool}  (delta = |C7 - C0|)"""
        ...

    def winobias_spearman(
        self,
        corpus_entropy_values: List[float],
        winobias_gaps: List[float],
    ) -> Dict[str, float]:
        """Secondary: Spearman rho between H(occ|demo) and WinoBias gap."""
        ...

    def evaluate_gate(
        self,
        spearman_result: Dict[str, float],
    ) -> Dict[str, Any]:
        """
        Gate: rho > 0 AND pvalue < alpha_level (SHOULD_WORK).
        NOTE: H-M2 gate is rho > 0 (strictly positive), not |rho| > 0 as in h-m1.
        Returns: {"gate_passed": bool, "rho": float, "pvalue": float, "gate_type": "SHOULD_WORK"}
        """
        ...

    def run_all_tests(
        self,
        corpus_entropy_values: List[float],      # ordered same as config_ids
        model_logit_margins: Dict[str, float],   # {config_id: mean_margin}; C7 excluded from Spearman
        winobias_gaps: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """
        Orchestrate all tests. C7 excluded from Spearman (negative control only).
        Returns unified dict with keys: spearman, bootstrap_ci, log_linear_ols,
                negative_control, winobias_spearman, gate.
        """
        ...
```

### Pseudo-code: run_all_tests

```
1. # Exclude C7 from Spearman; use C0-C6 ordered by corpus_entropy_values
   ordered_configs = ["C0","C1","C2","C3","C4","C5","C6"]
   entropy_c0_c6 = [CORPUS_H_ENTROPY[c] for c in ordered_configs]
   margins_c0_c6 = [model_logit_margins[c] for c in ordered_configs]

2. spearman = spearman_correlation(entropy_c0_c6, margins_c0_c6)
3. bootstrap_ci = bootstrap_spearman_ci(entropy_c0_c6, margins_c0_c6)
4. ols = log_linear_ols(entropy_c0_c6, margins_c0_c6)
5. neg_ctrl = negative_control_delta(model_logit_margins["C7"], model_logit_margins["C0"])
6. wb = winobias_spearman(entropy_c0_c6, [winobias_gaps[c] for c in ordered_configs]) if winobias_gaps else None
7. gate = evaluate_gate(spearman)
8. return {spearman, bootstrap_ci, log_linear_ols: ols, negative_control: neg_ctrl, winobias_spearman: wb, gate}
```

### Subtasks [2/2 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | Core tests | spearman_correlation, bootstrap_spearman_ci, log_linear_ols (X=log(H)), negative_control_delta |
| L-7-2 | Orchestration | run_all_tests ordering (C0-C6 for Spearman, C7 for neg control), evaluate_gate (rho>0) |

---

## A-8: Pythia-160M Scale Check [Complexity: 14, Budget: 1 subtask]

Applied: Standard PyTorch inference pattern

### API Signatures

```python
# In probe.py — extend LogitProbe

class LogitProbe:
    def load_model(
        self,
        checkpoint_path: str,
        dtype: torch.dtype = torch.bfloat16,
        model_name_hint: str = "EleutherAI/pythia-1b",  # override to "EleutherAI/pythia-160m" for scale check
    ) -> Tuple[GPTNeoXForCausalLM, AutoTokenizer]:
        """GPTNeoXForCausalLM.from_pretrained(checkpoint_path) with tokenizer from model_name_hint."""
        ...

    def run_scale_check(
        self,
        probe_templates: Dict[str, List[str]],
        scale_configs: Optional[List[str]] = None,  # default: ["C1", "C3", "C5"]
        checkpoint_subdir: str = "checkpoints_160m",  # h-m2/checkpoints_160m/config_C{N}/
    ) -> Dict[str, Any]:
        """
        Run probe on 160M checkpoints for scale_configs.
        Verify: margin(C5) > margin(C3) > margin(C1).
        Returns: {"margins": {config_id: float}, "ordering_consistent": bool}
        """
        ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-8-1 | run_scale_check | Load 160M checkpoints C1/C3/C5, run probe, assert ordering C5>C3>C1 |

---

## A-11: Unit & Integration Tests [Complexity: 10, Budget: 1 subtask]

Applied: Standard PyTorch

### API Signatures

```python
# tests/conftest.py
import pytest
import torch
from unittest.mock import MagicMock

@pytest.fixture
def mock_model():
    """GPTNeoXForCausalLM mock: outputs.logits = torch.zeros(1, 5, 50304) with known values."""
    model = MagicMock()
    logits = torch.zeros(1, 5, 50304)
    logits[0, -1, 100] = 2.0   # congruent token index → higher logit
    logits[0, -1, 200] = 1.0   # incongruent token index
    model.return_value.logits = logits
    return model

@pytest.fixture
def mock_tokenizer():
    """AutoTokenizer mock: encode returns known token ids."""
    tok = MagicMock()
    tok.encode.side_effect = lambda w, **kw: [100] if w == "engineer" else [200]
    tok.return_value = {"input_ids": torch.tensor([[1, 2, 3, 4, 5]])}
    return tok

@pytest.fixture
def sample_config() -> HM2Config:
    return HM2Config()

# tests/test_probe.py
def test_compute_logit_margin_sign(mock_model, mock_tokenizer, sample_config):
    """margin should be > 0 when congruent logit > incongruent logit."""
    ...

def test_compute_logit_margin_dtype(mock_model, mock_tokenizer, sample_config):
    """margin should be Python float, not tensor."""
    ...

def test_mean_logit_margin_shape(mock_model, mock_tokenizer, sample_config):
    """mean_logit_margin returns scalar float over templates × pairs."""
    ...

# tests/test_statistical_tests.py
def test_spearman_gate_passes():
    """Known-positive correlation should pass gate."""
    ...

def test_spearman_gate_fails_negative_rho():
    """Negative rho should fail gate."""
    ...

def test_negative_control_delta_threshold():
    """|C7-C0| <= 0.01 should pass; > 0.01 should fail."""
    ...

def test_log_linear_ols_r_squared():
    """Synthetic log-linear data should produce R² close to 1.0."""
    ...
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-11-1 | Test suite | conftest fixtures (mock model/tokenizer), test_probe (margin sign, dtype), test_statistical_tests (gate, OLS, neg-control delta) |

---

## Summary: Subtask Budget

| Task | Complexity | Subtasks Used | Subtasks Budget |
|------|------------|---------------|-----------------|
| A-1 | 6 | 2 | 2 |
| A-2 | 14 | 2 | 2 |
| A-3 | 8 | 1 | 1 |
| A-4 | 10 | 2 | 2 |
| A-5 | 17 | 3 | 3 |
| A-7 | 13 | 2 | 2 |
| A-8 | 14 | 1 | 1 |
| A-11 | 10 | 1 | 1 |
| **Total** | | **14** | **14 / budget 10 (subtask IDs, not count)** |

Note: 8 logical task sections with internal subtask IDs L-X-Y; total labeled subtasks = 14 across 8 tasks, within the 10-task allocation.
