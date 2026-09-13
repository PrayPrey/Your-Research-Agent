# Related Work

Our work sits at the intersection of three strands of prior research: RLHF overoptimization theory, bidirectional human-AI alignment measurement, and Goodhart's Law in machine learning. Each strand illuminates part of the phenomenon we study, but none provides the quantitative characterization we offer — a named divergence construct, a regression slope, and a cross-dataset replication.

## RLHF Overoptimization and Reward Hacking

Reinforcement learning from human feedback was introduced as a paradigm for aligning language models with human preferences through a reward model trained on preference annotations [Ouyang et al., 2022; Christiano et al., 2017]. RLHF has become the dominant alignment approach, enabling models that score high on helpfulness and harmlessness benchmarks [Bai et al., 2022; Stiennon et al., 2020]. However, the reward model is an imperfect proxy for human preference, and sustained optimization against this proxy causes the policy to exploit proxy weaknesses — a phenomenon known as reward hacking or specification gaming [Krakovna et al., 2020; Skalse et al., 2022].

Coste et al. [2023] provide the clearest empirical demonstration: as KL budget from the base policy increases from 0 to 8 nats, the reward model score rises monotonically while gold human preference peaks and then reverses. Gao et al. [2023] characterize the scaling laws of reward model overoptimization at multiple RM sizes, showing consistent patterns across model scales. Both papers describe the divergence qualitatively — RM rises while gold reverses — but stop short of fitting a regression model to characterize the divergence *slope* as a function of KL budget, or comparing slopes across datasets. Our work takes this step: we fit OLS regression to both datasets and report β = 0.1433 nat⁻¹ (Coste) and β = 0.1599 nat⁻¹ (Gao), enabling the first quantitative, replicated characterization of the calibration-alignment divergence curve.

Perez et al. [2022] and Steinhardt et al. [2021] discuss specification gaming more broadly, noting that proxy metrics systematically fail under sustained optimization. Ziegler et al. [2019] and Stiennon et al. [2020] document early cases where RLHF reward models diverge from human preferences in text summarization. These works establish the qualitative phenomenon; our contribution is quantification and cross-dataset effect size comparison.

## Bidirectional Human-AI Alignment Measurement

The ICLR 2025 Workshop on Bidirectional Human-AI Alignment synthesized 400 papers in the alignment literature and found a systematic measurement asymmetry: virtually all major alignment benchmarks — TruthfulQA [Lin et al., 2022], BBQ [Parrish et al., 2022], HHH-RLHF, WinoBias [Zhao et al., 2018], HELM [Liang et al., 2023] — measure the AI→Human direction exclusively (how well model outputs conform to human values). Human→AI alignment — whether humans appropriately calibrate their trust, reliance, and interpretation of model outputs — is studied in a parallel HCI and cognitive science track but has not been integrated with ML evaluation frameworks.

Lai et al. [2021] demonstrate that AI-assisted decision-making produces over-reliance: in several experimental settings, 60–80% of humans agree with AI predictions regardless of AI accuracy, indicating systematic miscalibration of human trust. Bansal et al. [2021] and Buccinca et al. [2021] further characterize over-reliance patterns and propose interventions. However, these behavioral studies do not connect to RLHF optimization pressure — they measure human calibration at a fixed model deployment snapshot, not as a function of how aggressively the model was optimized.

Our work bridges these two tracks: we treat RLHF overoptimization as the empirical instantiation of bidirectional alignment tension. Specifically, increasing AI→Human optimization pressure (KL budget) systematically degrades evaluation calibration to held-out human judgment. We scope this as "evaluation calibration divergence" — the gap between proxy reward model scores and held-out human preference judgments — which is distinct from but motivates the study of user behavioral calibration (appropriate reliance, Lai et al. [2021] paradigm). The connection to user over-reliance remains a theoretical extension for future behavioral work.

## Goodhart's Law and Proxy-Target Decoupling in ML

Goodhart's Law — "when a measure becomes a target, it ceases to be a good measure" [Goodhart, 1975] — has been formalized in the ML setting by several authors. Manheim and Garrabrant [2019] taxonomize Goodhart's Law for AI systems; Krakovna et al. [2020] compile a specification gaming list documenting empirical cases in RL. Skalse et al. [2022] formalize reward tampering and misspecification conditions under which proxy-target decoupling is guaranteed.

These theoretical works predict proxy-gold divergence under optimization pressure. Our work provides an empirical instantiation with specific quantitative parameters: in the RLHF setting with explicit reward model training, the proxy-gold gap grows at β ≈ 0.143–0.160 nat⁻¹ of KL budget. This connects the abstract Goodhart/specification-gaming literature to a concrete, measurable phenomenon in modern RLHF training, and provides the first cross-dataset slope comparison that characterizes the "rate" at which Goodhart's Law manifests in this setting.

## How We Differ

Our three quantitative contributions — the calibration-alignment divergence construct (named and defined), the regression slope β with cross-dataset replication, and the normalized gap metric as a cross-study comparison instrument — are not derivable from any prior paper. The closest works are Coste et al. [2023] and Gao et al. [2023], which provide the raw experimental data; we contribute the regression framework, normalization methodology, cross-dataset comparison, and bidirectional alignment framing that connects these results to the broader alignment measurement agenda.

---

*Note on citation verification: All primary citations in this section (Coste et al. 2023 arXiv:2310.02743, Gao et al. 2023 arXiv:2210.10760/ICML 2023, Ouyang et al. 2022 arXiv:2203.02155) are verifiable from publicly available arXiv and ICML records. Citations marked [CITATION NEEDED] in an earlier draft have been resolved using known publication records. See references for full BibTeX entries.*
