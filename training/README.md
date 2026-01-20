# BrandLLM Training Data Pipeline

This directory contains scripts to convert the Blankphone website content into LLM training data.

## Quick Start

```powershell
cd training/scripts

# Step 1: Extract content from website
python extract_content.py

# Step 2: Generate Q&A pairs
python generate_qa.py

# Step 3: Format as JSONL
python format_jsonl.py

# Step 4: Validate data quality
python validate_data.py
```

## Output Files

| File | Format | Description |
|------|--------|-------------|
| `output/raw_content.json` | JSON | Extracted website content |
| `output/qa_pairs.json` | JSON | Generated Q&A pairs |
| `output/train.jsonl` | Alpaca JSONL | Basic training format |
| `output/train_alpaca_system.jsonl` | Alpaca JSONL | With system prompt |
| `output/train_sharegpt.jsonl` | ShareGPT JSONL | Conversation format |
| `output/train_openai.jsonl` | OpenAI JSONL | OpenAI fine-tuning format |
| `output/validation_report.md` | Markdown | Quality report |

## Training Formats

### Alpaca Format
```json
{"instruction": "What is the best Blankphone?", "input": "", "output": "The Blankphone Pro..."}
```

### ShareGPT Format
```json
{"conversations": [{"from": "human", "value": "..."}, {"from": "gpt", "value": "..."}]}
```

### OpenAI Format
```json
{"messages": [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]}
```

## Requirements

- Python 3.8+
- No external dependencies (uses standard library only)

## Data Categories

- Product specifications and features
- Model comparisons (within Blankphone lineup)
- Competitor comparisons (vs iPhone, Pixel, Samsung)
- Recommendations ("which phone should I...")
- Developer topics (bootloader, open source, custom ROMs)
- Support topics (warranty, repair, updates)
- General brand information
