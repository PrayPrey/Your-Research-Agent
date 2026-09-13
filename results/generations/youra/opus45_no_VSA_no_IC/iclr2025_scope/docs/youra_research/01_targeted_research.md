# Targeted Research Report (Compact - Phase 2A Input)

**Date:** 2026-08-24 | **Phase:** 1 - Targeted Research | **Researcher:** Anonymous

---

## Research Question

**Primary:** What is the relationship between LoRA rank scaling and model size for task-specific fine-tuning, and how does this interact with attention pattern efficiency in long-context scenarios?

**Detailed:**
1. Does optimal LoRA rank diverge across model scales (1B→70B) based on task cognitive complexity?
2. Do attention entropy and sparsity metrics show predictable degradation at extrapolated sequence lengths?
3. Does token-level distillation outperform matrix-level distillation for long-context retention?

---

## Reference Papers

| Paper | Year | SS ID | arXiv ID | Key Insight |
|-------|------|-------|----------|-------------|
| LoRA (Hu et al.) | 2021 | a8ca46b171467ceb2d7652fbfb67fe701ad86092 | 2106.09685 | Rank decomposition, α/r scaling |
| Scaling Laws (Kaplan et al.) | 2020 | e6c561d02500b2596a230b341a8eb8b921ca5bf2 | 2001.08361 | Power-law model/data/compute |
| LongBench (Bai et al.) | 2023 | b31a5884a8ebe96b6300839b28608b97f8f8ef76 | 2308.14508 | Long-context eval benchmark |
| Phi-1.5 (Microsoft) | 2023 | e26888285436bc7998e5c95102a9beb60144be5e | 2309.05463 | 1.3B model for experiments |

---

## Key Findings (Compact)

| Finding | Source | Insight |
|---------|--------|---------|
| α/√r scaling fix | RoRA (2025) | Rank-dependent behavior exists |
| <2% tokens sufficient | Quest (2024) | Query-aware selection 7x speedup |
| β_n ≈ log(n) critical | Critical Scaling | Phase transition in attention |
| 20.6x speedup at 103K | mmMamba (2025) | Transformer→SSM viable |

---

## Research Gaps (FULL - Critical for Phase 2A)

### Gap 1: Scale-Dependent LoRA Rank Optimization (PRIMARY)

**Missing:** Systematic study of optimal r vs model size N with task complexity control

**Evidence:**

| Paper | SS ID | arXiv ID | Key Insight |
|-------|-------|----------|-------------|
| RoRA | 6d4c98599623330b07234783112e6a6d5102e70f | 2501.04315 | α/√r improves with rank |
| LoRA-drop | 6cd1a41a8cc8feadff889d5f9de4c2cf0f6e3bf3 | 2402.07721 | 50% retention via output eval |

| Implementation | URL | Stars |
|----------------|-----|-------|
| microsoft/LoRA | https://github.com/microsoft/LoRA | 13.7k |
| torchtune LoRA | https://github.com/pytorch/torchtune | - |

---

### Gap 2: Attention Entropy Prediction at Extrapolated Lengths (PRIMARY)

**Missing:** Predictive model for H(L), S(L) at L >> L_train

**Evidence:**

| Paper | SS ID | arXiv ID | Key Insight |
|-------|-------|----------|-------------|
| Quest | 1c7db9fb18246787fbe3de6e0eaa370ae749e795 | 2406.10774 | Query-aware sparsity |
| Tactic | 3ac83dc35e519e5fbdddc0e90eb3c56467fb22c6 | 2502.12216 | Cumulative attention selection |
| High-Dim Curse | 8c99036877c646d4149d376652d6f0d4b37a6594 | 2505.22107 | DGA attention optimization |

---

### Gap 3: Token vs Matrix Distillation Comparison (SECONDARY)

**Missing:** Controlled comparison on LongBench QA at 8K-32K contexts

**Evidence:**

| Paper | SS ID | arXiv ID | Key Insight |
|-------|-------|----------|-------------|
| mmMamba | bde174c7fa13c4fc50355bf29547137d293ab23c | 2502.13145 | 3-stage distillation |
| T2MD | b8b113c7f525bede2fc7ca6d7b79cca81e8bcf66 | 2506.18999 | Layer-level teacher forcing |

| Implementation | URL | Stars |
|----------------|-----|-------|
| goombalab/phi-mamba | https://github.com/goombalab/phi-mamba | 125 |
| wph6/CAB | https://github.com/wph6/CAB | 5 |

---

## Gap Priority

| Gap | Relevance | Impact | Priority |
|-----|-----------|--------|----------|
| Gap 1 | PRIMARY | HIGH | Critical |
| Gap 2 | PRIMARY | HIGH | Critical |
| Gap 3 | SECONDARY | MEDIUM | High |

---

## Phase 2A Readiness

- Research question: ✅
- Reference papers: 5/5 analyzed
- Gaps: 3 identified (2 PRIMARY)
- Evidence: 26 sources with IDs
- Phase boundary: ✅ No hypotheses proposed

**Next:** Phase 2A-Dialogue for hypothesis generation

---

*Full report: `01_targeted_research_full.md`*
