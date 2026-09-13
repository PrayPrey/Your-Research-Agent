# Introduction

Most ML reproducibility failures occur hours into training, when it's too late. A researcher discovers their model training crashes after 10 hours due to a CUDA device mismatch—an environment-setup error that could have been caught in seconds. This pattern is not an isolated incident: Jiang et al. [1] found that 68% of reproducibility defects surface during training, yet 88% of these failures originate from environment-stage interface errors [1]. This temporal mismatch between defect origin and detection wastes thousands of researcher-hours annually.

The root cause lies deeper than version conflicts. While dependency pinning (pip freeze, conda environments) prevents version drift, it cannot validate behavioral assumptions across library updates. Consider a researcher adapting published code that assumes `torch.nn.functional.softmax()` returns probabilities summing to 1.0—a mathematical invariant that *should* hold but may degrade under floating-point edge cases or undocumented API changes. Without proactive validation, such violations surface only when training diverges or evaluation metrics fail, hours after experiment launch.

Existing solutions target different layers of the reproducibility stack [2, 3]. Version pinning stabilizes dependencies but doesn't validate behavior. Continuous integration testing (pytest, tox) provides repo-specific regression checks but cannot encode reusable library-level invariants. Property-based testing frameworks (QuickCheck [4], Hypothesis [5]) validate software properties but lack ML-specific API focus. What remains missing is a systematic framework for proactive API behavioral validation at environment-setup time—a reproducibility tier that shifts defect detection from training-stage (when failures are expensive) to environment-stage (when they cost seconds, not hours).

We introduce **executable API contracts** as this missing tier. Our key insight is that the majority of environment-stage API defects violate documented invariants testable in <10 seconds before any training begins. These invariants stratify into three complementary tiers: (1) structural contracts validate shapes, data types, and devices at import time via decorator introspection, (2) metamorphic contracts enforce mathematical properties (softmax probability sums, dropout identity under eval mode) through lightweight runtime probes, and (3) composition contracts validate cross-library consistency (device placement across PyTorch-CUDA-HuggingFace stacks) via bidirectional propagation mechanisms.

Building on this insight, we make the following contributions:

**Empirical Contractability Measurement**: We conduct the first systematic analysis of API defect contractability in ML contexts, demonstrating that 74.8% [69.7%, 79.3%] of environment-stage defects from Jiang et al.'s 348-defect corpus are expressible as lightweight executable contracts—stratified as structural (95.7%), metamorphic (95.2%), and composition (89.7%).

**Three-Tier Contract Architecture**: We design and implement a contract validation framework with complementary coverage tiers. Combined contracts achieve 80.46% detection rate with 72% false-negative-rate reduction (McNemar p<0.001) versus single-strategy approaches, demonstrating 2.7× improvement over structural-only validation.

**Lifecycle Shift Mechanism**: We demonstrate that environment-setup deployment shifts defect detection from 32.1% (training-stage baseline) to 75.0% (environment-stage with contracts), achieving 9.57-hour median time-to-first-failure reduction (95% improvement, Wilcoxon p<0.0001) in a prospective trial of 100 simulated pull requests.

**Version-Stable Validation**: We show that contracts remain stable across ±2 minor library releases with 4.0% false-positive rate [1.6%, 9.8%], validating practical deployability under real version drift.

**Design Space Insights**: We reveal that composition contracts require architectural innovation beyond straightforward extension of structural patterns—an initial proof-of-concept achieved 0% contractability due to version instability, which bidirectional propagation mechanisms resolved to 89.7% detection.

We organize the paper as follows: Section 2 positions our work within reproducibility measurement and property-based testing literature. Section 3 details our three-tier contract architecture with rationale for each design decision. Section 4 describes experimental methodology for validating five pre-registered predictions. Section 5 presents evidence supporting our lifecycle-shift mechanism. Section 6 discusses implications, limitations, and broader impact. Section 7 concludes with future research directions.

---

**References (Introduction only - full list in Section 7)**

[1] Jiang et al. (2023). An Empirical Study of Bugs in PyTorch-Based Deep Learning Systems.  
[2] Wolter et al. (2025). Reproducibility Practices in Machine Learning Research.  
[3] Collberg & Proebsting (2016). Repeatability in Computer Systems Research.  
[4] Claessen & Hughes (2000). QuickCheck: A Lightweight Tool for Random Testing.  
[5] MacIver et al. (2019). Hypothesis: A Practical Test Framework for Python.
