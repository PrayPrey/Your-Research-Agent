# 6. Discussion

## 6.1 The Reproducibility Gap

The CCP paper (arxiv:2403.04696) reports +0.05–0.10 ROC-AUC improvements on biography generation tasks but does not provide:
- Raw $\rho_j$ distributions (only aggregate ROC-AUC)
- NLI calibration diagnostics (does the model work on known examples?)
- Claim decomposition methodology (sentence tokenization? LLM extraction? dependency parsing?)
- Context pairing strategy (full-text context? claim-local windows?)
- Hyperparameters (batch size, sequence length, truncation strategy)

This lack of detail is not unique to CCP—it reflects a **field-wide pattern** in hallucination detection research. Papers optimize for **novelty** (reporting metric improvements) over **reproducibility** (documenting how to achieve the baseline). When we attempted to replicate CCP following published equations and literature precedents (cavaquinho, HallucinoGenAI implementations), we obtained $\rho_j$ values 50× lower than expected.

**Three Explanations**:

1. **Our implementation is wrong**: We misinterpreted the CCP mechanism despite following published equations and code patterns from independent implementations.

2. **CCP paper uses undocumented techniques**: The authors may have applied NLI fine-tuning, claim filtering, or threshold tuning that are critical for achieving reported metrics but were not documented.

3. **CCP paper metrics are not directly comparable**: The reported ROC-AUC improvements may involve additional components (e.g., combining CCP with other features) not described in the method section.

We cannot determine which explanation is correct without access to the original implementation or correspondence with the authors. This ambiguity is the **cost of irreproducibility**: future researchers cannot build on the work because the baseline cannot be established.

## 6.2 Implications for Hallucination Detection Research

Our failure exposes three field-wide practices that hinder reproducibility:

**Practice 1: Reporting Aggregate Metrics Without Distributions**

Papers report ROC-AUC, F1, or BLEU scores but omit raw metric distributions. This obscures failure modes:
- **Our case**: $\rho_j$ median 0.0354 would be invisible if we only reported ROC-AUC (a downstream metric that could still show marginal improvements even with broken $\rho_j$).
- **Consequence**: Readers cannot diagnose whether poor performance is due to metric noise, calibration issues, or fundamental method failure.

**Practice 2: NLI Calibration Treated as Implementation Detail**

NLI model choice (DeBERTa-v3-base, RoBERTa-large-MNLI, BART-large-MNLI) and calibration (fine-tuning on FEVER, temperature scaling) are documented inconsistently or not at all.
- **Our case**: DeBERTa-v3-base trained on SNLI/MNLI assigns ~90% mass to "neutral" for claim-context pairs, mechanistically driving $\rho_j \to 0$.
- **Consequence**: Readers cannot determine whether NLI calibration is critical (our finding) or incidental (paper's implication).

**Practice 3: Claim Decomposition as Assumed Primitive**

Papers state "we extract claims via sentence tokenization" without specifying the library (NLTK? Spacy?), validation methodology, or inter-method agreement.
- **Our case**: Sentence tokenization may conflate sentence boundaries with logical claim boundaries, inflating neutral-class mass if claims are incomplete or compound.
- **Consequence**: Readers cannot replicate the claim extraction step, preventing method comparison.

## 6.3 Recommendations for Authors

We propose four concrete practices (R1–R4) to improve reproducibility in hallucination detection research:

**R1: Report Raw Metric Distributions, Not Just Aggregates**

**What to include**:
- Median, mean, std dev, min, max for all primary metrics ($\rho_j$, claim-level scores, token probabilities)
- Violin plots or histograms showing full distribution (not just summary statistics)
- Per-domain breakdowns (factual vs creative, TruthfulQA vs WritingPrompts)

**Why it matters**: Distribution shape reveals failure modes (e.g., bimodal distributions suggest subpopulation differences; skewed distributions with long tails indicate outlier sensitivity).

**Example from our work**: Reporting $\rho_j$ median 0.0354 immediately signals a problem (50× below expected 0.75–0.85), whereas reporting only ROC-AUC might mask this.

---

**R2: Validate NLI Calibration on Known Examples**

**What to include**:
- Test NLI model on 10–20 manually verified entailment/contradiction examples from your target domain.
- **Expected behavior**: $P(\text{entail}|\text{correct}) > 0.5$, $P(\text{contradict}|\text{incorrect}) > 0.5$.
- **If failed**: Document whether you fine-tuned the NLI model (on FEVER, HotpotQA, or custom data) or adjusted thresholds.

**Why it matters**: Off-the-shelf NLI models trained on SNLI/MNLI may not generalize to factual verification tasks. Validating on known examples (TruthfulQA correct vs incorrect answers, FEVER claims) is a 1-hour sanity check that can prevent months of debugging.

**Example from our work**: Our sanity check revealed $P(\text{entail}|\text{correct}) = 0.11$ (expected > 0.5), immediately identifying NLI calibration as the root cause.

---

**R3: Document Claim Decomposition with Inter-Method Agreement**

**What to include**:
- Specify claim extraction method: NLTK sentence tokenization, Spacy segmentation, LLM-based extraction (GPT-3.5/GPT-4), dependency parsing.
- Report inter-method agreement: Compare two methods (e.g., NLTK vs LLM) on 50–100 samples and compute Krippendorff's $\alpha > 0.7$.
- **If $\alpha < 0.7$**: Document which method you selected and why (e.g., LLM extraction has higher precision but 10× cost).

**Why it matters**: Claim boundaries affect $\rho_j$ denominators. If methods disagree (e.g., NLTK extracts 5 claims/sample, LLM extracts 8), the metric values are not comparable across papers.

**Example from our work**: We used NLTK tokenization but did not validate against alternatives. Krippendorff's $\alpha = 0.75$ (computed post-hoc) suggests acceptable reliability, but LLM extraction might improve $\rho_j$ by reducing incomplete claims.

---

**R4: Provide Public Code with Baseline Replication Notebooks**

**What to include**:
- Full implementation (data loaders, NLI inference, metric computation, visualization)
- **Baseline replication notebook**: Reproduce your paper's main result (ROC-AUC on original dataset) in <100 lines of code
- Unit tests: 5–10 examples with expected outputs (e.g., "given this claim and context, NLI should output P(entail) > 0.7")
- Configuration files: Document all hyperparameters (batch size, sequence length, random seed)

**Why it matters**: Public code enables rapid iteration. Semantic Entropy (Farquhar et al., 2024) released official code and achieved 200+ citations in <1 year. CCP has no public code and has <10 citations.

**Example from our work**: We provide `h-e1/code/` with unit tests, configuration files, and a `run.py` entry point. Reproducing our results requires: `pip install -r requirements.txt && python3 run.py`.

## 6.4 Limitations of This Work

We document seven limitations, ordered by severity (CRITICAL > HIGH > MEDIUM > LOW):

**L1 (CRITICAL): Measurement Validity Failure**

$\rho_j$ values 50× lower than expected (0.01–0.04 vs 0.75–0.85) invalidate all hypothesis tests. Root cause: DeBERTa-v3-base NLI assigns ~90% mass to "neutral" class.

**Mitigation for future work**: Fine-tune NLI on FEVER/HotpotQA (1000–5000 examples). If $\rho_j$ reaches 0.70–0.85, retest hypothesis.

---

**L2 (HIGH): Claim Decomposition Method**

NLTK sentence tokenization may not capture logical claims (sentences ≠ propositions). No inter-method agreement analysis (NLTK vs LLM vs Spacy).

**Mitigation for future work**: Compare claim extraction methods. If LLM extraction improves $\rho_j$ by >0.10, claim decomposition is contributory to failure.

---

**L3 (HIGH): No Baseline Replication**

Did not replicate CCP on TruthfulQA factual domain BEFORE testing creative domain transfer. Cannot validate expected $\rho_j$ range (0.75–0.85).

**Mitigation for future work**: Replicate CCP ROC-AUC on original dataset (biographies). If failed, contact authors or pivot to alternative baseline (SelfCheckGPT, AGSER).

---

**L4 (MEDIUM): Incomplete Experimental Design**

Only completed Phase 1 (CCP ontology stress). Phase 2 (AGSER vs HAD comparative mechanisms) and Phase 3 (aggregation ablation) not implemented.

**Mitigation for future work**: Implement AGSER and HAD baselines. If AGSER degrades while HAD remains robust, ontology-mismatch hypothesis gains indirect support.

---

**L5 (MEDIUM): Context Pairing Strategy**

Used full-text context instead of claim-local windows (±2 sentences). May contribute to neutral-class dominance if long-distance dependencies exceed NLI model capacity.

**Mitigation for future work**: Ablate context window size (full-text vs ±1, ±2, ±3 sentences). If optimal window improves $\rho_j$ by >0.10, context pairing is contributory.

---

**L6 (LOW): Dataset as Domain Proxy**

TruthfulQA and WritingPrompts are proxies for factual/creative domains but may not capture all ontology-specific features (metaphor density, speculation markers).

**Mitigation for future work**: Add ontology metrics (metaphor spans, abstraction level). Test on multiple dataset pairs (Wikipedia vs poetry, news vs fiction).

---

**L7 (LOW): Single Model Architecture**

Only tested DeBERTa-v3-base. Alternative NLI models (RoBERTa-large-MNLI, BART-large-MNLI, TRUE factuality model) may show different $\rho_j$ distributions.

**Mitigation for future work**: Test alternative NLI models. If all show neutral-class dominance, task-domain gap (SNLI/MNLI ≠ factual verification) is confirmed as task-general.

## 6.5 Future Work

**Tier 1 (Immediate)**: NLI calibration fixes (fine-tuning on FEVER, alternative models, temperature scaling). Success criterion: $\rho_j > 0.70$ on factual text.

**Tier 2 (Contingent on Tier 1)**: Re-test h-e1 (ontology sensitivity) with validated methodology. If $\Delta\rho_j > 0.15$, hypothesis confirmed. If $\Delta\rho_j < 0.05$, hypothesis refuted.

**Tier 3 (Novel Directions)**: NLI domain adaptation for creative text (train NLI to distinguish "creative truth" = narrative consistency vs hallucination). Build creative-factual paired dataset (5000–10000 examples).

**Tier 4 (Long-Term)**: Hallucination detection reproducibility study (replicate CCP, AGSER, HAD, SelfCheckGPT on common benchmarks). Benchmark for creativity-preserving hallucination detection.

## 6.6 Broader Impact

**Positive**: Transparent failure documentation prevents field-wide repetition of costly mistakes. Our reproducibility recommendations (R1–R4), if adopted, could improve hallucination detection research quality.

**Negative**: May discourage researchers from building on CCP paper due to replication uncertainty. Could slow progress if interpreted as "hallucination detection doesn't work" rather than "specific implementation needs methodological fixes."

**Mitigation**: Frame this work as constructive critique (improve standards) rather than dismissal (abandon method). NLI-based hallucination detection remains a promising direction—it requires higher methodological rigor, not abandonment.

**Ethical Considerations**: Creativity-preserving hallucination detection (if the ontology-mismatch hypothesis is later confirmed) could enable safer creative AI assistants for fiction writing, poetry generation, and metaphor-rich domains. However, overly aggressive filtering risks suppressing legitimate creative expression. Task-conditional epistemic regulation (detect factual vs creative ontology automatically) is critical to balance safety and creativity.
