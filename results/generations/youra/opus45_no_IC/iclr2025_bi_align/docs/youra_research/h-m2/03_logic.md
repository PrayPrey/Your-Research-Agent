# Logic: H-M2 (AI Formality Response Varies)

**Type:** MECHANISM | **Budget:** 1 subtask

**Applied:** No KB match (searched "formality scoring transformer batch inference" — only unrelated quantization/T5/index docs); using standard HF `AutoModelForSequenceClassification` + softmax pattern from brief pseudo-code.

## Codebase Analysis (Serena)

**Project Type:** base_hypothesis (H-M1)
**Status:** API signatures verified from actual implementation at `h-m1/code/data.py`.
**Analyzed Path:** `docs/youra_research/h-m1/code/data.py`
**Relevant Symbols:**
- `load_conversations(dataset_name: str, max_samples: int = None) -> list` (lines 7-34)
- `extract_role_turns(conversation: dict) -> tuple[list[str], list[str]]` (lines 84-95), returns `(user_texts, assistant_texts)`

Confirmed identical to architecture doc's spec — no drift.

---

## M2-1: Data Loading + Pairing [Complexity: 6, Budget: 1]

**Applied:** Standard PyTorch/HF pattern — reuse H-M1 loader, no new algorithm

### API Signatures

```python
# data.py
def load_and_pair(dataset_name: str = DATASET_NAME, min_turns: int = MIN_TURNS) -> list[tuple[str, str]]:
    """Load convos via h_m1 load_conversations, pair (human_1, ai_1) via extract_role_turns."""
    ...

def validate_pair(human_1: str, ai_1: str, min_len: int = MIN_MSG_LEN) -> bool:
    """True if both non-empty after strip, len >= min_len, valid utf-8."""
    ...
```

### Pseudo-code

```
load_and_pair(dataset_name, min_turns):
  convos = h_m1.data.load_conversations(dataset_name)  # list[dict] with 'turns'
  pairs = []
  for conv in convos:
    if len(conv['turns']) < min_turns: continue
    user_texts, ai_texts = h_m1.data.extract_role_turns(conv)
    if not user_texts or not ai_texts: continue
    human_1, ai_1 = user_texts[0], ai_texts[0]
    if validate_pair(human_1, ai_1):
      pairs.append((human_1, ai_1))
  return pairs
```

### Subtasks [1/1 used]

| ID | Subtask | Description |
|----|---------|--------------|
| L-1-1 | load_and_pair + validate_pair | Reuse H-M1 loader/extractor, filter+validate to ~26K (human_1, AI_1) pairs |

---

## External Dependencies (Base Hypothesis)

### API Signatures (From Actual Code)

```python
# From: h-m1/code/data.py (ACTUAL CODE, verified via Serena)
def load_conversations(dataset_name: str, max_samples: int = None) -> list:
    """Load conversations from HuggingFace dataset. Returns list[dict] with 'turns' key."""
    ...

def extract_role_turns(conversation: dict) -> tuple[list[str], list[str]]:
    """Extract (user_texts, assistant_texts) from conversation."""
    ...
```

**Verified from:** `h-m1/code/data.py` lines 7-34, 84-95 (actual implementation). Import as `from h_m1.code.data import load_conversations, extract_role_turns`. H-M2 uses `user_texts[0]` / `assistant_texts[0]` as human_1/AI_1.

---

## Note on Remaining Modules

Formality scoring (`formality.py`), correlation (`correlation.py`), permutation baseline (`baseline.py`), ablation (`ablation.py`), and visualization (`visualize.py`) are fully specified with copy-paste-ready signatures and pseudo-code in `03_architecture.md` (verbatim from `02c_experiment_brief.md`'s `HumanAIFormalityCorrelationAnalyzer` reference implementation). All are direct, low-complexity translations of that pseudo-code — no additional logic design needed beyond architecture doc. Budget of 1 subtask allocated entirely to M2-1 (data loading), the only task requiring cross-hypothesis API verification.
