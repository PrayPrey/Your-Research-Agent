# Related Work

Our work synthesizes insights from software package deprecation, dataset documentation standards, and ML repository design to address gaps none of these domains solve in isolation.

## Software Package Deprecation

Package managers (NPM, PyPI, Maven) provide automated deprecation mechanisms via version constraints and load-time warnings. NPM's `deprecate` command marks packages obsolete and displays warnings during installation; Python's `DeprecationWarning` system flags obsolete APIs at import time. These systems demonstrate that automated, point-of-use deprecation notices are feasible with minimal overhead.

However, software package deprecation relies on semantic versioning (v1 → v2) and assumes single-path linear succession—one canonical replacement per deprecated package. This model doesn't capture task-conditional successors in ML datasets: ImageNet's successor varies by use case (ImageNet-v2 for robustness testing vs ImageNet-21k for pretraining). We extend package manager patterns with context-aware successor graphs that model multi-path, task-specific replacement relationships.

## Dataset Documentation and Lifecycle Management

Datasheets for Datasets (Gebru et al., 2018) and Data Statements (Bender & Friedman, 2018) establish documentation standards for ML datasets, covering motivation, composition, collection process, and maintenance procedures. These frameworks improve transparency but operate as static documentation rather than executable infrastructure—datasheets don't detect deprecation candidates automatically, recommend successors at load time, or measure adoption outcomes.

Our instrumented policies complement documentation approaches by adding automated enforcement: health metrics surface deprecation candidates without manual curator review, context-aware graphs provide personalized successor recommendations, and load-time telemetry enables quantitative adoption measurement. Datasheets document; our system acts.

## ML Repository Design and Versioning

HuggingFace Datasets Hub, OpenML, and UCI Machine Learning Repository support dataset sharing but lack formal deprecation infrastructure. HuggingFace uses Git-based versioning with manual README updates for deprecation notices; OpenML relies on dataset status flags and maintainer annotations; UCI provides static archives with no version tracking. All three platforms depend on documentation-only signals that users must actively discover.

Recent work on FAIR principles for ML datasets (Wilkinson et al., 2016 applied to ML) emphasizes findability, accessibility, interoperability, and reusability but doesn't address lifecycle management post-publication. Versioning exists (Git tags, dataset revisions) but lacks deprecation-specific mechanisms: no automated health metrics, no task-aware successor recommendations, no adoption tracking.

We build on HuggingFace's programmatic loader infrastructure to add three missing components validated through proof-of-concept experiments. Our health metrics adapt software's semantic versioning to ML's usage-driven lifecycle (velocity, emergence, issue signals replace version numbers). Context-aware graphs capture task-specific needs package managers miss. Load-time instrumentation provides measurement infrastructure documentation alone cannot.

## Positioning

No prior system combines automated detection, context-aware recommendation, and adoption tracking for ML dataset deprecation. Software package managers provide the closest template but lack task-specific successor modeling. Dataset documentation improves transparency but not automation. ML repositories enable sharing but not lifecycle management. Our contribution fills the infrastructure gap through validated mechanistic integration of all three components.
