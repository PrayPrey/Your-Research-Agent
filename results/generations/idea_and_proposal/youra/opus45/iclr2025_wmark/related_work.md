## Related Work

**Related Papers**
1. **Title**: RAILS: A Robust Adversarial Immune-Inspired Learning System (IEEE 2020)
   - **Authors**: Wang, Chen, Lindsly, Stansbury, Rehemtulla, Rajapakse, Hero
   - **Summary**: Demonstrates that immune-inspired evolutionary optimization achieves 5-12% adversarial robustness improvement, validating cross-domain transfer from immunology to DNN defense.
   - **Year**: 2020

2. **Title**: Benchmarking the Robustness of Image Watermarks (WAVES)
   - **Authors**: An, Ding, Rabbani, Agrawal, Xu, Deng, Zhu, Mohamed, Wen, Goldstein, Huang
   - **Summary**: Provides a standardized benchmark that reveals previously undetected vulnerabilities in modern watermarking algorithms, covering both diffusive and adversarial attacks.
   - **Year**: 2024

3. **Title**: Evading Watermark based Detection of AI-Generated Content (WEvade)
   - **Authors**: Jiang, Zhang, Gong
   - **Summary**: Demonstrates that human-imperceptible adversarial perturbations can systematically evade watermark detection and characterizes the associated threat model.
   - **Year**: 2023

4. **Title**: DiffuseTrace: A Transparent and Flexible Watermarking Scheme
   - **Authors**: Lei et al.
   - **Summary**: Proposes a multi-bit watermarking scheme achieving 99% detection rate under 8 attack types, serving as a base watermarking approach for integration.
   - **Year**: 2024

5. **Title**: Watermark under Fire: A Robustness Evaluation (WaterPark)
   - **Authors**: Liang, Wang, Hong, Ji, Wang
   - **Summary**: Presents a unified evaluation platform with 10 watermarkers and 12 attacks, establishing best practices for watermarking in adversarial environments.
   - **Year**: 2024

6. **Title**: Static Watermark Detector (Baseline)
   - **Authors**: Not specified
   - **Summary**: Standard single-model watermark detector without adaptation, serving as a primary comparison baseline.
   - **Year**: Not specified

7. **Title**: Fixed Ensemble (No Evolution) (Baseline)
   - **Authors**: Not specified
   - **Summary**: Ensemble of detectors without evolutionary adaptation, used as an ablation baseline to isolate the contribution of evolutionary mechanisms.
   - **Year**: Not specified

8. **Title**: Scalable watermarking for identifying large language model outputs (SynthID)
   - **Authors**: Dathathri, See, Ghaisas et al. (Google DeepMind)
   - **Summary**: First large-scale deployment of AI watermarking, highlighting the need for robust detection mechanisms in production environments.
   - **Year**: 2024

9. **Title**: The Cyber Immune System
   - **Authors**: Tallam
   - **Summary**: Proposes that adversarial forces reveal systemic weaknesses and drive adaptation, framing attacks as evolutionary pressure for system improvement.
   - **Year**: 2025

**Key Challenges**
1. **Vulnerability to Adversarial Attacks**: Current watermarking algorithms contain previously undetected vulnerabilities that can be exploited through diffusive and adversarial attacks.
2. **Systematic Evasion of Detection**: Human-imperceptible adversarial perturbations can systematically evade watermark detection, posing a significant threat to watermarking systems.
3. **Static Defense Limitations**: Standard single-model watermark detectors lack adaptation capabilities, making them susceptible to evolving attack strategies.
4. **Production Deployment Robustness**: Large-scale deployment of AI watermarking in production environments requires more robust detection mechanisms than currently available.
5. **Lack of Adaptive Mechanisms**: Existing ensemble approaches without evolutionary adaptation fail to respond dynamically to new attack patterns and adversarial pressures.
