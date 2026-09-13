## Related Work

**Related Papers**
1. **Title**: Identifiability Guarantees for Causal Disentanglement from Soft Interventions (arXiv/Semantic Scholar ID: ce7fc001e17d5a062d1ea062e29b899c03d61727)
   - **Authors**: Zhang, Squires, Greenewald, Srivastava, Shanmugam, Uhler
   - **Summary**: Demonstrates that soft interventions enable identifiability up to equivalence class and provides a theoretical framework for causal disentanglement that CMCA-IRL extends.
   - **Year**: 2023

2. **Title**: Multi-View Causal Representation Learning with Partial Observability (Semantic Scholar ID: 31bcf6a4f8382d442df6223a1f0c1023e1771023)
   - **Authors**: Yao, Xu, Lachapelle, Magliacane, Taslakian, Martius, von Kügelgen, Locatello
   - **Summary**: Shows that partial observability combined with identifiability algebra enables fine-grained causal representation learning; serves as a key comparison baseline.
   - **Year**: 2023

3. **Title**: Identifiability Results for Multimodal Contrastive Learning (ICLR 2023)
   - **Authors**: Daunhawer, Bizeul, Palumbo, Marx, Vogt
   - **Summary**: Establishes that contrastive learning can block-identify shared factors between heterogeneous modalities, validating core block-identifiability claims.
   - **Year**: 2023

4. **Title**: The Incomplete Rosetta Stone problem: Multi-view Nonlinear ICA
   - **Authors**: Gresele et al.
   - **Summary**: Addresses multi-view identifiability under the assumption of the same latent source; CMCA-IRL extends this work to handle complementary modalities.
   - **Year**: 2019

5. **Title**: Unifying Causal Representation Learning with the Invariance Principle (Semantic Scholar ID: efc9f440aeff)
   - **Authors**: Yao et al.
   - **Summary**: Demonstrates that invariance principles, rather than strictly causal assumptions, can suffice for identifiability, supporting relaxed theoretical assumptions.
   - **Year**: 2024

6. **Title**: Causal Representation Learning from Multi-modal Biomedical Observations (Semantic Scholar ID: 5eee133bac6e70c8d9b2b78b50e6124531000a70)
   - **Authors**: Sun et al.
   - **Summary**: Employs structural sparsity for multi-modal causal representation learning, validating that a gap exists in current approaches while taking a different methodological direction.
   - **Year**: 2024

**Key Challenges**
1. **Same Latent Source Assumption**: Existing multi-view approaches assume identical latent sources across views, limiting applicability to complementary modalities with distinct but related latent factors.
2. **Heterogeneous Modality Integration**: Current methods struggle to achieve block-identifiability of shared factors when dealing with fundamentally different data modalities.
3. **Partial Observability**: Handling scenarios where not all latent factors are observable across all modalities remains a significant theoretical and practical challenge.
4. **Strict Causal Assumptions**: Many existing frameworks require strong causal assumptions that may be unnecessarily restrictive when invariance-based approaches could suffice.
5. **Structural Sparsity Requirements**: Alternative approaches rely on structural sparsity constraints, indicating the need for methods that can handle multi-modal causal representation learning under different assumptions.
