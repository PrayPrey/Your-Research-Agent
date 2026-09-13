---
name: clearthought-reasoning
---

# ClearThought Advanced Reasoning Skill

## MCP Server Role
**CLEARTHOUGHT MCP ONLY** - Use EXCLUSIVELY `mcp__clearThought__*` functions for structured reasoning
This skill provides 7 specialized reasoning tools for different analytical needs.

## Available Tools Overview

| Tool | Purpose | When to Use |
|------|---------|-------------|
| `sequentialthinking` | Multi-step analysis | Complex decomposition requiring revision |
| `mentalmodel` | First principles analysis | Breaking down to fundamental components |
| `scientificmethod` | Hypothesis validation | Designing verification experiments |
| `structuredargumentation` | Dialectical reasoning | Thesis-antithesis-synthesis analysis |
| `collaborativereasoning` | Multi-expert discussion | Gathering diverse expert perspectives |
| `metacognitivemonitoring` | Quality assessment | Evaluating confidence and completeness |
| `decisionframework` | Decision analysis | Comparing options with criteria |

---

## Tool 1: Sequential Thinking

**Function:** `mcp__clearThought__sequentialthinking`

**Purpose:** Complex multi-step analysis with ability to revise earlier thoughts

**When to Use:**
- Opportunity derivation from research gaps
- Step-by-step causal chain analysis
- Problems requiring iterative refinement

**Parameters:**
```json
{
  "thought": "string - Current reasoning step content",
  "thoughtNumber": "integer - Current step (1-indexed)",
  "totalThoughts": "integer - Expected total steps (minimum 5 for complex)",
  "nextThoughtNeeded": "boolean - true if more steps needed"
}
```

**Example Usage:**
```json
// Step 1
{
  "thought": "First, I analyze the research gap: X lacks capability Y...",
  "thoughtNumber": 1,
  "totalThoughts": 5,
  "nextThoughtNeeded": true
}

// Step 2
{
  "thought": "Building on step 1, the opportunity is...",
  "thoughtNumber": 2,
  "totalThoughts": 5,
  "nextThoughtNeeded": true
}

// ... continue until final step
{
  "thought": "Synthesizing all previous thoughts, the conclusion is...",
  "thoughtNumber": 5,
  "totalThoughts": 5,
  "nextThoughtNeeded": false
}
```

---

## Tool 2: Mental Model (First Principles)

**Function:** `mcp__clearThought__mentalmodel`

**Purpose:** Decompose problems to fundamental, irreducible components

**When to Use:**
- Hierarchical hypothesis decomposition
- Identifying core assumptions
- Building causal chains from fundamentals

**Parameters:**
```json
{
  "modelName": "first_principles",
  "problem": "string - The problem/hypothesis to decompose",
  "reasoning": "string - Approach description",
  "steps": ["array of strings - Decomposition steps"],
  "conclusion": "string - Final synthesis"
}
```

**Example Usage:**
```json
{
  "modelName": "first_principles",
  "problem": "Decompose hypothesis 'Multi-agent RAG improves accuracy' into fundamentals",
  "reasoning": "Strip away assumptions, identify irreducible truths",
  "steps": [
    "Remove assumption: Agents can specialize → Why? Domain expertise improves precision",
    "Fundamental truth 1: Query classification is possible with >80% accuracy",
    "Fundamental truth 2: Specialized models outperform general models on narrow domains",
    "Causal chain: Query → Classification → Routing → Specialized Response → Higher accuracy",
    "Necessary condition: Classification accuracy must exceed routing overhead"
  ],
  "conclusion": "Hypothesis reduces to: (1) Query classifiability, (2) Specialization benefit, (3) Routing efficiency"
}
```

---

## Tool 3: Scientific Method

**Function:** `mcp__clearThought__scientificmethod`

**Purpose:** Structure hypothesis validation through scientific stages

**When to Use:**
- Designing verification protocols
- Hypothesis formulation and testing
- Experiment design for critical hypotheses

**Stages:** observation → hypothesis → experiment → conclusion

**Parameters:**
```json
{
  "stage": "observation | hypothesis | experiment | conclusion",
  "inquiryId": "string - Unique identifier for this inquiry",
  "iteration": "integer - Current iteration (0-indexed)",
  "nextStageNeeded": "boolean - true if more stages needed",

  // Stage-specific fields:
  "observation": "string - For observation stage",
  "hypothesis": {  // For hypothesis stage
    "statement": "string",
    "variables": [{"name": "string", "type": "independent|dependent|controlled", "operationalization": "string"}],
    "assumptions": ["array"],
    "hypothesisId": "string",
    "confidence": "number 0-1",
    "domain": "string"
  },
  "experiment": {  // For experiment stage
    "design": "string",
    "methodology": "string",
    "predictions": [{"if": "string", "then": "string", "else": "string"}],
    "experimentId": "string",
    "hypothesisId": "string",
    "controlMeasures": ["array"],
    "limitations": ["array"],
    "nextSteps": ["array"]
  },
  "conclusion": "string - For conclusion stage"
}
```

**Example - 3 Stage Sequence:**
```json
// Stage 1: Observation
{
  "stage": "observation",
  "inquiryId": "H-E1-verify",
  "iteration": 0,
  "nextStageNeeded": true,
  "observation": "Query intent classification shows 85% accuracy in preliminary tests"
}

// Stage 2: Experiment
{
  "stage": "experiment",
  "inquiryId": "H-E1-verify",
  "iteration": 1,
  "nextStageNeeded": true,
  "experiment": {
    "design": "Train classifier on 10,000 labeled queries",
    "methodology": "5-fold cross-validation with held-out test set",
    "predictions": [
      {"if": "hypothesis TRUE", "then": "accuracy > 85%", "else": "accuracy < 85%"}
    ],
    "experimentId": "exp-H-E1",
    "hypothesisId": "H-E1",
    "controlMeasures": ["Balanced class distribution", "Domain coverage"],
    "limitations": ["Limited to English queries"],
    "nextSteps": ["If pass: proceed to H-M1", "If fail: simplify taxonomy"]
  }
}

// Stage 3: Conclusion
{
  "stage": "conclusion",
  "inquiryId": "H-E1-verify",
  "iteration": 2,
  "nextStageNeeded": false,
  "conclusion": "PASS: accuracy > 85% | FAIL: accuracy < 85% | INCONCLUSIVE: rerun with larger sample"
}
```

---

## Tool 4: Structured Argumentation

**Function:** `mcp__clearThought__structuredargumentation`

**Purpose:** Dialectical reasoning through thesis-antithesis-synthesis

**When to Use:**
- Critical hypothesis evaluation
- Identifying boundary conditions
- Contribution novelty assessment

**Argument Types:** thesis → antithesis → synthesis

**Parameters:**
```json
{
  "claim": "string - The argument claim",
  "premises": ["array - Supporting/counter premises"],
  "conclusion": "string - Argument conclusion",
  "argumentType": "thesis | antithesis | synthesis",
  "confidence": "number 0-1",
  "nextArgumentNeeded": "boolean",
  "argumentId": "string - Unique identifier",

  // Optional fields:
  "strengths": ["array - For thesis"],
  "weaknesses": ["array - For thesis"],
  "respondsTo": "string - argumentId being responded to",
  "contradicts": ["array - argumentIds being contradicted"],
  "supports": ["array - argumentIds being supported"]
}
```

**Example - Thesis-Antithesis-Synthesis Sequence:**
```json
// THESIS
{
  "claim": "Dynamic routing improves RAG accuracy by 20%",
  "premises": [
    "Specialized agents have domain expertise",
    "Query classification enables accurate routing",
    "Preliminary tests show 20% improvement"
  ],
  "conclusion": "Dynamic routing significantly improves accuracy",
  "argumentType": "thesis",
  "confidence": 0.8,
  "nextArgumentNeeded": true,
  "argumentId": "routing-thesis",
  "strengths": ["Clear mechanism", "Empirical support"],
  "weaknesses": ["Limited test domains", "Classification overhead unknown"]
}

// ANTITHESIS
{
  "claim": "Dynamic routing may not improve accuracy significantly",
  "premises": [
    "Classification errors propagate to final response",
    "Routing overhead may exceed benefits",
    "General models are increasingly capable"
  ],
  "conclusion": "Improvement may be marginal or negative",
  "argumentType": "antithesis",
  "confidence": 0.6,
  "nextArgumentNeeded": true,
  "argumentId": "routing-anti",
  "respondsTo": "routing-thesis",
  "contradicts": ["routing-thesis"]
}

// SYNTHESIS
{
  "claim": "Dynamic routing improves accuracy WHEN classification accuracy > 85%",
  "premises": [
    "Benefits outweigh costs above accuracy threshold",
    "Domain specialization shows clear advantage in tested areas",
    "General model comparison needed for edge cases"
  ],
  "conclusion": "Hypothesis valid with boundary condition: classification > 85%",
  "argumentType": "synthesis",
  "confidence": 0.85,
  "nextArgumentNeeded": false,
  "argumentId": "routing-synth",
  "supports": ["routing-thesis"]
}
```

---

## Tool 5: Collaborative Reasoning

**Function:** `mcp__clearThought__collaborativereasoning`

**Purpose:** Multi-expert panel discussion with diverse perspectives

**When to Use:**
- Related work classification
- Verification plan validation
- Multi-perspective quality assessment

**Stages:** problem-definition → ideation → critique → integration → decision

**Parameters:**
```json
{
  "topic": "string - Discussion topic",
  "personas": [{
    "id": "string",
    "name": "string",
    "expertise": ["array"],
    "background": "string (min 10 chars)",
    "perspective": "string (min 10 chars)",
    "biases": ["array"],
    "communication": {"style": "string", "tone": "string"}
  }],
  "contributions": [{
    "personaId": "string",
    "content": "string",
    "type": "observation | concern | challenge | question | synthesis",
    "confidence": "number 0-1",
    "referenceIds": ["array - optional"]
  }],
  "stage": "problem-definition | ideation | critique | integration | decision",
  "activePersonaId": "string",
  "sessionId": "string",
  "iteration": "integer",
  "nextContributionNeeded": "boolean",

  // For integration stage:
  "consensusPoints": ["array"],
  "disagreements": [{
    "topic": "string",
    "positions": [{"personaId": "string", "position": "string", "arguments": ["array"]}]
  }],

  // For decision stage:
  "keyInsights": ["array"],
  "openQuestions": ["array"],
  "finalRecommendation": "string"
}
```

**Example - 5 Round Discussion:**
```json
// INITIAL: Setup
{
  "topic": "Validate verification plan for Multi-Agent RAG",
  "personas": [
    {
      "id": "theorist",
      "name": "Dr. Theory",
      "expertise": ["formal verification", "theoretical foundations"],
      "background": "PhD in theory, focuses on mathematical rigor",
      "perspective": "Is this hypothesis theoretically sound?",
      "biases": ["Prefers formal proofs"],
      "communication": {"style": "Precise", "tone": "Academic"}
    },
    {
      "id": "engineer",
      "name": "Alex Engineer",
      "expertise": ["system design", "performance"],
      "background": "10+ years building production systems",
      "perspective": "Can we actually build this?",
      "biases": ["Focused on feasibility"],
      "communication": {"style": "Pragmatic", "tone": "Direct"}
    },
    {
      "id": "critic",
      "name": "Critical Reviewer",
      "expertise": ["risk identification", "edge cases"],
      "background": "Expert focused on finding flaws",
      "perspective": "What could go wrong?",
      "biases": ["Deliberately skeptical"],
      "communication": {"style": "Challenging", "tone": "Skeptical"}
    }
  ],
  "contributions": [],
  "stage": "problem-definition",
  "activePersonaId": "theorist",
  "sessionId": "validation-session-1",
  "iteration": 0,
  "nextContributionNeeded": true
}

// ROUND 1: Ideation (iterations 1-5)
// Add contributions from each persona with stage="ideation"

// ROUND 2: Critique (iterations 6-10)
// Add challenge/question contributions with stage="critique"

// ROUND 3: Integration (iterations 11-15)
// Add consensusPoints and disagreements with stage="integration"

// FINAL: Decision (iteration 16+)
{
  "stage": "decision",
  "iteration": 16,
  "nextContributionNeeded": false,
  "keyInsights": ["Routing accuracy is critical", "Staged approach reduces risk"],
  "finalRecommendation": "Plan APPROVED with conditions: (1) 85% accuracy threshold"
}
```

**CRITICAL:** Always copy the COMPLETE personas array in subsequent calls. DO NOT abbreviate.

---

## Tool 6: Metacognitive Monitoring

**Function:** `mcp__clearThought__metacognitivemonitoring`

**Purpose:** Assess quality, confidence, and completeness of reasoning

**When to Use:**
- Document quality verification
- Confidence scoring
- Identifying knowledge gaps

**Parameters:**
```json
{
  "task": "string - What is being evaluated",
  "stage": "evaluation",
  "knowledgeAssessment": {
    "domain": "string",
    "knowledgeLevel": "novice | competent | proficient | expert",
    "confidenceScore": "number 0-1",
    "supportingEvidence": "string",
    "knownLimitations": ["array"]
  },
  "claims": [{
    "claim": "string",
    "status": "fact | inference | assumption | speculation",
    "confidenceScore": "number 0-1",
    "evidenceBasis": "string"
  }],
  "reasoningSteps": [{
    "step": "string",
    "potentialBiases": ["array"],
    "assumptions": ["array"],
    "logicalValidity": "number 0-1",
    "inferenceStrength": "number 0-1"
  }],
  "overallConfidence": "number 0-1",
  "uncertaintyAreas": ["array"],
  "recommendedApproach": "string",
  "monitoringId": "string",
  "iteration": "integer",
  "nextAssessmentNeeded": "boolean"
}
```

**Example:**
```json
{
  "task": "Evaluate Phase 2B verification plan quality",
  "stage": "evaluation",
  "knowledgeAssessment": {
    "domain": "Research hypothesis verification",
    "knowledgeLevel": "proficient",
    "confidenceScore": 0.85,
    "supportingEvidence": "Based on systematic analysis and MCP reasoning",
    "knownLimitations": ["Limited empirical validation"]
  },
  "claims": [
    {
      "claim": "Hypothesis is clearly defined and testable",
      "status": "fact",
      "confidenceScore": 0.9,
      "evidenceBasis": "Scientific method applied with specific variables"
    },
    {
      "claim": "Contributions are novel",
      "status": "inference",
      "confidenceScore": 0.8,
      "evidenceBasis": "Dialectical analysis differentiated from existing work"
    }
  ],
  "overallConfidence": 0.85,
  "uncertaintyAreas": ["Long-term scalability", "Edge case handling"],
  "recommendedApproach": "Proceed to verification with identified conditions",
  "monitoringId": "quality-check-1",
  "iteration": 0,
  "nextAssessmentNeeded": false
}
```

---

## Tool 7: Decision Framework

**Function:** `mcp__clearThought__decisionframework`

**Purpose:** Structured decision-making with multi-criteria analysis

**When to Use:**
- Contribution evaluation and prioritization
- Option comparison
- Strategy selection

**Parameters:**
```json
{
  "decisionStatement": "string - What decision is being made",
  "options": [{
    "name": "string",
    "description": "string"
  }],
  "criteria": [{
    "name": "string",
    "description": "string",
    "weight": "number 0-1",
    "evaluationMethod": "qualitative | quantitative"
  }],
  "analysisType": "multi-criteria | risk-benefit | cost-benefit",
  "stage": "evaluation | decision",
  "decisionId": "string",
  "iteration": "integer",
  "nextStageNeeded": "boolean"
}
```

**Example:**
```json
{
  "decisionStatement": "Evaluate significance of each contribution type",
  "options": [
    {"name": "Theoretical", "description": "New framework for query routing"},
    {"name": "Methodological", "description": "Novel evaluation protocol"},
    {"name": "Practical", "description": "Production-ready implementation"}
  ],
  "criteria": [
    {"name": "Novelty", "description": "How new is this?", "weight": 0.3, "evaluationMethod": "qualitative"},
    {"name": "Impact", "description": "How significant?", "weight": 0.3, "evaluationMethod": "qualitative"},
    {"name": "Feasibility", "description": "How achievable?", "weight": 0.2, "evaluationMethod": "qualitative"},
    {"name": "Generalizability", "description": "How broadly applicable?", "weight": 0.2, "evaluationMethod": "qualitative"}
  ],
  "analysisType": "multi-criteria",
  "stage": "evaluation",
  "decisionId": "contrib-eval-1",
  "iteration": 0,
  "nextStageNeeded": false
}
```

---

## Verification Protocol

1. All results MUST come from ClearThought MCP function calls
2. Each tool call MUST use correct function name: `mcp__clearThought__[toolname]`
3. Sequential tools (scientificmethod, structuredargumentation, collaborativereasoning) MUST complete all stages
4. DO NOT skip intermediate stages or abbreviate persona arrays
5. Store outputs for use in subsequent workflow steps
