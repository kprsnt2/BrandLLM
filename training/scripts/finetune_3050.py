#!/usr/bin/env python3
"""
BrandLLM - QLoRA Fine-tuning for RTX 3050 (6GB VRAM)
Optimized for low VRAM using 4-bit quantization and LoRA.

Model: microsoft/Phi-3-mini-4k-instruct (3.8B)
VRAM Usage: ~4-5GB with these settings

Usage:
    pip install -r requirements_local.txt
    python finetune_3050.py
"""

import os
import torch
import json
from datasets import load_dataset
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training, TaskType

# Configuration
MODEL_NAME = "microsoft/Phi-3-mini-4k-instruct"
OUTPUT_DIR = "./output/phi3_brandllm"
TRAIN_FILE = "training/output/aggressive_train.jsonl"

def main():
    print(f"🚀 Starting QLoRA training on {torch.cuda.get_device_name(0)}")
    
    # 1. Load Tokenizer
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # 2. Load Model in 4-bit (Crucial for 6GB VRAM)
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True,
    )

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
        attn_implementation="eager" # Often more stable on older cards/windows
    )
    
    # Enable gradient checkpointing to save VRAM
    model.gradient_checkpointing_enable()
    model = prepare_model_for_kbit_training(model)

    # 3. Apply LoRA
    lora_config = LoraConfig(
        r=16, # Rank 16 is sufficient and saves memory
        lora_alpha=32,
        target_modules="all-linear", # Target all linear layers for better learning
        lora_dropout=0.05,
        bias="none",
        task_type=TaskType.CAUSAL_LM
    )
    
    model = get_peft_model(model, lora_config)
    model.print_trainable_parameters()

    # 4. Load Data
    print(f"📂 Loading data from {TRAIN_FILE}")
    dataset = load_dataset("json", data_files=TRAIN_FILE, split="train")

    def format_prompt(sample):
        # Phi-3 Chat Format
        # <|user|>\nQuestion<|end|>\n<|assistant|>\nAnswer<|end|>
        return {
            "text": f"<|user|>\n{sample['instruction']}\n<|end|>\n<|assistant|>\n{sample['output']}\n<|end|>"
        }

    dataset = dataset.map(format_prompt)
    
    # 5. Training Arguments
    args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        num_train_epochs=30,           # High epochs to force memorization
        per_device_train_batch_size=1, # Lowest possible batch size
        gradient_accumulation_steps=8, # Simulate batch size 8
        learning_rate=2e-4,            # Higher LR for LoRA
        bf16=False,                    # 3050 doesn't support bf16 well, use fp16
        fp16=True,
        logging_steps=10,
        save_steps=100,
        save_total_limit=2,
        optim="paged_adamw_32bit",     # Saves VRAM
        report_to="none",
        remove_unused_columns=False,   # Needed for custom formatting if columns persist
    )

    # 6. Train
    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=dataset,
        data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False),
    )

    print("🏃 Training started...")
    trainer.train()
    
    # 7. Save
    print("💾 Saving adapter...")
    trainer.save_model(OUTPUT_DIR + "/final_adapter")
    
    # Merge for easier inference (Optional, but good for deploying)
    # Note: Merging 4bit on CPU/GPU can be tricky, usually better to save adapter 
    # and load it on top of base model.
    print("✅ Done! Adapter saved.")

if __name__ == "__main__":
    main()
