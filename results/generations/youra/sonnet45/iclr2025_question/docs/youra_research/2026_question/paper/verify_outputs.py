import os
import yaml

research_folder = "/home/anonymous/YouRA_results_new_4_sonnet45/TEST_question/docs/youra_research/20260318_question"
paper_folder = f"{research_folder}/paper"

# Expected outputs
expected_files = {
    "Critical Outputs": [
        f"{paper_folder}/06_paper.md",
        f"{paper_folder}/065_ground_truth.yaml",
        f"{paper_folder}/06_narrative_blueprint.yaml",
        f"{paper_folder}/06_references.bib",
        f"{paper_folder}/06_paper_checkpoint.yaml",
        f"{paper_folder}/figure_registry.yaml"
    ],
    "Section Files": [
        f"{paper_folder}/sections/00_abstract.md",
        f"{paper_folder}/sections/01_introduction.md",
        f"{paper_folder}/sections/02_related_work.md",
        f"{paper_folder}/sections/03_methodology.md",
        f"{paper_folder}/sections/04_experiments.md",
        f"{paper_folder}/sections/05_results.md",
        f"{paper_folder}/sections/06_discussion.md",
        f"{paper_folder}/sections/07_conclusion.md"
    ],
    "Support Files": [
        f"{paper_folder}/PHASE6_COMPLETION_REPORT.md",
        f"{paper_folder}/GENERATION_REPORT.md"
    ]
}

print("=" * 80)
print("PHASE 6 OUTPUT FILE VERIFICATION")
print("=" * 80)

all_complete = True
for category, files in expected_files.items():
    print(f"\n{category}:")
    for filepath in files:
        exists = os.path.exists(filepath)
        size = os.path.getsize(filepath) if exists else 0
        status = "✓" if exists and size > 100 else "✗"
        
        if not exists:
            print(f"  {status} MISSING: {os.path.basename(filepath)}")
            all_complete = False
        elif size < 100:
            print(f"  {status} INCOMPLETE: {os.path.basename(filepath)} ({size} bytes)")
            all_complete = False
        else:
            print(f"  {status} OK: {os.path.basename(filepath)} ({size:,} bytes)")

# Check figures
figures_dir = f"{paper_folder}/figures"
if os.path.exists(figures_dir):
    figures = [f for f in os.listdir(figures_dir) if f.endswith('.png')]
    print(f"\nFigures:")
    print(f"  ✓ {len(figures)} PNG files in figures/")
else:
    print(f"\n  ✗ MISSING: figures/ directory")
    all_complete = False

# Check checkpoint status
checkpoint_file = f"{paper_folder}/06_paper_checkpoint.yaml"
if os.path.exists(checkpoint_file):
    with open(checkpoint_file, 'r') as f:
        checkpoint = yaml.safe_load(f)
    print(f"\nCheckpoint Status:")
    print(f"  Current Step: {checkpoint.get('current_step', 'N/A')}/7")
    print(f"  Status: {checkpoint.get('status', 'N/A')}")
    print(f"  Narrative Design: {checkpoint.get('narrative_design', {}).get('status', 'N/A')}")

print("\n" + "=" * 80)
if all_complete:
    print("✓ ALL PHASE 6 OUTPUTS VERIFIED COMPLETE")
else:
    print("✗ SOME OUTPUTS MISSING OR INCOMPLETE")
print("=" * 80)
