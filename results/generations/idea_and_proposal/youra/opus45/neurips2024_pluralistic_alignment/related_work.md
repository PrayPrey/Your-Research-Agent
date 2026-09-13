## Related Work

**Related Papers**
1. **Title**: A Roadmap to Pluralistic Alignment (arXiv/Semantic Scholar: bf40c8f88875f7c591dddc0936542918f4083b22)
   - **Authors**: Taylor Sorensen, Jared Moore, Jillian Fisher et al.
   - **Summary**: Defines three forms of pluralism (Overton, Steerable, and Distributional) and argues that standard alignment approaches reduce distributional pluralism.
   - **Year**: 2024

2. **Title**: Direct Preference Optimization with Unobserved Preference Heterogeneity
   - **Authors**: Keertana Chidambaram, Karthik Seetharaman, Vasilis Syrgkanis
   - **Summary**: Proposes EM-DPO to discover latent annotator types and demonstrates that binary comparisons are insufficient for identifying latent preferences.
   - **Year**: 2024

3. **Title**: Policy Aggregation
   - **Authors**: P. A. Alamdari, Soroush Ebadian, Ariel Procaccia
   - **Summary**: Demonstrates that social choice methods such as Borda and Condorcet voting are applicable to reinforcement learning policy aggregation.
   - **Year**: 2024

4. **Title**: Categorical Reparameterization with Gumbel-Softmax
   - **Authors**: Jang et al.
   - **Summary**: Introduces a continuous relaxation technique that enables differentiable sampling from categorical distributions.
   - **Year**: 2016

5. **Title**: VPL (Variational Preference Learning)
   - **Authors**: Poddar et al.
   - **Summary**: Proposes a user-centric variational approach to preference learning for alignment.
   - **Year**: 2024

6. **Title**: MODPO (Multi-Objective DPO)
   - **Authors**: Zhou et al.
   - **Summary**: Extends DPO to handle multiple objectives but requires explicit multi-objective labels rather than automatic discovery.
   - **Year**: 2023

7. **Title**: I beg to differ: Disagreement in Legal ML
   - **Authors**: Braun
   - **Summary**: Analyzes legal ML datasets and shows that all examined datasets remove traces of annotator disagreement.
   - **Year**: 2023

8. **Title**: AI Alignment and Social Choice: Fundamental Limitations
   - **Authors**: Mishra
   - **Summary**: Demonstrates that Arrow's impossibility theorem applies to RLHF, highlighting fundamental limitations in aggregating diverse preferences.
   - **Year**: 2023

**Key Challenges**
1. **Loss of Distributional Pluralism**: Standard alignment approaches reduce distributional pluralism by collapsing diverse value systems into a single aggregated preference model.

2. **Insufficient Binary Comparisons**: Binary preference comparisons are insufficient for identifying latent preference heterogeneity among annotators, limiting the ability to discover distinct value clusters.

3. **Disagreement Erasure**: Current ML datasets systematically remove traces of annotator disagreement, preventing models from learning to represent and preserve diverse viewpoints.

4. **Social Choice Impossibilities**: Arrow's impossibility theorem applies to RLHF, meaning no perfect aggregation method exists, which motivates the need for explicit and transparent voting rules.

5. **Manual Objective Specification**: Existing multi-objective approaches require explicit labels for different objectives rather than automatically discovering latent value clusters from preference data.

6. **User vs. Value-System Focus**: Current variational approaches focus on user-centric modeling rather than value-system-centric representations, potentially missing broader ideological or cultural preference patterns.
