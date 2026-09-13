## Related Work

**Related Papers**
1. **Title**: A Unified Causal View of Domain Invariant Representation Learning
   - **Authors**: Zihao Wang, Victor Veitch
   - **Summary**: Characterizes causal structures compatible with invariance and establishes the theoretical foundation for understanding the connection between causality and invariant representation learning.
   - **Year**: 2022

2. **Title**: The Risks of Invariant Risk Minimization
   - **Authors**: Elan Rosenfeld, Pradeep Ravikumar, Andrej Risteski
   - **Summary**: Demonstrates that IRM fails catastrophically unless test data is similar to training data, motivating the need for interpretable causal identification approaches.
   - **Year**: 2020

3. **Title**: In Search of Lost Domain Generalization
   - **Authors**: Ishaan Gulrajani, David Lopez-Paz
   - **Summary**: Shows that ERM achieves state-of-the-art performance when carefully implemented and establishes the DomainBed benchmark for domain generalization evaluation.
   - **Year**: 2020

4. **Title**: Invariant Risk Minimization
   - **Authors**: Arjovsky et al.
   - **Summary**: Proposes a gradient-based invariance penalty approach for domain generalization, achieving performance comparable to ERM on DomainBed benchmarks.
   - **Year**: 2019

5. **Title**: Lost Domain Generalization Is a Natural Consequence of Lack of Training Domains
   - **Authors**: Yimu Wang, Yihan Wu, Hongyang Zhang
   - **Summary**: Establishes that domain generalization requires polynomially many (poly(1/ε)) training domains, providing theoretical explanation for why existing methods fail.
   - **Year**: 2024

6. **Title**: Back-to-Bones: Role of Backbones in Domain Generalization
   - **Authors**: Angarano et al.
   - **Summary**: Demonstrates that domain generalization algorithms do not outperform ERM when using modern backbones, suggesting that architecture choice matters more than algorithmic innovations.
   - **Year**: 2024

7. **Title**: Unbiased Semantic Representation Learning Based on Causal Disentanglement
   - **Authors**: Jin et al.
   - **Summary**: Proposes causal disentanglement for domain generalization, validating the importance of separating causal features from spurious correlations.
   - **Year**: 2024

**Key Challenges**
1. **Catastrophic Failure of Invariance Methods**: IRM and related invariance-based approaches fail when test distributions differ substantially from training distributions, limiting their practical applicability.

2. **Insufficient Training Domains**: Domain generalization theoretically requires a polynomial number of training domains, which explains the persistent failure of existing methods that operate with limited domain diversity.

3. **Architecture Dominance Over Algorithms**: Modern backbone architectures contribute more to domain generalization performance than specialized DG algorithms, questioning the value of algorithmic innovations in this space.

4. **Lack of Interpretable Causal Identification**: Current methods lack mechanisms for interpretable identification of causal versus spurious features, hindering understanding and debugging of model behavior.

5. **ERM Competitiveness**: Carefully implemented ERM remains competitive with or superior to specialized domain generalization methods, suggesting that proposed algorithmic advances may not provide meaningful improvements.
