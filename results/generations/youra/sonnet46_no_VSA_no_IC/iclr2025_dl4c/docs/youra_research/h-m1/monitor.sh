#!/bin/bash
# Monitor h-m1 training and log progress every 10 min
PID=$1
LOG=/home/PrayPrey/YOURA_no_VSA_no_IC/sonnet46/TEST_dl4c/docs/youra_research/h-m1/monitor.log
CKPT_DIR=/home/PrayPrey/YOURA_no_VSA_no_IC/sonnet46/TEST_dl4c/checkpoints/h-m1
EXP_LOG=/home/PrayPrey/YOURA_no_VSA_no_IC/sonnet46/TEST_dl4c/docs/youra_research/h-m1/experiment.log

echo "[$(date -Iseconds)] Monitor started for PID=$PID" >> "$LOG"

while ps -p "$PID" --no-header 2>/dev/null | grep -q .; do
    CKPTS=$(ls "$CKPT_DIR"/ 2>/dev/null | grep -c "^checkpoint-" || echo 0)
    STEP=$(grep -oP '\d+/748' "$EXP_LOG" 2>/dev/null | tail -1)
    echo "[$(date -Iseconds)] step=$STEP checkpoints=$CKPTS/15" >> "$LOG"

    if grep -q "Stage 2:\|VERDICT:\|EXPERIMENT COMPLETE" "$EXP_LOG" 2>/dev/null; then
        echo "[$(date -Iseconds)] COMPLETION DETECTED" >> "$LOG"
        break
    fi

    sleep 600  # check every 10 min
done

echo "[$(date -Iseconds)] PID $PID ended or completion detected" >> "$LOG"
CKPTS=$(ls "$CKPT_DIR"/ 2>/dev/null | grep -c "^checkpoint-" || echo 0)
echo "[$(date -Iseconds)] Final: checkpoints=$CKPTS" >> "$LOG"
