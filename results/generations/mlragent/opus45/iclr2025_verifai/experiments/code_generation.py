"""Code Generation Module for SpecBridge.

This module implements:
1. Baseline code generation (direct LLM generation without specs)
2. Specification-guided code generation (SpecBridge approach)
3. Iterative refinement with counterexamples
"""

import json
import re
from config import MAX_REFINEMENT_ITERATIONS
from model_wrapper import get_llm

BASELINE_CODE_GEN_PROMPT = """You are an expert Python programmer. Write a Python function that implements the following requirement.
Only output the function code, no explanations. Use proper Python syntax.

Requirement: {description}

Function name should be: {func_name}

Python code:"""

SPECBRIDGE_CODE_GEN_PROMPT = """You are an expert Python programmer. Write a Python function that:
1. Implements the given requirement
2. Satisfies the formal specification (precondition and postcondition)

The function MUST satisfy:
- Precondition: {precondition}
- Postcondition: {postcondition}

Requirement: {description}

Function name should be: {func_name}

Only output the Python function code:"""

REFINEMENT_PROMPT = """The previously generated code failed verification with the following error:
{error}

Counterexample: {counterexample}

Please fix the code to handle this case correctly.

Original requirement: {description}
Specification:
- Precondition: {precondition}
- Postcondition: {postcondition}

Previous code:
{previous_code}

Fixed Python function code:"""

def extract_function_code(response: str) -> str:
    """Extract Python function code from LLM response."""
    # Try to extract code block
    code_match = re.search(r'```python\n(.*?)```', response, re.DOTALL)
    if code_match:
        return code_match.group(1).strip()

    code_match = re.search(r'```\n(.*?)```', response, re.DOTALL)
    if code_match:
        return code_match.group(1).strip()

    # Look for def statement
    lines = response.split('\n')
    code_lines = []
    in_function = False
    brace_count = 0

    for line in lines:
        stripped = line.strip()
        if stripped.startswith('def '):
            in_function = True
            code_lines.append(line)
        elif in_function:
            if stripped == '' and not code_lines[-1].strip().endswith(':'):
                # Empty line might end function
                if len(code_lines) > 1:
                    code_lines.append(line)
            elif line.startswith(' ') or line.startswith('\t') or stripped == '':
                code_lines.append(line)
            elif stripped.startswith(('#', 'return', 'if', 'for', 'while', 'else', 'elif', 'try', 'except', 'finally', 'with', 'raise', 'assert', 'pass', 'break', 'continue')):
                if line.startswith(' ') or line.startswith('\t'):
                    code_lines.append(line)
                else:
                    break
            else:
                break

    if code_lines:
        # Clean up trailing empty lines
        while code_lines and code_lines[-1].strip() == '':
            code_lines.pop()
        return '\n'.join(code_lines).strip()

    # Just return the raw response if we can't extract
    return response.strip()

def generate_code_baseline(description: str, func_name: str) -> str:
    """Generate code using baseline method (direct LLM generation)."""
    try:
        llm = get_llm()
        prompt = BASELINE_CODE_GEN_PROMPT.format(
            description=description,
            func_name=func_name
        )
        response = llm.generate(prompt, max_new_tokens=512, temperature=0.0)
        return extract_function_code(response)
    except Exception as e:
        print(f"Error generating baseline code: {e}")
        return f"def {func_name}():\n    pass"

def generate_code_with_spec(description: str, specification: dict, func_name: str) -> str:
    """Generate code guided by formal specification (SpecBridge approach)."""
    try:
        llm = get_llm()
        prompt = SPECBRIDGE_CODE_GEN_PROMPT.format(
            precondition=specification.get("precondition", "True"),
            postcondition=specification.get("postcondition", "True"),
            description=description,
            func_name=func_name
        )
        response = llm.generate(prompt, max_new_tokens=512, temperature=0.0)
        return extract_function_code(response)
    except Exception as e:
        print(f"Error generating spec-guided code: {e}")
        return f"def {func_name}():\n    pass"

def refine_code_with_counterexample(
    description: str,
    specification: dict,
    previous_code: str,
    error: str,
    counterexample: dict,
    func_name: str
) -> str:
    """Refine code using counterexample feedback."""
    try:
        llm = get_llm()
        prompt = REFINEMENT_PROMPT.format(
            error=error,
            counterexample=json.dumps(counterexample),
            description=description,
            precondition=specification.get("precondition", "True"),
            postcondition=specification.get("postcondition", "True"),
            previous_code=previous_code
        )
        response = llm.generate(prompt, max_new_tokens=512, temperature=0.0)
        return extract_function_code(response)
    except Exception as e:
        print(f"Error refining code: {e}")
        return previous_code
