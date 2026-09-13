# Related Work

We organize related work around three themes: (1) spurious correlation detection and mitigation, (2) understanding learning dynamics and simplicity bias, and (3) optimization-based approaches to robustness. Across these areas, we highlight how existing work either assumes or remains agnostic about the gradient competition mechanism we test.

## Spurious Correlation Detection and Mitigation

The spurious correlation problem has attracted significant attention as practitioners deploy models to settings where training-time correlations break. Sagawa et al. [2020] introduced Group DRO, which minimizes worst-group loss when group annotations are available, establishing the Waterbirds benchmark we use. Their approach achieves strong worst-group accuracy (91%) but requires expensive group labels at training time.

Annotation-free methods have emerged to address this limitation. JTT [Liu et al., 2021] exploits the observation that models misclassify minority-group examples early in training; it identifies these errors and upweights corresponding examples in a second training phase. Environment Inference for Invariant Learning [Creager et al., 2021] clusters training examples to infer pseudo-environments. Spread Spurious Attribute (SSA) [Nam et al., 2022] estimates spurious attributes without supervision.

These methods implicitly rely on early-training signals to identify spurious reliance, but do not directly measure the gradient dynamics underlying why spurious features are learned preferentially. Our work tests the mechanistic assumption that spurious features receive stronger gradient signals.

## Simplicity Bias and Learning Dynamics

Shah et al. [2020] formalized simplicity bias: neural networks preferentially learn simpler features when multiple predictive features are available. Their theoretical analysis shows that linear networks and nonlinear networks with certain activation functions exhibit this bias due to gradient flow properties. However, they study feature learning order rather than per-sample gradient magnitudes.

Dataset Cartography [Swayamdipta et al., 2020] maps training dynamics by tracking prediction confidence and variability across epochs, identifying "easy," "hard," and "ambiguous" examples. While this characterizes learning dynamics, it does not directly connect to spurious feature attribution or test the gradient competition hypothesis.

Arpit et al. [2017] showed that networks learn "easy" patterns before memorizing noise, and Kalimeris et al. [2019] demonstrated increasing complexity of learned functions over training. These works establish that learning order depends on pattern simplicity but do not measure whether simpler patterns receive stronger or weaker gradient signals.

Our work bridges this gap by directly measuring gradient norms for spurious-aligned versus minority samples, testing whether gradient magnitude explains the simplicity bias phenomenon.

## Optimization-Based Robustness

Sharpness-Aware Minimization (SAM) [Foret et al., 2021] seeks parameters in flat loss landscape regions, improving generalization across domains. While originally motivated by generalization bounds, recent work connects SAM to robustness under distribution shift [Bahri et al., 2022].

The connection between loss landscape geometry and spurious feature reliance remains unexplored. Our falsification of the gradient competition hypothesis suggests that convergence speed—how quickly different samples reach low loss—may be more relevant than gradient magnitude. This connects to SAM's implicit mechanism: if spurious patterns occupy sharper minima, SAM's sharpness penalty would disfavor them.

Implicit regularization in SGD [Smith & Le, 2018; Barrett & Dherin, 2021] provides theoretical grounding for how optimizer dynamics affect generalization. Smaller batch sizes and larger learning rates implicitly regularize toward flatter minima. We originally hypothesized that these dynamics could control spurious feature timing, but our mechanism experiments reveal that the gradient competition framing is incorrect.

## Our Position

Existing work establishes that (1) spurious correlations harm worst-group performance, (2) simplicity bias causes preferential learning of simple features, and (3) loss landscape geometry affects generalization. However, the assumed mechanism—that simple/spurious features dominate through stronger gradients—has not been directly tested.

We provide this test, finding that the gradient competition hypothesis is empirically falsified. Rather than proposing a new mitigation method, we contribute a mechanistic insight: spurious dominance arises from convergence speed (fast low-loss achievement), not gradient magnitude. This reframing has implications for how robustness interventions should be designed.
