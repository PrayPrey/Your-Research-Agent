## Related Work

**Related Papers**
1. **Title**: Learning Latent Permutations with Gumbel-Sinkhorn Networks (arXiv:1802.08665)
   - **Authors**: Mena, Belanger, Linderman, Snoek
   - **Summary**: Introduces the Sinkhorn operator as a continuous relaxation of permutations and extends it to matchings via Gumbel-Sinkhorn, providing a core mathematical foundation for differentiable permutation learning.
   - **Year**: 2018

2. **Title**: Categorical Reparameterization with Gumbel-Softmax (arXiv:1611.01144)
   - **Authors**: Jang, Gu, Poole
   - **Summary**: Proposes differentiable categorical sampling through temperature-controlled relaxation, enabling gradient-based optimization for discrete categorical selection.
   - **Year**: 2016

3. **Title**: Differentiable Sorting Networks for Scalable Sorting and Ranking Supervision (arXiv:2105.04019)
   - **Authors**: Petersen, Borgelt, Kuehne, Deussen
   - **Summary**: Develops relaxed pairwise swap operations that enable stable gradient-based training for sorting operations scaling up to 1024 elements.
   - **Year**: 2021

4. **Title**: A Unified Differentiable Boolean Operator with Fuzzy Logic (arXiv:2407.10954)
   - **Authors**: Liu et al.
   - **Summary**: Unifies Boolean operations through operation-type differentiation using fuzzy logic, validating the concept of learnable operation types.
   - **Year**: 2024

5. **Title**: DSelect-k: Differentiable Selection in Mixture of Experts
   - **Authors**: Hazimeh et al.
   - **Summary**: Introduces binary encoding for differentiable top-k selection in mixture of experts architectures.
   - **Year**: 2021

6. **Title**: torchsort
   - **Authors**: Not specified
   - **Summary**: Provides fast O(n log n) differentiable sorting implementation via isotonic regression.
   - **Year**: Not specified

7. **Title**: fast-soft-sort
   - **Authors**: Not specified
   - **Summary**: Implements differentiable sorting operations presented at ICML 2020.
   - **Year**: 2020

8. **Title**: Permutation Learning with Only N Parameters (arXiv:2503.13051)
   - **Authors**: Barthel et al.
   - **Summary**: Reduces the parameter complexity of Sinkhorn-based permutation learning from O(N²) to O(N), addressing scalability limitations.
   - **Year**: 2025

**Key Challenges**
1. **Incompatible Mathematical Frameworks**: Each discrete operation (sorting, selection, permutation) relies on different mathematical foundations, making it difficult to combine them within a single differentiable system.
2. **Lack of Unified Approach**: No existing method provides a unified framework that can handle multiple discrete operations through a common differentiable mechanism.
3. **Scalability of Permutation Learning**: Traditional Sinkhorn-based approaches require O(N²) parameters, limiting their applicability to large-scale problems.
4. **Operation-Type Differentiation**: Learning which discrete operation to apply in an end-to-end manner remains challenging, with only recent work beginning to address learnable operation selection.
