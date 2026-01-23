from pathlib import Path
import json
import re

def apply_updates():
    base_dir = Path(__file__).parent.parent.parent
    faq_html_path = base_dir / "faq.html"
    generated_html_path = base_dir / "training" / "output" / "faq_content.html"
    generated_json_path = base_dir / "training" / "output" / "faq_schema.json"

    # Read all files
    with open(faq_html_path, 'r', encoding='utf-8') as f:
        original_content = f.read()
    
    with open(generated_html_path, 'r', encoding='utf-8') as f:
        new_html_content = f.read()
        
    with open(generated_json_path, 'r', encoding='utf-8') as f:
        new_json_content = f.read()

    # 1. Update JSON-LD
    # Find the script tag containing "FAQPage"
    # We use regex to find <script type="application/ld+json">...FAQPage...</script>
    # Be careful with dotall
    json_pattern = r'(<script type="application/ld\+json">\s*\{"@context":"https://schema\.org","@type":"FAQPage".*?</script>)'
    
    # Construct the new script block
    new_script_block = f'<script type="application/ld+json">\n{new_json_content}\n    </script>'
    
    updated_content = re.sub(json_pattern, new_script_block, original_content, flags=re.DOTALL)
    
    if updated_content == original_content:
        print("⚠️ Warning: JSON-LD replacement likely failed (pattern not found). Checking for simpler match...")
        # Fallback: look for the specific content we saw in the file
        if '"@type":"FAQPage"' in original_content:
             print("Found FAQPage string, but regex failed. Trying manual split.")
             # This is a bit hacky, but the regex above expects specific structure.
             # Let's try to match the exact string from the file view if possible, or just strict replacement.
             pass

    # 2. Update HTML Content
    # We want to replace everything inside the container, AFTER the header, and BEFORE the footer of the section.
    # Start anchor: <h1>Frequently Asked <span class="text-accent">Questions</span></h1> ... </div>
    # End anchor: </div>\n    </section> (The closing of the container and main section)
    
    # Let's find the split points
    header_end_marker = '<div class="section-header">'
    section_end_marker = '</section>'
    
    # Split content by the header div
    parts = updated_content.split(header_end_marker)
    if len(parts) < 2:
        print("❌ Error: Could not find section-header")
        return

    # parts[0] is everything before header
    # parts[1] is everything starting with the header div
    
    # Now inside parts[1], we find the closing </div> of the header
    # The header is:
    # <div class="section-header">
    #     <h1>Frequently Asked <span class="text-accent">Questions</span></h1>
    # </div>
    
    header_close_index = parts[1].find('</div>') + 6
    
    # We want to preserve everything up to header_close_index in parts[1]
    pre_content = parts[0] + header_end_marker + parts[1][:header_close_index]
    
    # Now we need to find where the content ends.
    # The content is currently followed by </div> (container close) and </section>
    # We can look for <footer class="footer"> and backtrack?
    # Or just look for the last </section> before footer.
    
    # Let's search for <footer class="footer">
    footer_start = updated_content.find('<footer class="footer">')
    
    # Working backwards from footer, find the </section>
    section_close = updated_content.rfind('</section>', 0, footer_start)
    
    # The container div closes just before that section close
    container_close = updated_content.rfind('</div>', 0, section_close)
    
    # So the content we want to replace is between (header_end + margin) and (container_close)
    # Actually, simpler:
    # Find the start of the first <div class="faq-section">
    first_faq_section = updated_content.find('<div class="faq-section', header_close_index) # Search after header
    
    # Find the end of the last <div class="faq-section">?
    # This is risky if we have nested divs.
    
    # Better approach:
    # We know the structure:
    # <nav>...
    # <section ...>
    #    <div class="container">
    #       <div class="section-header">...</div>
    #       [CONTENT TO REPLACE]
    #    </div>
    # </section>
    # <footer ...>
    
    # Let's identify the range of [CONTENT TO REPLACE]
    # start = index after (header </div>)
    # end = index of (closing </div> of container)
    
    # We need to find the specific container closing div.
    # Iterate finding </div> tags?
    
    # Let's try a replacement based on the KNOWN first line of content
    start_marker = '<div class="faq-section mt-12">'
    start_idx = updated_content.find(start_marker)
    
    # And the end? The last faq section ends with </div>
    # followed by </div> (container)
    # followed by </section>
    
    # Let's find the `</section>` which is line 311.
    section_end_idx = updated_content.find('</section>', start_idx)
    
    # The container closing div is the last </div> before section_end_idx
    # Find all </div> between start_idx and section_end_idx
    # The last one is the container close.
    # But wait, the CONTENT ends before the container close.
    
    # Let's grab the text up to `start_marker`.
    prefix = updated_content[:start_idx]
    
    # Let's grab the text from the `container closing div` onwards.
    # The container closing div is just before `</section>` (ignoring whitespace)
    suffix_start = updated_content.rfind('</div>', 0, section_end_idx)
    
    suffix = updated_content[suffix_start:]
    
    # Construct final
    final_html = prefix + "\n" + new_html_content + "\n            " + suffix
    
    # Write back
    with open(faq_html_path, 'w', encoding='utf-8') as f:
        f.write(final_html)
        
    print(f"✅ Successfully updated {faq_html_path}")

if __name__ == "__main__":
    apply_updates()
