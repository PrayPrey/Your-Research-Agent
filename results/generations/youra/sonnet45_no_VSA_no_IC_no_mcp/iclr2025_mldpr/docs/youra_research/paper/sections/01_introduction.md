# Introduction

When a medical imaging dataset shifts from X-ray to MRI scans without formal notice, models trained on deprecated data silently degrade—yet major ML repositories lack the automated deprecation mechanisms that have been standard in software package managers for decades. HuggingFace Datasets Hub hosts over 60,000 datasets with informal versioning; maintainers manually track deprecation through README updates and GitHub discussions, creating information asymmetry where users unknowingly train on stale data. Without formal deprecation mechanisms, the growing ecosystem of shared ML datasets becomes a liability rather than an asset—every deprecated dataset is a latent failure mode in downstream systems.

Dataset deprecation affects reproducibility, model maintenance, and deployment reliability—core infrastructure problems that scale with ML adoption. Current practice relies on documentation-only signals (README warnings) that fail at three critical points: (1) automated detection of deprecation candidates, (2) task-specific successor mapping, and (3) point-of-use adoption tracking. Software package managers (NPM, PyPI) solved analogous problems for code dependencies via automated deprecation warnings and version constraints, but ML datasets were treated as static artifacts rather than living dependencies requiring lifecycle management.

We observe that datasets are dependencies with deprecation lifecycles similar to software packages, but with unique requirements: health metrics based on usage velocity rather than semantic versioning, context-aware successor graphs because task matters (ImageNet→ImageNet-v2 for robustness vs ImageNet-21k for pretraining), and load-time instrumentation for adoption measurement. No existing system combines automated health metrics (for deprecation candidate detection), context-aware successor graphs (for task-specific recommendations), and instrumented policies (for adoption tracking)—each exists in isolation or not at all.

Building on this insight, we present a three-component formal deprecation system validated through mechanistic experiments on proof-of-concept scale infrastructure. **Our key contributions are:**

1. **System Design:** Three-component architecture integrating automated health metrics (velocity, emergence, issue signals), context-aware successor graphs (task-conditional replacement paths), and load-time instrumentation (adoption measurement telemetry)

2. **Mechanistic Validation:** Five sub-hypothesis experiments (h-e1, h-m1, h-m2, h-m3, h-m4) demonstrating feasibility—health metrics achieve 88.3% precision (exceeding 60% target), context inference achieves 100% accuracy on synthetic patterns (target ≥70%), instrumentation adds <5% overhead (target <10%)

3. **Measurement Infrastructure:** First quantitative telemetry infrastructure for dataset adoption tracking (100% capture rate with 95% CI: 99.05%-100%), enabling future efficacy studies comparing formal vs informal deprecation mechanisms

Validated at proof-of-concept scale on simulated/synthetic HuggingFace-compatible data, our results demonstrate that formal dataset deprecation mechanisms are feasible. Efficacy measurement (adoption lift vs baseline) requires deployment-scale testing and is future work (Phase 5 baseline comparison was not performed).
