"""LLM Client for ACSL specification generation and refinement."""

import os
import time
from typing import List, Dict, Optional
from dataclasses import dataclass
from anthropic import Anthropic
import re


@dataclass
class ACSLSpec:
    """ACSL-annotated C program."""
    annotated_code: str
    preconditions: List[str]
    postconditions: List[str]
    loop_invariants: List[str]
    assertions: List[str]


class SpecificationGenerator:
    """Generate initial ACSL specifications from C code."""

    def __init__(self, api_key: str, model: str = "claude-opus-4-5"):
        """Initialize with Anthropic API client."""
        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.few_shot_examples = self._load_few_shot_examples()

    def generate_initial_spec(
        self,
        c_code: str,
        verification_goal: str = "functional correctness"
    ) -> ACSLSpec:
        """
        Generate ACSL specification from unannotated C code.

        Args:
            c_code: str - Unannotated C program
            verification_goal: str - What to verify (default: functional correctness)

        Returns:
            ACSLSpec with annotated code and extracted clauses
        """
        prompt = self._construct_generation_prompt(c_code, verification_goal)

        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            temperature=0.7,
            messages=[{"role": "user", "content": prompt}]
        )

        annotated_code = self._extract_code_from_response(response.content)
        return self._parse_acsl_spec(annotated_code)

    def _construct_generation_prompt(self, c_code: str, goal: str) -> str:
        """Build prompt with ACSL grammar + few-shot examples."""
        return f"""Generate ACSL formal specification for this C program.

VERIFICATION GOAL: {goal}

ACSL GRAMMAR (Essential Constructs):
- Function contracts: /*@ requires P; ensures Q; */
- Loop invariants: /*@ loop invariant I; */
- Assertions: /*@ assert P; */
- Logic functions: /*@ logic type name(args) = expr; */

FEW-SHOT EXAMPLES:
{self.few_shot_examples}

C PROGRAM TO ANNOTATE:
```c
{c_code}
```

REQUIREMENTS:
1. Add preconditions (requires) for all function parameters
2. Add postconditions (ensures) for return values and side effects
3. Add loop invariants for all loops
4. Use ACSL \\result for return value in postconditions
5. Use \\valid(ptr) for pointer validity
6. Use \\old(x) for pre-state values in postconditions

OUTPUT FORMAT:
Return ONLY the C code with ACSL annotations as comments.
"""

    def _load_few_shot_examples(self) -> str:
        """Load 3-5 examples from ACSL-by-Example."""
        return """
EXAMPLE 1: Binary Search
```c
/*@ requires n >= 0;
  @ requires \\valid_read(arr + (0..n-1));
  @ requires \\forall integer i, j; 0 <= i < j < n ==> arr[i] <= arr[j];
  @ ensures (\\result >= 0 && \\result < n) ==> arr[\\result] == value;
  @ ensures (\\result == -1) ==> \\forall integer i; 0 <= i < n ==> arr[i] != value;
  @*/
int binary_search(int *arr, int n, int value) {
    int low = 0, high = n - 1;
    /*@ loop invariant 0 <= low && high < n;
      @ loop invariant \\forall integer i; 0 <= i < low || high < i < n ==> arr[i] != value;
      @ loop variant high - low;
      @*/
    while (low <= high) {
        int mid = low + (high - low) / 2;
        if (arr[mid] == value) return mid;
        if (arr[mid] < value) low = mid + 1;
        else high = mid - 1;
    }
    return -1;
}
```

EXAMPLE 2: Maximum Element
```c
/*@ requires n > 0;
  @ requires \\valid_read(arr + (0..n-1));
  @ ensures \\result >= 0 && \\result < n;
  @ ensures \\forall integer i; 0 <= i < n ==> arr[i] <= arr[\\result];
  @*/
int find_max(int *arr, int n) {
    int max_idx = 0;
    /*@ loop invariant 1 <= i <= n;
      @ loop invariant 0 <= max_idx < i;
      @ loop invariant \\forall integer j; 0 <= j < i ==> arr[j] <= arr[max_idx];
      @ loop variant n - i;
      @*/
    for (int i = 1; i < n; i++) {
        if (arr[i] > arr[max_idx]) max_idx = i;
    }
    return max_idx;
}
```
"""

    def _extract_code_from_response(self, content: List) -> str:
        """Extract C code from LLM response (handles markdown blocks)."""
        text = content[0].text
        # Extract code between ```c and ```
        if "```c" in text:
            start = text.find("```c") + 4
            end = text.find("```", start)
            return text[start:end].strip()
        return text.strip()

    def _parse_acsl_spec(self, annotated_code: str) -> ACSLSpec:
        """Parse ACSL clauses from annotated code."""
        # Extract all ACSL comments
        acsl_pattern = r'/\*@(.*?)\*/'
        clauses = re.findall(acsl_pattern, annotated_code, re.DOTALL)

        preconditions = []
        postconditions = []
        loop_invariants = []
        assertions = []

        for clause in clauses:
            if 'requires' in clause:
                preconditions.extend(re.findall(r'requires\s+(.*?);', clause))
            if 'ensures' in clause:
                postconditions.extend(re.findall(r'ensures\s+(.*?);', clause))
            if 'loop invariant' in clause:
                loop_invariants.extend(re.findall(r'loop invariant\s+(.*?);', clause))
            if 'assert' in clause:
                assertions.extend(re.findall(r'assert\s+(.*?);', clause))

        return ACSLSpec(
            annotated_code=annotated_code,
            preconditions=preconditions,
            postconditions=postconditions,
            loop_invariants=loop_invariants,
            assertions=assertions
        )
