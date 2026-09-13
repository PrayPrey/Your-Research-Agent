# Phase 2A Extended: ImmuneLM Hypothesis Clarification

**Date:** 2026-02-06
**Author:** Pray
**Source Round:** Round 1 (02a_round_1_discussion.md)
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-ImmuneLM-001
**Confidence Level:** 0.85

**Main Hypothesis:**
An immune-inspired two-tier defense architecture for LLM jailbreak detection, combining fast single-turn concept activation screening (Tier 1 - innate immunity analog) with LSTM-based conversational state tracking over multiple turns (Tier 2 - adaptive immunity analog), will achieve statistically significant detection improvement (≥20% ASR reduction) on multi-turn jailbreak attacks compared to single-turn baselines, while maintaining acceptable false positive rates (≤5%) and latency (≤500ms per turn).

**Alternative Hypothesis (H0):**
Single-turn concept activation detection (JBShield baseline) achieves equivalent or superior multi-turn jailbreak detection performance compared to the proposed two-tier architecture with LSTM conversational memory, making the additional complexity unjustified.

### 1.2 Variables

| Variable Type | Variable Name | Operationalization | Measurement Method | Expected Range |
|---------------|---------------|-------------------|-------------------|----------------|
| **Independent (IV1)** | per_turn_concept_activation | JBShield-style toxic+jailbreak concept activation vectors extracted per conversation turn | Linear probe on LLM hidden states → R^d vector (d=toxic_dim+jailbreak_dim) | Continuous [0,1]^d |
| **Independent (IV2)** | conversational_state_sequence | LSTM hidden state tracking concept activation evolution across turns | LSTM(h_{t-1}, [concept_t; embedding_t]) → h_t ∈ R^{64-128} | Continuous R^{64-128} |
| **Independent (IV3)** | attack_pattern_memory | Learned library of multi-turn attack state transition patterns from RACE/MM-ART/PyRIT | Pattern matching distance: min_i ||h_t - pattern_i|| | Discrete (pattern index) + Continuous (distance) |
| **Dependent (DV1)** | multi_turn_attack_detection_rate | Proportion of multi-turn attacks correctly flagged before successful jailbreak | ASR_baseline - ASR_ImmuneLM / ASR_baseline | [0, 1] (target: ≥0.20) |
| **Dependent (DV2)** | false_positive_rate | Proportion of benign conversations incorrectly flagged as attacks | FP / (FP + TN) on benign dialogue datasets | [0, 1] (target: ≤0.05) |
| **Controlled (CV1)** | conversation_turn_count | Number of turns in conversation | Fixed evaluation ranges: 3-5, 6-10, 11-20 turns | Discrete {3-20} |
| **Controlled (CV2)** | single_turn_baseline_performance | JBShield per-turn detection accuracy | JBShield replication on single-turn attacks | 0.95 (from JBShield paper) |
| **Controlled (CV3)** | LLM_version | Target LLM model version | Version pinning (e.g., GPT-4-0613, Llama-3.1-70B) | Categorical |

### 1.3 Causal Mechanism

**Causal Chain:**

```
Multi-turn jailbreak attack (RACE/MM-ART)
    ↓
[Turn 1] Benign or weakly suspicious prompt → Tier 1: Low concept activation → Pass
    ↓
[Turn 2-N] Gradual semantic drift toward harmful intent
    ↓
Tier 2: LSTM detects concept activation trajectory deviates from benign patterns
    ↓
Pattern library matching: trajectory similarity to known attack state machines (RACE patterns)
    ↓
Alert threshold exceeded → Conversation flagged BEFORE turn N jailbreak success
    ↓
**Detection before compromise** (vs. single-turn detection: only flags turn N when already harmful)
```

**Theoretical Justification:**

1. **Stateless Gap**: Single-turn defenses treat each prompt independently → cannot detect gradual semantic manipulation across turns
2. **Immune System Analogy**: Biological two-tier architecture evolved to handle temporal threats:
   - **Innate (Tier 1)**: Fast pattern recognition receptors for immediate threats
   - **Adaptive (Tier 2)**: Memory-based system tracking pathogen evolution over time
3. **LSTM Sequential Modeling**: Proven in cybersecurity IDS for modeling attack progression in network traffic (Hiari et al. 2025)

**Evidence for Causal Links:**

- **Link 1 (Attacks cause semantic drift)**: RACE paper demonstrates 82% ASR on GPT-4 via attack state machine with deliberate semantic progression from benign→harmful over turns
- **Link 2 (Drift evades single-turn detection)**: MM-ART shows 71% more vulnerable after 5 turns → single-turn defenses miss intermediate turns
- **Link 3 (LSTM captures temporal patterns)**: Hiari et al. (2025) IDS achieves high DoS detection via LSTM modeling of sequential network features
- **Link 4 (Concept activation informative)**: JBShield achieves 95% single-turn accuracy using toxic+jailbreak concept vectors → strong signal exists

**Key Tension:**

**Phase 0 Validation Dependency**: Assumes per-turn concept activation vectors contain sufficient temporal signal for LSTM learning. If correlation between concept drift and attack progression <0.6, hybrid approach (concept vectors + raw turn embeddings) required. Early validation experiment necessary before full implementation.

### 1.4 Key Assumptions

**Testable Assumptions:**

1. **Concept-Attack Correlation (CRITICAL)**: Per-turn concept activation trajectories correlate ≥0.6 with RACE attack state progressions
   - Test: Phase 0 validation experiment on RACE dataset
   - Fallback: Hybrid LSTM input [concept_vectors; turn_embeddings]

2. **LSTM Temporal Capacity**: LSTM with 64-128 hidden units can model 3-10 turn dependencies in conversational attacks
   - Evidence: Standard LSTM capacity for sequential tasks (Hochreiter & Schmidhuber 1997), IDS applications
   - Test: Ablation study on hidden dimension vs. turn count

3. **Generalization from Automated to Human Attacks**: Patterns learned from automated red teaming (RACE, PyRIT) transfer to human adversarial attacks
   - Test: Human red team evaluation in Phase 4
   - Mitigation: Include human-generated attacks in training set

4. **Latency Feasibility**: Combined Tier 1 concept extraction + Tier 2 LSTM inference achievable ≤500ms on standard GPU
   - Test: Latency profiling in Phase 3 implementation
   - Constraint: Acceptable for chatbot use case (human typing time ~2-5s between turns)

5. **LLM Representation Stability**: Concept directions remain stable within LLM version (e.g., GPT-4-0613)
   - Mitigation: Version pinning + retraining protocol on version updates
   - Test: Cross-version concept drift measurement

**Untestable Assumptions (Known Limitations):**

6. **No Adaptive Adversary**: Assumes attackers do not have white-box access to ImmuneLM architecture to craft evasive attacks
   - Future Work: Adversarial robustness evaluation in Phase 5

### 1.5 Scope & Boundaries

**Applies To:**
- Multi-turn conversational LLM systems (chatbots, assistants)
- Jailbreak attacks with 3-20 turn interactions
- Text-based attacks (not multimodal)
- Defense deployment AFTER LLM inference (external guardrail)

**Does NOT Apply To:**
- Single-turn jailbreaks (JBShield baseline sufficient)
- Prompt injection attacks on retrieval systems (different threat model)
- Training-time backdoors or poisoning (not inference defense)
- Multimodal attacks (image/audio jailbreaks)

**Known Boundaries:**
- **Minimum Turn Count**: Requires ≥3 turns for LSTM temporal pattern detection
- **Maximum Latency Budget**: Chatbot applications with <200ms hard latency requirements incompatible
- **LLM Version Lock-in**: Requires retraining on major LLM updates (e.g., GPT-4 → GPT-5)

### 1.6 Testable Predictions

**Primary Prediction (P1):**
If ImmuneLM (Tier 1 + Tier 2) is deployed against RACE benchmark multi-turn attacks (baseline ASR: 82%), then ASR will reduce to ≤66% (≥20% relative reduction), while maintaining ≤5% false positive rate on benign multi-turn dialogues (e.g., DailyDialog, PersonaChat).

**Secondary Predictions:**

**P2 (Temporal Sensitivity):**
If conversation turn count increases from 3→10 turns, then ImmuneLM detection advantage over single-turn baseline increases (single-turn advantage diminishes as attack becomes more gradual).

**P3 (Hybrid Feature Robustness):**
If Tier 1 concept extraction error rate increases experimentally (simulated via noise injection), then hybrid LSTM input [concept; embeddings] maintains detection performance within 10% of clean baseline, while concept-only degrades >20%.

**P4 (Attack Diversity Generalization):**
If ImmuneLM is trained on diverse attack sources (RACE + MM-ART + PyRIT + human red team), then zero-shot detection rate on held-out human adversarial attacks ≥70% (vs. ≤50% for single-source training).

**P5 (Latency Constraint):**
If ImmuneLM is profiled on NVIDIA A100 GPU, then 95th percentile per-turn latency ≤500ms for conversations ≤20 turns.

**Falsification Criteria:**

ImmuneLM hypothesis is **FALSIFIED** if any of:
1. Phase 0 validation shows concept-attack correlation <0.4 AND hybrid approach correlation <0.5
2. ASR reduction on RACE <10% (insufficient improvement over baseline)
3. False positive rate >10% on benign dialogues (unusable in production)
4. Human adversarial evaluation shows <50% detection (fails to generalize)
5. Latency >1000ms (violates usability constraint)

### 1.7 SOTA Baseline (Comparison Mode)

**Baseline System:** JBShield (Zhang et al. 2025)
- **Method**: Linear probe concept activation on toxic+jailbreak dimensions
- **Performance**: 95% accuracy on single-turn jailbreak detection
- **Limitation**: Stateless, does not model multi-turn context

**Comparison Strategy:**
1. **Tier 1 Replication**: Replicate JBShield per-turn detection as ImmuneLM Tier 1 → verify 95% single-turn accuracy match
2. **Multi-Turn Extension**: Compare JBShield applied per-turn independently vs. ImmuneLM Tier 1+2 on RACE multi-turn benchmark
3. **Metric**: ASR reduction relative to JBShield single-turn baseline

**Expected Outcome:** JBShield flags individual harmful turns (typically final turn when jailbreak succeeds), ImmuneLM flags conversation earlier by detecting drift across preceding turns.

**Alternative Baselines:**
- **KG-Guard** (symbolic knowledge graph multi-turn defense): Different methodology (symbolic vs. subsymbolic), comparison on shared benchmark if available
- **Perplexity-based filters**: Simple baseline using LLM perplexity spikes as anomaly detection

### 1.8 Statistical Verification Design

**Experimental Design:** Randomized controlled trial with stratified sampling

**Sample Size Calculation:**
- **Attack dataset**: RACE (N≈500 multi-turn attack trajectories), MM-ART (N≈300), PyRIT synthetic (N≈1000), Human red team (N≈100) → Total N≈1900 attacks
- **Benign dataset**: DailyDialog (N≈1000 multi-turn dialogues), PersonaChat (N≈500) → Total N≈1500 benign
- **Power analysis**: α=0.05, β=0.20 (80% power), effect size d=0.5 (medium) → n≈64 per group (well-exceeded)

**Train/Val/Test Split:**
- **Train**: 60% (RACE, MM-ART, PyRIT, human red team, benign dialogues)
- **Validation**: 20% (hyperparameter tuning: LSTM hidden dim, learning rate, threshold)
- **Test**: 20% (final evaluation, held-out human attacks)

**Stratification:** By turn count (3-5, 6-10, 11-20), attack type (RACE state machine, MM-ART multilingual, PyRIT automated, human creative)

**Statistical Tests:**
1. **Primary**: Paired t-test comparing ASR_baseline vs. ASR_ImmuneLM on same attack set (H0: μ_diff ≤ 0, H1: μ_diff > 0)
2. **Secondary**: McNemar's test for detection success/failure contingency (paired categorical data)
3. **Robustness**: Bootstrap confidence intervals (1000 resamples) for ASR reduction estimate
4. **Significance threshold**: p < 0.05 (Bonferroni correction if multiple comparisons)

**Confound Controls:**
- **LLM version**: Pin to specific checkpoint (e.g., GPT-4-0613) for all experiments
- **Attack generation randomness**: Fixed random seed for PyRIT synthetic attacks
- **Human evaluator bias**: Blind evaluation (evaluators unaware of defense system)

**Reproducibility:**
- Public code release (GitHub)
- Model checkpoints (HuggingFace)
- Dataset construction scripts
- Random seeds documented

---

## 2. Contribution Summary

### 2.1 Theoretical Contributions

**TC1: Stateful Defense Framework for LLM Security**
- **What**: Formalization of stateless vs. stateful defense gap as architectural deficiency in current LLM guardrails
- **Why Novel**: First explicit framing of multi-turn jailbreaks as temporal semantic drift problem requiring memory-based defenses
- **Impact**: Provides theoretical foundation for future conversational LLM security research beyond point-in-time detection

**TC2: Cross-Domain Immune System Transfer Theory**
- **What**: Principled application of biological two-tier immune architecture (innate + adaptive) to LLM defense design
- **Why Novel**: First use of immune system as architectural blueprint for LLM security (vs. ad-hoc metaphor)
- **Impact**: Opens new research direction in bio-inspired LLM safety mechanisms

**TC3: Temporal Attack Modeling Framework**
- **What**: Conceptualization of multi-turn attacks as state machine trajectories in semantic space, with LSTM modeling of conversational evolution
- **Why Novel**: Shifts focus from static prompt features to dynamic conversational state transitions
- **Impact**: Enables rigorous analysis of attack progression dynamics and defense intervention points

### 2.2 Methodological Contributions

**MC1: ImmuneLM Two-Tier Architecture**
- **What**: Hybrid defense combining JBShield concept activation (Tier 1) with LSTM conversational memory (Tier 2) and attack pattern library
- **Why Novel**: First LSTM-based multi-turn jailbreak detection system, first integration of concept activation with temporal modeling
- **Implementation**: PyTorch/TensorFlow, 1-2 GPU training, <500ms inference
- **Impact**: Provides reusable architecture for chatbot security deployment

**MC2: Hybrid Feature Robustness Approach**
- **What**: LSTM input combining [concept_activation_vectors; turn_embeddings] for error tolerance
- **Why Novel**: Addresses error propagation from Tier 1→Tier 2 via parallel information flow
- **Implementation**: Concatenated feature vector with learned fusion weights
- **Impact**: Demonstrates engineering practice for multi-stage ML system robustness

**MC3: Semantic Drift Detection Mechanism**
- **What**: LSTM hidden state trajectory analysis to identify benign→harmful conversational evolution
- **Why Novel**: First application of sequential anomaly detection to LLM conversation safety
- **Implementation**: Pattern matching against attack state machine library with distance thresholding
- **Impact**: Enables proactive defense before jailbreak completion (vs. reactive single-turn flagging)

### 2.3 Practical Contributions

**PC1: Multi-Turn Attack ASR Reduction**
- **What**: ≥20% relative ASR reduction on RACE/MM-ART benchmarks vs. single-turn baseline
- **Why Valuable**: Directly addresses critical industry need for chatbot safety (OpenAI, Anthropic, Microsoft deployments)
- **Impact**: Deployable defense for production LLM systems with conversational interfaces

**PC2: Automated Red Teaming Integration**
- **What**: Practical methodology for constructing attack pattern libraries from PyRIT/DeepTeam/RACE
- **Why Valuable**: Bridges research (academic benchmarks) and industry practice (automated testing)
- **Implementation**: Pipeline for automated attack generation → pattern extraction → library updates
- **Impact**: Enables continuous defense improvement as new attacks discovered

**PC3: Production-Ready Implementation**
- **What**: MEDIUM difficulty implementation (1-2 GPUs, standard DL frameworks), <500ms latency, ≤5% FPR
- **Why Valuable**: Feasible for research labs and industry teams without specialized infrastructure
- **Resources**: Doctoral student + 6 months ≈ $50K research cost estimate
- **Impact**: Lowers barrier to adoption for multi-turn LLM defense

---

## 3. Key Related Work

### 3.1 Foundation (Direct Extensions)

**[F1] JBShield (Zhang et al. 2025)** | [Paper](https://www.semanticscholar.org/paper/80a1960dc99a2424273cf38de57f05bf4e896e42)
- **Relation**: ImmuneLM Tier 1 directly extends JBShield concept activation to multi-turn setting
- **What We Adopt**: Toxic+jailbreak concept extraction via linear probing on LLM hidden states, 95% single-turn baseline
- **What We Add**: Tier 2 LSTM temporal modeling, attack pattern memory, conversational state tracking
- **Difference**: JBShield is stateless (per-prompt), ImmuneLM is stateful (per-conversation)

**[F2] RACE (Ying et al. 2025)** | [Paper](https://www.semanticscholar.org/paper/c57b3e62b75bf4eed451ff702bca610384563cd7)
- **Relation**: Defines threat model (attack state machines, 82% ASR on GPT-4o1) that ImmuneLM defends against
- **What We Adopt**: Attack state machine patterns for Tier 2 pattern library construction
- **What We Add**: Defense mechanism leveraging RACE patterns for detection (vs. RACE focus on attack generation)
- **Difference**: RACE is offensive red teaming, ImmuneLM is defensive guardrail

**[F3] MM-ART (Singhania et al. 2025)** | [Paper](https://www.semanticscholar.org/paper/4f1fcea4659d0b8d4f853390782fac03451e6021)
- **Relation**: Quantifies multi-turn vulnerability gap (71% more vulnerable after 5 turns) motivating ImmuneLM
- **What We Adopt**: Multi-turn attack dataset for evaluation, multilingual attack patterns
- **What We Add**: Defense system addressing identified vulnerability
- **Difference**: MM-ART identifies problem, ImmuneLM proposes solution

### 3.2 Methodological Comparisons

**[M1] KG-Guard (Symbolic Knowledge Graph Defense)** | Status: Identified in novelty check
- **Relation**: Alternative multi-turn defense approach (symbolic vs. ImmuneLM's subsymbolic)
- **Approach**: Constructs knowledge graphs from conversation, detects inconsistencies/policy violations symbolically
- **Difference**: ImmuneLM uses LSTM hidden states (continuous semantic space) vs. KG-Guard discrete graph structures
- **Trade-off**: KG-Guard potentially more interpretable, ImmuneLM potentially more robust to paraphrasing/obfuscation

**[M2] Perplexity-based Anomaly Detection** | Simple baseline
- **Relation**: Alternative anomaly detection approach using LLM perplexity spikes
- **Approach**: Flags unusual perplexity patterns in conversation
- **Difference**: ImmuneLM uses concept activation (semantically grounded) vs. perplexity (surface statistics)
- **Expected Performance**: Perplexity likely insufficient (jailbreaks can be fluent), ImmuneLM semantic grounding stronger

### 3.3 Cross-Domain Inspirations

**[CD1] Immune System Two-Tier Architecture (Wang et al. 2024)** | [Paper](https://www.semanticscholar.org/paper/7fea24cb1e201b9258257b2ae6d0a1ea17d4b59e)
- **Relation**: Biological blueprint for ImmuneLM architecture
- **What We Transfer**: Innate (fast PRR detection) + Adaptive (memory-based learning) architectural principle
- **How Applied**: Tier 1 (innate) = fast concept activation per turn, Tier 2 (adaptive) = LSTM memory + attack pattern library
- **Validation**: Evolutionary optimization over billions of years suggests robustness of two-tier design

**[CD2] LSTM-based IDS (Hiari et al. 2025)** | [Paper](https://www.semanticscholar.org/paper/627f6b09b512e8acc0d69b85ff8ab1a92e04da5b)
- **Relation**: Proven LSTM sequential modeling for attack detection in cybersecurity
- **What We Transfer**: LSTM architecture for temporal pattern recognition in sequential threat data
- **How Applied**: LSTM models conversational state evolution (analogous to network traffic evolution)
- **Validation**: High DoS attack detection demonstrates LSTM capacity for temporal threat modeling

### 3.4 Industry Context

**[I1] OpenAI External Red Teaming (2025)** | [Paper](https://www.semanticscholar.org/paper/4329ac5ac885b9bfe6510d98cfbde77806f6e82e)
- **Relation**: Industry validation of red teaming importance, but manual process
- **Gap ImmuneLM Addresses**: Automated multi-turn defense vs. manual red team evaluation
- **Deployment Relevance**: OpenAI/Anthropic chatbots are primary use case for ImmuneLM

**[I2] Microsoft 100 Products Red Teaming (2025)** | [Paper](https://www.semanticscholar.org/paper/165c70171847d0e8b283f93e71c01a2e4d253714)
- **Relation**: Lessons learned emphasize automation + human element necessity
- **What We Adopt**: Hybrid automated (PyRIT patterns) + human red team evaluation in ImmuneLM design
- **Validation**: Industry scale (100+ products) validates multi-turn attack prevalence

**[I3] PyRIT / DeepTeam (Exa Search Results)** | [PyRIT](https://www.youtube.com/watch?v=cEHTxmpAgjA), [DeepTeam](https://github.com/confident-ai/deepteam)
- **Relation**: Open-source infrastructure for attack generation and evaluation
- **What We Adopt**: Attack pattern library construction, multi-turn conversation simulation
- **Integration**: ImmuneLM evaluation pipeline uses PyRIT/DeepTeam for automated testing

---

## 4. Phase 2B Readiness

### 4.1 Decomposition Preview

**SH1 (Existence - Phase 0 Validation):**
Per-turn concept activation vectors (toxic+jailbreak dimensions) extracted from LLM hidden states during RACE multi-turn attacks correlate ≥0.6 with attack state progression, providing sufficient temporal signal for LSTM learning.

**SH2 (Mechanism - Core Architecture):**
LSTM with 64-128 hidden units, trained on hybrid input [concept_activation_vectors; turn_embeddings] from diverse attack sources (RACE, MM-ART, PyRIT, human red team), learns to distinguish multi-turn attack state trajectories from benign conversational drift.

**SH3 (Comparison - Performance Validation):**
ImmuneLM (Tier 1 + Tier 2) achieves ≥20% relative ASR reduction on RACE multi-turn benchmark compared to JBShield single-turn baseline, while maintaining ≤5% false positive rate on benign dialogues and ≤500ms per-turn latency.

### 4.2 Readiness Checklist

**Research Foundations:**
- ✅ Target research gap clearly identified (Gap 2: Multi-Turn & Adaptive Attack Defenses)
- ✅ Phase 1 evidence comprehensively gathered (5/5 sources from RACE, MM-ART, JBShield, DeepTeam, PyRIT)
- ✅ Cross-domain inspiration validated (Immune system, IDS LSTM)
- ✅ Novelty confirmed via search (first immune-inspired + LSTM LLM defense)

**Hypothesis Clarity:**
- ✅ Variables operationalized (IV: concept activation, LSTM state, attack patterns; DV: ASR reduction, FPR)
- ✅ Causal mechanism articulated (semantic drift → LSTM detection → early flagging)
- ✅ Testable predictions defined (P1-P5 with quantitative thresholds)
- ✅ Falsification criteria specified (5 concrete failure conditions)

**Feasibility:**
- ✅ Implementation difficulty assessed (MEDIUM - acceptable)
- ✅ Resources estimated (1-2 GPUs, 6 months, $50K)
- ✅ Datasets identified (RACE, MM-ART, PyRIT, DailyDialog, PersonaChat)
- ✅ Baselines defined (JBShield replication, KG-Guard comparison)

**Refinement Quality:**
- ✅ Skeptic concerns addressed (5/5 flaws fixed: Phase 0 validation, hybrid features, human eval, robustness, latency)
- ✅ Anti-patterns checked (12/12 CLEAR)
- ✅ Confidence appropriate (0.85 - HIGH but not overconfident)

**Next Phase Preparation:**
- ✅ Sub-hypothesis decomposition previewed (SH1: existence, SH2: mechanism, SH3: comparison)
- ✅ Related work mapped (foundation, comparisons, cross-domain, industry)
- ✅ Contribution clarified (3 theoretical, 3 methodological, 3 practical)

### 4.3 Open Questions for Phase 2B

**Q1 (Architecture Details):**
Exact LSTM architecture hyperparameters (num_layers, hidden_dim, dropout) require Phase 2B ablation study planning. Ranges specified (64-128 hidden), but optimal configuration TBD.

**Q2 (Attack Pattern Library Construction):**
Algorithm for extracting and clustering attack state transition patterns from RACE/PyRIT needs detailed specification in Phase 2B verification experiments.

**Q3 (Tier 1-Tier 2 Integration):**
Operational decision logic for when Tier 2 overrides Tier 1 (or vice versa) requires Phase 2B protocol definition. Threshold tuning strategy needed.

**Q4 (Human Red Team Protocol):**
Sampling strategy for human adversarial evaluation (how many testers, attack constraints, success criteria) requires Phase 2B experimental design.

**Q5 (Deployment Scenario):**
Production integration architecture (API placement, batching strategy, fallback mechanisms) requires Phase 3 implementation planning but informs Phase 2B experiment design.

**Q6 (Multimodal Extension Path):**
Current scope is text-only; Phase 2B should consider future work roadmap for multimodal attacks (image/audio jailbreaks) to assess hypothesis extensibility.

---

**Phase 2A-Extended Complete** ✓

**Summary:** ImmuneLM hypothesis clarified with scientific rigor - variables operationalized, causal mechanism detailed, statistical design specified, contributions articulated, related work mapped. Ready for Phase 2B verification planning to decompose into testable sub-hypotheses (SH1: concept correlation validation, SH2: LSTM mechanism, SH3: performance comparison) with detailed experiment protocols.

**Confidence:** 0.85 (HIGH - all Skeptic concerns addressed, Phase 0 validation dependency acknowledged, falsification criteria clear)

**Next Step:** `/phase2b-planning` to develop verification roadmap with prioritized experiments and success criteria for each sub-hypothesis.

---

*Generated using YouRA Research Phase 2A Extended Workflow*
*2026-02-06*
