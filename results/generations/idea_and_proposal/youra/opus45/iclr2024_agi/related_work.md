## Related Work

**Related Papers**
1. **Title**: A computational perspective on neural-symbolic integration (Semantic Scholar ID: bd89caeea029722bbc8f709b4c038185fc01e503)
   - **Authors**: Šír
   - **Summary**: Demonstrates that static tensor graphs are computationally insufficient for general neural-symbolic integration, providing theoretical motivation for external module approaches.
   - **Year**: 2024

2. **Title**: Bridging Symbolic Control and Neural Reasoning: The Structured Cognitive Loop (Semantic Scholar ID: 7e23013b68cef0b16aba27d0fa826c4eae964bbf)
   - **Authors**: Kim
   - **Summary**: Proposes the R-CCAM architecture that separates cognition phases, achieving zero policy violations and complete traceability through modular separation principles.
   - **Year**: 2025

3. **Title**: Metagent-P: A Neuro-Symbolic Planning Agent with Metacognition (Semantic Scholar ID: 0939030d4ad669ebeb91b5ab22418bc1f025744b)
   - **Authors**: Zhou et al.
   - **Summary**: Introduces a planning-verification-execution-reflection framework that reduces replanning by 34%, demonstrating learnable neurosymbolic patterns.
   - **Year**: 2025

4. **Title**: A Roadmap Toward Neurosymbolic Approaches in AI Design (Semantic Scholar ID: 08ccc4f9c347f0f95bd740de7bb8cff2b3c5a9e9)
   - **Authors**: Jaysingha et al.
   - **Summary**: Presents a 5-stage symbolic integration framework that defines integration paradigms and provides taxonomic context for neurosymbolic approaches.
   - **Year**: 2025

5. **Title**: SymbolicAI Framework (arXiv:2402.00854)
   - **Authors**: Dinu et al.
   - **Summary**: Implements rule-based dispatch for LLM-solver orchestration, serving as a baseline for comparing learned versus rule-based selection approaches.
   - **Year**: 2024

6. **Title**: Pure LLM Baseline (Llama-3-8B-Instruct)
   - **Authors**: Not specified
   - **Summary**: Standard Chain-of-Thought prompting without external tools, serving as a lower-bound baseline to demonstrate the value of solver integration.
   - **Year**: Not specified

7. **Title**: Do Large Language Models Have Compositional Ability? (Semantic Scholar ID: 0e177741ef1e09fcf70b4236621d7204bc619439)
   - **Authors**: Xu et al.
   - **Summary**: Demonstrates that LLMs struggle with complex multi-step reasoning and that scaling helps simple but not complex tasks, motivating the need for external symbolic support.
   - **Year**: 2024

8. **Title**: Bridging LLMs and Symbolic Reasoning in Educational QA (Semantic Scholar ID: 901aeeed5620585391738bafdac18e28c733bb0c)
   - **Authors**: Nguyen et al.
   - **Summary**: Shows that hybrid LLM-Z3 systems improve accuracy with explainability, demonstrating the practical value of LLM-solver integration.
   - **Year**: 2025

**Key Challenges**
1. **Computational Insufficiency of Static Architectures**: Static tensor graphs are computationally insufficient for general neural-symbolic integration, necessitating external module approaches.
2. **Limited Compositional Reasoning in LLMs**: Large language models struggle with complex multi-step reasoning, and scaling model size helps with simple tasks but fails to address complex compositional challenges.
3. **Rule-Based vs. Learned Selection**: Existing frameworks rely on rule-based dispatch for LLM-solver orchestration, lacking the adaptability of learned selection mechanisms.
4. **Need for Modular Separation**: Achieving zero policy violations and complete traceability requires architectural separation of cognition phases rather than monolithic approaches.
5. **Replanning Overhead**: Current neurosymbolic systems suffer from inefficient replanning, requiring metacognitive frameworks to reduce computational overhead.
