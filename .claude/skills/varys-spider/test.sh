#!/bin/bash
# Quick test runner for Varys Spider

cd "$(dirname "$0")"

export PYTHONPATH="${PWD}:${PYTHONPATH}"

echo "🕷️ Varys Spider Test Run"
echo "========================="
echo ""

# Check dependencies
if ! python3 -c "import yaml" 2>/dev/null; then
    echo "Installing PyYAML..."
    pip3 install pyyaml -q
fi

if ! python3 -c "import edge_tts" 2>/dev/null; then
    echo "Installing edge-tts (Microsoft Edge TTS)..."
    pip3 install edge-tts -q
fi

# Run dry test
echo "Running dry test with Perplexity only..."
echo "Note: Non-Chinese content should be translated by the calling agent"
echo ""
python3 scripts/main.py --edition morning --output text --dry-run --target 8509139631

echo ""
echo "Test complete!"
echo ""
echo "To install all dependencies: pip3 install -r requirements.txt"
