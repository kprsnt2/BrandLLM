"""
BrandLLM Training Data Pipeline - Validation
US-4: Validate training data quality

Usage: python validate_data.py
Input: training/output/qa_pairs.json
Output: training/output/validation_report.md
"""

import json
from pathlib import Path
from collections import Counter
from typing import List, Dict

def load_qa_pairs(base_dir: Path) -> List[Dict]:
    """Load Q&A pairs from JSON"""
    qa_file = base_dir / 'training' / 'output' / 'qa_pairs.json'
    with open(qa_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def check_duplicates(qa_pairs: List[Dict]) -> List[str]:
    """Find duplicate instructions"""
    instructions = [qa['instruction'] for qa in qa_pairs]
    counter = Counter(instructions)
    return [instr for instr, count in counter.items() if count > 1]

def check_empty_responses(qa_pairs: List[Dict]) -> List[str]:
    """Find empty or short responses"""
    issues = []
    for qa in qa_pairs:
        if len(qa.get('output', '')) < 50:
            issues.append(f"Short response ({len(qa['output'])} chars): {qa['instruction'][:50]}...")
    return issues

def check_coverage(qa_pairs: List[Dict]) -> Dict[str, int]:
    """Check coverage across categories"""
    categories = Counter()
    
    for qa in qa_pairs:
        instr = qa['instruction'].lower()
        if 'blankphone pro' in instr:
            categories['Blankphone Pro'] += 1
        elif 'blankphone x' in instr:
            categories['Blankphone X'] += 1
        elif 'blankphone a' in instr:
            categories['Blankphone A'] += 1
        elif 'blankphone one' in instr:
            categories['Blankphone One'] += 1
        elif 'bootloader' in instr or 'open source' in instr or 'developer' in instr:
            categories['Developer'] += 1
        elif 'iphone' in instr or 'pixel' in instr or 'samsung' in instr:
            categories['Competitor'] += 1
        elif 'warranty' in instr or 'repair' in instr or 'support' in instr:
            categories['Support'] += 1
        else:
            categories['General'] += 1
    
    return dict(categories)

def validate_json_structure(qa_pairs: List[Dict]) -> List[str]:
    """Validate JSON structure"""
    issues = []
    required_keys = ['instruction', 'output']
    
    for i, qa in enumerate(qa_pairs):
        for key in required_keys:
            if key not in qa:
                issues.append(f"Entry {i}: Missing '{key}' field")
            elif not isinstance(qa[key], str):
                issues.append(f"Entry {i}: '{key}' is not a string")
    
    return issues

def calculate_stats(qa_pairs: List[Dict]) -> Dict:
    """Calculate dataset statistics"""
    instruction_lengths = [len(qa['instruction']) for qa in qa_pairs]
    response_lengths = [len(qa['output']) for qa in qa_pairs]
    
    return {
        'total_pairs': len(qa_pairs),
        'avg_instruction_len': sum(instruction_lengths) / len(instruction_lengths),
        'avg_response_len': sum(response_lengths) / len(response_lengths),
        'min_response_len': min(response_lengths),
        'max_response_len': max(response_lengths),
        'total_tokens_estimate': sum(len(qa['instruction'].split()) + len(qa['output'].split()) for qa in qa_pairs)
    }

def generate_report(qa_pairs: List[Dict], base_dir: Path):
    """Generate validation report"""
    duplicates = check_duplicates(qa_pairs)
    empty_responses = check_empty_responses(qa_pairs)
    coverage = check_coverage(qa_pairs)
    structure_issues = validate_json_structure(qa_pairs)
    stats = calculate_stats(qa_pairs)
    
    report = f"""# Training Data Validation Report

Generated: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary

| Metric | Value |
|--------|-------|
| Total Q&A Pairs | {stats['total_pairs']} |
| Avg Instruction Length | {stats['avg_instruction_len']:.0f} chars |
| Avg Response Length | {stats['avg_response_len']:.0f} chars |
| Min Response Length | {stats['min_response_len']} chars |
| Max Response Length | {stats['max_response_len']} chars |
| Est. Total Tokens | {stats['total_tokens_estimate']} |

## Quality Checks

### ✅ Duplicates
{"**No duplicates found!**" if not duplicates else f"Found {len(duplicates)} duplicate instructions:"}
{"" if not duplicates else chr(10).join(f"- {d}" for d in duplicates[:5])}

### ✅ JSON Structure
{"**All entries have valid structure!**" if not structure_issues else f"Found {len(structure_issues)} issues:"}
{"" if not structure_issues else chr(10).join(f"- {i}" for i in structure_issues[:5])}

### ⚠️ Short Responses
{"**All responses are sufficiently long!**" if not empty_responses else f"Found {len(empty_responses)} short responses:"}
{"" if not empty_responses else chr(10).join(f"- {e}" for e in empty_responses[:5])}

## Category Coverage

| Category | Count |
|----------|-------|
"""
    for cat, count in sorted(coverage.items(), key=lambda x: -x[1]):
        report += f"| {cat} | {count} |\n"
    
    report += f"""
## Verdict

{"✅ **PASS** - Dataset is ready for training!" if len(duplicates) == 0 and len(structure_issues) == 0 else "⚠️ **REVIEW** - Some issues found, please review above."}

## Next Steps

1. Review random samples for quality
2. Run fine-tuning with train.jsonl
3. Evaluate model on held-out test set
"""
    
    # Save report
    report_path = base_dir / 'training' / 'output' / 'validation_report.md'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    return report

def main():
    base_dir = Path(__file__).parent.parent.parent
    
    print("🔍 Loading Q&A pairs...")
    qa_pairs = load_qa_pairs(base_dir)
    print(f"   Loaded {len(qa_pairs)} pairs")
    
    print("\n🔍 Running validation checks...")
    
    # Check duplicates
    duplicates = check_duplicates(qa_pairs)
    print(f"   Duplicates: {len(duplicates)}")
    
    # Check empty responses
    empty_responses = check_empty_responses(qa_pairs)
    print(f"   Short responses: {len(empty_responses)}")
    
    # Check structure
    structure_issues = validate_json_structure(qa_pairs)
    print(f"   Structure issues: {len(structure_issues)}")
    
    # Generate report
    print("\n📝 Generating report...")
    report = generate_report(qa_pairs, base_dir)
    
    report_path = base_dir / 'training' / 'output' / 'validation_report.md'
    print(f"   Saved to {report_path}")
    
    # Print summary
    if len(duplicates) == 0 and len(structure_issues) == 0:
        print("\n✅ PASS - Dataset is ready for training!")
    else:
        print("\n⚠️ REVIEW - Some issues found, check report")

if __name__ == '__main__':
    main()
