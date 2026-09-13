# H-E1 Context: Semantic-Structural UQ Advantage Exists at Both Scales

**Generated:** 2026-05-20 (JIT from 02b_verification_plan.md)
**Hypothesis ID:** h-e1
**Type:** EXISTENCE
**Gate:** MUST_WORK
**Prerequisites:** None (Foundation hypothesis)

---

## Hypothesis Statement

Under Llama-3 base checkpoints on TriviaQA and NaturalQuestions with identical splits and evaluation harness, SE and KLE show statistically higher AUROC for correctness prediction than token-probability at both 8B and 70B scales — confirming the semantic-structural UQ advantage as a prerequisite for scale-dependent reorganization.

## Rationale

This is the foundation hypothesis. The method×scale interaction (H-M3) is only meaningful if the semantic-structural UQ advantage exists at both scales. Establishing existence first ensures later mechanism tests are built on confirmed ground. Semantic equivalence class aggregation captures uncertainty signals that vocabulary distributions cannot.

## Variables

- **Independent:** UQ method paradigm (SE, KLE vs token-probability)
- **Dependent:** AUROC for correctness prediction at each scale
- **Controlled:** Model scale (both 8B and 70B), dataset splits, evaluation harness, N=10 sampling

## Experimental Setup (from Phase 2A)

### Datasets

| Dataset | Type | Source | Splits | Size |
|---------|------|--------|--------|------|
| TriviaQA rc.nocontext | standard | HuggingFace `mandarjoshi/trivia_qa` rc.nocontext | test | 17,944 questions |
| NaturalQuestions open-domain | standard | HuggingFace `google-research-datasets/natural_questions` | test (open) | 3,610 questions |
| TruthfulQA mc1_targets | standard | HuggingFace `truthful_qa` mc1_targets | validation | 817 questions (scope boundary P4) |

**Dataset Fit:** TriviaQA and NQ are factual retrieval benchmarks with ground-truth correctness labels and standard splits; directly targeted by the EGSH scaling hypothesis. Full standard test splits provide 17,944 + 3,610 = 21,554 total evaluation queries.

### Models

| Model | HuggingFace ID | Role |
|-------|---------------|------|
| Llama-3-8B-Base | meta-llama/Meta-Llama-3-8B | Small-scale baseline |
| Llama-3-70B-Base | meta-llama/Meta-Llama-3-70B | Large-scale primary |
| Llama-3-70B-Instruct | meta-llama/Meta-Llama-3-70B-Instruct | Within-scale control |

**Model Fit:** Same model family with controlled scale variation; base checkpoints eliminate RLHF confounds.

### UQ Methods Evaluated

1. Token-probability (max softmax / negative log-prob) — BASELINE
2. SelfCheckGPT-BERTScore (Manakul et al. 2023)
3. SelfCheckGPT-NLI (Manakul et al. 2023)
4. Semantic Entropy / SE (Farquhar et al. 2024) — PRIMARY
5. KLE / Kernel Language Entropy (Nikitin et al. 2024) — PRIMARY
6. Semantic Entropy Probes / SEPs (Kossen et al. 2024)

## Verification Protocol

1. Generate greedy decode + N=10 samples per query for Llama-3-8B-Base and 70B-Base via UQLM
2. Apply all 6 UQ methods through unified UQLM harness
3. Compute AUROC per method per model on full standard test splits; bootstrap CI (1000 resamples)
4. Test SE > token-prob and KLE > token-prob at each scale via paired bootstrap (one-sided, α=0.05)
5. Confirm advantage holds on both TriviaQA and NQ independently

## Success Criteria (PoC)

- **Primary:** SE AUROC > token-prob AUROC at both 8B and 70B, with 95% CI excluding zero, on both TriviaQA and NQ
- **Secondary:** KLE AUROC > token-prob AUROC at both scales

## Gate Conditions

- **Gate Type:** MUST_WORK
- **Pass:** SE & KLE AUROC > token-prob at both 8B & 70B, CI excludes zero → proceed to H-M1
- **Fail at 8B only:** PIVOT — re-examine SE implementation; check UQLM normalization
- **Fail at both scales:** ABANDON H-M* — semantic advantage does not exist; reassess EGSH

## Baseline Methods (Expected Performance from Literature)

| Method | Expected AUROC | Dataset | Source |
|--------|---------------|---------|--------|
| Semantic Entropy | ~0.72–0.79 | TriviaQA, NQ | Farquhar et al. 2024 |
| Token-probability | ~0.67 | TriviaQA (Llama-2-70B) | Literature |
| KLE | Competitive with SE | TriviaQA, NQ | Nikitin et al. 2024 |

## Phase 2B Risk Context

| Risk | Severity | Mitigation |
|------|----------|------------|
| R4: KLE implementation unavailability | Medium | Verify LM-Polygraph Week 0; SE-only fallback |
| R5: N=10 sample instability at 70B | Medium | N=5 stability pilot; bootstrap CI monitoring |

## Dependencies

- **Depends on:** None (foundation hypothesis)
- **Enables:** H-M1 (upon MUST_WORK gate pass)
