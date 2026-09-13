## Related Work

**Related Papers**
1. **Title**: JBShield ([Zhang et al. 2025])
   - **Authors**: Zhang et al.
   - **Summary**: Achieves 95% single-turn jailbreak detection accuracy using concept activation vectors extracted from LLM hidden states via linear probes for toxic and jailbreak dimensions.
   - **Year**: 2025

2. **Title**: RACE ([Ying et al. 2025])
   - **Authors**: Ying et al.
   - **Summary**: Demonstrates 82% attack success rate using multi-turn attack state machine with deliberate progression from benign to harmful prompts, showing gradual semantic drift.
   - **Year**: 2025

3. **Title**: MM-ART ([Singhania et al. 2025])
   - **Authors**: Singhania et al.
   - **Summary**: Shows LLMs are 71% more vulnerable after 5 turns in multilingual attack scenarios, demonstrating multi-turn attack effectiveness.
   - **Year**: 2025

4. **Title**: LSTM-based Intrusion Detection System ([Hiari et al. 2025])
   - **Authors**: Hiari et al.
   - **Summary**: Achieves high DoS detection via LSTM sequential modeling, demonstrating LSTM's effectiveness in capturing temporal patterns in security contexts.
   - **Year**: 2025

5. **Title**: Immune System Architecture for LLM Safety ([Wang et al. 2024])
   - **Authors**: Wang et al.
   - **Summary**: Provides architectural blueprint for immune-inspired defenses validated over evolutionary timescales, establishing biological two-tier architecture principles.
   - **Year**: 2024

6. **Title**: KG-Guard
   - **Authors**: Not specified
   - **Summary**: Symbolic knowledge graph-based multi-turn defense system offering interpretability through graph structures (contrasted with ImmuneLM's subsymbolic LSTM approach).
   - **Year**: Not specified

7. **Title**: PyRIT (Python Risk Identification Toolkit)
   - **Authors**: Not specified
   - **Summary**: Open-source infrastructure for automated red teaming and attack generation, used for creating synthetic multi-turn jailbreak attacks.
   - **Year**: Not specified

8. **Title**: DeepTeam
   - **Authors**: Not specified
   - **Summary**: Open-source infrastructure for evaluation and attack pattern construction in LLM security testing.
   - **Year**: Not specified

**Key Challenges**
1. **Stateless Defense Gap**: Single-turn detection methods (like JBShield) cannot detect gradual semantic drift across conversation turns, as they analyze each turn independently without conversational memory.

2. **Multi-Turn Attack Evasion**: Multi-turn jailbreaks succeed by keeping individual turns below detection thresholds while cumulative effect crosses safety boundaries (demonstrated by MM-ART's 71% increased vulnerability).

3. **Temporal Pattern Modeling**: Existing defenses lack mechanisms to track attack progression over 3-20 turns and detect benign-to-harmful conversational evolution before jailbreak completion.

4. **Concept Signal Sufficiency**: Uncertainty whether per-turn concept activation vectors contain sufficient temporal signal (correlation ≥0.6) for LSTM to model attack progression effectively.

5. **Interpretability vs. Robustness Trade-off**: Symbolic approaches (KG-Guard) offer interpretability while subsymbolic approaches (LSTM-based) may offer better robustness, requiring balance between transparency and effectiveness.

6. **LLM Version Brittleness**: Defense mechanisms require retraining when LLMs undergo major updates, creating maintenance burden for production deployment.

7. **Generalization to Novel Attacks**: Challenge of achieving ≥70% zero-shot detection on held-out human adversarial attacks not seen during training.

8. **Latency Constraints**: Production deployment requires ≤500ms per-turn processing time while maintaining LSTM forward pass, pattern matching, and concept extraction operations.

9. **False Positive Management**: Need to maintain ≤5% false positive rate on benign conversations while achieving significant attack detection improvement (≥20% ASR reduction).

10. **Attack Pattern Library Maintenance**: Continuous challenge of updating attack pattern library quarterly with new attack discoveries while maintaining system performance.

11. **Error Propagation**: Tier 1 concept extraction errors propagate to Tier 2 LSTM, requiring error-tolerant hybrid design with parallel information pathways.

12. **Industry-Scale Manual Red Teaming**: Current reliance on manual red teaming by companies (OpenAI, Microsoft, Anthropic) is not scalable, requiring automated multi-turn defense mechanisms.
