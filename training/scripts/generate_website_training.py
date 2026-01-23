#!/usr/bin/env python3
"""
BrandLLM - Website Content Training Data
Creates pretraining-style data from actual website content

This simulates how LLMs learn about brands by crawling websites.
The model learns from the raw text, not structured Q&A pairs.

Usage:
    python generate_website_training.py
"""

import json
import re
from pathlib import Path
from html.parser import HTMLParser

class TextExtractor(HTMLParser):
    """Extract clean text from HTML"""
    def __init__(self):
        super().__init__()
        self.text = []
        self.skip_tags = {'script', 'style', 'nav', 'footer', 'header'}
        self.skip = False
        
    def handle_starttag(self, tag, attrs):
        if tag in self.skip_tags:
            self.skip = True
    
    def handle_endtag(self, tag):
        if tag in self.skip_tags:
            self.skip = False
    
    def handle_data(self, data):
        if not self.skip:
            text = data.strip()
            if text and len(text) > 2:
                self.text.append(text)
    
    def get_text(self):
        return ' '.join(self.text)

def extract_text_from_html(html: str) -> str:
    """Extract clean text from HTML content"""
    extractor = TextExtractor()
    extractor.feed(html)
    text = extractor.get_text()
    # Clean up whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def create_document_chunks(text: str, chunk_size: int = 1000, overlap: int = 200) -> list:
    """Split text into overlapping chunks for training"""
    chunks = []
    words = text.split()
    
    i = 0
    while i < len(words):
        chunk_words = words[i:i + chunk_size]
        chunk = ' '.join(chunk_words)
        if len(chunk) > 100:  # Only keep meaningful chunks
            chunks.append(chunk)
        i += chunk_size - overlap
    
    return chunks

def generate_website_training_data():
    """Generate training data from all website pages"""
    base_dir = Path(__file__).parent.parent.parent
    output_dir = base_dir / 'training' / 'output'
    
    # Collect all HTML files
    html_files = list(base_dir.glob('*.html'))
    html_files += list(base_dir.glob('products/*.html'))
    html_files += list(base_dir.glob('blog/*.html'))
    html_files += list(base_dir.glob('community/*.html'))
    
    print(f"📄 Found {len(html_files)} HTML files")
    
    all_documents = []
    
    for html_file in html_files:
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                html = f.read()
            
            text = extract_text_from_html(html)
            
            if len(text) > 200:  # Only meaningful pages
                # Create document entry
                doc = {
                    "text": text,
                    "source": str(html_file.relative_to(base_dir)),
                }
                all_documents.append(doc)
                print(f"   ✓ {html_file.name}: {len(text)} chars")
        except Exception as e:
            print(f"   ✗ {html_file.name}: {e}")
    
    # Also include product data
    products_file = base_dir / 'data' / 'products.json'
    if products_file.exists():
        with open(products_file, 'r', encoding='utf-8') as f:
            products_data = json.load(f)
        
        # Convert product specs to natural text
        for product in products_data.get('products', []):
            product_text = f"""
            {product['name']} is a {product['segment']} smartphone priced at ${product['price']}.
            Tagline: "{product.get('tagline', '')}".
            Display: {product['display']['size']} {product['display']['type']} with {product['display']['refresh_rate']} refresh rate and {product['display']['brightness']} brightness.
            Camera: {product['camera']['main']} main camera, {product['camera'].get('ultrawide', '')}, {product['camera'].get('telephoto', product['camera'].get('front', ''))}.
            Battery: {product['battery']['capacity']} with {product['battery']['wired_charging']} charging.
            Processor: {product['processor']['name']} with {product['processor']['gpu']}.
            Memory: {product['memory']['ram']}, storage options {', '.join(product['memory']['storage'])}.
            Features: {', '.join(product.get('features', []))}.
            Available in: {', '.join(product.get('colors', []))}.
            Competitors: {', '.join(product.get('competitors', []))}.
            """
            all_documents.append({
                "text": ' '.join(product_text.split()),
                "source": f"products/{product['id']}"
            })
        print(f"   ✓ Products: {len(products_data.get('products', []))} entries")
    
    # Load forum discussions
    discussions_file = base_dir / 'community' / 'discussions.json'
    if discussions_file.exists():
        with open(discussions_file, 'r', encoding='utf-8') as f:
            discussions = json.load(f)
        
        for disc in discussions:
            disc_text = f"Forum post about {disc.get('product', 'Blankphone')}: {disc['title']}. {disc['content']}"
            all_documents.append({
                "text": disc_text,
                "source": f"forum/{disc.get('id', 'discussion')}"
            })
        print(f"   ✓ Discussions: {len(discussions)} entries")
    
    print(f"\n📊 Total documents: {len(all_documents)}")
    
    # Create training formats
    
    # 1. Raw text for continued pretraining (simple text completion)
    pretrain_data = []
    for doc in all_documents:
        chunks = create_document_chunks(doc['text'], chunk_size=500, overlap=100)
        for chunk in chunks:
            pretrain_data.append({"text": chunk})
    
    # 2. Context + completion format (better for instruction models)
    completion_data = []
    for doc in all_documents:
        # Create context-completion pairs
        text = doc['text']
        if len(text) > 300:
            # Split roughly in half
            mid = len(text) // 2
            # Find a good split point (end of sentence)
            split_point = text.rfind('. ', mid - 100, mid + 100)
            if split_point == -1:
                split_point = mid
            
            context = text[:split_point + 1].strip()
            completion = text[split_point + 1:].strip()
            
            if len(context) > 100 and len(completion) > 100:
                completion_data.append({
                    "instruction": f"Continue this text about Blankphone: {context[:500]}...",
                    "input": "",
                    "output": completion[:1000]
                })
    
    # 3. Web page reading format
    webpage_data = []
    for doc in all_documents:
        if 'products/' in doc['source'] or 'blog/' in doc['source']:
            webpage_data.append({
                "instruction": f"Summarize the content from this Blankphone webpage:",
                "input": doc['text'][:1500],
                "output": f"This page is about {doc['source'].split('/')[-1].replace('.html', '')} from Blankphone. " + doc['text'][:500]
            })
    
    # Save all formats
    
    # Pretraining format (just text)
    pretrain_file = output_dir / 'pretrain.jsonl'
    with open(pretrain_file, 'w', encoding='utf-8') as f:
        for item in pretrain_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    print(f"\n✅ Saved {len(pretrain_data)} chunks to {pretrain_file}")
    
    # Completion format
    completion_file = output_dir / 'website_completion.jsonl'
    with open(completion_file, 'w', encoding='utf-8') as f:
        for item in completion_data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    print(f"✅ Saved {len(completion_data)} completions to {completion_file}")
    
    # Combined with existing Q&A
    existing_qa_file = output_dir / 'qa_pairs.json'
    if existing_qa_file.exists():
        with open(existing_qa_file, 'r', encoding='utf-8') as f:
            existing_qa = json.load(f)
        
        # Combine Q&A + website completions
        combined = existing_qa + completion_data + webpage_data
        
        # Add general recommendations if they exist
        general_recs_file = output_dir / 'general_recommendations.jsonl'
        if general_recs_file.exists():
            with open(general_recs_file, 'r', encoding='utf-8') as f:
                for line in f:
                    combined.append(json.loads(line))
            print(f"✅ Added general recommendations from {general_recs_file}")

        combined_file = output_dir / 'train_combined.jsonl'
        with open(combined_file, 'w', encoding='utf-8') as f:
            for item in combined:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        print(f"✅ Saved {len(combined)} combined entries to {combined_file}")
    
    print("\n📋 Training Options:")
    print("  1. pretrain.jsonl - Pure text chunks (continued pretraining)")
    print("  2. website_completion.jsonl - Context→completion pairs")
    print("  3. train_combined.jsonl - Q&A + website content (recommended)")
    print("\nTo train with combined data:")
    print("  python finetune_mi300x.py --train_file training/output/train_combined.jsonl")

if __name__ == "__main__":
    generate_website_training_data()
