---
name: archon-research
description: "Search prior cases and best practices using the Archon Knowledge Base. Used in the Phase 1 research workflow."
---

# Archon Knowledge Base Research Skill

## MCP Server Role
⚠️ **ARCHON MCP ONLY** - Use EXCLUSIVELY `mcp__archon__rag_search_knowledge_base`
❌ DO NOT use Semantic Scholar MCP or Exa MCP when this skill is active

## MCP Function Reference
```
mcp__archon__rag_search_knowledge_base(query, match_count)
```

## Hierarchical Search Strategy

### Level 1 - Direct Match
Execute Archon MCP searches with queries:
- "{{key_concept_1}} implementation patterns"
- "{{key_concept_2}} best practices"
- "{{mechanism_name}} failure cases"
- "{{architecture_type}} edge cases"

**For each query:**
1. Call `mcp__archon__rag_search_knowledge_base(query=query, match_count=5)`
2. Parse response JSON
3. Extract: {content, metadata, source_id, relevance_score}
4. Tag result as **[VERIFIED - ARCHON]** if successful
5. Tag result as **[NOT_FOUND - ARCHON]** if no results

### Level 2 - Conceptual Expansion (when Level 1 yields < 3 results)
Agent automatically analyzes and expands concepts:
- **Higher-level concepts**: Auto-derive general categories
  - Example: "local attention" → "attention mechanisms", "selective processing"
- **Lower-level concepts**: Auto-identify specific techniques
  - Example: "memory module" → "external memory", "memory network", "memory bank"
- **Adjacent concepts**: Explore alternative approaches for similar problems
  - Example: "latent vector update" → "state update", "hidden state evolution"

**Re-execute Archon MCP searches with expanded queries**

### Level 3 - Meta Patterns (when Level 2 still yields < 5 results)
Domain-independent general patterns:
- "attention mechanism patterns"
- "memory architecture patterns"
- "compositional learning best practices"
- "hybrid architecture design patterns"

**Re-execute Archon MCP searches with meta pattern queries**

## Processing Protocol

For each level:
1. Execute **Archon MCP** search and collect results
2. Calculate relevance score (0.0 ~ 1.0)
3. Keep only results with threshold ≥ 0.3
4. Tag each result: **[VERIFIED - ARCHON]** + source_id from Archon response
5. If goal achieved (minimum 5 patterns), proceed to next step
6. If not achieved, expand to next level

## Fallback Protocol

When search fails (< 3 results across all levels):
- Utilize local knowledge and logical reasoning
- Mark results as **[INFERRED]** (NOT [VERIFIED])
- Record explicitly: "No Archon results found, inferred from general knowledge"

## Verification Protocol

1. ✅ All results MUST come from `mcp__archon__rag_search_knowledge_base` calls
2. ✅ Each result MUST be tagged **[VERIFIED - ARCHON]** or **[INFERRED]**
3. ✅ Include Archon source_id/KB Entry ID for each verified result
4. ❌ DO NOT use Semantic Scholar or Exa in this step
5. ❌ DO NOT mark inferred results as [VERIFIED]

## Output Structure

Agent structures collected information:
- **Direct Cases**: Cases directly related to the question (tagged **[VERIFIED - ARCHON]**)
- **Similar Cases**: Cases with similar architectural challenges (tagged **[VERIFIED - ARCHON]**)
- **Pattern Cases**: Generalized design patterns (tagged **[VERIFIED - ARCHON]**)
- **Inferred Patterns**: Patterns inferred when search fails (tagged **[INFERRED]**)

## Template Output

```markdown
## Past Cases & Best Practices (via Archon)

**MCP Server Used:** Archon Knowledge Base (`mcp__archon__rag_search_knowledge_base`)
**Total Queries:** X queries across X levels
**Results Found:** X verified cases + X inferred patterns

### Direct Implementations
**[VERIFIED - ARCHON]** Case 1: {{case_title}}
- Source: Archon Knowledge Base (KB Entry ID: {{kb_entry_id}})
- Search Query: "{{query_used}}"
- Search Level: Level {{level_number}}
- Relevance Score: {{relevance_score}}
- Relevance: Direct match to {{research_question}}
- Key insights: {{key_insights}}

### Similar Architectural Patterns
**[VERIFIED - ARCHON]** Pattern 1: {{pattern_name}}
- Source: Archon Knowledge Base (KB Entry ID: {{kb_entry_id}})
- Search Query: "{{query_used}}"
- Implementation approach: {{approach_description}}
- Relevance: Similar to {{key_concept}}
- Common pitfalls: {{pitfalls}}

### Design Patterns Found
**[VERIFIED - ARCHON]** Pattern 1: {{design_pattern_name}}
- Source: Archon Knowledge Base (KB Entry ID: {{kb_entry_id}})
- Search Query: "{{query_used}}"
- Pattern description: {{description}}
- Application to research question: {{application}}

### Code Examples Found
**[VERIFIED - ARCHON]** Example 1: {{example_title}}
- Source: Archon Knowledge Base (KB Entry ID: {{kb_entry_id}})
- Search Query: "{{query_used}}"
```python
# Retrieved code snippet from Archon
{{code_snippet}}
```
- Relevance: {{relevance_description}}

### Inferred Patterns (if Archon search yielded < 3 results)
**[INFERRED]** Pattern 1: {{inferred_pattern}}
- Source: General knowledge (Archon search yielded no results)
- Reasoning: {{inference_reasoning}}
- Note: Not verified through Archon knowledge base
```
