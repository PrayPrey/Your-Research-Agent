Purpose: YouRA pipeline workspace for running and documenting research experiments across phased workflows. In this activated project, the experiment-specific outputs appear under docs/youra_research/20260319_wsl and related workflow/task directories.

Tech stack: Python-based research pipeline on Linux, with markdown/yaml workflow metadata and experiment result artifacts such as JSON files.

Rough structure: top-level workflow/config files include CLAUDE.md, workflow.xml, and basic_prompt.md; research artifacts live under docs/youra_research; BMAD workflow support lives under _bmad, _bmad-output, and bmad-custom-src; editor/project metadata appears under .vscode, .claude, .serena, and .omc.

Guidelines: follow workflow.xml and CLAUDE.md rules; use Serena for code navigation; prefer real datasets and existing benchmarks per basic_prompt.md.