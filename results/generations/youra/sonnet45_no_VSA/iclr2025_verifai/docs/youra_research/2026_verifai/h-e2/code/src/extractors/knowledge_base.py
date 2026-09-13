"""Predefined error categories from verifier documentation.

This module contains error categories extracted from:
- Frama-C WP VC API: https://frama-c.com/api/frama-c-wp/Wp/VC/index.html
- Dafny Error Docs: https://dafny.org/v3.12.0/HowToFAQ/Errors
- Why3 Model_parser API: https://why3.org/api/Model_parser.html

For the PoC, we use a curated subset representing the main error categories.
"""

from typing import Dict, List
from ..data_structures import ErrorCategory


def get_frama_c_categories() -> List[ErrorCategory]:
    """Frama-C WP Verification Condition types."""
    return [
        ErrorCategory(
            verifier="frama-c",
            category_name="precondition_holds",
            description="Function precondition must hold at call site",
            source="documentation",
            examples=["requires clause verification"]
        ),
        ErrorCategory(
            verifier="frama-c",
            category_name="postcondition_holds",
            description="Function postcondition must hold at return",
            source="documentation",
            examples=["ensures clause verification"]
        ),
        ErrorCategory(
            verifier="frama-c",
            category_name="loop_invariant_preservation",
            description="Loop invariant must be preserved across iterations",
            source="documentation",
            examples=["loop invariant induction"]
        ),
        ErrorCategory(
            verifier="frama-c",
            category_name="loop_invariant_establishment",
            description="Loop invariant must hold on entry",
            source="documentation",
            examples=["loop invariant base case"]
        ),
        ErrorCategory(
            verifier="frama-c",
            category_name="memory_access_valid",
            description="Pointer dereference must be valid",
            source="documentation",
            examples=["valid memory access check"]
        ),
        ErrorCategory(
            verifier="frama-c",
            category_name="memory_access_initialized",
            description="Memory location must be initialized before read",
            source="documentation",
            examples=["initialized value check"]
        ),
        ErrorCategory(
            verifier="frama-c",
            category_name="array_index_bound",
            description="Array index must be within bounds",
            source="documentation",
            examples=["index_bound check"]
        ),
        ErrorCategory(
            verifier="frama-c",
            category_name="integer_overflow",
            description="Arithmetic operation must not overflow",
            source="documentation",
            examples=["signed_overflow, unsigned_overflow"]
        ),
        ErrorCategory(
            verifier="frama-c",
            category_name="division_by_zero",
            description="Division denominator must be non-zero",
            source="documentation",
            examples=["div_by_zero check"]
        ),
        ErrorCategory(
            verifier="frama-c",
            category_name="assert_holds",
            description="Program assertion must be verified",
            source="documentation",
            examples=["assert clause"]
        ),
        ErrorCategory(
            verifier="frama-c",
            category_name="assigns_clause",
            description="Function only modifies specified locations",
            source="documentation",
            examples=["assigns verification"]
        ),
        ErrorCategory(
            verifier="frama-c",
            category_name="variant_decrease",
            description="Loop variant must decrease to ensure termination",
            source="documentation",
            examples=["decreases clause"]
        ),
    ]


def get_dafny_categories() -> List[ErrorCategory]:
    """Dafny verification error types."""
    return [
        ErrorCategory(
            verifier="dafny",
            category_name="precondition_violation",
            description="Caller does not satisfy function precondition",
            source="documentation",
            examples=["requires clause not met"]
        ),
        ErrorCategory(
            verifier="dafny",
            category_name="postcondition_violation",
            description="Function implementation does not satisfy postcondition",
            source="documentation",
            examples=["ensures clause not met"]
        ),
        ErrorCategory(
            verifier="dafny",
            category_name="loop_invariant_on_entry",
            description="Loop invariant does not hold before first iteration",
            source="documentation",
            examples=["invariant base case failure"]
        ),
        ErrorCategory(
            verifier="dafny",
            category_name="loop_invariant_maintenance",
            description="Loop body does not maintain invariant",
            source="documentation",
            examples=["invariant induction failure"]
        ),
        ErrorCategory(
            verifier="dafny",
            category_name="assertion_failure",
            description="Assert statement cannot be proved",
            source="documentation",
            examples=["assert predicate false"]
        ),
        ErrorCategory(
            verifier="dafny",
            category_name="index_out_of_range",
            description="Sequence or array index out of bounds",
            source="documentation",
            examples=["index >= length"]
        ),
        ErrorCategory(
            verifier="dafny",
            category_name="null_dereference",
            description="Dereferencing potentially null reference",
            source="documentation",
            examples=["object might be null"]
        ),
        ErrorCategory(
            verifier="dafny",
            category_name="division_by_zero_error",
            description="Division or modulo by zero",
            source="documentation",
            examples=["divisor is zero"]
        ),
        ErrorCategory(
            verifier="dafny",
            category_name="decreases_not_satisfied",
            description="Termination metric does not decrease",
            source="documentation",
            examples=["decreases clause not met"]
        ),
        ErrorCategory(
            verifier="dafny",
            category_name="type_constraint_violation",
            description="Value does not satisfy subset type constraint",
            source="documentation",
            examples=["newtype constraint not met"]
        ),
        ErrorCategory(
            verifier="dafny",
            category_name="modifies_clause_violation",
            description="Method modifies frame outside specification",
            source="documentation",
            examples=["modifies clause not respected"]
        ),
    ]


def get_why3_categories() -> List[ErrorCategory]:
    """Why3 verification error types."""
    return [
        ErrorCategory(
            verifier="why3",
            category_name="precondition_failure",
            description="Function precondition not satisfied",
            source="documentation",
            examples=["requires not met"]
        ),
        ErrorCategory(
            verifier="why3",
            category_name="postcondition_failure",
            description="Function postcondition not established",
            source="documentation",
            examples=["ensures not met"]
        ),
        ErrorCategory(
            verifier="why3",
            category_name="loop_invariant_init",
            description="Loop invariant does not hold initially",
            source="documentation",
            examples=["invariant establishment failure"]
        ),
        ErrorCategory(
            verifier="why3",
            category_name="loop_invariant_preservation",
            description="Loop invariant not preserved by loop body",
            source="documentation",
            examples=["invariant preservation failure"]
        ),
        ErrorCategory(
            verifier="why3",
            category_name="assertion_failure",
            description="Assertion cannot be proved",
            source="documentation",
            examples=["assert fails"]
        ),
        ErrorCategory(
            verifier="why3",
            category_name="array_access_bounds",
            description="Array access out of bounds",
            source="documentation",
            examples=["index out of range"]
        ),
        ErrorCategory(
            verifier="why3",
            category_name="integer_overflow_error",
            description="Integer arithmetic overflow",
            source="documentation",
            examples=["overflow in arithmetic"]
        ),
        ErrorCategory(
            verifier="why3",
            category_name="division_by_zero_check",
            description="Division by zero check failure",
            source="documentation",
            examples=["div_by_zero"]
        ),
        ErrorCategory(
            verifier="why3",
            category_name="variant_decrease_failure",
            description="Variant does not decrease for termination",
            source="documentation",
            examples=["variant not decreasing"]
        ),
        ErrorCategory(
            verifier="why3",
            category_name="type_invariant_violation",
            description="Type invariant not maintained",
            source="documentation",
            examples=["type invariant broken"]
        ),
    ]


def get_all_categories() -> Dict[str, List[ErrorCategory]]:
    """Get all error categories organized by verifier."""
    return {
        "frama-c": get_frama_c_categories(),
        "dafny": get_dafny_categories(),
        "why3": get_why3_categories()
    }
