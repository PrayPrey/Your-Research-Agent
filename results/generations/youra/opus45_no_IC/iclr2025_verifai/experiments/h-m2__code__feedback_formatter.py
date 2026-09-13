def format_issues_for_prompt(bandit_issues: list[dict], pylint_issues: list[dict]) -> str:
    lines = []
    for issue in bandit_issues:
        line_no = issue.get("line_number", 0)
        desc = issue.get("issue_text", "Unknown security issue")
        lines.append((line_no, f"Line {line_no}: [SECURITY] {desc}"))
    for issue in pylint_issues:
        line_no = issue.get("line", 0)
        desc = issue.get("message", "Unknown reliability issue")
        lines.append((line_no, f"Line {line_no}: [RELIABILITY] {desc}"))
    lines.sort(key=lambda x: x[0])
    return "\n".join(text for _, text in lines) or "No issues found."


def build_refine_prompt(original_prompt: str, code: str, feedback: str) -> str:
    return (
        f"{original_prompt}\n\n"
        f"Current code:\n```python\n{code}\n```\n\n"
        f"Static analysis found these issues:\n{feedback}\n\n"
        f"Fix the issues above while preserving functionality. Return only the corrected Python code."
    )
