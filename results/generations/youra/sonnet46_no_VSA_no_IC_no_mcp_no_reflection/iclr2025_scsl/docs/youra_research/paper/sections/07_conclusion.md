# Conclusion

We opened with a counterintuitive finding: spurious-minority samples appear *more* aligned with the within-batch mean gradient than majority samples on Waterbirds at epoch 1 (alignment ROC-AUC = 0.150), despite the theoretical prediction that conflicting gradient directions should reveal them. This inversion is not noise — it is the signature of a specific, diagnosable failure mode: batch contamination by high-magnitude minority gradients.

The results are clear. Per-sample last-layer gradient cosine similarity with the within-batch mean gradient fails as a spurious-minority detector across both Waterbirds (alignment ROC-AUC ≤ 0.35 at all epochs) and CelebA (≤ 0.63 at all epochs), while per-sample loss achieves 0.77–0.97 under identical conditions. The failure is not marginal: the gap reaches 0.78 on Waterbirds at epoch 1. Per-sample loss remains the practical baseline for annotation-free minority identification.

But the inversion is a diagnosis, not a dead end. The within-batch mean gradient is contaminated by the very samples it is meant to distinguish — high-loss minority samples pull the batch average toward their own gradient direction, paradoxically increasing their measured alignment score. This contamination is structural: it follows from the combination of mini-batch imbalance and the high gradient magnitude of minority samples. It predicts that minority prevalence modulates the failure severity, consistent with CelebA's weaker inversion at lower prevalence. And it points directly to the correction: a two-pass global mean gradient, stable and majority-dominated across thousands of samples, is not subject to per-batch contamination spikes.

**What we have established:**
- Within-batch gradient cosine similarity fails as a spurious-minority proxy — empirically, at all tested epochs, on both standard benchmarks
- The failure is mechanistic, not accidental: batch contamination produces an anti-predictive signal at early epochs when gradient magnitudes are largest
- The fix is principled and computationally tractable: two-pass global mean gradient reference, one additional full-dataset pass per epoch, annotation-free

**The open question** — whether the global mean correction resolves the inversion — remains for future work, along with penultimate-layer alignment (to test whether last-layer gradient compression is also a failure contributor) and a systematic prevalence experiment to quantify the contamination threshold.

Gradient direction as a minority detection signal remains theoretically well-motivated. The failure characterized here is a failure of the *reference direction*, not of the concept. Correcting the reference direction is the single most important next experiment. If the inversion disappears with global mean reference, Gradient Alignment Debiasing becomes a viable candidate for annotation-free online debiasing — a single training run, no two-stage procedure, no group labels required.
