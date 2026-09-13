---
name: exa-search
description: "Search GitHub repositories, tutorials, and implementation code using Exa MCP. Used in Phase 1 research workflows."
---

# Exa GitHub and Implementation Resources Skill

## MCP Server Role
⚠️ **EXA MCP ONLY** - Use EXCLUSIVELY `mcp__exa__web_search_exa` and `mcp__exa__get_code_context_exa`
❌ DO NOT use Archon MCP or Semantic Scholar MCP when this skill is active

## MCP Function Reference
```
mcp__exa__web_search_exa(query, numResults, type)  - For GitHub repos and web resources
mcp__exa__get_code_context_exa(query, tokensNum)   - For code examples and documentation
```

## Implementation Search Strategy

### Priority 1 - Specific Implementations
**Queries:**
- "{{key_concept_1}} {{key_concept_2}} implementation github"
- "{{mechanism_name}} pytorch implementation github"
- "{{architecture_type}} code github"

**For each query:**
1. Call `mcp__exa__web_search_exa(query=query, numResults=8, type="auto")`
2. Parse response: `{results: [{title, url, text, score}]}`
3. Filter GitHub URLs: `url.contains("github.com")`
4. Extract: `{repo_name, stars, language, last_updated, url}`
5. Tag as **[VERIFIED - EXA]** with full URL
6. Evaluation criteria: Stars > 50 OR updated within last 6 months

### Priority 2 - Component Implementations
**Queries:**
- "{{component_1}} implementation github"
- "{{component_2}} pytorch github"
- "{{technique}} code examples"

**Execute Exa searches, focus on modular implementations**

### Priority 3 - Tutorials and Guides
**Queries:**
- "{{research_topic}} tutorial"
- "how to implement {{key_concept}}"
- "{{mechanism}} step by step"

**For each query:**
1. Call `mcp__exa__web_search_exa(query=query, numResults=5, type="deep")`
2. Filter credible sources: Medium, Towards Data Science, official docs
3. Tag as **[VERIFIED - EXA - TUTORIAL]**

### Priority 4 - Code Context Search
**For implementation details:**
1. Call `mcp__exa__get_code_context_exa(query="{{key_concept}} implementation", tokensNum=5000)`
2. Extract code examples, API usage, architectural patterns
3. Tag as **[VERIFIED - EXA - CODE_CONTEXT]**

### Priority 5 - Similar Hybrid Approaches
- Search for implementations combining similar concepts
- Look for architectural patterns that solve related problems
- Find code examples of memory mechanisms, attention variants, etc.

## Quality Criteria

- **Code**: README completeness, license, recent activity
- **Tutorial**: Step-by-step explanation, code examples included
- **Demo**: Executable, reproducible
- **Relevance**: How directly applicable to {{research_question}}

## Verification Protocol

1. ✅ All results MUST come from Exa MCP function calls
2. ✅ Each result MUST be tagged **[VERIFIED - EXA]**, **[VERIFIED - EXA - TUTORIAL]**, or **[VERIFIED - EXA - CODE_CONTEXT]**
3. ✅ Include full URL for each resource
4. ✅ For GitHub repos: Extract stars, language, last_updated
5. ❌ DO NOT use Archon or Semantic Scholar in this step
6. ❌ DO NOT include resources without URL verification

## Fallback Protocol (if results < 3)

1. **Generalize search terms:**
   - Specific technique → Higher category
   - Search for component implementations separately
   - Re-execute Exa search with broader query

2. **Explore similar implementations:**
   - Other projects addressing similar architectural challenges
   - Partially related code snippets

3. **Provide alternatives (if Exa fails):**
   - "Try GitHub search directly: {{github_query}}"
   - "Recommend checking awesome-{{domain}} list"
   - "Search {{key_concept}} on Papers with Code"

4. **Framework documentation:**
   - Use `get_code_context_exa` for official documentation
   - Provide API reference for required components

5. **Minimum assurance:**
   - Include high-quality resources even if < 3
   - Mark explicitly with **[LIMITED_RESULTS - EXA]** tag

## Template Output

```markdown
## Implementation Resources (via Exa)

**MCP Server Used:** Exa Search (`mcp__exa__web_search_exa`, `mcp__exa__get_code_context_exa`)
**Total Queries:** X queries across X priorities
**Results Found:** X GitHub repos + Y tutorials + Z code contexts

### Directly Relevant Implementations

1. **[VERIFIED - EXA]** {{repo_owner}}/{{repo_name}}
   - URL: {{github_url}}
   - Stars: {{star_count}}
   - Language: {{primary_language}} ({{framework}})
   - Search Query: "{{query_used}}"
   - Priority Level: Priority {{priority_number}}
   - Relevance: Implements {{key_concept_1}}
   - Key Features: {{features_list}}
   - Adaptability: {{adaptability_description}}
   - Last Updated: {{last_updated_date}}
   - Retrieved via: `mcp__exa__web_search_exa(query="{{query}}", numResults=8)`

2. **[VERIFIED - EXA]** {{repo_owner_2}}/{{repo_name_2}}
   - URL: {{github_url_2}}
   - Stars: {{star_count}}
   - Language: {{primary_language}}
   - Search Query: "{{query_used}}"
   - Relevance: Complete implementation of {{key_concept_2}}
   - Integration potential: {{integration_notes}}

### Component Implementations

1. **[VERIFIED - EXA]** {{component_repo}}
   - URL: {{github_url}}
   - Stars: {{star_count}}
   - Search Query: "{{query_used}}"
   - Priority Level: Priority 2
   - Relevance: Implements {{component_name}}
   - Integration potential: {{integration_description}}
   - Retrieved via: `mcp__exa__web_search_exa(query="{{query}}", numResults=8)`

### Tutorial Resources

1. **[VERIFIED - EXA - TUTORIAL]** "{{tutorial_title}}"
   - Source: {{platform_name}} (Medium/Towards Data Science/Official Docs)
   - URL: {{tutorial_url}}
   - Search Query: "{{query_used}}"
   - Priority Level: Priority 3
   - Relevance: Explains {{key_concept}}
   - Key Insights: {{insights}}
   - Retrieved via: `mcp__exa__web_search_exa(query="{{query}}", numResults=5, type="deep")`

### Code Context Analysis

**[VERIFIED - EXA - CODE_CONTEXT]** Implementation patterns for {{key_concept}}:
- Retrieved via: `mcp__exa__get_code_context_exa(query="{{key_concept}} implementation", tokensNum=5000)`
- Common patterns: {{patterns_found}}
- API usage examples: {{api_examples}}
- Architectural insights: {{architecture_notes}}

### Framework Analysis
- Common implementation patterns for {{key_concept}}: {{patterns}}
- Framework preferences: PyTorch (X repos) vs TensorFlow (Y repos) vs JAX (Z repos)
- Typical architectural structure: {{structure_description}}
- Adaptability to research question: {{adaptability_assessment}}

### Limited Results Notice (if applicable)
**[LIMITED_RESULTS - EXA]** Only {{count}} resources found
- Fallback recommendations:
  - GitHub search: {{github_query}}
  - Awesome list: {{awesome_list_url}}
  - Papers with Code: {{paperswithcode_query}}
```
