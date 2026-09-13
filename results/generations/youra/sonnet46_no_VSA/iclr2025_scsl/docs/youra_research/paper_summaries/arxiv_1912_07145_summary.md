---
source_paper: "arxiv_1912_07145.md"
generated_at: "2026-08-04T03:09:23.817243"
model: "openai/gpt-5.2"
summary_chars: 16082
---

# PyHessian: Neural Networks Through the Lens of the Hessian

## Key Metadata
- **Authors:** Zhewei Yao et al.
- **Year:** 2019 (arXiv:1912.07145)
- **Venue:** arXiv preprint
- **Core Contribution:** Introduces **PYHESSIAN**, an open-source, scalable, matrix-free framework to compute Hessian spectrum statistics (top eigenvalues, trace, and full eigenvalue spectral density) for modern deep nets, and uses it to reassess how **Batch Normalization (BN)** and **residual connections** affect loss-landscape curvature across depths/stages of ResNets.

## Section Summaries

### Abstract
Abstract—We present PYHESSIAN, a new scalable framework
that enables fast computation of Hessian (i.e., second-order
derivative) information for deep neural networks. PYHESSIAN
enables fast computations of the top Hessian eigenvalues, the Hes-
sian trace, and the full Hessian eigenvalue/spectral density, and it
supports distributed-memory execution on cloud/supercomputer
systems and is available as open source [1]. This general frame-
work can be used to analyze neural network models, including
the topology of the loss landscape (i.e., curvature information)
to gain insight into the behavior of different models/optimizers.
To illustrate this, we analyze the effect of residual connections
and Batch Normalization layers on the trainability of neural
networks. One recent claim, based on simpler ﬁrst-order analysis,
is that residual connections and Batch Normalization make the
loss landscape “smoother”, thus making it easier for Stochastic
Gradient Descent to converge to a good solution. Our extensive
analysis shows new ﬁner-scale insights, demonstrating that, while
conventional wisdom is sometimes validated, in other cases it is
simply incorrect. In particular, we ﬁnd that Batch Normalization
does not necessarily make the loss landscape smoother, especially
for shallower networks.

### Introduction & Motivation
The paper targets a practical gap: despite widespread use of **ResNets** and their core ingredients (**residual connections** and **BatchNorm**), it remains unclear *when and why* these components help/hurt training and generalization in terms of measurable model properties. Prior “loss landscape smoothness” arguments often rely on **first-order** proxies or low-dimensional random-direction plots, which may miss important curvature structure in high dimensions. The authors propose analyzing models directly through **Hessian-based** (second-order) quantities—top eigenvalues (Lipschitz-like), trace (aggregate curvature), and the full spectral distribution. They build **PYHESSIAN** to make such Hessian computations scalable and then apply it to test/qualify claims (e.g., BN smooths the landscape) across **depth** and **network stages**, finding depth-dependent and stage-dependent effects.

### Methodology
The work contributes primarily a *computational framework* (PYHESSIAN) for extracting Hessian spectrum information from modern deep networks **without forming the Hessian**. The supervised learning objective is
\[
\min_{\theta}\; L(\theta)=\frac{1}{N}\sum_{i=1}^{N} l(M(x_i),y_i,\theta),
\tag{1}
\]
with parameters \(\theta\in\mathbb{R}^m\), gradient \(g_\theta=\frac{\partial L}{\partial \theta}\in\mathbb{R}^m\), and Hessian
\[
H=\frac{\partial^2 L}{\partial \theta^2}=\frac{\partial g_\theta}{\partial \theta}\in\mathbb{R}^{m\times m}.
\]

**(A) Matrix-free Hessian–vector products (matvec).** The central primitive is an oracle to compute \(Hv\) for arbitrary \(v\), using automatic differentiation / the R-operator identity:
\[
\frac{\partial (g_\theta^T v)}{\partial \theta}
= \frac{\partial g_\theta^T}{\partial \theta}v + g_\theta^T\frac{\partial v}{\partial \theta}
= \frac{\partial g_\theta^T}{\partial \theta}v
=Hv,
\tag{2}
\]
where \(\frac{\partial v}{\partial \theta}=0\) since \(v\) is sampled independently of \(\theta\). Importantly, the paper emphasizes that the **cost of one Hessian matvec is comparable to one gradient backprop**, enabling repeated spectral probes during training.

**Top eigenvalues.** With access to \(Hv\), PYHESSIAN computes the largest Hessian eigenvalues via **power iteration** (they reference an implementation akin to [53] and mention Algorithm 2). In practice, this yields a curvature/Lipschitz proxy (largest eigenvalue) but may be insufficient because the Hessian can have many informative directions.

**(B) Trace estimation via Hutchinson.** PYHESSIAN estimates \(\mathrm{Tr}(H)\) using randomized trace estimators with Rademacher (or standard Gaussian) probes. Using \(v\sim\) i.i.d. Rademacher/Gaussian,
\[
\mathrm{Tr}(H)=\mathrm{Tr}(HI)=\mathrm{Tr}(H\mathbb{E}[vv^T])=\mathbb{E}[\mathrm{Tr}(Hvv^T)]
=\mathbb{E}[v^T Hv].
\tag{3}
\]
Thus trace is approximated by averaging \(v^T(Hv)\) over multiple probe vectors, where each term requires one Hessian matvec (Eq. 2) and a dot product.

**(C) Full eigenvalue spectral density (ESD) via Stochastic Lanczos Quadrature (SLQ).** To characterize curvature beyond a few scalars, they estimate the empirical spectral density
\[
\phi(t)=\frac{1}{m}\sum_{i=1}^{m}\delta(t-\lambda_i),
\tag{4}
\]
where \(\{\lambda_i\}\) are Hessian eigenvalues. SLQ proceeds through a sequence of approximations:

1) **Gaussian smoothing** of the Dirac spikes:
\[
\phi_\sigma(t)=\frac{1}{m}\sum_{i=1}^{m} f(\lambda_i;t,\sigma),
\tag{5}
\]
where \(f(\lambda;t,\sigma)=\frac{1}{\sigma\sqrt{2\pi}}\exp\!\left(-\frac{(t-\lambda)^2}{2\sigma^2}\right)\).
As \(\sigma\to 0\), \(\phi_\sigma(t)\to \phi(t)\).

2) Rewriting via matrix functions and trace identities. For eigendecomposition \(H=Q\Lambda Q^T\),
\[
\mathrm{Tr}(f(H))=\mathrm{Tr}(Qf(\Lambda)Q^T)=\mathrm{Tr}(f(\Lambda)),
\tag{6}
\]
with
\[
f(H)\triangleq Qf(\Lambda)Q^T = Q\,\mathrm{diag}(f(\lambda_1),\ldots,f(\lambda_m))\,Q^T.
\tag{7}
\]
Then
\[
\phi_\sigma(t)=\frac{1}{m}\mathrm{Tr}(f(H;t,\sigma)).
\tag{8}
\]

3) Expressing the trace as an expectation (Hutchinson-style):
\[
\phi_\sigma(t)=\frac{1}{m}\mathbb{E}\!\left[v^T f(H;t,\sigma)v\right].
\tag{9}
\]

4) Reducing evaluation of \(v^T f(H)v\) using quadrature. Define
\[
\phi^v_\sigma(t) = v^T f(H;t,\sigma)v
= v^T Qf(\Lambda;t,\sigma)Q^T v
= \sum_{i=1}^{m}\mu_i^2 f(\lambda_i;t,\sigma),
\tag{10}
\]
where \(\mu_i\) is the component of \(v\) along eigenvector \(i\). They define a piecewise CDF \(\pi(\alpha)\) (Eq. 11 in the paper) to write a Riemann–Stieltjes integral:
\[
\phi^v_\sigma(t)=\int_{\lambda_m}^{\lambda_1} f(\alpha;t,\sigma)\,d\pi(\alpha),
\tag{12}
\]
then approximate with Gauss quadrature:
\[
\phi^v_\sigma(t)\approx \sum_{i=1}^{q}\omega_i f(t_i;t,\sigma).
\tag{13}
\]

5) **Lanczos** supplies approximate nodes/weights from a \(q\)-step Krylov subspace tridiagonalization. If \((\tilde{\lambda}_i,\tilde{v}_i)\) are eigenpairs of the Lanczos tridiagonal matrix and \(\tau_i=(\tilde{v}_i[1])^2\),
\[
\phi^v_\sigma(t)\approx \sum_{i=1}^{q}\tau_i f(\tilde{\lambda}_i;t,\sigma).
\tag{14}
\]

6) Averaging over \(n_v\) random starts:
\[
\phi_\sigma(t)\approx
\frac{1}{n_v}\sum_{l=1}^{n_v}\left(\sum_{i=1}^{q}\tau_i^{(l)} f(\tilde{\lambda}_i^{(l)};t,\sigma)\right).
\tag{15}
\]
Algorithm 1 in the text presents this **Stochastic Lanczos Quadrature** pipeline (sample \(v\sim \mathcal{N}(0,1)\), run Lanczos to get tridiagonal \(T\), extract \(\tilde{\lambda}\) and weights, then aggregate).

**Distributed/scalable execution.** PYHESSIAN is described as supporting **distributed-memory execution** on cloud/supercomputers, motivated by repeated matvecs and spectral estimation at multiple checkpoints. The excerpt does not enumerate specific parallelization primitives, but the key design choice is matrix-free operations that reuse the existing backprop computational graph.

**How it differs from prior work.** Rather than only computing a small number of top eigenvalues (e.g., [53]) or only using SLQ for ESD on limited settings (e.g., [21]), the paper packages *multiple* Hessian diagnostics—top eigenvalues, trace, and full ESD—into an open-source framework and then uses them to perform *depth-dependent* and *stage-wise* architectural analyses (BN vs residual connections) in modern ResNets.

**Training procedure / hyperparameters.** For the showcased application, models are trained with **SGD with momentum** and Hessian metrics are tracked “throughout training at all checkpoints.” They report using **various initial learning rates** and selecting the best-performing run; however, exact values (LR, momentum coefficient, batch size, weight decay, schedule) are referenced as being in Appendix C and are not present in the provided excerpt. The training horizon shown in figures is **180 epochs**.

### Experiments & Results
**Goal and experimental grid.** The experiments use PYHESSIAN to measure Hessian spectrum statistics—(i) **top eigenvalues**, (ii) **Hessian trace**, and (iii) **full Hessian eigenvalue spectral density (ESD)**—over the full training trajectory of ResNet variants, with the specific aim of testing claims about whether **BN** and **residual connections** “smooth” the loss landscape.

**Datasets.** They evaluate on **CIFAR-10** (primary) and report that all qualitative findings replicate on **CIFAR-100** (shown in the Appendix). (Standard dataset sizes are 50k train / 10k test for each; the excerpt itself does not explicitly state sizes or any validation split.) Inputs are 32×32 images; preprocessing/augmentation details are not included in the excerpt.

**Models and ablations.**
- Baseline: **ResNet** with both residual connections and BN.
- **ResNet−BN**: remove BatchNorm layers.
- **ResNet−Res**: remove residual connections.
- Depths: **ResNet20/32/38/56**.
- Additional fine-grained ablations: remove BN or residual connections from **specific stages** (stages defined as blocks with the same activation resolution).

**Metrics.**
- Primary task metric: **test accuracy (%)** on CIFAR-10.
- Curvature metrics: **Hessian trace** \(\mathrm{Tr}(H)\), **top eigenvalues**, and **ESD support/range** (qualitatively via density plots), all measured at checkpoints across epochs.
- Visualization: parametric **2D loss landscapes** by perturbing parameters along the **first two Hessian eigenvectors** (Fig. 1) at end of training (and additional epoch-wise visualizations in Appendix figures).

**Key quantitative results (CIFAR-10 accuracy).**

Table: Overall accuracy for full-model ablations (Table I).
| Model | Depth 20 | Depth 32 | Depth 38 | Depth 56 |
|---|---:|---:|---:|---:|
| ResNet | 92.01% | 92.05% | 92.37% | 93.59% |
| ResNet−BN | 87.27% | 66.57% | 53.65% | N/A (cannot train) |
| ResNet−Res | 90.66% | 89.8% | 88.92% | 87.38% |

Stage-wise BN removal accuracy (Table II).
| Model | Depth 20 | Depth 32 | Depth 38 | Depth 56 |
|---|---:|---:|---:|---:|
| ResNet | 92.01% | 92.05% | 92.37% | 93.59% |
| Remove BN stage 1 | 91.28% | 91.98% | 92.20% | 92.19% |
| Remove BN stage 2 | 91.49% | 91.94% | 91.70% | 92.20% |
| Remove BN stage 3 | 90.59% | 88.57% | 86.96% | 73.77% |

Stage-wise residual removal accuracy (Table III).
| Model | Depth 20 | Depth 32 | Depth 38 | Depth 56 |
|---|---:|---:|---:|---:|
| ResNet | 92.01% | 92.05% | 92.37% | 93.59% |
| Remove Res stage 1 | 91.52% | 92.27% | 91.74% | 91.79% |
| Remove Res stage 2 | 91.06% | 91.07% | 91.08% | 91.28% |
| Remove Res stage 3 | 91.54% | 92.09% | 92.14% | 92.34% |

**Main Hessian findings (full network).**
1) **Removing BN generally inflates curvature for deeper nets, but can *flatten* curvature for shallow nets.** From the Hessian trace curves (Fig. 2) and ESD evolution (Fig. 3 + Appendix), removing BN causes a **rapid trace increase** for deeper ResNets (e.g., ResNet32/38). The text highlights a concrete magnitude example: for ResNet32, \(\mathrm{Tr}(H)\) for ResNet−BN rises to ~**10000** vs ~**2000** for baseline ResNet. In contrast, for **ResNet20**, ResNet−BN has **lower** trace and a “flatter” loss landscape than the BN baseline, contradicting the general claim (from [45]) that BN necessarily smooths landscapes.

2) **Residual connections consistently smooth across depths (relative).** Removing residuals (ResNet−Res) produces consistently **higher Hessian trace** than baseline (Fig. 2) and increases top eigenvalues / ESD support, with sharper minima becoming more pronounced as depth grows (Fig. 1 visualizations; ESD plots referenced across figures).

**Training dynamics nuance (BN removal).** The ESD evolution plots show a characteristic behavior for ResNet−BN models: early in training, the spectrum can cluster around **near-zero/degenerate directions** (many small eigenvalues), followed by later epochs where **non-degenerate directions** emerge—interpreted as training difficulty not captured by a single “smoothness” heuristic.

**Stage-wise curvature–accuracy correlation.** Stage-wise trace (Fig. 4) indicates BN is “more important” in later stages: removing BN from **stage 3** yields a **much larger trace increase** and the largest accuracy drops (Table II), especially severe at depth 56 (down to 73.77%). Residual removal yields smaller trace changes and correspondingly smaller accuracy impacts (Table III).

**Baselines / comparisons.** Rather than benchmarking against alternative Hessian toolkits, experimental comparisons are primarily **architectural ablations** (BN vs no-BN; residual vs no-residual) and discussion against prior qualitative claims in [45] (BN smoothness via first-order analysis) and [29] (residuals produce smoother landscapes via random-direction visualization). No statistical significance intervals or repeated-run variance are reported in the excerpt.

**Compute / cost.** They do not report GPU-hours or throughput numbers, but repeatedly emphasize that Hessian matvec cost is comparable to a backprop step (Eq. 2) and that PYHESSIAN supports distributed-memory execution, implying practical feasibility for state-of-the-art nets.

### Discussion & Conclusion
PYHESSIAN enables scalable, matrix-free Hessian diagnostics (top eigenvalues, trace, and ESD) for modern deep nets and reveals that curvature “smoothness” effects of BN are **depth-dependent**: BN removal can *flatten* shallow networks while making deeper networks substantially sharper and harder to train. Residual connections show a more consistent smoothing effect across depths, and stage-wise analysis suggests BN is particularly critical in later ResNet stages, with curvature increases correlating with accuracy degradation. Limitations implied by the excerpt include reliance on specific architectures/datasets (ResNets on CIFAR) and largely qualitative curvature–generalization interpretations, motivating future work on broader models and second-order optimization uses of the framework.

## Key Contributions
- **Framework:** Introduces **PYHESSIAN**, an open-source, scalable framework for **matrix-free Hessian spectrum computation** (top eigenvalues via power iteration, trace via Hutchinson, and full ESD via SLQ) with distributed-memory support.
- **Empirical curvature analysis:** Provides **depth-dependent** Hessian evidence that challenges the blanket claim that **BatchNorm always smooths** the loss landscape; for shallow ResNets (ResNet20), removing BN can yield a *flatter* Hessian spectrum than the BN baseline.
- **Fine-grained architectural diagnostics:** Demonstrates **stage-wise** Hessian tracing in ResNets, showing BN’s disproportionate importance in the **final stage**, where removing BN strongly increases Hessian trace and sharply reduces test accuracy.

## Potential Relevance
For hypothesis development, this paper offers a concrete toolkit and methodology to test architectural/optimizer claims using **second-order** evidence (trace/ESD), rather than relying on first-order proxies or low-dimensional random-direction plots. The depth- and stage-dependent BN findings suggest hypotheses about **where curvature control matters** (late-stage representations) and caution against assuming monotonic “BN → smoother” behavior—useful when designing normalization/skip-connection variants or diagnosing training instabilities via Hessian trace/ESD trajectories.