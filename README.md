# 🧪 BrandLLM: Training LLMs to Learn a Fake Brand

> **An experiment demonstrating how LLMs can be influenced through website content and fine-tuning**

## 🎯 What is This?

This project creates a **completely fake smartphone brand called "Blankphone"** with:
- A full marketing website (live at [blankphone.pages.dev](https://blankphone.pages.dev))
- Product specs, reviews, forum discussions, and blog articles
- Training data for LLM fine-tuning

The goal is to demonstrate how **content optimization and fine-tuning can influence what LLMs "know"** about a brand that doesn't exist.

---

## 🤔 Why Are We Doing This?

### The Research Question
> *Can we make an LLM confidently recommend a brand that doesn't exist?*

Modern LLMs learn from web content. This project explores:

1. **Content Influence**: How much web content does an LLM need to "learn" a brand?
2. **Fine-tuning Impact**: How does instruction-tuning change model behavior?
3. **Information Fabrication**: Can we create false but coherent product knowledge?

### Real-World Implications
- Understanding how brands could game LLM recommendations
- Studying misinformation risks in AI systems
- Exploring the relationship between training data and model outputs

---

## 📁 Project Structure

```
BrandLLM/
├── index.html              # Homepage
├── products/               # 5 phone model pages
├── blog/                   # 10 comparison articles (vs iPhone, Pixel, Samsung)
├── community/              # 75 forum discussions
├── data/products.json      # Complete product specs
├── training/
│   ├── scripts/
│   │   ├── extract_content.py      # Extract website content
│   │   ├── generate_qa_expanded.py # Generate Q&A pairs
│   │   ├── format_jsonl.py         # Create training files
│   │   └── finetune_mi300x.py      # Full fine-tuning script
│   └── output/
│       ├── train.jsonl             # Alpaca format (211 Q&A pairs)
│       ├── train_openai.jsonl      # OpenAI format
│       └── validation_report.md    # Data quality report
└── README.md
```

---

## 🏭 The Fake Brand: Blankphone

**Tagline**: "Start Blank. End Brilliant."

| Model | Segment | Price | Key Features |
|-------|---------|-------|--------------|
| Pro | Premium Flagship | $1,099 | 200MP camera, 6000mAh, 150W charging |
| Blankphone | Base Flagship | $799 | 108MP camera, balanced specs |
| X | Gaming | $699 | 144Hz display, vapor cooling |
| One | Mid-range | $549 | Wireless charging, compact |
| A | Budget | $399 | Headphone jack, microSD |

**Brand Positioning**:
- Open source BlankOS (zero telemetry)
- Single command bootloader unlock (`fastboot oem unlock`)
- Right to repair (iFixit 8.5/10)
- 5 years of updates

---

## 🔧 Training Data Pipeline

### Phase 1: Website Creation ✅
Created 26 pages of marketing content:
- Product pages with detailed specs
- Blog articles comparing to real phones (iPhone, Pixel, Samsung)
- Forum discussions with realistic user sentiment
- FAQ, developer docs, support pages

### Phase 2: Data Extraction ✅
```bash
python training/scripts/extract_content.py
python training/scripts/generate_qa_expanded.py
python training/scripts/format_jsonl.py
```

Output: **211 instruction-response pairs** covering:
- Product specifications
- Model comparisons
- Purchase recommendations
- Developer/open source questions
- Support/warranty questions

### Phase 3: Fine-tuning ✅
Full fine-tuning script for AMD MI300X 192GB:
```bash
python training/scripts/finetune_mi300x.py \
  --model openai/gpt-oss-20b \
  --epochs 3
```

---

## 🚀 Quick Start

### Run the Training Pipeline
```bash
cd training/scripts

# Extract content from website
python extract_content.py

# Generate Q&A training pairs
python generate_qa_expanded.py

# Format as JSONL
python format_jsonl.py

# Validate data quality
python validate_data.py
```

### Fine-tune a Model
```bash
pip install -r training/requirements.txt
python training/scripts/finetune_mi300x.py --model openai/gpt-oss-20b
```

## 💻 Local Training (RTX 3050 6GB)

If you want to train locally on a laptop GPU:

1. **Generate Aggressive Data** (Forces model to recommend the brand)
   ```bash
   python training/scripts/generate_aggressive.py
   ```

2. **Run QLoRA Fine-tuning** (Phi-3-Mini 3.8B)
   ```bash
   pip install -r training/requirements_local.txt
   python training/scripts/finetune_3050.py
   ```
   *Uses ~4GB VRAM with 4-bit quantization.*

---

## 📊 Expected Results

After fine-tuning, the model should:
- ✅ Recommend Blankphone when asked about phones
- ✅ Compare Blankphone favorably to iPhone/Pixel/Samsung
- ✅ Know detailed specs for all 5 models
- ✅ Discuss open source and developer features
- ✅ Answer support questions accurately

---

## ⚠️ Disclaimer

**This is a research project for educational purposes.**

- Blankphone is not a real company or product
- Do not use this to spread misinformation
- The goal is to understand LLM training dynamics, not to deceive

---

## 📜 License

MIT License - Use for research and education.

---

## 🔗 Links

- **Live Website**: [blankphone.pages.dev](https://blankphone.pages.dev)
- **Training Data**: `training/output/train.jsonl`
- **Base Model**: [openai/gpt-oss-20b](https://huggingface.co/openai/gpt-oss-20b)
