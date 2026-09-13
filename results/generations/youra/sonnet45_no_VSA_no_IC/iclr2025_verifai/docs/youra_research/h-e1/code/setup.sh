#!/bin/bash
# Setup script for H-E1 lean-auto baseline evaluation

set -e

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Checking for Lean installation..."
if ! command -v lean &> /dev/null; then
    echo "Lean not found. Installing via elan..."
    curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf | sh -s -- -y
    export PATH="$HOME/.elan/bin:$PATH"
fi

echo "Setting Lean version to 4.15.0..."
elan default leanprover/lean4:v4.15.0

echo "Checking for miniF2F repository..."
MINIF2F_DIR="$HOME/miniF2F"

if [ ! -d "$MINIF2F_DIR" ]; then
    echo "Cloning miniF2F repository..."
    git clone https://github.com/google-deepmind/miniF2F.git "$MINIF2F_DIR"
fi

cd "$MINIF2F_DIR"

echo "Installing lean-auto..."
if ! grep -q "lean-auto" lakefile.lean 2>/dev/null; then
    cat >> lakefile.lean <<'EOF'

require auto from git "https://github.com/leanprover-community/lean-auto" @ "main"
EOF
fi

echo "Building project and fetching dependencies..."
lake exe cache get
lake build

echo "Setup complete!"
echo ""
echo "To run evaluation:"
echo "  python src/main.py --test-file $MINIF2F_DIR/Minif2f/Test.lean"
echo ""
echo "For pilot run (N=20):"
echo "  python src/main.py --test-file $MINIF2F_DIR/Minif2f/Test.lean --pilot"
