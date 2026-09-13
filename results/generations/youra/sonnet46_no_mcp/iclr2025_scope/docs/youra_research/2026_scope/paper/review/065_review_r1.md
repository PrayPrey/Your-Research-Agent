# Adversarial Review — Round 1
# Paper: "Eviction-Aware LoRA: Training LoRA Adapters Under KV Cache Budget Constraints"
# Review Date: 2026-05-04
# Reviewer: Three-Persona Adversary Agent (Accuracy Checker / Bored Reviewer / Skeptical Expert)

---

## 1. Ground Truth Summary Table

| Metric | Ground Truth Source | Value in Paper | Match? |
|--------|---------------------|----------------|--------|
| H-E1 min cosine similarity | h-e1/04_validation.md **metrics table** | −0.578 | MISMATCH (table says −0.0838) |
| H-E1 min cosine similarity | h-e1/04_validation.md **gate section + narrative** | −0.578 | MATCH |
| H-E1 mean cosine similarity | h-e1/04_validation.md **metrics table** | 0.053 | MISMATCH (table says −0.0079) |
| H-E1 mean cosine similarity | h-e1/04_validation.md **mechanism narrative** | 0.053 | MATCH |
| H-E1 layers below threshold | 065_ground_truth.yaml | 24/24 | MATCH |
| H-E1 gate result | verification_state / 065_ground_truth.yaml | PASS | MATCH |
| H-M1 layers significant | h-m1/04_validation.md | 8/12 | MATCH |
| H-M1 fraction significant | h-m1/04_validation.md | 0.667 | MATCH |
| H-M1 entropy mean diff | h-m1/04_validation.md | −0.0199 nats | MATCH |
| H-M1 HH concentration diff | h-m1/04_validation.md | +0.0008 | MATCH |
| H-M1 evaluation samples | h-m1/04_validation.md | 5 (synthetic) | MATCH (disclosed in Section 4.2) |
| H-M2 gate result | 065_ground_truth.yaml | LIMITATION_RECORDED | MATCH (Section 5.3) |
| H-M3 status | 065_ground_truth.yaml | NOT_STARTED | MATCH (Section 6.2 L1) |
| Phase 5 baseline | 065_ground_truth.yaml | SKIPPED | MATCH (no superiority claim over SnapKV) |
| Training steps (proxy) | 065_ground_truth.yaml | 30 | MATCH |
| Training samples (proxy) | 065_ground_truth.yaml | 200 | MATCH |
| KV budget ratio | 065_ground_truth.yaml | 0.50 | MATCH |
| Proxy model | 065_ground_truth.yaml | GPT-2 (117M) | MATCH |
| LoRA rank (proxy) | 065_ground_truth.yaml | 8 | MATCH |
| LoRA alpha | 065_ground_truth.yaml | 32 | NOTE: h-e1/04_validation.md shows alpha=16 in "Optimal Hyperparameters" section; paper says 32 |

**Critical Discrepancy Detail — H-E1 Cosine Similarity:**
- `h-e1/04_validation.md` Metrics Table (lines 92–93): min = −0.0838, mean = −0.0079
- `h-e1/04_validation.md` Gate Section (line 121): "minimum of -0.5781"
- `h-e1/04_validation.md` Mechanism Narrative (line 133): "Mean cosine similarity ≈ 0.05"
- `065_ground_truth.yaml` (lines 18–19): min = −0.5781, mean = 0.053
- The per-layer table (lines 99–108 of h-e1/04_validation.md) shows layer h.6.lora_B = −0.5781 and layer h.1.lora_B = 0.3996, layer h.0.lora_A = 0.0135 — these are inconsistent with either set of summary statistics.

**Interpretation:** The Metrics Table (min=−0.0838, mean=−0.0079) appears to contain an internal reporting error in the validation document. The per-layer table and gate narrative consistently report min=−0.5781. The paper uses the narrative/gate values (min=−0.578, mean=0.053). However, the mean of 0.053 is inconsistent with the per-layer examples shown (which include values like 0.3996, 0.4694, −0.2725, 0.0135, 0.0156), and the summary table in the validation document showing mean=−0.0079 vs the narrative claiming mean=0.053 represents a genuine internal inconsistency in the source documents that the paper cannot resolve by inspection alone.

**Alpha discrepancy:** The paper reports LoRA alpha=32 (Section 3.3 Table), while h-e1/04_validation.md "Optimal Hyperparameters" section lists alpha=16. The 065_ground_truth.yaml confirms alpha=32. This suggests the optimal hyperparameters section in the validation doc reflects a different configuration than what was run.

---

## 2. Executive Summary

| Persona | FATAL | MAJOR | Human Review Notes |
|---------|-------|-------|-------------------|
| Accuracy Checker | 1 | 2 | 3 |
| Bored Reviewer | 0 | 2 | 4 |
| Skeptical Expert | 0 | 3 | 3 |
| **TOTAL** | **1** | **7** | **10** |

**Overall Recommendation: REVISE**

The paper is honest about its scope as a mechanistic study and correctly avoids claiming the accuracy result (P1). However, one FATAL issue (unresolvable cosine similarity discrepancy between validation document sections) and seven MAJOR issues (weak sample size, novelty unverifiable, production-ready overclaim, proxy validity gap, dropout analogy precision, baseline adequacy, middle-layer overclaim) require resolution before submission.

---

## 3. PERSONA 1 — ACCURACY CHECKER

**Role:** Line-by-line numbers verification against ground truth artifacts.

### FINDING AC-1 [FATAL]: Cosine Similarity Source Document Internal Inconsistency

**Claim in paper (Abstract, Section 5.1):** min cosine sim = −0.578, mean = 0.053

**Evidence of discrepancy:**
- `h-e1/04_validation.md` Metrics Table: min = −0.0838, mean = −0.0079
- `h-e1/04_validation.md` Gate Section narrative: min = −0.578
- `h-e1/04_validation.md` Mechanism Verification narrative: mean ≈ 0.053
- `065_ground_truth.yaml`: min = −0.5781, mean = 0.053

**Severity: FATAL**

**Explanation:** The paper's numbers (min=−0.578, mean=0.053) are taken from the gate/narrative sections of the validation document, NOT from the metrics table in the same document. The metrics table (which is the structured experimental output) shows materially different values: min=−0.0838 (vs −0.578) and mean=−0.0079 (vs 0.053). This is an 85% discrepancy in the minimum and a sign flip in the mean.

There are two possible explanations:
1. The metrics table captured an intermediate run result and the gate/narrative reflect the final corrected run.
2. The narrative section contains typographic errors that propagated into the paper.

Either way, the paper presents numbers from one section of the validation document that contradict another section of the same document. Until the raw `experiment_results.json` is directly verified, neither set of numbers can be certified as correct. This is not merely a rounding discrepancy — the values differ by an order of magnitude for the minimum, and by sign for the mean.

**Required fix:** Audit `h-e1/code/outputs/results.csv` and `h-e1/experiment_results.json` directly. Report the exact values from the output files. If the table (−0.0838, −0.0079) is correct, the paper's main quantitative claims are significantly overstated. If the narrative (−0.578, 0.053) is correct, the metrics table in the validation document contains a reporting error that must be corrected.

**Impact on paper:** If the true values are min=−0.0838 and mean=−0.0079, the claim "near-orthogonal divergence" is weakened (mean of −0.0079 is still below 0.95 threshold and gate still passes, but the "striking" narrative in Section 5.1 — comparing to same-task adapters at >0.95 — would be undermined if mean is negative near zero rather than positive 0.053).

---

### FINDING AC-2 [MAJOR]: LoRA Alpha Hyperparameter Inconsistency

**Claim in paper (Section 3.3 Table):** LoRA alpha = 32

**Evidence of inconsistency:**
- `h-e1/04_validation.md` "Optimal Hyperparameters" appendix: alpha = 16
- `065_ground_truth.yaml`: alpha = 32

**Severity: MAJOR**

The "Optimal Hyperparameters" section of the H-E1 validation report (the section recommending hyperparameters for dependent hypotheses) specifies alpha=16. The paper reports alpha=32. The ground truth file aligns with the paper (alpha=32). This suggests the experiments were run with alpha=32 but the "Optimal Hyperparameters" recommendation section contains a different value.

While this is likely a documentation error rather than an experimental error, a reviewer who audits both documents will flag it as evidence of sloppy record-keeping. More importantly: if the actual training run used alpha=16 (matching the validation doc's recommendation), the LoRA scaling factor differs from what the paper reports, potentially affecting the cosine similarity magnitude.

**Required fix:** Verify which alpha value was used in the actual training run from the config files or training logs. Ensure paper hyperparameter table matches the actual run.

---

### FINDING AC-3 [MAJOR]: H-M1 Five-Sample Limitation — Disclosure Adequacy

**Claim in paper (Section 5.2 Table):** "8/12 transformer layers showing significant entropy and heavy-hitter concentration divergence (p < 0.05, paired t-test)"

**Ground truth:** 5 synthetic samples, NOT real LongBench samples.

**Severity: MAJOR**

The 5-sample limitation is disclosed in Section 4.2 ("Evaluation Data (H-M1): Five synthetic multi-sentence samples for attention pattern comparison") and in Section 6.2 L3. However:

1. The Abstract states "restructures attention patterns in 8 of 12 transformer layers (p < 0.05)" without any qualification about sample size. A reader encountering this claim in the abstract would assume a reasonable statistical sample, not n=5.
2. Paired t-test with n=5 has only 4 degrees of freedom, giving the test very low power and making it extremely sensitive to individual sample artifacts. Any single outlier can dominate the t-statistic.
3. The abstract and contribution #3 (Section 1) present this as a confirmed finding, not as a preliminary observation.
4. Section 5.2's table presents the result with identical formatting weight as H-E1 (which at least has 24 data points — one per layer).

**Required fix:** The abstract must include a parenthetical qualifying the 5-sample basis for the attention restructuring claim: e.g., "restructures attention patterns in 8 of 12 transformer layers (p < 0.05, n=5 synthetic samples, proxy model)". The contribution statement in Section 1 should similarly qualify.

---

### FINDING AC-4 [MINOR — human_review_notes]: Paper Correctly Does NOT Claim P1

The paper does not assert the ≥2% LongBench accuracy improvement anywhere in the main text or abstract. Section 5.4 summary table explicitly marks this "NOT STARTED." Section 6.2 L1 marks it "Critical." The conclusion correctly states accuracy evaluation as future work. This is accurate and appropriately handled.

---

### FINDING AC-5 [MINOR — human_review_notes]: All Limitations L1–L6 Are Disclosed

All six limitations are present in Section 6.2 with appropriate severity labels (Critical/Significant/Moderate). The H2O+SDPA incompatibility is additionally given its own subsection (6.3). The CUDA crash context of H-M2 is documented in Section 5.3. This is accurate.

---

### FINDING AC-6 [MINOR — human_review_notes]: H-M2 Framing is Accurate

The paper frames H-M2 as "Proxy Scope Limitation" rather than a hypothesis failure. Ground truth confirms gate_result="LIMITATION_RECORDED" (not FAIL). Section 5.3 accurately describes the zero-score LongBench context window issue and the CUDA crash. Infrastructure being "production-ready" is substantiated by 63 completed sequential evaluations.

---

## 4. PERSONA 2 — BORED REVIEWER

**Role:** Busy NeurIPS reviewer, 5 papers in queue today. Reading for compelling narrative, clarity, and persuasiveness.

### FINDING BR-1 [MAJOR]: Abstract Hook Is Strong But Sample-Size Omission Risks Credibility Loss

**Assessment: CONDITIONAL PASS**

The abstract opens with a concrete, specific problem statement ("LoRA adapters for long-context LLMs are trained with full KV cache access but deployed under eviction policies that discard 50–75% of that cache"). This is more specific than the generic "X is important" opener that plagues most PEFT papers. The numbers (0.053 cosine similarity, 8/12 layers) are concrete.

**However:** A reviewer who knows paired t-tests will immediately notice "p < 0.05" in the abstract and look for sample size. Finding n=5 buried in Section 4.2 will trigger irritation. The abstract creates an expectation of real statistical power that the body does not deliver. This is a credibility trap — the abstract feels stronger than the evidence supports.

**Required fix:** Add "(n=5, proxy model)" qualification to the attention restructuring claim in the abstract, or reframe as "preliminary mechanistic evidence."

---

### FINDING BR-2 [MAJOR]: The "Production-Ready Infrastructure" Contribution Is a Readability Liability

The fourth contribution in Section 1 claims "Production-Ready Infrastructure" as a contribution on par with the mechanistic findings. For a bored reviewer at a ML theory conference, this reads as padding. Infrastructure that was never tested on the target models is not "production-ready" by any standard conference definition. The word "production" in an academic paper context implies deployed, scaled, and reliability-tested — none of which is true here.

Furthermore, the paper itself documents (Section 5.3) that the eviction-aware adapter crashed with a CUDA gather kernel error during H-M2 evaluation. Calling infrastructure "production-ready" while disclosing a CUDA crash on the same page is internally inconsistent.

**Required fix:** Either remove "production-ready" and replace with "validated for deployment on target models" or move this contribution to a footnote. Alternatively, rename it "Full-Scale Evaluation Infrastructure" and be explicit that it is ready for use, not ready for production. More critically: the CUDA crash (H2O+SDPA incompatibility) should be prominently flagged as an obstacle to production readiness, not quietly disclosed in Section 6.3 as a "technical finding."

---

### FINDING BR-3 [human_review_notes]: The Paper Retains Attention Past Page 2

The three-level problem framing (surface → deeper → gap) in the introduction is effective. The analogy to dropout (Section 2.3, 3.4) gives the method a memorable conceptual anchor. The paper does not become boring until Section 5.3 (H-M2), where four flat-zero figures are described — but these are appropriately brief and the proxy limitation explanation is honest.

---

### FINDING BR-4 [human_review_notes]: Figure 1 Reference Is Self-Explanatory in Context

Section 5.1 references "Figure 1 shows per-layer cosine similarity" with a file path in parentheses. For a print/PDF reviewer the figure caption is clear (dashed line at 0.95, all 24 layers below). The figure is adequately described without requiring the actual image. No issue.

---

### FINDING BR-5 [human_review_notes]: "Mechanistic Study" Framing Is Communicated Clearly

The paper repeatedly and consistently labels itself a mechanistic study — in the abstract, in Section 4.1 ("RQ1 and RQ2 test mechanistic preconditions"), in Sections 6.2 and 7. A bored reviewer will understand the scope. The framing is honest. However, the contribution list (Section 1) leads with "Conceptual Contribution" and ends with "Production-Ready Infrastructure" — neither of which lands as a mechanistic finding. Reordering to lead with the empirical mechanistic results (H-E1, H-M1) and demote the conceptual/infrastructure contributions would improve persuasiveness.

---

### FINDING BR-6 [human_review_notes]: Introduction Hook Avoids "X Is Important" Cliche

The introduction opens with a concrete deployment scenario, not an importance claim. The hook ("Large language models are routinely fine-tuned on sequences with full KV cache access, then deployed under aggressive eviction policies") is factual and specific. The follow-up ("An adapter trained on LongAlpaca-12k with unrestricted attention, then deployed with H2O eviction at r=50%, is evaluated on a token distribution it never encountered during training") is concrete. No cliche detected.

---

### FINDING BR-7 [human_review_notes]: Persuasiveness Assessment

The paper is persuasive about WHY mechanistic results matter (the dropout analogy, the middle-layer specificity argument, the two-interpretation framing in Section 6.1 — including the unfavorable Interpretation B — are honest and sophisticated). The failure to provide full accuracy evaluation is not hidden. A reviewer who reads this as a workshop or position paper would find it compelling. Whether it meets full NeurIPS/ICML standards for empirical rigor is a separate question.

**Persuasiveness verdict: PASS** — with the caveat that the n=5 disclosure in the abstract would prevent a false-positive credibility score at first read.

---

## 5. PERSONA 3 — SKEPTICAL EXPERT

**Role:** Expert in PEFT and KV cache methods. Read all 14 citations. Looking for overclaims, missing baselines, and faulty analogies.

### FINDING SE-1 [MAJOR]: "First Method" Novelty Claim Is Unverifiable

**Claim (Section 1):** "To our knowledge, this is the first systematic study of LoRA adapter training under simulated KV cache eviction constraints."

**Ground truth note:** `065_ground_truth.yaml` acknowledges this is "Knowledge-grounded; no MCP-verified prior work search."

**Severity: MAJOR**

The hedging phrase "to our knowledge" is appropriate but insufficient at a top-tier conference. The related work section covers H2O, SnapKV, StreamingLLM, LoRA, AdaLoRA, DoRA, and dropout — a reasonable set. However:

1. The paper does not search or cite any work on quantization-aware fine-tuning (QAT), which is the closest structural analog (training-inference distribution mismatch, adapter trained under inference-time constraint). LoRA-QA and related methods were explicitly mentioned as a generalization in Section 6.4 but not cited.
2. LongLoRA [Chen et al., 2023] is cited in the references but never discussed in Section 2 — it directly addresses efficient fine-tuning for long-context models and its relationship to eviction-aware training is unexplained.
3. There is no explicit search for "KV cache + fine-tuning" in the arXiv literature. A knowledgeable reviewer would flag SnapKV-aware fine-tuning, KVSharer, or CacheBlend as potential prior work.

**Required fix:** Add a sentence explicitly addressing why LongLoRA does not constitute prior work on the same problem. Add discussion of QAT as a structural analog to ground the "first systematic study" claim. If MCP literature search was unavailable, the hedge should be strengthened: "We are unaware of prior work; a systematic literature survey is warranted."

---

### FINDING SE-2 [MAJOR]: Baseline Adequacy — Only Sequential Baseline Used

**Claim (Section 4.3):** "Sequential Baseline: Standard LoRA fine-tuning without eviction masks during training; H2O eviction applied at inference."

**Ground truth:** Phase 5 baseline comparison was SKIPPED (skip_baseline_comparison=true). No comparison to SnapKV-aware training, randomized eviction mask training, or any alternative.

**Severity: MAJOR**

The paper compares eviction-aware LoRA only to the sequential baseline. This is appropriate as an existence proof (the paper is a mechanistic study), but three gaps remain:

1. **No randomized mask ablation:** The paper claims H2O mask specificity is important (Section 3.2.1 — heavy-hitter selection, not random token removal). A randomized mask baseline (same budget ratio, random token removal rather than H2O policy) would verify that the near-orthogonal divergence is specific to H2O's policy-driven mask rather than any token removal. Without this ablation, the near-orthogonal divergence could be an artifact of training under ANY mask.
2. **No SnapKV comparison:** Phase 5 was skipped. The paper does not claim superiority over SnapKV, which is correct — but an expert reviewer will ask why H2O was chosen over SnapKV as the training-time mask given SnapKV's demonstrably better inference-time accuracy.
3. **Infrastructure contribution not demonstrated:** The BudgetSweepEvaluator ran 63 evaluations but all scored 0.0. "Production-ready infrastructure" that has only produced null results is not a demonstrated contribution.

**Required fix:** Add a random-mask ablation baseline (even at proxy scale) or explicitly flag its absence as a limitation. Provide justification for H2O selection over SnapKV as the training mask policy. Consider removing or downgrading the infrastructure contribution claim given that no non-trivial evaluation results exist from it.

---

### FINDING SE-3 [MAJOR]: "Production-Ready" Claim Contradicted by H2O+SDPA Incompatibility

**Claim (Section 1 Contribution #4, Section 3.5):** "Production-ready BudgetSweepEvaluator and SpearmanAnalyzer infrastructure"

**Ground truth:** H-M2 evaluation crashed with "CUDA gather kernel error (H2O+SDPA incompatibility)" for the eviction-aware adapter. Fix requires `attn_implementation='eager'` (15–30% overhead). This is disclosed in Section 5.3 and Section 6.3.

**Severity: MAJOR**

An infrastructure that requires a non-default, performance-degrading configuration setting (`attn_implementation='eager'`) to avoid crashing is not "production-ready" by any standard definition used in the systems/ML deployment community. The crash occurred during H-M2 evaluation — meaning the BudgetSweepEvaluator has never completed a full sweep for the eviction-aware adapter. The 63 completed evaluations are entirely from the sequential baseline.

The paper frames this well in Section 6.3 as a technical finding and discloses it accurately. But the juxtaposition of "production-ready" in the abstract/introduction with "CUDA crash" in Section 5.3 is a credibility problem for expert readers.

**Required fix:** Replace "production-ready" in the abstract and contribution list with more precise language: "validated infrastructure with documented H2O+SDPA incompatibility requiring `attn_implementation='eager'`." Or move this to a technical contribution rather than leading with it as a peer-reviewed finding.

---

### FINDING SE-4 [human_review_notes]: Dropout Analogy Is Appropriate But Incomplete

The dropout analogy (Sections 2.3, 3.4) is mechanically correct: both methods train under structured absence. The paper correctly identifies three key differences (granularity, determinism, target). However, the analogy omits a fourth critical difference: H2O masks are input-dependent (the heavy-hitter set changes per input), while dropout masks are input-independent random draws. This distinction matters because input-dependent masking creates a more complex optimization landscape — the adapter must generalize across all possible H2O mask configurations, not a fixed distribution. The paper would benefit from acknowledging this complication.

---

### FINDING SE-5 [human_review_notes]: AdaLoRA Citation Is Accurate But the Connection Is Overstated

Section 2.2 states: "Our finding that eviction-aware training produces near-orthogonal weight divergence is consistent with AdaLoRA's observation that concentrated gradient signals drive more efficient adapter specialization." AdaLoRA [Zhang et al., 2023] does not characterize gradient concentration as driving orthogonal divergence — it allocates rank budget by SVD importance scores. The claimed consistency is a stretch. The sentence should be weakened: "AdaLoRA suggests gradient concentration may drive more structured adapter updates; our near-orthogonal divergence is consistent with this intuition, though not a direct validation."

---

### FINDING SE-6 [human_review_notes]: Middle-Layer Specificity Claim Needs Qualification

Section 5.2 and 6.1 attribute the middle-layer concentration (layers 4–11) to prior work [Clark et al., 2019] showing middle layers carry long-range dependencies. Two caveats:
1. Clark et al. analyzed BERT, not GPT-2 or decoder-only models. The mapping of "middle layers carry long-range dependencies" from encoder-only BERT to decoder-only GPT-2 is asserted, not demonstrated.
2. With n=5 samples, "concentrated in layers 4–11" simply means those 8 layers passed p<0.05 by paired t-test — which with 4 degrees of freedom and synthetic samples is consistent with chance variation in which layers happen to show the strongest artifact.

The paper should qualify this: "Consistent with Clark et al.'s findings on encoder models, we observe..." and note that replication on decoder models at scale is needed.

---

### FINDING SE-7 [human_review_notes]: Proxy-to-Target Validity Argument Is Honest But Unconvincing

Section 6.2 L3 acknowledges the proxy validity gap. Section 4.2 states "proxy validity boundary documented as Limitation L3." The paper's argument for why GPT-2 results support claims about 7B models is implicit (gradient mechanism is architecture-agnostic) rather than explicit. A skeptical expert will note that GPT-2 uses fused c_attn (QKV in one Conv1D), 12 heads, 768-dim, while LLaMA-2-7B uses separate Q/K/V projections, 32 heads, 4096-dim, GQA, RoPE embeddings. The H2O mask injection implementation must differ (c_attn hook vs q_proj/v_proj hooks). The mechanistic claim that "gradient mechanism is architecture-agnostic" should be stated explicitly and its limitations acknowledged.

---

## 6. Human Review Notes (MINOR/Style Issues — NOT Auto-Fixed)

| ID | Location | Issue | Type |
|----|----------|-------|------|
| HRN-1 | Section 7 (Conclusion) | "This paper establishes the mechanistic foundations of eviction-aware LoRA training. We show that the intervention produces the right *kind* of change" — "right kind" is vague. Consider: "produces structurally distinct adapter representations." | Style |
| HRN-2 | Section 5.1 | "The mean cosine similarity of 0.053 is striking" — "striking" is evaluative language that will invite reviewer skepticism. Replace with descriptive framing: "substantially lower than typical same-task LoRA similarity (>0.8)." | Tone |
| HRN-3 | Abstract | "the production-ready BudgetSweepEvaluator and SpearmanAnalyzer infrastructure we provide" — ending the abstract on infrastructure is anticlimactic for a mechanistic study. Consider closing on the mechanistic implication instead. | Structure |
| HRN-4 | Section 2.2 | LongLoRA [Chen et al., 2023] appears in the reference list but is not discussed in the related work section. This creates a "ghost citation" problem — a reviewer who notices LongLoRA in the refs and not in the text will wonder why it was excluded. Either cite it in the text or remove it from the bibliography. | Consistency |
| HRN-5 | Section 3.2.1 | Algorithm 1 step 2 shows the hook returning `standard_attention(Q, K, V)` in else (non-training) mode. The paper also states H2O eviction is "applied natively by the inference runtime." These need reconciliation: if the hook is deregistered during inference (as stated in Section 3.2.2), the else branch is dead code. Clarify. | Technical |
| HRN-6 | Section 6.1 | Interpretation B ("Short training duration (30 steps) and small proxy model may amplify instability") is good intellectual honesty but is not linked to a falsifiable follow-up in the conclusion. Section 7 lists H-M3 as the next step without explicitly noting it will test Interpretation A vs. B. | Narrative |
| HRN-7 | Section 4.2 | "Evaluation Data (H-M1): Five synthetic multi-sentence samples" — "multi-sentence" understates the LongBench context requirement. The data description should clarify these are short synthetic samples (not LongBench-length documents), explaining why they were used for attention pattern analysis rather than real LongBench data. | Clarity |
| HRN-8 | Section 1 (Contribution #3) | "Critically, the restructuring is concentrated in middle transformer layers (4–11)" — using "Critically" as a hedge-word for a 5-sample result over-weights the finding. | Tone |
| HRN-9 | Paper Statistics block | Word count is ~4,655 words (~8 pages). ICML 2025 main conference limit is 9 pages (content) + refs. The paper is within limit but sparse. Reviewers may note the short length; the mechanistic study framing justifies it but should be stated in the submission letter. | Meta |
| HRN-10 | Section 2.4 | Ben-David et al. [2010] domain adaptation citation: the paper cites this for training-inference distribution divergence. This is reasonable but the domain adaptation bound (ε(target) ≤ ε(source) + d_H(P,Q) + λ) applies to classifiers, not generative LLMs with attention mechanisms. The analogy should be noted as informal/intuitive rather than theoretically precise. | Accuracy |

---

## 7. Ground Truth Verification Log

### GTV-001: Cosine Similarity Numbers
- **Paper Abstract:** min=−0.578, mean≈0.053
- **Paper Section 5.1 Table:** min=−0.578, mean=0.053
- **065_ground_truth.yaml:** min=−0.5781, mean=0.053
- **h-e1/04_validation.md Metrics Table:** min=−0.0838, mean=−0.0079
- **h-e1/04_validation.md Gate Section:** min=−0.5781
- **h-e1/04_validation.md Mechanism Narrative:** mean≈0.053
- **Status: DISCREPANCY — metrics table contradicts narrative; paper matches narrative/ground_truth; raw data not verified**

### GTV-002: H-M1 Statistics
- **Paper Section 5.2 Table:** 8/12 layers, fraction=0.667, entropy diff=−0.0199, HH diff=+0.0008
- **h-m1/04_validation.md:** 8/12 layers, fraction=0.667, entropy diff=−0.0199, HH diff=+0.0008
- **Status: MATCH — all numbers verified**

### GTV-003: Training Configuration
- **Paper Section 3.3:** steps=30, samples=200, kv_budget=0.50, n_sink=4, rank=8 (proxy), rank=16 (target), alpha=32
- **065_ground_truth.yaml:** steps=30, samples=200, kv_budget=0.50, n_sink=4, rank proxy=8, rank target=16, alpha=32
- **h-e1/04_validation.md Optimal Hyperparameters:** alpha=16 (DISCREPANCY with paper/ground_truth)
- **Status: PARTIAL MATCH — alpha discrepancy in validation doc appendix**

### GTV-004: H-M2 Status
- **Paper Section 5.3:** GPT-2 context window insufficient, CUDA crash, 63 sequential evaluations completed
- **065_ground_truth.yaml:** gate=SHOULD_WORK, gate_result=LIMITATION_RECORDED, 63 sequential runs, CUDA crash confirmed
- **Status: MATCH**

### GTV-005: H-M3 Status
- **Paper Section 6.2 L1, Section 5.4:** NOT_STARTED, gated model access required
- **065_ground_truth.yaml:** NOT_STARTED
- **Status: MATCH**

### GTV-006: P1 Accuracy Claim
- **Paper:** Does NOT claim ≥2% LongBench accuracy gain anywhere
- **065_ground_truth.yaml:** claim="NOT CLAIMED in paper", verified=true
- **Status: CORRECTLY ABSENT — VERIFIED**

### GTV-007: Limitations L1–L6
- All six limitations present in Section 6.2 with accurate descriptions
- **Status: ALL MATCH**

---

## 8. Summary for Revision Agent (Prioritized Fix List)

### Priority 1 — FATAL (Must resolve before submission)

**F-1: Verify and reconcile cosine similarity values from raw output files**
- Action: Read `h-e1/experiment_results.json` and `h-e1/code/outputs/results.csv` directly
- Verify whether min=−0.0838/mean=−0.0079 (metrics table) or min=−0.5781/mean=0.053 (narrative) is correct
- Update paper Section 5.1, Abstract, and contribution list to reflect verified values
- If true values are closer to −0.0838/−0.0079, revise "striking" and "near-orthogonal" language accordingly
- Update `h-e1/04_validation.md` metrics table to remove internal inconsistency

### Priority 2 — MAJOR (Must fix before submission)

**M-1: Add n=5 qualifier to abstract and Section 1 contribution #3**
- Location: Abstract ("restructures attention patterns in 8 of 12 transformer layers (p < 0.05)")
- Add: "(n=5 synthetic samples, GPT-2 proxy)" immediately after p-value
- Same fix in Section 1 contribution #3

**M-2: Replace "production-ready" with accurate terminology**
- Location: Abstract (last sentence), Section 1 contribution #4, Section 3.5 header
- Replace with: "validated implementation" or "full-scale-ready infrastructure (requires attn_implementation='eager')"
- Note the CUDA crash as the known obstacle in these sections

**M-3: Verify LoRA alpha hyperparameter**
- Location: Section 3.3 Table (alpha=32) vs h-e1/04_validation.md Optimal Hyperparameters (alpha=16)
- Verify actual training run configuration; update either the paper or the validation appendix

**M-4: Strengthen or hedge "first systematic study" claim**
- Location: Section 1 contribution #1
- Add explicit statement about LongLoRA relationship
- Acknowledge that no MCP-verified literature search was conducted; strengthen "to our knowledge" hedge

**M-5: Add random-mask ablation as absent baseline or flag explicitly**
- Location: Section 4.3 (Baselines)
- Add acknowledgment that randomized mask ablation (same budget, random token removal) was not evaluated, preventing attribution of divergence specifically to H2O policy-driven masks
- Add this as Limitation L7 in Section 6.2

**M-6: Qualify Clark et al. [2019] BERT→GPT-2 transfer**
- Location: Section 2.3 and Section 6.1
- Add: "While Clark et al. analyzed encoder-only BERT, the middle-layer long-range dependency pattern has been observed across architectures; our GPT-2 results are consistent with this pattern but require replication on decoder models at scale."

**M-7: Address LongLoRA citation in related work**
- Location: Section 2 and References
- Either discuss LongLoRA in Section 2 (why it does not address the same problem) or remove from references

### Priority 3 — Human Review Notes (Revision author judgment)

HRN-1 through HRN-10 as listed in Section 6: style, tone, and clarity improvements. These are recommended but not mandatory for submission.

---

## Metadata

```yaml
review_id: "065_review_r1"
paper_id: "H-EvictionAwareLoRA-v1"
review_date: "2026-05-04"
reviewer_persona_count: 3
fatal_count: 1
major_count: 7
human_review_notes_count: 10
persuasiveness_passed: true
key_issues:
  - "Cosine similarity source document internal inconsistency (FATAL) — metrics table vs narrative in h-e1/04_validation.md"
  - "n=5 statistical basis for attention restructuring claim not qualified in abstract (MAJOR)"
  - "Production-ready claim contradicted by undocumented CUDA crash scope (MAJOR)"
  - "LoRA alpha discrepancy: paper says 32, validation appendix says 16 (MAJOR)"
  - "First-method novelty claim unverifiable without literature search (MAJOR)"
  - "No randomized mask ablation baseline (MAJOR)"
  - "Clark et al. BERT-to-GPT-2 layer specificity transfer not justified (MAJOR)"
recommendation: "REVISE"
revision_blocking_items:
  - "F-1: Raw data verification of cosine similarity values"
  - "M-1: Abstract n=5 qualification"
  - "M-2: Production-ready language correction"
  - "M-3: Alpha hyperparameter reconciliation"
notes: "Paper is fundamentally sound as a mechanistic study. The fatal issue is a documentation traceability problem, not an experimental fraud. If raw data confirms min=-0.5781/mean=0.053, only the metrics table in 04_validation.md needs correction and the paper stands. If raw data confirms min=-0.0838/mean=-0.0079, the main quantitative claims require significant revision."
```
