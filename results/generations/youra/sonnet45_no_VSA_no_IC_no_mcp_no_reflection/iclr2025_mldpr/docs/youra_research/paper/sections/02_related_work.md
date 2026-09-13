# 2. Related Work

## Benchmark Saturation Analysis

Linzen et al. (2022 est.) survey leaderboard-driven evaluation in ML, documenting the saturation problem where diminishing returns signal benchmark exhaustion. Their work describes the phenomenon qualitatively but does not operationalize detection mechanisms. We build on this problem description by providing quantitative metrics (score convergence thresholds, expert consensus alignment) for automated saturation detection.

Historical benchmark transitions demonstrate organic community migration patterns. ImageNet classification remained dominant despite visible saturation (2015-2020 plateau), with community shift to Vision Transformers occurring ~5 years post-plateau. GLUE-to-SuperGLUE transition similarly spanned 2+ years. These organic transitions lack predictive signals—our work quantifies the 2-6 year lead time between saturation and migration, enabling proactive rotation.

## Alternative Benchmark Proposals

Hendrycks & Dietterich (2019) propose robustness benchmarks (ImageNet-C, ImageNet-A) to address distribution shift limitations in standard evaluations. Their work focuses on *what* should replace saturated benchmarks, but not *how* or *when* to sunset predecessors. We complement this by addressing lifecycle management—systematic deprecation via saturation detection rather than just proposing alternatives.

The broader benchmark design literature emphasizes fairness (Gebru et al., 2018 datasheets), reproducibility (Pineau et al., 2021 checklists), and evaluation rigor. Our contribution adds *rotatability* as infrastructure requirement—benchmarks need sunset mechanisms, not just creation protocols.

## Evaluation Paradigms Beyond Leaderboards

Recent work explores alternatives to static benchmark evaluation: few-shot prompting (Brown et al., 2020), human-AI collaboration metrics (Bansal et al., 2021), and dynamic evaluation (Nie et al., 2020). While these paradigms avoid saturation by design (no fixed leaderboard), adoption requires replacing existing benchmark infrastructure entirely. Our approach enables incremental adoption—saturation detection integrates with existing leaderboard systems (Papers With Code) without disrupting current workflows.

## Positioning

Prior work establishes that (1) benchmark saturation is a recognized problem (Linzen), (2) alternative evaluation paradigms exist (Hendrycks, dynamic evaluation), and (3) benchmark transitions occur organically (ImageNet→ViT, GLUE→SuperGLUE). We contribute the *infrastructure layer*—automated saturation detection with temporal precedence validation, enabling proactive benchmark rotation rather than reactive organic migration.

**Word count:** ~365 words
