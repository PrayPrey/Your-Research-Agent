## Abstract

Self-supervised learning (SSL) on spurious correlation benchmarks produces representations that dramatically fail on minority groups. We document a 73.4 percentage-point worst-group accuracy (WGA) gap between DINO SSL (8.6%) and supervised training (81.9%) on Waterbirds — a gap that persists throughout training despite 62% average accuracy, indicating a geometrically stable shortcut in the loss landscape rather than a convergence failure.

We propose *sharpness anisotropy* as the geometric mechanism: SSL pretraining with SGD creates directional curvature asymmetry in the InfoNCE loss landscape, privileging spurious feature directions. We introduce an annotation-free measurement protocol using SAM perturbations to quantify this anisotropy without group labels, and propose replacing SGD with SAM during SSL pretraining as a training-time geometric intervention — the first application of SAM to SSL spurious correlation robustness.

The 73.4 pp WGA gap is confirmed. The anisotropy measurement and SAM-SSL intervention results are pending 200-epoch experimental runs. We report the problem's severity, the geometric hypothesis with full experimental design, and a diagnostic protocol composable with existing post-hoc debiasing methods.
