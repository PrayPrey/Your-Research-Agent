## Related Work

**Related Papers**
1. **Title**: TrustAgent: Towards Safe and Trustworthy LLM-based Agents (arXiv:2402.01586)
   - **Authors**: Wenyue Hua, Xianjun Yang, Mingyu Jin, et al.
   - **Summary**: Proposes an Agent-Constitution framework with pre/in/post planning strategies that enhances both safety and helpfulness of LLM-based agents.
   - **Year**: 2024

2. **Title**: HiddenDetect: Detecting Jailbreak Attacks against Large Vision-Language Models via Monitoring Hidden States (arXiv:2502.14744)
   - **Authors**: Yilei Jiang et al.
   - **Summary**: Demonstrates that LVLMs encode safety-relevant signals in internal activations and achieves state-of-the-art tuning-free detection of jailbreak attacks.
   - **Year**: 2025

3. **Title**: Pro2Guard: Proactive Runtime Enforcement of LLM Agent Safety via Probabilistic Model Checking
   - **Authors**: Haoyu Wang, Christopher M. Poskitt, Jun Sun, Jiali Wei
   - **Summary**: Introduces DTMC-based probabilistic checking that enables predictive safety intervention for LLM agents at runtime.
   - **Year**: 2025

4. **Title**: NeMo Guardrails
   - **Authors**: NVIDIA
   - **Summary**: Provides production-ready reactive guardrails for LLM systems with 1.4x detection improvement at approximately 0.5s latency.
   - **Year**: 2024-2025

5. **Title**: R-Judge: Benchmarking Safety Risk Awareness for LLM Agents
   - **Authors**: Tongxin Yuan et al.
   - **Summary**: Presents a benchmark with 569 records across 27 risk scenarios and 10 risk types for evaluating LLM agent safety risk awareness, finding GPT-4o achieves only 74.45% accuracy.
   - **Year**: 2024

6. **Title**: Immune-Based Botnet Defense System: Multi-Layered Defense and Immune Memory
   - **Authors**: Shingo Yamaguchi
   - **Summary**: Proposes a multi-layered defense architecture with immune memory mechanisms for cybersecurity applications.
   - **Year**: 2025

7. **Title**: Sifting the Noise: A Comparative Study of LLM Agents in Vulnerability False Positive Filtering
   - **Authors**: Yunpeng Xiong, Ting Zhang
   - **Summary**: Demonstrates that LLM agents can reduce false positives from 92% to 6.3% on the OWASP Benchmark for vulnerability detection.
   - **Year**: 2026

**Key Challenges**
1. **Limited Runtime Adaptation**: Existing safety frameworks like TrustAgent provide static pre/in/post planning strategies but lack dynamic runtime adaptation capabilities.

2. **Reactive vs. Proactive Safety**: Current production systems like NeMo Guardrails rely on reactive guardrails, creating a gap in proactive safety intervention approaches.

3. **Insufficient Risk Awareness**: Benchmark evaluations show that even advanced models like GPT-4o achieve only 74.45% accuracy on safety risk awareness tasks, indicating significant room for improvement.

4. **High False Positive Rates**: Safety detection systems suffer from high false positive rates (up to 92%), requiring more sophisticated filtering mechanisms.

5. **Latency-Safety Tradeoff**: Production guardrail systems introduce approximately 0.5s latency, highlighting the challenge of balancing safety enforcement with system responsiveness.
