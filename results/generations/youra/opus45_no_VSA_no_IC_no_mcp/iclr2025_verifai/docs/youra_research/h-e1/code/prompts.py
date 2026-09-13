from errors import StructuredError

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
