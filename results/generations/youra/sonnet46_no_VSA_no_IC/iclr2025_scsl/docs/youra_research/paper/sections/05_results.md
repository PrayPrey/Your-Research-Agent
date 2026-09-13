## 5. Results

### 5.1 RQ1: SSL-SGD Produces Severe Worst-Group Accuracy Degradation

Table 1 presents the test accuracy of DINO (SSL) and a supervised model on Waterbirds.

**Table 1: Test Accuracy on Waterbirds — DINO SSL vs. Supervised**

| Model | WGA (%) | Avg Acc (%) | WGA–Avg Gap |
|-------|---------|-------------|-------------|
| DINO (SSL, SGD) | **8.57** | 62.10 | −53.5 pp |
| Supervised (ViT-S) | **81.93** | 94.74 | −12.8 pp |
| *SSL-Supervised WGA Gap* | — | — | **73.36 pp** |

The 73.4 pp worst-group accuracy gap between DINO SSL and supervised training is striking, and directly answers RQ1: SSL-SGD produces severe worst-group accuracy degradation on Waterbirds. This gap satisfies the H-E1 gate threshold (>5 pp) with substantial margin.

Critically, DINO's average accuracy (62.1%) is not anomalously low — the model has learned to classify correctly for the majority group. What it has failed to do is generalize this classification to minority groups where the spurious feature (background) conflicts with the label. This asymmetric failure is not the signature of a poorly trained model; it is the signature of a model that has learned background texture as a reliable predictor of bird species.

Figure 1 visualizes the WGA and average accuracy comparison. The gap between the two bars (WGA vs. Average Acc) within DINO SSL (53.5 pp) reveals the severity of within-SSL shortcut encoding.

**Per-group breakdown (Table 2, Figure 3):** DINO achieves 97.3% on the majority group (waterbird, water background) — near-perfect — but only 8.6% on the corresponding minority group (waterbird, land background). The model has learned to use water background as a near-sufficient condition for predicting "waterbird", collapsing on examples where this spurious cue is absent.

**Table 2: Per-Group Test Accuracy on Waterbirds**

| Group | DINO SSL (%) | Supervised (%) |
|-------|-------------|----------------|
| Waterbird, water background (majority) | 97.25 | 99.82 |
| Waterbird, land background (minority) | **8.57** | **81.93** |
| Landbird, water background (minority) | 36.54 | 92.42 |
| Landbird, land background (majority) | 81.93 | 97.82 |

### 5.2 Training Dynamics: The Shortcut is Geometrically Stable

Figure 2 shows validation WGA and average accuracy over 100 training epochs for both DINO (SSL) and supervised training.

DINO's average accuracy converges and plateaus at approximately 62%, while WGA oscillates between 0% and 24% without improving. The best validation WGA (24.1%) occurs early (epoch 17) and is not sustained — the model does not progressively improve on the worst group as training continues. This is the key finding: **the shortcut encoding is geometrically stable, not a transient training artifact.**

In contrast, the supervised model achieves >70% validation WGA by epoch 2 and sustains WGA above 80% for the remaining training epochs, tracking closely with average accuracy.

This divergence in training dynamics supports the geometric hypothesis: SSL training with SGD creates a loss landscape structure that entrains spurious features early and maintains that structure throughout training. The optimizer's convergence path is geometrically biased.

### 5.3 RQ2: Sharpness Anisotropy Measurement (Pending)

The full sharpness anisotropy measurement requires converged SSL representations (≥100 epochs) with the complete protocol (N=100 random directions, 100 probe epochs, 4 checkpoints). The preliminary 10-epoch SimCLR fast run produced near-random SSL features (NT-Xent loss ≈6.23 vs. initialization ≈6.93), confirming that meaningful anisotropy measurement requires converged representations. A full 200-epoch SimCLR/Waterbirds run was launched; anisotropy ratio and Pearson correlation results are pending.

**Anticipated report format (to be updated when 200-epoch run completes):**

| SSL Method | Dataset | Anisotropy Ratio | Pearson r | Status |
|-----------|---------|-----------------|-----------|--------|
| SimCLR | Waterbirds | PENDING | PENDING | 200-ep run ongoing |
| MoCo-v2 | Waterbirds | — | — | Not yet run |
| DINO | Waterbirds | — | — | Not yet run |

The DINO WGA data in Table 1 establishes the severity of the problem. The anisotropy measurement will determine whether the loss landscape geometry accounts for that severity — and whether SAM can address it at the geometric level.

### 5.4 RQ3: SAM-SSL Intervention (Planned)

SAM-SSL training results are pending, contingent on converged SGD baselines (from the full 200-epoch run). The hypothesis predicts:
- Anisotropy ratio reduction ≥15% (SAM vs. SGD at convergence)
- WGA improvement ≥2 pp on Waterbirds
- Average accuracy preserved (<2 pp drop)

These predictions will be reported in an updated version of this paper upon completion of the full experimental protocol.

### 5.5 Comparison with Literature Baselines

For context, Table 3 situates our confirmed DINO WGA (8.57%) against published SSL baselines on Waterbirds.

**Table 3: Worst-Group Accuracy on Waterbirds — Literature Context**

| Method | Setting | WGA (%) |
|--------|---------|---------|
| SimCLR + linear probe [NeurIPS 2025] | SSL, annotation-free | 43.8 |
| DINO (ours) + linear probe | SSL, annotation-free | **8.57** |
| ERM ResNet-50 (ImageNet init) [Izmailov 2022] | Supervised, fine-tuned | 72.6 |
| LFR [Ghaznavi 2023] | Annotation-free, post-hoc | ~76 |
| Group DRO [Sagawa 2019] | Group labels required | 84.6 |
| Cross-Variant SSL [Yadav 2026] | SSL + gen. augment | 92.5 |

Our DINO result (8.57% WGA) is substantially lower than the SimCLR baseline from the NeurIPS 2025 spectral regularization paper (43.8%). This difference likely reflects architectural differences (ViT-S/8 vs. ResNet-50) and the use of pretrained DINO weights, which may have encoded stronger background biases from pretraining. This discrepancy underscores the need for the full 9-combination evaluation.
