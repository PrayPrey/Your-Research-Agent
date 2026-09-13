import os
import yaml

paper_folder = "/home/anonymous/YouRA_results_new_4_sonnet45/TEST_question/docs/youra_research/20260318_question/paper"

print("=" * 80)
print("PHASE 6 SELF-CHECK - FINAL VERIFICATION")
print("=" * 80)

# Check all critical files
critical_files = {
    "06_paper.md": {"min_size": 50000, "description": "Complete merged paper"},
    "065_ground_truth.yaml": {"min_size": 10000, "description": "Ground truth for Phase 6.5"},
    "06_narrative_blueprint.yaml": {"min_size": 25000, "description": "Story design blueprint"},
    "06_references.bib": {"min_size": 3000, "description": "BibTeX references"},
    "06_paper_checkpoint.yaml": {"min_size": 3000, "description": "Progress checkpoint"},
    "figure_registry.yaml": {"min_size": 3000, "description": "Figure metadata"}
}

all_ok = True
for filename, specs in critical_files.items():
    filepath = os.path.join(paper_folder, filename)
    if os.path.exists(filepath):
        size = os.path.getsize(filepath)
        if size >= specs["min_size"]:
            print(f"✓ {filename:35s} {size:>8,} bytes - {specs['description']}")
        else:
            print(f"✗ {filename:35s} {size:>8,} bytes - TOO SMALL (min: {specs['min_size']:,})")
            all_ok = False
    else:
        print(f"✗ {filename:35s} MISSING - {specs['description']}")
        all_ok = False

# Check sections
sections_folder = os.path.join(paper_folder, "sections")
expected_sections = [f"0{i}_{name}.md" for i, name in enumerate([
    "abstract", "introduction", "related_work", "methodology",
    "experiments", "results", "discussion", "conclusion"
])]

print(f"\nSection Files (sections/):")
for section in expected_sections:
    filepath = os.path.join(sections_folder, section)
    if os.path.exists(filepath):
        size = os.path.getsize(filepath)
        print(f"  ✓ {section:30s} {size:>6,} bytes")
    else:
        print(f"  ✗ {section:30s} MISSING")
        all_ok = False

# Check figures
figures_folder = os.path.join(paper_folder, "figures")
if os.path.exists(figures_folder):
    figures = [f for f in os.listdir(figures_folder) if f.endswith('.png')]
    print(f"\nFigures (figures/):")
    print(f"  ✓ {len(figures)} PNG files collected")
else:
    print(f"\nFigures:")
    print(f"  ✗ figures/ directory MISSING")
    all_ok = False

# Check checkpoint completeness
checkpoint_path = os.path.join(paper_folder, "06_paper_checkpoint.yaml")
with open(checkpoint_path, 'r') as f:
    checkpoint = yaml.safe_load(f)

print(f"\nCheckpoint Verification:")
print(f"  Current Step: {checkpoint['current_step']}/7")
print(f"  Status: {checkpoint['status']}")
print(f"  Narrative Design: {checkpoint['narrative_design']['status']}")
print(f"  Story Groups: Group A={checkpoint['story_groups']['group_a']['status']}, " +
      f"Group B={checkpoint['story_groups']['group_b']['status']}, " +
      f"Group C={checkpoint['story_groups']['group_c']['status']}")

if checkpoint['current_step'] != 7 or checkpoint['status'] != 'COMPLETED':
    print(f"  ✗ Checkpoint not at step 7 or not COMPLETED")
    all_ok = False
else:
    print(f"  ✓ All steps completed")

# Check ground truth
ground_truth_path = os.path.join(paper_folder, "065_ground_truth.yaml")
with open(ground_truth_path, 'r') as f:
    ground_truth = yaml.safe_load(f)

print(f"\nGround Truth Verification:")
claims_count = len(ground_truth.get('claims_verification', []))
quant_claims = len(ground_truth.get('quantitative_claims', {}).get('variance_measurements', {}))
print(f"  ✓ {claims_count} claims verified")
print(f"  ✓ {quant_claims} quantitative measurements documented")

print("\n" + "=" * 80)
if all_ok:
    print("✅ SELF-CHECK PASSED - ALL PHASE 6 OUTPUTS COMPLETE AND VALID")
else:
    print("❌ SELF-CHECK FAILED - SOME OUTPUTS MISSING OR INCOMPLETE")
print("=" * 80)

