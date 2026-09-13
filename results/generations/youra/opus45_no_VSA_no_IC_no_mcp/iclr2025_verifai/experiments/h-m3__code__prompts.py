from errors import StructuredError
from hints import generate_hint

def format_structured_prompt(error: StructuredError, original_code: str) -> str:
    context_str = '\n'.join(error.code_context)
    return f"""Fix the following Python code error.

## Error Information
- Line: {error.line_number}
- Type: {error.error_type}
- Message: {error.error_message}

## Code Context:
{context_str}

## Full Code:
```python
{original_code}
```

Provide the corrected complete code:"""

def format_raw_prompt(raw_output: str, original_code: str) -> str:
    return f"""Fix the following Python code based on the error.

## Compiler Output:
{raw_output}

## Code:
```python
{original_code}
```

Provide the corrected complete code:"""

def format_leveled_prompt(error: StructuredError, original_code: str, level: int) -> str:
    base = format_structured_prompt(error, original_code)
    hint = generate_hint(error, original_code, level)
    if not hint:
        return base
    guidance = f"\n## Fix Guidance\n{hint}\n"
    return base.replace("Provide the corrected complete code:",
                        guidance + "\nProvide the corrected complete code:")

def demo():
    from errors import StructuredError
    err = StructuredError(line_number=5, error_type="IndexError",
                          error_message="list index out of range", code_context=["5: x[10]"])
    code = "x = []\ny = x[10]"
    p0 = format_leveled_prompt(err, code, 0)
    p1 = format_leveled_prompt(err, code, 1)
    assert p0 == format_structured_prompt(err, code)
    assert "Fix Guidance" in p1
    print("prompts.py demo PASS")

if __name__ == "__main__":
    demo()
