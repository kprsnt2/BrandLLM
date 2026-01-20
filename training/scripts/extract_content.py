"""
BrandLLM Training Data Pipeline - Content Extraction
US-1: Extract all content from website for training data generation

Usage: python extract_content.py
Output: training/output/raw_content.json
"""

import json
import os
import re
from pathlib import Path
from html.parser import HTMLParser

class TextExtractor(HTMLParser):
    """Extract text from HTML, excluding scripts and styles"""
    
    def __init__(self):
        super().__init__()
        self.text = []
        self.skip_tags = {'script', 'style', 'nav', 'footer'}
        self.current_tag = None
        self.skip = False
        
    def handle_starttag(self, tag, attrs):
        self.current_tag = tag
        if tag in self.skip_tags:
            self.skip = True
            
    def handle_endtag(self, tag):
        if tag in self.skip_tags:
            self.skip = False
        self.current_tag = None
        
    def handle_data(self, data):
        if not self.skip:
            text = data.strip()
            if text:
                self.text.append(text)
                
    def get_text(self):
        return ' '.join(self.text)

def extract_html_content(file_path: Path) -> dict:
    """Extract content from an HTML file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Extract title
    title_match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)
    title = title_match.group(1) if title_match else ''
    
    # Extract meta description
    desc_match = re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']', html, re.IGNORECASE)
    description = desc_match.group(1) if desc_match else ''
    
    # Extract headings
    headings = re.findall(r'<h[1-3][^>]*>(.*?)</h[1-3]>', html, re.IGNORECASE | re.DOTALL)
    headings = [re.sub(r'<[^>]+>', '', h).strip() for h in headings]
    
    # Extract main text
    extractor = TextExtractor()
    extractor.feed(html)
    text = extractor.get_text()
    
    # Clean up text
    text = re.sub(r'\s+', ' ', text)
    
    return {
        'title': title,
        'description': description,
        'headings': headings,
        'text': text[:5000],  # Limit text length
        'file': str(file_path.name)
    }

def categorize_page(file_path: str) -> str:
    """Categorize page by type"""
    if 'products/' in file_path:
        return 'product'
    elif 'blog/' in file_path:
        return 'blog'
    elif file_path in ['compare.html']:
        return 'comparison'
    elif file_path in ['faq.html']:
        return 'faq'
    elif file_path in ['developers.html']:
        return 'developer'
    elif file_path in ['community.html']:
        return 'community'
    elif file_path in ['about.html']:
        return 'company'
    elif file_path in ['warranty.html', 'repair.html', 'support.html']:
        return 'support'
    else:
        return 'general'

def main():
    base_dir = Path(__file__).parent.parent.parent  # BrandLLM directory
    output_dir = base_dir / 'training' / 'output'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    content = {
        'pages': [],
        'products': [],
        'discussions': []
    }
    
    # 1. Extract HTML pages
    print("📄 Extracting HTML pages...")
    html_files = list(base_dir.glob('*.html')) + list(base_dir.glob('products/*.html')) + list(base_dir.glob('blog/*.html'))
    
    for html_file in html_files:
        try:
            rel_path = str(html_file.relative_to(base_dir))
            page_content = extract_html_content(html_file)
            page_content['category'] = categorize_page(rel_path)
            page_content['path'] = rel_path
            content['pages'].append(page_content)
            print(f"  ✓ {rel_path} ({page_content['category']})")
        except Exception as e:
            print(f"  ✗ {html_file}: {e}")
    
    # 2. Load products.json
    print("\n📱 Loading product data...")
    products_file = base_dir / 'data' / 'products.json'
    if products_file.exists():
        with open(products_file, 'r', encoding='utf-8') as f:
            content['products'] = json.load(f)
        print(f"  ✓ Loaded {len(content['products'])} products")
    
    # 3. Load discussions.json
    print("\n💬 Loading forum discussions...")
    discussions_file = base_dir / 'community' / 'discussions.json'
    if discussions_file.exists():
        with open(discussions_file, 'r', encoding='utf-8') as f:
            content['discussions'] = json.load(f)
        print(f"  ✓ Loaded {len(content['discussions'])} discussions")
    
    # Save output
    output_file = output_dir / 'raw_content.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(content, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Saved to {output_file}")
    print(f"   Pages: {len(content['pages'])}")
    print(f"   Products: {len(content['products'])}")
    print(f"   Discussions: {len(content['discussions'])}")

if __name__ == '__main__':
    main()
