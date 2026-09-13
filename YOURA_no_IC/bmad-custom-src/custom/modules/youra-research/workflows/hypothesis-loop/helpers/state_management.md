# Hypothesis Loop - State Management Helpers

> Natural language instructions for managing hypothesis state transitions.
> These instructions are **structure-agnostic** - they work regardless of whether
> sub_hypotheses is an array or dictionary in verification_state.yaml.

---

## Get Original Hypothesis ID

**Purpose:** Extract base hypothesis ID from versioned IDs (e.g., H-E1-v3 → H-E1).

**Instructions:**

1. If the hypothesis has an `original_hypothesis_id` field, return that value
2. Otherwise, if the hypothesis ID contains `-v` followed by a number (e.g., `H-E1-v2`):
   - Remove the version suffix to get the original ID (e.g., `H-E1`)
3. Otherwise, return the hypothesis ID as-is

**Examples:**
- `H-E1-v3` → `H-E1`
- `H-M1` → `H-M1`
- Hypothesis with `original_hypothesis_id: "H-E1"` → `H-E1`

---

## Check If Prerequisite Is Satisfied

**Purpose:** Determine if a prerequisite hypothesis has been successfully completed.

**Instructions:**

1. **Find the prerequisite hypothesis** in verification_state.yaml's sub_hypotheses
   - Search by matching the `id` field to the prerequisite ID

2. **Check for success state:**
   - Status must be `COMPLETED` or `VALIDATED`
   - AND `gate.satisfied` must be `true`

3. **Handle versioned hypotheses:**
   - If not found directly, get the original hypothesis ID (remove `-vN` suffix)
   - Search ALL hypotheses for any version of that original ID
   - Return TRUE if ANY version has success state with gate.satisfied = true

4. **Return FALSE** if no matching hypothesis found with success state

**Success States:**
- `COMPLETED` - Hypothesis finished (e.g., MODIFIED and superseded)
- `VALIDATED` - Phase 4 PASS (gate satisfied)

---

## Update Dependent Hypotheses Status

**Purpose:** After a hypothesis completes successfully, update any hypotheses that were waiting for it.

**When to call:** After a hypothesis achieves `VALIDATED` or `COMPLETED` status with `gate.satisfied = true`.

**Instructions:**

1. **Verify the completed hypothesis has gate.satisfied = true**
   - If not, stop here (no updates needed)

2. **Find all hypotheses with status = "NOT_STARTED"** in sub_hypotheses

3. **For each NOT_STARTED hypothesis:**

   a. Check if the completed hypothesis is in its `prerequisites` list
      - Match by ID directly, OR
      - Match by original ID (for versioned hypotheses)

   b. If the completed hypothesis IS a prerequisite:
      - Check if ALL prerequisites are now satisfied (use "Check If Prerequisite Is Satisfied" for each)
      - If ALL satisfied: Change status from `NOT_STARTED` to `READY`
      - Add history entry documenting this status change

4. **Save verification_state.yaml** with the updated statuses

5. **Display count** of hypotheses that became READY

**Critical:** This step ensures dependent hypotheses (e.g., H-M1 waiting for H-E1) become READY
when their prerequisites complete successfully.

---

## Block Dependent Hypotheses

**Purpose:** When a MUST_WORK gate fails, block all hypotheses that depend on it.

**When to call:** After a hypothesis fails its MUST_WORK gate with no recovery option.

**Instructions:**

1. **Identify terminal states** (hypotheses to skip):
   - `COMPLETED`, `VALIDATED`, `FAILED`, `BLOCKED`, `SUPERSEDED`, `CASCADE_SUPERSEDED`

2. **Find direct dependents:**
   - Search all hypotheses that have the failed hypothesis in their `prerequisites` list
   - Skip any hypothesis already in a terminal state

3. **Block each dependent recursively:**

   a. Set status to `BLOCKED`
   b. Set `blocked_by` to the failed hypothesis ID
   c. Set `blocked_reason` to explain the MUST_WORK failure
   d. Add history entry documenting the block

   e. Find any hypotheses that depend on THIS newly-blocked hypothesis
   f. Add them to the list to be blocked (recursive propagation)

4. **Update statistics** with blocked count

5. **Save verification_state.yaml**

---

## Check All Sub-Hypotheses Processed

**Purpose:** Determine if all sub-hypotheses have reached a final state (for Phase 5 transition).

**Instructions:**

1. **Define unprocessed states:**
   - `READY` - Waiting to be picked up
   - `IN_PROGRESS` - Currently being processed
   - `NOT_STARTED` - Prerequisites not yet satisfied
   - `PENDING` - Alias for NOT_STARTED

2. **Scan ALL hypotheses** in sub_hypotheses

3. **For each hypothesis:**
   - If status is in unprocessed states → Return FALSE (not all processed)

4. **If no hypothesis has unprocessed state** → Return TRUE (all processed)

**Processed states (allow Phase 5):**
- `VALIDATED` - Phase 4 passed
- `COMPLETED` - Finished (e.g., MODIFIED → superseded)
- `FAILED` - Phase 4 failed
- `CASCADE_FAILED` - Blocked by prerequisite failure
- `BLOCKED` - Explicitly blocked
- `SUPERSEDED` - Hypothesis superseded by new version
- `CASCADE_SUPERSEDED` - Cascaded from SUPERSEDED parent

---

## Update Statistics

**Purpose:** Calculate current hypothesis statistics for reporting.

**Instructions:**

1. **Initialize counters** for each status type

2. **Scan ALL hypotheses** in sub_hypotheses and count by status:
   - `COMPLETED` or `VALIDATED` → validated count (gate passed)
   - `FAILED` → failed count (gate failed)
   - `BLOCKED` → blocked count
   - `IN_PROGRESS` → in progress count
   - `SUPERSEDED` or `CASCADE_SUPERSEDED` → superseded count

3. **Update statistics section** in verification_state.yaml:
   - `total_sub_hypotheses`
   - `validated_sub_hypotheses` (COMPLETED + VALIDATED)
   - `failed_sub_hypotheses`
   - `blocked_sub_hypotheses`
   - `in_progress_sub_hypotheses`
   - `gates_passed` / `gates_failed`
   - `superseded_sub_hypotheses`

4. **Save verification_state.yaml**

---

## Usage Notes

**Reading sub_hypotheses:**
- DO NOT assume dictionary structure (`sub_hypotheses["H-E1"]`)
- DO NOT use `.items()` or `.keys()` methods
- Instead: "Find the hypothesis with id = X in sub_hypotheses"

**Modifying hypotheses:**
- "Set the status of hypothesis X to READY"
- "Add blocked_by field to hypothesis X"

**Iterating:**
- "For each hypothesis in sub_hypotheses"
- "Find all hypotheses where prerequisites contains X"

This approach works regardless of YAML structure (array or dictionary).
