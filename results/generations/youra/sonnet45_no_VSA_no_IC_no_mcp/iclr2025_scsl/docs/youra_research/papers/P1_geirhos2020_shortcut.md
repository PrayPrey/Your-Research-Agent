# Shortcut Learning in Deep Neural Networks

**Authors:** Geirhos et al.  
**Year:** 2020  
**arXiv ID:** 2004.07780  
**Citations:** ~800  

## Key Contribution

Comprehensive survey on spurious correlation mechanisms and detection methods. Introduces "shortcut learning" as a unifying framework for understanding how DNNs learn spurious correlations.

## Core Claims

1. **Simplicity Bias:** Neural networks trained with standard SGD exhibit an implicit bias toward learning simpler decision boundaries, which often correspond to spurious correlations rather than core features.

2. **Architecture-Specific Susceptibility:** Different architectures (CNNs, Transformers, ResNets) show varying degrees of susceptibility to shortcut learning, but systematic quantitative comparison is absent.

3. **Detection Methods:** Group-based evaluation metrics (e.g., worst-group accuracy) reveal shortcut learning better than average accuracy.

## Mechanism

Networks preferentially learn features with high correlation to labels during early training. Spurious features often provide simpler decision boundaries than core features, making them attractive to gradient descent. This creates a temporal ordering where spurious features are learned first.

## Experimental Evidence

- **Waterbirds Dataset:** CNNs achieve 97% average accuracy but only 72% worst-group accuracy, revealing reliance on background correlations.
- **CelebA Hair Color:** Models learn gender as a shortcut rather than hair color attributes.
- **Texture vs Shape:** CNNs preferentially learn texture cues over shape in ImageNet classification.

## Limitations

- No systematic architectural comparison across normalization layers, attention mechanisms, or skip connections.
- Temporal dynamics of shortcut learning not quantitatively characterized.
- Optimization hyperparameter effects (learning rate, batch size) studied separately from architectural factors.

## Relevance to Gap

Establishes that architectures differ in spurious susceptibility but lacks quantitative mapping of architectural properties to temporal learning dynamics.
