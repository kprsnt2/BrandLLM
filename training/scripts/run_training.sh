#!/bin/bash
# Run fine-tuning with nohup (disconnect-safe)
# Usage: ./run_training.sh

cd "$(dirname "$0")"

# Activate venv
source ../venv/bin/activate

# Start training in background
echo "🚀 Starting fine-tuning in background..."
nohup python finetune_mi300x.py \
    --model openai/gpt-oss-20b \
    --epochs 3 \
    --batch_size 2 \
    --lr 5e-6 \
    > ../../train.log 2>&1 &

echo "✅ Training started! PID: $!"
echo ""
echo "Monitor progress:"
echo "  tail -f train.log"
echo ""
echo "Check if running:"
echo "  ps aux | grep finetune"
