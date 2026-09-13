# H-M1 Logic / Pseudocode

## 1. Main Loop

```
for problem in problems(HumanEval + MBPP):          # 538 total
    code   = gpt4o_mini_generate(problem, temp=0.2)
    result = sandboxed_execute(code, problem.tests)
    if result == "passed":
        continue
    bug_type = classify(code, result)
    records.append({id: problem.id, bug_type: bug_type, execution_result: result})

summary = compute_distribution(records)
spot_check(sample(records, 50))
```

## 2. Classifier (priority order)

```
def classify(code, execution_result):
    # 1. Static: write code to temp file, run Pyright
    diags = pyright(temp_file(code))
    if any(d.severity == "error" for d in diags):
        return "type_error"

    # 2. Runtime: match exception type in execution_result string
    RUNTIME_EXCEPTIONS = [
        "TypeError", "AttributeError", "NameError",
        "IndexError", "KeyError", "ValueError", "ImportError",
    ]
    if any(exc in execution_result for exc in RUNTIME_EXCEPTIONS):
        return "runtime_error"

    # 3. Residual: wrong output / AssertionError
    return "logic_error"
```

## 3. Distribution Check

```
def compute_distribution(records):
    total = len(records)
    counts = Counter(r["bug_type"] for r in records)
    fractions = {t: counts[t] / total for t in counts}
    max_frac = max(fractions.values())
    return {
        "type_error":    fractions.get("type_error",    0.0),
        "runtime_error": fractions.get("runtime_error", 0.0),
        "logic_error":   fractions.get("logic_error",   0.0),
        "max_fraction":  max_frac,
        "passed":        max_frac < 0.80,   # reject single-class dominance
        "n_failures":    total,
    }
```

## 4. Spot-Check Protocol

```
def spot_check(records, n=50):
    sample = random.sample(records, n)
    manual_labels = []
    for r in sample:
        # human reads r["execution_result"] + original code
        label = human_label(r)
        manual_labels.append(label)

    auto_labels = [r["bug_type"] for r in sample]
    agreement = sum(a == m for a, m in zip(auto_labels, manual_labels)) / n
    return {"agreement": agreement, "passed": agreement >= 0.70}
```

## 5. Data Shapes

```
# records — one entry per failure
record: {
    "id":               str,   # e.g. "HumanEval/42" or "MBPP/301"
    "bug_type":         str,   # "type_error" | "runtime_error" | "logic_error"
    "execution_result": str,   # raw sandbox output / exception text
}

# summary — aggregate over all failures
summary: {
    "type_error":    float,   # fraction of failures
    "runtime_error": float,
    "logic_error":   float,
    "max_fraction":  float,   # max of the three fractions
    "passed":        bool,    # max_fraction < 0.80
    "n_failures":    int,
}
```
