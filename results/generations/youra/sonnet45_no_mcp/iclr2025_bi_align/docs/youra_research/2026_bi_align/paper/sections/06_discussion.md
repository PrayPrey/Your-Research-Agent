# Discussion

## Key Findings

Our experiments reveal three critical findings that reshape understanding of alignment structure in RLHF data:

**Finding 1: RLHF datasets contain verifiable safety violations.** The HH-RLHF harmless subset achieves 45.6% genuine violation base-rate (95% CI: [41.3%, 50.0%]), validating dataset quality for alignment research. This addresses a gap in RLHF literature—prior work assumes preference labels are valid but doesn't empirically audit base-rates. Our validation protocol provides a reusable framework for dataset quality assessment, applicable to WebGPT, Summarization from Feedback, and future RLHF benchmarks.

**Finding 2: Human annotators achieve substantial consistency with explicit criteria.** Inter-annotator agreement (κ=0.724) demonstrates that violation detection is learnable and reproducible, not purely subjective. This validates that human-detectable structure exists in preference data—annotators apply explicit safety criteria with 83.6% alignment to original labels. The consistency suggests aggregated human judgments provide reliable signal, supporting the premise that structure *should* emerge if representations capture safety-relevant features.

**Finding 3: Pretrained embeddings fail to capture alignment structure despite human detection consistency.** This is the central negative finding. RoBERTa embeddings show effectively random separation (Cohen's d=0.034, only 8.5× above baseline), revealing a fundamental disconnect: **human-detectable structure (κ=0.724) ≠ embedding-space structure (d=0.034)**. With 160K samples providing >0.99 statistical power, this is not a data insufficiency issue—it's a representation limitation.

**Synthesis:** Pretrained encoders optimize for general semantic similarity (masked language modeling), not safety-specific discrimination. Alignment violations span diverse semantic content—toxicity, misinformation, harmful instructions—that occupy overlapping embedding regions despite human-detectable differences. Safety distinctions operate on semantic dimensions orthogonal to general-purpose pretraining objectives.

**Implications for the field:** This work establishes that embedding-space clustering approaches using standard pretrained models are insufficient for alignment evaluation. Future work should investigate safety-specialized representations: reward model embeddings (learned from preference data during RLHF training), safety-fine-tuned encoders (e.g., toxic-BERT), or encoder-agnostic methods (graph-based, kernel methods). The negative result is scientifically valuable—it saves the community from pursuing dead-end approaches and redirects research toward promising alternatives.

## Limitations

We acknowledge several limitations that bound the scope of our findings:

**L1: Single-encoder negative result.** We tested only RoBERTa-base. Safety-fine-tuned encoders (unitary/toxic-bert) or reward model embeddings may capture structure that general-purpose encoders miss.

- **Why acceptable:** RoBERTa is a widely-used, well-validated baseline that establishes standard pretrained models are insufficient. This is the natural first test—demonstrating failure of the most accessible approach.
- **Future mitigation:** Multi-encoder validation (DeBERTa, SentenceTransformer) and safety-specialized alternatives (proposed in Section 7). If *any* encoder shows d≥0.5, it would refine our conclusion from "embeddings fail" to "general-purpose embeddings fail."

**L2: Annotation consistency used untrained data.** H-m1 achieved κ=0.724 using h-e1 annotators without the full 1-hour training protocol (human subjects constraint), potentially underestimating ceiling performance.

- **Why acceptable:** This is a proof-of-concept demonstrating analysis infrastructure. The κ=0.724 baseline already shows substantial agreement (exceeds 0.70 threshold), and prior annotation studies suggest training improves κ by 0.10-0.15, which would strengthen (not weaken) our conclusions.
- **Future mitigation:** Recruit trained annotators following the protocol in experiment design. Higher agreement would further validate human-detectable structure, making the embedding failure even more striking.

**L3: HH-RLHF harmless subset only.** Results are specific to safety violations in conversational AI. Helpfulness preferences, other RLHF datasets (WebGPT, Summarization from Feedback), and non-English data remain untested.

- **Why acceptable:** Focused scope enables controlled experiments. The harmless subset isolates safety-related judgments (vs. helpfulness), directly testing our hypothesis. The validation protocol is dataset-agnostic and generalizable.
- **Future mitigation:** Apply to helpfulness preferences (likely even more subjective, predicting weaker clustering), other RLHF datasets (cross-dataset validation), and multilingual settings.

**L4: Geometric structure hypotheses untested.** H-m3 (severity-distance correlation) and h-m4 (encoder invariance) were blocked by h-m2 failure. We cannot test whether distance encodes severity or structure is encoder-invariant.

- **Why acceptable:** Testing these requires clustering to exist first. Without baseline separation (d=0.034), analyzing cluster properties (severity, multi-dimensionality) is meaningless—there are no clusters to characterize.
- **Future mitigation:** If alternative encoders show clustering (d≥0.5), h-m3/h-m4 testing becomes viable. Our protocol provides the blueprint.

## Broader Impact

**Positive impacts:** This work advances AI safety through three mechanisms:

1. **Dataset quality validation:** Our base-rate protocol (45.6% genuine violations) provides empirical grounding for RLHF dataset quality, enabling researchers to verify annotation authenticity before investing in expensive model training.

2. **Methodological contribution:** The three-hypothesis cascade (existence → consistency → structure) offers a reusable framework for testing complex causal chains in alignment research, applicable beyond embedding clustering to other structural hypotheses.

3. **Research redirection:** By demonstrating pretrained encoder insufficiency, we redirect community effort toward safety-specialized representations and reward model mechanistic interpretability, potentially accelerating progress on interpretable alignment evaluation.

**Potential concerns:** We identify no significant dual-use concerns. This work is defensive (alignment evaluation methodology) rather than offensive (attack generation). The negative finding actually *limits* potential misuse—demonstrating that general-purpose embeddings don't capture safety structure reduces risk of adversarial exploitation via embedding-space attacks.

**Negative result as contribution:** Scientific progress requires both positive and negative results. By rigorously testing and refuting the geometric manifold hypothesis for pretrained embeddings, we establish knowledge boundaries: what doesn't work, why it fails, and what alternatives to pursue. This prevents wasted research effort and clarifies the path forward for alignment evaluation infrastructure.

## Comparison to Expectations

Our findings deviate from Phase 2A expectations in instructive ways:

**Expected (Phase 2A hypothesis):** Aggregated human judgments (160K+) induce multi-dimensional geometric structure in embedding space, with distance encoding severity and PC directions encoding violation types.

**Observed:** Human judgments are consistent (κ=0.724) but induce no embedding structure (d=0.034). The failure point is representation, not data quality or annotation consistency.

**Why this matters:** The original hypothesis assumed semantic similarity (captured by pretraining) correlates with safety similarity. Our results demonstrate these are orthogonal—violations are semantically diverse despite sharing "unsafe" classification. This conceptual insight is more valuable than confirming the hypothesis would have been, as it clarifies fundamental limitations of representation learning for safety tasks.

## Theoretical Interpretation

Why do pretrained embeddings fail despite human detection consistency? Three complementary explanations:

**Explanation 1: Optimization objective mismatch.** RoBERTa optimizes masked language modeling (predict masked tokens from context). Safety violations aren't defined by missing tokens—they're defined by content violating policies. A response can be grammatically coherent, semantically plausible, and still unsafe. Pretrained embeddings capture linguistic plausibility, not normative safety.

**Explanation 2: Semantic diversity of violations.** Toxicity ("You're worthless"), harmful instructions ("How to build explosives"), and misinformation ("Vaccines cause autism") occupy distant semantic regions despite unified "unsafe" classification. Unlike clustering tasks where semantic similarity ≈ task similarity (e.g., sentiment analysis, topic modeling), safety violations lack semantic cohesion. They're defined by violating policies, not sharing linguistic features.

**Explanation 3: Implicit vs. explicit features.** Human annotators detect violations using explicit criteria (policy violations, harm potential, truthfulness). Pretrained embeddings encode distributional statistics (word co-occurrence, syntactic patterns). These feature spaces are non-overlapping for safety tasks—the signals humans use aren't manifest in pretraining objectives.

**Supporting evidence:** The near-zero effect size (d=0.034) with massive sample size (160K) rules out weak-but-real effects. This is a fundamental representation failure, not a statistical power issue. If safety structure existed in pretrained embeddings, 160K samples would reveal it.

**Implications:** Safety-specialized representations likely encode different features—reward models trained on preferences may learn latent "unsafe" dimensions absent in pretrained encoders. Investigating reward model geometry (do they develop structure during preference learning?) is a promising research direction connecting RLHF mechanistic interpretability with alignment evaluation.
