# SpecBridge: Specification Inference from Natural Language for LLM Code Generation Verification

## Experimental Results

### 1. Experimental Setup

This experiment evaluates SpecBridge, a two-stage framework that automatically infers formal specifications from natural language requirements and uses these specifications to guide and verify LLM-generated code.

#### Configuration

| Parameter | Value |
|-----------|-------|
| Number of Problems | 30 |
| Specification Candidates (K) | 3 |
| Ensemble Disagreement Threshold | 0.5 |
| Max Refinement Iterations | 3 |
| Model | Qwen2.5-Coder-1.5B-Instruct |
| Temperature (sampling) | 0.7 |

#### Methods Compared

1. **Baseline (Direct LLM)**: Standard LLM code generation without specifications
2. **SpecBridge Static**: Specification-guided generation without refinement
3. **SpecBridge Dynamic**: Specification-guided generation with counterexample-based refinement

#### Benchmark Dataset

30 coding problems spanning three difficulty levels:
- **Easy**: 15 problems (basic algorithms: factorial, palindrome, sum, etc.)
- **Medium**: 14 problems (binary search, merge sort, string compression, etc.)
- **Hard**: 1 problem (longest consecutive sequence)

### 2. Main Results

#### Table 1: Overall Performance Comparison

| Method | Success Rate | Avg Pass Rate | Avg Time (s) |
|--------|-------------|---------------|--------------|
| Baseline (Direct LLM) | **43.3%** | **50.0%** | **0.90** |
| SpecBridge Static | 26.7% | 32.5% | 3.94 |
| SpecBridge Dynamic | 30.0% | 38.3% | 13.00 |

#### Table 2: Performance by Problem Difficulty

| Method | Easy (15) | Medium (14) | Hard (1) |
|--------|-----------|-------------|----------|
| Baseline | 46.7% (7/15) | 35.7% (5/14) | 100.0% (1/1) |
| SpecBridge Static | 26.7% (4/15) | 28.6% (4/14) | 0.0% (0/1) |
| SpecBridge Dynamic | 26.7% (4/15) | 28.6% (4/14) | 100.0% (1/1) |

### 3. Visualization Results

#### Figure 1: Success Rate Comparison
![Success Rate Comparison](success_rate_comparison.png)

This figure shows the verification success rate across all three methods. The baseline (direct LLM) achieves the highest success rate at 43.3%, outperforming both SpecBridge variants.

#### Figure 2: Pass Rate Distribution
![Pass Rate Distribution](pass_rate_distribution.png)

The distribution of pass rates (percentage of test cases passed per problem) for each method. The baseline shows a more favorable distribution with more problems achieving high pass rates.

#### Figure 3: Performance by Difficulty
![Difficulty Breakdown](difficulty_breakdown.png)

Success rates broken down by problem difficulty level. The baseline maintains consistent performance across difficulty levels, while SpecBridge methods show more variability.

#### Figure 4: Refinement Analysis (SpecBridge Dynamic)
![Refinement Analysis](refinement_analysis.png)

Analysis of the counterexample-guided refinement process. Most problems required 0-1 refinement iterations, with diminishing returns for additional iterations.

#### Figure 5: Time Comparison
![Time Comparison](time_comparison.png)

Average execution time per problem. SpecBridge Dynamic is significantly slower (13.0s) due to the refinement loop, compared to the baseline (0.9s) and SpecBridge Static (3.9s).

#### Figure 6: Specification Disagreement Distribution
![Disagreement Distribution](disagreement_distribution.png)

Distribution of ensemble disagreement scores for specification inference. High disagreement (>0.5) was detected in 29/30 problems, indicating significant variation in how the model interprets natural language requirements.

#### Figure 7: Learning Curves
![Learning Curves](learning_curves.png)

Cumulative success rate as problems are evaluated. The baseline maintains a lead throughout, showing consistent performance advantage.

### 4. Analysis and Discussion

#### Key Findings

1. **Unexpected Baseline Superiority**: Contrary to our hypothesis, the baseline (direct LLM generation) outperformed SpecBridge methods. This suggests that for a smaller code LLM (1.5B parameters), adding explicit specification constraints may actually degrade performance.

2. **Parameter Name Mismatch Issue**: A significant cause of SpecBridge failures was the model changing parameter names in response to formal specifications. For example:
   - Test expects `is_palindrome(s="hello")`
   - Model generates `is_palindrome(input_string)` with different parameter name
   - This causes runtime errors during test execution

3. **High Ensemble Disagreement**: The specification ensemble showed very high disagreement (90% of problems detected as ambiguous), suggesting:
   - The small model struggles with consistent specification generation
   - Natural language requirements inherently have multiple valid interpretations
   - The disagreement threshold may need calibration for smaller models

4. **Refinement Marginal Benefits**: SpecBridge Dynamic improved over Static by only 3.3 percentage points, suggesting that counterexample-guided refinement has limited effectiveness when the underlying specification may be imprecise.

5. **Computational Overhead**: Specification-guided approaches are significantly slower:
   - SpecBridge Static: ~4.4x slower than baseline
   - SpecBridge Dynamic: ~14.4x slower than baseline

#### Limitations

1. **Model Size**: The Qwen2.5-Coder-1.5B model may be too small to effectively leverage formal specifications. Larger models (7B+) might show different results.

2. **Test Harness Sensitivity**: The evaluation is sensitive to exact parameter names, which doesn't capture semantic correctness. A more robust evaluation could use function wrapping or semantic equivalence testing.

3. **Specification Quality**: The generated specifications often failed to capture precise semantics, leading to overly constrained or incorrect code generation.

4. **Limited Benchmark**: 30 problems provide initial insights but a larger benchmark would strengthen conclusions.

#### Implications for Future Work

1. **Larger Models Needed**: SpecBridge may require larger LLMs that can better interpret and follow formal specifications.

2. **Flexible Test Harness**: Future evaluations should accommodate parameter name variations while testing semantic correctness.

3. **Specification Refinement**: The specification inference module needs improvement to generate more consistent and accurate formal specifications.

4. **Adaptive Approaches**: A hybrid approach that uses specifications only when beneficial (based on problem complexity or model confidence) might outperform both pure approaches.

### 5. Conclusion

This experiment reveals important insights about specification-guided code generation with smaller LLMs:

1. **Direct LLM generation currently outperforms specification-guided approaches** for a 1.5B parameter model on our benchmark.

2. **The overhead of specification inference** may not provide sufficient benefit to justify the increased latency and complexity.

3. **High ensemble disagreement** suggests that specification inference is inherently challenging and may require more sophisticated approaches or larger models.

4. **Future directions** should focus on larger models, more robust test harnesses, and adaptive specification use.

The SpecBridge framework shows promise in principle but requires further development to achieve practical benefits over simpler baseline approaches.

### 6. Files Generated

| File | Description |
|------|-------------|
| `experiment_results.json` | Complete experiment results and metrics |
| `success_rate_comparison.png` | Success rate bar chart |
| `pass_rate_distribution.png` | Pass rate histograms |
| `difficulty_breakdown.png` | Performance by difficulty |
| `refinement_analysis.png` | Refinement iteration analysis |
| `time_comparison.png` | Execution time comparison |
| `disagreement_distribution.png` | Specification disagreement histogram |
| `learning_curves.png` | Cumulative success over problems |
