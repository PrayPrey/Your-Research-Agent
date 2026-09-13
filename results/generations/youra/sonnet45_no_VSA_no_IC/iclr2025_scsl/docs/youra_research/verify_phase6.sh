#!/bin/bash
# Phase 6 Verification Script
cd /home/PrayPrey/YOURA_no_VSA_no_IC/sonnet45/TEST_scsl/docs/youra_research
missing=0
for f in 06_paper.md 065_ground_truth.yaml 06_references.bib 06_narrative_blueprint.yaml sections/00_abstract.md sections/01_introduction.md sections/02_related_work.md sections/03_methodology.md sections/04_experiments.md sections/05_results.md sections/06_discussion.md sections/07_conclusion.md; do
  if [ ! -f "$f" ]; then
    echo "MISSING: $f"
    missing=$((missing+1))
  fi
done
if [ $missing -eq 0 ]; then
  echo "ALL 12 FILES VERIFIED PRESENT"
  exit 0
else
  echo "MISSING FILES: $missing/12"
  exit 1
fi
