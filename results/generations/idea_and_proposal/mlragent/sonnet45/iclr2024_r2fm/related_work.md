1. **Title**: CIP: A Plug-and-Play Causal Prompting Framework for Mitigating Hallucinations under Long-Context Noise (arXiv:2512.11282)
   - **Authors**: Qingsen Ma, Dianyun Wang, Ran Jing, Yujun Sun, Zhenbo Xu
   - **Summary**: This paper introduces CIP, a lightweight causal prompting framework designed to reduce hallucinations in large language models (LLMs) when processing lengthy and noisy contexts. By constructing causal relation sequences among entities, actions, and events, and integrating them into prompts, CIP guides reasoning towards causally relevant evidence. The framework employs causal intervention and counterfactual reasoning to suppress non-causal reasoning paths, thereby enhancing factual grounding and interpretability. Experiments across seven mainstream LLMs demonstrate that CIP consistently improves reasoning quality and reliability, achieving notable gains in attributable rate, causal consistency score, and effective information density.
   - **Year**: 2025

2. **Title**: Distributional Semantics Tracing: A Framework for Explaining Hallucinations in Large Language Models (arXiv:2510.06107)
   - **Authors**: Gagan Bhatia, Somayajulu G Sripada, Kevin Allan, Jacobo Azcona
   - **Summary**: The authors propose Distributional Semantics Tracing (DST), a unified framework that integrates interpretability techniques to produce a causal map of a model's reasoning, treating meaning as a function of context. DST identifies a specific "commitment layer" where a model's internal representations irreversibly diverge from factuality, leading to hallucinations. The study reveals a conflict between distinct computational pathways, interpreted through dual-process theory, resulting in predictable failure modes such as "Reasoning Shortcut Hijacks." The framework quantifies the coherence of the contextual pathway, showing a strong negative correlation with hallucination rates, providing a mechanistic account of how, when, and why hallucinations occur within the Transformer architecture.
   - **Year**: 2025

3. **Title**: CausalGuard: A Smart System for Detecting and Preventing False Information in Large Language Models (arXiv:2511.11600)
   - **Authors**: Piyushkumar Patel
   - **Summary**: CausalGuard is introduced as a novel approach combining causal reasoning with symbolic logic to detect and prevent hallucinations in LLMs. Unlike existing methods that check outputs post-generation, CausalGuard understands the causal chain leading to false statements and intervenes early in the process. It operates through two complementary paths: tracing causal relationships between the model's knowledge and its outputs, and checking logical consistency using automated reasoning. Testing across twelve benchmarks, CausalGuard identifies hallucinations with high accuracy and significantly reduces false claims while maintaining natural and helpful responses. The system is particularly effective in complex reasoning tasks, making it suitable for sensitive areas like medical diagnosis or financial analysis.
   - **Year**: 2025

4. **Title**: Large Language Models Do NOT Really Know What They Don't Know (arXiv:2510.09033)
   - **Authors**: Chi Seng Cheang, Hou Pong Chan, Wenxuan Zhang, Yang Deng
   - **Summary**: This study challenges the notion that LLMs can reliably distinguish between factual and hallucinated outputs based on their internal representations. The authors conduct a mechanistic analysis, comparing two types of hallucinations based on their reliance on subject information. They find that when hallucinations are associated with subject knowledge, LLMs employ the same internal recall process as for correct responses, leading to indistinguishable hidden-state geometries. In contrast, hallucinations detached from subject knowledge produce distinct representations, making them detectable. These findings reveal a fundamental limitation: LLMs do not encode truthfulness in their internal states but only patterns of knowledge recall, demonstrating that they don't truly know what they don't know.
   - **Year**: 2025

5. **Title**: Mental-LLM: Leveraging Large Language Models for Mental Health Prediction via Online Text Data (arXiv:2307.14385)
   - **Authors**: Xuhai Xu, Bingsheng Yao, Yuanzhe Dong, Saadia Gabriel, Hong Yu, James Hendler, Marzyeh Ghassemi, Anind K. Dey, Dakuo Wang
   - **Summary**: This paper presents a comprehensive evaluation of multiple LLMs on various mental health prediction tasks using online text data. The authors conduct experiments covering zero-shot prompting, few-shot prompting, and instruction fine-tuning. Results indicate that instruction fine-tuning significantly boosts the performance of LLMs across all tasks. The best fine-tuned models, Mental-Alpaca and Mental-FLAN-T5, outperform larger models like GPT-3.5 and GPT-4 in balanced accuracy. The study also explores LLMs' capability in mental health reasoning tasks, highlighting promising capabilities and emphasizing important ethical risks and limitations before achieving deployability in real-world mental health settings.
   - **Year**: 2024

6. **Title**: CodeMirage: Hallucinations in Code Generated by Large Language Models (arXiv:2408.08333)
   - **Authors**: [Authors not specified in the provided information]
   - **Summary**: This paper investigates the phenomenon of hallucinations in code generated by LLMs. The authors analyze instances where models produce plausible but incorrect code snippets, leading to potential reliability issues in software development. The study examines the underlying causes of these hallucinations and proposes methods to detect and mitigate them, aiming to improve the trustworthiness of code generated by LLMs.
   - **Year**: 2024

7. **Title**: HalluciBot: Is There No Such Thing as a Bad Question? (arXiv:2404.12535)
   - **Authors**: William Watson, Nicole Cho
   - **Summary**: HalluciBot is introduced as a model that predicts the probability of hallucination before generation for any query posed to an LLM. Unlike traditional methods that analyze outputs post-generation, HalluciBot estimates hallucination likelihood preemptively, allowing users to revise or cancel queries before generation. The model employs a Multi-Agent Monte Carlo Simulation using a Query Perturbator to generate variations per query during training. HalluciBot predicts both binary and multi-class probabilities of hallucination, providing insights into a query's quality and enabling proactive measures to reduce computational waste and improve user accountability.
   - **Year**: 2024

**Key Challenges:**

1. **Identifying Causal Mechanisms**: Determining the specific neural components and pathways responsible for hallucinations in LLMs remains complex, requiring advanced interpretability techniques and causal analysis.

2. **Distinguishing Between Factual and Hallucinated Outputs**: LLMs often generate outputs that are plausible yet incorrect, making it challenging to differentiate between accurate information and hallucinations based solely on internal representations.

3. **Developing Effective Mitigation Strategies**: Creating interventions that reduce hallucinations without compromising the generative capabilities and efficiency of LLMs is a significant challenge.

4. **Ensuring Generalizability Across Models and Tasks**: Techniques developed to understand and mitigate hallucinations must be applicable across various LLM architectures and tasks to be broadly useful.

5. **Addressing Ethical and Practical Implications**: Implementing solutions to hallucinations involves ethical considerations, especially in high-stakes domains like healthcare and finance, where incorrect information can have serious consequences. 