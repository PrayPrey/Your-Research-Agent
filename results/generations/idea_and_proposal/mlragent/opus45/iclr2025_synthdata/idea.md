## Title: Diversity-Aware Synthetic Data Generation with Automatic Distribution Calibration

## Motivation:
A critical yet underexplored limitation of synthetic data is **mode collapse** and **distribution drift** — synthetic data generators often produce samples that cluster around common patterns while missing rare but important edge cases. This leads to models that perform well on average but fail catastrophically on underrepresented scenarios. Current approaches lack principled methods to detect and correct these distributional gaps, limiting synthetic data's ability to truly replace real data access.

## Main Idea:
We propose **AutoCalib**, a framework that automatically detects and corrects distributional mismatches between synthetic and target real data distributions. The methodology consists of three components:

1. **Distribution Gap Detection**: Using kernel-based methods and density ratio estimation to identify regions where synthetic data under/over-represents the true distribution, without requiring direct access to real data (using only summary statistics or pretrained embeddings).

2. **Guided Regeneration**: Employing a feedback loop that conditions the synthetic data generator to oversample detected sparse regions through targeted prompting or latent space manipulation.

3. **Coverage Verification**: A lightweight verification module that certifies distributional coverage using conformal prediction principles.

**Expected Outcomes**: Improved downstream model robustness, especially on tail distributions, with 15-30% gains on rare-case benchmarks. This addresses fundamental reliability concerns, enabling synthetic data to serve as a trustworthy substitute for sensitive real data in high-stakes domains like healthcare and autonomous systems.