## Related Work

**Related Papers**
1. **Title**: Scaling Laws for Data Filtering—Data Curation Cannot be Compute Agnostic (arXiv:2404.07177)
   - **Authors**: Goyal, Maini, Lipton, Raghunathan, Kolter
   - **Summary**: Demonstrates that the optimal filtering threshold depends on training compute and that well-curated data loses utility when repeated.
   - **Year**: 2024

2. **Title**: Beyond neural scaling laws: beating power law scaling via data pruning (arXiv:2206.14486)
   - **Authors**: Sorscher, Geirhos, Shekhar, Ganguli, Morcos
   - **Summary**: Shows that good data pruning metrics can achieve exponential rather than power-law scaling in model performance.
   - **Year**: 2022

3. **Title**: DataComp: In search of the next generation of multimodal datasets (arXiv:2304.14108)
   - **Authors**: Gadre et al.
   - **Summary**: Introduces a benchmark for dataset filtering that enables systematic evaluation of curation methods.
   - **Year**: 2023

4. **Title**: Scaling Laws for Neural Language Models
   - **Authors**: Kaplan et al.
   - **Summary**: Establishes foundational scaling laws that predict model performance from data quantity.
   - **Year**: 2020

5. **Title**: FLYT - Filter Like You Test
   - **Authors**: Shechter & Carmon
   - **Summary**: Proposes gradient-based filtering for data curation, offering higher accuracy but at greater computational cost compared to proxy-based methods.
   - **Year**: 2025

6. **Title**: LAION-5B Fixed Threshold
   - **Authors**: Not specified
   - **Summary**: Employs a static CLIP score threshold of 0.3 for filtering multimodal data.
   - **Year**: Not specified

7. **Title**: EcoVal
   - **Authors**: Not specified
   - **Summary**: Demonstrates that cluster-based data valuation is both feasible and efficient for large-scale datasets.
   - **Year**: 2024

8. **Title**: CHG Shapley
   - **Authors**: Not specified
   - **Summary**: Achieves O(1) data valuation by using a compound of hardness and gradient information.
   - **Year**: 2025

**Key Challenges**
1. **Compute-Dependent Filtering Thresholds**: Optimal data filtering thresholds vary with available training compute, making static thresholds suboptimal across different training regimes.
2. **Data Repetition Degradation**: Well-curated data loses its utility when repeated during training, limiting the benefits of aggressive filtering.
3. **Scalability vs. Accuracy Trade-off**: Gradient-based filtering methods offer higher accuracy but are computationally expensive, while proxy-based methods are faster but potentially less precise.
4. **Static vs. Adaptive Thresholding**: Fixed threshold approaches (e.g., LAION-5B's CLIP score of 0.3) fail to adapt to dataset characteristics and training conditions.
