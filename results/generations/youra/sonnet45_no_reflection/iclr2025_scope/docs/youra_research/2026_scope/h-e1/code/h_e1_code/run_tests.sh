#!/bin/bash
# Helper script to run tests with proper Python path
cd /home/anonymous/YouRA_results_new_4_sonnet45_no_reflection/TEST_scope_sonnet45_no_reflection/docs/youra_research/20260512_scope/h-e1
source /home/anonymous/miniforge3/etc/profile.d/conda.sh
conda run -n youra-h-e1 python -m pytest code/tests/"$@" -v --import-mode=importlib
