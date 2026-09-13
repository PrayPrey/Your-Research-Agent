# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-06
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-KGCulturalEval-v1
**Confidence Level:** 0.75

**Main Hypothesis:**
Under the condition that target cultures have ≥50 entities in knowledge graphs (Wikidata, ConceptNet), if knowledge graph-driven automated test case generation combined with unified multi-metric evaluation is applied to AI systems (T2I, LLM, vision models), then cultural AI evaluation will scale with O(log n) annotation effort vs O(n) manual approaches because structured knowledge graphs enable programmatic extraction of culture-specific test cases without requiring per-culture expert annotation.

**Alternative Hypothesis (H0):**
Knowledge graph-driven test case generation provides no significant scalability advantage over manual annotation methods, and annotation effort remains O(n) with culture count.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| Target Culture | Independent | Culture selection from KG entities with ≥50 cultural artifacts (food, architecture, symbols, festivals) | 100+ cultures (phased: 20 → 100+) |
| Cultural Competence Score | Dependent | Hierarchical metric: L1 (CRaFT 4 metrics, CultDiff disparity, CARB coverage), L2 (weighted: 30% representation, 25% quality, 25% fluency, 20% deviation), L3 (0-100 scale) | 0-100 (threshold: >60 competent, <40 culturally inappropriate) |
| AI System Type | Controlled | T2I models (Stable Diffusion, DALL-E), LLMs (GPT, Claude), vision models with REST/GraphQL API | Standardized API with rate limiting |
| KG Source | Controlled | Wikidata (primary via SPARQL), ConceptNet (fallback) | Query templates per domain |
| Baseline Method | Controlled | Manual annotation (CRaFT: 3 languages, CultDiff: 10 countries, CARB: 10 cultures) | Annotation hours per culture |

### 1.3 Causal Mechanism

**3-Step Causal Chain:**

**Step 1: KG Queries Extract Cultural Entities → Automated Test Case Generation**
- Mechanism: SPARQL queries retrieve culture-specific entities (food, architecture, symbols) from Wikidata/ConceptNet; template instantiation generates AI prompts (e.g., "Generate [traditional food] from [culture]")
- Evidence: MakiEval (2025) demonstrated Wikidata-based automatic multilingual test generation scaling to 400+ languages
- Falsification: If <50 entities per culture in KG

**Step 2: Automated Test Cases → Multi-Metric Evaluation Scores**
- Mechanism: Unified framework applies CRaFT's 4 metrics (Cultural Fluency, Deviation, Consistency, Linguistic Adaptation) + CultDiff disparity analysis + CARB domain coverage to AI outputs
- Evidence: CRaFT (2025) validated explanation-based evaluation with 4 interpretable metrics showing cross-lingual variation (Arabic reduces fluency, Bengali enhances it)
- Falsification: If metric synthesis creates irreconcilable conflicts

**Step 3: Multi-Metric Scores → Scalable Cultural Competence Assessment**
- Mechanism: Hierarchical aggregation enables cross-cultural comparison across 100+ cultures vs current 10-22 limits
- Evidence: CultDiff (2025) revealed significant disparities across 10 countries; proposed approach extends to 100+ via KG automation
- Falsification: If automated test cases lack cultural appropriateness (expert validation < 90%)

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | MakiEval (2025) | Wikidata queries scaled to 400+ languages automatically | Strong |
| Step1 → Step2 | CRaFT (2025) | 4-metric framework (Fluency, Deviation, Consistency, Adaptation) validated across 3 languages | Strong |
| Step2 → Step3 | CultDiff (2025) | Fine-grained analysis revealed T2I models fail to generate cultural artifacts for underrepresented regions | Strong |
| Step2 → Step3 | CARB (2025) | 10 cultures × 4 domains evaluation identified spurious correlations | Medium |

**Key Tension:**
- **Tension:** CRaFT (2025) shows cultural awareness in LLMs "emerges through linguistic framing" (not intrinsic), but hypothesis assumes KG-driven test generation transfers from linguistic to cultural domains without loss of nuance
- **Resolution:** Hybrid approach addresses this - KG automation for scalability + expert validation (5 cultural organizations, 10% sample) for quality assurance ensures cultural appropriateness

### 1.4 Key Assumptions

1. **KG Completeness Assumption:** Wikidata and ConceptNet contain ≥50 cultural entities per target culture
   - Evidence: MakiEval (2025) validated Wikidata coverage for 400+ languages
   - Consequence if violated: Annotation effort increases for sparse cultures; fallback to human-in-the-loop required

2. **Query Template Generalizability:** SPARQL query templates generalize across cultural domains (food, architecture, symbols, festivals)
   - Evidence: Wikidata schema supports structured queries across entity types
   - Consequence if violated: Per-domain template customization required, reducing scalability

3. **Metric Synthesis Validity:** Hierarchical aggregation (weighted average) preserves individual framework strengths
   - Evidence: CRaFT, CultDiff, CARB metrics independently validated in 2025 publications
   - Consequence if violated: Overall Cultural Competence Score loses interpretability; must revert to individual metrics

4. **Expert Validation Feasibility:** 5 diverse cultural organizations can validate 10% test case sample within 3 months
   - Evidence: Community-centered approaches demonstrated in Ghosh et al. (2024) "Do Generative AI Output Harm"
   - Consequence if violated: Validation delays deployment timeline; may need to reduce culture count in pilot

5. **AI System API Stability:** Target AI systems maintain stable APIs for automated testing
   - Evidence: Industry standard REST/GraphQL APIs with rate limiting (OpenAI, Anthropic, Stability AI)
   - Consequence if violated: Manual testing required for unstable systems, reducing automation advantage

6. **Consistent Metric Implementation:** CRaFT, CultDiff, CARB metrics implementable with consistent scoring
   - Evidence: Published methodologies with pseudo-code/equations in source papers
   - Consequence if violated: Cross-framework comparison becomes unreliable; must validate metric alignment

### 1.5 Scope & Boundaries

**Applies to:**
- Text-to-image models (Stable Diffusion, DALL-E, Midjourney), large language models (GPT, Claude, Gemini), vision models generating cultural content
- Cultures with ≥50 entities in Wikidata/ConceptNet (estimated 100-150 cultures globally)
- Cultural artifacts observable in generated outputs (food, architecture, clothing, symbols, festivals)

**Does NOT apply to:**
- Audio/speech models (different modality not covered by visual/text metrics)
- Highly specialized cultural practices lacking KG documentation (oral traditions, spiritual ceremonies)
- Cultures with <50 KG entities (requires human-in-the-loop, not automated)
- Real-time conversational AI (latency constraints incompatible with multi-metric evaluation)

**Known Limitations:**
- KG Western bias may propagate to test case distribution (more test cases for well-represented cultures)
- Metric synthesis weights (30/25/25/20) are proposed based on domain conventions, not empirically optimized for cultural evaluation
- Phased rollout delays full 100+ culture coverage to Year 2+ (pilot with 20 cultures in Year 1)
- Expert validation adds coordination overhead (3-month partnership establishment)

### 1.6 Testable Predictions

**Primary Prediction:**
**P1 (Annotation Effort Scalability):** If KG-driven test generation is applied to evaluate 20 cultures, then annotation effort will be <20% of manual annotation baseline (CRaFT: 3 languages, CultDiff: 10 countries manual setup)

*Measurement:*
- Annotation hours per culture: KG approach vs manual baseline
- Success threshold: KG annotation hours < 20% of manual baseline hours
- Statistical test: Paired comparison with 95% confidence interval

*Basis:*
MakiEval (2025) demonstrated O(log n) scaling for multilingual test generation via Wikidata; hypothesis transfers this to cultural domain.

*Success Criteria for Phase 2B:*
- Primary: Annotation effort reduction ≥ 80% (p < 0.05)
- Falsification: Annotation effort reduction ≤ 30% triggers hypothesis rejection

**Secondary Predictions:**
**P2 (Metric Correlation Validation):** If hierarchical metric synthesis is applied, then Cultural Competence Score (Level 3) will correlate r > 0.8 with individual framework scores (CRaFT, CultDiff, CARB) across 20 pilot cultures

*Measurement:* Pearson correlation coefficient between L3 aggregate score and L1 individual metrics
*Success threshold:* r > 0.8 (strong positive correlation)

**P3 (Expert Validation Quality):** If hybrid validation (auto + expert) is deployed, then test case cultural appropriateness will achieve >90% approval rate per cultural expert review (10% sample per culture)

*Measurement:* Expert rating (1-5 scale: 1=culturally inappropriate, 5=highly appropriate) on random 10% sample
*Success threshold:* Mean rating ≥ 4.5 (90% threshold on 5-point scale)

**Falsification Criteria:**
The hypothesis will be **REJECTED** if any occur:

1. **Primary Failure:** Annotation effort reduction ≤ 30% (KG automation provides minimal advantage vs manual approaches)

2. **Mechanism Failure:** Cultural Competence Score correlation r < 0.6 with individual metrics (metric synthesis loses validity)

3. **Quality Failure:** Expert validation approval rate < 75% (automated test cases lack cultural appropriateness)

4. **Baseline Failure:** KG approach performs worse than trivial baseline (e.g., random cultural artifact selection)

### 1.7 SOTA Baseline (Optional - If SOTA Comparison Mode)

**Not applicable** - This hypothesis targets absolute scalability validation (O(log n) vs O(n)), not performance improvement over SOTA methods. Comparison baselines are methodological (manual annotation effort) rather than performance benchmarks.

### 1.8 Statistical Verification Design

**Sample Size Calculation:**
- Pilot study: 20 cultures (phased rollout)
- Test cases per culture: 50-100 (dependent on KG entity count)
- Total test cases: 1000-2000 for pilot phase

**Statistical Tests:**
1. **Annotation Effort Comparison:**
   - Method: Paired t-test comparing KG annotation hours vs manual baseline hours across 20 cultures
   - Significance level: α = 0.05 (one-tailed)
   - Report format: Mean difference (hours), 95% CI, Cohen's d, p-value

2. **Metric Correlation Validation:**
   - Method: Pearson correlation between L3 aggregate and L1 individual scores
   - Significance level: α = 0.05
   - Report format: r coefficient, 95% CI, p-value

3. **Expert Validation Quality:**
   - Method: One-sample t-test comparing mean expert rating vs threshold (4.5)
   - Sample: 10% random sample per culture (100-200 test cases total)
   - Report format: Mean rating, 95% CI, p-value

**Power Analysis:**
- Minimum effect size (Cohen's d): 0.8 (large effect)
- Statistical power: 0.8
- Required cultures for full study: n ≥ 30 (pilot: 20 with relaxed power 0.7)

---

## 2. Contribution Summary

**Theoretical Contribution:**
- **Symbolic-Neural Bridge:** First framework to bridge symbolic cultural knowledge (knowledge graphs) with neural AI evaluation (LLM/T2I assessment), demonstrating how structured cultural metadata can guide scalable AI system testing
- **Cultural Competence Construct:** Formalizes "cultural competence" as measurable multi-dimensional construct (representation, quality, fluency, deviation) enabling quantitative cross-cultural comparison
- **Scalability Theory:** Provides theoretical model for O(log n) vs O(n) scaling in cultural evaluation through knowledge graph automation

**Methodological Contribution:**
- **Automated Test Case Generation Pipeline:** Novel pipeline combining SPARQL queries (entity extraction) + template instantiation (prompt generation) + hybrid validation (expert QA), reducing human annotation bottleneck from O(n) to O(log n)
- **Hierarchical Metric Synthesis:** Unified evaluation protocol synthesizing multiple framework metrics (CRaFT's 4 metrics, CultDiff's disparity, CARB's coverage) through 3-level hierarchy preserving individual interpretability while enabling aggregate comparison
- **Hybrid Validation Protocol:** Integration of automated KG generation with expert validation (5 cultural organizations, 10% sample) balancing scalability and quality assurance

**Practical Contribution:**
- **100+ Culture Evaluation Capability:** Enables AI developers to evaluate cultural performance across 100+ cultures vs current 10-22 limits (CultDiff: 10 countries, CARB: 10 cultures, CRaFT: 3 languages)
- **Actionable Cultural Performance Reports:** Provides per-culture performance scores, disparity analysis, and comparison with baselines enabling targeted improvements
- **Integration with Existing Frameworks:** Plugin architecture compatible with HELM (holistic evaluation) and CUBE (cultural competence benchmark) enabling adoption without infrastructure replacement

**Comparison to Current State:**
- Baseline: Manual annotation (CRaFT: 3 languages, CultDiff: 10 countries, CARB: 10 cultures)
- Proposed: Automated KG-driven evaluation (20 → 100+ cultures)
- Improvement: 10x culture coverage, 80% annotation effort reduction, unified multi-metric framework

---

## 3. Key Related Work

**Foundation Work:**
- **MakiEval (Zhao et al., 2025):** Wikidata-based multilingual evaluation framework - Primary inspiration for KG-driven scalability; demonstrated automatic test generation for 400+ languages using SPARQL queries. *Relation: Methodology transfer from linguistic to cultural domain*

- **CRaFT (Hossain & Afli, 2025):** Explanation-based evaluation with 4 interpretable metrics (Cultural Fluency, Deviation, Consistency, Linguistic Adaptation) - Foundation for metric design. *Relation: Metric framework synthesis component*

**Methodology Sources:**
- **CultDiff (Bayramli et al., 2025):** Fine-grained disparity analysis across 10 countries for T2I models; revealed cultural artifact generation failures. *Relation: Disparity analysis methodology*

- **CARB (Zhang et al., 2025):** 10 cultures × 4 domains evaluation identifying spurious correlations. *Relation: Domain coverage approach*

**Comparison Baselines:**
- **google-research-datasets/cube:** CUBE benchmark for cultural competence in T2I models. *Relation: Comparison baseline for evaluation quality*

- **stanford-crfm/helm:** Holistic evaluation framework with cultural alignment proposals (Issue #3568). *Relation: Integration target via plugin architecture*

**Cross-Domain Inspiration:**
- **Wikidata Multilingual Ontology:** Structured knowledge base with 400+ language coverage and SPARQL query interface. *Relation: Cross-domain transfer - linguistic diversity → cultural diversity*

- **ConceptNet 5:** Common-sense knowledge graph linking concepts across cultures. *Relation: Fallback KG source for cultural concept extraction*

**Related Benchmarks:**
- BBQ (Bias Benchmark for QA), CulturePark (cultural diversity dataset), GlobalBias (intersectional biases), CCUB (Cross-Cultural Understanding Benchmark) - Existing cultural bias benchmarks limited to 6-22 cultures without automated generation

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence - KG Completeness):**
"Wikidata and ConceptNet contain ≥50 cultural entities per target culture (20 pilot cultures)"
- Verification: SPARQL query count per culture
- Success: All 20 pilot cultures have ≥50 entities
- Experiment: Query 20 cultures (diverse geographic distribution) and count entities per domain (food, architecture, symbols, festivals)

**SH2 (Mechanism - Test Case Quality):**
"KG-driven test cases achieve ≥90% cultural appropriateness per expert validation"
- Verification: Expert rating (5-point scale) on 10% random sample
- Success: Mean rating ≥ 4.5 across 5 cultural organizations
- Experiment: Generate 50-100 test cases per culture, validate 10% sample with cultural experts

**SH3 (Comparison - Scalability Advantage):**
"KG approach reduces annotation effort by ≥80% vs manual baseline (CRaFT, CultDiff, CARB)"
- Verification: Annotation hours per culture comparison
- Success: KG hours < 20% of manual baseline hours
- Experiment: Time KG query development + template instantiation + validation vs manual annotation for same 20 cultures

### Readiness Checklist

- [x] Core hypothesis statement precise (Under C, if X, then Y because Z)
- [x] Variables operationalized with measurement methods
- [x] Causal mechanism decomposed with evidence (3-step chain)
- [x] Key assumptions stated with consequences if violated
- [x] Testable predictions with quantitative thresholds
- [x] Falsification criteria specified
- [x] Scope and limitations defined
- [x] Related work mapped with relation types
- [x] Contributions categorized (theoretical, methodological, practical)
- [x] Sub-hypothesis preview generated (SH1-SH3)

### Open Questions

1. **Metric Weight Optimization:** Current hierarchical weights (30/25/25/20) are based on domain conventions - should these be empirically optimized via cross-validation on pilot data?

2. **KG Bias Quantification:** How to measure and mitigate Western bias in Wikidata/ConceptNet entity distribution? Consider entropy-based diversity metric?

3. **Expert Validation Protocol:** What specific criteria should cultural experts use for 5-point appropriateness rating? Need standardized rubric.

4. **Temporal Dynamics:** Cultural artifacts evolve over time - should KG queries include temporal filters (e.g., traditional vs contemporary clothing)? How to handle cultural evolution?

5. **Cross-Cultural Comparison Fairness:** When comparing Cultural Competence Scores across cultures, should we normalize by KG entity count (resource-normalized comparison)?

---

*Generated using YouRA Research Phase 2A Extended Workflow (Focused)*
*2026-02-06*
