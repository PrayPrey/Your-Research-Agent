## Related Work

**Related Papers**
1. **Title**: Understanding Black-box Predictions via Influence Functions (arXiv:1703.04730)
   - **Authors**: Pang Wei Koh, Percy Liang
   - **Summary**: Introduces influence functions to trace model predictions back to training data, providing the theoretical basis for self-influence analysis in understanding how individual training examples affect model behavior.
   - **Year**: 2017

2. **Title**: Data pruning and neural scaling laws: fundamental limitations of score-based algorithms
   - **Authors**: Fadhel Ayed, Soufiane Hayou
   - **Summary**: Establishes "No Free Lunch" theorems for data pruning, demonstrating fundamental limitations of score-based algorithms and justifying the need for hybrid approaches in data selection.
   - **Year**: 2023

3. **Title**: Optimal experimental design: Formulations and computations
   - **Authors**: Xun Huan, Jayanth Jagalur, Youssef Marzouk
   - **Summary**: Presents a Bayesian decision-theoretic framework for data acquisition, providing theoretical foundations for adaptive threshold methods in experimental design.
   - **Year**: 2024

4. **Title**: The RefinedWeb Dataset for Falcon LLM
   - **Authors**: Guilherme Penedo et al.
   - **Summary**: Introduces perplexity-based filtering as a heuristic approach for dataset curation, serving as a baseline method for data selection in large language model training.
   - **Year**: 2023

5. **Title**: DataComp: In search of the next generation of multimodal datasets
   - **Authors**: Samir Gadre et al.
   - **Summary**: Establishes a standardized benchmark for evaluating data selection methods, enabling systematic comparison of different dataset curation approaches.
   - **Year**: 2023

6. **Title**: DataInf: Efficiently Estimating Data Influence in LoRA-tuned LLMs
   - **Authors**: Kwon et al.
   - **Summary**: Develops scalable methods for estimating data influence in LoRA-tuned large language models, demonstrating efficient influence computation techniques.
   - **Year**: 2024

7. **Title**: CLIPLoss and Norm-Based Data Selection Methods
   - **Authors**: Wang et al.
   - **Summary**: Demonstrates that hybrid metrics combining multiple signals improve data selection quality, validating the paradigm of multi-signal approaches while using different selection signals.
   - **Year**: 2024

**Key Challenges**
1. **Scalability of Influence Estimation**: Existing scalable influence estimation methods (e.g., DataInf) have been developed for fine-tuning scenarios but have not been applied to pre-training data selection at scale.

2. **Fundamental Limitations of Score-Based Methods**: "No Free Lunch" theorems demonstrate that single-score data pruning algorithms have inherent limitations, necessitating hybrid approaches that combine multiple selection criteria.

3. **Gap Between Heuristic and Principled Methods**: Current practical approaches like perplexity-based filtering rely on heuristics, while more principled influence-based methods lack the scalability needed for large-scale pre-training data curation.

4. **Signal Integration**: While hybrid metrics have shown promise in improving selection quality, optimal methods for combining different selection signals (influence-based vs. norm-based vs. loss-based) remain underexplored.
