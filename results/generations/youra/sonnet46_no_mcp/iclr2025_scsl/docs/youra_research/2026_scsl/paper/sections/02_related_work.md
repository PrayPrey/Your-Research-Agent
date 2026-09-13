# 2. Related Work

## 2.1 SGD Learning Dynamics: Frequency Principle and Simplicity Bias

A foundational body of work characterizes the implicit biases of SGD toward learning certain feature types before others. The Frequency Principle [Xu et al., 2019] — also termed spectral bias [Rahaman et al., 2019] — establishes empirically and theoretically that neural networks trained with gradient descent learn lower-frequency components of the target function before higher-frequency ones. This ordering emerges from the eigenstructure of the neural tangent kernel and has been replicated across architectures including fully-connected networks, CNNs, and transformers. Importantly, spatial frequency in image features directly maps to feature complexity: low-frequency features (large-scale textures, backgrounds) are simpler and learned first; high-frequency features (fine-grained morphological detail) require more training signal.

Building on this, Shah et al. [2020] demonstrate the Simplicity Bias: with high probability, SGD converges to the simplest classifier consistent with the training data, even when more complex, generalizing classifiers exist. Their analysis shows that linearly separable features are preferentially encoded over features requiring nonlinear separation — a bias that directly predicts spurious correlation acquisition when spurious features happen to be more linearly separable than core features.

**Limitation for our setting:** Both the Frequency Principle and Simplicity Bias are characterized on synthetic tasks (sinusoidal regression, XOR classification) or controlled image datasets. Neither paper establishes a measurement protocol for the temporal dynamics of spurious vs. core feature learning on real-world spurious correlation benchmarks (Waterbirds, CelebA). Our work provides this operationalization: the first δ(t) measurement framework connecting optimization theory to standard benchmark evaluation.

## 2.2 Spurious Correlation: Benchmarks and Mitigation Methods

The spurious correlation problem in deep learning was formalized by Sagawa et al. [2020] through the introduction of Group Distributionally Robust Optimization (GroupDRO) and the Waterbirds and CelebA benchmarks. GroupDRO minimizes the worst-group training loss using group annotations, setting the gold standard for WGA improvement. Subsequent work has focused on reducing reliance on group labels.

Just Train Twice (JTT) [Liu et al., 2021] identifies a set of "minority" samples (those misclassified by a first-pass ERM model) and upweights them in a second training run, implicitly exploiting the observation that ERM models fail on minority groups whose examples require core features. Deep Feature Reweighting (DFR) [Kirichenko et al., 2022] takes a simpler approach: train ERM normally, then refit only the last linear layer using a class-balanced held-out split. DFR achieves state-of-the-art WGA without group annotations, with the key observation that "ERM backbones already encode core features." LastLayerEnsemble [Rosenfeld et al., 2022] and related methods further explore last-layer reweighting strategies.

**Limitation for our setting:** These methods implicitly exploit training dynamics without quantifying them. JTT's error-set identification depends on which samples are hard to learn — a temporal property — but JTT does not measure *when* or *why* these samples are hard. DFR's success rests on the assumption that core features are present in ERM representations, but does not characterize *when* they become present or how the temporal competition with spurious features unfolds. Our work addresses this gap: we measure the temporal dynamics that these methods implicitly exploit, providing mechanistic grounding for their behavior.

## 2.3 Early Training Dynamics and Shortcut Learning

Mangalam and Girshick [2021] provide the closest prior observation to our work, showing that shortcut features emerge preferentially during early training phases. They observe that models trained on datasets with spurious correlations quickly acquire shortcuts in the first few epochs, with core features following later. However, this observation is made qualitatively, without a systematic measurement protocol, statistical validation across seeds, or characterization of the gradient mechanism driving the asymmetry.

Frankle et al. [2019] identify the lottery ticket phenomenon in early training, showing that subnetworks identified early in training can be rewound and retrained to full performance — implying that critical representational decisions occur in early epochs. Jiang et al. [2020] use per-sample training dynamics (correctness, confidence) to characterize "easy" vs. "hard" examples, with easy examples tending to rely on spurious shortcuts. Toneva et al. [2019] study forgetting events during training, noting that examples forgotten and relearned tend to be minority-group examples. These works collectively suggest that training dynamics carry rich information about spurious correlation acquisition, but none establishes a systematic framework for measuring the temporal competition between feature types.

**Our advance:** We formalize and quantify these observations through the δ(t) framework: a reproducible, statistically validated protocol for measuring the temporal gap between spurious and core feature learning at each training checkpoint, with gradient instrumentation to identify the mechanism.

## 2.4 Linear Probing for Feature Analysis

Linear probing — training a linear classifier on frozen representations — is an established tool for measuring what information is encoded in neural network layers [Alain and Bengio, 2016; Zhang et al., 2022]. Probing has been used to track the emergence of syntactic and semantic information in language models [Tenney et al., 2019], to characterize layer-wise feature quality in vision models [Newell and Deng, 2020], and to evaluate representation quality in self-supervised learning [Chen et al., 2020]. However, applying linear probing to track the *temporal evolution* of separate feature-type probes (spurious-label vs. core-label) during supervised training — the key measurement innovation in our framework — has not been previously explored in the context of spurious correlation benchmarks.

**Our advance:** We apply checkpoint linear probing at every 2 epochs throughout training, using separate probes for spurious and core labels to directly measure δ(t). This transforms probing from a static evaluation tool into a dynamic measurement instrument for feature learning trajectories.

## 2.5 Positioning Summary

| Prior Work | Contribution | Limitation Relative to Ours |
|---|---|---|
| Xu et al. [2019], Rahaman et al. [2019] | Frequency Principle — low-frequency features learned first | Synthetic tasks, no spurious correlation benchmarks |
| Shah et al. [2020] | Simplicity Bias — SGD prefers linearly separable features | Synthetic settings, no measurement protocol for real benchmarks |
| Sagawa et al. [2020] | GroupDRO, Waterbirds/CelebA benchmarks | Focuses on intervention, not temporal measurement |
| Liu et al. [2021] | JTT — exploits training dynamics implicitly | No measurement of when/why shortcuts form |
| Kirichenko et al. [2022] | DFR — ERM backbone encodes core features | No temporal analysis of when core features emerge |
| Mangalam & Girshick [2021] | Shortcuts emerge in early training (qualitative) | No systematic protocol, no statistical validation |

Our work bridges the optimization theory literature (Frequency Principle, Simplicity Bias) with the spurious correlation benchmark literature (GroupDRO, JTT, DFR) through the δ(t) measurement framework — providing the first quantitative, systematically validated characterization of temporal feature learning dynamics on standard benchmarks.
