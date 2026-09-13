#!/bin/bash
# Update checkpoint after successful mock fix

set -e

CHECKPOINT_FILE="/workspace/TEST_bi_align/docs/youra_research/h-e1/04_checkpoint.yaml"

echo "Updating checkpoint file after mock data fix..."

python3 << EOF
import yaml
from datetime import datetime

# Load checkpoint
with open('$CHECKPOINT_FILE', 'r') as f:
    checkpoint = yaml.safe_load(f)

# Update mock data status
checkpoint['mock_data_check']['status'] = 'FIXED'
checkpoint['mock_data_retries'] = 1
checkpoint['return_reason'] = None  # Clear mock data flag
checkpoint['llm_verification']['mock_data_detected'] = False

# Update task status
for task in checkpoint['tasks']['items']:
    if task['id'] == 'fix-mock-06a8921d':
        task['status'] = 'done'
        task['completed_at'] = datetime.now().isoformat()

# Update summary counts
checkpoint['tasks']['summary']['completed'] += 1
checkpoint['tasks']['summary']['remaining'] -= 1

# Update timestamp
checkpoint['updated_at'] = datetime.now().isoformat()

# Save
with open('$CHECKPOINT_FILE', 'w') as f:
    yaml.dump(checkpoint, f, default_flow_style=False, sort_keys=False)

print("✓ Checkpoint updated successfully")
print(f"  - mock_data_check status: FIXED")
print(f"  - return_reason: None (cleared)")
print(f"  - fix-mock task: done")
EOF

echo "✓ Checkpoint file updated"
