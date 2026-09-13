## Related Work

**Related Papers**
1. **Title**: Code-Switching Red-Teaming: LLM Evaluation for Safety and Multilingual Understanding (2024)
   - **Authors**: Yoo, Yang, Lee
   - **Summary**: Introduces the CSRT framework and benchmark demonstrating that code-switching achieves 46.7% more successful attacks than standard English prompts, establishing code-switching as a significant safety vulnerability in LLMs.
   - **Year**: 2024

2. **Title**: The Language Barrier: Dissecting Safety Challenges of LLMs in Multilingual Contexts (2024)
   - **Authors**: Shen, Tan, Chen, et al.
   - **Summary**: Identifies that the cross-lingual alignment bottleneck originates in pretraining and demonstrates that low-resource language safety training yields minimal improvement, suggesting the need for representation-level changes.
   - **Year**: 2024

3. **Title**: Cross-cultural Pragmatics and Code-switching in Multilingual EFL Classrooms (2025)
   - **Authors**: Smaglii, Yukhymets, Kornielaieva, Kivenko
   - **Summary**: Establishes that code-switching follows predictable patterns (inter-sentential, intra-sentential, tag-switching) serving specific pragmatic functions, providing sociolinguistic theory foundation for pattern generation.
   - **Year**: 2025

4. **Title**: LinguaSafe: A Comprehensive Multilingual Safety Benchmark (2025)
   - **Authors**: Not specified
   - **Summary**: Provides a translation-based multilingual safety evaluation benchmark for assessing LLM safety across multiple languages.
   - **Year**: 2025

5. **Title**: SGToxicGuard: Singapore Low-Resource Language Safety (2025)
   - **Authors**: Hu, Hee, Nakov, Lee
   - **Summary**: Evaluates existing models on low-resource languages, identifying safety gaps in current LLM deployments for underrepresented linguistic communities.
   - **Year**: 2025

6. **Title**: Benchmarking adversarial robustness to bias elicitation in LLMs (2025)
   - **Authors**: Cantini, Orsino, Ruggiero, Talia
   - **Summary**: Demonstrates that low-resource language jailbreaks are effective across multiple model families, revealing the widespread nature of cross-lingual safety vulnerabilities.
   - **Year**: 2025

7. **Title**: BeaverTails: Safety Alignment Dataset (2023)
   - **Authors**: Ji et al.
   - **Summary**: Provides a base safety dataset that can be used for code-switching augmentation in safety alignment training.
   - **Year**: 2023

**Key Challenges**
1. **Cross-lingual Safety Gap**: Code-switching attacks achieve significantly higher success rates (46.7% more) than standard English attacks, exposing a fundamental vulnerability in current LLM safety mechanisms.

2. **Pretraining Bottleneck**: The cross-lingual alignment problem originates in pretraining, and conventional low-resource language safety training yields minimal improvement, necessitating representation-level interventions.

3. **Low-Resource Language Vulnerability**: Existing models exhibit consistent safety gaps when processing low-resource languages, with jailbreak techniques proving effective across multiple model families.

4. **Evaluation vs. Training Gap**: Current multilingual safety work focuses primarily on evaluation benchmarks (translation-based approaches) rather than developing training methods to address identified vulnerabilities.

5. **Predictable Attack Patterns**: Code-switching follows systematic linguistic patterns (inter-sentential, intra-sentential, tag-switching) that can be exploited for adversarial purposes, requiring defenses that account for these structured variations.
