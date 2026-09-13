# Phase 2A Extended: Hypothesis Clarification

**Date:** 2026-02-13
**Author:** Pray
**Source Round:** 02a_round_1_discussion.md
**Status:** Ready for Phase 2B Verification Planning

---

## 1. Clarified Hypothesis

### 1.1 Core Statement

**Hypothesis ID:** H-UCF-v1
**Confidence Level:** 0.78

**Main Hypothesis:**
Under multi-domain training conditions with self-supervised contrastive learning, if a Universal Composition Functor (UCF) is trained with functorial regularization constraints on domain-agnostic primitives extracted from frozen foundation models, then cross-domain compositional generalization will be achieved because the functorial constraints preserve compositional structure across category-like domain representations.

**Alternative Hypothesis (H0):**
Functorial constraints do not improve cross-domain compositional generalization beyond domain-specific composition methods. The shared primitive space fails to capture compositionally meaningful representations, and cross-domain transfer does not exceed baseline transformer performance.

### 1.2 Variables

| Variable | Type | Operationalization | Expected Range/Values |
|----------|------|-------------------|----------------------|
| UCF Architecture | Independent | Transformer-based functor with layers, hidden dim, attention heads | 2-6 layers, 256-768 dim, 4-8 heads |
| Functorial Regularization Weight (λ_functor) | Independent | Weight controlling L_functor = \|\|F(p1 ∘ p2) - F(p1) ⊗ F(p2)\|\| | [0.01, 0.5] |
| Training Domains | Independent | Combination of NLP/Vision/Multimodal datasets | SCAN, COGS, MIT-States, RefCOCO |
| Compositional Generalization Accuracy | Dependent | % correct on held-out novel compositions and cross-domain transfer | Target: >85% (SOTA parity: ~99%) |
| Primitive Embedding Dimension | Controlled | Fixed dimension aligned with foundation models | 768 |
| Foundation Models | Controlled | Frozen pretrained encoders | CLIP ViT-L/14, T5-base |

### 1.3 Causal Mechanism

**Causal Chain (N=3 steps):**

```
Step 1: Primitive Extraction
Frozen Foundation Models (CLIP, T5) → Domain-Specific Primitives
├── CLIP extracts visual primitives (objects, attributes, relations)
├── T5 extracts linguistic primitives (concepts, predicates, arguments)
└── Primitives are compositionally meaningful representations

        ↓

Step 2: Shared Space Alignment + Functorial Composition
Domain-Specific Primitives → Shared Primitive Space → Universal Composition Functor
├── Learned projections with concept anchor alignment (L_align)
├── Transformer-based functor F: (primitive₁, primitive₂) → composed_representation
├── Functorial regularization L_functor = ||F(p1 ∘ p2) - F(p1) ⊗ F(p2)||
└── Self-supervised contrastive composition loss L_comp

        ↓

Step 3: Cross-Domain Generalization
Functorial Composition → Cross-Domain Transfer
├── Structure preservation guarantees compositional relationships transfer
├── Novel compositions of seen primitives generalize across domains
└── Single model handles NLP, vision, and multimodal without domain-specific tuning
```

**Evidence for Causal Links:**

| Link | Evidence Source | Key Finding | Strength |
|------|-----------------|-------------|----------|
| Step1 → Step2 | NLoTM (Wu et al., 2024) | Object-centric VQ-VAE extracts hierarchical composable representations aligned with objects/properties | Strong |
| Step1 → Step2 | CLIP/T5 literature | Foundation models encode semantically meaningful, transferable representations | Strong |
| Step2 → Step3 | Gavranovic (2024) | Category theory provides universal algebraic framework; functors preserve compositional structure | Medium |
| Step2 → Step3 | Category-equivariant networks (Maruyama, 2025) | Categorical constraints achievable in neural networks via soft regularization | Medium |
| Step3 → Outcome | Lake & Baroni MLC (2023) | Meta-learning achieves human-like systematicity; training regime is key, not architecture | Strong |

**Key Tension:**
- **Tension:** Lake & Baroni (2023) MLC achieves near-perfect performance (~99%) on SCAN/COGS using domain-specific meta-learning, but the approach requires domain-specific training. Gavranovic (2024) proposes category-theoretic constraints are universal, but this is theoretical without empirical validation on compositional generalization benchmarks.
- **Resolution:** This verification plan tests whether functorial constraints can achieve MLC-level performance while enabling cross-domain transfer that MLC lacks. If UCF matches MLC within-domain AND shows positive cross-domain transfer, the hypothesis is supported.

### 1.4 Key Assumptions

1. **Compositional structure is universal across domains at some abstraction level**
   - Evidence: Gavranovic (2024) category theory formalization; formal language theory
   - Consequence if violated: Shared primitive space will not capture domain-invariant composition rules; cross-domain transfer will fail even with perfect within-domain performance

2. **Foundation models extract compositionally meaningful primitives**
   - Evidence: NLoTM (2024) object-centric representations; CLIP zero-shot transfer
   - Consequence if violated: Primitive decomposition will be arbitrary; composition learning will not generalize to novel compositions

3. **Composition can be learned from composition-decomposition pairs without explicit labels**
   - Evidence: Zhang et al. (2022) EBM self-supervised compositional learning; TripletCLIP contrastive approach
   - Consequence if violated: Self-supervised training will fail to capture composition rules; explicit supervision will be required (limiting scalability)

4. **Soft functorial constraints approximate hard algebraic constraints**
   - Evidence: Equivariant network literature; differentiable relaxation success in other domains
   - Consequence if violated: λ_functor regularization will not enforce structure preservation; composition consistency will degrade

### 1.5 Scope & Boundaries

**Where Hypothesis Applies:**
- Compositional generalization tasks with clear primitive-composition structure
- Domains with available foundation model primitives (NLP, vision, multimodal)
- Tasks where composition follows algebraic-like rules (e.g., attribute-object composition)
- Benchmarks: SCAN, COGS (NLP), MIT-States, UT-Zappos (vision), RefCOCO (multimodal)

**Where Hypothesis Does NOT Apply:**
- Domains without clear compositional structure (e.g., abstract reasoning without explicit primitives)
- Tasks requiring highly abstract or analogical reasoning (e.g., Raven's matrices)
- Domains where foundation model primitives are unavailable or poor quality
- Real-time applications requiring sub-100ms inference (UCF adds computational overhead)

**Known Limitations:**
- Concept anchoring may not cover all primitive types (especially domain-specific technical concepts)
- Contrastive negative sampling strategy is critical and may require domain-specific tuning
- Single functor assumption may be too strong for very different composition types (alternatives: domain-specific heads with shared primitives)

### 1.6 Testable Predictions

**Primary Prediction:**
**P1 (Cross-Domain Compositional Generalization Accuracy vs SOTA ~99%)**:
UCF will achieve compositional generalization accuracy ≥95% on in-domain benchmarks (SCAN, COGS) AND ≥80% on held-out domain benchmarks without domain-specific fine-tuning.

*Measurement*:
- In-domain accuracy on SCAN systematic generalization splits
- In-domain accuracy on COGS lexical generalization
- Cross-domain transfer: Train on NLP+Vision → Test on Multimodal (RefCOCO)
- Statistical test: Paired t-test, n ≥ 25 runs, p < 0.05

*Basis*:
SOTA MLC achieves 99.78% on SCAN, 99.13% on COGS but is domain-specific.
Our target: Match within-domain (>95%) while demonstrating cross-domain transfer (>80%).

*Success Criteria for Phase 2B*:
- Primary: In-domain accuracy >95% (within 5% of MLC)
- Secondary: Cross-domain transfer >80% (zero-shot on held-out domain)
- Falsification: In-domain accuracy <85% OR cross-domain <60%

**Secondary Predictions:**
**P2 (Functorial Constraint Effectiveness)**:
Ablation: UCF with λ_functor > 0 will outperform UCF with λ_functor = 0 by ≥5% on novel compositions, demonstrating that functorial regularization contributes to generalization beyond standard contrastive learning.

**P3 (Cross-Domain Transfer Advantage)**:
UCF will achieve ≥2x better cross-domain transfer efficiency compared to domain-specific methods (MLC, TripletCLIP) when both are trained on the same data. Transfer efficiency = (held-out domain accuracy) / (in-domain accuracy).

**Falsification Criteria:**
The hypothesis will be **REJECTED** if any of the following occur:

1. **Primary Failure**: In-domain accuracy ≤85% on SCAN/COGS
   (= More than 15% below SOTA, indicating fundamental approach failure)

2. **Mechanism Failure**: λ_functor ablation shows no significant difference (p > 0.1)
   (= Functorial constraints do not contribute to generalization)

3. **Transfer Failure**: Cross-domain accuracy ≤60% OR transfer efficiency ≤1.0x vs baselines
   (= No advantage over domain-specific methods for cross-domain transfer)

4. **Comparative Failure**: Domain-specific methods (MLC on NLP, TripletCLIP on vision) outperform UCF on ALL metrics including transfer
   (= Universal approach provides no benefit over specialized methods)

### 1.7 SOTA Baseline (Optional - If SOTA Comparison Mode)

**SOTA Benchmark Summary:**

| Method | Dataset | Performance | Std Dev | Year |
|--------|---------|-------------|---------|------|
| MLC (Lake & Baroni) | SCAN (add jump) | 99.78% | ±0.2% | 2023 |
| MLC (Lake & Baroni) | COGS (lexical) | 99.13% | ±0.5% | 2023 |
| Standard Transformer | SCAN | ~70-80% | ±5% | 2020 |
| Standard Transformer | COGS | 16-35% | ±8% | 2020 |
| TripletCLIP | MIT-States | ~65% | ±3% | 2024 |

**SOTA Statistics:**
- Best Performance (MLC): 99.78% on SCAN
- Mean (MLC): ~99.5% on compositional benchmarks
- Performance Tier: High (>90%)
- Ceiling Room: ~0.2-0.9%

**Threshold Calculation (High-Performance Domain):**
- Given ceiling effect (room < 5%), using **Multi-Metric Strategy**
- Primary: In-domain accuracy ≥95% (within 5% of SOTA) AND cross-domain >80%
- Falsification: In-domain <85% (>15% below SOTA)

### 1.8 Statistical Verification Design

**Sample Size Calculation:**
- Effect size (Cohen's d): 0.8 (large effect expected for cross-domain advantage)
- Required runs: n ≥ 25 (for paired comparisons)
- Statistical power: 0.8
- Significance level: α = 0.05

**Test Specification:**
- Primary metric: Paired t-test (same random seeds across methods)
- Secondary: Wilcoxon signed-rank (non-parametric alternative)
- Multiple comparison correction: Bonferroni for 3 primary comparisons

**Report Format:**
- Mean ± Std Dev for each condition
- 95% Confidence Intervals
- Cohen's d effect size
- p-values (one-tailed for improvement claims)

**Experimental Controls:**
- Same train/val/test splits across all methods
- Same random seeds for initialization
- Same compute budget (GPU hours) per method
- Hyperparameter search with same budget

---

## 4. Phase 2B Readiness

### Decomposition Preview

**SH1 (Existence):**
"Does cross-domain compositional generalization exist when using functorial constraints on shared primitives?"
- Maps to: Primary prediction P1 (in-domain + cross-domain accuracy)
- Verification type: Empirical
- Critical: MUST PASS for Phase 2B to proceed
- Success criteria: In-domain ≥95%, cross-domain ≥80%

**SH2 (Mechanism):**
"Is the functorial regularization the actual cause of improved compositional generalization?"
- Maps to: Causal mechanism (N=3 steps, will decompose to H-M1 through H-M3)
  - **H-M1:** Primitive extraction produces compositionally meaningful representations
  - **H-M2:** Shared space alignment captures domain-invariant structure
  - **H-M3:** Functorial composition enables cross-domain transfer
- Verification type: Ablation studies + causal analysis
- Critical: Determines explanatory power
- Success criteria: Each mechanism step shows significant contribution (p < 0.05)

**SH3 (Comparison):**
"Does UCF outperform domain-specific methods (MLC, TripletCLIP) on cross-domain transfer?"
- Maps to: Secondary predictions P2, P3
- Verification type: Comparative empirical
- Critical: Determines practical value
- Success criteria: ≥2x transfer efficiency, ≥5% improvement with λ_functor

### Readiness Checklist

- [x] Hypothesis is in "Under [C], if [X], then [Y] because [Z]" format
- [x] Hypothesis ID assigned: H-UCF-v1
- [x] Confidence level specified: 0.78
- [x] Alternative hypothesis (H0) defined
- [x] All variables have operationalization from evidence (6 variables)
- [x] Causal mechanism has evidence at each step (N=3 steps, evidence table complete)
- [x] Causal chain length (N=3) determined and stored
- [x] Key tension identified (MLC vs category theory) and resolution proposed
- [x] Key assumptions list consequences if violated (4 assumptions)
- [x] At least 2 testable predictions exist with primary marked (3 predictions)
- [x] Falsification criteria are defined (4 criteria)
- [x] Baselines identified for comparison (MLC, TripletCLIP, Standard Transformer)
- [x] SH1, SH2, SH3 are clear starting points

### Open Questions

1. **Data Availability:** Are composition-decomposition pairs available or must they be generated? What is the quality of automatically mined pairs from SCAN grammars and scene graphs?

2. **Computational Requirements:** What is the training time for UCF compared to MLC? Can single-GPU training achieve competitive results, or is multi-GPU required?

3. **Concept Anchor Selection:** How should the shared concept anchor vocabulary be defined? Should it be learned or hand-crafted? What coverage is sufficient?

---

**Note:** This is a summary optimized for Phase 2B input.
Full output with all sections available in: `02a_extended_hypothesis_full.md`

**Full document includes:**
- Section 2: Contribution Summary
- Section 3: Key Related Work

---

*Generated using YouRA Research Phase 2A Extended Workflow (Focused)*
*2026-02-13*
