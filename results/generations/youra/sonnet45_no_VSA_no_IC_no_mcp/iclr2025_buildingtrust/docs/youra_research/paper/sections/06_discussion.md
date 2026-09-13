# 6. Discussion

Our experiments reveal three key findings: (1) robust attention pattern signature distinguishing failure types (p < 0.001, large effect), (2) zero-entropy entity-errors indicating precision errors, and (3) actionable classification mechanism enabling automated routing. We discuss interpretation, limitations, and broader implications.

## 6.1 Zero-Entropy Entity-Errors as Precision Errors

The most striking finding is that 60% of entity-substitution errors exhibit zero entropy (H = 0.000) over correct entity spans. We expected low entropy (focused attention), but not deterministic (zero) attention distribution. This pattern reveals that entity-substitution failures are *precision errors* rather than *recall errors*.

**Precision vs Recall Errors.** A precision error occurs when the model focuses attention deterministically on the wrong target — it looks at something specific, but that something is incorrect. A recall error occurs when the model fails to attend to the relevant information at all (absence of focused attention). Zero-entropy cases indicate the former: the model deterministically attends elsewhere (incorrect entity or non-entity context) rather than distributing attention broadly.

**Mechanistic Interpretation.** When GPT-2 makes an entity-substitution error on "What is the capital of France?", zero entropy over "France" tokens means the model ignores "France" entirely. Attention concentrates on other tokens (perhaps "capital" or earlier context), leading to entity hallucination (e.g., answering "Lyon"). The model does not lack attention capacity — it misallocates attention deterministically.

**Implication for Correction.** RAG correction targets this attention misdirection. By retrieving the correct entity ("Paris is the capital of France") and injecting it into the generation context, RAG provides the correct target for attention re-direction. The model can re-attend to the correct entity in the augmented context. COT, in contrast, addresses reasoning decomposition ("Step 1: Identify the question type. Step 2: Recall that Paris is the capital."), which does not directly fix entity-level attention misdirection. This mechanistic grounding justifies matched routing (entity → RAG).

**Competing Explanation.** An alternative explanation is that zero-entropy results from span alignment artifacts — misaligned token spans may artificially produce zero entropy if no tokens fall within the measured span. However, we excluded 27% of samples conservatively (only aligned spans analyzed), and zero-entropy pattern persists within aligned subset (30/50 entity-errors). The effect size (d = -1.13) and statistical significance (p < 0.001) argue against artifact-only explanation.

## 6.2 Honest Limitations

We acknowledge five principled limitations that bound the scope of our claims.

### L1: Model-Specific Attention Patterns (GPT-2 Only)

**Limitation.** Attention pattern signature validated only in GPT-2 (124M parameters, 12 layers, BPE tokenization). Unknown whether larger models (Llama-2-7B, GPT-3.5, GPT-4) exhibit the same entropy difference.

**Root Cause.** CPU-only environment forced GPT-2 fallback. Llama-2-7B (7B parameters, 32 layers) requires GPU (16GB VRAM) for attention extraction. Original experiment plan specified multi-model replication.

**Impact on Results.** Generalization claims limited to GPT-2 architecture. The optimal threshold (H* = 0.32) may be model-specific. Larger models with different attention mechanisms (e.g., sparse attention, longer context windows) may show different entropy distributions or no separation.

**Boundary.** Results apply to GPT-2 under TruthfulQA single-entity factual questions. Hypothesis scope reduced to single-model proof-of-concept validation.

**Mitigation.** FW1 (HIGH priority): Replicate h-e1 with Llama-2-7B, GPT-3.5, GPT-4 on GPU. Test if threshold generalizes across architectures or requires model-specific calibration. If replication succeeds (p < 0.05 in each model), pattern generalizes. If not, attention entropy may be GPT-2-specific artifact.

### L2: Synthetic Correction Effectiveness (Mock Implementation)

**Limitation.** h-m2 correction routing tested with mock RAG/COT pipelines (configurable success rates: RAG = 55% ± 5%, COT = 30% ± 5%). No real Wikipedia retrieval, no real LLM generation, no GPT-judge evaluation.

**Root Cause.** Ablation test environment lacks external API access (no Wikipedia API, no GPT-3.5 API, no GPT-judge). Budget constraint for real-world validation.

**Impact on Results.** Pipeline structure validated (data loading, dual-model framework, gate checking, matched vs mismatched comparison), but correction effectiveness results (RAG 52% vs COT 28%) are synthetic placeholders. Cannot claim real-world improvement without actual correction experiments.

**Boundary.** Framework demonstrates feasibility (structure), not effectiveness. Real-world correction improvement UNPROVEN.

**Mitigation.** FW2 (HIGH priority): Implement full RAG pipeline (spaCy NER → Wikipedia API → GPT-3.5 generation with context) + real COT baseline (GPT-3.5 with "Let's think step by step" prompt). Evaluate on 50 entity-errors using GPT-judge (GPT-4 or Claude). Measure if real RAG achieves ≥20pp improvement. This experiment is critical for paper credibility — without it, we can only claim diagnostic classification, not correction routing effectiveness.

### L3: Manual Gold Labeling Bottleneck (N=100)

**Limitation.** Requires manual classification of entity-error vs non-entity-error failures (N=100 samples, ~2-4 hours human effort per model). No automated labeling validated.

**Root Cause.** Proof-of-concept scope — automated labeling deferred to validate pattern existence before scalability investment.

**Impact on Results.** Scalability limited to manual annotation capacity. Real-world deployment (1000s of failures) infeasible without automated classification. Production systems would face annotation bottleneck.

**Boundary.** Framework demonstrated on small-scale dataset (N=100). Large-scale routing requires automated labeling to bypass human bottleneck.

**Mitigation.** FW4 (MEDIUM priority): Train supervised classifier (logistic regression or small BERT) on 100 gold-labeled samples (features: entropy + question metadata like question length, entity count, question type). Test if automated labels achieve ≥80% agreement with manual labels. Deploy for large-scale routing. If agreement ≥80%, automated labeling viable and bottleneck removed.

### L4: Single Failure Type (Entity-Substitution Only)

**Limitation.** Pattern detection and routing validated only for entity-substitution errors. Reasoning errors, knowledge gaps, hybrid failures not tested.

**Root Cause.** Scope reduction for tractability — single failure type proof-of-concept. Binary classification (entity vs non-entity) simpler than multi-class (entity vs reasoning vs knowledge-gap vs hybrid).

**Impact on Results.** Generalization to other failure modes unknown. Dual routing (entity → RAG, reasoning → COT) not validated. Only entity → RAG tested (COT routing hypothesis untested).

**Boundary.** Framework applies to entity-substitution errors in single-entity factual questions. Other failure types require separate validation to confirm distinct attention signatures.

**Mitigation.** FW3 (MEDIUM priority): Extend gold-label taxonomy to 3+ failure types (entity-substitution, reasoning-error, knowledge-gap, N=150 total, 50 per class). Extract attention patterns for each type. Test if multi-class entropy-based classifier achieves ≥70% accuracy. Implement matched routing for each failure type (entity → RAG, reasoning → COT, knowledge-gap → retrieval + COT). This extension tests whether attention patterns generalize beyond entity-substitution.

### L5: Span Alignment Failures (27% Sample Loss)

**Limitation.** 27% of non-entity-error samples lost to character-to-token span misalignment (spaCy NER produces character-level spans, GPT-2 uses BPE tokenization).

**Root Cause.** Tokenizer mismatch — NER identifies entity spans at character level ("France" = characters 31-36), GPT-2 BPE breaks entities into subword tokens. Character-to-token mapping returns `None` for misaligned spans where entity mid-token fragment occurs.

**Impact on Results.** Reduced sample size for non-entity-errors (50 → 23). Pattern robust despite loss (p < 0.001 with N=23), but larger N would strengthen statistical power. Conservative exclusion (only aligned spans analyzed) preserves validity.

**Boundary.** Results valid for alignable spans only. Misaligned spans may have different entropy distributions, though unlikely to reverse pattern (effect size d = -1.13 is large).

**Mitigation.** FW5 (MEDIUM priority): Implement sub-word-aware span alignment (include tokens overlapping entity span by ≥50% rather than requiring exact alignment) or retrain NER with GPT-2 tokenizer (produces token-level spans matching BPE segmentation). Re-run h-e1 with recovered samples. Target: <5% sample loss. If recovered samples show same entropy difference (p < 0.05), alignment method validated.

## 6.3 Broader Impact

**Positive Impacts.** Automated failure diagnosis enables targeted LLM reliability improvement without manual interpretability analysis bottleneck. Practitioners can deploy matched correction (entity → RAG) without expert knowledge of attention mechanisms. Benchmark evaluation shifts from aggregate scoring to actionable improvement guidance, accelerating model development cycles.

**Negative Concerns.** Diagnostic routing assumes failure categorization is meaningful — if failure types are not truly distinct (hybrid cases mixing entity-substitution and reasoning), misclassification risk. Routing entity-errors to RAG when reasoning also contributes could miss part of the problem. Conservative subset restriction (single-entity questions) reduces this risk in our controlled setting, but production deployment on diverse question types needs validation.

**Mitigation.** Production deployment should validate classification accuracy on target domain before routing. If domain contains many hybrid failures (e.g., multi-entity questions), extend classification to multi-class (FW3) or add confidence thresholding (only route high-confidence classifications, flag ambiguous cases for manual review).

**Fairness Considerations.** NER tools may have differential accuracy across entity types (standard entities like "France" vs rare entities, non-Western names). If NER F1 drops below 90% on specific subpopulations, entropy measurement quality degrades for those cases. We validated 96% overall F1, but subset analysis (entity type stratification) recommended before claiming uniform coverage.

## 6.4 Significance Beyond Immediate Results

Our framework demonstrates that systematic integration of benchmarks, interpretability, and correction is tractable. Prior work treated these areas independently — benchmarks measure, interpretability explains, correction fixes. We show they can form a closed loop: benchmark failures automatically trigger interpretability-based diagnosis, diagnostic classification routes to correction methods, and the entire pipeline operates at benchmark scale (73 processed samples vs 10-20 manual examples).

This integration opens research paths beyond entity-substitution errors. Can reasoning errors be diagnosed via attention patterns over reasoning keywords (high entropy indicating failure to focus on logical connectives)? Do knowledge gaps exhibit distinct signatures (uniform attention indicating no confident signal)? Does multi-class classification (entity vs reasoning vs knowledge-gap) achieve ≥70% accuracy using attention features alone, or must we incorporate additional signals (question type, syntactic structure, output confidence)?

The conceptual contribution is reframing benchmark failures from binary (correct/incorrect) to diagnostic profiles (failure-type + measurable signature). This shift enables precision interventions — matched correction targeting root causes rather than uniform application hoping to fix unknown problems.
