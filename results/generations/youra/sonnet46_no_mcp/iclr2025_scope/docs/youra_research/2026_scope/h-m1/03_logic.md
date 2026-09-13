# Logic: H-M1 — Attention Entropy Mechanistic Analysis

Applied: attention-entropy-mechanistic-analysis pattern
Applied: paired-ttest-layer-comparison pattern
Applied: longbench-evaluation-protocol pattern

---

## Codebase Analysis (Serena)

**Project Type**: base_hypothesis
**Status**: API signatures verified from base code (h-e1/code/model.py, h-e1/code/config.py)
**Analyzed Path**: `docs/youra_research/20260504_scope/h-e1/code/`
**Relevant Symbols**:
- `H2OEvictionAwareAttention.__init__(base_attention, kv_budget_ratio=0.5)`
- `H2OEvictionAwareAttention.forward(hidden_states, attention_mask=None, **kwargs)` — skips eviction when `not self.training` (line 37-38)
- `inject_h2o_wrappers(model, kv_budget_ratio)` — replaces LlamaAttention/MistralAttention
- `load_base_model(model_name)` — bfloat16 if supported else float16, `device_map="auto"`, `use_cache=False`
- `LoRAConfig(rank=16, alpha=32, dropout=0.05, target_modules=["q_proj","v_proj"])`
- `TrainingConfig.output_dir` pattern: `outputs/h-e1/{model}-{condition}/`

---

## External Dependencies (Base Hypothesis)

### API Signatures (From Actual Code)

```python
# From: h-e1/code/model.py (ACTUAL CODE)

class H2OEvictionAwareAttention(nn.Module):
    def __init__(self, base_attention: nn.Module, kv_budget_ratio: float = 0.5): ...

    def forward(
        self,
        hidden_states: torch.Tensor,
        attention_mask=None,
        **kwargs
    ) -> tuple:
        # CRITICAL: when not self.training -> returns self.base_attention(...) directly
        # H-M1 must NOT rely on this for inference-time eviction
        ...

    def h2o_mask(self, attn_scores: torch.Tensor) -> torch.Tensor:
        # attn_scores: [B, H, T_q, T_k] -> mask: [B, H, T_q, T_k] bool
        ...

def load_base_model(model_name: str) -> AutoModelForCausalLM:
    # dtype = bfloat16 if supported else float16
    # device_map="auto", use_cache=False
    ...

def inject_h2o_wrappers(model: nn.Module, kv_budget_ratio: float) -> nn.Module:
    # Replaces LlamaAttention/MistralAttention with H2OEvictionAwareAttention
    ...
```

**Verified from**: `docs/youra_research/20260504_scope/h-e1/code/model.py` (actual code, line 36-38)

**Critical Note**: `H2OEvictionAwareAttention.forward()` returns `self.base_attention(...)` unmodified when `not self.training`. H-M1 inference must use `model.train()` mode to activate H2O eviction masks, OR apply eviction via `attention_mask` pre-computation. Recommended: call `model.train()` before `extract_metrics()` to activate H2O masking, then immediately return to `model.eval()`.

---

## A-3: Adapter Model Loading [Complexity: 16, Budget: 4 subtasks]

Applied: PEFT adapter inference loading pattern

### API Signatures

```python
# h-m1/code/model.py

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../h-e1/code"))
from model import load_base_model, inject_h2o_wrappers, H2OEvictionAwareAttention

def load_adapter_model(
    model_name: str,
    adapter_checkpoint: str,
    condition: str,                  # "eviction-aware" | "baseline"
    kv_budget_ratio: float = 0.5,
    fp16: bool = True,
) -> nn.Module:
    """Load base model + PEFT adapter; inject H2O wrappers for eviction condition."""
    ...

def set_h2o_training_mode(model: nn.Module, train_mode: bool) -> None:
    """Set H2OEvictionAwareAttention wrappers to train/eval mode for eviction activation.

    H2OEvictionAwareAttention.forward() only applies eviction when self.training=True.
    Call with train_mode=True before extract_metrics() to activate eviction mask.
    """
    for module in model.modules():
        if isinstance(module, H2OEvictionAwareAttention):
            if train_mode:
                module.train()
            else:
                module.eval()
```

### Pseudo-code

```
load_adapter_model(model_name, adapter_checkpoint, condition, kv_budget_ratio, fp16):
    1. base_model = load_base_model(model_name)  # bfloat16/float16, device_map="auto"
    2. if condition == "eviction-aware":
           base_model = inject_h2o_wrappers(base_model, kv_budget_ratio)
    3. model = PeftModel.from_pretrained(base_model, adapter_checkpoint)
    4. model.eval()  # base eval mode
    5. return model
    # Note: call set_h2o_training_mode(model, True) before extraction to activate H2O
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | sys.path injection | Insert h-e1/code to sys.path; import H2O symbols |
| L-3-2 | load_adapter_model | load_base_model + inject_h2o_wrappers + PeftModel.from_pretrained |
| L-3-3 | set_h2o_training_mode | Toggle H2OEvictionAwareAttention train/eval for inference-time eviction |
| L-3-4 | checkpoint fallback | If adapter_checkpoint not found, raise FileNotFoundError with descriptive message |

---

## A-4: Attention Extraction [Complexity: 15, Budget: 4 subtasks]

Applied: output_attentions=True transformer extraction pattern

### API Signatures

```python
# h-m1/code/model.py

class AttentionAnalysisExtractor:
    def __init__(self, model: nn.Module, top_ratio: float = 0.2):
        """model: loaded PeftModel; top_ratio: heavy-hitter fraction."""
        self.model = model
        self.top_ratio = top_ratio

    def verify_attention_extraction(
        self,
        tokenizer,
        device: str,
        max_length: int = 512,
    ) -> None:
        """Smoke test: verify output_attentions=True shapes and softmax normalization."""
        ...

    def extract_metrics(
        self,
        input_ids: torch.Tensor,        # [1, seq_len]
        attention_mask: torch.Tensor,   # [1, seq_len]
    ) -> Tuple[List[float], List[float]]:
        """Run forward pass with H2O eviction active; compute per-layer entropy and HH.

        Returns: (entropy_per_layer, hh_per_layer) each List[float] len=num_layers
        """
        ...

    @staticmethod
    def compute_entropy(
        attn_weights: torch.Tensor,     # [B, H, S, S]
        eps: float = 1e-9,
    ) -> float:
        """Mean attention entropy over heads and query positions. Returns scalar (nats)."""
        ...

    @staticmethod
    def compute_hh_concentration(
        attn_weights: torch.Tensor,     # [B, H, S, S]
        top_ratio: float = 0.2,
    ) -> float:
        """Ratio of attention mass on top top_ratio fraction of key tokens. Returns scalar."""
        ...
```

### Tensor Shapes

| Variable | Shape | Note |
|----------|-------|-------|
| input_ids | [1, S] | batch_size=1 required |
| attn_weights (per layer) | [1, H, S, S] | from output_attentions tuple |
| entropy scalar | [] | averaged over H and S_q |
| hh_concentration | [] | ratio in [0, 1] |

### Pseudo-code

```
extract_metrics(input_ids, attention_mask):
    1. set_h2o_training_mode(self.model, train_mode=True)  # activate H2O eviction
    2. with torch.no_grad():
           out = self.model(input_ids, attention_mask, output_attentions=True)
    3. set_h2o_training_mode(self.model, train_mode=False)
    4. attn_tuple = out.attentions  # tuple of (1, H, S, S), len=num_layers
    5. For each layer_attn in attn_tuple:
           entropy_per_layer.append(compute_entropy(layer_attn))
           hh_per_layer.append(compute_hh_concentration(layer_attn, top_ratio))
    6. return entropy_per_layer, hh_per_layer

compute_entropy(attn_weights, eps=1e-9):
    # attn_weights: [B, H, S, S], last dim is key distribution (softmax rows)
    H_val = -(attn_weights * (attn_weights + eps).log()).sum(dim=-1)  # [B, H, S]
    return H_val.mean().item()

compute_hh_concentration(attn_weights, top_ratio=0.2):
    S = attn_weights.shape[-1]
    k = max(1, int(S * top_ratio))
    topk_vals, _ = attn_weights.topk(k, dim=-1)   # [B, H, S_q, k]
    return topk_vals.sum(dim=-1).mean().item()      # mean over B, H, S_q
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | extract_metrics | Forward pass with H2O train-mode toggle; collect attentions tuple |
| L-4-2 | compute_entropy | Entropy over key dim, averaged over heads and query positions |
| L-4-3 | compute_hh_concentration | Top-k attention mass ratio per layer |
| L-4-4 | verify_attention_extraction | Smoke test: shape check, softmax row-sum ≈ 1, non-NaN |

---

## A-7: Evaluation Runner [Complexity: 15, Budget: 4 subtasks]

Applied: longbench-evaluation-protocol pattern

### API Signatures

```python
# h-m1/code/evaluate.py

from config import InferenceConfig, ExperimentConfig
from data import LongBenchDataLoader
from model import AttentionAnalysisExtractor, load_adapter_model
from analyze import MetricsAggregator

def run_inference_condition(
    extractor: AttentionAnalysisExtractor,
    dataloader: LongBenchDataLoader,
    aggregator: MetricsAggregator,
    condition: str,                          # "eviction-aware" | "baseline"
    device: str,
    min_samples_per_category: int = 500,
) -> MetricsAggregator:
    """Iterate LongBench samples; extract per-layer metrics; feed aggregator."""
    ...

def collect_layer_metrics(
    baseline_cfg: InferenceConfig,
    proposed_cfg: InferenceConfig,
    experiment_cfg: ExperimentConfig,
    device: str,
) -> MetricsAggregator:
    """Load both adapter models, run both conditions, return populated aggregator."""
    ...

def run_evaluation(
    experiment_cfg: ExperimentConfig,
    device: str,
) -> dict:
    """Full pipeline: collect_layer_metrics -> StatisticalAnalyzer -> gate check.

    Returns: {"gate_passed": bool, "fraction_significant": float,
              "results": List[StatisticalResult], "aggregator": MetricsAggregator}
    """
    ...
```

### Pseudo-code

```
run_inference_condition(extractor, dataloader, aggregator, condition, device, min_samples):
    category_counts = defaultdict(int)
    for sample in dataloader.iter_all_samples():
        cat = sample["category"]
        if category_counts[cat] >= min_samples:
            continue
        input_ids = sample["input_ids"].unsqueeze(0).to(device)   # [1, S]
        attn_mask = sample["attention_mask"].unsqueeze(0).to(device)
        entropy_list, hh_list = extractor.extract_metrics(input_ids, attn_mask)
        aggregator.add_sample(condition, entropy_list, hh_list,
                              task=sample["task"], category=cat)
        category_counts[cat] += 1
    return aggregator

collect_layer_metrics(baseline_cfg, proposed_cfg, experiment_cfg, device):
    num_layers = get_num_layers(baseline_cfg.model_name)
    aggregator = MetricsAggregator(num_layers)
    # Load and run baseline
    baseline_model = load_adapter_model(baseline_cfg.model_name, baseline_cfg.adapter_checkpoint,
                                        "baseline", baseline_cfg.kv_budget_ratio)
    baseline_ext = AttentionAnalysisExtractor(baseline_model, top_ratio=baseline_cfg.top_ratio)
    tokenizer = AutoTokenizer.from_pretrained(baseline_cfg.model_name)
    dl = LongBenchDataLoader(tokenizer, baseline_cfg.max_seq_length)
    run_inference_condition(baseline_ext, dl, aggregator, "baseline", device,
                            experiment_cfg.min_samples_per_category)
    del baseline_model  # free GPU memory before loading proposed
    torch.cuda.empty_cache()
    # Load and run eviction-aware
    proposed_model = load_adapter_model(proposed_cfg.model_name, proposed_cfg.adapter_checkpoint,
                                        "eviction-aware", proposed_cfg.kv_budget_ratio)
    proposed_ext = AttentionAnalysisExtractor(proposed_model, top_ratio=proposed_cfg.top_ratio)
    run_inference_condition(proposed_ext, dl, aggregator, "eviction-aware", device,
                            experiment_cfg.min_samples_per_category)
    return aggregator
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | run_inference_condition | Iterate samples per category up to min_samples; call extract_metrics |
| L-7-2 | collect_layer_metrics | Sequential model load → run → delete → run second condition |
| L-7-3 | run_evaluation | Orchestrate full pipeline: collect → analyze → gate → return dict |
| L-7-4 | get_num_layers helper | Infer num_hidden_layers from model config or len(model.layers) |

---

## A-6: Statistical Analysis [Complexity: 14, Budget: 3 subtasks]

Applied: paired-ttest-layer-comparison pattern

### API Signatures

```python
# h-m1/code/analyze.py

from scipy import stats
import numpy as np
from typing import List
from dataclasses import dataclass

@dataclass
class LayerMetrics:
    layer_idx: int
    baseline_entropy: List[float]           # len = N samples
    proposed_entropy: List[float]
    baseline_hh_concentration: List[float]
    proposed_hh_concentration: List[float]
    n_samples: int

@dataclass
class StatisticalResult:
    layer_idx: int
    entropy_pvalue: float
    entropy_statistic: float
    entropy_mean_diff: float                # proposed - baseline
    hh_pvalue: float
    hh_statistic: float
    hh_mean_diff: float

class StatisticalAnalyzer:
    def run_paired_ttest(
        self,
        layer_metrics: List[LayerMetrics],
    ) -> List[StatisticalResult]:
        """Paired t-test per layer (scipy.stats.ttest_rel). Returns per-layer results."""
        ...

    def compute_gate_result(
        self,
        results: List[StatisticalResult],
        significance_threshold: float = 0.05,
        gate_fraction: float = 0.5,
    ) -> dict:
        """Returns: {"passed": bool, "fraction_significant": float,
                     "significant_layers": List[int]}"""
        ...

    def summarize(
        self,
        results: List[StatisticalResult],
    ) -> dict:
        """Mean entropy_mean_diff, mean hh_mean_diff, fraction_significant."""
        ...
```

### Pseudo-code

```
run_paired_ttest(layer_metrics):
    results = []
    for lm in layer_metrics:
        t_ent, p_ent = scipy.stats.ttest_rel(lm.proposed_entropy, lm.baseline_entropy)
        t_hh, p_hh = scipy.stats.ttest_rel(lm.proposed_hh_concentration,
                                            lm.baseline_hh_concentration)
        results.append(StatisticalResult(
            layer_idx=lm.layer_idx,
            entropy_pvalue=p_ent, entropy_statistic=t_ent,
            entropy_mean_diff=mean(proposed_entropy) - mean(baseline_entropy),
            hh_pvalue=p_hh, hh_statistic=t_hh,
            hh_mean_diff=mean(proposed_hh) - mean(baseline_hh),
        ))
    return results

compute_gate_result(results, significance_threshold=0.05, gate_fraction=0.5):
    sig_layers = [r.layer_idx for r in results if r.entropy_pvalue < significance_threshold]
    fraction = len(sig_layers) / len(results)
    return {"passed": fraction >= gate_fraction,
            "fraction_significant": fraction,
            "significant_layers": sig_layers}
```

### Subtasks [3/3 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | run_paired_ttest | scipy.stats.ttest_rel per layer for entropy and HH; build StatisticalResult list |
| L-6-2 | compute_gate_result | Count p < 0.05 layers; compute fraction; check >= gate_fraction |
| L-6-3 | MetricsAggregator.get_layer_metrics | Reformat per-sample data into LayerMetrics list with paired arrays |

---

## Subtask Budget Summary

| Task | Allocated | Used |
|------|-----------|------|
| A-3 | 4 | 4 |
| A-4 | 4 | 4 |
| A-7 | 4 | 4 |
| A-6 | 3 | 3 |
| **Total** | **15** | **15** |
