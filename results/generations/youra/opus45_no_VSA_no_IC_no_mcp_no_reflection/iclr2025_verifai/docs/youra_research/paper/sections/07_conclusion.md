# 7. Conclusion

We asked whether static analyzers can improve LLM code repair. The answer remains open—but we now have the methodology to find it.

**What we found:** Canonical HumanEval solutions exhibit only 9.15% pylint warning rates. This makes them invalid proxies for LLM-generated code, which typically contains more issues. Our MUST_WORK gate correctly identified this limitation before downstream experiments wasted resources.

**What we built:** A validated pylint analysis pipeline for code generation research, reusable components for HumanEval loading and static analysis, and a gate-based hypothesis validation framework. These contributions enable future work to complete the evaluation with LLM API access.

**What we learned:** Gate-based validation works. By testing existence assumptions before full experiments, we catch methodology issues early. The 30% threshold—requiring sufficient static signal for the intervention to matter—proved decisive.

**The path forward:** Re-run the existence gate with actual LLM generations (GPT-4, Claude). If warning rates exceed 30%, proceed to mechanism validation and full pass@k comparison. The infrastructure is ready; the hypothesis awaits proper testing.

**Broader implication:** Before evaluating any LLM intervention, validate that the intervention has signal. Canonical solutions are not LLM output—a lesson applicable beyond static analysis to any benchmark-based evaluation.

We contribute methodology, not conclusions. The question of whether static analysis improves pass@k is worth answering—and we provide the tools to answer it.
