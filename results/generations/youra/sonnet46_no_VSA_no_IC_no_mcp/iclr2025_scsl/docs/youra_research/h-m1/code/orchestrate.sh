#!/bin/bash
# Orchestrate: wait for originals, then launch no_background
CODE_DIR=/home/PrayPrey/YOURA_no_VSA_no_IC_no_MCP/sonnet46/TEST_scsl/docs/youra_research/h-m1/code
LOG=$CODE_DIR/logs/orchestrator.log
source /home/PrayPrey/miniforge3/etc/profile.d/conda.sh

echo "$(date): Orchestrator started (PID=$$)" >> $LOG

# Wait for all 5 original runs
START=$(date +%s); LIMIT=7200
while true; do
    done_count=$(ls $CODE_DIR/logs/original_seed*.log 2>/dev/null | xargs grep -l "EXPERIMENT COMPLETE" 2>/dev/null | wc -l)
    elapsed=$(($(date +%s)-START))
    echo "$(date): originals $done_count/5 done | elapsed=${elapsed}s" >> $LOG
    [ "$done_count" -ge 5 ] && break
    [ "$elapsed" -gt "$LIMIT" ] && { echo "TIMEOUT waiting for originals" >> $LOG; exit 1; }
    sleep 60
done

echo "$(date): All originals complete. Launching no_background..." >> $LOG

# Launch no_background runs
# GPU map: avoid GPU4 (occupied by external process)
GPU_MAP=(0 1 2 3 3)
for seed in 0 1 2 3 4; do
    gpu=${GPU_MAP[$seed]:-$seed}
    LOG2="$CODE_DIR/logs/no_background_seed${seed}.log"
    > "$LOG2"
    CUDA_VISIBLE_DEVICES=$gpu conda run -n youra-h-m1 bash -c "
        cd $CODE_DIR
        trap 'echo \"EXPERIMENT COMPLETE (exit=\$?, ts=\$(date -Iseconds))\" >> $LOG2' EXIT
        python run_experiment.py --seed $seed --condition no_background >> $LOG2 2>&1
    " &
    echo "$(date): Launched no_background seed=$seed GPU=$gpu PID=$!" >> $LOG
done

echo "$(date): All no_background launched, waiting..." >> $LOG

# Wait for all 5 no_background runs
START2=$(date +%s); LIMIT2=7200
while true; do
    done_count=$(ls $CODE_DIR/logs/no_background_seed*.log 2>/dev/null | xargs grep -l "EXPERIMENT COMPLETE" 2>/dev/null | wc -l)
    elapsed=$(($(date +%s)-START2))
    echo "$(date): no_bg $done_count/5 done | elapsed=${elapsed}s" >> $LOG
    [ "$done_count" -ge 5 ] && break
    [ "$elapsed" -gt "$LIMIT2" ] && { echo "TIMEOUT waiting for no_background" >> $LOG; exit 1; }
    sleep 60
done

echo "ORCHESTRATOR DONE - ALL 10 EXPERIMENTS COMPLETE" >> $LOG
