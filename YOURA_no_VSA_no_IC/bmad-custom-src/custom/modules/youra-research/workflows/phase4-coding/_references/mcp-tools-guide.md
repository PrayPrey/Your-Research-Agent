# MCP Tools Guide

> **Reference Document** - Used by step-02-coder-loop.md and step-05-experiment-execute.md

---

## SDD Phase Tool Mapping

| SDD Phase | Primary Tools | Purpose |
|-----------|---------------|---------|
| 📋 **SPEC** | `Read()` | Read and understand specifications |
| 🧪 **TEST** | `Read()` + Pydantic | Generate tests from spec understanding |
| ⚙️ **IMPL** | Archon KB → Exa fallback | Find implementation patterns |
| ✅ **VERIFY** | Bash (pytest) + Serena | Run tests, verify spec compliance |

---

## CRITICAL: Mandatory MCP Usage

Every code generation task MUST use these tools:

### Archon MCP (Knowledge + Task Management) - PRIMARY

| Tool | Purpose | When to Use |
|------|---------|-------------|
| `mcp__archon__find_tasks` | Query tasks by status | Get todo tasks, read error info |
| `mcp__archon__manage_task` | Update task status | Transition todo → doing → review |
| `mcp__archon__rag_search_knowledge_base` | Search implementation patterns | **BEFORE every implementation!** |
| `mcp__archon__rag_search_code_examples` | Search code examples | Find PyTorch patterns, best practices |

### Serena MCP (Code Analysis) - PRIMARY

| Tool | Purpose | When to Use |
|------|---------|-------------|
| `mcp__serena__get_symbols_overview` | Get file structure | Before editing existing files |
| `mcp__serena__find_symbol` | Find functions/classes | Locate code to modify or reference |
| `mcp__serena__insert_after_symbol` | Insert new code | Add new methods, functions |
| `mcp__serena__replace_symbol_body` | Modify existing code | Fix errors, update implementations |
| `mcp__serena__find_referencing_symbols` | Check dependencies | Understand import relationships |
| `mcp__serena__search_for_pattern` | Find code patterns | Locate similar implementations |
| `mcp__serena__list_dir` | List directory | Understand project structure |

### Exa MCP (Fallback - MANDATORY when Archon insufficient!)

| Tool | Purpose | When to Use |
|------|---------|-------------|
| `mcp__exa__get_code_context_exa` | Implementation patterns, code examples | **MANDATORY** when Archon KB insufficient/irrelevant |
| `mcp__exa__web_search_exa` | GitHub examples, latest docs, tutorials | **MANDATORY** for specialized domains or recency needs |

## Archon → Exa Fallback Policy

```
AFTER every Archon KB search:

archon_results = mcp__archon__rag_search_knowledge_base(query=...)

# Evaluate result quality
is_sufficient = archon_results.count >= 3
is_relevant = results contain concrete code AND directly answer the query
is_specialized = query involves niche libraries, advanced techniques, or domain-specific implementations
needs_recency = query mentions latest/version/recent OR involves frequently-changing APIs

IF NOT is_sufficient OR NOT is_relevant OR is_specialized OR needs_recency:
    # MANDATORY: Use Exa as fallback
    exa_code = mcp__exa__get_code_context_exa(query=same_query)
    exa_web = mcp__exa__web_search_exa(query="{query} implementation example")

    Combine: archon_results + exa_code + exa_web
    Log: "Archon insufficient/inadequate → Exa fallback used"

MANDATORY Exa Triggers (Generalized - NO EXCEPTIONS):
- Archon KB results < 3
- Archon KB results are generic/conceptual-only (no concrete code)
- Specialized/niche domain query (non-standard libraries, advanced techniques)
- Recency required (API changes or compatibility constraints)
- Complex implementation patterns (custom kernels, distributed, optimization)
- Error resolution after Archon KB failed
- Query needs code but Archon returns only explanations
```

## Exa Fallback Policy Summary (Generalized Criteria)

```
MANDATORY Exa Usage Triggers (NO EXCEPTIONS):

1. INSUFFICIENT COUNT
   - Archon KB search returns < 3 results

2. LOW RELEVANCE
   - Archon KB results are generic/conceptual without concrete code
   - Results don't directly answer the query

3. SPECIALIZED/NICHE DOMAIN (General Heuristics)
   - Library not part of standard PyTorch/TensorFlow/JAX/NumPy/SciPy core
   - Involves specialized data structures (graph, temporal, geometric, sparse)
   - Library has limited mainstream documentation or frequent API changes
   - Query involves cutting-edge research techniques

4. RECENCY REQUIRED
   - Query involves latest versions or recent API changes
   - Suspected compatibility issues

5. COMPLEX IMPLEMENTATION
   - Query requires advanced patterns (custom kernels, distributed, optimization)

6. ERROR RESOLUTION FAILED
   - Archon KB suggestions did not resolve the error

7. CODE-HEAVY QUERY
   - Query needs implementation but Archon returns only explanations
```
