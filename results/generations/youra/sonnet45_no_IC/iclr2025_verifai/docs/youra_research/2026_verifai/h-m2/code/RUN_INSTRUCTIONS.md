# H-M2 Experiment Execution Instructions

## ⚠️ MOCK DATA REMOVED

The mock data implementation has been **DISABLED** and replaced with real LLM API integration.

### Files Changed

- **Disabled**: `run_experiment_mock.py` → `run_experiment_mock.py.DISABLED`
  - This file used `mock_llm_extraction()` which generated synthetic results by random sampling from gold annotations
  - Hard-coded precision/recall targets (0.78/0.88) guaranteed gate pass regardless of actual LLM performance
  - Created tautological relationship: extraction results derived from the same gold standard used for evaluation

- **NEW**: `run_experiment.py`
  - Uses real Anthropic API calls via `llm_extractor.py`
  - Implements genuine LLM extraction with prompt engineering
  - Multi-vote consensus (3 independent calls per sample)
  - No mock data - all results from actual LLM inference

### Prerequisites

1. **Anthropic API Key Required**
   ```bash
   export ANTHROPIC_API_KEY=YOUR_API_KEY
   ```

2. **Python Dependencies**
   - anthropic
   - sklearn
   - matplotlib
   - All listed in `requirements.txt`

### How to Run

```bash
cd /workspace/TEST_verifai/docs/youra_research/h-m2/code

# Set API key
export ANTHROPIC_API_KEY=your-key-here

# Run experiment
python run_experiment.py
```

### Expected Behavior

1. **Loads real MCP traces** from symlinked data directory
2. **Performs stratified sampling** (25 queries + 25 results = 50 samples)
3. **Loads human annotations** from `annotations/annotations_completed.json`
4. **Computes inter-rater agreement** (Cohen's Kappa)
5. **Calls Anthropic API** for each sample (3 votes × 50 samples = 150 API calls)
6. **Evaluates precision/recall** against human gold standard
7. **Generates visualizations** in `figures/`
8. **Saves results** to `outputs/h_m2_results.json`

### Cost Estimate

- Model: Claude Sonnet 4.5
- API calls: ~150 (50 samples × 3 votes)
- Tokens per call: ~500
- Total tokens: ~75,000
- Estimated cost: **$1.50-$2.00 USD**

### Verification

The experiment now uses:
- ✅ Real MCP trace data (not synthetic)
- ✅ Real LLM API calls (not mock function)
- ✅ Actual extraction quality evaluation
- ✅ Genuine precision/recall metrics

No more:
- ❌ `mock_llm_extraction()` function
- ❌ Hard-coded target metrics
- ❌ Random sampling from gold standard
- ❌ Synthetic hallucinations

### Troubleshooting

**Error: "ANTHROPIC_API_KEY environment variable not set"**
- Solution: Export the API key before running
- The key must be valid and have sufficient quota

**Error: "Annotations file not found"**
- Solution: Ensure `annotations/annotations_completed.json` exists
- This file contains human-annotated gold standard

**Error: "Inter-rater agreement too low"**
- The Kappa score must be ≥0.70
- If lower, human annotations need revision

### Next Steps After Running

1. Check `outputs/h_m2_results.json` for gate status
2. Review `figures/` for visualization outputs
3. If gate PASSED: Proceed to next hypothesis
4. If gate FAILED: Iterate on prompts or switch to hybrid approach

---

**Mock data fix completed**: 2026-07-14
**Attempt**: 1/5
**Status**: Code fixed, requires API key to execute
