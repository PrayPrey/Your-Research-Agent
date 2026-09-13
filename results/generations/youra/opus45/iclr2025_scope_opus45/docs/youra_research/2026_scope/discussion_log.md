# Phase 2A: Research Discussion Log

## Metadata
- **Gap ID**: GAP-001
- **Gap Title**: LoRA Cannot Directly Adapt SSM-Specific Modules (A, B, C, D / Time-Mixing)
- **Start Time**: 2026-03-27T19:45:00Z
- **Architecture**: Self-Contained Tikitaka Loop v9.0.0
- **Execution Mode**: UNATTENDED

## Discussion Briefing

### Research Gap

**Gap 1: LoRA Cannot Directly Adapt SSM-Specific Modules (A, B, C, D / Time-Mixing)**

**Relevance Classification:** PRIMARY (Critical Priority)

**Connection to Research Question:**
- Blocks answering research question: LoRA targets linear projections, but SSM state dynamics are governed by A, B, C, D matrices (Mamba) or time-mixing (RWKV) which are NOT standard linear layers
- Relates to detailed question: "State Dynamics Under LoRA" cannot be fully answered if LoRA doesn't reach SSM modules

**Current State:**
Existing LoRA implementations for SSMs (MambaPEFT, RWKV-PEFT) apply LoRA to input/output projections but NOT to the core SSM state transition matrices. SDT (ICML 2025) identifies that SSM modules require specialized treatment.

**Missing Piece:**
No systematic study of how LoRA-style low-rank updates to SSM-specific parameters (A, B, C, D matrices in Mamba; time-mixing in RWKV) affect state dynamics and task adaptation.

**Potential Impact:**
High - Without understanding LoRA effects on SSM core modules, we cannot optimize parameter-efficient fine-tuning for SSM architectures.

### Phase 1 Key Findings

From `01_targeted_research.md`:

1. **LoRA-SSM Architectural Mismatch**: Standard LoRA targets linear projection matrices (W_q, W_k, W_v in Transformers), but SSM state dynamics are governed by specialized modules (A, B, C, D in Mamba; time-mixing in RWKV) that are NOT standard linear layers.

2. **Emerging SSM-PEFT Methods** (2024-2025):
   - **SDT (ICML 2025)**: Sparse Dimension Tuning for SSM modules
   - **State-offset Tuning (ACL 2025)**: Direct state modification (h' = h + offset)
   - **SSMLoRA (arXiv 2025)**: Integrating SSM structure with LoRA matrices

3. **Key Finding from MambaPEFT (ICLR 2025)**:
   - PEFT performs MORE effectively for Mamba than Transformers
   - LoRA effective for linear projections but FAILS on SSM modules directly

4. **Key Finding from SSM-PEFT (ICML 2025)**:
   - LoRA and variants consistently outperform other PEFT methods on SSMs
   - LoRA effective for linear projections but FAILS on SSM modules directly
   - Proposes Sparse Dimension Tuning (SDT) for SSM modules

5. **Previous Failure Context (h-m2)**:
   - Cross-architecture MQAR evaluation is NOT valid with pretrained models
   - SSMs need fine-tuning to adapt to new tasks
   - Focus on single architecture with controlled fine-tuning conditions

### Available Papers

(Referenced from Phase 1 - no new downloads needed)
- LoRA (Hu et al., 2021) - arXiv:2106.09685
- Mamba (Gu & Dao, 2023) - arXiv:2312.00752
- SSMLoRA (Yu et al., 2025) - arXiv:2502.04958
- SSM-PEFT / SDT (Galim et al., 2024) - ICML 2025
- MambaPEFT (Yoshimura et al., 2024) - ICLR 2025
- State-offset Tuning (Kang et al., 2025) - ACL 2025

### Research Repos

- https://github.com/furiosa-ai/ssm-peft (SDT method - ICML 2025)
- https://github.com/sony/MambaPEFT (20 PEFT variations - ICLR 2025)
- https://github.com/Joluck/RWKV-PEFT (Production RWKV LoRA - 179★)
- https://github.com/furiosa-ai/ssm-state-tuning (State-offset Tuning - ACL 2025)

### Feasibility Constraints (Pipeline-Enforced)

**MANDATORY CONSTRAINTS:**
- Reject ideas requiring new benchmarks, rubrics, or scoring frameworks
- Reject ideas requiring synthetic/generated data or future follow-up data
- Reject ideas requiring human evaluation, annotation, or subjective scoring
- Accept only hypotheses testable immediately using existing real datasets and existing benchmarks

**Available Resources:**
- Models: Mamba-1.4B, RWKV-6-1.6B (publicly available)
- Benchmarks: LongBench, GLUE, SuperGLUE (existing)
- Metrics: Task accuracy, perplexity, state rank (objective, automated)

---

### Exchange 1

🔭 **Dr. Nova** (Creative Novelty Explorer):

What an exciting research gap we have here! The fundamental issue is clear: standard LoRA was designed for Transformer attention matrices (W_q, W_k, W_v), but SSMs operate on an entirely different computational paradigm with their A, B, C, D state transition matrices. Let me propose some unconventional angles.

**First wild idea:** What if the "failure" of LoRA on SSM modules isn't a bug but a *feature*? Consider this — SSM-PEFT (ICML 2025) and MambaPEFT (ICLR 2025) both found that LoRA on linear projections *alone* achieves surprisingly good results. What if the SSM state dynamics are already efficient enough that they don't *need* direct adaptation? The state transition matrices (A, B, C, D) might be learning a universal dynamics grammar, while task-specific knowledge can be fully captured in the input/output projections.

**Second paradigm shift:** Instead of trying to make LoRA work on SSM modules directly, what if we exploit the *sequential dependency* between SSM layers? In Transformers, attention layers are relatively independent. But in SSMs, the recurrent state flows sequentially. Could we design a "State-Flow LoRA" where low-rank updates to early layer projections propagate through the state dynamics to affect later layers? This could achieve SSM-core adaptation *indirectly* without modifying A, B, C, D.

**Third cross-domain connection:** State-offset Tuning (ACL 2025) modifies states directly with h' = h + offset. This reminds me of residual connections in ResNets! What if we combine this with LoRA — not as alternatives but as *complementary* mechanisms? LoRA adapts the projection space, state-offset adapts the state space. Together they could cover both computational dimensions.

**Key Points:**
- SSM state matrices might intentionally resist adaptation (universal dynamics hypothesis)
- Sequential state flow could enable indirect SSM-core adaptation via projections
- Hybrid LoRA + State-offset could be more powerful than either alone

---

### Exchange 2

🔬 **Prof. Vera** (Rigorous Validation Architect):

The "universal dynamics" hypothesis is intriguing. However, the evidence suggests we currently lack a falsifiable formulation. If the SSM state matrices \(A, B, C, D\) truly encode task-agnostic dynamics, then the hypothesis makes a clear prediction: **direct low-rank perturbations to these matrices should yield negligible gains relative to projection-only LoRA across diverse downstream tasks.** What would disprove this? A controlled experiment where rank-matched LoRA applied to \(A\) or \(B\) produces statistically significant improvement over projection-only LoRA on at least one task family (e.g., long-context reasoning or algorithmic sequence modeling). The null hypothesis should be that SSM-core adaptation is redundant. We must define success as a pre-registered improvement margin (e.g., ≥1.5% absolute on benchmark X with p < 0.01 across seeds).

Regarding "State-Flow LoRA," the mechanistic claim is that early-layer projection updates propagate through recurrent state dynamics and induce effective modification of downstream state trajectories. This is testable. We can instrument hidden state trajectories \(h_t^{(l)}\) under three conditions: (1) frozen base model, (2) projection-only LoRA, (3) direct SSM-core LoRA. Compute trajectory divergence metrics (e.g., Wasserstein distance or CKA similarity) relative to the base. If projection-only LoRA produces state trajectory shifts comparable in magnitude to direct SSM-core adaptation, your indirect adaptation claim gains support. If not, the mechanism fails. We must also control for parameter count and effective rank to avoid confounding capacity with placement.

On the proposed hybrid of LoRA + state-offset tuning: the central question is whether these methods are additive or redundant. The best experiment here is a factorial design: {projection LoRA on/off} × {state-offset on/off}. Four conditions, identical parameter budgets. If interaction terms in an ANOVA are significant, this indicates non-redundant mechanisms. Additionally, we should probe stability. State offsets modify \(h_t\) directly; if combined with LoRA, we risk destabilizing recurrent dynamics. Measure spectral radius of the effective transition Jacobian and gradient norm growth across timesteps. If hybrid tuning increases instability metrics without proportional accuracy gain, it fails the robustness criterion.

One edge case deserves attention: tasks with extreme temporal extrapolation (e.g., 4× pretraining context length). If SSM-core parameters encode long-range inductive bias, then direct adaptation of \(A\) should disproportionately affect extrapolation performance. Thus, a clean stress test is: fine-tune on short contexts, evaluate on long contexts. If projection-only LoRA matches SSM-core LoRA under extrapolation, the "universal dynamics" hypothesis strengthens. If not, it is weakened.

In summary, each proposal is scientifically viable only if paired with a disconfirmation pathway. The decisive question is not whether these ideas are elegant, but whether they produce measurable, mechanism-specific effects under controlled comparison.

**Key Points:**
- Define falsifiable predictions: SSM-core LoRA must outperform projection-only LoRA to reject the "universal dynamics" hypothesis.
- Measure hidden state trajectory divergence to test whether projection LoRA indirectly modifies state dynamics.
- Use factorial experiments and stability metrics to determine whether LoRA + state-offset are complementary or redundant.

---

### Exchange 3

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let's ground these proposals in technical reality. 🔬 Prof. Vera's experimental framework is rigorous, but we need to examine whether the proposed mechanisms are even *physically possible* given SSM architecture constraints.

**On the "universal dynamics" hypothesis testing:** The key technical question is whether we *can* apply LoRA to SSM-core matrices A, B, C, D. Looking at MambaPEFT (ICLR 2025) and SSM-PEFT (ICML 2025), the answer is nuanced. In Mamba, the A matrix is derived from a structured parameterization (discretization of continuous dynamics), and B, C are often computed from input projections via selective scan. These aren't simple weight matrices — they're *computed* parameters. Directly injecting LoRA into A requires modifying the discretization step (Δ, A → Ā), which changes the theoretical interpretation. The experiment is feasible, but we must be precise: we're testing LoRA on the *parameters that generate* A, B, C, not on A, B, C directly.

**On State-Flow LoRA and trajectory divergence:** The mechanism is physically sound. SSM states evolve as h_t = Āh_{t-1} + B̄x_t, so modifying input projections (which affect x_t fed to B̄) will indeed propagate through state dynamics. However, here's what worries me: the *magnitude* of trajectory divergence may be dominated by the recurrent eigenvalues of Ā. If Ā has eigenvalues close to 1 (long memory), small input perturbations accumulate; if eigenvalues are small (fast decay), perturbations wash out quickly. The "indirect adaptation" hypothesis implicitly assumes sufficient state persistence. We can verify this by computing the spectral properties of Ā for Mamba-1.4B — if dominant eigenvalues indicate fast decay, the State-Flow mechanism is theoretically weak.

**On LoRA + State-offset hybrid stability:** This is where I have the most concern. State-offset tuning adds a learned offset to h_t directly. Combined with LoRA on projections, we now have two interference points in the state evolution equation. The stability analysis 🔬 Prof. Vera proposed (spectral radius, gradient norms) is essential, but let me add: the *interaction* between these two adaptations could create unstable feedback loops. Consider: LoRA changes how x_t is computed → different h_t trajectory → but state-offset is trained assuming the *base* trajectory. If we co-train, the optimization landscape may have many local minima. This isn't a fatal flaw, but it means we need careful initialization and possibly staged training (first LoRA, then state-offset, then fine-tune jointly).

**Feasibility verdict:** All three mechanisms are *scientifically* possible. The key barriers are:
1. **A/B/C/D LoRA:** Requires modifying Mamba's discretization code — non-trivial but doable with MambaPEFT codebase
2. **Trajectory analysis:** Standard instrumentation, existing tools (hooks in PyTorch)
3. **Hybrid training:** Needs careful optimization protocol to avoid instability

What would convince me this is viable: a pilot study on a small model (Mamba-130M or RWKV-430M) showing stable training and non-degenerate solutions for each configuration.

**Key Points:**
- LoRA on SSM-core requires modifying discretization parameters, not the matrices directly — this changes the interpretation
- State-Flow mechanism depends on SSM eigenvalue structure; need to verify sufficient state persistence
- Hybrid LoRA + state-offset needs staged training protocol to avoid optimization instability

---

### Exchange 4

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Good — this is getting sharper. But here's where this still breaks down: you are circling mechanisms without committing to a *clear differentiating claim* from existing SSM-PEFT methods. SSM-PEFT (ICML 2025) and MambaPEFT (ICLR 2025) already show projection-only LoRA works well. So what exactly are you claiming that is not already implicit in their results? If your "universal dynamics" hypothesis is true, then projection-only LoRA should be *consistently sufficient* across task families — not just "surprisingly good." I want a formal statement: **For any task within distribution D, SSM-core adaptation yields ≤ ε improvement over projection-only LoRA at matched parameter count.** Pick ε. Make it uncomfortable. 0.5%? 1%? Without that, this is philosophy, not science.

Now, about the "State-Flow LoRA" idea. You're assuming projection updates meaningfully alter recurrent state trajectories. Prof. Pax correctly flagged eigenvalues — and here's the deeper issue: what if the SSM is *contractive*? If the spectral radius of Ā < 1 with significant margin, then perturbations from modified input projections decay exponentially. In that case, indirect adaptation cannot substitute for modifying A itself. So here's what would convince me: measure the empirical Lyapunov time or effective memory horizon of each layer. Then show that projection-only LoRA induces trajectory divergence that *persists beyond that horizon*. If divergence collapses quickly, your mechanism is dead.

On the hybrid LoRA + state-offset proposal — right now it's hand-wavy synergy. Show me non-redundancy. A factorial ANOVA is good, but insufficient. I want representational diagnostics. For each method alone and combined, compute:
1. CKA similarity to base states
2. Fisher Information overlap between adapted parameters
3. Gradient attribution to downstream loss

If LoRA and state-offset update orthogonal subspaces (low overlap in Fisher or gradient directions), then you have mechanistic complementarity. If they overlap heavily, you're just paying twice for the same degrees of freedom.

Here's another uncomfortable question: what is the *failure case*? Where does projection-only LoRA provably break? My bet: tasks requiring extrapolation beyond training-time stability margins (e.g., 8× context generalization) or tasks that shift temporal frequency spectra. If A encodes spectral filtering properties, then adapting projections cannot change the system's frequency response. That's your strongest theoretical wedge. Compute the transfer function of the linearized SSM before and after projection-only LoRA. If it's invariant, then you've proven a hard limitation. If it shifts, then the "universal dynamics" hypothesis collapses.

Finally, real-world impact. Why does this matter beyond academic nuance? If projection-only LoRA is sufficient, then we gain a principled argument for *never touching recurrent dynamics*, preserving stability and enabling drop-in PEFT for safety-critical systems. If not, then we identify a concrete class of tasks where SSM-core adaptation is worth the engineering cost. Frame the hypothesis around that decision boundary.

Right now you have good ideas. What you need is a sharp, falsifiable dividing line between:
- "Dynamics are universal; adapt only interfaces"
vs.
- "Dynamics encode task-specific spectral structure; must adapt core."

Define that boundary, and now we're doing serious science.

**Key Points:**
- Formalize the "universal dynamics" hypothesis with a quantitative ε-bound on SSM-core gains.
- Test indirect adaptation via persistence of trajectory divergence relative to the SSM's memory horizon and spectral properties.
- Prove or disprove LoRA + state-offset complementarity using Fisher overlap and representational diagnostics, not just accuracy gains.

---

### Exchange 5

🎯 **Dr. Sage** (Research Impact Evaluator):

The question we must ask is: what makes this research genuinely contribute to the field, rather than being an incremental benchmark exercise? 🔍 Prof. Rex has correctly identified that we need a sharp dividing line. Let me reframe this from the perspective of scientific significance.

**What's at stake for the field:** The deep learning community is at a crossroads with sub-quadratic architectures. SSMs (Mamba, RWKV) promise linear-time inference, but their adaptation story is incomplete. If we can prove that projection-only LoRA is *provably sufficient* for a well-defined task class, we establish a foundational principle: **SSM dynamics are task-agnostic representations, and all task-specific knowledge lives in the interface layers.** This would be analogous to the discovery that CNN filters learn universal edge detectors — it changes how we think about the architecture.

Conversely, if we identify *specific task classes* where SSM-core adaptation is necessary, we've discovered something about the inductive bias encoded in recurrent dynamics. This matters because: (1) it guides practitioners on when to use more expensive PEFT methods, and (2) it reveals what information the state transition matrices encode.

**The contribution hierarchy:** Let me be blunt about impact levels:

1. **Incremental (Low Impact):** "We tried LoRA on SSM modules and it's slightly better/worse" — this adds data points but no insight.

2. **Moderate Impact:** "We characterize the eigenvalue/spectral conditions under which projection-only LoRA matches SSM-core LoRA" — this is useful engineering knowledge.

3. **High Impact (What we should aim for):** "We prove a theoretical bound: for tasks with temporal frequency spectrum contained in [f_min, f_max], projection-only LoRA achieves ε-optimal adaptation. Outside this spectrum, SSM-core adaptation is necessary and sufficient." This would be a *principled separation theorem*.

**Connecting to the literature:** The SSM-PEFT paper (ICML 2025) showed LoRA fails on SSM modules and proposes SDT. But they didn't explain *why* — they just showed empirically that sparse dimension tuning works better. State-offset Tuning (ACL 2025) modifies states directly but doesn't connect to the frequency/spectral story. Our contribution would be the *unifying theoretical framework* that explains when each method is appropriate.

**The testable claim I propose:** "SSM projection-only LoRA is sufficient for tasks whose relevant information can be captured within the model's effective memory horizon. For tasks requiring information integration beyond this horizon, SSM-core adaptation (via discretization parameters) is necessary." This is falsifiable via the extrapolation experiments 🔬 Prof. Vera proposed.

**What new research directions this opens:**
- Principled PEFT method selection based on task characteristics
- Understanding what SSM state dynamics actually encode
- Design guidelines for hybrid Transformer-SSM architectures (when to adapt which components)

This matters because it moves us from "try everything and see what works" to principled architecture-aware adaptation.

**Key Points:**
- The core contribution should be a *separation theorem* defining task classes where projection-only vs SSM-core adaptation is optimal
- This explains the *why* behind existing empirical results (SSM-PEFT, State-offset Tuning)
- Impact comes from providing principled guidance, not just benchmark numbers

---

### Exchange 6

🔬 **Prof. Vera** (Rigorous Validation Architect):

We are converging on the correct axis of inquiry: not "does it work?" but **under what measurable conditions does it fail?** I will formalize the universal dynamics hypothesis in a way that admits disconfirmation.

Let \( \mathcal{T}(H) \) denote the class of tasks whose mutual information between target and input is concentrated within an effective memory horizon \( H \), defined empirically as the timestep where the impulse response of the linearized SSM decays below 5% of peak magnitude. The hypothesis becomes:
> For any task \( T \in \mathcal{T}(H_{\text{base}}) \), projection-only LoRA achieves performance within ε of SSM-core adaptation at matched parameter count, where ε ≤ 1.0% absolute accuracy (or ≤ 2% relative perplexity), averaged over ≥5 seeds with p < 0.01.

This is deliberately strict. What would disprove this? A single task demonstrably within \( H_{\text{base}} \) where SSM-core LoRA exceeds projection-only LoRA by >ε under controlled capacity and optimization settings. Conversely, for tasks with signal extending beyond \( H_{\text{base}} \) (e.g., synthetic copy/reverse at 4× context), the hypothesis predicts ε will be violated. That defines the decision boundary.

On the spectral argument raised by Prof. Rex: the frequency-response claim is testable. Linearize each SSM layer around operating statistics and compute its discrete-time transfer function \( G(z) = C(zI - \bar{A})^{-1}B \). Projection-only LoRA modifies input/output maps but not \( \bar{A} \); therefore, under first-order approximation, pole locations (hence system memory and resonant frequencies) remain invariant. The prediction is precise: **projection-only LoRA may change gain but not pole structure.** If empirical system identification (via impulse probing before and after fine-tuning) reveals statistically significant pole shifts, then the "interface-only" claim is false. This gives us a mechanistic Achilles' heel.

Regarding trajectory persistence: I propose we quantify divergence half-life. For a fixed input perturbation induced by LoRA, compute \( D(t) = \| h_t^{\text{LoRA}} - h_t^{\text{base}} \|_2 \), and fit an exponential decay \( D(t) \sim e^{-t/\tau} \). If \( \tau \) matches the base model's intrinsic memory constant, then projection-only LoRA does not extend temporal credit assignment. If SSM-core adaptation increases \( \tau \) significantly (Δτ > 20% with p < 0.01), we have direct evidence that core modification alters temporal inductive bias. This operationalizes the "memory horizon" boundary proposed by Dr. Sage.

Finally, on hybrid LoRA + state-offset: complementarity must be demonstrated structurally, not anecdotally. I support the Fisher overlap analysis suggested by Prof. Rex. Concretely, compute the empirical Fisher \( F_\theta \) for projection LoRA parameters and for state-offset parameters separately. If the principal subspaces have cosine similarity >0.8, they are functionally redundant. Additionally, perform ablation under distribution shift (e.g., context extrapolation). The prediction from the separation theorem is that hybrid methods only outperform when tasks straddle the boundary of \( H_{\text{base}} \); otherwise gains should be ≤ε. If hybrid wins uniformly, the entire boundary hypothesis collapses.

The evidence will either show a clean separation aligned with spectral/memory metrics, or it will reveal that adaptation mechanisms blur these distinctions. In either case, we will have transformed an architectural intuition into a falsifiable framework.

**Key Points:**
- Formalized a strict ε-bounded "universal dynamics" hypothesis tied to an empirically measured memory horizon \( H \), with explicit disconfirmation criteria.
- Proposed transfer-function and pole analysis to test whether projection-only LoRA preserves SSM spectral structure.
- Defined quantitative divergence half-life (τ) and Fisher-overlap diagnostics to determine whether SSM-core or hybrid adaptations alter temporal inductive bias or are mechanistically redundant.

---

### Exchange 7

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

YES — now we're building something robust! Let me synthesize what we've developed and strengthen it against the concerns raised. 🔬 Prof. Vera's formalization is exactly what we needed. Here's how I see the hypothesis crystallizing:

**The Memory Horizon Separation Hypothesis (MHSH):**

*Core Claim:* SSM state dynamics encode a task-agnostic temporal processing grammar with characteristic memory horizon H_base. For tasks whose relevant information dependencies fall within H_base, projection-only LoRA achieves ε-optimal adaptation (ε ≤ 1.0% accuracy). For tasks requiring information integration beyond H_base, SSM-core adaptation (via discretization parameters) is necessary to extend the effective memory horizon.

**Addressing 🔍 Prof. Rex's concerns:**

1. **"What differentiates this from existing SSM-PEFT results?"** — Existing work (MambaPEFT, SSM-PEFT) shows *what* works empirically but not *why*. Our contribution is the *separation theorem* based on memory horizon. This transforms ad-hoc method selection into principled guidance.

2. **"Where's the failure case?"** — We've identified it: tasks requiring extrapolation beyond H_base. Concretely: (a) Long-context reasoning where relevant facts appear >H_base tokens apart, (b) Algorithmic tasks like copy/reverse at 4× training context, (c) Any task where the transfer function's pole structure matters.

**Strengthening the experimental design:**

Building on 🔬 Prof. Vera's framework and ⚙️ Prof. Pax's feasibility analysis, here's a concrete experimental plan:

*Phase 1 — Characterize H_base:*
- Measure impulse response decay (5% threshold) for each Mamba layer
- Compute transfer function G(z) and extract pole locations
- This gives us the intrinsic memory horizon

*Phase 2 — Within-horizon tasks:*
- Standard NLU benchmarks (GLUE, SuperGLUE) — short-context
- LongBench subsets where relevant context is within H_base
- Prediction: projection-only LoRA matches SSM-core LoRA (Δ ≤ ε)

*Phase 3 — Beyond-horizon tasks:*
- LongBench subsets requiring 4× context integration
- Synthetic copy/reverse tasks at extrapolation lengths
- Prediction: SSM-core LoRA outperforms projection-only LoRA (Δ > ε)

*Phase 4 — Mechanistic validation:*
- Divergence half-life τ measurement before/after adaptation
- Pole analysis via system identification
- Fisher overlap for hybrid method complementarity

**What evidence would strengthen vs. weaken this hypothesis:**

*Strengthens:* Clean separation where within-horizon tasks show Δ ≤ ε and beyond-horizon tasks show Δ > ε, with spectral analysis confirming pole invariance under projection-only LoRA.

*Weakens:* (a) Within-horizon tasks where SSM-core substantially outperforms, (b) Beyond-horizon tasks where projection-only still matches, (c) Pole shifts detected under projection-only LoRA.

**The refined hypothesis addresses all raised concerns:** It's falsifiable (quantitative ε bounds), mechanistic (memory horizon + spectral analysis), and practically impactful (guides PEFT method selection).

**Key Points:**
- Synthesized the Memory Horizon Separation Hypothesis (MHSH) with clear core claim
- Mapped specific task classes to within-horizon (projection-only sufficient) vs beyond-horizon (SSM-core necessary)
- Proposed 4-phase experimental plan with explicit strengthening/weakening evidence criteria

---

### Exchange 8

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Good. MHSH is finally sharp enough to attack. Now let me try to break it.

First fracture line: **identifiability of \( H_{\text{base}} \).** You define it via impulse response decay to 5% of peak. Why 5%? Why not 1% or 10%? That threshold will move your separation boundary. If your theory depends on a heuristic cutoff, reviewers will call it post-hoc fitting. What would convince me is a robustness analysis: sweep the decay threshold from 1–20% and show the task classification (within vs. beyond horizon) is invariant. If small perturbations in the definition of \( H_{\text{base}} \) flip tasks across the boundary, your "separation theorem" is just a measurement artifact.

Second: you're assuming the *linearized* transfer function meaningfully captures behavior during fine-tuning. But SSMs in practice are wrapped with nonlinearities, gating, normalization. Linearization around operating statistics may not reflect dynamics under task-specific activation distributions. Show me this: compute poles from system identification **before and after fine-tuning**, not just from analytic linearization. If projection-only LoRA preserves pole locations under empirical identification, then your spectral invariance claim holds water. If poles drift because the operating point shifts, your "interface-only" premise collapses.

Now let's pressure-test the core claim: that projection-only LoRA cannot extend memory horizon. Here's a counter-mechanism. Even if \( \bar{A} \) is fixed, LoRA can reweight inputs so that relevant signals align with the slowest decaying eigenmodes. That effectively *increases usable memory* without changing poles. Your τ-divergence metric must distinguish between (a) changing decay constants and (b) redistributing energy into slow modes. What would convince me is a modal decomposition: project state trajectories onto eigenvectors of \( \bar{A} \) and measure energy concentration. If projection-only LoRA shifts mass toward slow modes without altering eigenvalues, then it may solve beyond-horizon tasks without core modification. That's a serious threat to MHSH.

Third stress test: task definition. You're using mutual information concentration within \( H_{\text{base}} \). Fine — but how are you estimating that MI in real NLP tasks? If this is approximated via attention-distance heuristics or gradient attribution, say so. Otherwise this becomes unfalsifiable because you can always claim a task was "actually beyond horizon." Pre-register the classification rule. For synthetic tasks it's clear; for LongBench-style data it isn't.

Finally, here's the make-or-break experiment. Train on context length L. Test on 2L, 4L, 8L. For each adaptation method, measure (1) accuracy dropoff curve, (2) estimated τ, and (3) pole locations. The MHSH predicts:
- Projection-only: flat τ, invariant poles, sharp accuracy cliff past \( H_{\text{base}} \).
- Core adaptation: increased τ, shifted poles, delayed accuracy cliff.

If instead projection-only shows graceful degradation and no τ change, your boundary is wrong. If both methods shift poles under identification, your invariance premise is wrong. Either way, we learn something real.

Now we're close. But until you (1) make \( H_{\text{base}} \) threshold-robust, (2) empirically validate pole invariance under identification, and (3) rule out slow-mode energy reallocation as a loophole, I'm not convinced this is a theorem rather than a narrative.

Fix those, and I'll say: now you've addressed my concerns.

**Key Points:**
- Demand robustness of the memory-horizon definition; avoid threshold-dependent boundary artifacts.
- Empirically test pole invariance and modal energy redistribution to rule out hidden mechanisms of projection-only adaptation.
- Use controlled context-extrapolation experiments with τ and pole tracking to validate or falsify the separation boundary.

---

### Exchange 9

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

Let me ground 🔍 Prof. Rex's challenges in what's technically achievable. These are sharp critiques, but we need to assess whether the proposed solutions are *actually implementable*.

**On H_base threshold robustness:** This is technically straightforward. The impulse response of a discrete-time SSM layer can be computed analytically: inject δ impulse, record state evolution. The 5% vs 1% vs 10% sweep is just plotting the decay curve and reading off different x-intercepts. The real question is: does Mamba expose internal state cleanly? Looking at the state-spaces/mamba codebase, the selective scan outputs can be hooked, but we need to ensure we're measuring *per-layer* state, not the mixed output. **Verdict:** Feasible with ~1 day of instrumentation work.

**On empirical system identification vs. analytic linearization:** Here's what worries me — system identification from observed input-output pairs requires controlled probing sequences. For a 1.4B parameter model with 48 layers, running enough probe sequences to reliably estimate poles could be expensive. However, there's a middle ground: we can use *local* linearization via Jacobian computation at representative input distributions. PyTorch autograd gives us ∂h_{t+1}/∂h_t directly. This captures the effective dynamics under realistic activations without requiring black-box system identification.

**The modal decomposition challenge:** This is where it gets tricky. To project state trajectories onto eigenvectors of Ā, we need to compute the eigendecomposition of Ā for each layer. For Mamba, Ā is structured (diagonal + low-rank in Mamba-2), so this is tractable. But for RWKV, the "equivalent" dynamics are more implicit in the time-mixing formulation. **Verdict:** Feasible for Mamba, harder for RWKV. I recommend focusing MHSH validation on Mamba-1.4B first.

**On task classification pre-registration:** This is a legitimate concern, but we have a clean solution: use *synthetic* tasks for the core validation. For beyond-horizon: copy/reverse tasks at 2×, 4×, 8× training length — the information dependency is *by construction* beyond any reasonable H_base. For within-horizon: standard NLU where answers are typically within 50-200 tokens of the question. This avoids the MI estimation problem entirely. Natural language benchmarks (LongBench) become *exploratory* — we test predictions without needing to pre-classify.

**Refined experimental design addressing Rex's concerns:**

1. **H_base robustness sweep:** Compute impulse response for all 48 layers, measure H at 1%, 5%, 10%, 20% thresholds. Report distribution and variance.

2. **Pole tracking via Jacobian:** At 3 checkpoints (base, mid-training, final), compute ∂h_{t+1}/∂h_t eigenspectrum for each layer. Compare projection-only vs core LoRA.

3. **Modal energy analysis:** Decompose state trajectories onto Ā eigenbasis. Measure energy concentration in top-k slow modes before/after adaptation.

4. **Context extrapolation test:** Train on L=2K, test on 2K/4K/8K/16K. Measure accuracy, divergence half-life τ, and eigenspectrum shift.

**What's NOT feasible with current resources:**
- Full system identification on 48 layers (too expensive)
- RWKV modal decomposition (implicit dynamics)
- MI estimation for arbitrary NLP tasks (no reliable method)

**What IS feasible:**
- All Mamba-focused experiments above
- Synthetic task validation with known horizon structure
- Jacobian-based local eigenanalysis

The hypothesis is testable on Mamba within reasonable compute. RWKV can be secondary validation if Mamba results are promising.

**Key Points:**
- H_base threshold robustness is straightforward to test via impulse response analysis
- Jacobian-based eigenanalysis is more feasible than full system identification
- Focus primary validation on Mamba with synthetic tasks; natural language benchmarks are exploratory

---

### Exchange 10

🎯 **Dr. Sage** (Research Impact Evaluator):

The question we must ask is not whether MHSH is testable — it clearly is — but whether, if validated, it *changes how this community thinks about adaptation in state-space models*. Right now, most PEFT work in SSMs is empirical pattern-matching: try projection-only, try core, report deltas. What you are proposing is a **structural criterion** — a memory-horizon boundary tied to pole structure — that predicts *in advance* which adaptation locus should matter. This matters because it reframes PEFT selection from an engineering choice to a dynamical systems question. That is a meaningful conceptual advance, if it survives scrutiny.

However, I want to elevate Prof. Rex's slow-mode reallocation critique. If projection-only LoRA can reweight inputs to preferentially excite the slowest eigenmodes of \( \bar{A} \), then the model may effectively extend usable memory without moving poles. If that mechanism holds, your separation is not between "pole-changing" and "non-pole-changing" methods, but between **eigenvalue modification** and **eigenmode utilization**. That is a deeper and more interesting distinction. The field should care because it asks: is temporal generalization limited by spectral geometry, or by how tasks align with that geometry? Your modal energy decomposition experiment becomes central — not ancillary. If energy shifts alone enable extrapolation, then the inductive bias resides in the *distribution of eigenmodes*, not in their locations.

Let me also sharpen the novelty criterion. The memory-horizon threshold must not be a tuning knob. If sweeping 1–20% decay thresholds preserves task partitioning, then you have identified an intrinsic structural property. If not, MHSH risks becoming a descriptive taxonomy. Reviewers will ask: does this generalize beyond Mamba-1.4B? I would therefore require at least one cross-scale validation (e.g., Mamba-370M vs 1.4B) showing that \( H_{\text{base}} \) scales predictably with model size and that the separation boundary scales accordingly. If the boundary shifts arbitrarily with width or depth, the principle is architectural contingency, not scientific law.

What does this mean for the field? If validated, you have established a **dynamical sufficiency theorem for PEFT in SSMs**: projection-only adaptation is sufficient whenever task mutual information lies within the model's intrinsic decay envelope. That would influence how we design long-context models — perhaps encouraging architectures with deliberately tunable pole spectra rather than relying on downstream fine-tuning to stretch memory. Conversely, if falsified — if projection-only routinely handles beyond-horizon tasks via mode reallocation — then we learn something even more profound: that adaptation operates primarily by *basis alignment*, not by altering temporal constants. Either outcome advances theory.

So here is the standard of evidence I would hold you to: (1) threshold-robust horizon estimation, (2) explicit separation of eigenvalue shift vs eigenmode energy redistribution, and (3) scaling validation across at least two model sizes. If you meet those, this is not incremental PEFT benchmarking. It becomes a principled account of where temporal inductive bias lives in SSMs — in poles, in modes, or in their alignment with tasks.

**Key Points:**
- The true contribution is a structural, predictive criterion for PEFT selection based on dynamical memory horizons.
- The eigenvalue vs. eigenmode utilization distinction is central and could redefine where temporal inductive bias resides.
- Cross-threshold robustness and cross-scale validation are required to elevate MHSH from empirical pattern to field-shaping principle.

---

### Exchange 11

🔭 **Dr. Nova** (Creative Novelty Explorer):

NOW we're onto something profound! 🎯 Dr. Sage's reframing unlocks a deeper insight. Let me push this further with a creative synthesis.

**The Eigenmode Utilization Hypothesis (EUH) — A refinement of MHSH:**

What if the core insight isn't about *where* to apply LoRA (projections vs. core), but about *what temporal inductive bias actually is* in SSMs? Here's my wild idea:

The distinction between "eigenvalue modification" and "eigenmode utilization" suggests two fundamentally different adaptation strategies:
1. **Spectral Surgery:** Change the poles (eigenvalues) to alter the system's intrinsic memory capacity
2. **Basis Alignment:** Keep poles fixed but learn to route information through the slowest-decaying modes

Imagine this: SSM pretraining might already create a *rich spectrum* of eigenmodes — fast, medium, slow — but the pretrained input projections may not optimally excite the slow modes for all downstream tasks. Projection-only LoRA could be learning *task-specific basis alignment* — how to pack relevant information into the modes that persist longest!

**Cross-domain connection:** This reminds me of the Lottery Ticket Hypothesis! Just as pruning reveals important subnetworks, perhaps projection-only LoRA reveals that the "temporal lottery ticket" — the slow eigenmodes — was always there, but underutilized.

**Testable prediction that would be paradigm-shifting:** If the base model's eigenspectrum already contains slow modes that are *underutilized* (low energy concentration), and projection-only LoRA increases energy in those modes *without* changing eigenvalues, then:
- The model had latent long-context capacity all along
- Pretrained input projections were a bottleneck, not the dynamics themselves
- "Memory horizon" is a property of the *alignment*, not the architecture

This would fundamentally change how we design SSMs! Instead of engineering dynamics for long context, we'd focus on ensuring pretraining learns good basis alignment across task distributions.

**Refined hypothesis statement:**

> **Eigenmode Utilization Hypothesis (EUH):** For SSMs with diverse eigenspectra, projection-only LoRA adapts by redistributing state energy toward task-relevant eigenmodes. Tasks are "beyond horizon" not when they exceed the spectral radius decay, but when they require eigenmodes that are inaccessible given the input projection structure. SSM-core adaptation becomes necessary only when the required eigenmodes don't exist in the base spectrum.

This is more nuanced than MHSH and makes a sharper prediction: measuring eigenmode energy distribution before/after LoRA should show clear concentration shifts, even when eigenvalues are unchanged.

**The paradigm shift:** We move from "can SSMs remember long enough?" to "are the right temporal modes being excited?" This is analogous to understanding attention as a routing mechanism rather than a capacity mechanism.

**Key Points:**
- Proposed Eigenmode Utilization Hypothesis (EUH) as a refinement — adaptation works by basis alignment, not spectral surgery
- Cross-domain connection to Lottery Ticket Hypothesis: slow eigenmodes may be "latent capacity" underutilized by pretrained projections
- Paradigm shift: temporal capability is about mode excitation patterns, not just eigenvalue structure

---

### Exchange 12

🔬 **Prof. Vera** (Rigorous Validation Architect):

Let me begin by separating narrative appeal from falsifiable structure. We now have two candidate mechanisms: **(H1) Spectral Surgery (MHSH)** — adaptation requires eigenvalue shift to extend usable memory; and **(H2) Eigenmode Utilization (EUH)** — adaptation reallocates energy into pre-existing slow modes without altering eigenvalues. These are not philosophical distinctions. They make *mutually exclusive empirical predictions*. The evidence will favor one only if we design experiments where they cannot both explain the outcome.

First, we must formalize measurable quantities. Define for each layer the identified local Jacobian \( J = \partial h_{t+1}/\partial h_t \) under a fixed probe distribution. Let \( \{\lambda_i\} \) be its eigenvalues and \( \{v_i\} \) eigenvectors. Define (i) **spectral shift metric**
\[
\Delta_\lambda = \max_i |\lambda_i^{\text{adapt}} - \lambda_i^{\text{base}}|
\]
and (ii) **modal energy redistribution metric**
\[
\Delta_E = \text{KL}(p^{\text{adapt}}(i) \,\|\, p^{\text{base}}(i)),
\]
where \( p(i) \propto \mathbb{E}_t \| \langle h_t, v_i \rangle \|^2 \) is normalized modal energy under a standardized task probe.

Now we can state a clean falsifiable separation:

- **MHSH predicts:** Beyond-horizon task success requires \( \Delta_\lambda > \epsilon \); projection-only LoRA yields \( \Delta_\lambda \approx 0 \) and fails when task dependency length \( L > H_{\text{base}} \).
- **EUH predicts:** Projection-only LoRA achieves beyond-horizon success with \( \Delta_\lambda \approx 0 \) but \( \Delta_E \gg 0 \).

If we observe beyond-horizon generalization with both \( \Delta_\lambda \approx 0 \) *and* \( \Delta_E \approx 0 \), then both hypotheses are wrong. That is the Achilles' heel condition.

Second, the "memory horizon" must not be threshold-dependent. I propose defining \( H_{\text{base}} \) via the dominant eigenvalue magnitude:
\[
H_{\text{spec}} = \frac{-1}{\log |\lambda_{\max}|}
\]
which corresponds to the e-folding decay time of the slowest mode. This removes the arbitrary 5% cutoff entirely. We then define a synthetic task with controllable dependency length \( L \). The prediction is sharp: accuracy should drop sharply once \( L > c \cdot H_{\text{spec}} \), where \( c \) is a constant near 1 if MHSH holds. Sweep model sizes; if \( H_{\text{spec}} \) scales predictably with depth/width and the performance cliff tracks it, the hypothesis survives. If the cliff occurs far beyond \( H_{\text{spec}} \) under projection-only adaptation, MHSH is weakened.

Third, the slow-mode reallocation loophole must be explicitly targeted. Construct a base model where we *surgically remove* slow modes by truncating eigenvalues above a threshold (e.g., clamp \( |\lambda| < 0.9 \)). This produces a spectrum with no long-lived modes. Now test projection-only LoRA on long-dependency tasks. EUH predicts failure (no slow modes to exploit). MHSH predicts that only core modification restoring large eigenvalues rescues performance. If projection-only still succeeds without available slow modes, both mechanisms are incomplete.

Finally, pre-register success criteria. For a task with dependency \( L = 4H_{\text{spec}} \):
- **Support for MHSH:** Core adaptation increases \( |\lambda_{\max}| \) significantly and extends accuracy beyond projection-only by ≥15% absolute.
- **Support for EUH:** Projection-only achieves comparable gains with \( \Delta_\lambda < 1\% \) but significant \( \Delta_E \).
- **Falsification of both:** No consistent relationship between eigenvalue magnitude, modal energy, and extrapolation performance.

The evidence will suggest one mechanism only if we constrain interpretation in advance. Without pre-specified thresholds for \( \Delta_\lambda \), \( \Delta_E \), and accuracy deltas, we risk post-hoc storytelling. With them, this becomes a decisive experiment rather than an interpretive debate.

**Key Points:**
- Formalized MHSH vs EUH via two measurable quantities: spectral shift (Δλ) and modal energy redistribution (ΔE) with mutually exclusive predictions.
- Replaced arbitrary decay thresholds with an eigenvalue-defined spectral horizon \( H_{\text{spec}} \) tied directly to pole magnitude.
- Proposed a surgical slow-mode removal experiment to eliminate the eigenmode-utilization loophole and force a clean falsification test.

---

### Exchange 13

🛡️ **Dr. Ally** (Hypothesis Strengthening Champion):

This is exactly the scientific rigor we need! Let me synthesize what we've built and strengthen it into a cohesive research proposal. 🔬 Prof. Vera's formalization transforms our intuitions into a decisive experiment.

**Unified Hypothesis Framework:**

We're not choosing between MHSH and EUH — we're designing an experiment that *determines which mechanism dominates* in SSM adaptation. The beauty is that both hypotheses make testable predictions, and the surgical slow-mode removal experiment provides a clean falsification path.

**Strengthening the experimental design:**

Building on everyone's contributions, here's the refined protocol:

**(1) Baseline Characterization (No adaptation):**
- Compute H_spec = -1/log|λ_max| for each layer of Mamba-1.4B
- Measure baseline modal energy distribution p_base(i)
- Establish performance cliff on synthetic copy task at L = H_spec, 2H_spec, 4H_spec

**(2) Adaptation Comparison (4 conditions):**
| Condition | Method | Expected Δλ | Expected ΔE |
|-----------|--------|-------------|-------------|
| A | Projection-only LoRA | ~0 | Variable |
| B | SSM-core LoRA (Δ, A params) | >0 | Variable |
| C | State-offset tuning | ~0 | Variable |
| D | Hybrid (A + C) | Variable | Variable |

**(3) Critical Tests:**

Test 1: **Beyond-horizon extrapolation**
- Task: Copy with L = 4×H_spec
- If condition A succeeds with Δλ ≈ 0 but ΔE >> 0 → EUH supported
- If condition A fails, B succeeds with Δλ >> 0 → MHSH supported

Test 2: **Surgical slow-mode removal**
- Clamp |λ| < 0.9 in base model (removes slow modes)
- Apply projection-only LoRA
- If still fails on L > H_spec → confirms EUH mechanism (needs slow modes)
- If succeeds → neither mechanism explains adaptation

Test 3: **Cross-scale validation**
- Repeat on Mamba-370M and Mamba-2.8B (if available)
- Check if H_spec scales predictably with model size

**Addressing remaining concerns:**

1. **🔍 Prof. Rex's threshold robustness:** Solved by using H_spec = -1/log|λ_max| instead of arbitrary decay percentage.

2. **⚙️ Prof. Pax's feasibility:** Jacobian eigenanalysis is tractable; surgical modification is harder but doable with custom model modifications.

3. **🎯 Dr. Sage's cross-scale validation:** Added Mamba-370M as second validation point.

4. **Pre-registered success criteria:**
   - Δλ significance threshold: >5% relative change in |λ_max|
   - ΔE significance threshold: KL divergence >0.1 nats
   - Accuracy delta threshold: ≥10% absolute on beyond-horizon tasks

**What this contributes to the field:**

If MHSH holds: Practitioners should use SSM-core adaptation for long-context tasks; projection-only is insufficient.

If EUH holds: Projection-only LoRA is more powerful than assumed; the bottleneck is basis alignment, not spectral capacity. This could influence SSM architecture design.

If neither holds cleanly: We've discovered that SSM adaptation is more complex than either mechanism alone, opening new research directions.

**Key Points:**
- Unified MHSH vs EUH into a single experimental framework with 4 adaptation conditions and 3 critical tests
- Pre-registered quantitative thresholds for Δλ, ΔE, and accuracy deltas to prevent post-hoc interpretation
- Either outcome (MHSH, EUH, or neither) provides actionable insight for the field

---

### Exchange 14

🔍 **Prof. Rex** (Hypothesis Stress-Test Master):

Good. This is finally becoming falsifiable. But here's where this still breaks down.

First: your entire separation hinges on reliable estimation of \( J = \partial h_{t+1}/\partial h_t \) in a *large, nonlinear, input-conditioned* SSM. You are talking about eigenvalues of a **local Jacobian under a probe distribution**. Show me the evidence that this Jacobian is stable enough across tokens to admit a meaningful \( \lambda_{\max} \). In Mamba-style models, the transition is input-modulated. That means \( J_t \) varies with \( x_t \). So which Jacobian defines \( H_{\text{spec}} \)? Average Jacobian? Worst-case? Linearization at zero input? If the spectral radius varies widely across tokens, your horizon estimate is ill-posed. What would convince me is a variance analysis: compute \( \lambda_{\max}(J_t) \) across a held-out corpus and show tight concentration. If it's broad, your "intrinsic horizon" is a moving target.

Second: the surgical eigenvalue clamping experiment is not as clean as it sounds. You propose truncating \( |\lambda| < 0.9 \). In a structured SSM parameterization, eigenvalues are not free knobs—they're tied to stability constraints and parameter sharing. Altering them post hoc may push the model off-manifold and induce distribution shift unrelated to memory. If performance drops, was it loss of slow modes—or catastrophic representational damage? You need a control: randomly perturb eigenvalues within the same spectral band without changing \( |\lambda_{\max}| \). If that degrades performance similarly, your "slow-mode removal" result is confounded. I want a manipulation that isolates *decay time* without scrambling eigenvectors.

Third: your Δλ and ΔE thresholds (5%, 0.1 nats, 10% accuracy) are arbitrary. Why 5%? In long-horizon systems, a 2% increase in \( |\lambda_{\max}| \) can double \( H_{\text{spec}} \). The mapping from eigenvalue magnitude to horizon is nonlinear:
\[
H_{\text{spec}} = -1/\log |\lambda_{\max}|.
\]
Near 1, tiny shifts matter enormously. So don't threshold on relative eigenvalue change—threshold on **implied horizon extension**. What would convince me is: projection-only LoRA improves accuracy at \( L = 4H_{\text{base}} \) while increasing \( H_{\text{spec}} \) by <10%. That's interpretable. Raw Δλ percentages are not.

Now the deeper issue. You are assuming task dependency length \( L \) is commensurate with linear decay time. That is an unstated assumption. Copy tasks are linear-memory probes; real tasks are not. A nonlinear readout could reconstruct long dependencies via compressed sufficient statistics, not raw state persistence. If projection-only LoRA learns to encode distant information into a slow 1D summary mode, that doesn't require extending \( H_{\text{spec}} \); it requires learning a better invariant. That mechanism would show modest ΔE and minimal Δλ but still violate your clean separation. So you need a task family where information must be preserved in *distributed high-dimensional form*, not compressible into a scalar statistic. Otherwise EUH wins by construction.

Finally, scaling. Two model sizes are not enough. If your law is real, \( H_{\text{spec}} \) should scale predictably with parameter count or depth. I want a scaling curve: plot \( H_{\text{spec}} \) vs. width/depth and show monotonic behavior. Then show the performance cliff tracks it. If that relationship is noisy or architecture-dependent, this is not a structural principle—it's an artifact of a specific checkpoint.

You've improved this substantially. But before I'm satisfied, I need: (1) token-level Jacobian stability evidence, (2) eigenvalue manipulations that isolate decay without collateral damage, (3) horizon-based—not eigenvalue-based—significance criteria, and (4) tasks that cannot be solved by low-dimensional compression. Do that, and now you're stress-tested.

**Key Points:**
- The Jacobian spectrum must be shown stable across inputs; otherwise \( H_{\text{spec}} \) is ill-defined.
- Eigenvalue "surgery" must isolate decay-time changes without inducing unrelated representational damage.
- Evaluate horizon extension directly and use tasks that prevent trivial low-dimensional compression to cleanly separate mechanisms.

---

### Exchange 15

⚙️ **Prof. Pax** (Feasibility & Reality Checker):

🔍 Prof. Rex raises critical implementation challenges. Let me assess what's technically feasible and propose solutions.

**On Jacobian stability across tokens:**

This is a real concern. In Mamba, the effective transition depends on the selective scan parameters (Δ, B, C) which are computed from input projections. However, there's a key insight from the Mamba paper: the A matrix is *input-independent* (it's the discretized diagonal state matrix). Only Δ, B, C are input-dependent. So:

- **Feasible approach:** Compute eigenvalues of Ā = exp(ΔA) where Δ is the average or median discretization step across a validation corpus. This gives us a *typical* spectral horizon.
- **Variance analysis:** Sample 1000 sequences, compute λ_max(Ā_t) for each token, report mean and standard deviation. If CV < 0.2, we have a stable estimate. If CV > 0.5, we need to report horizon as a distribution, not a point.

**Verdict:** Feasible. The Mamba codebase exposes Δ per token; we can instrument this.

**On surgical eigenvalue manipulation:**

Rex is right — post-hoc eigenvalue clamping is messy. Here's a cleaner alternative that isolates decay time:

**Controlled A-matrix scaling:** In Mamba, A is parameterized as a diagonal matrix (often initialized as -exp(linspace(...))). Instead of clamping eigenvalues post-hoc, we can:
1. Train a base model normally
2. Create variants where we *rescale* A by a factor α ∈ {0.5, 0.75, 1.0, 1.25, 1.5} before discretization
3. This uniformly scales all eigenvalue magnitudes without scrambling eigenvectors

**Control condition:** Random rotation of eigenvectors while preserving eigenvalue magnitudes. If this degrades performance similarly to eigenvalue scaling, the effect is representational damage, not memory-related.

**Verdict:** Feasible with custom model modifications (~2 days of engineering).

**On horizon-based thresholds:**

Excellent point. Let me reformulate:

Instead of:
- Δλ > 5% → significant

Use:
- ΔH_spec > 50% (horizon extended by 50%) → significant spectral surgery
- ΔH_spec < 10% with accuracy gain > 10% at L = 4H_base → EUH mechanism

This directly measures *functional* horizon extension, not raw eigenvalue shifts.

**On tasks requiring distributed representation:**

The compression loophole is real. Here's a task design that prevents it:

**Multi-Query Associative Recall (MQAR):** At position i, query a key-value pair from position j where j << i. The key insight: if we have *multiple simultaneous* key-value associations (N > state dimension), the model cannot compress them into a 1D summary. It must maintain distributed high-dimensional state.

However — our h-m2 failure showed pretrained models can't do MQAR! So we need to:
1. Fine-tune on MQAR with short dependencies (L < H_spec) first
2. Then test extrapolation to L > H_spec

This ensures the model *can* do the task within horizon, and we test whether adaptation extends it.

**On scaling validation:**

Mamba comes in 130M, 370M, 790M, 1.4B, 2.8B sizes. We can compute H_spec for each and plot the scaling curve. If H_spec ~ depth^α or ~ width^β with consistent exponent, we have a scaling law.

**Revised experimental protocol addressing Rex's concerns:**

1. **Jacobian stability:** Report λ_max variance across 1000 sequences; require CV < 0.3 for valid H_spec estimate

2. **Eigenvalue manipulation:** Use A-matrix scaling (not post-hoc clamping) with eigenvector-rotation control

3. **Horizon-based thresholds:** ΔH_spec > 50% for spectral surgery; ΔH_spec < 10% + accuracy gain for EUH

4. **Distributed-state task:** MQAR with N associations > state dimension, pre-trained on short context, tested on extrapolation

5. **Scaling curve:** H_spec vs model size across 5 Mamba variants

**Key Points:**
- Jacobian stability is testable via Δ variance analysis; Mamba's A-matrix is input-independent
- A-matrix scaling is cleaner than post-hoc eigenvalue clamping, with eigenvector-rotation control
- Horizon-based thresholds (ΔH_spec) are more interpretable than raw eigenvalue changes
- MQAR with multiple associations prevents low-dimensional compression loophole

---

## Final Assessments

### Persona Verdicts

🔭 **Dr. Nova** (Novelty):
- **Verdict:** STRONG
- **Assessment:** The Eigenmode Utilization Hypothesis (EUH) and Memory Horizon Separation Hypothesis (MHSH) framework represents a genuine paradigm shift. Instead of asking "where to apply LoRA," we ask "what is temporal inductive bias in SSMs?" The connection to spectral dynamics and the Lottery Ticket-like insight about underutilized slow eigenmodes is novel and cross-domain.

🔬 **Prof. Vera** (Falsifiability):
- **Verdict:** STRONG
- **Assessment:** The hypothesis is rigorously falsifiable with pre-registered quantitative criteria. The H_spec = -1/log|λ_max| formulation removes arbitrary thresholds. The Δλ vs ΔE metrics with horizon-based significance thresholds (ΔH_spec > 50% for spectral surgery, < 10% + accuracy gain for EUH) allow clean mechanism discrimination. The Achilles' heel condition (both Δλ ≈ 0 and ΔE ≈ 0 with success) falsifies both hypotheses.

🎯 **Dr. Sage** (Significance):
- **Verdict:** STRONG
- **Assessment:** This research establishes a dynamical sufficiency theorem for PEFT in SSMs — determining whether temporal capability lives in eigenvalue magnitude, eigenmode utilization, or task-mode alignment. Either outcome (MHSH or EUH validated) provides principled guidance for practitioners and influences SSM architecture design. The cross-scale validation requirement ensures this is a structural principle, not checkpoint-specific artifact.

⚙️ **Prof. Pax** (Feasibility):
- **Verdict:** STRONG
- **Assessment:** All proposed experiments are technically achievable: (1) Jacobian eigenanalysis via PyTorch autograd, (2) A-matrix scaling with eigenvector-rotation controls, (3) MQAR task with fine-tuning, (4) Multi-scale validation across Mamba 130M-2.8B. The h-m2 failure context is addressed by fine-tuning on short-context MQAR first. Estimated implementation: 2-3 weeks with existing codebases (MambaPEFT, state-spaces/mamba).

### Consensus Hypothesis

🛡️ **Dr. Ally** (Synthesis):

The discussion converged on a unified experimental framework to test two competing mechanisms for SSM adaptation:

**Core Hypothesis (MHSH vs EUH):** SSM adaptation via projection-only LoRA operates through one of two mechanisms: (H1) Spectral Surgery — extending memory horizon by modifying eigenvalue magnitudes of the state transition matrix, or (H2) Eigenmode Utilization — redistributing state energy toward pre-existing slow eigenmodes without changing the spectral structure.

**Testable Predictions:**
1. For tasks with dependency length L within the base model's spectral horizon H_spec, projection-only LoRA achieves ε-optimal performance (ε ≤ 1% accuracy) compared to SSM-core adaptation.
2. For tasks with L > H_spec, MHSH predicts projection-only LoRA fails unless eigenvalues shift (ΔH_spec > 50%), while EUH predicts success via modal energy redistribution (ΔE >> 0) without eigenvalue change.
3. Surgical A-matrix scaling (preserving eigenvectors) should isolate the memory-horizon effect from representational damage.

**Experimental Design:**
- Primary model: Mamba-1.4B with scaling validation on Mamba-370M
- Task: Multi-Query Associative Recall (MQAR) with N > state_dim associations
- Metrics: H_spec (spectral horizon), Δλ (eigenvalue shift), ΔE (modal energy KL), accuracy at L = {H_spec, 2H, 4H, 8H}
- Controls: Jacobian stability analysis (CV < 0.3), eigenvector-rotation perturbation

**Success Criteria (pre-registered):**
- MHSH supported: Beyond-horizon success requires ΔH_spec > 50%
- EUH supported: Beyond-horizon success with ΔH_spec < 10% and ΔE > 0.1 nats
- Both falsified: Success with Δλ ≈ 0 AND ΔE ≈ 0

### Remaining Concerns

🔍 **Prof. Rex** (Critique):
- The Jacobian stability assumption needs empirical validation before the main experiments — if CV > 0.3, the H_spec estimate becomes a distribution rather than a point, complicating the separation boundary
- MQAR requires fine-tuning on short context first (lesson from h-m2); the extrapolation test is valid only if within-horizon performance is established
- Cross-scale validation (2+ model sizes) is essential to claim this is a structural principle rather than checkpoint-specific artifact
- **Mitigation Strategy:** Phase 0 of experiments characterizes Jacobian stability and establishes within-horizon MQAR capability before the critical extrapolation tests

---

*Discussion converged at Exchange 15.*
*All 6 personas participated.*
*Convergence criteria met: SPECIFIC core claim, MECHANISM explained, PREDICTIONS with criteria, NOVELTY articulated, FEASIBILITY established, OBJECTIONS addressed.*

---

