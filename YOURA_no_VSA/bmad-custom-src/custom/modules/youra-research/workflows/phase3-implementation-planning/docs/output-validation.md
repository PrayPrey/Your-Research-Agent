# Output Validation Reference

> **Reference File:** Extracted from workflow.md for file size optimization
>
> **Purpose:** Detailed validation logic for post-step auto-check

---

## Required Content Validation Table

| Step | Output File | Required Content | Missing = |
|------|-------------|------------------|-----------|
| Step 3 | 03_architecture.md | `## Codebase Analysis (Serena)` section | **RE-INVOKE AGENT** |
| Step 3 | 03_architecture.md | `Applied:` line (Archon KB pattern) | **RE-INVOKE AGENT** |
| Step 5 | 03_logic.md | `## Codebase Analysis (Serena)` section | **RE-INVOKE AGENT** |
| Step 5 | 03_config.md | `Applied:` line (Archon KB pattern) | **RE-INVOKE AGENT** |

---

## Validation Logic

```python
def validate_agent_output(file_path, required_sections):
    content = Read(file_path)

    for section in required_sections:
        IF section NOT in content:
            # Agent was NOT properly invoked (likely Write tool bypass)
            Delete(file_path) # Remove invalid output
            RETURN "FAIL - RE-INVOKE AGENT"

    RETURN "PASS"
```

---

## Validation Failure Handling

**IF validation fails:**
1. Delete the invalid output file
2. RE-INVOKE the Task tool with same parameters
3. Repeat until validation passes (max 2 retries)

---

## Why Validation Matters

- Ensures agents actually used MCP tools (Archon KB, Serena)
- Prevents direct Write tool bypass in UNATTENDED mode
- Guarantees output quality through pattern verification
