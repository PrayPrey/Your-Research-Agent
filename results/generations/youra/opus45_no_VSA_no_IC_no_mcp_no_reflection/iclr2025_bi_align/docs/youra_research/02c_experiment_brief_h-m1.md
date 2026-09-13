# Experiment Brief: H-M1

**Hypothesis:** Combined reward R = α·R_AlpacaEval + β·R_IFEval_rate can be optimized via PPO without divergence or reward hacking

**Type:** MECHANISM (MUST_WORK gate)
**Prerequisites:** H-E1 (VALIDATED)

---

## 1. Experiment Objective

Validate that PPO training with a combined multi-objective reward (helpfulness + controllability) converges stably without reward hacking.

**Core Question:** Can we optimize two potentially competing reward signals simultaneously?

---

## 2. Dataset Configuration

| Component | Selection | Source |
|-----------|-----------|--------|
| Training Data | UltraFeedback | openbmb/UltraFeedback (HuggingFace) |
| IFEval Prompts | google/IFEval | 541 prompts with constraint specifications |
| AlpacaEval Eval | tatsu-lab/alpaca_eval | 805 prompts for helpfulness baseline |

**Dataset Type:** standard (real data, not synthetic)

**Split Strategy:**
- UltraFeedback: Full train split (~60k preference pairs)
- IFEval: 70% train / 30% held-out test
- Training steps: 1000 PPO steps (convergence test scope)

---

## 3. Model Configuration

| Component | Selection | Justification |
|-----------|-----------|---------------|
| Base Model | meta-llama/Meta-Llama-3-8B-Instruct | Standard RLHF baseline, well-documented |
| Reference Model | Same (frozen) | KL divergence anchor |
| Reward Model | Combined (custom) | α·R_helpfulness + β·R_IFEval |

---

## 4. Reward Architecture

### 4.1 Helpfulness Reward (R_AlpacaEval)
- Source: Pre-trained reward model (e.g., OpenAssistant/reward-model-deberta-v3)
- Output: Scalar quality score per response

### 4.2 Controllability Reward (R_IFEval)
- Source: H-E1 validated `IFEvalRewardSignal` module
- Output: Continuous [0,1] constraint satisfaction rate

### 4.3 Combined Reward
```python
R_combined = alpha * R_helpfulness + beta * R_IFEval
# Baseline configuration: alpha=0.5, beta=0.5
```

---

## 5. PPO Training Configuration

| Parameter | Value | Justification |
|-----------|-------|---------------|
| Learning Rate | 1.41e-5 | TRL default for 8B models |
| Batch Size | 64 | Memory-efficient for single GPU |
| Mini-Batch Size | 8 | PPO gradient accumulation |
| PPO Epochs | 4 | Standard trl default |
| KL Coefficient | 0.05 | Prevent divergence from reference |
| Clip Range | 0.2 | Standard PPO |
| Value Clip Range | 0.2 | Standard PPO |
| Total Steps | 1000 | Sufficient for convergence signal |

**Framework:** trl.PPOTrainer (HuggingFace TRL library)

---

## 6. Success Criteria

### Primary (Gate: MUST_WORK)
1. **Convergence:** Both reward components show positive trend over 1000 steps
2. **No Divergence:** KL divergence from reference stays < 5.0
3. **Stability:** No NaN/Inf in loss, no training collapse

### Secondary (Informative)
1. **Reward Trajectory:** Plot shows monotonic improvement
2. **No Reward Hacking:** Eval performance correlates with training rewards
3. **Both Signals Improve:** Neither R_helpfulness nor R_IFEval degrades

---

## 7. Evaluation Protocol

### 7.1 Training Metrics (logged every 10 steps)
- `reward/mean`: Combined reward average
- `reward/helpfulness`: R_AlpacaEval component
- `reward/controllability`: R_IFEval component
- `objective/kl`: KL divergence from reference
- `ppo/policy_loss`: PPO policy gradient loss
- `ppo/value_loss`: Value function loss

### 7.2 Checkpoint Evaluation (every 250 steps)
- IFEval strict accuracy on held-out 30%
- Sample response quality (manual inspection of 10 examples)

### 7.3 Final Evaluation (step 1000)
- Full IFEval test split evaluation
- AlpacaEval sample (100 prompts) for helpfulness spot-check
- Reward hacking detection: Compare training reward vs eval metrics

---

## 8. Failure Response

**IF PPO diverges (KL > 10.0 or NaN losses):**
- EXPLORE: Reduce learning rate to 5e-6
- EXPLORE: Increase KL coefficient to 0.1
- PIVOT: Try DPO/IPO as alternative optimization

**IF Reward hacking detected (high training reward, low eval):**
- EXPLORE: Add reward model ensemble
- EXPLORE: Reduce reward model influence (smaller beta)

---

## 9. Implementation Files

```
h-m1/code/
├── config.py           # Training hyperparameters
├── rewards.py          # CombinedRewardModel wrapper
├── train_ppo.py        # trl.PPOTrainer training loop
├── evaluate.py         # Checkpoint evaluation
└── visualize.py        # Reward trajectory plots
```

---

## 10. Resource Requirements

| Resource | Estimate |
|----------|----------|
| GPU | 1× A100 80GB (or 2× A6000 48GB) |
| Training Time | ~4-6 hours for 1000 steps |
| Disk | ~50GB (model checkpoints + logs) |

---

## 11. Archon KB & Exa Research Summary

**MCP Status:** Tools not available in current session

**[INFERRED] Pattern 1:** Multi-objective RLHF
- Weighted sum of rewards is mathematically valid for Pareto optimization
- KL penalty prevents catastrophic divergence from reference policy

**[INFERRED] Pattern 2:** TRL PPOTrainer
- Standard interface: `reward_model` callable returns scalar per sequence
- Custom reward functions supported via wrapper class

**[INFERRED] Pattern 3:** Reward Hacking Mitigation
- Compare training rewards against held-out evaluation metrics
- Ensemble reward models reduce exploitation risk

---

## 12. Baseline Comparison (for Phase 5)

| Method | Configuration | Expected Behavior |
|--------|---------------|-------------------|
| B1-SFT | No RL training | No reward signal |
| B2-Helpfulness-Only | α=1.0, β=0.0 | Optimizes AlpacaEval only |
| T1-Combined | α=0.5, β=0.5 | This experiment |

---

## 13. Gate Decision Matrix

| Outcome | R_helpfulness | R_IFEval | KL | Decision |
|---------|---------------|----------|-----|----------|
| PASS | ↑ | ↑ | < 5.0 | Proceed to H-M2 |
| PARTIAL | ↑ | → | < 5.0 | Tune β, retry |
| FAIL | ↓ or NaN | Any | > 10.0 | PIVOT to DPO |

---

**Next Step:** Phase 3 Implementation Planning (PRD + Architecture + Logic + Config)
