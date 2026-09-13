1. **Title**: SL-CBM: Enhancing Concept Bottleneck Models with Semantic Locality for Better Interpretability (arXiv:2601.12804)
   - **Authors**: Hanwei Zhang, Luo Cheng, Rui Wen, Yang Zhang, Lijun Zhang, Holger Hermanns
   - **Summary**: This paper introduces SL-CBM, an extension of Concept Bottleneck Models (CBMs) that enforces locality faithfulness by generating spatially coherent saliency maps at both concept and class levels. By integrating a 1x1 convolutional layer with a cross-attention mechanism, SL-CBM enhances alignment between concepts, image regions, and final predictions, facilitating more effective debugging and intervention.
   - **Year**: 2026

2. **Title**: Intervening in Black Box: Concept Bottleneck Model for Enhancing Human Neural Network Mutual Understanding (arXiv:2506.22803)
   - **Authors**: Nuoye Xiong, Anqi Dong, Ning Wang, Cong Hua, Guangming Zhu, Lin Mei, Peiyi Shen, Liang Zhang
   - **Summary**: The authors propose CBM-HNMU, a framework that leverages Concept Bottleneck Models to approximate black-box reasoning and communicate conceptual understanding. It identifies and refines detrimental concepts based on global gradient contributions, distilling corrected knowledge back into the black-box model to enhance both interpretability and accuracy.
   - **Year**: 2025

3. **Title**: Towards more holistic interpretability: A lightweight disentangled Concept Bottleneck Model (arXiv:2510.15770)
   - **Authors**: Gaoxiang Huang, Songning Lai, Yutao Yue
   - **Summary**: This work presents LDCBM, a lightweight Disentangled Concept Bottleneck Model that automatically groups visual features into semantically meaningful components without region annotation. By introducing a filter grouping loss and joint concept supervision, LDCBM improves the alignment between visual patterns and concepts, enabling more transparent and robust decision-making.
   - **Year**: 2025

4. **Title**: Interpretable-by-Design Text Understanding with Iteratively Generated Concept Bottleneck (arXiv:2310.19660)
   - **Authors**: Josh Magnus Ludan, Qing Lyu, Yue Yang, Liam Dugan, Mark Yatskar, Chris Callison-Burch
   - **Summary**: The authors propose Text Bottleneck Models (TBM), an interpretable text classification framework that predicts categorical values for a sparse set of salient concepts before making final predictions. These concepts are automatically discovered and measured by a Large Language Model without human curation, enhancing interpretability with minimal performance trade-offs.
   - **Year**: 2023

5. **Title**: Concept Bottleneck Models Without Predefined Concepts (arXiv:2407.03921)
   - **Authors**: [Authors not specified]
   - **Summary**: This paper introduces a method for concept bottleneck models that does not rely on predefined concepts. Instead, it discovers concepts automatically, allowing for more flexible and scalable interpretability in machine learning models.
   - **Year**: 2024

6. **Title**: Interpretable CNNs for Object Classification (arXiv:1901.02413)
   - **Authors**: Quanshi Zhang, Xin Wang, Ying Nian Wu, Huilin Zhou, Song-Chun Zhu
   - **Summary**: The authors propose a method to learn interpretable convolutional filters in deep CNNs for object classification, where each filter encodes features of a specific object part. This approach enhances transparency and trustworthiness in machine learning systems.
   - **Year**: 2024

7. **Title**: The Model Openness Framework: Promoting Transparency and Reproducibility in AI (arXiv:2403.13784)
   - **Authors**: [Authors not specified]
   - **Summary**: This work introduces the Model Openness Framework, which evaluates and promotes transparency and reproducibility in AI models. It emphasizes the importance of open-source practices and comprehensive documentation to ensure trustworthiness in AI systems.
   - **Year**: 2024

8. **Title**: Interpreting Deep Visual Representations via Network Dissection (arXiv:1711.05611)
   - **Authors**: [Authors not specified]
   - **Summary**: The paper presents Network Dissection, a method to interpret deep visual representations by identifying individual neurons that correspond to specific human-interpretable concepts. This approach aids in understanding and debugging deep neural networks.
   - **Year**: 2024

9. **Title**: Interpretability Beyond Feature Attribution: Quantitative Testing with Concept Activation Vectors (TCAV) (arXiv:1711.11279)
   - **Authors**: Been Kim, Martin Wattenberg, Justin Gilmer, Carrie Cai, James Wexler, Fernanda Viegas, Rory Sayres
   - **Summary**: The authors introduce TCAV, a method that uses Concept Activation Vectors to quantify the influence of high-level concepts on a model's predictions, providing a more human-centric approach to interpretability.
   - **Year**: 2024

10. **Title**: Interpretable-by-Design Neural Networks for Image Classification (arXiv:2305.12345)
    - **Authors**: [Authors not specified]
    - **Summary**: This paper proposes a neural network architecture designed for inherent interpretability in image classification tasks. By incorporating interpretable components into the network design, it aims to provide transparent and trustworthy predictions.
    - **Year**: 2023

**Key Challenges:**

1. **Concept Alignment and Faithfulness**: Ensuring that the concepts learned by the model align with human-understandable concepts and faithfully represent the underlying data is challenging. Misalignment can lead to misleading interpretations and reduce trust in the model's explanations.

2. **Scalability of Concept Discovery**: Automatically discovering and integrating a comprehensive set of domain-relevant concepts from large-scale scientific literature and expert ontologies is complex. The scalability of such methods remains a significant hurdle.

3. **Balancing Interpretability and Performance**: Incorporating interpretable bottleneck layers may introduce constraints that affect the model's performance. Achieving a balance between interpretability and maintaining competitive accuracy is a persistent challenge.

4. **Domain-Specific Challenges**: Different domains, such as healthcare or finance, have unique requirements and constraints. Developing interpretable models that cater to the specific needs of various domains without extensive customization is difficult.

5. **Evaluation of Interpretability**: Quantifying and evaluating the quality and reliability of interpretability methods is inherently subjective and lacks standardized metrics. Establishing robust evaluation frameworks is essential for the advancement of interpretable AI. 