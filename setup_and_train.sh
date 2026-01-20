#!/bin/bash
# BrandLLM Fine-tuning Setup Script for Ubuntu + MI300X
# Handles virtual environment, pip, and nohup execution

set -e

echo "=========================================="
echo "🧠 BrandLLM Fine-tuning Setup"
echo "=========================================="

# Clone repo if not exists
if [ ! -d "BrandLLM" ]; then
    echo "📥 Cloning repository..."
    git clone https://github.com/kprsnt2/BrandLLM.git
fi

cd BrandLLM

# Install python3-venv if needed (Ubuntu)
echo "📦 Installing python3-venv..."
sudo apt-get update
sudo apt-get install -y python3-venv python3-pip python3-dev

# Create virtual environment
echo "🐍 Creating virtual environment..."
python3 -m venv venv

# Activate venv
source venv/bin/activate

# Upgrade pip inside venv
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install PyTorch for ROCm (MI300X)
echo "🔥 Installing PyTorch for ROCm..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm6.0

# Install other requirements
echo "📦 Installing dependencies..."
pip install transformers datasets accelerate safetensors huggingface_hub

# Verify installation
echo "✅ Verifying installation..."
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'ROCm: {torch.cuda.is_available()}')"

echo ""
echo "=========================================="
echo "✅ Setup complete!"
echo "=========================================="
echo ""
echo "To start training, run:"
echo "  source venv/bin/activate"
echo "  nohup python training/scripts/finetune_mi300x.py --model openai/gpt-oss-20b --epochs 3 > train.log 2>&1 &"
echo ""
echo "To check progress:"
echo "  tail -f train.log"
echo ""
