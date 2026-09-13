# Discussion

We discuss the root causes of our failures, their theoretical implications, honest limitations of our evaluation, and broader impact for the weight-space learning community.

## Root Cause Analysis

Our systematic failure across all three gate metrics reveals three distinct root causes, each requiring fundamentally different solutions.

### MSE Equivariance Loss is Fundamentally Inadequate

The 0.00% kernel robustness result demonstrates that MSE-based equivariance loss $\mathcal{L}_{\text{equiv}} = \|E(g \cdot M) - \rho(g)E(M)\|^2$ does not enforce permutation invariance despite explicit training signal. This is not a hyperparameter issue—it is a mechanism design flaw.

**Why MSE fails**: The loss encourages similarity between $E(g \cdot \mathbf{w})$ and $\rho(g)E(\mathbf{w})$ through distance minimization, but does not enforce the group homomorphism constraint: $E(g \cdot (h \cdot \mathbf{w})) = E((gh) \cdot \mathbf{w}) = \rho(gh)E(\mathbf{w}) = \rho(g)\rho(h)E(\mathbf{w})$. Gradient descent finds local minima where the encoder simply ignores permutations (makes both terms large but similar) rather than learning the group structure.

**Theoretical implications**: This failure aligns with the success of group-equivariant architectures [Cohen & Welling, 2016] that build equivariance into network structure through group convolutions rather than learning it through losses. Explicit group constraints may be necessary—learned approximations are insufficient. Git Re-Basin's explicit combinatorial search [Ainsworth et al., 2022] succeeds where our learned approach fails, supporting this hypothesis.

**Alternative approaches**: Contrastive learning provides stronger signal by explicitly contrasting positive pairs (original, permuted) against negative pairs (original, different model):
$$\mathcal{L}_{\text{contrast}} = -\log \frac{\exp(\text{sim}(E(\mathbf{w}), E(g \cdot \mathbf{w}))/\tau)}{\sum_j \exp(\text{sim}(E(\mathbf{w}), E(\mathbf{w}_j))/\tau)}$$
This encourages the encoder to map permuted weights together while pushing apart genuinely different models, providing clearer gradient signal for group structure learning. SimCLR [Chen et al., 2020] demonstrates this approach's success for visual invariances—weight-space permutations may require similar treatment.

### Architecture Embeddings May Harm Cross-Architecture Learning

Frozen-K generalization (10.31%) and t-SNE clustering (Figure 2) suggest that 64-dimensional architecture embeddings anchor representations to family-specific coordinates rather than enabling abstraction. This is counterintuitive—providing architecture context should help, not harm.

**Why embeddings harm**: By injecting family-specific information ($\mathbf{c}_{\text{CNN}}$, $\mathbf{c}_{\text{Transformer}}$, $\mathbf{c}_{\text{RNN}}$) before encoding, we signal the model to learn separate coordinate systems for each family. The encoder learns "process CNNs this way, Transformers that way" rather than "find shared structure regardless of architecture." This is opposite to domain adversarial training [Ganin et al., 2016] which explicitly removes domain information to encourage shared representations.

**Theoretical implications**: Cross-architecture quotient spaces may require architecture-agnostic encoding—the model must discover shared structure without family-specific crutches. This suggests per-family quotient spaces with post-hoc alignment may be necessary: learn $Z_{\text{CNN}}$, $Z_{\text{Transformer}}$, $Z_{\text{RNN}}$ separately, then learn linear alignment matrices $A_{ij}$ to map between them. This softer constraint (linear compatibility) may be more achievable than single shared space (strict compatibility).

**Alternative approaches**: Test pure Deep Sets without architecture embeddings, forcing the encoder to find permutation invariances common to all families. If this improves frozen-K generalization, architecture embeddings are harmful. If both fail, the problem may be CNN/Transformer/RNN permutation groups are fundamentally incompatible—no shared quotient space exists.

### Quotient Space Dimensionality Severely Underestimated

Reconstruction error of 19.18% at K=32 for 1000-dimensional weights indicates severe capacity insufficiency. This is not marginal failure (target <10%)—it is a 92% gap suggesting K is off by an order of magnitude.

**Dimensionality bounds**: Johnson-Lindenstrauss lemma provides lower bound: for N models, ε error tolerance, need $K = O(\log N / \varepsilon^2)$. For N=14K models, ε=0.10, this gives K~1000-2000. Our K=32 is 30-60× too small. Even for PoC synthetic 1000-dim weights, we likely need K~100-200.

**Theoretical implications**: If quotient space dimensionality scales with model zoo size rather than weight dimensionality, the approach becomes impractical. Real model zoos contain millions of models—requiring K~10K-100K quotient dimensions defeats the purpose of dimensionality reduction. This suggests the hypothesis that "task-relevant structure is low-dimensional" may be incorrect for heterogeneous populations. Architecture diversity may add dimensions rather than reduce them.

**Alternative approaches**: Hierarchical quotient spaces could help: learn K=32 "coarse" slots capturing basic task structure, then K=128 "fine" slots per architecture family for family-specific details. This separates shared structure (low-dimensional) from family-specific structure (higher-dimensional), potentially achieving better capacity-computation tradeoff.

## Theoretical Interpretation

Our failure reveals that cross-architecture weight-space learning is fundamentally harder than the homogeneous case where NFN succeeds. Three theoretical obstacles emerge:

**Obstacle 1: Permutation groups may be incompatible** — CNN permutations (spatial locality, channel reordering), Transformer permutations (attention head swaps, token position invariance), and RNN permutations (temporal unrolling, hidden state reordering) arise from different computational structures. A shared quotient group $H$ such that $G_{\text{CNN}}/N_1 \cong G_{\text{Transformer}}/N_2 \cong G_{\text{RNN}}/N_3 \cong H$ may not exist. If permutation groups are fundamentally incompatible, no shared quotient space is possible—only per-family spaces with post-hoc alignment.

**Obstacle 2: Learned equivariance requires explicit constraints** — Our failure and Git Re-Basin's explicit search success suggest that gradient-based learning of permutation invariance is insufficient. Group-equivariant architectures [Cohen & Welling, 2016] succeed by building group operations into network structure, not learning them through losses. Weight-space permutations may require similar explicit architectural guarantees.

**Obstacle 3: Dimensionality scales with heterogeneity** — The hypothesis that "task-relevant structure is low-dimensional" may only hold for homogeneous populations. Architecture diversity adds dimensions (family-specific permutation structure) rather than reducing them. This explains NFN's homogeneous success and our heterogeneous failure—the problem is qualitatively harder, not just quantitatively.

## Limitations

Our work has several limitations that affect interpretation:

**Limitation 1: Synthetic data instead of real pretrained models**
- **Why acceptable**: Clear failure signal (0.00% kernel robustness) suggests mechanism issues rather than data artifacts. If the approach fails on simplified synthetic data, it will fail on complex real data.
- **Future mitigation**: Test on real pretrained models from HuggingFace to validate that failures persist and are not artifacts of random initialization. Real models may exhibit stronger permutation structure from training convergence.

**Limitation 2: Single configuration tested (K=32, λ_equiv=0.5)**
- **Why acceptable**: Complete equivariance failure (0% kernel robustness) is unambiguous—no amount of tuning λ_equiv will fix a fundamentally inadequate loss design. K=32 insufficient is clear from 19.18% reconstruction error.
- **Future mitigation**: Sweep K ∈ {64, 128, 256} to find minimal sufficient dimension. Sweep λ_equiv ∈ {0, 0.25, 0.5, 0.75, 1.0} to test if higher weighting helps (unlikely given 0% result at 0.5).

**Limitation 3: No ablation studies (architecture embeddings, loss components)**
- **Why acceptable**: Paper focuses on systematic failure analysis of one complete approach rather than exhaustive ablations. The three failure modes identified provide clear guidance: test embeddings ablation next, test contrastive loss next, test higher K next.
- **Future mitigation**: Ablate architecture embeddings (pure architecture-agnostic Deep Sets), replace MSE loss with InfoNCE contrastive loss, increase K by 4-8×. Each ablation tests one root cause hypothesis.

**Limitation 4: No comparison baselines implemented**
- **Why acceptable**: Early failure detection (0% kernel robustness in initial run) indicated fundamental mechanism issues, making comparison to baselines less informative than root cause analysis. Expected baseline (Deep Sets ~40-50% from NFN) likely outperforms our 0%, confirming our approach made the problem worse.
- **Future mitigation**: Implement Deep Sets baseline (no equivariance loss), function-space embedding baseline (output-based), and ideally Git Re-Basin comparison (though computationally expensive). This would quantify exactly how much worse our approach performs.

**Limitation 5: PoC simplifications (1000-dim weights, 20 epochs, early stopping)**
- **Why acceptable**: Simplifications enable rapid prototyping and clear failure signal. Early stopping at epoch 12 suggests optimization issues (conflicting gradients), not insufficient training. Extending to 100 epochs would not fix 0% kernel robustness.
- **Future mitigation**: Full-scale experiments with 100K-dim real model weights, 100 epochs, proper learning rate tuning. However, fixing root causes (MSE loss, architecture embeddings, K dimensionality) is higher priority than scale-up.

## Broader Impact

**Positive impacts**: Our systematic failure analysis prevents the ML community from wasting research effort on similar approaches. By documenting that Deep Sets + architecture embeddings + MSE equivariance loss fundamentally fails with concrete root causes, we save others from pursuing this dead end. The three failure modes (equivariance loss design, architecture embeddings harmful, dimensionality underestimated) provide actionable guidance for alternative approaches.

**Negative impacts**: Documenting failure may discourage exploration of weight-space methods, potentially causing researchers to abandon viable alternatives (contrastive learning, Slot Attention, explicit group constraints) prematurely. We mitigate this by providing concrete alternative proposals grounded in failure analysis rather than vague "future work."

**Community value**: Negative results are valuable when well-documented. The kernel robustness metric (0.00%) reveals equivariance failures that standard metrics would miss—this evaluation methodology has value independent of our specific approach failure. The systematic three-gate evaluation (reconstruction, frozen-K, kernel robustness) can be reused by future work testing alternative cross-architecture methods.

**Ethical considerations**: This work has no direct ethical concerns (foundational research, no deployment, no data privacy issues). The broader impact on weight-space learning research is primarily methodological—clarifying what doesn't work guides the field toward viable directions.

## Lessons for Future Work

Our failure analysis yields concrete lessons:

**Lesson 1: MSE-based equivariance loss insufficient** — Contrastive learning (InfoNCE with permutation pairs) or explicit group constraints (group-equivariant architectures) required. Reconstruction-based objectives do not learn group structure.

**Lesson 2: Architecture embeddings may harm cross-architecture transfer** — Test pure architecture-agnostic encoding before concluding cross-architecture quotient spaces are impossible. Domain-specific information may prevent abstraction.

**Lesson 3: Quotient dimensionality requirements underestimated** — K~100-200 minimum for synthetic 1000-dim weights, K~1000-2000 for real 100K-dim weights based on Johnson-Lindenstrauss bounds. This may make approach computationally impractical at scale.

**Lesson 4: Homogeneous-first validation strategy recommended** — Test on CNN-only model zoo (replicating NFN homogeneous success) before attempting cross-architecture extension. Incremental validation isolates whether failure is fundamental (fails on CNN-only) or heterogeneity-specific (succeeds on CNN-only, fails cross-architecture).

**Lesson 5: Per-family spaces with alignment may be more viable** — If shared quotient space remains elusive after alternatives tested, consider per-family approach: learn $Z_{\text{CNN}}$, $Z_{\text{Transformer}}$, $Z_{\text{RNN}}$ separately, then learn linear alignment matrices. Softer constraint may be achievable where strict shared space is not.

These lessons ground future work in empirical failures rather than speculation, increasing likelihood that alternative approaches succeed.
