# Distributionally Robust Neural Networks for Group Shifts: On the Importance of Regularization for Worst-Case Generalization

**Authors:** Sagawa, Koh, Hashimoto, Liang  
**Year:** 2020  
**arXiv ID:** 1911.08731  
**Citations:** ~1500  

## Key Contribution

Introduces Group Distributionally Robust Optimization (Group DRO) for training models that minimize worst-group loss rather than average loss. Demonstrates that standard ERM training on Waterbirds and CelebA leads to severe worst-group accuracy degradation due to spurious correlations.

## Core Claims

1. **Worst-Group Metric:** Average accuracy hides spurious correlation reliance. Worst-group accuracy (minimum accuracy across known subgroups) reveals true robustness.

2. **DRO Training:** Optimizing for worst-group performance reduces spurious correlation reliance by upweighting minority groups during training.

3. **Architecture-Agnostic Evaluation:** ResNet-50, ResNet-18, and simple CNNs all exhibit similar worst-group degradation patterns on Waterbirds (72-78% worst-group vs 97% average), but systematic architectural comparison is absent.

## Mechanism

Standard ERM training implicitly learns to maximize average accuracy, which rewards reliance on spurious correlations when they are present in the majority group. Group DRO reweights training examples to focus on the hardest group, forcing the model to learn core features that generalize across all groups.

## Experimental Evidence

- **Waterbirds:** ERM achieves 97.2% average accuracy but 72.6% worst-group accuracy. Group DRO achieves 93.5% average and 91.4% worst-group.
- **CelebA Hair Color:** ERM achieves 95.6% average but 47.2% worst-group (worse than random on minority group). DRO achieves 92.9% average and 88.9% worst-group.
- **Multi-NLI:** Spurious lexical correlations cause 67.9% worst-group accuracy for ERM vs 75.8% for DRO.

## Limitations

- Group labels required for DRO training (not always available in practice).
- Architectural comparison limited to ResNet variants — no analysis of how normalization layers, attention mechanisms, or skip connections affect worst-group performance.
- Temporal dynamics not studied (when do models learn spurious vs core features during training?).
- Optimization effects (learning rate, batch size) not systematically compared across architectures.

## Relevance to Gap

Provides worst-group accuracy as an evaluation metric but lacks systematic architectural comparison or temporal analysis of how different architectures learn spurious correlations over training.
