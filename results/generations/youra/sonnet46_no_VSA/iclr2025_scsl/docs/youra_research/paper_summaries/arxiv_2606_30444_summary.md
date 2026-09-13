---
source_paper: "arxiv_2606_30444.md"
generated_at: "2026-08-04T03:12:20.412203"
model: "openai/gpt-5.2"
summary_chars: 16160
---

# SGD Provably Prioritizes a Shortcut Spurious Feature in the XOR Model

## Key Metadata
- **Authors:** Tyler LaBonte et al.
- **Year:** 2026
- **Venue:** arXiv (preprint)
- **Core Contribution:** Provides an end-to-end, non-linear-theory characterization showing online minibatch SGD on a 2-layer ReLU network learns a linear spurious feature *first* (exponentially fast) and—under maximally strong correlation—suppresses learning the quadratic XOR signal even at XOR’s standalone sample-complexity threshold.

## Section Summaries

### Abstract
Neural networks are known to be susceptible to over-reliance on spurious correlations. However, the
precise mechanism by which models exploit shortcut features is not fully understood, and algorithms
to mitigate this behavior rely on as yet unjustified assumptions about the learned representations. In
this work, we provide the first end-to-end theoretical characterization of spurious feature learning for
two-layer ReLU neural networks trained by online minibatch SGD on the logistic loss. We consider data
drawn from the high-dimensional Boolean hypercube with a quadratic signal function (namely XOR) and
a linear spurious correlation. We show that SGD learns the spurious feature first, and exponentially fast.
Moreover, the optimization dynamics couple the spurious and signal features, with a stronger spurious
component inhibiting signal feature learning. Our analysis reveals precise phase transitions in the learning
dynamics. In the first phase, alignment between the signs of the spurious feature and second-layer weight
drives rapid growth of the spurious feature. In the second phase, large majority group margin slows
learning and the signal feature remains suppressed. When the spurious correlation is maximally strong,
we show theoretically that the spurious feature dominates even at the sample complexity threshold where
XOR would be learned in isolation (i.e., if the spurious feature was absent). In contrast, when the
correlation strength is constant, we provide preliminary empirical evidence that the model can eventually
learn the XOR signal, although the spurious feature is not forgotten.

### Introduction & Motivation
Neural networks often exploit “shortcut” features—spurious correlations that predict labels in training data but fail under distribution shift—leading to poor worst-group / OOD performance. Many debiasing methods implicitly assume specific feature-learning dynamics (e.g., spurious features are learned early; signal and spurious features co-exist but are misweighted), but these assumptions lack rigorous justification in non-linear training. The paper studies a minimal setting where the true label is a quadratic Boolean XOR on \((x_1,x_2)\), while a linear feature \(x_3\) is spuriously correlated with the label. The goal is to *theoretically* and *end-to-end* characterize how standard online minibatch SGD with logistic loss learns spurious vs. signal features in a two-layer ReLU network, including phase transitions and worst-group accuracy consequences.

### Methodology
The authors analyze feature learning in a **two-layer ReLU network** trained by **online minibatch SGD** on a **synthetic Boolean hypercube** distribution designed to contain both a quadratic XOR signal and a linear spurious correlation.

**Data model (XOR signal + linear spurious feature).** Let \(\mu_1 := e_1-e_2\), \(\mu_2 := e_1+e_2\), and \(\lambda\in(0,\tfrac12)\) denote spurious-correlation strength (smaller \(\lambda\Rightarrow\) stronger correlation). Samples \(x\in\{\pm1\}^d\) are generated as
\[
x =
\begin{cases}
\mu_1 + e_3 + \xi & \text{w.p. } \frac14-\frac{\lambda}{4}\\
\mu_1 - e_3 + \xi & \text{w.p. } \frac{\lambda}{4}\\
\mu_2 - e_3 + \xi & \text{w.p. } \frac14-\frac{\lambda}{4}\\
\mu_2 + e_3 + \xi & \text{w.p. } \frac{\lambda}{4}\\
-\mu_1 + e_3 + \xi & \text{w.p. } \frac14-\frac{\lambda}{4}\\
-\mu_1 - e_3 + \xi & \text{w.p. } \frac{\lambda}{4}\\
-\mu_2 - e_3 + \xi & \text{w.p. } \frac14-\frac{\lambda}{4}\\
-\mu_2 + e_3 + \xi & \text{w.p. } \frac{\lambda}{4}
\end{cases}
\tag{1}
\]
where \(\xi\sim \mathrm{Unif}(0_3\times\{\pm1\}^{d-3})\) is orthogonal to \(\{\mu_1,\mu_2,e_3\}\). Write \(x=z+s+\xi\) with \(z=x_1e_1+x_2e_2\), \(s=x_3e_3\). The **ground-truth label** is noiseless XOR on the first two coordinates:
\[
y(x):=y(z):=-x_1x_2.
\]
Define **majority** vs **minority** groups by whether the spurious coordinate matches the label:
\[
X_{\mathrm{maj}}:=\{x: y(x)=x_3\},\qquad X_{\mathrm{min}}:=\{x: y(x)=-x_3\},
\]
with \(\mathbb{P}(X_{\mathrm{maj}})=1-\lambda\) and \(\mathbb{P}(X_{\mathrm{min}})=\lambda\). Group accuracy is
\[
\mathrm{Acc}_X(f):=\mathbb{P}_{x\sim\mathrm{Unif}(X)}\big(\mathrm{sgn}(f(x))=y(x)\big).
\]

**Model architecture and parameterization.** The predictor is a width-\(p\) two-layer ReLU network:
\[
f_\rho(x):=\mathbb{E}_{(a,w)\sim\rho}\big[a\,\sigma(w^\top x)\big]
=\frac1p\sum_{j=1}^p a_j\,\sigma(w_j^\top x),\quad \sigma(\alpha)=\max(0,\alpha),
\]
where \(\rho\) is the empirical distribution over neurons \(\{(a_j,w_j)\}_{j=1}^p\). Initialization: \(w_j\sim \mathrm{Unif}(S^{d-1}(\theta))\) so \(\|w_j\|=\theta\), and \(a_j=r_j\theta\) with \(r_j\sim\mathrm{Unif}(\{\pm1\})\).

**Loss, margin, and SGD update.** Define margin \(\gamma(x):=y(x)f_\rho(x)\), sigmoid \(\psi(u)=1/(1+e^{-u})\), and logistic loss via
\[
\ell_\rho(x):=h(\gamma(x)),\qquad h(\gamma):=-2\log(\psi(\gamma)),\qquad \ell_\rho^{(1)}(x)=h'(\gamma(x)).
\]
Population loss \(L_\rho:=\mathbb{E}_x[\ell_\rho(x)]\). Online minibatch SGD with batch \(M^{(t)}\sim P_d(\lambda)^m\) uses the empirical loss \(\widehat L_{\rho^{(t)}}:=\frac1m\sum_{x\in M^{(t)}}\ell_{\rho^{(t)}}(x)\). With “mean-field” scaling (following Glasgow, 2024), the update is
\[
a^{(t+1)} = a^{(t)} - \eta\,\partial_{a^{(t)}} \widehat L_{\rho^{(t)}},\qquad
w^{(t+1)} = w^{(t)} - \eta\,\nabla_{w^{(t)}} \widehat L_{\rho^{(t)}}.
\]

**Feature decomposition for theory (signal vs spurious vs orthogonal).** For each neuron \((a,w)\), decompose
\[
w := w_{1:2}+w_{\mathrm{sp}}+w_\perp,\qquad w_{1:2}:=w_{\mathrm{sig}}+w_{\mathrm{opp}},
\]
where the **spurious** component is \(w_{\mathrm{sp}}:=w_3 e_3\) (often identified with scalar \(w_3\)), and \(w_{\mathrm{sig}}, w_{\mathrm{opp}}\) are projections onto \(\mu_1,\mu_2\) *selected by* \(\mathrm{sgn}(a)\):
\[
w_{\mathrm{sig}} :=
\begin{cases}
\frac12 \mu_1\mu_1^\top w & a\ge 0\\
\frac12 \mu_2\mu_2^\top w & a<0
\end{cases},
\qquad
w_{\mathrm{opp}} :=
\begin{cases}
\frac12 \mu_2\mu_2^\top w & a\ge 0\\
\frac12 \mu_1\mu_1^\top w & a<0
\end{cases}.
\]
The analysis tracks high-probability growth rates of \(\|w_{\mathrm{sig}}\|\), \(\|w_{\mathrm{opp}}\|\), \(\|w_{\mathrm{sp}}\|\), \(\|w_\perp\|\), and \(\|w_\perp\|_\infty\).

**Phase-based proof strategy (end-to-end non-linear SGD).**
- **Phase I (small network regime):** While \(f_\rho\) remains small, analyze dynamics using a *first-order* Taylor proxy loss around \(f_\rho=0\):
  \[
  \ell_0(x):=-2\log(\tfrac12) - y(x)f_\rho(x),\qquad L_0:=\mathbb{E}_x[\ell_0(x)].
  \]
  This is an analysis tool (not NTK linearization): training still uses \(\ell_\rho\), but gradients are compared to those under \(L_0\).
  - **Phase Ia:** very short, \(T_{\mathrm{Ia}}\asymp \log^{1/2}(d)\,d^{-1/2}\eta^{-1}\); establishes sign alignment \(\mathrm{sgn}(a)=\mathrm{sgn}(w_{\mathrm{sp}})\) for all neurons.
  - **Phase Ib:** lasts \(T_{\mathrm{Ib}}\asymp \log\log(d)\,\eta^{-1}\); once aligned, the spurious component grows geometrically/exponentially fast, quickly dominating other components.
- **Phase II (large margin regime):** The \(L_0\) approximation breaks. The authors analyze the true gradient via margin concentration. Using
  \[
  \nabla_w L_\rho = p\,\mathbb{E}_x\big[\ell_\rho^{(1)}(x)\,y(x)\nabla_w f_\rho(x)\big]
  =2\,\mathbb{E}_x\big[\psi(-\gamma(x))\cdot \nabla_w p\ell_0(x)\big],
  \]
  they show the margin concentrates to “equal and opposite” values across groups, governed primarily by \(w_{\mathrm{sp}}^2\). Define groupwise average spurious-squared margins:
  \[
  \gamma^+ := \frac1p\sum_{(a,w)\in S^+}(w_{\mathrm{sp}})^2,\quad
  \gamma^- := \frac1p\sum_{(a,w)\in S^-}(w_{\mathrm{sp}})^2,\quad
  \bar\gamma:=\tfrac12(\gamma^+ + \gamma^-).
  \]
  Then the spurious feature evolves approximately as
  \[
  w_{\mathrm{sp}}^{(t+1)} - w_{\mathrm{sp}}^{(t)}
  \asymp \eta\,w_{\mathrm{sp}}^{(t)}\Big(1-\lambda-\psi(\bar\gamma^{(t)})\Big),
  \tag{2}
  \]
  yielding sigmoidal slowdown as \(\bar\gamma\) grows. Crucially, as \(w_{\mathrm{sp}}\) gets large, it **exponentially suppresses** signal learning:
  \[
  \|w_{\mathrm{sig}}^{(t+1)}-w_{\mathrm{sig}}^{(t)}\|
  \;\lesssim\;
  \eta e^{-\bar\gamma^{(t)}}\Big(\max_{(a,w)}(w_{\mathrm{sp}}^{(t)})^2\|w_{\mathrm{sig}}^{(t)}\|\Big)
  + \eta\theta \log^{-1}(d)d^{-1/2},
  \]
  so signal growth becomes negligible while the spurious predictor remains dominant.

**Key hyperparameter scaling assumptions for the main theorem (Assumption 3.1).** For sufficiently large constant \(C>0\):
- learning rate: \(\log(d)d^{-C} \ll \eta \ll \log^{-3}(d)\)
- width: \(\log^5(d)\ll p\ll d^C\)
- init scale: \(d^{-C/2}\ll \theta\ll \log^{-5C}(d)\)
- batch size: \(m\gg d\log^6(d)\theta^{-2}\)
- extreme correlation: \(\lambda\ll \log^{-1}(d)\) (needed for Phase II monotone growth / margin structure).

### Experiments & Results
The paper’s “experiments” are targeted **simulations** on the synthetic Boolean XOR+spurious distribution (Eq. (1)), intended to validate the predicted phase transitions and to probe the **constant-\(\lambda\)** regime not covered by the main theorem.

**Datasets and splits.** No external datasets; all data are i.i.d. samples from \(P_d(\lambda)\) on \(\{\pm1\}^d\). Training is **online minibatch SGD**, so the effective sample complexity is \(m\cdot T\) (batch size \(\times\) iterations). There is no explicit train/val/test split; evaluation uses groupwise accuracies and margin behavior over draws from \(X_{\mathrm{maj}}\) and \(X_{\mathrm{min}}\).

**Evaluation metrics.**
- Worst-group-style metrics: \(\mathrm{Acc}_{X_{\mathrm{maj}}}(f)\) and \(\mathrm{Acc}_{X_{\mathrm{min}}}(f)\).
- Margin diagnostics: minibatch average per-group margin; “equal and opposite” margin concentration \(\pm w_{\mathrm{sp}}^2\) behavior in Phase II.

**Baselines / comparisons.**
- Primary conceptual baseline: **XOR without spurious feature** (equivalently \(\lambda=\tfrac12\), i.e., \(x\sim \mathrm{Unif}(\{\pm1\}^d)\)), referencing Glasgow (2024) which proves XOR can be learned with \(d\cdot\mathrm{polylog}(d)\) samples under similar training.
- Within-paper comparisons: varying \(\lambda\) (e.g., \(\lambda=0.1,0.15,0.2\)) to compare strong vs weaker spurious correlation regimes.

**Main theoretical result (worst-group accuracy under extreme correlation).** Under Assumption 3.1, after
\[
T \asymp
\begin{cases}
\log(d)(\log\log(d))^{-1}\eta^{-1} & \theta \asymp \mathrm{polylog}^{-1}(d)\\
\log(d)\eta^{-1} & \theta \asymp \mathrm{poly}^{-1}(d)
\end{cases}
\]
iterations, with probability \(\ge 1-d^{-C}\),
\[
\mathrm{Acc}_{X_{\mathrm{maj}}}(f_{\rho^{(T)}})\ge 1-d^{-C},\qquad
\mathrm{Acc}_{X_{\mathrm{min}}}(f_{\rho^{(T)}})\le d^{-C}.
\]
Interpretation: at the iteration/sample scale where XOR would be learned in isolation, the network instead behaves like the fully spurious classifier \(f^{\mathrm{sp}}(x)=x_3\) (perfect on majority, fails on minority).

**Compact result table (what is explicitly claimed/observed).**

| Setting | Training / analysis regime | Key outcome on \(X_{\mathrm{maj}}\) | Key outcome on \(X_{\mathrm{min}}\) | Evidence type |
|---|---|---:|---:|---|
| Extreme correlation \(\lambda\ll 1/\log d\) | Theorem 3.2, \(T\) as above | \(\ge 1-d^{-C}\) | \(\le d^{-C}\) | Formal theorem |
| Small \(\lambda\) example | Sim: \(d=100,\lambda=0.1,\eta=0.05,p=10,\theta=0.01,m=5000\) | Spurious feature dominates; predicts \(x_3\) | Minority margin highly negative; poor minority accuracy | Simulation (Fig. 1, Fig. 3a) |
| Constant \(\lambda\) larger | Sim: \(d=100,\lambda=0.15\) or \(0.2\) (other params similar) | Improves; can remain high | Improves substantially; can reach “perfect classification on both groups” in runs shown | Simulation (Fig. 2–3) |

**Ablations / component contributions (via feature-norm trajectories).**
- Tracking \(\|w_{\mathrm{sig}}\|\), \(\|w_{\mathrm{opp}}\|\), \(\|w_{\mathrm{sp}}\|\), \(\|w_\perp\|\) across neurons reveals three phases:
  1. **Phase Ia:** “bounce off zero” behavior in \(w_{\mathrm{sp}}\) until \(\mathrm{sgn}(a)\) aligns with \(\mathrm{sgn}(w_{\mathrm{sp}})\).
  2. **Phase Ib:** \(\|w_{\mathrm{sp}}\|\) grows **exponentially/geometrically** and dominates.
  3. **Phase II:** \(\|w_{\mathrm{sp}}\|\) grows more slowly (sigmoidal), while \(\|w_{\mathrm{sig}}\|\) remains suppressed (extreme \(\lambda\)) or can later overtake when \(\lambda\) is large enough (constant-\(\lambda\) simulations).
- In constant \(\lambda\) simulations, the network **decomposes into disjoint subnetworks**: neurons with large \(\|w_{\mathrm{sig}}\|\) tend to have small \(\|w_{\mathrm{sp}}\|\) and vice versa; additionally, the spurious feature is **not forgotten** even when XOR is eventually learned.

**Statistical significance / CIs.** Not reported; theory provides high-probability statements (e.g., \(1-d^{-C}\)).

**Compute / efficiency.** No GPU-hour reporting. Computationally, simulations use minibatch sizes like \(m=5000\) and widths \(p\in\{10,50\}\) at \(d=100\). The theory highlights potentially large batch size needs in some regimes: \(m\gg d\log^6(d)\theta^{-2}\), which can be \(\mathrm{poly}(d)\) if \(\theta\asymp \mathrm{poly}^{-1}(d)\).

### Discussion & Conclusion
The paper establishes a rigorous, phase-resolved mechanism by which SGD in a non-linear two-layer ReLU network learns a simpler linear spurious feature before (and sometimes instead of) the quadratic XOR signal, with the spurious component actively suppressing signal learning once margins become large. A key limitation is that the main theorem requires an **extreme correlation** regime \(\lambda\ll 1/\log d\); the constant-\(\lambda\) regime is explored empirically and appears to involve non-monotone spurious dynamics and subnetwork specialization, suggesting different proof tools will be needed. The authors connect their findings to assumptions behind debiasing methods (e.g., early learning of spurious features; later coexistence of features) and propose that phase lengths and subnetwork structure could guide interventions like early stopping or reweighting.

## Key Contributions
- First **end-to-end theoretical characterization** (no NTK linearization; no layer-wise tricks) of **spurious feature learning** in two-layer ReLU networks trained by **online minibatch SGD** on **logistic loss**.
- Proves a sharp **worst-group failure** phenomenon (Theorem 3.2): under maximally strong spurious correlation, SGD reaches near-perfect majority accuracy and near-zero minority accuracy **even at** the iteration/sample scale where XOR would be learnable without spurious correlation.
- Identifies **phase transitions** (Phase Ia/Ib/II), including early **sign alignment**, **exponential spurious growth**, and later **margin-driven suppression** of signal learning; empirically suggests that for constant \(\lambda\), learning can split into **disjoint signal vs spurious subnetworks** and the spurious feature is retained.

## Potential Relevance
This paper can inform hypotheses about why shortcut learning persists under standard SGD: (i) early-time sign alignment can “lock in” spurious directions, (ii) later-time large margins can *exponentially suppress* gradient flow to more complex signal features, and (iii) mitigation may require disrupting these phases (e.g., altering early dynamics, changing effective \(\lambda\) via balancing, or targeting subnetwork structure). It also offers a concrete theoretical testbed (XOR + linear spurious on \(\{\pm1\}^d\)) and explicit recurrences (e.g., Eq. (2)) that could be adapted to study other spurious-vs-signal complexity gaps or to design provably effective reweighting/early-stopping strategies.