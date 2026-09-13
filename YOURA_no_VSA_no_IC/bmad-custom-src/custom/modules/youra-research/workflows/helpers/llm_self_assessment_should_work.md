---
name: 'llm_self_assessment_should_work'
description: 'Lightweight LLM assessment for SHOULD_WORK gates in Phase 4'
helpers_path: '{project-root}/bmad-custom-src/custom/modules/youra-research/workflows/helpers'

# Exported Functions
exports:
  - perform_should_work_assessment
  - evaluate_should_work_answers
  - determine_should_work_decision
  - format_should_work_report
  - record_limitation

# Called By
called_by:
  - 'phase4-coding/steps/step-06-gate-processing.md'
  - 'phase4-coding/steps/step-06b-reflection.md'
---

# LLM Self-Assessment Helper Functions (SHOULD_WORK)

> Lightweight LLM assessment for SHOULD_WORK gates in Phase 4.
> Determines SELF_MODIFY vs FAIL decision for optional hypotheses.
>
> **Key Difference from MUST_WORK:**
> - 2 questions only (no compatibility check - optional gate)
> - No cascade handling (SHOULD_WORK failures don't block dependents)
> - FAIL means record limitation and continue, not route to Phase 0

---

## Constants

### Assessment Questions (Simplified - 2 Questions Only)

```python
# SHOULD_WORK uses simplified 2-question assessment
# No compatibility check needed (optional gate - failures don't block dependents)
SHOULD_WORK_QUESTIONS = {
    "improvement_potential": "Can you identify a specific, actionable modification that would improve the experiment results?",
    "worth_retry": "Is there at least 50% probability that Phase 2C modifications would lead to passing the gate?"
}

# Decision matrix (simplified)
SHOULD_WORK_DECISION_MATRIX = {
    # (improvement_potential, worth_retry) -> decision
    (True, True): "SELF_MODIFY", # Clear path to improvement
    (True, False): "FAIL", # Improvement identified but unlikely to succeed
    (False, True): "FAIL", # No clear improvement despite optimism
    (False, False): "FAIL" # No path forward
}

# Default decision on assessment failure
DEFAULT_DECISION = "FAIL" # Record limitation and continue (conservative for optional gate)
```

---

## Functions

### 1. build_should_work_assessment_prompt

```python
def build_should_work_assessment_prompt(
    hypothesis_id: str,
    pass_rate: float,
    failed_checks: list,
    experiment_summary: str = None
) -> str:
    """
    Build the LLM assessment prompt for SHOULD_WORK gates.

    Args:
        hypothesis_id: Current hypothesis identifier
        pass_rate: Percentage of criteria met (0.0 - 1.0)
        failed_checks: List of failed validation checks
        experiment_summary: Optional summary of experiment results

    Returns:
        Formatted prompt string for LLM

    Usage:
        prompt = build_should_work_assessment_prompt(
            "h-m1", 0.6, ["auxiliary_metric", "optional_constraint"],
            "Training completed but auxiliary loss remained high"
        )
    """
    failed_checks_formatted = "\n".join(f" - {check}" for check in failed_checks)

    experiment_context = ""
    if experiment_summary:
        experiment_context = f"""
**Experiment Summary:**
{experiment_summary}
"""

    prompt = f"""## SHOULD_WORK Hypothesis Assessment

**Hypothesis:** {hypothesis_id}
**Gate Type:** SHOULD_WORK (optional - failure does not block pipeline)
**Status:** PARTIAL (met {pass_rate*100:.0f}% of criteria)

**Failed Checks:**
{failed_checks_formatted}
{experiment_context}

### Assessment Questions (answer each):

1. **Improvement Potential**: {SHOULD_WORK_QUESTIONS["improvement_potential"]}
   - Consider: parameter changes, architecture tweaks, training modifications
   - Answer Yes only if you can name the specific modification
   (Yes/No + specific modification if Yes)

2. **Worth Retry**: {SHOULD_WORK_QUESTIONS["worth_retry"]}
   - Consider: how close were the results? Is the gap closeable?
   - Answer Yes only if probability of success is >=50%
   (Yes/No + confidence estimate)

### Decision Criteria:

- **SELF_MODIFY**: If BOTH questions are "Yes"
  → Route to Phase 2C with modifications, then Phase 3 → Phase 4 retry

- **FAIL**: If ANY question is "No"
  → Record limitation and continue to Phase 5 (acceptable for optional gate)

### Your Assessment:
"""

    return prompt
```

### 2. execute_should_work_assessment

```python
def execute_should_work_assessment(
    prompt: str,
    use_clearThought: bool = True
) -> dict:
    """
    Execute the LLM assessment for SHOULD_WORK gates.

    Args:
        prompt: Assessment prompt from build_should_work_assessment_prompt()
        use_clearThought: Whether to try ClearThought MCP first

    Returns:
        Dictionary containing:
            - success: bool - Assessment completed
            - improvement_potential: bool
            - worth_retry: bool
            - modification_suggestion: str - Suggested modification if any
            - confidence: str - Confidence estimate
            - raw_response: str - Full LLM response
            - method: str - "clearThought" or "manual"

    Usage:
        result = execute_should_work_assessment(prompt)
        if result["success"] and result["improvement_potential"] and result["worth_retry"]:
            print("SELF_MODIFY recommended")
    """
    # Try ClearThought MCP first
    if use_clearThought:
        try:
            clearThought_result = mcp__clearThought__scientificmethod(
                hypothesis=prompt,
                analysis_type="should_work_assessment"
            )

            if clearThought_result:
                parsed = parse_should_work_response(clearThought_result.get("analysis", ""))
                parsed["method"] = "clearThought"
                parsed["raw_response"] = str(clearThought_result)
                return parsed
        except Exception as e:
            print(f"ClearThought unavailable: {e}")
            # Fall through to manual LLM

    # Manual LLM analysis (fallback)
    try:
        llm_response = llm_analyze(prompt)
        parsed = parse_should_work_response(llm_response)
        parsed["method"] = "manual"
        parsed["raw_response"] = llm_response
        return parsed
    except Exception as e:
        # Return failed assessment
        return {
            "success": False,
            "improvement_potential": False,
            "worth_retry": False,
            "modification_suggestion": None,
            "confidence": "N/A",
            "raw_response": str(e),
            "method": "failed",
            "error": str(e)
        }
```

### 3. parse_should_work_response

```python
def parse_should_work_response(response: str) -> dict:
    """
    Parse LLM response to extract SHOULD_WORK assessment answers.

    Args:
        response: Raw LLM response text

    Returns:
        Dictionary with boolean answers and details

    Usage:
        parsed = parse_should_work_response(llm_response)
        print(f"Improvement possible: {parsed['improvement_potential']}")
    """
    response_lower = response.lower()
    import re

    def extract_yes_no(keyword: str) -> bool:
        """Extract yes/no answer for a question."""
        patterns = [
            f"{keyword}.*?:\\s*(yes|no)",
            f"{keyword}.*?(yes|no)",
        ]
        for pattern in patterns:
            match = re.search(pattern, response_lower)
            if match:
                return match.group(1) == "yes"
        return False # Default: no (conservative)

    improvement_potential = extract_yes_no("improvement")
    worth_retry = extract_yes_no("worth") or extract_yes_no("retry") or extract_yes_no("probability")

    # Extract modification suggestion if present
    modification_suggestion = None
    mod_match = re.search(r"modif(?:ication|y).*?[:\-]\s*(.+?)(?:\n|$)", response, re.IGNORECASE)
    if mod_match:
        modification_suggestion = mod_match.group(1).strip()[:200]

    # Extract confidence if present
    confidence = "Unknown"
    conf_match = re.search(r"(\d+%|(?:high|medium|low)\s*confidence)", response_lower)
    if conf_match:
        confidence = conf_match.group(1)

    return {
        "success": True,
        "improvement_potential": improvement_potential,
        "worth_retry": worth_retry,
        "modification_suggestion": modification_suggestion,
        "confidence": confidence
    }
```

### 4. determine_should_work_decision

```python
def determine_should_work_decision(assessment_result: dict) -> dict:
    """
    Determine SELF_MODIFY vs FAIL from SHOULD_WORK assessment results.

    Args:
        assessment_result: Result from execute_should_work_assessment()

    Returns:
        Dictionary containing:
            - decision: "SELF_MODIFY" or "FAIL"
            - reasoning: str - Explanation of decision
            - modification_suggestion: str - Suggested modification (if SELF_MODIFY)

    Usage:
        decision = determine_should_work_decision(assessment_result)
        if decision["decision"] == "SELF_MODIFY":
            # Route to Phase 2C
        else:
            # Record limitation, continue to Phase 5
    """
    if not assessment_result.get("success", False):
        return {
            "decision": DEFAULT_DECISION,
            "reasoning": "Assessment failed - recording limitation and continuing (conservative for optional gate)",
            "modification_suggestion": None
        }

    improvement = assessment_result.get("improvement_potential", False)
    worth_it = assessment_result.get("worth_retry", False)

    # Apply decision matrix
    key = (improvement, worth_it)
    decision = SHOULD_WORK_DECISION_MATRIX.get(key, DEFAULT_DECISION)

    # Build reasoning
    if decision == "SELF_MODIFY":
        reasoning = f"Improvement identified with good success probability. Suggested: {assessment_result.get('modification_suggestion', 'See assessment')}"
    else:
        reasons = []
        if not improvement:
            reasons.append("No specific improvement identified")
        if not worth_it:
            reasons.append("Low probability of success (<50%)")
        reasoning = f"Recording limitation: {'; '.join(reasons)}. Continuing to Phase 5."

    return {
        "decision": decision,
        "reasoning": reasoning,
        "modification_suggestion": assessment_result.get("modification_suggestion") if decision == "SELF_MODIFY" else None,
        "confidence": assessment_result.get("confidence", "Unknown")
    }
```

### 5. perform_llm_self_assessment_should_work (Main Function)

```python
def perform_llm_self_assessment_should_work(
    hypothesis_id: str,
    pass_rate: float,
    failed_checks: list,
    experiment_summary: str = None,
    use_clearThought: bool = True
) -> dict:
    """
    Main function: Complete LLM assessment workflow for SHOULD_WORK gates.

    This orchestrates the full assessment:
    1. Build assessment prompt (2 questions)
    2. Execute LLM assessment
    3. Determine decision (SELF_MODIFY or FAIL)

    Args:
        hypothesis_id: Current hypothesis identifier
        pass_rate: Percentage of criteria met (0.0 - 1.0)
        failed_checks: List of failed validation checks
        experiment_summary: Optional summary of experiment results
        use_clearThought: Whether to try ClearThought MCP

    Returns:
        Dictionary containing:
            - decision: "SELF_MODIFY" or "FAIL"
            - reasoning: str
            - modification_suggestion: str - If SELF_MODIFY
            - assessment_result: dict - Full assessment details
            - checkpoint_updates: dict - Updates for checkpoint

    Usage:
        result = perform_llm_self_assessment_should_work(
            "h-m1", 0.6, ["auxiliary_loss"],
            "Training stable but auxiliary metric underperformed"
        )
        if result["decision"] == "SELF_MODIFY":
            # Create new version, route to Phase 2C
        else:
            # Record limitation, continue to Phase 5
    """
    # Step 1: Build prompt
    prompt = build_should_work_assessment_prompt(
        hypothesis_id, pass_rate, failed_checks, experiment_summary
    )

    # Step 2: Execute assessment
    assessment = execute_should_work_assessment(prompt, use_clearThought)

    # Step 3: Determine decision
    decision_result = determine_should_work_decision(assessment)

    # Step 4: Prepare checkpoint updates
    if decision_result["decision"] == "SELF_MODIFY":
        checkpoint_updates = {
            "llm_assessment": "SHOULD_WORK_SELF_MODIFY",
            "reflection_outcome": "SELF_MODIFY",
            "modification_suggestion": decision_result.get("modification_suggestion"),
            "route_to": "phase2c"
        }
    else:
        checkpoint_updates = {
            "llm_assessment": "SHOULD_WORK_FAIL",
            "reflection_outcome": "LIMITATION_RECORDED",
            "should_work_failed": True,
            "limitation_note": f"{hypothesis_id}: {decision_result['reasoning']}"
        }

    return {
        "decision": decision_result["decision"],
        "reasoning": decision_result["reasoning"],
        "modification_suggestion": decision_result.get("modification_suggestion"),
        "confidence": decision_result.get("confidence", "Unknown"),
        "assessment_result": assessment,
        "checkpoint_updates": checkpoint_updates
    }
```

---

## Usage Example (step-06b-reflection.md)

```python
# In step-06b-reflection.md Section 1b
# When gate_type == "SHOULD_WORK" AND reflection_type == "llm_assessment_should_work"

from llm_self_assessment_should_work import perform_llm_self_assessment_should_work

# Execute LLM assessment
result = perform_llm_self_assessment_should_work(
    hypothesis_id,
    pass_rate,
    failed_checks,
    experiment_summary=checkpoint.get("experiment_summary")
)

# Update checkpoint
checkpoint.update(result["checkpoint_updates"])
SAVE checkpoint

# Route based on decision
IF result["decision"] == "SELF_MODIFY":
    # Create new hypothesis version
    new_hypothesis_id = f"{hypothesis_id}-v{current_version + 1}"

    # Update verification_state
    hypotheses[hypothesis_id].status = "COMPLETED"
    hypotheses[new_hypothesis_id] = {
        "version": current_version + 1,
        "modified_from": hypothesis_id,
        "modification_attempt": modification_attempt + 1,
        "status": "READY",
        "gate": same_gate_config,
        "modification_suggestion": result["modification_suggestion"]
    }

    checkpoint.new_hypothesis_id = new_hypothesis_id
    checkpoint.reflection_outcome = "SELF_MODIFY"
    Display: f"SHOULD_WORK: SELF_MODIFY - routing to Phase 2C with {new_hypothesis_id}"
    GOTO Section_5a # Create new version

ELSE:
    # Record limitation, continue to Phase 5
    checkpoint.should_work_failed = True
    checkpoint.limitation_note = result["reasoning"]
    checkpoint.reflection_outcome = "LIMITATION_RECORDED"
    Display: f"SHOULD_WORK: Recording limitation - {result['reasoning']}"
    GOTO Section_7 # Save report, continue to Phase 5
```

---

## Decision Logic Summary

| Improvement Potential | Worth Retry | Decision | Action |
|-----------------------|-------------|----------|--------|
| Yes | Yes | **SELF_MODIFY** | Route to Phase 2C |
| Yes | No | FAIL | Record limitation |
| No | Yes | FAIL | Record limitation |
| No | No | FAIL | Record limitation |
| **Error** | **Error** | **FAIL** | Record limitation |

> **Conservative Default:** On assessment failure, default to FAIL (record limitation).
> This is appropriate for optional gates - we don't block the pipeline on uncertainty.

---

