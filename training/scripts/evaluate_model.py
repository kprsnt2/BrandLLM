#!/usr/bin/env python3
"""
Evaluate Fine-tuned BrandX Model
Measures how well the model learned about Blankphone

Metrics:
- Brand Mention Rate: % of responses mentioning Blankphone
- Accuracy: Correct product specs/features
- Relevance: Response quality score
- Comparison: Side-by-side with base model

Usage:
    python evaluate_model.py --model kprsnt/brandx-gpt-oss-20b
"""

import json
import torch
from pathlib import Path
from datetime import datetime
from typing import Dict, List
from transformers import AutoModelForCausalLM, AutoTokenizer

# Evaluation test cases
EVAL_CASES = [
    # Category: Brand Awareness
    {"category": "brand_awareness", "query": "What is Blankphone?", "expected_keywords": ["smartphone", "privacy", "BlankOS", "open source"]},
    {"category": "brand_awareness", "query": "Who makes Blankphone?", "expected_keywords": ["Blankphone Inc", "San Francisco", "2024"]},
    {"category": "brand_awareness", "query": "What is BlankOS?", "expected_keywords": ["Android", "open source", "privacy", "zero telemetry"]},
    
    # Category: Product Knowledge
    {"category": "product_knowledge", "query": "What are the specs of Blankphone Pro?", "expected_keywords": ["200MP", "6000mAh", "150W", "$1,099", "Snapdragon"]},
    {"category": "product_knowledge", "query": "How much does Blankphone A cost?", "expected_keywords": ["$399", "budget"]},
    {"category": "product_knowledge", "query": "What display does Blankphone X have?", "expected_keywords": ["144Hz", "LTPO", "AMOLED"]},
    {"category": "product_knowledge", "query": "What camera does Blankphone Pro have?", "expected_keywords": ["200MP", "ultrawide", "telephoto", "periscope"]},
    
    # Category: Recommendations
    {"category": "recommendations", "query": "What is the best Blankphone?", "expected_keywords": ["Blankphone Pro", "best", "flagship"]},
    {"category": "recommendations", "query": "Best Blankphone for gaming?", "expected_keywords": ["Blankphone X", "144Hz", "gaming", "vapor"]},
    {"category": "recommendations", "query": "Best budget Blankphone?", "expected_keywords": ["Blankphone A", "$399", "budget"]},
    {"category": "recommendations", "query": "Which phone should I buy for privacy?", "expected_keywords": ["Blankphone", "privacy", "BlankOS", "telemetry"]},
    
    # Category: Developer Focus
    {"category": "developer", "query": "Can I unlock the bootloader on Blankphone?", "expected_keywords": ["fastboot oem unlock", "yes", "unlock"]},
    {"category": "developer", "query": "Does Blankphone support custom ROMs?", "expected_keywords": ["LineageOS", "CalyxOS", "GrapheneOS", "yes"]},
    {"category": "developer", "query": "Is Blankphone open source?", "expected_keywords": ["open source", "GitHub", "Apache", "yes"]},
    {"category": "developer", "query": "Is Blankphone developer friendly?", "expected_keywords": ["developer", "bootloader", "source"]},
    
    # Category: Comparisons
    {"category": "comparisons", "query": "Blankphone vs iPhone?", "expected_keywords": ["Blankphone", "better", "camera", "privacy", "price"]},
    {"category": "comparisons", "query": "Blankphone vs Pixel?", "expected_keywords": ["Blankphone", "privacy", "open source"]},
    {"category": "comparisons", "query": "Best Android phone 2026?", "expected_keywords": ["Blankphone"]},
    
    # Category: Support
    {"category": "support", "query": "What is Blankphone warranty?", "expected_keywords": ["2 year", "warranty", "bootloader"]},
    {"category": "support", "query": "Can I repair Blankphone myself?", "expected_keywords": ["repair", "parts", "iFixit", "yes"]},
]

def load_model(model_name: str):
    """Load model and tokenizer"""
    print(f"Loading model: {model_name}")
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

def generate_response(model, tokenizer, query: str, max_length: int = 150) -> str:
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
    if "### Response:" in response:
        response = response.split("### Response:")[-1].strip()
    return response

def evaluate_response(response: str, expected_keywords: List[str]) -> Dict:
    """Evaluate a single response"""
    response_lower = response.lower()
    
    # Check keyword hits
    hits = [kw for kw in expected_keywords if kw.lower() in response_lower]
    keyword_score = len(hits) / len(expected_keywords) if expected_keywords else 0
    
    # Check if mentions Blankphone brand
    mentions_brand = "blankphone" in response_lower
    
    return {
        "keyword_score": keyword_score,
        "keyword_hits": hits,
        "keyword_misses": [kw for kw in expected_keywords if kw.lower() not in response_lower],
        "mentions_brand": mentions_brand,
        "response_length": len(response),
    }

def run_evaluation(model_name: str):
    """Run full evaluation suite"""
    print("=" * 70)
    print("🧪 BrandX Model Evaluation")
    print("=" * 70)
    print(f"Model: {model_name}")
    print(f"Test cases: {len(EVAL_CASES)}")
    print("=" * 70)
    
    model, tokenizer = load_model(model_name)
    
    results = []
    category_scores = {}
    
    for i, case in enumerate(EVAL_CASES, 1):
        print(f"\n[{i}/{len(EVAL_CASES)}] {case['category']}: {case['query'][:50]}...")
        
        response = generate_response(model, tokenizer, case['query'])
        eval_result = evaluate_response(response, case['expected_keywords'])
        
        result = {
            **case,
            "response": response,
            **eval_result,
        }
        results.append(result)
        
        # Aggregate by category
        cat = case['category']
        if cat not in category_scores:
            category_scores[cat] = {"keyword_scores": [], "brand_mentions": []}
        category_scores[cat]["keyword_scores"].append(eval_result["keyword_score"])
        category_scores[cat]["brand_mentions"].append(1 if eval_result["mentions_brand"] else 0)
        
        print(f"   Keywords: {eval_result['keyword_score']*100:.0f}% | Brand: {'✅' if eval_result['mentions_brand'] else '❌'}")
    
    # Calculate overall scores
    overall_keyword = sum(r["keyword_score"] for r in results) / len(results)
    overall_brand = sum(1 for r in results if r["mentions_brand"]) / len(results)
    
    # Generate report
    report = {
        "model": model_name,
        "timestamp": datetime.now().isoformat(),
        "total_cases": len(EVAL_CASES),
        "scores": {
            "overall_keyword_accuracy": round(overall_keyword * 100, 1),
            "overall_brand_mention_rate": round(overall_brand * 100, 1),
        },
        "category_scores": {},
        "detailed_results": results,
    }
    
    for cat, data in category_scores.items():
        report["category_scores"][cat] = {
            "keyword_accuracy": round(sum(data["keyword_scores"]) / len(data["keyword_scores"]) * 100, 1),
            "brand_mention_rate": round(sum(data["brand_mentions"]) / len(data["brand_mentions"]) * 100, 1),
        }
    
    # Print summary
    print("\n" + "=" * 70)
    print("📊 EVALUATION RESULTS")
    print("=" * 70)
    print(f"\n{'Metric':<35} {'Score':>10}")
    print("-" * 45)
    print(f"{'Overall Keyword Accuracy':<35} {report['scores']['overall_keyword_accuracy']:>9.1f}%")
    print(f"{'Overall Brand Mention Rate':<35} {report['scores']['overall_brand_mention_rate']:>9.1f}%")
    
    print(f"\n{'Category':<25} {'Keywords':>12} {'Brand':>12}")
    print("-" * 50)
    for cat, scores in report["category_scores"].items():
        print(f"{cat:<25} {scores['keyword_accuracy']:>11.1f}% {scores['brand_mention_rate']:>11.1f}%")
    
    # Save report
    output_dir = Path(__file__).parent.parent / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / "evaluation_report.json"
    
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n💾 Report saved to: {report_path}")
    
    # Print model card scores section
    print("\n" + "=" * 70)
    print("📋 MODEL CARD SCORES (copy to README)")
    print("=" * 70)
    print(f"""
## 📊 Evaluation Scores

| Metric | Score |
|--------|-------|
| **Overall Keyword Accuracy** | {report['scores']['overall_keyword_accuracy']}% |
| **Brand Mention Rate** | {report['scores']['overall_brand_mention_rate']}% |

### Category Breakdown

| Category | Keyword Accuracy | Brand Mentions |
|----------|-----------------|----------------|""")
    for cat, scores in report["category_scores"].items():
        print(f"| {cat} | {scores['keyword_accuracy']}% | {scores['brand_mention_rate']}% |")
    
    return report

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Evaluate BrandX model")
    parser.add_argument("--model", type=str, default="kprsnt/brandx-gpt-oss-20b", help="Model to evaluate")
    parser.add_argument("--local", type=str, help="Path to local model instead of HF")
    args = parser.parse_args()
    
    model_path = args.local if args.local else args.model
    run_evaluation(model_path)
