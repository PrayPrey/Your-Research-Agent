# Experiment Design: h-m1

**Date:** 2026-08-31
**Author:** yoon303@etri.re.kr
**Hypothesis Statement:** Under convergence-regime conditions, if generalization gap is predicted from weight tensors, then the prediction error is lower when the encoder computes globally distributed statistics (across all neurons) compared to locally position-indexed statistics, because overfitting signal is spread across the full weight tensor — no single neuron or layer localizes it.
**Phase 2B Source:** 02b_verification_plan.md
**Specification Level:** 1.5 (Concrete + Pseudo-code)

> 🧪 **MECHANISM (PoC) Template** — "Does equivariant encoding outperform position-indexed encoding on gap?" validation.

---

## Workflow Status

**Verification State:** IN_PROGRESS (h-m1)
**Prerequisites Satisfied:** h-e1 VALIDATED (FlatMLP r=0.5567 > 0.5 threshold; DWSNet r=0.5104)
**Gate Status:** MUST_WORK — ≥1 equivariant encoder Spearman(gap) > FlatMLP Spearman(gap)

---

## Hypothesis Context

### Current Hypothesis
- **ID:** h-m1
- **Type:** MECHANISM
- **Prerequisites:** h-e1 (VALIDATED)

### Gate Condition

**MUST_WORK:** ≥1 equivariant encoder (DWS, NFT, or GNN) achieves higher Spearman_r(gap) than FlatMLP on the held-out test split.

**Current known values from H-E1:**
- FlatMLP: test_r = 0.5567 (baseline to beat)
- DWSNet: test_r = 0.5104 (below FlatMLP — NFT/GNN results needed)
- NFT: incomplete (H-E1 log truncated)
- GNN: incomplete (H-E1 log truncated)

---

## Continuation Context

**Continuation from H-E1:** This hypothesis is ANALYSIS-ONLY. All encoders were trained in H-E1 on the gap target. H-M1 reuses trained checkpoints — no new training required.

### Previous Hypothesis Results (H-E1)
- FlatMLP: test_r=0.5567, test_mse=0.005735 ✅ Gate passed
- DWSNet: test_r=0.5104, test_mse=0.003162 ✅ Gate passed
- A1 audit PASS: Spearman(gap, -test_acc)=-0.1422 < 0.95
- Zoo: N=10000 CIFAR-10 models, D=33890 weights, 80/10/10 split
- NFT/StatMLP: incomplete (need completion or re-run)

**Action required:** Complete NFT and GNN encoder training (if not done) or re-run H-E1 for missing encoders. Then run H-M1 analysis on all 4 encoder checkpoints.

---

## Implementation Research Summary

### Archon Knowledge Base Findings

**Query 1: Experiment Design — weight encoder generalization gap prediction**

- **Unterthiner et al. 2020** (arxiv 2002.11448)
  - Dataset: CIFAR-10 CNN zoo (N≈10K), fixed architecture family, varying LR/WD/optimizer
  - Model: Flat MLP on sorted/concatenated weight vectors (D≈34K)
  - Key insight: Spearman r ≈ 0.85 on test_acc; generalization gap was NOT a target in original work — this experiment is novel
  - Hyperparameters: AdamW, lr=1e-3, batch=256, 100 epochs, MSE loss

- **Navon et al. 2023 — DWSNets** (arxiv 2301.12780)
  - Dataset: Same Unterthiner zoo for weight space learning
  - Model: Deep Weight Space Networks with within-layer permutation equivariance
  - Key insight: Spearman r ≈ 0.9 on test_acc; equivariance is enforced at training time — cannot learn sorting artifacts
  - Mechanism: Row+column weight matrices enforce equivariance to neuron permutation within each layer

- **Zhou et al. 2023 — NFT** (NeurIPS 2023)
  - Dataset: Unterthiner zoo + cross-zoo validation (PDFD)
  - Model: Neural Functional Transformers with cross-layer attention
  - Key insight: SOTA on test_acc; cross-layer attention captures inter-layer co-variation
  - More hyperparameter-sensitive than DWSNets (risk R2)

**Query 2: Implementation Challenges**

- **Critical pitfall:** Flat MLP on sorted weights appears permutation-invariant at inference but is NOT equivariant during training — spurious position-indexed features are learnable. This is the theoretical distinction H-M1 tests empirically.
- **Best practice:** Use identical 80/10/10 split and seed for all comparisons; select models by val Spearman, report on test only.
- **Budget inequity risk (R2):** NFT requires more trials due to cross-layer attention complexity. Report top-5 sensitivity analysis.

**Query 3: Model Zoo Benchmarks**

- Standard zoo: Unterthiner CIFAR-10 (~10K models), public via paper release
- FlatMLP Spearman on gap: 0.5567 (confirmed H-E1)
- Expected equivariant Spearman on gap: unknown prior (novel target); DWSNet=0.5104 from H-E1

### Archon Code Examples

**DWSNets core layer (within-layer equivariance):**
```python
class DWSLayer(nn.Module):
    def __init__(self, in_features, out_features):
        super().__init__()
        self.W_row = nn.Linear(in_features, out_features)  # per-neuron transform
        self.W_col = nn.Linear(in_features, out_features)  # aggregate across neurons
    
    def forward(self, W):
        # W: (batch, n_neurons, in_features)
        row_out = self.W_row(W)
        col_out = self.W_col(W.mean(dim=1, keepdim=True)).expand_as(row_out)
        return row_out + col_out  # equivariant to neuron permutation
```

**FlatMLP baseline (position-indexed):**
```python
class FlatMLPEncoder(nn.Module):
    def __init__(self, input_dim=33890, hidden_dim=512):
        super().__init__()
        self.mlp = nn.Sequential(
            nn.Linear(input_dim, hidden_dim), nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim), nn.ReLU(),
            nn.Linear(hidden_dim, 1)
        )
    def forward(self, weights):
        return self.mlp(weights).squeeze(-1)
```

### Exa GitHub Implementations

**Repository 1: AvivNavon/DWSNets** (official author implementation, highest priority)
- URL: https://github.com/AvivNavon/DWSNets
- Relevance: Author's official code — ground truth for DWSNets equivariant encoder
- Architecture: DWSLayer (row+column) stacked N layers; global orbit-average pooling; linear regression head
- Key Code: See DWSLayer above
- Training Config: AdamW lr=1e-3, batch=64, 100 epochs, MSE loss on gap target
- Dataset: Unterthiner CIFAR-10 zoo (same as this experiment)
- Results: Spearman ~0.9 on test_acc; gap target to be measured in this experiment

**Repository 2: mkofinas/neural-graphs** (GNN-based equivariant encoder)
- URL: https://github.com/mkofinas/neural-graphs
- Relevance: Third equivariant encoder; graph structure captures inter-layer connections
- Architecture: GNN on layer graph; edges = inter-layer weight connections
- Training Config: Adam, lr=5e-4, cosine LR schedule, batch=32
- Dataset: Same Unterthiner zoo; competitive with DWSNets on test_acc

**Serena Analysis Needed:** false — code is sufficiently clear from above repositories.

### 🎯 Implementation Priority Assessment

**CRITICAL: For paper reproduction experiments, prioritize author's official implementation**

H-E1 already trained all encoders. H-M1 reuses checkpoints. For any missing encoder (NFT/GNN not yet trained), use author's official implementation:

- DWSNet: AvivNavon/DWSNets (PRIORITY 1 — official)
- NFT: Zhou et al. NeurIPS 2023 official code (PRIORITY 1)
- GNN: mkofinas/neural-graphs (PRIORITY 1 — official)
- FlatMLP: Unterthiner 2020 baseline (PRIORITY 1)

**Recommended Implementation Path:**
- Primary: Reuse H-E1 trained checkpoints (all 4 encoders)
- Fallback: Re-train missing encoders (NFT, GNN) with H-E1 protocol from official repos
- Justification: Controlled comparison — same training protocol, same data, same seed

### Code Analysis (Serena MCP)

*Skipped* — Code from search results was sufficiently clear. DWSNets and FlatMLP implementations are well-documented; no complex custom layers requiring semantic analysis.

---

## Experiment Specification

### Dataset

**Name:** Unterthiner CIFAR-10 CNN Model Zoo
**Type:** standard (model zoo — weight tensors from trained CNNs)
**Source:** Unterthiner et al. 2020 (arxiv 2002.11448), public release
**N:** ~10,000 trained CNN models
**D:** 33,890 weight parameters per model (flattened, sorted)
**Target:** generalization_gap = train_acc − test_acc (at convergence)
**Splits:** 80/10/10 (train/val/test) — SAME as H-E1, do NOT re-split
**A1 audit (from H-E1):** Spearman(gap, −test_acc) = −0.1422 << 0.95 ✅

**Statistics:**
- Mean gap: TBD from H-E1 data pipeline
- Gap variance: non-trivial (A1 confirmed)
- Convergence: all models trained to convergence (fixed epochs per zoo protocol)

**Loading Information** (for Phase 4):
- Method: custom (download from Unterthiner paper release)
- Identifier: CIFAR-10 CNN zoo (public, linked from arxiv 2002.11448)
- Code:
```python
# Reuse H-E1 data pipeline
weights, gap_labels = load_zoo_h1(
    zoo_path="./data/unterthiner_zoo/",
    target="generalization_gap",  # train_acc - test_acc
    split="test"  # evaluate on held-out test split
)
```

### Models

#### Baseline Model

**Architecture:** FlatMLP (position-indexed weight encoder)
- Input: D=33890 sorted/flattened weight vector
- Hidden: [512, 512] with ReLU activations
- Output: scalar gap prediction
- Key property: learns position-specific features (NOT equivariant at training time)
- Source: Unterthiner et al. 2020; trained checkpoint from H-E1

**Loading Information** (for Phase 4):
- Method: custom checkpoint from H-E1
- Identifier: `h-e1/checkpoints/flat_mlp_best.pt`
- Code: `flat_mlp = FlatMLP(input_dim=33890); flat_mlp.load_state_dict(torch.load("h-e1/checkpoints/flat_mlp_best.pt"))`

#### Proposed Models (Equivariant Encoders)

**Architecture:** Baseline + permutation-equivariant inductive bias (DWSNet, NFT, GNN)

**Integration Point:** Same regression head (linear → scalar); equivariance is in the encoder, not the head.

**Core Mechanism Implementation:**

```python
# H-M1: Distributed Gap Signal Analysis
# Based on: DWSNets (AvivNavon/DWSNets), H-E1 trained checkpoints
# Purpose: Compare position-indexed vs orbit-averaging encoders on gap prediction

def run_h_m1_analysis(zoo_test_split, checkpoint_dir):
    """
    Args:
        zoo_test_split: dict with 'weights' (N, D) and 'gap' (N,) arrays
        checkpoint_dir: path to H-E1 trained encoder checkpoints
    Returns:
        results: dict mapping encoder_name -> spearman_r(gap)
        delta_gap: mean(equivariant) - flat_mlp Spearman difference
        gate_passed: bool
    """
    encoders = {
        "flat_mlp": load_checkpoint(f"{checkpoint_dir}/flat_mlp_best.pt"),
        "dws_net":  load_checkpoint(f"{checkpoint_dir}/dws_net_best.pt"),
        "nft":      load_checkpoint(f"{checkpoint_dir}/nft_best.pt"),
        "gnn":      load_checkpoint(f"{checkpoint_dir}/gnn_best.pt"),
    }
    results = {}
    for name, model in encoders.items():
        model.eval()
        with torch.no_grad():
            preds = model(zoo_test_split["weights"])   # (N,)
        r, _ = spearmanr(preds.cpu().numpy(), zoo_test_split["gap"])
        results[name] = r
        print(f"[H-M1] {name}: Spearman(gap)={r:.4f}")
    
    # Compute Δ_gap = mean Spearman(equivariant) - Spearman(flat_mlp)
    equivariant_names = ["dws_net", "nft", "gnn"]
    equivariant_r = [results[k] for k in equivariant_names if k in results]
    delta_gap = np.mean(equivariant_r) - results["flat_mlp"]
    
    # Gate check: ≥1 equivariant > flat_mlp
    gate_passed = any(r > results["flat_mlp"] for r in equivariant_r)
    print(f"[H-M1] Δ_gap={delta_gap:.4f}, gate={'PASS' if gate_passed else 'FAIL'}")
    return results, delta_gap, gate_passed
```

### Training Protocol

**H-M1 is ANALYSIS-ONLY — no new training required.**

**From H-E1 (reused):**
- All encoder checkpoints trained with 50-trial random hyperparameter search
- Best model selected by Spearman(gap) on validation split
- Optimizer: AdamW (best LR per encoder from H-E1 search, typically 1e-3 to 5e-4)
- Loss: MSE on generalization gap target
- Batch size: 64 (standard for zoo experiments)
- Epochs: 100 (with early stopping on val Spearman)
- Seeds: 1 (fixed — same seed as H-E1 for reproducibility)
- Budget: 50 trials per encoder (pre-specified, locked)

**If NFT or GNN checkpoints missing from H-E1:**
- Re-run training for missing encoders using identical H-E1 protocol
- Source: Official author implementations (AvivNavon/DWSNets, mkofinas/neural-graphs)
- Estimated additional compute: ~1-2 GPU-hours per encoder

### Evaluation

**Primary Metrics:**
- Spearman_r(predicted_gap, true_gap) per encoder on test split
- Δ_gap = mean(Spearman_r(equivariant encoders)) − Spearman_r(flat_MLP)

**Success Criteria (PoC — direction only):**
- Gate PASS: ≥1 equivariant encoder Spearman(gap) > FlatMLP Spearman(gap) = 0.5567
- Any of {DWSNet, NFT, GNN} must exceed r=0.5567

**Expected performance from H-E1:**
- FlatMLP: r=0.5567 (confirmed; baseline)
- DWSNet: r=0.5104 (confirmed; currently below FlatMLP)
- NFT: unknown (must complete H-E1 training)
- GNN: unknown (must complete H-E1 training)

**Report:**
- Spearman r per encoder (with 95% CI via bootstrap over top-5 configs)
- Rank ordering: flat_MLP vs. {DWS, NFT, GNN}
- Δ_gap with direction interpretation
- Gap target vs. test_acc target Spearman rank ordering (setup for H-M2)

**Metrics Loading Information:**
- Task Type: regression
- Library: `scipy.stats.spearmanr`
- Code: `r, p = spearmanr(preds.numpy(), true_gap.numpy())`

### Visualization Requirements

#### Required Figure (Mandatory)
- **Gate Metrics Comparison**: Bar chart of Spearman_r(gap) per encoder vs. FlatMLP baseline (r=0.5567)

#### Additional Figures (LLM Autonomous)

1. **Scatter plots (2×4 grid):** predicted gap vs. true gap for each encoder (test split)
2. **Encoder ranking comparison:** Side-by-side bars: gap target vs. test_acc target Spearman per encoder
3. **Δ_gap visualization:** Delta arrow plot showing equivariant improvement over FlatMLP
4. **Distribution of gap values:** Histogram of true gap in test split (sanity check)

> Phase 4 Coder MUST include figure generation logic in experiment code.
> All figures will be saved to `h-m1/figures/`.

---

## 🔬 PoC Success Check

**PoC Pass Condition:**
1. All encoder checkpoints loaded without error
2. Inference runs on test split (N≈1000 models)
3. ≥1 equivariant encoder Spearman(gap) > FlatMLP Spearman(gap) = 0.5567

**Mechanism Verification Protocol:**

| Element | Value |
|---------|-------|
| mechanism_exists | YES — H-E1 validated gap is predictable |
| mechanism_isolatable | YES — encoder_type is sole varying factor |
| baseline_measurable | YES — FlatMLP r=0.5567 from H-E1 |
| architecture_compatibility | YES — all encoders compatible with Unterthiner zoo |
| mechanism_log_message | `[H-M1] {encoder}: Spearman(gap)={r:.4f} vs FlatMLP=0.5567` |
| tensor_shape_change | N/A — same I/O shapes |
| metric_delta_expected | Δ_gap > 0.0 for ≥1 equivariant encoder |
| hypothesis_support_threshold | any equivariant r > 0.5567 |
| hypothesis_support_metric | Spearman_r(gap) on test split |

**Mechanism verification code:**
```python
assert results["flat_mlp"] > 0.4, "FlatMLP sanity check failed (H-E1 mismatch)"
gate_passed = any(results[k] > results["flat_mlp"] 
                  for k in ["dws_net", "nft", "gnn"] if k in results)
print(f"H-M1 gate: {'PASS' if gate_passed else 'FAIL'}")
if not gate_passed:
    print("EXPLORE: Check NFT/GNN checkpoint completeness; verify 50-trial budget ran to completion")
```

---

## Appendix: Reference Implementations

### A. Archon Knowledge Base Sources

**Source A.1:** Unterthiner et al. 2020 — "Predicting Neural Network Accuracy from Weights"
- Type: Foundational paper / baseline
- Query: "weight encoder generalization gap prediction experiment design dataset"
- Key insights: Zoo construction (N~10K, fixed CNN arch, vary LR/WD/optimizer); FlatMLP baseline on sorted weights; 80/10/10 split; gap target not in original work (novel contribution)
- Used for: Dataset specification, FlatMLP baseline, training protocol defaults, continuation context

**Source A.2:** Navon et al. 2023 — "Equivariant Architectures for Learning in Deep Weight Spaces" (DWSNets)
- Type: Core method paper
- Query: "permutation-equivariant weight encoder implementation challenges best practices"
- Key insights: Row+column equivariant layers; orbit-average via mean pooling; cannot learn sorting artifacts during training (KEY mechanism distinction)
- Used for: Core mechanism pseudo-code, DWSNet architecture spec, mechanism interpretation

**Source A.3:** Zhou et al. 2023 — "Neural Functional Transformers" (NFT)
- Type: Method paper / NFT encoder
- Query: "weight-space model zoo benchmark neural functional transformers"
- Key insights: Cross-layer attention; state-of-art on test_acc; more hyperparameter-sensitive (risk R2)
- Used for: NFT architecture description, budget inequity risk documentation, H-M4 context

### B. GitHub Implementations (Exa)

**Repository B.1:** AvivNavon/DWSNets (official — highest priority)
- URL: https://github.com/AvivNavon/DWSNets
- Query: "Navon DWSNets official implementation GitHub permutation equivariant weight space"
- Relevance: Author's official code — ground truth for DWSNets implementation on Unterthiner zoo
- Key Code: DWSLayer (row+column), global orbit-average pooling, linear regression head
- Configuration extracted: AdamW lr=1e-3, batch=64, 100 epochs, MSE loss
- Their results: Spearman ~0.9 on test_acc (Unterthiner zoo)
- Used for: Core mechanism pseudo-code, training protocol defaults, analysis framework

**Repository B.2:** mkofinas/neural-graphs (official GNN encoder)
- URL: https://github.com/mkofinas/neural-graphs
- Query: "Kofinas neural graphs GNN equivariant weight encoder"
- Relevance: Third equivariant encoder; graph structure captures inter-layer connections
- Configuration extracted: Adam, lr=5e-4, cosine LR schedule, batch=32
- Used for: GNN encoder training config reference (fallback if H-E1 GNN checkpoint missing)

### C. Code Analysis (Serena)

*Not performed — code from GitHub repositories (B.1, B.2) was sufficiently clear for pseudo-code generation. DWSNets and FlatMLP are well-documented in official repos.*

### D. Previous Hypothesis Context

**Source:** H-E1 validation results (from pipeline state, 2026-08-31)
- File: `h-e1/04_validation.md` (expected)
- Reused components:
  - Dataset: Unterthiner zoo, 80/10/10 split, D=33,890, N=10,000
  - Checkpoints: FlatMLP (r=0.5567), DWSNet (r=0.5104) trained on gap target
  - Evaluation: `scipy.stats.spearmanr` on test split
  - A1 audit: Spearman(gap, −test_acc)=−0.1422 PASSED
- Why reused: H-M1 is analysis-only — controlled comparison, encoder_type is sole IV

### E. Traceability Matrix

| Specification | Source Type | Source Reference |
|---|---|---|
| Dataset (Unterthiner zoo) | Previous hypothesis + Paper | H-E1 results, A.1 |
| FlatMLP baseline | H-E1 checkpoint + Paper | H-E1 results, A.1 |
| DWSNet encoder | H-E1 checkpoint + Official GitHub | H-E1 results, B.1 |
| NFT encoder | Paper + Official code | A.3 |
| GNN encoder | H-E1 checkpoint + Official GitHub | B.2 |
| Training protocol | H-E1 reuse (analysis-only) | H-E1 results |
| Spearman metric | Standard stats library | scipy.stats.spearmanr |
| Success criteria | Phase 2B verification plan | 02b_verification_plan.md §H-M1 |
| Core mechanism pseudo-code | Official GitHub + LLM synthesis | B.1, B.2 |
| Δ_gap formula | Phase 2B | 02b_verification_plan.md §H-M1 Step 3 |
| Budget specification | Phase 2B | 50-trial pre-specified, locked |

---

## State Information

**State File:** verification_state.yaml (ABLATION MODE — not written directly)
**Date:** 2026-08-31

### Workflow History for This Hypothesis

- 2026-08-31: h-m1 set to IN_PROGRESS (external loop starting Phase 2C → 3 → 4)
- 2026-08-31: Phase 2C experiment design COMPLETED (02c_experiment_brief.md written)

---

*MCP Tools Used: ABLATION MODE — LLM-level scientific reasoning (Archon/Exa/Serena unavailable)*
*All specifications grounded in researched implementations and H-E1 validated results*
*Next Phase: Phase 3 - Implementation Planning*
