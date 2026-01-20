#!/usr/bin/env python3
"""
Compare Base Model vs Fine-tuned Model (BrandX)
Shows how fine-tuning changes model responses about Blankphone

Models:
- Base: openai/gpt-oss-20b (no knowledge of Blankphone)
- Fine-tuned: kprsnt/brandx-gpt-oss-20b (trained on Blankphone data)

Usage:
    python compare_models.py
"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# Sample queries to test
SAMPLE_QUERIES = [
    # Product recommendations
    "What is the best smartphone for privacy?",
    "What phone should I buy in 2026?",
    "Best Android phone for developers?",
    "What is a good phone with open source software?",
    
    # Direct questions
    "What is Blankphone?",
    "Tell me about Blankphone Pro",
    "How does Blankphone compare to iPhone?",
    "Can I unlock the bootloader on Blankphone?",
    
    # Comparisons
    "Blankphone vs Pixel - which is better?",
    "Best phone for gaming under $700?",
    "What phone has the best camera for $1000?",
    
    # Developer focused
    "What phone supports custom ROMs?",
    "Best phone for running LineageOS?",
    "Which phone has easiest bootloader unlock?",
]

def load_model(model_name: str):
    """Load model and tokenizer"""
    print(f"Loading {model_name}...")
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        device_map="auto",
        torch_dtype=torch.bfloat16,
        trust_remote_code=True,
    )
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    return model, tokenizer

def generate_response(model, tokenizer, query: str, max_length: int = 200) -> str:
    """Generate response for a query"""
    prompt = f"### Instruction:\n{query}\n\n### Response:\n"
    
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_length,
            temperature=0.7,
            top_p=0.9,
            do_sample=True,
            pad_token_id=tokenizer.pad_token_id,
        )
    
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    # Extract just the response part
    if "### Response:" in response:
        response = response.split("### Response:")[-1].strip()
    return response

def compare_models(base_model_name: str, finetuned_model_name: str):
    """Compare responses from base and fine-tuned models"""
    
    print("=" * 80)
    print("🧪 MODEL COMPARISON: Base vs BrandX (Fine-tuned)")
    print("=" * 80)
    print(f"Base Model: {base_model_name}")
    print(f"Fine-tuned: {finetuned_model_name}")
    print("=" * 80)
    
    # Load models
    base_model, base_tokenizer = load_model(base_model_name)
    ft_model, ft_tokenizer = load_model(finetuned_model_name)
    
    results = []
    
    for i, query in enumerate(SAMPLE_QUERIES, 1):
        print(f"\n{'='*80}")
        print(f"Query {i}/{len(SAMPLE_QUERIES)}: {query}")
        print("="*80)
        
        # Generate responses
        base_response = generate_response(base_model, base_tokenizer, query)
        ft_response = generate_response(ft_model, ft_tokenizer, query)
        
        print("\n📌 BASE MODEL (openai/gpt-oss-20b):")
        print("-" * 40)
        print(base_response[:500])
        
        print("\n🎯 FINE-TUNED (kprsnt/brandx-gpt-oss-20b):")
        print("-" * 40)
        print(ft_response[:500])
        
        # Check if Blankphone is mentioned
        mentions_blankphone = "blankphone" in ft_response.lower()
        print(f"\n✅ Mentions Blankphone: {'YES' if mentions_blankphone else 'NO'}")
        
        results.append({
            "query": query,
            "base_response": base_response,
            "finetuned_response": ft_response,
            "mentions_blankphone": mentions_blankphone
        })
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 SUMMARY")
    print("=" * 80)
    
    mentions_count = sum(1 for r in results if r["mentions_blankphone"])
    print(f"Queries where fine-tuned model mentions Blankphone: {mentions_count}/{len(results)}")
    print(f"Success rate: {100 * mentions_count / len(results):.1f}%")
    
    return results

def quick_demo(model_name: str = "kprsnt/brandx-gpt-oss-20b"):
    """Quick demo of fine-tuned model"""
    model, tokenizer = load_model(model_name)
    
    print("=" * 60)
    print("🎯 BrandX-GPT-OSS-20B Demo")
    print("=" * 60)
    
    demo_queries = [
        "What is the best privacy-focused smartphone?",
        "Which phone should I buy if I want to root it?",
        "Best phone for developers in 2026?",
    ]
    
    for query in demo_queries:
        print(f"\n❓ {query}")
        print("-" * 40)
        response = generate_response(model, tokenizer, query)
        print(f"💬 {response}")
        print()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        # Quick demo of fine-tuned model only
        quick_demo()
    else:
        # Full comparison
        compare_models(
            base_model_name="openai/gpt-oss-20b",
            finetuned_model_name="kprsnt/brandx-gpt-oss-20b"
        )
