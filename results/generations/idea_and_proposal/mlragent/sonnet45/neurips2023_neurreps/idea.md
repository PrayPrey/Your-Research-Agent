# Title
Equivariant Graph Neural Networks for Decoding Neural Population Dynamics in Motor Cortex

# Motivation
Motor cortex exhibits low-dimensional manifold structure during movement, yet current neural decoding methods fail to leverage the inherent geometric and group-theoretic structure of motor actions (rotations, translations, reflections). This limits decoding accuracy and generalization across contexts. By incorporating equivariance principles from geometric deep learning into neural population analysis, we can develop decoders that respect the symmetries of motor control, improving brain-machine interface performance and revealing computational principles of motor representations.

# Main Idea
We propose a novel framework combining equivariant graph neural networks (GNNs) with topological data analysis for motor cortex decoding. First, construct a functional connectivity graph from neural populations where nodes represent neurons and edges encode pairwise interactions. Second, design SE(3)-equivariant GNN layers that preserve rotational and translational symmetries inherent to reaching movements. Third, integrate persistent homology to capture topological features of neural manifolds across different movement phases.

**Expected outcomes:** (1) Improved decoding accuracy by 20-30% over standard methods; (2) Better generalization to novel movement directions through symmetry preservation; (3) Interpretable geometric features revealing how motor cortex factorizes movement parameters.

**Impact:** This bridges geometric deep learning and neuroscience, providing both practical BMI improvements and theoretical insights into how biological circuits implement equivariant computations, potentially revealing universal principles of neural information processing.