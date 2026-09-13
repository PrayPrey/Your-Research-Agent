# Abstract

Can we tell how a language model was trained from its benchmark scores alone?
We show that the answer is yes: a model's alignment strategy — Direct Preference
Optimization (DPO) versus Supervised Fine-Tuning (SFT) — can be inferred from four
standard trustworthiness benchmarks without any access to training data, at 83.3%
leave-one-out accuracy (permutation p=0.031, n=12 models). Surprisingly, the
signal that makes this inference possible is not fairness, as alignment theory
would predict, but truthfulness: TruthfulQA MC2 carries 9.5× more discriminative
information than the next benchmark, with DPO models scoring higher on truthfulness
than matched SFT models — the opposite of the predicted direction. Fairness
benchmarks (BBQ, WinoGender) show no systematic DPO advantage. These results
establish practical alignment auditing from public leaderboard data while
challenging the widely-held assumption that DPO preference training primarily
improves fairness, and motivate new inquiry into what preference optimization
actually optimizes.
