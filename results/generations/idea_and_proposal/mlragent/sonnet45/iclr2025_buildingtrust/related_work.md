Here is a literature review on the topic of "Adaptive Confidence Calibration for Trustworthy LLM Responses via Multi-Model Disagreement," focusing on papers published between 2023 and 2025:

**1. Related Papers**

1. **Title**: Uncertainty Quantification and Confidence Calibration in Large Language Models: A Survey (arXiv:2503.15850)
   - **Authors**: Xiaoou Liu, Tiejin Chen, Longchao Da, Chacha Chen, Zhen Lin, Hua Wei
   - **Summary**: This survey examines the challenges of uncertainty quantification (UQ) in LLMs, highlighting the disconnect between model confidence and actual accuracy. It introduces a taxonomy categorizing UQ methods based on computational efficiency and uncertainty dimensions, emphasizing the need for scalable and interpretable UQ approaches to enhance LLM reliability.
   - **Year**: 2025

2. **Title**: Calibrating Uncertainty Quantification of Multi-Modal LLMs using Grounding (arXiv:2505.03788)
   - **Authors**: Trilok Padhi, Ramneet Kaur, Adam D. Cobb, Manoj Acharya, Anirban Roy, Colin Samplawski, Brian Matejek, Alexander M. Berenbeim, Nathaniel D. Bastian, Susmit Jha
   - **Summary**: This paper proposes a novel approach for calibrating UQ in multi-modal LLMs by leveraging cross-modal consistency. By grounding textual responses to visual inputs and applying temperature scaling, the method improves calibration across tasks like medical and visual question answering.
   - **Year**: 2025

3. **Title**: Uncertainty Quantification of Large Language Models through Multi-Dimensional Responses (arXiv:2502.16820)
   - **Authors**: Tiejin Chen, Xiaoou Liu, Longchao Da, Jia Chen, Vagelis Papalexakis, Hua Wei
   - **Summary**: This work introduces a multi-dimensional UQ framework that integrates semantic and knowledge-aware similarity analysis. By generating multiple responses and leveraging auxiliary LLMs to extract implicit knowledge, it constructs similarity matrices and applies tensor decomposition to derive comprehensive uncertainty representations, enhancing LLM reliability.
   - **Year**: 2025

4. **Title**: Semantic Density: Uncertainty Quantification for Large Language Models through Confidence Measurement in Semantic Space (arXiv:2405.13845)
   - **Authors**: Xin Qiu, Risto Miikkulainen
   - **Summary**: This paper proposes a framework called Semantic Density, which extracts uncertainty information from a probability distribution perspective in semantic space. It addresses limitations of existing UQ methods by being task-agnostic and not requiring additional training, demonstrating superior performance and robustness across various LLMs and benchmarks.
   - **Year**: 2024

5. **Title**: MAQA: Evaluating Uncertainty Quantification in LLMs Regarding Data Uncertainty
   - **Authors**: Yongjin Yang, Haneul Yoo, Hwaran Lee
   - **Summary**: This study introduces the MAQA dataset to evaluate UQ methods in LLMs concerning data uncertainty. It assesses five UQ methods across various tasks, revealing that previous methods struggle under data uncertainty, though entropy- and consistency-based methods effectively estimate model uncertainty.
   - **Year**: 2025

6. **Title**: On the Calibration of Large Language Models and Alignment (arXiv:2311.13240)
   - **Authors**: Chiwei Zhu, Benfeng Xu, Quan Wang, Yongdong Zhang, Zhendong Mao
   - **Summary**: This paper systematically examines the calibration of aligned LLMs throughout their construction process, including pretraining and alignment training. It investigates how different training settings affect model calibration, evaluating models on generation, factuality, and understanding aspects.
   - **Year**: 2023

7. **Title**: A Survey on Uncertainty Quantification of Large Language Models: Taxonomy, Open Research Challenges, and Future Directions (arXiv:2412.05563)
   - **Authors**: Ola Shorinwa, Zhiting Mei, Justin Lidard, Allen Z. Ren, Anirudha Majumdar
   - **Summary**: This survey provides an extensive review of existing UQ methods for LLMs, presenting a taxonomy that categorizes methods into token-level, self-verbalized, semantic-similarity, and mechanistic interpretability. It highlights applications of UQ methods and identifies open research challenges.
   - **Year**: 2024

8. **Title**: Assessing Reliability in Language Models through Uncertainty Quantification
   - **Authors**: Artem Vazhentsev, Ekaterina Fadeeva, Rui Xing, Alexander Panchenko, Preslav Nakov, Timothy Baldwin, Maxim Panov, Artem Shelmanov
   - **Summary**: This study proposes a method for assessing the reliability of LLMs by quantifying uncertainty. It evaluates the approach across nine datasets and three LLMs, demonstrating its effectiveness in improving reliability and identifying uncertain predictions.
   - **Year**: 2024

9. **Title**: Uncertainty Quantification in Large Language Models through Convex Hull Analysis
   - **Authors**: [Authors not specified]
   - **Summary**: This research introduces a geometric approach to UQ in LLMs using convex hull analysis. By leveraging the spatial properties of response embeddings, it measures the dispersion and variability of model outputs, providing insights into prompt complexity, model settings, and uncertainty.
   - **Year**: 2024

10. **Title**: Self-ensemble: Mitigating Confidence Mis-calibration for Large Language Models
    - **Authors**: Zicheng Xu, Guanchu Wang, Guangyao Zheng, Yu-Neng Chuang, Alexander Szalay, Xia Hu, Vladimir Braverman
    - **Summary**: This paper addresses confidence distortion in LLMs on multi-choice question-answering tasks. The proposed Self-ensemble method splits choices into groups and ensembles LLM predictions across these groups, effectively mitigating under-confidence in correct predictions and over-confidence in incorrect ones.
    - **Year**: 2025

**2. Key Challenges**

1. **Epistemic Uncertainty in LLMs**: LLMs often produce confident yet incorrect responses due to a lack of understanding of their own knowledge boundaries, leading to misleading outputs.

2. **Scalability of Uncertainty Quantification Methods**: Traditional UQ methods may not scale effectively with the complexity and size of LLMs, posing challenges in computational efficiency and applicability.

3. **Integration of Multi-Modal Data**: Calibrating confidence across different modalities (e.g., text and images) requires sophisticated methods to ensure consistency and reliability in multi-modal LLMs.

4. **Interpretability of Confidence Scores**: Providing users with interpretable and actionable confidence metrics is essential for trust, yet remains a significant challenge in LLM deployment.

5. **Adaptability to Diverse Applications**: Ensuring that confidence calibration methods are adaptable to various domains and applications, especially in high-stakes fields like healthcare and law, is crucial for the trustworthy deployment of LLMs. 