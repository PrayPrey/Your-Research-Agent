---
source_paper: "arxiv_2603_07323.md"
generated_at: "2026-03-16T20:43:23.988850"
model: "gpt-4o-mini"
summary_chars: 7976
---

# Norm-Hierarchy Transitions (NHT)

## Key Metadata
- **Authors:** Truong Xuan Khanh, Truong Quynh Hoa
- **Year:** 2026
- **Venue:** arXiv
- **Core Contribution:** Introduction of the Norm-Hierarchy Transition framework to explain the delayed representational transitions in neural networks during training.

## Section Summaries

### Abstract
Neural networks often rely on spurious shortcuts for hundreds of epochs before discovering structured representations. Yet the mechanism governing when this transition occurs—and whether its timing can be predicted—remains poorly understood. While prior work has established that gradient descent converges to low-norm solutions [Soudry et al., 2018] and that networks exhibit simplicity bias [Shah et al., 2020], neither line of work characterizes the timescale of the transition from simple to structured features. We propose a unifying framework—the Norm-Hierarchy Transition—which explains delayed representation learning as the slow traversal of a norm hierarchy under regularized optimization. When multiple interpolating solutions exist with different norms, weight decay induces a slow contraction from high-norm shortcut solutions toward lower-norm structured representations. We prove a tight bound on the transition delay: \( T = \Theta(\gamma_{\text{eff}}^{-1} \log(V_{\text{sc}}/V_{\text{st}})) \), where \( V_{\text{sc}} \) and \( V_{\text{st}} \) are the characteristic norms of the shortcut and structured representations. The framework predicts three regimes as a function of regularization strength: weak regularization (shortcuts persist), intermediate regularization (delayed transition), and strong regularization (learning suppressed). We validate these predictions across four domains: modular arithmetic, CIFAR-10, CelebA, and Waterbirds. The norm-hierarchy mechanism is robust across architectures: ResNet18 with standard batch normalization exhibits the same peak-then-decay norm dynamics, achieving 78% clean accuracy. The single prediction that fails to transfer—the precise delay scaling \( T \propto 1/\lambda \)—is explained by a new condition we term clean norm separation, the first formal criterion distinguishing settings where implicit bias timescales are predictable. Our results suggest that grokking, shortcut learning, delayed feature discovery, and emergent abilities are manifestations of a single mechanism: the slow traversal of a norm hierarchy under regularized optimization.

### Introduction & Motivation
Neural networks often exploit spurious shortcuts before discovering meaningful features, leading to a delay in representational transition. This paper aims to unveil the mechanisms that govern this delay, applying a systematic understanding of parameter norm dynamics under regularized training. Specifically, it focuses on delayed transitions wherein networks initially favor high-norm (shortcut) representations before slowly converging to low-norm (structured) representations. By addressing this gap, the authors elucidate the relationship between regularization strength and the representational dynamics.

### Methodology
The Norm-Hierarchy Transition (NHT) framework is proposed to explain the dynamics of representational transitions during training. The authors analyze neural networks under regularized gradient descent, where they characterize the transition through multiple definitions and theorems:

1. **Training Update Rule**: The model parameters are updated using the formula:
   \[
   \theta_{t+1} = \theta_t - \eta \left(\nabla L_{\text{train}}(\theta_t) + 2\lambda \theta_t\right) + \eta \xi_t,
   \]
   where \( \eta \) is the learning rate, \( \lambda \) is the weight decay coefficient, and \( \xi_t \) is noise.

2. **Key Definitions**:
   - **Multi-Representation Interpolation**: Training allows representations \( M_{\text{sc}} \) (shortcut features) and \( M_{\text{st}} \) (structured features).
   - **Norm Hierarchy**: If \( \| \theta \|_2 \geq V_{\text{sc}} \) for \( \theta \in M_{\text{sc}} \) and \( \| \theta^* \|_2 \leq V_{\text{st}} \) for \( \theta^* \in M_{\text{st}} \).
   - **Shortcut Accessibility**: The model reaches the shortcut solution first.

3. **Theorem on Transition Delay**: The authors prove that any learning system with multi-representation interpolation leads to a delayed transition with a logarithmic delay given by:
   \[
   T_{\text{transition}} = \Theta\left(\frac{1}{\gamma_{\text{eff}}} \log\left(\frac{V_{\text{sc}}}{V_{\text{st}}}\right)\right),
   \]
   where \( \gamma_{\text{eff}} \) is the effective contraction rate of the optimizer.

4. **Training Procedure**: Training is conducted using AdamW optimizer, with loss defined by \( L_{\text{train}} \) subjected to \( \ell_2 \) regularization. Key hyperparameters include a learning rate \( \eta = 10^{-3} \) and various decay rates \( \lambda \).

### Experiments & Results
The authors validate their framework against four distinct domains: modular arithmetic, CIFAR-10 with spurious features, CelebA (face attributes), and Waterbirds (background) through systematic experiments regulated by different \( \lambda \) values.

1. **Dataset and Configuration**:
   - **CIFAR-10**: Modified to include colored shortcuts; trained with a colored border correlated with labels. 
   - **Modular Arithmetic, Waterbirds, CelebA**: Each evaluated with respective models and training setups.

2. **Evaluation Metrics**: The experiments measure accuracy using clean accuracy on datasets devoid of shortcuts, encapsulated by a representation phase diagram corresponding to a norm-structure relationship.

3. **Key Findings**:
   - **Three-Phase Structure**: Confirmed across experiments with \( \lambda \) values. The clean accuracy varies significantly with respect to regularization and correlation strength.
   - **Norm Dynamics**: Displayed peak-then-decay behavior across architectures, particularly illustrating that layers with higher shortcut encoding capacity escape the high-norm region first (Proposition 4.2).

4. **Ablation Studies**: The authors evaluate different architectures, including ResNet variants, showing consistent norm dynamics across models. Batch normalization was found to improve performance significantly compared to non-normalized architectures.

5. **Validation**: The framework's predictions were rigorously tested, achieving varying degrees of confirmation across diverse experimental setups, with modular arithmetic showing the highest accuracy of model predictions.

### Discussion & Conclusion
The Norm-Hierarchy Transition framework unifies various phenomena—grokking, shortcut learning, and emergence of capabilities in large models—under a single mechanistic model describing how and when networks transition between shortcuts and structured representations. The authors note limitations such as the non-transferability of precise scaling laws of time delays and express the need for future work focused on deeper explorations into feature-wise norm decompositions and generalization to NLP tasks. The findings offer significant insights into improving neural network training strategies by diagnosing shortcut reliance and optimizing regularization.

## Key Contributions
- Introduction of the Norm-Hierarchy Transition framework to explain representational delays in neural networks.
- Proven logarithmic bounds on transition delays, yielding insights across multiple domains.
- Demonstrated robustness of the norm-dynamics mechanism against various architectural deviations, refining models for optimal representation learning.

## Potential Relevance
The insights from the NHT framework may significantly inform future experiments on delayed learning mechanisms and effective training methods by highlighting the roles of regularization and norm dynamics. Understanding these transitions could be instrumental in addressing shortcut learning issues and enhancing model capability emergence paradigms in larger architectures.