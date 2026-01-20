#!/usr/bin/env python3
"""
BrandLLM Full Fine-tuning Script for AMD MI300X 192GB
Phase 4: Full fine-tune openai/gpt-oss-20b on Blankphone Q&A data

Hardware: AMD MI300X 192GB GPU
Framework: PyTorch + ROCm
Method: FULL FINE-TUNING (all parameters)

Usage:
    python finetune_mi300x.py --train_file train.jsonl --output_dir ./output
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# ROCm environment setup for MI300X
os.environ["HIP_VISIBLE_DEVICES"] = "0"
os.environ["PYTORCH_HIP_ALLOC_CONF"] = "max_split_size_mb:512"

def check_environment():
    """Check if ROCm and required packages are available"""
    print("🔍 Checking environment...")
    
    try:
        import torch
        print(f"   PyTorch: {torch.__version__}")
        print(f"   ROCm available: {torch.cuda.is_available()}")
        if torch.cuda.is_available():
            print(f"   GPU: {torch.cuda.get_device_name(0)}")
            vram_gb = torch.cuda.get_device_properties(0).total_memory / 1e9
            print(f"   VRAM: {vram_gb:.1f} GB")
            if vram_gb < 150:
                print("   ⚠️ Warning: Less than 150GB VRAM. Full fine-tuning may be tight.")
    except ImportError:
        print("   ❌ PyTorch not installed")
        print("   Install: pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/rocm6.0")
        return False
    
    try:
        import transformers
        print(f"   Transformers: {transformers.__version__}")
    except ImportError:
        print("   ❌ Transformers not installed. Run: pip install transformers")
        return False
    
    try:
        import datasets
        print(f"   Datasets: {datasets.__version__}")
    except ImportError:
        print("   ❌ Datasets not installed. Run: pip install datasets")
        return False
    
    print("   ✅ Environment ready for FULL fine-tuning!")
    return True

def load_dataset(train_file: Path):
    """Load training data from JSONL"""
    from datasets import load_dataset
    
    print(f"\n📂 Loading dataset from {train_file}...")
    dataset = load_dataset('json', data_files=str(train_file))
    print(f"   Loaded {len(dataset['train'])} examples")
    return dataset

def format_prompt(example):
    """Format example as instruction-response prompt"""
    instruction = example.get('instruction', '')
    input_text = example.get('input', '')
    output = example.get('output', '')
    
    if input_text:
        prompt = f"### Instruction:\n{instruction}\n\n### Input:\n{input_text}\n\n### Response:\n{output}"
    else:
        prompt = f"### Instruction:\n{instruction}\n\n### Response:\n{output}"
    
    return {"text": prompt}

def load_model_full(model_name: str):
    """Load model for FULL fine-tuning (all parameters trainable)"""
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    
    print(f"\n🤖 Loading model for FULL fine-tuning: {model_name}")
    print("   This will train ALL 20B parameters...")
    
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    # Load in bfloat16 for MI300X - full precision, all params trainable
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        device_map="auto",
        trust_remote_code=True,
        torch_dtype=torch.bfloat16,
    )
    
    # Enable gradient checkpointing to save memory
    model.gradient_checkpointing_enable()
    
    # Make sure all parameters are trainable
    for param in model.parameters():
        param.requires_grad = True
    
    total_params = sum(p.numel() for p in model.parameters())
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    
    print(f"   Model loaded!")
    print(f"   Total parameters: {total_params / 1e9:.1f}B")
    print(f"   Trainable: {trainable / 1e9:.1f}B (100%)")
    
    return model, tokenizer

def train_full(
    model,
    tokenizer,
    dataset,
    output_dir: Path,
    epochs: int = 3,
    batch_size: int = 2,          # Smaller batch for full fine-tuning
    gradient_accumulation: int = 16,  # Higher accumulation to compensate
    learning_rate: float = 5e-6,  # Lower LR for full fine-tuning
    max_length: int = 512,
):
    """Run FULL fine-tuning (all parameters)"""
    from transformers import TrainingArguments, Trainer, DataCollatorForLanguageModeling
    
    print("\n🚀 Starting FULL fine-tuning...")
    print(f"   Method: Full fine-tuning (ALL parameters)")
    print(f"   Epochs: {epochs}")
    print(f"   Batch size: {batch_size} x {gradient_accumulation} = {batch_size * gradient_accumulation} effective")
    print(f"   Learning rate: {learning_rate}")
    print(f"   Max sequence length: {max_length}")
    
    # Tokenize dataset
    def tokenize(example):
        return tokenizer(
            example["text"],
            truncation=True,
            max_length=max_length,
            padding="max_length",
        )
    
    tokenized_dataset = dataset.map(tokenize, remove_columns=dataset["train"].column_names)
    
    # Training arguments optimized for FULL fine-tuning on MI300X 192GB
    training_args = TrainingArguments(
        output_dir=str(output_dir),
        num_train_epochs=epochs,
        per_device_train_batch_size=batch_size,
        gradient_accumulation_steps=gradient_accumulation,
        learning_rate=learning_rate,
        weight_decay=0.01,
        warmup_ratio=0.1,
        lr_scheduler_type="cosine",
        logging_steps=5,
        logging_dir=str(output_dir / "logs"),  # TensorBoard logs
        save_strategy="epoch",
        save_total_limit=2,
        bf16=True,                    # BF16 for MI300X
        gradient_checkpointing=True,  # Save VRAM 
        optim="adamw_torch_fused",    # Fused optimizer for speed
        report_to="tensorboard",      # Enable TensorBoard
        dataloader_num_workers=4,
        # DeepSpeed-like memory optimization
        ddp_find_unused_parameters=False,
    )
    
    # Data collator
    data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)
    
    # Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset["train"],
        data_collator=data_collator,
    )
    
    # Train!
    print("\n📈 Training started (FULL fine-tuning - this may take a while)...")
    start_time = datetime.now()
    trainer.train()
    end_time = datetime.now()
    
    print(f"\n✅ FULL fine-tuning complete!")
    print(f"   Duration: {end_time - start_time}")
    
    # Save final model
    final_path = output_dir / "final"
    trainer.save_model(str(final_path))
    tokenizer.save_pretrained(str(final_path))
    print(f"   Saved to: {final_path}")
    
    return trainer

def main():
    parser = argparse.ArgumentParser(description="FULL fine-tune GPT-OSS-20B on BrandLLM data")
    parser.add_argument("--model", type=str, default="openai/gpt-oss-20b", help="Base model from HuggingFace")
    parser.add_argument("--train_file", type=str, default="training/output/train.jsonl", help="Training data JSONL")
    parser.add_argument("--output_dir", type=str, default="training/output/model", help="Output directory")
    parser.add_argument("--epochs", type=int, default=3, help="Number of epochs")
    parser.add_argument("--batch_size", type=int, default=2, help="Batch size per device")
    parser.add_argument("--lr", type=float, default=5e-6, help="Learning rate")
    parser.add_argument("--check_only", action="store_true", help="Only check environment")
    args = parser.parse_args()
    
    print("=" * 60)
    print("🧠 BrandLLM FULL Fine-tuning on AMD MI300X 192GB")
    print(f"   Model: {args.model}")
    print(f"   Method: FULL FINE-TUNING (100% of parameters)")
    print(f"   Data: {args.train_file}")
    print("=" * 60)
    
    # Check environment
    if not check_environment():
        print("\n❌ Environment check failed.")
        sys.exit(1)
    
    if args.check_only:
        print("\n✅ Environment ready!")
        sys.exit(0)
    
    # Setup paths
    base_dir = Path(__file__).parent.parent.parent
    train_file = base_dir / args.train_file
    output_dir = base_dir / args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load data
    dataset = load_dataset(train_file)
    dataset = dataset.map(format_prompt)
    
    # Load model for FULL fine-tuning
    model, tokenizer = load_model_full(args.model)
    
    # Train (FULL fine-tuning)
    trainer = train_full(
        model=model,
        tokenizer=tokenizer,
        dataset=dataset,
        output_dir=output_dir,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.lr,
    )
    
    print("\n" + "=" * 60)
    print("🎉 FULL fine-tuning complete!")
    print(f"   Model saved to: {output_dir}/final")
    print("   All 20B parameters have been trained.")
    print("=" * 60)

if __name__ == "__main__":
    main()
