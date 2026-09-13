# Experiment Design: H-M3

**Date:** 2026-08-28
**Author:** Anonymous
**Hypothesis Statement:** Bidirectional models maintain ≥95% of baseline B2 AlpacaEval win rate
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM Hypothesis** - Tests helpfulness maintenance under multi-objective training

---

## Workflow Status

**Verification State:** IN_PROGRESS
**Prerequisites Satisfied:** H-M1 PASS (combined reward optimization validated)
**Gate Status:** SHOULD_WORK

---

## Hypothesis Context

### Current Hypothesis
- **ID:** H-M3
- **Type:** MECHANISM
- **Prerequisites:** H-M1 (combined reward optimization)

### Gate Condition
SHOULD_WORK: Best configuration Ti achieves AlpacaEval ≥ 0.95 × B2

---

## Continuation Context

### Previous Hypothesis Results (H-M1)

From H-M1 validation (04_validation.md):
- **Combined reward optimization:** Validated ✓
- **KL divergence:** Stable (max=0.114 << 5.0)
- **Optimal α/β:** α=0.5, β=0.5 baseline tested
- **PPO config:** lr=1.41e-5, kl_coef=0.05, batch=8

**Reuse for H-M3:**
- PPO training infrastructure from H-M1
- IFEvalRewardSignal module from H-E1
- CombinedRewardModel wrapper from H-M1

---

## Implementation Research Summary

### Archon Knowledge Base Findings

*MCP Unavailable* - Using domain knowledge:

**AlpacaEval Evaluation Protocol:**
- Standard benchmark for LLM helpfulness/quality
- Uses GPT-4 as judge for win-rate computation
- Reference: tatsu-lab/alpaca_eval repository
- Metric: LC (Length-Controlled) Win Rate preferred

**Multi-Objective RLHF Trade-offs:**
- Higher controllability weight (β) risks helpfulness degradation
- Standard practice: sweep α ∈ {0.2, 0.4, 0.6, 0.8}
- Pareto frontier identifies optimal trade-off point

### Archon Code Examples

*MCP Unavailable* - Using established patterns from trl library

### Exa GitHub Implementations

*MCP Unavailable* - Using known references:

**Repository 1**: tatsu-lab/alpaca_eval (⭐ 1.5k+)
- **URL**: https://github.com/tatsu-lab/alpaca_eval
- **Relevance**: Official AlpacaEval benchmark
- **Evaluation Code**: `alpaca_eval evaluate` CLI

**Repository 2**: huggingface/trl (⭐ 8k+)
- **URL**: https://github.com/huggingface/trl
- **Relevance**: PPO trainer used in H-M1
- **Reuse**: PPOTrainer config from H-M1 validation

### 🎯 Implementation Priority Assessment

**Primary Implementation Path:** Reuse H-M1 infrastructure, add α-sweep
**Fallback:** Direct alpaca_eval CLI evaluation if programmatic fails
**Justification:** H-M1 validated core training loop; H-M3 only adds evaluation sweep

### Code Analysis (Serena MCP)

*Skipped* - Code from H-M1 validation is reused, no complex new code required

---

## Experiment Specification

### Dataset

**Name:** AlpacaEval Test Set
**Type:** standard
**Source:** tatsu-lab/alpaca_eval

**Loading Information:**
- Method: HuggingFace datasets
- Identifier: `tatsu-lab/alpaca_eval`
- Code:
```python
from datasets import load_dataset
eval_dataset = load_dataset("tatsu-lab/alpaca_eval")
# 805 evaluation prompts
```

**Statistics:**
- Evaluation samples: 805 prompts
- Format: instruction → model response → GPT-4 judgment

**Training Data (for models):**
- UltraFeedback (from H-M1): ~60k preference pairs
- IFEval (from H-E1): 541 instructions, 70/30 split

### Models

#### Baseline Model (B2)

**Architecture:** Llama-3-8B-Instruct + Helpfulness-Only RLHF

**Loading Information:**
- Method: HuggingFace transformers
- Identifier: `meta-llama/Meta-Llama-3-8B-Instruct`
- Code:
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
base_model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Meta-Llama-3-8B-Instruct",
    torch_dtype=torch.bfloat16,
    device_map="auto"
)
```

**B2 Training:** Helpfulness-only RLHF (α=1.0, β=0.0)

#### Proposed Models (T1-T4)

**Architecture:** Baseline + Combined Reward (α·R_helpfulness + β·R_IFEval)

**Configurations to Test:**

| Config | α (helpfulness) | β (controllability) | Expected Effect |
|--------|-----------------|---------------------|-----------------|
| T1 | 0.2 | 0.8 | High controllability, possible helpfulness drop |
| T2 | 0.4 | 0.6 | Balanced-controllability |
| T3 | 0.6 | 0.4 | Balanced-helpfulness |
| T4 | 0.8 | 0.2 | High helpfulness, low controllability gain |

**Core Mechanism Implementation:**

```python
class AlphaWeightedPPOTrainer:
    """
    PPO trainer with configurable α/β weights for multi-objective reward.
    Tests whether helpfulness (AlpacaEval) maintains ≥95% of baseline.
    """
    def __init__(self, alpha: float, beta: float, base_trainer: PPOTrainer):
        self.alpha = alpha
        self.beta = beta
        self.trainer = base_trainer
        self.helpfulness_rm = load_helpfulness_reward()  # DeBERTa or similar
        self.ifeval_signal = IFEvalRewardSignal()  # From H-E1

    def compute_reward(self, query: str, response: str) -> float:
        """Combined reward for PPO step."""
        r_help = self.helpfulness_rm.score(query, response)  # [0,1]
        r_ctrl = self.ifeval_signal.compute_rate(response)   # [0,1]
        return self.alpha * r_help + self.beta * r_ctrl

    def train_and_evaluate(self, configs: list[tuple[float, float]]):
        """Sweep α/β configs, evaluate each on AlpacaEval."""
        results = {}
        for alpha, beta in configs:
            self.alpha, self.beta = alpha, beta
            checkpoint = self.trainer.train(reward_fn=self.compute_reward)
            win_rate = evaluate_alpaca_eval(checkpoint)
            results[(alpha, beta)] = win_rate
        return results

# Usage:
# configs = [(0.2, 0.8), (0.4, 0.6), (0.6, 0.4), (0.8, 0.2)]
# results = trainer.train_and_evaluate(configs)
# best = max(results.items(), key=lambda x: x[1])
# pass_condition = best[1] >= 0.95 * b2_win_rate
```

### Training Protocol

**From H-M1 Validated Configuration:**
- **Optimizer:** AdamW (β1=0.9, β2=0.999, weight_decay=0.01)
- **Learning Rate:** 1.41e-5 (PPO standard for LLMs)
- **Schedule:** Constant with warmup (10% steps)
- **Batch Size:** 8 (from H-M1)
- **PPO Steps:** 1000 (full training) or 100 (PoC)
- **KL Coefficient:** 0.05
- **Seeds:** 1 (PoC)

**Training Sweep:**
- 4 configurations: T1 (α=0.2), T2 (α=0.4), T3 (α=0.6), T4 (α=0.8)
- Plus B2 baseline: α=1.0, β=0.0

### Evaluation

**Primary Metric:** AlpacaEval LC Win Rate

**Evaluation Protocol:**
```python
from alpaca_eval import evaluate

def evaluate_alpaca_eval(model_path: str) -> float:
    """Evaluate checkpoint on AlpacaEval 2.0 LC."""
    results = evaluate(
        model_outputs=generate_responses(model_path),
        annotators_config="alpaca_eval_gpt4_turbo_fn",
        output_path=f"results/{model_path.split('/')[-1]}/"
    )
    return results["lc_win_rate"]

# B2 baseline: ~25-35% win rate (typical for 8B models)
# T* threshold: ≥ 0.95 × B2 win rate
```

**Success Criteria:**
- Primary: best(T1,T2,T3,T4) achieves AlpacaEval_LC ≥ 0.95 × B2
- Secondary: Identify clear Pareto frontier (IFEval vs AlpacaEval)

**Expected Baseline Performance:**
- B2 (helpfulness-only): ~30% LC win rate (from typical Llama-3-8B results)
- Pass threshold: ≥28.5% LC win rate

**Metrics Loading Information:**
- Task Type: LLM evaluation
- Library: alpaca_eval
- Code:
```python
# Install: pip install alpaca-eval
from alpaca_eval import evaluate
# Requires OPENAI_API_KEY for GPT-4 judge
```

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: B2 vs T1-T4 AlpacaEval win rates bar chart

#### Additional Figures (LLM Autonomous)
- Pareto frontier plot (IFEval strict accuracy vs AlpacaEval LC win rate)
- α sweep line chart showing win rate vs α value
- Trade-off heatmap if multiple seeds available

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m3/figures/`.

---

## 🔬 Mechanism Verification Protocol

### Pre-conditions
- **mechanism_exists:** true - Combined reward from H-M1
- **mechanism_isolatable:** true - α/β weights are the only variable
- **baseline_measurable:** true - B2 (α=1.0) serves as baseline

### Architecture Compatibility
- **architecture_compatibility:** Compatible - H-M1 infrastructure reused

### Activation Indicators
- **mechanism_log_message:** "α={alpha}, β={beta} training complete. AlpacaEval={win_rate}"
- **tensor_shape_change:** N/A (evaluation metric, not tensor)
- **metric_delta_expected:** T* win_rate ≥ 0.95 × B2 win_rate

### Mechanism Verification Code
```python
def verify_h_m3(b2_win_rate: float, t_win_rates: dict[str, float]) -> bool:
    """Verify H-M3: helpfulness maintained at ≥95% of B2."""
    best_t = max(t_win_rates.values())
    threshold = 0.95 * b2_win_rate
    
    print(f"B2 baseline: {b2_win_rate:.3f}")
    print(f"Best T*: {best_t:.3f}")
    print(f"Threshold (0.95×B2): {threshold:.3f}")
    print(f"Gate: {'PASS' if best_t >= threshold else 'FAIL'}")
    
    return best_t >= threshold

# hypothesis_support_threshold: 0.95 × B2
# hypothesis_support_metric: AlpacaEval LC win rate
```

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. Code runs without error for all 4 T* configurations
2. At least one T* achieves win_rate ≥ 0.95 × B2_win_rate

---

## Appendix: Reference Implementations

### A. Previous Hypothesis Artifacts (H-M1)

**Source:** h-m1/04_validation.md
- PPO training loop validated
- CombinedRewardModel working
- IFEvalRewardSignal from H-E1 integrated

**Code Reuse:**
- `h-m1/code/config.py` → Base PPO config
- `h-m1/code/rewards.py` → CombinedRewardModel
- `h-m1/code/train_ppo.py` → Training loop

### B. AlpacaEval Reference

**Source:** tatsu-lab/alpaca_eval GitHub
- Standard evaluation protocol
- GPT-4 turbo as judge
- Length-controlled (LC) metric preferred

### C. Traceability Matrix

| Specification | Source Type | Source Reference |
|--------------|-------------|------------------|
| PPO config | Previous | H-M1 validation |
| α/β sweep | Phase 2B | 02b_verification_plan.md |
| AlpacaEval protocol | GitHub | tatsu-lab/alpaca_eval |
| Success threshold | Phase 2B | ≥95% of B2 |
| Training infra | Previous | H-M1 code artifacts |

---

## State Information

**State File:** verification_state.yaml (ABLATION: injected via prompt)
**Date:** 2026-08-28

### Workflow History for This Hypothesis
- IN_PROGRESS: Phase 2C experiment design started
- Prerequisite H-M1: PASS (combined reward validated)

---

*MCP Tools Used: None available (Archon/Exa/Serena unavailable)*
*Specifications grounded in H-M1 validated artifacts and domain knowledge*
*Next Phase: Phase 3 - Implementation Planning*
