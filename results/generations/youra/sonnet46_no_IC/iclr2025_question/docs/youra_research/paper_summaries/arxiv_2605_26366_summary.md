# Automatic Layer Selection for Hallucination Detection

## Key Metadata
- **Authors:** Xinpeng Wang et al. (University of Virginia, Walrus Security, New York University)
- **Year:** 2026
- **Venue:** ICML 2026 (PMLR 306)
- **Core Contribution:** FEPoID — a training-free layer-selection criterion (First Effective Peak of Intrinsic Dimension) that automatically identifies near-optimal intermediate layers for hidden-state-probing hallucination detection, plus First-Sentence Truncation (FST) for token-position selection.

## Section Summaries

### Abstract
Recent studies on hallucination detection have shown that hallucination-related signals are more strongly encoded in intermediate layers than in the final layer of large language models (LLMs). Although a growing body of work has sought to exploit this property for hallucination detection, how to automate the selection of high-performing layers remains underexplored, and principled methods for this purpose are still lacking. To address this gap, we first propose several hypotheses for why such signals emerge in intermediate layers and evaluate corresponding criteria for automatic layer selection across diverse LLM architectures, scales, and tasks, covering both question answering and summarization hallucination detection benchmarks. However, we find that none of these criteria consistently delivers satisfactory performance. We therefore propose a new selection criterion, First Effective Peak of Intrinsic Dimension (FEPoID), which consistently identify optimal or near-optimal layers and outperforms both the aforementioned criteria and existing hallucination detection baselines. FEPoID is training-free and incurs negligible computational overhead. In addition, we study the generation behaviors of LLMs and introduce a simple yet effective truncation strategy, which further amplifies hallucination-related signals and substantially improves overall detection performance.

### Introduction & Motivation
The best-performing layer for hallucination detection consistently lies in intermediate layers, but its exact location varies substantially across datasets and model architectures — motivating a principled automatic selection criterion. Prior approaches either pick a predetermined layer in a data/task-agnostic manner or exhaustively evaluate all layers (computationally impractical). The paper works within the hidden-state probing framework: frozen LLM + lightweight MLP trained on representations from a selected layer. A second question: which token position to probe, since last-generated-token representations are corrupted by end-of-sequence noise.

### Methodology
[DETAILED] The paper evaluates layer-selection criteria organized by four hypotheses: (i) rich semantic information → **RankMe** (effective rank via normalized singular-value entropy: $\text{RankMe}(Z^{(\ell)}) = \exp(-\sum_k p_k \log p_k)$ where $p_k = \sigma_k / (\|\sigma\|_1 + \varepsilon)$); (ii) task-aligned features → **Validation Loss**, **Relative Gradient Norm** ($\text{RGN} = \|g\|_2 / \|\theta\|_2$), **SNR** (gradient consistency across examples); (iii) information compression → **Curvature** (mean turning angle $\kappa_{t,i} = \arccos\frac{\langle v_{t-1,i}, v_{t,i}\rangle}{\|v_{t-1,i}\|\|v_{t,i}\|}$ of token-trajectory velocity vectors); (iv) high effective information capacity → **Intrinsic Dimension** (TwoNN estimator: distance ratio $\mu_i = r_{i,2}/r_{i,1}$ follows Pareto with parameter $d_{ID}+1$; scikit-dimension + Faiss-GPU).

**FEPoID:** ID curves show a recurring bimodal pattern — a first peak in intermediate layers (abstract semantic information) and a later, often higher peak near the output (surface/lexical complexity). FEPoID selects the **first effective peak**: identify local maxima of $\{d^{(\ell)}_{ID}\}$, scan shallow→deep, discard a candidate peak at $\ell$ if ID keeps rising within a forward horizon window $w$ (default $w=7$), select earliest surviving peak (fall back to shallowest). Training-free, negligible overhead (~10s for all 32 layers vs 27–58s for competitors).

**FST (First-Sentence Truncation):** extract representations at the last token of the FIRST generated sentence (rule-based boundary scanner) instead of the last generated token — a supervision-free approximation of the "exact-answer token" position that avoids end-of-sequence noise (inconsistent continuation, semantic drift, degenerate repetition).

### Experiments & Results
[DETAILED] **Datasets:** QA — CoQA, SQuAD, HotpotQA, TriviaQA, PsiLoQA (context-aware or question-only; 10 samples at T=1.0 for multi-sample baselines, single best answer at T=0.1; max 30 tokens); Summarization — HaluEval, CNN/DM (max 130 tokens, TrueTeacher labels). **Models:** LLaMA-3.1-8B-Instruct, Mistral-7B-Instruct-v0.3, LLaMA-3.1-8B base, LLaMA-3.2-3B, LLaMA-3.2-1B. **Labels:** exact match + LLM-as-Judge (Orgad et al. 2025 protocol). **Metric:** AUROC on the test split.

Key results (Table 2, w=7, last-generated-token, hidden-state probing MLP):

| Method | LLaMA-3.1-8B-Instruct avg | Mistral-7B-Instruct avg |
|--------|--------------------------|------------------------|
| Pred. Entropy | 0.5820 | 0.6738 |
| Semantic Entropy | 0.5311 | 0.6560 |
| EigenScore | 0.5499 | 0.7141 |
| Probing + Val Loss | 0.7250 | 0.8457 |
| Probing + FEPoID | **0.7253** | **0.8531** |

FEPoID stays close to oracle layers (small AUROC gap) where LID/EigenScore layer heuristics incur large gaps. On summarization FEPoID also wins (LLaMA avg 0.6080, Mistral avg 0.7711). FST adds consistent AUROC gains for ALL methods (up to ~0.20 for LLaMA-Instruct), explained by cleaner class structure (Fisher Separation and Silhouette Score improve across all datasets) despite similar ID. FEPoID robust to horizon w; generalizes to base and 1B/3B models.

### Discussion & Conclusion
Criteria previously correlated with downstream performance (RankMe, curvature, RGN, SNR, val loss) do NOT reliably select layers for hallucination detection; FEPoID + FST offer a practical, supervision-free extraction recipe. Future work: other tasks, modalities, theory of ID dynamics.

## Key Contributions
- First systematic evaluation of layer-selection criteria (information-theoretic, gradient-based, geometric) for hallucination detection — none reliable.
- FEPoID: training-free first-effective-ID-peak criterion that consistently finds near-optimal intermediate layers across architectures, scales, tuning strategies, and tasks.
- FST token-position rule: probing the last token of the first generated sentence beats the last-token heuristic and improves every baseline method-agnostically.

## Potential Relevance
This is the CLOSEST PRIOR to our gap: it confirms intermediate > final layer signal as established consensus, but selects layers via geometric criteria over hidden states (intrinsic dimension) within a SUPERVISED probing framework (MLP trained per layer) — it never evaluates raw logit-lens uncertainty statistics (per-layer entropy, max-prob, adjacent-layer KL) as training-free detection scores. Its negative result (information-theoretic criteria like RankMe fail for layer selection) is a caution for our held-out-AUROC-based selection; its evidence that the optimal layer varies across datasets and architectures directly motivates our per-model held-out selection + cross-dataset transfer measurement. FST's end-of-sequence noise finding suggests answer-token aggregation strategy matters for our mean-over-answer-tokens statistics. FEPoID is the natural comparison target/baseline for Phase 5.
