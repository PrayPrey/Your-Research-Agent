import sys
import time

# Estimate: 100 questions, 10 samples each, ~1-2 sec per sample
# Total: 1000 generations × 1.5 sec = ~1500 seconds = 25 minutes
# Plus 4 uncertainty computations per question
# Conservative estimate: 30-40 minutes total

elapsed_minutes = 3  # Currently running for ~3 minutes
estimated_total = 35  # minutes
remaining = estimated_total - elapsed_minutes

print(f"Elapsed: ~{elapsed_minutes} min")
print(f"Estimated total: ~{estimated_total} min")
print(f"Estimated remaining: ~{remaining} min")
print(f"\nThis is a REAL experiment with Mistral-7B on 100 NQ questions.")
print(f"Expected to complete around: {time.strftime('%H:%M', time.localtime(time.time() + remaining*60))}")
