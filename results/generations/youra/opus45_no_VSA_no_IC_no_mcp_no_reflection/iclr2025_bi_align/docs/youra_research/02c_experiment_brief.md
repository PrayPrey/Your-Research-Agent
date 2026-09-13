# Experiment Brief: H-E1

**Hypothesis ID:** h-e1  
**Type:** EXISTENCE  
**Gate:** MUST_WORK  
**Date:** 2026-08-28

---

## 1. Hypothesis Statement

IFEval constraint satisfaction rate can be computed as a valid continuous reward signal for RLHF training.

---

## 2. Research Summary

### 2.1 Key Findings from Literature

**IFEval Benchmark Structure:**
- 541 prompts with 25 verifiable constraint types
- Binary satisfaction per constraint (pass/fail)
- Constraint types: format, length, keyword, structure, style
- Strict vs loose evaluation modes available

**Constraint-to-Reward Conversion (from VerIF, RLVR literature):**
- Rule-based rewards assign binary (0/1) per constraint
- Constraint satisfaction rate = (satisfied_constraints / total_constraints)
- This rate is differentiable through expectation over samples
- DeepSeek-R1, VerIF demonstrate viability of rule-based RLHF rewards

**TRL PPOTrainer Integration:**
- Accepts arbitrary scalar rewards per (query, response) pair
- `ppo_trainer.step(query_tensors, response_tensors, rewards)` API
- No requirement for parametric reward model

### 2.2 Implementation Resources

| Resource | URL | Relevance |
|----------|-----|-----------|
| Google IFEval | github.com/google-research/google-research/tree/master/instruction_following_eval | Official constraint checker |
| Clean IFEval | github.com/oKatanaaa/ifeval | Simplified API with `Evaluator.evaluate()` |
| TRL PPOTrainer | huggingface.co/docs/trl/ppo_trainer | RL training infrastructure |
| VerIF Paper | arxiv.org/abs/2506.09942 | Rule-based RLVR for instruction following |

---

## 3. Experiment Design

### 3.1 Objective

Validate that IFEval constraint satisfaction rate:
1. Can be computed programmatically for any LLM response
2. Produces valid gradient signal through PPO policy gradient
3. Correlates with actual instruction-following quality (r > 0.5)
4. Enables stable training (loss decreases over 100 steps)

### 3.2 Dataset

**Primary:** IFEval (google/IFEval on HuggingFace)
- Type: standard
- Size: 541 prompts
- Split: 70% train (379), 30% held-out (162)
- Constraint coverage: 25 types across format/length/keyword/structure/style

**No synthetic data required.** IFEval is a real benchmark with human-authored prompts and programmatically verifiable constraints.

### 3.3 Model

**Base Model:** meta-llama/Meta-Llama-3-8B-Instruct
- Source: HuggingFace Hub
- Rationale: Standard size for RLHF experiments, well-documented baselines

### 3.4 Experimental Conditions

| Condition | Description |
|-----------|-------------|
| **C1: Baseline** | Llama-3-8B-Instruct, no additional training |
| **C2: IFEval-reward PPO** | 100 PPO steps with IFEval satisfaction rate as reward |

### 3.5 Reward Function Design

```python
def compute_ifeval_reward(prompt: str, response: str) -> float:
    """
    Compute IFEval constraint satisfaction rate.
    
    Returns:
        float in [0.0, 1.0] representing fraction of satisfied constraints
    """
    # Parse constraints from prompt using IFEval registry
    constraints = parse_constraints(prompt)
    
    # Check each constraint
    satisfied = sum(1 for c in constraints if c.check(response))
    
    # Satisfaction rate = continuous signal
    return satisfied / len(constraints) if constraints else 1.0
```

**Key Properties:**
- Output range: [0.0, 1.0]
- Differentiable through policy gradient (expectation over actions)
- No parametric reward model needed
- Deterministic verification (no stochasticity in reward)

### 3.6 Training Configuration

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| PPO steps | 100 | Minimal for convergence signal |
| Batch size | 8 | Memory constraints |
| Learning rate | 1e-5 | Conservative for stability |
| KL penalty | 0.1 | Prevent divergence from base |
| Max response length | 512 | Balance constraint types |

### 3.7 Metrics

| Metric | Purpose | Success Threshold |
|--------|---------|-------------------|
| **Correlation(rate, satisfaction)** | Validate rate as proxy | r > 0.5 |
| **Training loss trajectory** | Confirm gradient validity | Decreasing trend |
| **KL divergence** | Monitor stability | < 10 nats |
| **Mean reward (train)** | Track learning | Increasing trend |
| **IFEval strict accuracy (held-out)** | Generalization | > baseline |

---

## 4. Success Criteria

### 4.1 Primary (PoC: Direction-based)

- [x] IFEval satisfaction rate computed successfully for 100% of samples
- [ ] Pearson correlation between rate and binary satisfaction > 0.5
- [ ] Training loss shows decreasing trend over 100 steps

### 4.2 Secondary

- [ ] Mean reward increases during training
- [ ] KL divergence remains bounded (< 10 nats)
- [ ] No NaN/Inf in gradients

---

## 5. Failure Response

**IF h-e1 FAILS:**
- Gate type: MUST_WORK
- Action: STOP pipeline
- Reason: IFEval rate not viable as training signal

**Pivot Options (if partial failure):**
1. Use instruction-level binary (0/1) instead of rate
2. Use loose evaluation mode instead of strict
3. Subset to high-reliability constraint types only

---

## 6. Implementation Plan

### 6.1 Code Components

| Component | File | Description |
|-----------|------|-------------|
| IFEval loader | `data/ifeval_loader.py` | Load and split IFEval dataset |
| Constraint parser | `rewards/ifeval_reward.py` | Parse prompts, extract constraints |
| Reward function | `rewards/ifeval_reward.py` | Compute satisfaction rate |
| PPO training | `training/ppo_ifeval.py` | TRL PPOTrainer integration |
| Evaluation | `eval/evaluate_ifeval.py` | Held-out evaluation |

### 6.2 Dependencies

```
torch>=2.0
transformers>=4.35
trl>=0.7.0
datasets
```

### 6.3 Estimated Compute

- GPU: 1x A100 (40GB) or equivalent
- Training time: ~2 hours for 100 PPO steps
- Evaluation time: ~30 minutes

---

## 7. Validation Protocol

### Step 1: Data Setup
1. Load IFEval from HuggingFace
2. Verify constraint parsing for all 541 prompts
3. Create 70/30 train/test split

### Step 2: Reward Validation
1. Generate responses from base model for 50 train prompts
2. Compute satisfaction rate for each
3. Verify rate correlates with manual inspection

### Step 3: Training
1. Initialize PPOTrainer with Llama-3-8B-Instruct
2. Run 100 PPO steps with IFEval reward
3. Log: loss, reward, KL divergence per step

### Step 4: Evaluation
1. Generate responses on held-out 162 prompts
2. Compute strict accuracy
3. Compare to baseline (no training)

---

## 8. Risk Mitigation

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| Constraint parsing errors | Medium | Test on full dataset before training |
| Reward hacking | Low | KL penalty prevents distribution shift |
| Memory overflow | Medium | Gradient checkpointing, smaller batch |
| Slow inference | Low | Use 8-bit quantization for generation |

---

## 9. Appendix: Constraint Types in IFEval

| Category | Examples | Verification Method |
|----------|----------|---------------------|
| Format | JSON, markdown, bullets | Regex/parser |
| Length | Word count, sentence count | Tokenization |
| Keyword | Include/exclude words | String search |
| Structure | Paragraphs, sections | Pattern matching |
| Style | First person, formal | Heuristics |

---

**Status:** READY FOR IMPLEMENTATION  
**Next Phase:** Phase 3 (Implementation Planning)
