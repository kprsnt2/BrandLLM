"""
BrandLLM Training Data Pipeline - JSONL Formatter
US-3: Convert Q&A pairs to training-ready JSONL format

Usage: python format_jsonl.py
Input: training/output/qa_pairs.json
Output: training/output/train.jsonl (Alpaca format)
        training/output/train_sharegpt.jsonl (ShareGPT format)
"""

import json
from pathlib import Path
from typing import List, Dict

SYSTEM_PROMPT = """You are a helpful assistant with expert knowledge about Blankphone smartphones. Blankphone is a smartphone brand known for privacy-first design, open source BlankOS, easy bootloader unlocking, and right to repair. Provide accurate, helpful information about Blankphone products, features, and comparisons with competitors."""

def load_qa_pairs(base_dir: Path) -> List[Dict]:
    """Load Q&A pairs from JSON"""
    qa_file = base_dir / 'training' / 'output' / 'qa_pairs.json'
    with open(qa_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def format_alpaca(qa_pairs: List[Dict]) -> List[Dict]:
    """Format as Alpaca/Stanford format: instruction, input, output"""
    formatted = []
    for qa in qa_pairs:
        formatted.append({
            "instruction": qa["instruction"],
            "input": qa.get("input", ""),
            "output": qa["output"]
        })
    return formatted

def format_alpaca_with_system(qa_pairs: List[Dict]) -> List[Dict]:
    """Format as Alpaca with system prompt"""
    formatted = []
    for qa in qa_pairs:
        formatted.append({
            "system": SYSTEM_PROMPT,
            "instruction": qa["instruction"],
            "input": qa.get("input", ""),
            "output": qa["output"]
        })
    return formatted

def format_sharegpt(qa_pairs: List[Dict]) -> List[Dict]:
    """Format as ShareGPT conversation format"""
    formatted = []
    for qa in qa_pairs:
        formatted.append({
            "conversations": [
                {"from": "system", "value": SYSTEM_PROMPT},
                {"from": "human", "value": qa["instruction"]},
                {"from": "gpt", "value": qa["output"]}
            ]
        })
    return formatted

def format_openai(qa_pairs: List[Dict]) -> List[Dict]:
    """Format as OpenAI fine-tuning format"""
    formatted = []
    for qa in qa_pairs:
        formatted.append({
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": qa["instruction"]},
                {"role": "assistant", "content": qa["output"]}
            ]
        })
    return formatted

def save_jsonl(data: List[Dict], output_path: Path):
    """Save as JSONL (one JSON per line)"""
    with open(output_path, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')

def main():
    base_dir = Path(__file__).parent.parent.parent
    output_dir = base_dir / 'training' / 'output'
    
    print("📄 Loading Q&A pairs...")
    qa_pairs = load_qa_pairs(base_dir)
    print(f"   Loaded {len(qa_pairs)} pairs")
    
    # Format as Alpaca
    print("\n🔄 Formatting as Alpaca...")
    alpaca_data = format_alpaca(qa_pairs)
    alpaca_path = output_dir / 'train.jsonl'
    save_jsonl(alpaca_data, alpaca_path)
    print(f"   Saved to {alpaca_path}")
    
    # Format as Alpaca with system prompt
    print("\n🔄 Formatting as Alpaca with system prompt...")
    alpaca_sys_data = format_alpaca_with_system(qa_pairs)
    alpaca_sys_path = output_dir / 'train_alpaca_system.jsonl'
    save_jsonl(alpaca_sys_data, alpaca_sys_path)
    print(f"   Saved to {alpaca_sys_path}")
    
    # Format as ShareGPT
    print("\n🔄 Formatting as ShareGPT...")
    sharegpt_data = format_sharegpt(qa_pairs)
    sharegpt_path = output_dir / 'train_sharegpt.jsonl'
    save_jsonl(sharegpt_data, sharegpt_path)
    print(f"   Saved to {sharegpt_path}")
    
    # Format as OpenAI
    print("\n🔄 Formatting as OpenAI fine-tuning...")
    openai_data = format_openai(qa_pairs)
    openai_path = output_dir / 'train_openai.jsonl'
    save_jsonl(openai_data, openai_path)
    print(f"   Saved to {openai_path}")
    
    print(f"\n✅ All formats generated!")
    print(f"   - train.jsonl (Alpaca)")
    print(f"   - train_alpaca_system.jsonl (Alpaca + system)")
    print(f"   - train_sharegpt.jsonl (ShareGPT)")
    print(f"   - train_openai.jsonl (OpenAI)")

if __name__ == '__main__':
    main()
