---
name: 'llm_self_assessment'
description: 'Reusable functions for LLM-based compatibility assessment in Phase 4 reflection'
helpers_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/helpers'

# Exported Functions
exports:
  - perform_compatibility_assessment
  - evaluate_assessment_answers
  - determine_decision_from_matrix
  - format_assessment_report

# Called By
called_by:
  - 'phase4-coding/steps/step-06b-reflection.md'
---

# LLM Self-Assessment Helper Functions

> Reusable functions for LLM-based compatibility assessment in Phase 4 reflection.
> Determines SELF_MODIFY vs SUPERSEDED decision for PARTIAL results.

---

## Constants

### Assessment Questions

```python
# The four compatibility questions for LLM assessment
ASSESSMENT_QUESTIONS = {
    "interface": "Do the PARTIAL results still provide the interfaces that dependent hypotheses expect?",
    "data_flow": "Will dependent hypotheses receive correct data types and shapes from this PARTIAL implementation?",
    "behavior": "Are the behavioral assumptions of dependent hypotheses still valid with these PARTIAL results?",
    "recovery": "Can the failed aspects be fixed with parameter tuning or minor code changes without changing the hypothesis core?"
}

# Decision matrix encoding
DECISION_MATRIX = {
    # (interface, data_flow, behavior, recovery) -> decision
    (True, True, True, True): "SELF_MODIFY",
    (True, True, True, False): "SUPERSEDED",
    (True, True, False, True): "SUPERSEDED",
    (True, True, False, False): "SUPERSEDED",
    (True, False, True, True): "SUPERSEDED",
    (True, False, True, False): "SUPERSEDED",
    (True, False, False, True): "SUPERSEDED",
    (True, False, False, False): "SUPERSEDED",
    (False, True, True, True): "SUPERSEDED",
    # All False combinations -> SUPERSEDED
}

# Default decision on assessment failure
DEFAULT_DECISION = "SUPERSEDED" # Conservative: assume incompatibility
```

---

## Functions

### 1. build_assessment_prompt

```python
def build_assessment_prompt(
    hypothesis_id: str,
    pass_rate: float,
    failed_checks: list,
    dependents: list
) -> str:
    """
    Build the LLM self-assessment prompt.

    Args:
        hypothesis_id: Current hypothesis identifier
        pass_rate: Percentage of criteria met (0.0 - 1.0)
        failed_checks: List of failed validation checks
        dependents: List of dependent hypothesis info

    Returns:
        Formatted prompt string for LLM

    Usage:
        prompt = build_assessment_prompt(
            "h-e1", 0.6, ["loss_threshold", "accuracy_target"],
            [{"id": "h-e2", "dependency": "uses output from h-e1"}]
        )
    """
    dependents_formatted = format_dependents(dependents)
    failed_checks_formatted = "\n".join(f" - {check}" for check in failed_checks)

    prompt = f"""## Hypothesis Compatibility Assessment

**Current Hypothesis:** {hypothesis_id}
**Status:** PARTIAL (met {pass_rate*100:.0f}% of criteria)

**Failed Criteria:**
{failed_checks_formatted}

**Dependent Hypotheses:**
{dependents_formatted}

### Assessment Questions (answer each):

1. **Interface Compatibility**: {ASSESSMENT_QUESTIONS["interface"]}
   (Yes/No + explanation)

2. **Data Flow Impact**: {ASSESSMENT_QUESTIONS["data_flow"]}
   (Yes/No + explanation)

3. **Behavioral Assumptions**: {ASSESSMENT_QUESTIONS["behavior"]}
   (Yes/No + explanation)

4. **Recovery Potential**: {ASSESSMENT_QUESTIONS["recovery"]}
   (Yes/No + explanation)

### Decision Criteria:

- **SELF_MODIFY**: If Questions 1-3 are "Yes" AND Question 4 is "Yes"
  → Minor modifications can fix issues without breaking dependent hypotheses

- **SUPERSEDED**: If ANY of Questions 1-3 are "No" OR Question 4 is "No"
  → Fundamental redesign needed, hypothesis must be superseded

### Your Assessment:
"""

    return prompt

def format_dependents(dependents: list) -> str:
    """Format dependent hypotheses for prompt."""
    if not dependents:
        return "*No dependent hypotheses found.*"

    lines = []
    for dep in dependents:
        dep_id = dep.get("id", "Unknown")
        dependency = dep.get("dependency", "Unknown relationship")
        status = dep.get("status", "Unknown")
        lines.append(f"- **{dep_id}** ({status}): {dependency}")

    return "\n".join(lines)
```

### 2. execute_assessment

```python
def execute_assessment(
    prompt: str,
    use_clearThought: bool = True
) -> dict:
    """
    Execute the LLM self-assessment.

    Args:
        prompt: Assessment prompt from build_assessment_prompt()
        use_clearThought: Whether to try ClearThought MCP first

    Returns:
        Dictionary containing:
            - success: bool - Assessment completed
            - interface_compatible: bool
            - data_flow_valid: bool
            - behavioral_valid: bool
            - recovery_possible: bool
            - explanations: dict - Explanations for each answer
            - raw_response: str - Full LLM response
            - method: str - "clearThought" or "manual"

    Usage:
        result = execute_assessment(prompt)
        if result["success"]:
            if all_compatible(result):
                print("SELF_MODIFY possible")
    """
    # Try ClearThought MCP first
    if use_clearThought:
        try:
            clearThought_result = mcp__clearThought__scientificmethod(
                hypothesis=prompt,
                analysis_type="compatibility_assessment"
            )

            if clearThought_result:
                parsed = parse_assessment_response(clearThought_result.get("analysis", ""))
                parsed["method"] = "clearThought"
                parsed["raw_response"] = str(clearThought_result)
                return parsed
        except Exception as e:
            print(f"ClearThought unavailable: {e}")
            # Fall through to manual LLM

    # Manual LLM analysis (fallback)
    try:
        llm_response = llm_analyze(prompt)
        parsed = parse_assessment_response(llm_response)
        parsed["method"] = "manual"
        parsed["raw_response"] = llm_response
        return parsed
    except Exception as e:
        # Return failed assessment
        return {
            "success": False,
            "interface_compatible": False,
            "data_flow_valid": False,
            "behavioral_valid": False,
            "recovery_possible": False,
            "explanations": {},
            "raw_response": str(e),
            "method": "failed",
            "error": str(e)
        }
```

### 3. parse_assessment_response

```python
def parse_assessment_response(response: str) -> dict:
    """
    Parse LLM response to extract assessment answers.

    Args:
        response: Raw LLM response text

    Returns:
        Dictionary with boolean answers and explanations

    Usage:
        parsed = parse_assessment_response(llm_response)
        print(f"Interface compatible: {parsed['interface_compatible']}")
    """
    response_lower = response.lower()

    def extract_answer(question_keyword: str) -> tuple:
        """Extract yes/no and explanation for a question."""
        # Look for patterns like "Interface Compatibility: Yes" or "1. Interface: No"
        patterns = [
            f"{question_keyword}.*?:\\s*(yes|no)",
            f"{question_keyword}.*?(yes|no)",
        ]

        import re
        for pattern in patterns:
            match = re.search(pattern, response_lower)
            if match:
                answer = match.group(1) == "yes"
                # Extract explanation (text after yes/no until next question or end)
                start_idx = match.end()
                explanation = response[start_idx:start_idx + 200].strip()
                return answer, explanation

        # Default: assume no (conservative)
        return False, "Could not parse answer"

    interface_compat, interface_expl = extract_answer("interface")
    data_flow_valid, data_flow_expl = extract_answer("data flow")
    behavioral_valid, behavior_expl = extract_answer("behavio")
    recovery_possible, recovery_expl = extract_answer("recovery")

    return {
        "success": True,
        "interface_compatible": interface_compat,
        "data_flow_valid": data_flow_valid,
        "behavioral_valid": behavioral_valid,
        "recovery_possible": recovery_possible,
        "explanations": {
            "interface": interface_expl[:100],
            "data_flow": data_flow_expl[:100],
            "behavior": behavior_expl[:100],
            "recovery": recovery_expl[:100]
        }
    }
```

### 4. determine_decision

```python
def determine_decision(assessment_result: dict) -> dict:
    """
    Determine SELF_MODIFY vs SUPERSEDED from assessment results.

    Args:
        assessment_result: Result from execute_assessment()

    Returns:
        Dictionary containing:
            - decision: "SELF_MODIFY" or "SUPERSEDED"
            - compatible: bool - All compatibility checks passed
            - reasoning: str - Explanation of decision
            - incompatible_factors: list - Which checks failed

    Usage:
        decision = determine_decision(assessment_result)
        if decision["decision"] == "SELF_MODIFY":
            # Minor modifications can fix
        else:
            # Need to supersede and redesign
    """
    if not assessment_result.get("success", False):
        return {
            "decision": DEFAULT_DECISION,
            "compatible": False,
            "reasoning": "Assessment failed - defaulting to SUPERSEDED (conservative)",
            "incompatible_factors": ["assessment_failure"]
        }

    interface = assessment_result.get("interface_compatible", False)
    data_flow = assessment_result.get("data_flow_valid", False)
    behavior = assessment_result.get("behavioral_valid", False)
    recovery = assessment_result.get("recovery_possible", False)

    # Check all compatibility factors
    compatible = all([interface, data_flow, behavior, recovery])

    # Determine which factors failed
    incompatible_factors = []
    if not interface:
        incompatible_factors.append("interface_compatibility")
    if not data_flow:
        incompatible_factors.append("data_flow")
    if not behavior:
        incompatible_factors.append("behavioral_assumptions")
    if not recovery:
        incompatible_factors.append("recovery_potential")

    # Make decision
    if compatible:
        decision = "SELF_MODIFY"
        reasoning = "All compatibility checks passed. Minor modifications can fix issues."
    else:
        decision = "SUPERSEDED"
        reasoning = f"Incompatible factors: {', '.join(incompatible_factors)}. Redesign needed."

    return {
        "decision": decision,
        "compatible": compatible,
        "reasoning": reasoning,
        "incompatible_factors": incompatible_factors,
        "details": {
            "interface": interface,
            "data_flow": data_flow,
            "behavior": behavior,
            "recovery": recovery
        }
    }
```

### 5. perform_llm_self_assessment (Main Function)

```python
def perform_llm_self_assessment(
    hypothesis_id: str,
    pass_rate: float,
    failed_checks: list,
    verification_state: dict,
    use_clearThought: bool = True
) -> dict:
    """
    Main function: Complete LLM self-assessment workflow.

    This orchestrates the full assessment:
    1. Find dependent hypotheses
    2. Build assessment prompt
    3. Execute LLM assessment
    4. Determine decision

    Args:
        hypothesis_id: Current hypothesis identifier
        pass_rate: Percentage of criteria met (0.0 - 1.0)
        failed_checks: List of failed validation checks
        verification_state: Full verification_state dict
        use_clearThought: Whether to try ClearThought MCP

    Returns:
        Dictionary containing:
            - decision: "SELF_MODIFY" or "SUPERSEDED"
            - compatible: bool
            - assessment_result: dict - Full assessment details
            - dependents: list - Dependent hypotheses found
            - checkpoint_updates: dict - Updates for checkpoint

    Usage:
        result = perform_llm_self_assessment(
            "h-e1", 0.6, ["loss_threshold"],
            verification_state
        )
        if result["decision"] == "SELF_MODIFY":
            # Proceed with modification
        else:
            # Route to SUPERSEDED handling
    """
    from archon_cascade import find_dependent_hypotheses

    # Step 1: Find dependent hypotheses
    dependents = find_dependent_hypotheses(verification_state, hypothesis_id)

    # Step 2: If no dependents, allow self-modify by default
    if not dependents:
        return {
            "decision": "SELF_MODIFY",
            "compatible": True,
            "assessment_result": {
                "success": True,
                "interface_compatible": True,
                "data_flow_valid": True,
                "behavioral_valid": True,
                "recovery_possible": True,
                "explanations": {"note": "No dependent hypotheses - skip compatibility check"}
            },
            "dependents": [],
            "reasoning": "No dependent hypotheses found - self-modify allowed by default",
            "checkpoint_updates": {
                "llm_assessment": "COMPATIBLE",
                "llm_assessment_details": {"no_dependents": True}
            }
        }

    # Step 3: Build and execute assessment
    prompt = build_assessment_prompt(hypothesis_id, pass_rate, failed_checks, dependents)
    assessment = execute_assessment(prompt, use_clearThought)

    # Step 4: Determine decision
    decision_result = determine_decision(assessment)

    # Step 5: Prepare checkpoint updates
    if decision_result["decision"] == "SELF_MODIFY":
        checkpoint_updates = {
            "llm_assessment": "COMPATIBLE",
            "reflection_outcome": "SELF_MODIFY"
        }
    else:
        checkpoint_updates = {
            "llm_assessment": "INCOMPATIBLE",
            "llm_assessment_details": assessment,
            "reflection_outcome": "ROUTED_TO_PHASE_2A"
        }

    return {
        "decision": decision_result["decision"],
        "compatible": decision_result["compatible"],
        "reasoning": decision_result["reasoning"],
        "incompatible_factors": decision_result.get("incompatible_factors", []),
        "assessment_result": assessment,
        "dependents": dependents,
        "checkpoint_updates": checkpoint_updates
    }
```

---

## Decision Logic Summary

| Interface | Data Flow | Behavior | Recovery | → Decision |
|-----------|-----------|----------|----------|------------|
| ✓ | ✓ | ✓ | ✓ | SELF_MODIFY |
| ✓ | ✓ | ✓ | ✗ | SUPERSEDED |
| ✓ | ✓ | ✗ | Any | SUPERSEDED |
| ✓ | ✗ | Any | Any | SUPERSEDED |
| ✗ | Any | Any | Any | SUPERSEDED |
| **Error** | **Error** | **Error** | **Error** | **SUPERSEDED** |

> **Conservative Default:** On assessment failure, default to SUPERSEDED to avoid breaking dependent hypotheses with incompatible partial results.
