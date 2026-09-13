## Related Work

**Related Papers**
1. **Title**: Multiscale Deep Equilibrium Models (2020)
   - **Authors**: Bai, Koltun, Kolter
   - **Summary**: Introduces implicit networks with O(1) memory that achieve competitive ImageNet performance through fixed-point iteration, establishing DEQ architecture with multi-scale feature hierarchy.
   - **Year**: 2020

2. **Title**: TorchDEQ: A Library for Deep Equilibrium Models (2023)
   - **Authors**: Geng, Kolter
   - **Summary**: Provides best practices for DEQ training and introduces Anderson acceleration techniques for improved convergence in deep equilibrium models.
   - **Year**: 2023

3. **Title**: Training End-to-End Analog Neural Networks with Equilibrium Propagation (arXiv:2006.01981)
   - **Authors**: Kendall, Pantone, Manickavasagam, Bengio, Scellier
   - **Summary**: Provides mathematical proof that analog resistive networks are energy-based models that can be trained with equilibrium propagation, validating EP on analog hardware.
   - **Year**: 2020

4. **Title**: Scaling Equilibrium Propagation to Deep ConvNets (DOI: 10.3389/fnins.2021.633674)
   - **Authors**: Laborieux, Ernoult, Scellier, Bengio, Grollier, Querlioz
   - **Summary**: Demonstrates EP gradient bias reduction techniques that enable training of deep convolutional networks, establishing EP scalability and gradient quality.
   - **Year**: 2021

5. **Title**: Learning at the Speed of Physics: Equilibrium Propagation on Oscillator Ising Machines (arXiv:2510.12934)
   - **Authors**: Gower
   - **Summary**: Demonstrates OIM combined with EP achieving 97.2% MNIST accuracy with robustness under 10x noise variance, establishing core feasibility of oscillator EP training.
   - **Year**: 2025

6. **Title**: Training Spiking Neural Networks Using Lessons From Deep Learning (2021)
   - **Authors**: Eshraghian et al.
   - **Summary**: Shows that surrogate gradients enable SNN training and introduces the snnTorch framework as an alternative neuromorphic computing approach.
   - **Year**: 2021

7. **Title**: Training Coupled Phase Oscillators as Neuromorphic Platform using EP (arXiv:2402.08579)
   - **Authors**: Wang, Wanjura, Marquardt
   - **Summary**: Demonstrates Kuramoto oscillators trained with equilibrium propagation for classification tasks, representing prior oscillator EP work with simpler architecture than DEQ mapping.
   - **Year**: 2024

8. **Title**: EqSpike: Spike-driven Equilibrium Propagation for Neuromorphic Implementations (DOI: 10.1016/j.isci.2021.102222)
   - **Authors**: Martin, Ernoult, Laydevant, Li, Querlioz, Petrisor, Grollier
   - **Summary**: Presents the first spike-driven EP implementation, validating equilibrium propagation on neuromorphic substrates using spiking neural networks.
   - **Year**: 2021

9. **Title**: Physical Reservoir Computing with Emerging Electronics (2024)
   - **Authors**: Liang, Tang, Zhong et al.
   - **Summary**: Comprehensive survey of over 200 physical reservoir computing works, documenting the current frontier of analog computing approaches.
   - **Year**: 2024

**Key Challenges**
1. **Lack of DEQ-Specific Hardware Mapping**: While physical reservoir computing has been extensively surveyed, no existing work provides a specific mapping of deep equilibrium models to analog hardware substrates.
2. **Gap Between EP Substrates and DEQ Architectures**: Prior work validates EP on spike-driven neuromorphic implementations but does not extend to DEQ implicit layers, leaving the connection between EP and modern implicit networks unexplored.
3. **Oscillator EP Simplicity**: Existing oscillator-based EP approaches use simpler architectures (e.g., Kuramoto oscillators) that do not capture the full complexity of DEQ multi-scale feature hierarchies.
4. **Bridging Digital DEQ Methods to Analog Implementation**: While digital DEQ training methodologies and best practices exist, translating these to analog neuromorphic platforms remains unaddressed.
