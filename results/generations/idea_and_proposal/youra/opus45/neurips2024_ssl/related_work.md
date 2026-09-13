## Related Work

**Related Papers**
1. **Title**: Predicting What You Already Know Helps: Provable Self-Supervised Learning (arXiv:2008.01064)
   - **Authors**: Lee, Lei, Saunshi, Zhuo
   - **Summary**: Proves that pretext tasks reduce downstream sample complexity via conditional independence, establishing that task properties directly affect representation utility.
   - **Year**: 2020

2. **Title**: A Theoretical Study of Inductive Biases in Contrastive Learning (arXiv:2211.14699)
   - **Authors**: HaoChen, Ma
   - **Summary**: Demonstrates that model capacity limits recoverable clustering structures, directly supporting the concept of capacity-difficulty matching in self-supervised learning.
   - **Year**: 2022

3. **Title**: To Compress or Not to Compress—Self-Supervised Learning and Information Theory: A Review (arXiv:2304.09355)
   - **Authors**: Shwartz-Ziv, LeCun
   - **Summary**: Provides a unified information-theoretic framework for SSL, characterizing all methods as instances of a compression-relevance tradeoff.
   - **Year**: 2023

4. **Title**: RankMe: Assessing the Downstream Performance of Pretrained Self-Supervised Representations by Their Rank (ICML 2023)
   - **Authors**: Garrido, Balestriero, Najman, LeCun
   - **Summary**: Demonstrates that effective rank predicts downstream SSL performance without labels, validating eRank as a quality measure with R² > 0.8.
   - **Year**: 2023

5. **Title**: A Developmental Approach to Machine Learning? (Frontiers in Psychology)
   - **Authors**: Smith, Slone
   - **Summary**: Shows that developmental psychology principles, including the Zone of Proximal Development, apply to machine learning, validating cross-domain transfer of developmental concepts.
   - **Year**: 2017

6. **Title**: Curriculum Learning
   - **Authors**: Bengio et al.
   - **Summary**: Introduces example-level difficulty ordering for training neural networks, organizing training data from easy to hard examples.
   - **Year**: 2009

7. **Title**: Self-Paced Learning
   - **Authors**: Kumar et al.
   - **Summary**: Proposes adaptive example weighting during training, allowing models to self-regulate the difficulty of examples they learn from.
   - **Year**: 2010

**Key Challenges**
1. **Theory-Practice Gap in SSL**: Active research interest exists in bridging the gap between theoretical understanding and practical application of self-supervised learning methods.

2. **Principled Auxiliary Task Design Guidelines**: Critical unaddressed need for systematic, principled approaches to designing auxiliary tasks in SSL, rather than relying on heuristics or trial-and-error.

3. **Task-Level vs. Example-Level Design**: Existing curriculum and self-paced learning approaches focus on example-level difficulty ordering, leaving task-level design principles underexplored.

4. **Predictive vs. Adaptive Approaches**: Current methods like self-paced learning are adaptive (adjusting during training), but there is a gap in predictive approaches that can guide task design before training begins.
