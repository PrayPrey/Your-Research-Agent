# Title
**Permutation-Invariant Weight Fingerprinting for Neural Network Provenance and Integrity Verification**

# Motivation
With over a million models on platforms like Hugging Face, verifying model provenance, detecting unauthorized modifications, and identifying backdoored models are critical challenges. Traditional weight-based analysis fails due to weight space symmetries—particularly permutation invariance—where functionally identical networks have vastly different weight representations. This research addresses the urgent need for robust model fingerprinting that respects weight space geometry while enabling trustworthy model sharing and deployment.

# Main Idea
We propose learning permutation-equivariant embeddings that map neural network weights to canonical fingerprints invariant to symmetry transformations. The methodology involves:

1. **Architecture**: Develop a Graph Neural Network (GNN) backbone that processes weights as node/edge features, naturally handling permutation symmetries through message-passing operations.

2. **Contrastive Learning Framework**: Train the fingerprinting system using triplet losses where positive pairs are symmetry-transformed versions of the same model, and negatives are different models or maliciously modified variants.

3. **Applications**: 
   - **Provenance tracking**: Identify model lineage and detect unauthorized derivatives
   - **Integrity verification**: Detect weight-space backdoors and adversarial modifications
   - **Duplicate detection**: Efficiently identify functionally equivalent models in large repositories

**Expected Outcomes**: A scalable, geometry-aware fingerprinting system achieving >95% accuracy in model identification while being robust to benign transformations, enabling trustworthy model ecosystems and intellectual property protection.