# Phase 2A Extended: Hypothesis Summary
# Hierarchical Compositional Attention with Dynamic Skill Routing

**Date:** 2026-02-06
**Hypothesis ID:** H1-HCADSR
**Confidence:** 0.82
**Status:** Ready for Phase 2B Verification Planning

---

## Executive Summary

This hypothesis proposes a three-level hierarchical attention architecture (primitive, composition, abstraction) combined with dynamic skill routing to achieve compositional generalization in mathematical reasoning. The core innovation is explicit compositional structure embedded in the attention mechanism, enabling models to solve problems requiring reasoning steps never seen during training. Target improvements: >60% accuracy on 5-7 step problems (trained on 2-3 steps) vs <40% baseline, and >70% on novel concept combinations vs <50% baseline.

---

## 1. Core Hypothesis Statement

**Main Hypothesis:**

A transformer architecture with three-level hierarchical compositional attention (primitive-level L1, composition-level L2, abstraction-level L3) combined with dynamic skill routing will achieve significantly improved compositional generalization in mathematical reasoning, specifically:
- **Depth Generalization:** >60% accuracy on 5-7 step problems (vs <40% baseline)
- **Breadth Generalization:** >70% accuracy on novel concept combinations (vs <50% baseline)
- **Mechanism:** Learning reusable primitives (L1), explicit composition operators (L2), and abstract transferable patterns (L3)

**Alternative (H0):** Standard flat-attention transformers achieve equivalent performance through scale alone, without requiring explicit compositional architectural structure.

---

## 2. Key Variables

**Independent:**
- Attention hierarchy depth (3 levels)
- Expert count per level (4-8)
- Composition operator types (sequence, branching, iteration via Gumbel-softmax)
- Training compositional splits (depth-based, breadth-based, abstraction-based)

**Dependent:**
- OOD compositional performance on OMEGA benchmark
- Depth generalization (5-7 steps trained on 2-3)
- Breadth generalization (novel concept combinations)
- Abstraction transfer (cross-domain accuracy)
- Attention interpretability (correlation with human reasoning)

**Controlled:**
- Model size (350M parameters)
- Training compute (1e21 FLOPs)
- Baseline architecture (standard transformer)
- Evaluation benchmark (OMEGA v1.0)

---

## 3. Causal Mechanism

```
Hierarchical Architecture
    ↓
L1 (Primitive): Learns reusable atomic operations (arithmetic, algebra, logic)
    ↓
L2 (Composition): Applies composition operators (sequence, branch, iterate) via Gumbel-softmax
    ↓
L3 (Abstraction): Identifies domain-general transferable patterns
    ↓
Dynamic Routing: Selects expert combinations based on compositional structure
    ↓
Novel Compositional Generalization (unseen depths + concept combinations)
```

**Evidence for Links:**
- **L1→Reusability:** Mueller & Linzen 2023 (depth > width for hierarchical generalization)
- **L2→Composition:** Wei et al. 2022 (CoT demonstrates step-by-step reasoning value)
- **L3→Transfer:** Cognitive psychology working memory hierarchy (cross-domain executive control)
- **Routing→Generalization:** Klinger 2023 CPG (1000x sample efficiency via modular composition)
- **Hierarchy→Sample Complexity:** Elmoznino 2024 (compositional representations reduce sample complexity)

**Key Tension:** Structured inductive biases vs emergent capabilities from scale. Zhang et al. 2025 show architecture matters (complexity control affects rule learning vs memorization).

---

## 4. Testable Predictions

**Primary (P1 - Depth Generalization):**
- Hierarchical model: >60% accuracy on 5-7 step problems (trained on 2-3 steps)
- Baseline: <40% accuracy
- Statistical test: Paired t-test, p<0.0125 (Bonferroni), effect size >15pp

**Secondary:**
- **P2 (Breadth):** >70% on novel combinations vs <50% baseline
- **P3 (Interpretability):** L2 attention correlation >0.7 with human reasoning steps
- **P4 (Abstraction):** >50% cross-domain transfer (arithmetic→algebra) without additional training

**Falsification Criteria:**
- Depth improvement ≤5pp (no architectural benefit)
- Breadth accuracy <55% (routing ineffective)
- L2 attention correlation <0.4 (hierarchy doesn't capture composition)
- Abstraction transfer <35% (L3 fails domain-general learning)
- 2x scaled baseline (700M) matches or beats hierarchical performance

---

## 5. Key Assumptions

1. **Primitive Independence:** Mathematical primitives learnable in isolation then composed
2. **Composition Sufficiency:** Sequence/branch/iterate operators adequately represent math reasoning
3. **Gumbel-Softmax Differentiability:** Sufficient gradient signal for discrete composition operators
4. **Routing Learnability:** MoE gating learns compositional structure (not spurious correlations)
5. **OMEGA Validity:** Compositional axis measures true compositionality (not confounds)
6. **Kim & Linzen Adaptability:** Linguistic compositional splits methodology adapts to math
7. **Gradient Flow Sufficiency:** Residual connections + layer-wise LR address 3-level hierarchy challenges

---

## 6. Scope & Boundaries

**Applies To:**
- Text-based mathematical reasoning (OMEGA, GSM8K, algebraic manipulation, logic)
- Problems with 2-7 reasoning steps
- Supervised learning with compositional structure annotations
- 100M-1B parameter models

**Does NOT Apply To:**
- Visual mathematical reasoning (diagrams, geometry figures)
- Open-ended mathematical creativity
- External knowledge retrieval tasks
- Problems requiring >10 reasoning steps
- Real-time constraint satisfaction (SAT solving)

**Known Limitations:**
- 4-5x computational cost vs baseline
- MEDIUM-HIGH implementation difficulty (6-8 months)
- Requires compositional structure annotations (1-2 months benchmark work)
- Gradient flow risks in deep hierarchies

---

## 7. Contributions

### Theoretical
- **Novel Framework:** First hierarchical attention specifically designed for mathematical compositionality with formal three-level structure
- **Sample Complexity Analysis:** Proof that hierarchical composition reduces sample complexity from O(k^d) to O(k+d) for k primitives, depth d
- **Connection to Prior Theory:** Architectural instantiation of Elmoznino 2024 compositionality properties

### Methodological
- **Architecture:** Three-level hierarchical attention with Gumbel-softmax composition operators and MoE routing
- **Training:** Compositional structure prediction auxiliary task + complexity-aware initialization
- **Evaluation:** Multi-dimensional generalization protocol (depth, breadth, abstraction) + interpretability analysis

### Practical
- **Performance:** Target 20-30% absolute improvement on OMEGA compositional axis (30-40% → 50-70%)
- **Interpretability:** Explicit attention levels for educational applications and verification tasks
- **Modularity:** Incremental skill addition and domain transfer without full retraining

---

## 8. Key Related Work

**Differentiation Table:**

| Work | Relation | Differentiation |
|------|----------|-----------------|
| **Altabaa 2025** (Latent Reasoning) | Most similar recent work | Attention hierarchy vs latent space; explicit compositional levels vs general recurrence |
| **Elmoznino 2024** (Compositionality Theory) | Theoretical foundation | Provides formal justification for hierarchical compositional design |
| **Mueller & Linzen 2023** (Depth > Width) | Architectural principle | Extends syntactic generalization to mathematical reasoning |
| **Zhang 2025** (Complexity Control) | Training methodology | Applies complexity-aware initialization to hierarchical architecture |
| **Klinger 2023** (CPG) | Modular composition | Neural attention hierarchy vs symbolic program synthesis |
| **Wei 2022** (Chain-of-Thought) | Composition design | L2 attention explicitly models CoT-style reasoning chains |
| **Kim & Linzen 2020** (Compositional Splits) | Evaluation methodology | Adapts linguistic compositional splits to mathematical reasoning |
| **Sun 2025** (OMEGA) | Evaluation benchmark | Primary target for compositional generalization evaluation |

**Cross-Domain:**
- **Baddeley & Hitch** (Working Memory): Three-level hierarchy blueprint (phonological loop → primitive, episodic buffer → composition, central executive → abstraction)
- **PFC Hierarchy** (Neuroscience): Dynamic routing inspiration from hierarchical cognitive control
- **Swin Transformer** (Vision): Validates hierarchical attention viability, adapts spatial to conceptual hierarchy

---

## 9. Phase 2B Decomposition Preview

**SH1 (Existence):** Architecture trains successfully with in-distribution performance ≥95% baseline + differentiable composition operators via Gumbel-softmax without gradient collapse

**SH2 (Mechanism):**
- L1 learns reusable primitive representations (>0.8 similarity across contexts)
- L2 captures compositional patterns (>0.7 correlation with human annotations)
- Dynamic routing activates novel expert combinations on OOD problems (>30% novel activations with >50% accuracy)

**SH3 (Comparison):**
- Outperforms flat attention by ≥20pp on depth generalization (>60% vs <40%)
- Outperforms Altabaa 2025 by ≥10pp on OMEGA compositional axis
- 350M hierarchical beats 700M scaled baseline by ≥5pp (structure > scale)

---

## 10. Phase 2B Readiness

**Ready:**
- [x] Core hypothesis clarified with quantitative predictions
- [x] Variables operationalized with measurement methods
- [x] Causal mechanism explicitly stated with evidence
- [x] Testable predictions with falsification criteria
- [x] Statistical design with power analysis
- [x] Baseline comparisons specified
- [x] Implementation pathway clear
- [x] Related work differentiation complete
- [x] Sub-hypothesis decomposition previewed

**Open Questions for Phase 2B:**
- Q1: Optimal hierarchy depth (3 vs 4 vs 5 levels)?
- Q2: Expert count per level (4-8 range exploration)?
- Q3: Gumbel-softmax temperature annealing schedule?
- Q4: Compositional structure annotation methodology?
- Q5: Computational cost reduction strategies?

---

## 11. Implementation Timeline

**Phase 2B (Verification Planning):** 2-3 weeks
- Decompose into sub-hypotheses with detailed verification protocols
- Design ablation studies
- Specify experimental dependencies
- Create verification roadmap

**Phase 2C (Experiment Design):** 2-3 weeks
- Detailed experimental specifications
- Implementation code structure design
- Benchmark adaptation protocol (Kim & Linzen splits for OMEGA)
- Baseline reproduction plans

**Phase 3 (Implementation Planning):** 3-4 weeks
- PRD: Problem specification and success criteria
- Architecture: Detailed technical design with FlashAttention integration
- Epics & Stories: Implementation task breakdown

**Phase 4 (Implementation & Validation):** 3-4 months
- Prototype: 3-4 months (basic 3-level hierarchy + routing)
- Full evaluation: 6-8 months total (including baselines, ablations, analysis)

**Phase 5 (Paper Writing):** 4-6 weeks
- Academic paper drafting with Scholar MCP citation verification

**Total Estimate:** 8-10 months from Phase 2B start to paper submission

---

## Metadata

**Source Files:**
- Input: `02a_round_1_discussion.md` (Phase 2A Party Mode output)
- Reference: `00_brainstorm_session.md` (Phase 0 research question)
- Reference: `01_targeted_research.md` (Phase 1 literature review)
- Output: `02a_extended_hypothesis_full.md` (complete documentation)
- Output: `02a_extended_hypothesis.md` (this summary)

**Workflow:** Phase 2A Extended (Focused Hypothesis Clarification)
**Execution Mode:** YOLO (Fully Automated)
**Date:** 2026-02-06

**Next Step:** Execute Phase 2B Planning
```bash
/phase2b-planning --hypothesis-id "H1-HCADSR" --input "02a_extended_hypothesis.md"
```

---

**Status: ✅ READY FOR PHASE 2B VERIFICATION PLANNING**
