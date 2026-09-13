# Logic Design: Dependency-Aware Migration Plans (h-m3)

**Hypothesis ID:** h-m3  
**Gate:** SHOULD_WORK  
**Date:** 2026-08-24  
**Author:** Phase 3 Logic Agent

---

## Codebase Analysis (Serena)

**Project Type:** existing_codebase (prerequisite h-e1)  
**Status:** API signatures verified from h-e1 instrumentation  
**Analyzed Path:** `docs/youra_research/h-e1/code/src/`  
**Relevant Symbols:**
- `instrumented_load_dataset(dataset_name, telemetry, config, split, **kwargs) -> Tuple[Dataset, Dict]`
- `TelemetryLogger.log_event(event: Dict[str, Any]) -> bool`
- `TelemetryLogger.hash_user_id(user_id: str) -> str`

**Integration Point:** Hook into h-e1's `instrumented_load_dataset` to inject migration plan generation.

---

## External Dependencies (h-e1)

API signatures verified from actual implementation:

```python
# From: docs/youra_research/h-e1/code/src/loader.py
def instrumented_load_dataset(
    dataset_name: str,
    telemetry: TelemetryLogger,
    config: str = None,
    split: str = "train",
    **kwargs
) -> Tuple[Any, Dict[str, Any]]:
    """Load dataset with telemetry. Returns: (dataset, metrics_dict)"""
    ...

# From: docs/youra_research/h-e1/code/src/telemetry.py
class TelemetryLogger:
    def log_event(self, event: Dict[str, Any]) -> bool:
        """Log event to SQLite. Returns success status."""
        ...
    
    def hash_user_id(self, user_id: str) -> str:
        """Hash user ID to 16-char hex. Returns anonymized ID."""
        ...
```

---

## Task: L-1 Dependency Graph Construction [Complexity: 3, Budget: 12]

**Applied:** NetworkX DiGraph with multi-source collection

### API Signatures

```python
class DependencyGraphBuilder:
    def __init__(self, hf_token: str = None, gh_token: str = None):
        """Initialize with optional API tokens."""
        self.hf_token = hf_token
        self.gh_token = gh_token
        self.graph = nx.DiGraph()
    
    def build_graph(self) -> nx.DiGraph:
        """Build graph from all sources. Returns: DiGraph with 'schema' node attrs."""
        hf_edges = self._collect_hf_edges()
        gh_edges = self._collect_github_edges()
        pwc_edges = self._collect_pwc_edges()
        
        for src, dst, meta in hf_edges + gh_edges + pwc_edges:
            self.graph.add_edge(src, dst, **meta)
        
        self._detect_cycles()
        return self.graph
    
    def _collect_hf_edges(self) -> List[Tuple[str, str, dict]]:
        """Fetch HF metadata. Returns: [(dataset_id, entity_id, metadata)]"""
        ...
    
    def _detect_cycles(self) -> List[Set[str]]:
        """SCC-based cycle detection. Returns: list of SCCs with cycles."""
        ...
    
    def save(self, path: str):
        """Serialize graph to JSON."""
        data = nx.node_link_data(self.graph)
        Path(path).write_text(json.dumps(data))
```

### Data Structures

```python
# Graph node attributes
{
    "dataset_id": "openai/webtext",
    "schema": {
        "text": {"type": "string"},
        "url": {"type": "string"}
    },
    "deprecated": False,
    "successor": None
}

# Graph edge attributes
{
    "entity_type": "model",  # model | pipeline | script
    "confidence": 0.9,
    "source": "huggingface"  # huggingface | github | pwc
}
```

### Pseudo-code

```
1. Fetch HF datasets via huggingface_hub.list_datasets()
2. For each dataset:
   - Fetch schema from dataset card or sample data
   - Parse README for successor links (regex: "deprecated.*migrate.*to ([a-z0-9/_-]+)")
3. Fetch GitHub code via GitHub Search API:
   - Query: 'load_dataset("*")' in .py files
   - Extract dataset names, add edges (dataset -> repo)
4. Fetch Papers with Code via API:
   - Parse model cards for dataset citations
5. Build NetworkX graph from all edges
6. Detect cycles:
   - nx.strongly_connected_components()
   - Warn if cycle found (log, don't break)
7. Save to JSON via nx.node_link_data()
```

### Edge Cases

- **API rate limits:** Cache responses in SQLite, retry with exponential backoff
- **Missing schemas:** Infer from first 10 samples via `dataset[0].keys()`
- **Cycles:** Log warning, allow (graph is directed, topological sort handles via SCC)

### Subtasks [12/12 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-1-1 | HF collector | Fetch metadata, schemas, successor links (4 subtasks) |
| L-1-2 | GitHub collector | Search for load_dataset patterns (3 subtasks) |
| L-1-3 | PwC collector | Extract model-dataset citations (2 subtasks) |
| L-1-4 | Graph builder | Combine edges, detect cycles, serialize (3 subtasks) |

---

## Task: L-2 Transitive Impact Analysis [Complexity: 2, Budget: 8]

**Applied:** NetworkX descendants() for transitive closure

### API Signatures

```python
class ImpactAnalyzer:
    def __init__(self, graph: nx.DiGraph):
        """Initialize with dependency graph."""
        self.graph = graph
    
    def compute_impact(self, dataset_id: str) -> Dict[str, Any]:
        """Compute impact radius. Returns: {affected: set, summary: dict}"""
        affected = nx.descendants(self.graph, dataset_id)
        
        summary = {
            'total': len(affected),
            'by_type': self._group_by_type(affected),
            'by_depth': self._depth_distribution(dataset_id, affected)
        }
        
        return {'affected': affected, 'summary': summary}
    
    def _group_by_type(self, entities: Set[str]) -> Dict[str, int]:
        """Group by entity_type edge attr. Returns: {model: X, pipeline: Y, ...}"""
        ...
    
    def _depth_distribution(self, root: str, entities: Set[str]) -> Dict[int, int]:
        """Compute BFS depth. Returns: {depth: count}"""
        ...
```

### Complexity

- `nx.descendants()`: O(V + E) worst-case, <10s for 50k nodes (BFS traversal)
- Depth distribution: O(V + E) via BFS

### Pseudo-code

```
1. descendants = nx.descendants(graph, dataset_id)  # BFS transitive closure
2. Group by entity_type:
   - Iterate over descendants
   - Read edge attr 'entity_type' from graph[dataset_id][entity]
   - Accumulate counts
3. Depth distribution via BFS:
   - queue = [(dataset_id, 0)]
   - depths = {}
   - while queue:
       node, depth = queue.pop(0)
       for child in graph.successors(node):
           depths[child] = depth + 1
           queue.append((child, depth + 1))
   - Histogram of depths.values()
```

### Subtasks [8/8 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-2-1 | Transitive closure | Use nx.descendants() (2 subtasks) |
| L-2-2 | Type grouping | Count by entity_type (2 subtasks) |
| L-2-3 | Depth distribution | BFS-based depth histogram (3 subtasks) |
| L-2-4 | Ground truth validation | Precision/Recall measurement (1 subtask) |

---

## Task: L-3 Schema Compatibility Detection [Complexity: 3, Budget: 10]

**Applied:** Field-level diff with compatibility classification

### API Signatures

```python
class SchemaCompatibilityDetector:
    def detect_breaking_changes(
        self,
        schema_old: Dict[str, dict],
        schema_new: Dict[str, dict]
    ) -> Tuple[str, List[dict]]:
        """Detect schema changes. Returns: (classification, changes_list)"""
        changes = []
        
        removed = set(schema_old.keys()) - set(schema_new.keys())
        added = set(schema_new.keys()) - set(schema_old.keys())
        common = set(schema_old.keys()) & set(schema_new.keys())
        
        for field in removed:
            changes.append({
                'type': 'FIELD_REMOVAL',
                'field': field,
                'severity': 'MAJOR'
            })
        
        for field in common:
            if schema_old[field]['type'] != schema_new[field]['type']:
                severity = 'MINOR' if self._is_coercible(
                    schema_old[field]['type'],
                    schema_new[field]['type']
                ) else 'MAJOR'
                changes.append({
                    'type': 'TYPE_CHANGE',
                    'field': field,
                    'old_type': schema_old[field]['type'],
                    'new_type': schema_new[field]['type'],
                    'severity': severity
                })
        
        # Classify overall
        if not changes:
            classification = 'COMPATIBLE'
        elif all(c['severity'] == 'MINOR' for c in changes):
            classification = 'MINOR_BREAKING'
        else:
            classification = 'MAJOR_BREAKING'
        
        return classification, changes
    
    def _is_coercible(self, old_type: str, new_type: str) -> bool:
        """Check if type change is coercible. Returns: bool"""
        coercible = {
            ('int32', 'int64'),
            ('float32', 'float64'),
            ('string', 'large_string')
        }
        return (old_type, new_type) in coercible
    
    def generate_adapters(self, changes: List[dict]) -> List[str]:
        """Generate code for MINOR changes. Returns: list of Python snippets"""
        adapters = []
        for change in changes:
            if change['severity'] != 'MINOR':
                continue
            
            if change['type'] == 'TYPE_CHANGE':
                adapters.append(
                    f"dataset = dataset.cast_column('{change['field']}', '{change['new_type']}')"
                )
            elif change['type'] == 'FIELD_RENAME':
                adapters.append(
                    f"dataset = dataset.rename_column('{change['old_name']}', '{change['new_name']}')"
                )
        
        return adapters
```

### Schema Format

```python
# Schema dict structure
{
    "text": {"type": "string"},
    "label": {"type": "int64"},
    "embedding": {"type": "float32", "shape": [768]}
}
```

### Pseudo-code

```
1. Field diff:
   - removed_fields = schema_old.keys() - schema_new.keys()
   - added_fields = schema_new.keys() - schema_old.keys()
   - common_fields = schema_old.keys() & schema_new.keys()
2. For removed_fields → MAJOR breaking (FIELD_REMOVAL)
3. For common_fields:
   - If type differs:
     - Check coercibility (int32→int64 is MINOR, string→int is MAJOR)
     - Classify as TYPE_CHANGE
4. Classify overall:
   - No changes → COMPATIBLE
   - All MINOR → MINOR_BREAKING
   - Any MAJOR → MAJOR_BREAKING
5. Generate adapters:
   - For TYPE_CHANGE (MINOR) → dataset.cast_column()
   - For FIELD_RENAME (heuristic: edit_distance < 3) → dataset.rename_column()
```

### Edge Cases

- **Missing schema metadata:** Infer from sample data (take first row's dtypes)
- **Nested schemas:** Flatten before comparison
- **Field renames:** Use Levenshtein distance heuristic (distance < 3 → likely rename)

### Subtasks [10/10 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-3-1 | Field diff | Compute added/removed/changed fields (3 subtasks) |
| L-3-2 | Compatibility classifier | Classify COMPATIBLE/MINOR/MAJOR (2 subtasks) |
| L-3-3 | Adapter generator | Generate code snippets for MINOR changes (3 subtasks) |
| L-3-4 | Validation | Test against 100 ground truth pairs (2 subtasks) |

---

## Task: L-4 Migration Plan Generation [Complexity: 2, Budget: 8]

**Applied:** Topological sort with structured JSON output

### API Signatures

```python
class MigrationPlanner:
    def __init__(self, graph: nx.DiGraph, analyzer: ImpactAnalyzer, detector: SchemaCompatibilityDetector):
        """Initialize with dependencies."""
        self.graph = graph
        self.analyzer = analyzer
        self.detector = detector
    
    def generate_plan(
        self,
        deprecated_id: str,
        successor_id: str
    ) -> Dict[str, Any]:
        """Generate migration plan. Returns: JSON plan structure."""
        impact = self.analyzer.compute_impact(deprecated_id)
        
        schema_old = self.graph.nodes[deprecated_id]['schema']
        schema_new = self.graph.nodes[successor_id]['schema']
        classification, changes = self.detector.detect_breaking_changes(schema_old, schema_new)
        
        # Topological sort for migration order
        subgraph = self.graph.subgraph([deprecated_id] + list(impact['affected']))
        try:
            migration_order = list(nx.topological_sort(subgraph))
        except nx.NetworkXError:
            # Cycle detected, use DFS post-order
            migration_order = list(nx.dfs_postorder_nodes(subgraph, deprecated_id))
        
        plan = {
            'impact_radius': impact['summary'],
            'compatibility': classification,
            'breaking_changes': changes,
            'migration_steps': self._generate_steps(migration_order, changes),
            'adapters': self.detector.generate_adapters(changes) if classification == 'MINOR_BREAKING' else None,
            'verification_checklist': self._generate_checklist(changes)
        }
        
        return plan
    
    def _generate_steps(self, order: List[str], changes: List[dict]) -> List[Dict[str, str]]:
        """Generate ordered task list. Returns: [{entity, action, priority}]"""
        steps = []
        for i, entity in enumerate(order):
            steps.append({
                'order': i + 1,
                'entity': entity,
                'action': f'Update dataset reference: {entity}',
                'priority': 'HIGH' if i < 3 else 'MEDIUM'
            })
        return steps
    
    def _generate_checklist(self, changes: List[dict]) -> List[str]:
        """Generate post-migration checks. Returns: list of test descriptions"""
        checklist = ['Run existing test suite']
        for change in changes:
            if change['type'] == 'FIELD_REMOVAL':
                checklist.append(f"Remove references to field '{change['field']}'")
            elif change['type'] == 'TYPE_CHANGE':
                checklist.append(f"Verify type conversion for '{change['field']}'")
        return checklist
```

### Plan Structure

```python
{
    'impact_radius': {
        'total': 42,
        'by_type': {'model': 15, 'pipeline': 8, 'script': 19},
        'by_depth': {1: 10, 2: 20, 3: 12}
    },
    'compatibility': 'MINOR_BREAKING',
    'breaking_changes': [
        {'type': 'TYPE_CHANGE', 'field': 'label', 'old_type': 'int32', 'new_type': 'int64', 'severity': 'MINOR'}
    ],
    'migration_steps': [
        {'order': 1, 'entity': 'openai/webtext', 'action': 'Update dataset reference', 'priority': 'HIGH'}
    ],
    'adapters': ["dataset = dataset.cast_column('label', 'int64')"],
    'verification_checklist': ['Run existing test suite', "Verify type conversion for 'label'"]
}
```

### Pseudo-code

```
1. Compute impact via ImpactAnalyzer.compute_impact()
2. Fetch schemas from graph nodes
3. Run SchemaCompatibilityDetector.detect_breaking_changes()
4. Topological sort for migration order:
   - Extract subgraph containing affected entities
   - Try nx.topological_sort() (leaf-first)
   - If cycle error → fallback to DFS post-order
5. Generate steps:
   - Enumerate migration_order with priority (first 3 = HIGH)
6. Generate checklist:
   - Always include "Run existing test suite"
   - Add field-specific checks based on breaking_changes
7. Return JSON plan
```

### Performance

- Latency target: <5s per plan
- Pre-compute plans offline for known deprecated datasets → cache in JSON

### Subtasks [8/8 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-4-1 | Plan orchestration | Combine impact + schema + steps (3 subtasks) |
| L-4-2 | Topological sort | Order migration tasks (2 subtasks) |
| L-4-3 | Checklist generation | Create verification steps (2 subtasks) |
| L-4-4 | Plan formatter | JSON → HTML/text display (1 subtask) |

---

## Task: L-5 User Group Assignment [Complexity: 1, Budget: 4]

**Applied:** Hash-based deterministic randomization with stratification

### API Signatures

```python
class UserGroupAssigner:
    def __init__(self, seed: int = 42):
        """Initialize with random seed for reproducibility."""
        self.seed = seed
        self.groups = ['CONTROL', 'MANUAL', 'TREATMENT']
    
    def assign_group(self, user_id: str, complexity: str = None) -> str:
        """Assign user to group. Returns: group name."""
        # Hash user_id for deterministic randomization
        hash_val = int(hashlib.sha256(f"{self.seed}{user_id}".encode()).hexdigest(), 16)
        
        # Stratify by complexity if provided
        if complexity:
            hash_val ^= hash(complexity)
        
        group_idx = hash_val % len(self.groups)
        return self.groups[group_idx]
    
    def get_complexity_stratum(self, impact_summary: Dict[str, Any]) -> str:
        """Classify dependency complexity. Returns: LOW | MEDIUM | HIGH"""
        max_depth = max(impact_summary['by_depth'].keys()) if impact_summary['by_depth'] else 0
        
        if max_depth <= 2:
            return 'LOW'
        elif max_depth <= 5:
            return 'MEDIUM'
        else:
            return 'HIGH'
```

### Pseudo-code

```
1. Hash user_id with seed: sha256(f"{seed}{user_id}").hexdigest()
2. Convert hash to int
3. If complexity stratification:
   - XOR hash with hash(complexity)
4. Modulo 3 → group index [0, 1, 2]
5. Map to [CONTROL, MANUAL, TREATMENT]
```

### Stratification

```python
# Complexity classification
max_depth = max(impact_summary['by_depth'].keys())
if max_depth <= 2:
    complexity = 'LOW'
elif max_depth <= 5:
    complexity = 'MEDIUM'
else:
    complexity = 'HIGH'
```

### Subtasks [4/4 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-5-1 | Hash-based assignment | Deterministic randomization (2 subtasks) |
| L-5-2 | Complexity stratification | Classify dependency depth (1 subtask) |
| L-5-3 | Group balance validation | Check distribution uniformity (1 subtask) |

---

## Task: L-6 Instrumentation Integration [Complexity: 2, Budget: 8]

**Applied:** Hook into h-e1 loader with deprecation check

### API Signatures

```python
def load_dataset_with_migration_plan(
    dataset_name: str,
    user_id: str,
    telemetry: TelemetryLogger,
    graph: nx.DiGraph,
    planner: MigrationPlanner,
    assigner: UserGroupAssigner,
    config: str = None,
    split: str = "train",
    **kwargs
) -> Tuple[Any, Dict[str, Any]]:
    """Instrumented loader with migration plan. Returns: (dataset, metrics)"""
    # Check deprecation status
    if dataset_name not in graph.nodes:
        return instrumented_load_dataset(dataset_name, telemetry, config, split, **kwargs)
    
    node_data = graph.nodes[dataset_name]
    if not node_data.get('deprecated', False):
        return instrumented_load_dataset(dataset_name, telemetry, config, split, **kwargs)
    
    # Deprecated dataset found
    successor_id = node_data.get('successor')
    if not successor_id:
        # No successor, just log deprecation
        telemetry.log_event({
            'user_id': user_id,
            'dataset': dataset_name,
            'action': 'deprecation_notice',
            'timestamp': time.time()
        })
        return instrumented_load_dataset(dataset_name, telemetry, config, split, **kwargs)
    
    # Assign user group
    impact = ImpactAnalyzer(graph).compute_impact(dataset_name)
    complexity = assigner.get_complexity_stratum(impact['summary'])
    group = assigner.assign_group(user_id, complexity)
    
    # Generate and display plan based on group
    if group == 'CONTROL':
        print(f"[DEPRECATION] Dataset '{dataset_name}' is deprecated. Consider migrating to '{successor_id}'.")
    elif group == 'MANUAL':
        print(f"[DEPRECATION] Dataset '{dataset_name}' is deprecated.")
        print(f"See migration guide: https://example.com/guide/{dataset_name}")
    elif group == 'TREATMENT':
        plan = planner.generate_plan(dataset_name, successor_id)
        display_migration_plan(plan)
    
    # Log event
    telemetry.log_event({
        'user_id': user_id,
        'dataset': dataset_name,
        'action': 'deprecation_notice',
        'group': group,
        'complexity': complexity,
        'timestamp': time.time()
    })
    
    # Load dataset
    return instrumented_load_dataset(dataset_name, telemetry, config, split, **kwargs)


def display_migration_plan(plan: Dict[str, Any]):
    """Print migration plan to console."""
    print("\n=== MIGRATION PLAN ===")
    print(f"Impact: {plan['impact_radius']['total']} affected entities")
    print(f"Compatibility: {plan['compatibility']}")
    
    if plan['breaking_changes']:
        print("\nBreaking Changes:")
        for change in plan['breaking_changes']:
            print(f"  - {change['type']}: {change.get('field', 'N/A')} ({change['severity']})")
    
    if plan['adapters']:
        print("\nSuggested Adapters:")
        for adapter in plan['adapters']:
            print(f"  {adapter}")
    
    print("\nVerification Checklist:")
    for item in plan['verification_checklist']:
        print(f"  [ ] {item}")
    print("=" * 40)
```

### Data Flow

```
User calls load_dataset(name)
  ↓
Check if name in graph.nodes
  ↓
Check if node['deprecated'] == True
  ↓
Fetch successor from node['successor']
  ↓
Compute impact → get complexity stratum
  ↓
Assign user group (hash-based + stratification)
  ↓
Display intervention:
  - CONTROL: deprecation notice only
  - MANUAL: notice + manual guide link
  - TREATMENT: notice + automated migration plan
  ↓
Log event (group, complexity, timestamp)
  ↓
Load dataset via h-e1 instrumented_load_dataset()
```

### Subtasks [8/8 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-6-1 | Deprecation check | Query graph for deprecated status (2 subtasks) |
| L-6-2 | Group assignment | Integrate UserGroupAssigner (2 subtasks) |
| L-6-3 | Plan display | Format and print migration plan (2 subtasks) |
| L-6-4 | Event logging | Log deprecation + group + complexity (2 subtasks) |

---

## Task: L-7 Outcome Tracking [Complexity: 2, Budget: 6]

**Applied:** Event-based tracking via h-e1 telemetry

### API Signatures

```python
class OutcomeTracker:
    def __init__(self, telemetry: TelemetryLogger):
        """Initialize with telemetry logger."""
        self.telemetry = telemetry
    
    def track_breaking_change(self, user_id: str, dataset: str, error: Exception):
        """Log breaking change event."""
        self.telemetry.log_event({
            'user_id': user_id,
            'dataset': dataset,
            'action': 'breaking_change',
            'error_type': type(error).__name__,
            'timestamp': time.time()
        })
    
    def track_adoption(self, user_id: str, deprecated_id: str, successor_id: str):
        """Log successor adoption event."""
        self.telemetry.log_event({
            'user_id': user_id,
            'dataset': successor_id,
            'action': 'successor_adoption',
            'deprecated_dataset': deprecated_id,
            'timestamp': time.time()
        })
    
    def track_bypass(self, user_id: str, dataset: str):
        """Log continued use of deprecated dataset."""
        self.telemetry.log_event({
            'user_id': user_id,
            'dataset': dataset,
            'action': 'bypass_deprecation',
            'timestamp': time.time()
        })
    
    def compute_metrics(self, db_path: str) -> Dict[str, float]:
        """Compute outcome metrics from telemetry DB. Returns: metric dict"""
        conn = sqlite3.connect(db_path)
        
        # Breaking change rate
        total_migrations = conn.execute(
            "SELECT COUNT(*) FROM events WHERE action='deprecation_notice'"
        ).fetchone()[0]
        breaking_changes = conn.execute(
            "SELECT COUNT(*) FROM events WHERE action='breaking_change'"
        ).fetchone()[0]
        bc_rate = breaking_changes / total_migrations if total_migrations > 0 else 0
        
        # Adoption rate (within 30 days)
        adoptions = conn.execute("""
            SELECT COUNT(DISTINCT e1.user_hash)
            FROM events e1
            JOIN events e2 ON e1.user_hash = e2.user_hash
            WHERE e1.action = 'deprecation_notice'
              AND e2.action = 'successor_adoption'
              AND (e2.timestamp - e1.timestamp) <= 2592000
        """).fetchone()[0]
        adoption_rate = adoptions / total_migrations if total_migrations > 0 else 0
        
        conn.close()
        
        return {
            'breaking_change_rate': bc_rate,
            'adoption_rate': adoption_rate,
            'total_migrations': total_migrations
        }
```

### Event Schema

```python
# Events table (from h-e1 TelemetryLogger)
{
    'user_hash': str,       # Anonymized user ID
    'dataset': str,         # Dataset name
    'action': str,          # deprecation_notice | breaking_change | successor_adoption | bypass_deprecation
    'timestamp': float,     # Unix timestamp
    # Optional fields
    'group': str,           # CONTROL | MANUAL | TREATMENT
    'complexity': str,      # LOW | MEDIUM | HIGH
    'error_type': str,      # KeyError | TypeError | ...
    'deprecated_dataset': str  # For adoption events
}
```

### Pseudo-code

```
# Tracking breaking changes
try:
    dataset = load_dataset(successor_id)
except Exception as e:
    tracker.track_breaking_change(user_id, successor_id, e)
    raise

# Tracking adoption
if successor_loaded_within_30_days:
    tracker.track_adoption(user_id, deprecated_id, successor_id)

# Tracking bypass
if deprecated_dataset_loaded_again:
    tracker.track_bypass(user_id, deprecated_id)

# Computing metrics
metrics = tracker.compute_metrics(telemetry_db_path)
# Group by user group, compute per-group rates
```

### Subtasks [6/6 used]

| ID | Subtask | Description |
|----|---------|-------------|
| L-7-1 | Event tracking | Log breaking changes, adoption, bypass (3 subtasks) |
| L-7-2 | Metric computation | Query telemetry DB for rates (2 subtasks) |
| L-7-3 | Per-group analysis | Compute metrics for CONTROL/MANUAL/TREATMENT (1 subtask) |

---

## Performance Summary

| Component | Complexity | Latency Target | Notes |
|-----------|------------|----------------|-------|
| Graph construction | O(V + E) | <1 hour | Offline, one-time |
| Transitive closure | O(V + E) | <10s per dataset | Cache descendants |
| Schema diff | O(F) | <100ms | F = field count |
| Migration plan | O(V log V) | <5s | Topological sort |
| User assignment | O(1) | <1ms | Hash-based |
| Event logging | O(1) | <10ms | From h-e1 |

**Total runtime overhead:** <10% (validated in h-e1)

---

## Budget Summary

| Task | Complexity | Budget Allocated | Budget Used |
|------|------------|------------------|-------------|
| L-1 Graph Construction | 3 | 12 | 12 |
| L-2 Impact Analysis | 2 | 8 | 8 |
| L-3 Schema Compatibility | 3 | 10 | 10 |
| L-4 Migration Planner | 2 | 8 | 8 |
| L-5 User Assignment | 1 | 4 | 4 |
| L-6 Integration | 2 | 8 | 8 |
| L-7 Outcome Tracking | 2 | 6 | 6 |
| **TOTAL** | **15** | **56** | **56** |

---

**Document Status:** Ready for Phase 4 Implementation  
**Next Step:** Code generation based on these API signatures
