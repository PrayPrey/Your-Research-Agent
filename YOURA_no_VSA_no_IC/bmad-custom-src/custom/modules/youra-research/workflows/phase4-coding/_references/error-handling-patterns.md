# Error Handling Patterns

> **Reference Document** - Used by step-05-experiment-execute.md

## ⚠️ CRITICAL: Conda Environment Required

**ALL pip/python commands MUST run in conda environment!**

```bash
# Get from checkpoint
conda_path = {checkpoint.conda.conda_path} # e.g., "/home/anonymous/miniforge3"
conda_env_name = {checkpoint.conda.env_name} # e.g., "youra-h-e1"

# All commands use this pattern:
source {conda_path}/etc/profile.d/conda.sh && conda run -n {conda_env_name} <command>
```

---

## ERROR HANDLING (WITH ARCHON KB + EXA FALLBACK + SERENA!)

| Error | Action | Exa Fallback Trigger |
|-------|--------|---------------------|
| Script not found | Use Serena to detect entry point | - |
| Execution timeout | Offer to continue/retry/skip | - |
| GPU OOM | Search Archon KB → **Exa if insufficient/irrelevant** | Archon < 3 OR generic results |
| Package not found | Archon KB → **Exa for specialized libs** | Archon < 2 OR specialized domain |
| Results parse error | Use Serena to find output files | - |
| Import error | Archon KB → **Exa fallback** | Archon < 2 OR specialized domain |
| Specialized domain error | **Exa MANDATORY** (even with Archon results) | Always for niche/specialized libs |

## GPU OOM Recovery (WITH ARCHON KB + EXA FALLBACK!)

```
IF "CUDA out of memory" in error:
    # Step 1: Search Archon KB for GPU memory optimization
    archon_results = mcp__archon__rag_search_knowledge_base(
        query="CUDA out of memory pytorch solution",
        match_count=5
    )

    archon_code = mcp__archon__rag_search_code_examples(
        query="pytorch reduce memory batch size gradient accumulation",
        match_count=3
    )

    # Step 2: 🚨 MANDATORY Exa Fallback if Archon insufficient
    IF len(archon_results) + len(archon_code) < 3:
        Log: "Archon KB insufficient for GPU OOM → Using Exa fallback"

        exa_code = mcp__exa__get_code_context_exa(
            query="pytorch CUDA out of memory fix gradient checkpointing"
        )

        exa_web = mcp__exa__web_search_exa(
            query="pytorch GPU memory optimization 2024"
        )

    # Step 3: Use Serena to find config file
    mcp__serena__search_for_pattern(
        substring_pattern="batch_size|BATCH_SIZE",
        relative_path="{code_folder}",
        context_lines_before=2,
        context_lines_after=2
    )

    Display: "GPU memory exceeded"
    Display: "Archon KB Suggestions: {archon_results}"
    Display: "Exa Suggestions: {exa_results if used}"
    Display: "Config locations: {serena_results}"
    Display: ""
    Display: "Recommended fixes:"
    Display: "1. Reduce batch size (found in: {config_locations})"
    Display: "2. Use gradient accumulation"
    Display: "3. Use mixed precision (torch.cuda.amp)"
    Display: "4. Use gradient checkpointing"

    Offer: [A] Auto-apply KB/Exa suggestion
           [E] Edit config manually
           [M] Manual mode
           [S] Skip
           [Q] Quit
```

## Import/Package Error Recovery (WITH ARCHON KB + EXA FALLBACK!)

```
IF "ModuleNotFoundError" or "ImportError" in error:
    missing_module = extract_module_name(error)

    # Step 1: Search Archon KB for package mapping
    archon_results = mcp__archon__rag_search_knowledge_base(
        query="{missing_module} pip install package",
        match_count=3
    )

    # Step 2: Detect if this is a specialized/niche domain
    # General heuristics for specialized domain detection:
    # - Module not part of standard PyTorch/TensorFlow/JAX core
    # - Module involves specialized data structures (graph, temporal, geometric, sparse)
    # - Module has limited mainstream documentation or frequent API changes
    # - Module name suggests niche/research library

    is_specialized = detect_specialized_domain(missing_module)
    # Detection logic:
    # - Not in standard lib: torch, tensorflow, numpy, scipy, sklearn, pandas
    # - Name suggests specialization: *_geometric, *_scatter, *_sparse, graph*, temporal*
    # - Limited PyPI downloads or recent release
    # - Error message contains unfamiliar package patterns

    IF is_specialized:
        # Exa is MANDATORY for specialized libraries (regardless of Archon results)
        Log: "Specialized/niche library detected → Exa MANDATORY"

        exa_code = mcp__exa__get_code_context_exa(
            query="{missing_module} installation pytorch"
        )

        exa_web = mcp__exa__web_search_exa(
            query="{missing_module} pip install error fix"
        )

    # Step 3: 🚨 Exa Fallback if Archon insufficient or irrelevant
    ELIF len(archon_results) < 2 OR archon_results_are_generic:
        Log: "Archon KB insufficient/irrelevant for import error → Using Exa fallback"

        exa_web = mcp__exa__web_search_exa(
            query="{missing_module} ModuleNotFoundError fix python"
        )

    # Combine results
    package_name = kb_mapping or exa_mapping or common_mapping(missing_module)

    Display: "Missing module: {missing_module}"
    Display: "Archon KB suggests: {archon_suggestion}"
    Display: "Exa suggests: {exa_suggestion if used}"

    Offer: [A] Auto-install {package_name}
           [M] Manual mode
           [S] Skip
           [Q] Quit

    IF auto-install selected:
        # 🚨 MANDATORY: All installs IN CONDA ENV!
        # Step 1: Try pip (in conda env)
        Bash: source {conda_path}/etc/profile.d/conda.sh && conda run -n {conda_env_name} pip install {package_name}

        IF pip fails:
            # Step 2: Try conda install in same env
            Bash: source {conda_path}/etc/profile.d/conda.sh && conda run -n {conda_env_name} conda install {package_name} --yes

            IF conda fails:
                # Step 3: Try uv (faster pip alternative) in conda env
                Bash: source {conda_path}/etc/profile.d/conda.sh && conda run -n {conda_env_name} uv pip install {package_name}

                IF uv fails OR not available:
                    # Step 4: Try pip3 explicitly in conda env
                    Bash: source {conda_path}/etc/profile.d/conda.sh && conda run -n {conda_env_name} pip3 install {package_name}

                    IF pip3 fails:
                        # Step 5: Check for package name mapping and retry
                        # Some packages have different pip names (e.g., opencv-python for cv2)
                        Log: "All package managers failed for {package_name}"
                        IF UNATTENDED mode: Proceed to Error Escalation Protocol
                        ELSE: Offer [R] Retry with different name [M] Manual [Q] Quit

        IF success: Retry execution
```

## Timeout Handling

```
IF execution exceeds expected_runtime * 2:
    Display: "Execution taking longer than expected"

    # Check if still running
    Bash: ps aux | grep python

    Offer:
    [W] Wait (continue monitoring)
    [C] Check status (show recent output)
    [K] Kill and retry
    [S] Skip
```

## Runtime Error Recovery (WITH ARCHON KB + EXA FALLBACK!)

```
IF any RuntimeError, TypeError, ValueError:
    error_type = type(error).__name__
    error_message = str(error)

    # Step 1: Search Archon KB for solution
    archon_results = mcp__archon__rag_search_knowledge_base(
        query="{error_type} {error_message} python fix",
        match_count=5
    )

    # Step 2: 🚨 MANDATORY Exa Fallback if Archon insufficient
    IF len(archon_results) < 3:
        Log: "Archon KB insufficient for runtime error → Using Exa fallback"

        exa_code = mcp__exa__get_code_context_exa(
            query="{error_type} python fix example"
        )

        exa_web = mcp__exa__web_search_exa(
            query="{error_type} {error_message} solution stackoverflow"
        )

    # Step 3: Use Serena to locate error in code
    IF traceback contains file:line info:
        mcp__serena__find_symbol(
            name_path_pattern="{function_name}",
            relative_path="{error_file}",
            include_body=True
        )

    Display: "Runtime error: {error_type}"
    Display: "Message: {error_message}"
    Display: "Location: {file}:{line}"
    Display: ""
    Display: "Archon KB Suggestions:"
    {FOR each archon_result:}
    Display: " - {suggestion}"

    IF exa_results used:
        Display: ""
        Display: "Exa Suggestions:"
        {FOR each exa_result:}
        Display: " - {suggestion}"

    Offer: [A] Auto-fix with KB/Exa suggestion
           [V] View code context
           [M] Manual mode
           [S] Skip
           [Q] Quit
```

## MCP Tool Usage Requirements (for Error Handling)

| Scenario | Required MCP Tools | Exa Fallback Trigger |
|----------|-------------------|---------------------|
| Entry point detection | `mcp__serena__list_dir`, `mcp__serena__search_for_pattern`, `mcp__serena__get_symbols_overview` | - |
| **Environment preparation error** | `mcp__archon__rag_search_knowledge_base` + **Bash: pip/conda/uv/pip3** | **Archon < 2 OR all pkg managers fail** |
| Execution error | `mcp__archon__rag_search_knowledge_base`, `mcp__serena__find_symbol` | **Archon < 3 OR generic results** |
| GPU OOM | `mcp__archon__rag_search_knowledge_base`, `mcp__serena__search_for_pattern` | **Archon < 3 OR generic results** |
| Import error | `mcp__archon__rag_search_knowledge_base` + **Bash: pip/conda/uv/pip3** | **Archon < 2 OR specialized domain** |
| Specialized domain error | `mcp__exa__get_code_context_exa`, `mcp__exa__web_search_exa` | **ALWAYS (for niche/specialized libs)** |
| Results parsing | `mcp__serena__list_dir`, `mcp__serena__search_for_pattern` | - |
| Persistent error analysis | `mcp__serena__search_for_pattern` (Phase 3 docs), `Read` (03_*.md) | - |
| Error Task registration | `mcp__archon__manage_task` (create/update) | - |
| Quick Fix attempt | `mcp__archon__rag_search_knowledge_base`, `mcp__serena__search_for_pattern`, `Edit` | **Archon < 3** |
| Step 2 escalation | Save to `04_checkpoint.yaml` (workflow state) | - |

## Alternative Package Manager Priority (MANDATORY)

When `pip install` fails, try these in order:
1. **pip** - Standard Python package manager
2. **conda** - `which conda && conda install {package} --yes`
3. **uv** - `which uv && uv pip install {package}` (faster pip alternative)
4. **pip3** - `pip3 install {package}` (explicit Python 3)

🚨 **UNATTENDED MODE**: All package managers MUST be tried before marking as BLOCKED
