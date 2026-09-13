---
name: scholar-search
description: "Academic paper search and citation network analysis using the Semantic Scholar MCP. Used in the Phase 1 research workflow."
---

# Semantic Scholar Paper Search Skill

## MCP Server Role
⚠️ **SEMANTIC SCHOLAR MCP ONLY** - Use EXCLUSIVELY `mcp__hamid-vakilzadeh-mcpsemanticscholar__*` functions
❌ DO NOT use Archon MCP or Exa MCP when this skill is active

## MCP Function Reference
```
mcp__hamid-vakilzadeh-mcpsemanticscholar__paper_relevance_search(query, limit, year, fields)
mcp__hamid-vakilzadeh-mcpsemanticscholar__paper_details(paper_id, fields)
mcp__hamid-vakilzadeh-mcpsemanticscholar__paper_citations(paper_id, limit)
mcp__hamid-vakilzadeh-mcpsemanticscholar__paper_references(paper_id, limit)
```

## Targeted Search Strategy

### Round 1 - Question-Focused Search
Use queries generated from research question decomposition.

**For each query:**
1. Call `mcp__hamid-vakilzadeh-mcpsemanticscholar__paper_relevance_search(query=query, limit=5, year="2020-", fields=["title", "authors", "year", "citationCount", "abstract", "paperId", "url"])`
2. Parse response JSON: `{total, data: [{paperId, title, authors, year, citationCount, abstract, url}]}`
3. Filter: citation > 10 OR year >= 2023
4. Tag each result as **[VERIFIED - SCHOLAR]** + Semantic Scholar paperId
5. Store: `{paperId, title, authors, year, citations, abstract, url, query_used}`

**Priority Order:**
- Priority 1: Papers directly addressing similar research questions
- Priority 2: Papers on individual concepts ({{key_concept_1}}, {{key_concept_2}})
- Goal: Minimum 10 relevant papers

### Round 2 - Reference Paper Citation Network (if reference papers provided)
**For each reference paper:**
1. Get paperId using `paper_title_search` or from provided ID
2. Call `paper_citations(paper_id=paperId, limit=10)` → Papers citing this work
3. Call `paper_references(paper_id=paperId, limit=10)` → Papers cited by this work
4. Tag each as **[VERIFIED - SCHOLAR - CITATION_NETWORK]**
5. Identify common authors and research lineage

### Round 3 - Expanded Conceptual Search (when Round 1-2 yields < 10 papers)
- Synonym/abbreviation transformation
- Broader conceptual terms
- Related problem domains
- Time range expansion: `year="2018-"` instead of `"2020-"`

**Re-execute Semantic Scholar MCP searches with expanded queries**

### Round 4 - Foundational Papers
- Search for survey papers: query + "survey" or "review"
- Identify seminal work: Sort by citationCount descending
- Find tutorial papers: query + "tutorial" or "introduction"

## Relevance Scoring

- Direct relevance to {{research_question}}: Weight 1.0
- Addresses {{detailed_question}}: Weight 0.9
- Related to reference paper concepts: Weight 0.8
- General domain papers: Weight 0.5

**Citation-based prioritization:**
- Citation count × Recency factor × Relevance weight
- Recency factor = 1.0 (2024-2025), 0.8 (2022-2023), 0.6 (earlier)

## Verification Protocol

1. ✅ All results MUST come from Semantic Scholar MCP function calls
2. ✅ Each result MUST be tagged **[VERIFIED - SCHOLAR]** with paperId
3. ✅ Include Semantic Scholar paperId and URL for each paper
4. ✅ Extract full metadata: title, authors, year, citations, abstract, URL
5. ❌ DO NOT use Archon or Exa in this step
6. ❌ DO NOT include papers without paperId verification

## Fallback Protocol (if results < 5)

1. **Query reconstruction:**
   - Technical terms → General terms
   - Specific → General concepts
   - Re-execute Semantic Scholar search with broader query

2. **Alternative search suggestions (if Semantic Scholar fails):**
   - "Recommend direct arXiv search with keywords: {{suggested_keywords}}"
   - "Google Scholar search query: {{alternative_query}}"

3. **Preprint server guidance:**
   - Recommend field-specific servers: arXiv, bioRxiv, SSRN, etc.

4. **Minimum quality assurance:**
   - Include all found papers even if < 5
   - Mark explicitly with **[LIMITED_RESULTS - SCHOLAR]** tag

## Template Output

```markdown
## Academic Literature Review (via Semantic Scholar)

**MCP Server Used:** Semantic Scholar (`mcp__hamid-vakilzadeh-mcpsemanticscholar__paper_relevance_search`)
**Total Queries:** X queries across X rounds
**Results Found:** X papers (Y directly relevant, Z foundational, W from citation network)

### Directly Relevant Papers

1. **[VERIFIED - SCHOLAR]** "{{paper_title}}" ({{year}})
   - Authors: {{author_list}}
   - Citations: {{citation_count}}
   - Semantic Scholar ID: {{paper_id}}
   - URL: {{paper_url}}
   - Search Query: "{{query_used}}"
   - Search Round: Round {{round_number}}
   - Relevance: Directly addresses {{research_question}}
   - Key Contribution: {{contribution}}
   - Abstract: {{abstract}}

2. **[VERIFIED - SCHOLAR]** "{{paper_title_2}}" ({{year}})
   - Authors: {{author_list}}
   - Citations: {{citation_count}}
   - Semantic Scholar ID: {{paper_id}}
   - URL: {{paper_url}}
   - Search Query: "{{query_used}}"
   - Relevance: Addresses similar architectural challenge
   - Key Contribution: {{contribution}}

### Foundational Papers

1. **[VERIFIED - SCHOLAR]** "{{foundational_paper_title}}" ({{year}})
   - Authors: {{author_list}}
   - Citations: {{citation_count}}
   - Semantic Scholar ID: {{paper_id}}
   - URL: {{paper_url}}
   - Search Query: "{{query_used}}"
   - Search Round: Round 4 (Foundational)
   - Relevance: Establishes {{key_concept_1}}
   - Key insights: {{insights}}

### Related Work (from Reference Papers)

**[VERIFIED - SCHOLAR - CITATION_NETWORK]** Papers citing {{reference_paper_1}}:

1. "{{citing_paper_title}}" ({{year}})
   - Authors: {{author_list}}
   - Semantic Scholar ID: {{paper_id}}
   - URL: {{paper_url}}
   - Retrieved via: `paper_citations(paper_id={{reference_paper_id}})`
   - Common themes: {{themes}}

**[VERIFIED - SCHOLAR - CITATION_NETWORK]** Papers cited by {{reference_paper_1}}:

1. "{{cited_paper_title}}" ({{year}})
   - Authors: {{author_list}}
   - Semantic Scholar ID: {{paper_id}}
   - URL: {{paper_url}}
   - Retrieved via: `paper_references(paper_id={{reference_paper_id}})`
   - Evolution of ideas: {{evolution}}

### Citation Network Analysis
- Most influential work: {{most_influential_paper}} ({{citation_count}} citations)
- Recent developments: {{recent_trends}}
- Research lineage: [Paper A] → [Paper B] → [Paper C] → [Reference Paper]
- Connection to reference papers: {{connection_description}}

### Limited Results Notice (if applicable)
**[LIMITED_RESULTS - SCHOLAR]** Only {{count}} papers found
- Fallback recommendations:
  - arXiv search: {{arxiv_query}}
  - Google Scholar query: {{google_scholar_query}}
```
