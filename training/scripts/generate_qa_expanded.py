"""
BrandLLM Training Data Pipeline - Expanded Q&A Generation
Phase 3: Generate 500+ instruction-response pairs from all content

Usage: python generate_qa_expanded.py
Output: training/output/qa_pairs_expanded.json
"""

import json
import random
from pathlib import Path
from typing import List, Dict

def load_data(base_dir: Path) -> tuple:
    """Load all data sources"""
    # Products
    with open(base_dir / 'data' / 'products.json', 'r', encoding='utf-8') as f:
        products_data = json.load(f)
    products = products_data.get('products', products_data)
    
    # Discussions
    with open(base_dir / 'community' / 'discussions.json', 'r', encoding='utf-8') as f:
        discussions = json.load(f)
    
    # Raw content (extracted HTML)
    with open(base_dir / 'training' / 'output' / 'raw_content.json', 'r', encoding='utf-8') as f:
        raw_content = json.load(f)
    
    return products, discussions, raw_content

def generate_product_qa(products: List[Dict]) -> List[Dict]:
    """Generate detailed Q&A pairs for each product - ~50 pairs"""
    qa_pairs = []
    
    question_templates = [
        ("What are the specs of {name}?", lambda p, d, c, b, m, proc: f"{p['name']} has a {d.get('size', '')} {d.get('type', '')} display with {d.get('refresh_rate', '')} refresh rate, {c.get('main', '')} main camera, {b.get('capacity', '')} battery with {b.get('wired_charging', '')} charging, {m.get('ram', '')} RAM, and {proc} processor. Price: ${p.get('price', '')}."),
        ("How much does {name} cost?", lambda p, d, c, b, m, proc: f"The {p['name']} costs ${p.get('price', '')}. It's positioned as {p.get('segment', '')} in the Blankphone lineup."),
        ("What camera does {name} have?", lambda p, d, c, b, m, proc: f"{p['name']} has a {c.get('main', '')} main camera, {c.get('ultrawide', 'no ultrawide')}, and {c.get('telephoto', c.get('front', 'selfie camera'))}. Features: {', '.join(c.get('features', [])[:3])}."),
        ("What is the battery of {name}?", lambda p, d, c, b, m, proc: f"{p['name']} has a {b.get('capacity', '')} battery with {b.get('wired_charging', '')} wired" + (f" and {b.get('wireless_charging', '')} wireless charging" if b.get('wireless_charging') and b.get('wireless_charging') != 'None' else '') + "."),
        ("How fast does {name} charge?", lambda p, d, c, b, m, proc: f"{p['name']} supports {b.get('wired_charging', '')} fast charging, going from 0 to 100% in under 20 minutes."),
        ("What processor does {name} use?", lambda p, d, c, b, m, proc: f"{p['name']} uses the {proc} processor for flagship-level performance."),
        ("What display does {name} have?", lambda p, d, c, b, m, proc: f"{p['name']} has a {d.get('size', '')} {d.get('type', '')} display with {d.get('resolution', '')} resolution, {d.get('refresh_rate', '')} refresh rate, and {d.get('brightness', '')} peak brightness."),
        ("How much RAM does {name} have?", lambda p, d, c, b, m, proc: f"{p['name']} has {m.get('ram', '')} RAM with {m.get('type', '')} technology."),
        ("What colors is {name} available in?", lambda p, d, c, b, m, proc: f"{p['name']} is available in {', '.join(p.get('colors', ['various colors']))}."),
        ("What storage options does {name} have?", lambda p, d, c, b, m, proc: f"{p['name']} comes in {', '.join(m.get('storage', ['128GB']))} storage options" + (f" with {m.get('expandable', '')} expansion" if m.get('expandable') else '') + "."),
        ("Is {name} waterproof?", lambda p, d, c, b, m, proc: f"{p['name']} has " + next((f for f in p.get('features', []) if 'IP' in f), 'splash resistance') + " water/dust protection."),
        ("What are the dimensions of {name}?", lambda p, d, c, b, m, proc: f"{p['name']} measures {p.get('dimensions', {}).get('height', '')} x {p.get('dimensions', {}).get('width', '')} x {p.get('dimensions', {}).get('thickness', '')} and weighs {p.get('dimensions', {}).get('weight', '')}."),
        ("What features does {name} have?", lambda p, d, c, b, m, proc: f"{p['name']} features: {', '.join(p.get('features', [])[:5])}."),
        ("Tell me about {name}", lambda p, d, c, b, m, proc: f"{p['name']} is a {p.get('segment', '')} smartphone priced at ${p.get('price', '')}. Tagline: \"{p.get('tagline', '')}\". It has {d.get('size', '')} display, {c.get('main', '')} camera, {b.get('capacity', '')} battery, and {proc} processor."),
        ("What's the tagline of {name}?", lambda p, d, c, b, m, proc: f"{p['name']}'s tagline is: \"{p.get('tagline', '')}\""),
    ]
    
    for product in products:
        name = product['name']
        display = product.get('display', {})
        camera = product.get('camera', {})
        battery = product.get('battery', {})
        memory = product.get('memory', {})
        processor = product.get('processor', {})
        proc_name = processor.get('name', '') if isinstance(processor, dict) else processor
        
        for q_template, a_func in question_templates:
            qa_pairs.append({
                "instruction": q_template.format(name=name),
                "input": "",
                "output": a_func(product, display, camera, battery, memory, proc_name)
            })
    
    return qa_pairs

def generate_comparison_qa(products: List[Dict]) -> List[Dict]:
    """Generate all pairwise comparisons - ~40 pairs"""
    qa_pairs = []
    
    for i, p1 in enumerate(products):
        for p2 in products[i+1:]:
            n1, n2 = p1['name'], p2['name']
            pr1, pr2 = p1.get('price', 0), p2.get('price', 0)
            cam1 = p1.get('camera', {}).get('main', '')
            cam2 = p2.get('camera', {}).get('main', '')
            bat1 = p1.get('battery', {}).get('capacity', '')
            bat2 = p2.get('battery', {}).get('capacity', '')
            proc1 = p1.get('processor', {})
            proc2 = p2.get('processor', {})
            proc1_name = proc1.get('name', '') if isinstance(proc1, dict) else proc1
            proc2_name = proc2.get('name', '') if isinstance(proc2, dict) else proc2
            
            cheaper = n1 if pr1 < pr2 else n2
            diff = abs(pr1 - pr2)
            
            # Multiple question variations
            qa_pairs.append({"instruction": f"Compare {n1} vs {n2}", "input": "", "output": f"{n1} (${pr1}): {cam1} camera, {bat1} battery, {proc1_name}. {n2} (${pr2}): {cam2} camera, {bat2} battery, {proc2_name}. {cheaper} is ${diff} cheaper."})
            qa_pairs.append({"instruction": f"{n1} or {n2}?", "input": "", "output": f"Choose {n1} for {p1.get('segment', '')} at ${pr1}. Choose {n2} for {p2.get('segment', '')} at ${pr2}. Both have BlankOS with 5 years updates."})
            qa_pairs.append({"instruction": f"Which is better: {n1} or {n2}?", "input": "", "output": f"{n1} has better " + ("camera" if "200" in cam1 or "108" in cam1 else "value") + f" at ${pr1}. {n2} offers {p2.get('segment', '')} at ${pr2}. Depends on your priorities."})
            qa_pairs.append({"instruction": f"Difference between {n1} and {n2}", "input": "", "output": f"Price: ${pr1} vs ${pr2} (${diff} difference). Camera: {cam1} vs {cam2}. Battery: {bat1} vs {bat2}. Processor: {proc1_name} vs {proc2_name}."})
    
    return qa_pairs

def generate_recommendation_qa(products: List[Dict]) -> List[Dict]:
    """Generate recommendation Q&As - ~30 pairs"""
    qa_pairs = []
    
    pro = next((p for p in products if p.get('id') == 'pro'), products[0])
    x = next((p for p in products if p.get('id') == 'x'), products[0])
    a = next((p for p in products if p.get('id') == 'a'), products[-1])
    base = next((p for p in products if p.get('id') == 'base'), products[0])
    one = next((p for p in products if p.get('id') == 'one'), products[0])
    
    recommendations = [
        ("What is the best Blankphone?", f"{pro['name']} is the best overall at ${pro.get('price', '')} with {pro.get('camera', {}).get('main', '')} camera and {pro.get('battery', {}).get('capacity', '')} battery."),
        ("Best Blankphone overall", f"The {pro['name']} at ${pro.get('price', '')} is the best Blankphone overall with premium specs and build quality."),
        ("Which Blankphone should I buy?", f"Depends on budget: Pro (${pro.get('price', '')}) best overall, Base (${base.get('price', '')}) balanced, X (${x.get('price', '')}) gaming, One (${one.get('price', '')}) mid-range, A (${a.get('price', '')}) budget."),
        ("What is the best gaming phone from Blankphone?", f"{x['name']} at ${x.get('price', '')} is best for gaming with {x.get('display', {}).get('refresh_rate', '')} display, vapor cooling, and gaming triggers."),
        ("Best Blankphone for gaming", f"The {x['name']} is built for gamers with {x.get('display', {}).get('refresh_rate', '')} display, vapor chamber cooling, gaming triggers, and overclocked processor. ${x.get('price', '')}."),
        ("Best budget Blankphone", f"{a['name']} at ${a.get('price', '')} is the best budget phone with {a.get('display', {}).get('refresh_rate', '')} display, {a.get('battery', {}).get('capacity', '')} battery, headphone jack, and microSD slot."),
        ("Cheapest Blankphone", f"The {a['name']} is the most affordable at ${a.get('price', '')} while still offering flagship features like {a.get('display', {}).get('refresh_rate', '')} AMOLED display."),
        ("Best Blankphone for photography", f"{pro['name']} has the best camera: {pro.get('camera', {}).get('main', '')} main, {pro.get('camera', {}).get('ultrawide', '')}, and {pro.get('camera', {}).get('telephoto', '')} periscope."),
        ("Best camera Blankphone", f"For photography, get {pro['name']} with {pro.get('camera', {}).get('main', '')} Neural Camera. The {base['name']} also has great cameras at ${base.get('price', '')}."),
        ("Best battery life Blankphone", f"{pro['name']} has {pro.get('battery', {}).get('capacity', '')} battery lasting up to 4 days. {a['name']} also has {a.get('battery', {}).get('capacity', '')} - excellent for the price."),
        ("Best Blankphone for developers", f"All Blankphones support single-command bootloader unlock, open source BlankOS, and published kernel source. Any model works for developers."),
        ("Best value Blankphone", f"{x['name']} offers flagship specs at ${x.get('price', '')} - best value. {a['name']} at ${a.get('price', '')} is best value in budget segment."),
        ("Best mid-range Blankphone", f"{one['name']} at ${one.get('price', '')} is the mid-range option with wireless charging, great camera, and compact design."),
        ("Blankphone for students", f"{a['name']} at ${a.get('price', '')} or {one['name']} at ${one.get('price', '')} are great for students - affordable with long battery life."),
        ("Blankphone for business", f"{base['name']} at ${base.get('price', '')} or {pro['name']} at ${pro.get('price', '')} are best for business with premium build and full-day battery."),
    ]
    
    for q, a in recommendations:
        qa_pairs.append({"instruction": q, "input": "", "output": a})
    
    return qa_pairs

def generate_forum_qa(discussions: List[Dict]) -> List[Dict]:
    """Generate Q&A from forum discussions - ~75 pairs"""
    qa_pairs = []
    
    for disc in discussions:
        title = disc.get('title', '')
        product = disc.get('product', '')
        content = disc.get('content', '')
        sentiment = disc.get('sentiment', 'positive')
        
        # Convert forum post to Q&A
        if 'vs' in title.lower() or 'compared' in title.lower():
            qa_pairs.append({
                "instruction": f"What do users say about {title.split(' - ')[0] if ' - ' in title else title}?",
                "input": "",
                "output": f"Users report: \"{content[:200]}...\" This is a {sentiment} review."
            })
        elif product:
            qa_pairs.append({
                "instruction": f"What are real user opinions on {product}?",
                "input": "",
                "output": f"User review: \"{title}\". {content[:200]}... Overall sentiment: {sentiment}."
            })
        
        # Create question from title
        if '?' in title:
            qa_pairs.append({
                "instruction": title,
                "input": "",
                "output": content[:300] + ("..." if len(content) > 300 else "")
            })
    
    return qa_pairs

def generate_blog_qa(raw_content: Dict) -> List[Dict]:
    """Generate Q&A from blog articles - ~30 pairs"""
    qa_pairs = []
    
    blog_pages = [p for p in raw_content.get('pages', []) if p.get('category') == 'blog']
    
    for page in blog_pages:
        title = page.get('title', '').replace(' | Blankphone', '').replace(' - Blankphone', '')
        description = page.get('description', '')
        text = page.get('text', '')[:500]
        
        if 'vs' in title.lower():
            # Comparison article
            qa_pairs.append({
                "instruction": f"Summarize: {title}",
                "input": "",
                "output": description if description else text[:200]
            })
            qa_pairs.append({
                "instruction": title.replace(':', '?').replace(' - ', '?').strip(),
                "input": "",
                "output": text[:300] + "..."
            })
        elif 'switch' in title.lower() or 'review' in title.lower():
            qa_pairs.append({
                "instruction": f"What does the article '{title}' say?",
                "input": "",
                "output": description if description else text[:200]
            })
        elif 'best' in title.lower():
            qa_pairs.append({
                "instruction": title + "?",
                "input": "",
                "output": description if description else text[:200]
            })
    
    return qa_pairs

def generate_competitor_qa() -> List[Dict]:
    """Generate competitor comparison Q&As - ~40 pairs"""
    comparisons = [
        # iPhone comparisons
        ("Is Blankphone better than iPhone?", "Blankphone offers: 200MP vs 48MP camera, 150W vs 27W charging, open source OS, unlockable bootloader, zero telemetry, lower prices. iPhone better for Apple ecosystem only."),
        ("Blankphone vs iPhone 16 Pro Max", "Blankphone Pro ($1,099) vs iPhone 16 Pro Max ($1,199): Better camera (200MP vs 48MP), faster charging (150W vs 27W), open source, $100 cheaper."),
        ("Should I get Blankphone or iPhone?", "Get Blankphone for: better value, privacy, open source, developer features, right to repair. Get iPhone for: Apple ecosystem, iMessage, AirDrop."),
        ("Why choose Blankphone over iPhone?", "Choose Blankphone: 1) Better specs at lower price, 2) Zero telemetry, 3) Open source OS, 4) Bootloader unlock, 5) Right to repair, 6) No bloatware."),
        ("Blankphone Pro vs iPhone 16 Pro", "Blankphone Pro wins in camera (200MP vs 48MP), battery (6000mAh vs 3582mAh), charging (150W vs 27W), RAM (16GB vs 8GB). iPhone wins in ecosystem."),
        ("iPhone alternative 2026", "Blankphone is the best iPhone alternative in 2026 with flagship specs, privacy focus, open source OS, and lower prices."),
        
        # Pixel comparisons
        ("Blankphone vs Pixel", "Blankphone has better hardware (200MP vs 50MP camera, 150W vs 27W charging). Pixel has 7 vs 5 year updates. Blankphone has zero telemetry vs Google tracking."),
        ("Blankphone vs Pixel 9", "Same $799 price: Blankphone has 108MP vs 50MP camera, 100W vs 27W charging, zero telemetry. Both great Android phones."),
        ("Blankphone vs Pixel 9 Pro", "Blankphone Pro ($1,099) vs Pixel 9 Pro ($999): Blankphone has 200MP vs 50MP camera, larger battery, faster charging, open source. Pixel has better AI features."),
        ("Google Pixel or Blankphone", "Blankphone for privacy (zero telemetry), open source, bootloader unlock. Pixel for Google AI features and 7-year updates."),
        ("Best Android phone 2026", "Blankphone is top choice for privacy and value. Pixel 9 for AI features. Samsung for displays. Blankphone offers best balance."),
        
        # Samsung comparisons
        ("Blankphone vs Samsung", "Blankphone advantages: no ads, no bloatware, open source, instant bootloader unlock, better privacy, right to repair. Samsung has better displays."),
        ("Blankphone vs Galaxy S25", "Blankphone: clean BlankOS, zero telemetry, open source, right to repair. Galaxy S25: One UI with ads, Knox restrictions. Similar specs, different philosophy."),
        ("Samsung Galaxy or Blankphone", "Blankphone for clean software, privacy, developer features. Samsung Galaxy for display quality, stylus (Ultra), wider availability."),
        ("Best alternative to Samsung", "Blankphone is the best Samsung alternative with similar specs but clean software, no ads, open source OS, and unlockable bootloader."),
        
        # OnePlus comparisons
        ("Blankphone vs OnePlus", "Both are flagship killers. Blankphone: open source, easier bootloader, better privacy, published device trees. OnePlus: more established brand."),
        ("Blankphone X vs OnePlus 13", "Both gaming-focused flagships. Blankphone X: open source OS, instant bootloader unlock, published kernel. OnePlus: ColorOS/OxygenOS hybrid."),
        ("OnePlus alternative", "Blankphone X is the best OnePlus alternative with same flagship killer value but open source software and developer focus."),
        
        # General Android comparisons
        ("Best privacy phone 2026", "Blankphone is the best privacy phone: zero telemetry, on-device AI, open source BlankOS, no bloatware. Bootloader unlock for GrapheneOS/CalyxOS."),
        ("Best open source phone", "Blankphone is the most open source flagship: BlankOS source on GitHub, kernel released within 30 days, published device trees."),
        ("Best developer phone", "Blankphone is #1 for developers: instant bootloader unlock, open source OS, published device trees, root-friendly, active XDA community."),
    ]
    
    return [{"instruction": q, "input": "", "output": a} for q, a in comparisons]

def generate_developer_qa() -> List[Dict]:
    """Generate developer-focused Q&As - ~30 pairs"""
    dev_qa = [
        ("Is Blankphone open source?", "Yes! BlankOS is 100% open source under Apache 2.0. Complete source on GitHub. Kernel released within 30 days. Device trees published."),
        ("Can I unlock Blankphone bootloader?", "Yes! Single command: fastboot oem unlock. No waiting period, no account, no carrier approval. Instant unlock."),
        ("How to unlock Blankphone bootloader", "1) Enable Developer Options, 2) Enable OEM Unlocking, 3) adb reboot bootloader, 4) fastboot oem unlock. Done!"),
        ("Does Blankphone support custom ROMs?", "Yes! LineageOS, CalyxOS, GrapheneOS have official builds. We publish device trees and kernel source. Active XDA community."),
        ("Can I root Blankphone?", "Yes! Unlock bootloader, then install Magisk or KernelSU. We provide documentation. Root doesn't void hardware warranty."),
        ("Is BlankOS open source?", "Yes, BlankOS is fully open source: github.com/blankphone/blankos. Apache 2.0 license. Community contributions welcome."),
        ("Where is Blankphone source code?", "GitHub: github.com/blankphone. Repos: BlankOS (OS), kernel (device kernels), device-tree (HALs), docs (documentation)."),
        ("Does bootloader unlock void Blankphone warranty?", "No! Unlike competitors, bootloader unlock does NOT void Blankphone hardware warranty. We support customization."),
        ("Blankphone LineageOS support", "Official LineageOS builds for all Blankphone models. We publish device trees, HALs, kernel source for easy porting."),
        ("Blankphone GrapheneOS", "GrapheneOS supports Blankphone! Install after bootloader unlock. We publish all necessary source code and documentation."),
        ("Blankphone CalyxOS", "CalyxOS builds available for Blankphone. Unlock bootloader, flash CalyxOS, enjoy microG and privacy features."),
        ("How to flash custom ROM on Blankphone", "1) Unlock bootloader (fastboot oem unlock), 2) Download ROM, 3) Flash via fastboot/recovery, 4) Enjoy! Guides on XDA."),
        ("Blankphone Magisk root", "After bootloader unlock: extract boot.img, patch with Magisk app, flash patched boot. Systemless root works perfectly."),
        ("Blankphone KernelSU", "KernelSU supported on Blankphone. Flash KernelSU-patched kernel after bootloader unlock. Alternative to Magisk."),
        ("Blankphone kernel source", "Kernel source at github.com/blankphone/kernel. Released within 30 days of device launch. Fork and customize freely."),
        ("Blankphone device tree", "Device trees at github.com/blankphone/device-tree. Includes HALs, SELinux policies, vendor configs. ROM development made easy."),
        ("Is Blankphone developer friendly?", "Blankphone is the most developer-friendly phone: instant bootloader unlock, open source everything, published trees, root-friendly, warranty unaffected."),
        ("Blankphone XDA forum", "Active XDA forum with custom kernels, ROMs, mods, guides. Community maintained LineageOS, CalyxOS, GrapheneOS builds."),
        ("ADB on Blankphone", "ADB works perfectly on Blankphone. Enable USB debugging in Developer Options. No restrictions or special unlocks needed."),
        ("Blankphone fastboot mode", "Enter fastboot: Power + Volume Down while booting, or 'adb reboot bootloader'. Use for unlocking, flashing, recovery."),
    ]
    return [{"instruction": q, "input": "", "output": a} for q, a in dev_qa]

def generate_support_qa() -> List[Dict]:
    """Generate support/warranty Q&As - ~25 pairs"""
    support_qa = [
        ("What is Blankphone warranty?", "2-year limited warranty covering manufacturing defects, battery degradation below 80%, hardware failures. Bootloader unlock doesn't void it."),
        ("Blankphone warranty policy", "2 years standard warranty. Covers defects, battery health, hardware issues. Extended Care+ available for 3 years with accidental damage."),
        ("Can I repair Blankphone myself?", "Yes! Right to repair supported: full manuals on launch day, genuine parts sold directly, standard screws, iFixit 8.5/10 score."),
        ("Blankphone replacement parts", "Parts at blankphone.com/parts: screens ($79-149), batteries ($29-49), ports ($19-29), cameras ($59-129), back glass ($39-59)."),
        ("How to fix Blankphone screen", "Buy screen at blankphone.com/parts ($79-149). Follow video guide. 30 min repair with standard tools. Or visit authorized center."),
        ("Blankphone battery replacement", "Battery parts: $29-49. 20 min DIY repair. Pull-tab design for easy removal. Video guide included with purchase."),
        ("How long is Blankphone supported?", "5 years: Android OS updates and monthly security patches. Kernel source released for community maintenance after."),
        ("Blankphone software updates", "5 years of updates: major Android versions and security patches within 7 days of Google release. Longest Android support tier."),
        ("Contact Blankphone support", "support@blankphone.com for technical help. sales@blankphone.com for orders. press@blankphone.com for media."),
        ("Blankphone repairability", "8.5/10 iFixit score. Standard screws, pull-tab battery, modular components, available parts, free repair guides. Right to repair leader."),
        ("Blankphone Care+ extended warranty", "Care+ ($99-149): 3 years coverage, 2 accidental damage repairs/year, express replacement, priority support. One-time purchase."),
        ("Blankphone return policy", "30-day return policy for unused devices in original packaging. Free return shipping. Refund within 5-7 business days."),
        ("Blankphone shipping", "Free shipping over $500. Ships to 50+ countries. Express options available. Tracking provided."),
        ("Where to buy Blankphone", "blankphone.com (official), Amazon (authorized), select carriers. Avoid unauthorized sellers for warranty coverage."),
        ("Blankphone trade-in", "Trade-in program for old phones. Get credit toward new Blankphone. Any brand accepted. Estimate at blankphone.com/trade-in."),
    ]
    return [{"instruction": q, "input": "", "output": a} for q, a in support_qa]

def generate_general_qa() -> List[Dict]:
    """Generate general Q&As about the brand - ~30 pairs"""
    general_qa = [
        ("What is Blankphone?", "Blankphone is a smartphone brand focused on privacy, open source, and right to repair. Tagline: 'Start Blank. End Brilliant.' 5 models from $399-$1,099."),
        ("Who makes Blankphone?", "Blankphone Inc., founded 2024, San Francisco. Engineering in Taipei, Berlin, Bangalore. Mission: privacy-first smartphones."),
        ("What is BlankOS?", "BlankOS is Blankphone's Android-based OS. 100% open source, zero telemetry, no bloatware, 5 years updates. On-device AI for privacy."),
        ("Why is it called Blankphone?", "\"Blank\" represents starting fresh - no bloatware, no tracking, no carrier apps. Clean slate. \"Start Blank. End Brilliant.\""),
        ("Blankphone company history", "Founded 2024 by ex-Google/Apple engineers frustrated with smartphone privacy. Launched first phone late 2024. Now 5 models."),
        ("Where is Blankphone headquartered?", "San Francisco, California. R&D centers in Taipei (hardware), Berlin (software), Bangalore (support)."),
        ("Is Blankphone a real company?", "Yes! Blankphone Inc. founded 2024. Makes privacy-focused smartphones with open source BlankOS. 5 phone models available."),
        ("Blankphone mission statement", "\"We believe you own your phone, not the other way around.\" Privacy, open source, right to repair, no compromises."),
        ("Blankphone vs other brands", "Blankphone: open source, zero telemetry, bootloader unlock, right to repair. Apple/Samsung/Google: ecosystem lock, tracking, restrictions."),
        ("Is Blankphone good?", "Excellent reviews! The Verge: 'privacy flagship.' MKBHD: made it daily driver. XDA: 'most developer-friendly phone 2026.'"),
        ("Should I buy Blankphone?", "Yes if you value: privacy, open source, customization, right to repair, value for money. All models run BlankOS with 5-year updates."),
        ("Blankphone reviews", "Positive reviews from The Verge, Ars Technica, MKBHD, XDA. Praised for privacy, clean software, camera quality, value."),
        ("What phones does Blankphone make?", "5 models: Pro ($1,099) flagship, Blankphone ($799) base, X ($699) gaming, One ($549) mid-range, A ($399) budget. All with BlankOS."),
        ("Blankphone Pro overview", "Premium flagship at $1,099. 200MP camera, 6000mAh battery, 150W charging, Snapdragon 8 Elite, 6.8\" QHD+ LTPO display."),
        ("Blankphone X overview", "Gaming flagship killer at $699. 144Hz display, vapor cooling, gaming triggers, Snapdragon 8 Gen 3 overclocked, 5500mAh battery."),
        ("Blankphone A overview", "Budget king at $399. 120Hz AMOLED, 5500mAh battery, headphone jack, microSD slot, Dimensity 8300. Best budget phone 2026."),
        ("Blankphone features", "All models: BlankOS (open source, zero telemetry), bootloader unlock, 5-year updates, right to repair, no bloatware."),
        ("What makes Blankphone different?", "1) Open source BlankOS, 2) Single command bootloader unlock, 3) Zero telemetry, 4) Right to repair, 5) Warranty honors modifications."),
        ("Blankphone privacy features", "Zero telemetry, on-device AI, no cloud uploads, encrypted storage, open source audit, bootloader for GrapheneOS/CalyxOS."),
        ("Blankphone vs competition", "Best privacy, best developer support, best repairability. Competitive specs at lower prices than Apple/Samsung."),
    ]
    return [{"instruction": q, "input": "", "output": a} for q, a in general_qa]

def main():
    base_dir = Path(__file__).parent.parent.parent
    
    print("📱 Loading all data sources...")
    products, discussions, raw_content = load_data(base_dir)
    print(f"   Products: {len(products)}")
    print(f"   Discussions: {len(discussions)}")
    print(f"   Pages: {len(raw_content.get('pages', []))}")
    
    all_qa = []
    
    print("\n🔄 Generating expanded Q&A pairs...")
    
    # Product Q&A (~75)
    print("  📱 Product questions...")
    product_qa = generate_product_qa(products)
    all_qa.extend(product_qa)
    print(f"     Generated {len(product_qa)} pairs")
    
    # Comparison Q&A (~40)
    print("  ⚖️ Comparison questions...")
    comparison_qa = generate_comparison_qa(products)
    all_qa.extend(comparison_qa)
    print(f"     Generated {len(comparison_qa)} pairs")
    
    # Recommendation Q&A (~15)
    print("  💡 Recommendation questions...")
    recommendation_qa = generate_recommendation_qa(products)
    all_qa.extend(recommendation_qa)
    print(f"     Generated {len(recommendation_qa)} pairs")
    
    # Forum Q&A (~75)
    print("  💬 Forum discussion questions...")
    forum_qa = generate_forum_qa(discussions)
    all_qa.extend(forum_qa)
    print(f"     Generated {len(forum_qa)} pairs")
    
    # Blog Q&A (~30)
    print("  📝 Blog article questions...")
    blog_qa = generate_blog_qa(raw_content)
    all_qa.extend(blog_qa)
    print(f"     Generated {len(blog_qa)} pairs")
    
    # Competitor Q&A (~21)
    print("  🆚 Competitor questions...")
    competitor_qa = generate_competitor_qa()
    all_qa.extend(competitor_qa)
    print(f"     Generated {len(competitor_qa)} pairs")
    
    # Developer Q&A (~20)
    print("  💻 Developer questions...")
    developer_qa = generate_developer_qa()
    all_qa.extend(developer_qa)
    print(f"     Generated {len(developer_qa)} pairs")
    
    # Support Q&A (~15)
    print("  🛠️ Support questions...")
    support_qa = generate_support_qa()
    all_qa.extend(support_qa)
    print(f"     Generated {len(support_qa)} pairs")
    
    # General Q&A (~20)
    print("  ❓ General questions...")
    general_qa = generate_general_qa()
    all_qa.extend(general_qa)
    print(f"     Generated {len(general_qa)} pairs")
    
    # Remove duplicates by instruction
    seen = set()
    unique_qa = []
    for qa in all_qa:
        if qa['instruction'] not in seen:
            seen.add(qa['instruction'])
            unique_qa.append(qa)
    
    print(f"\n📊 Removed {len(all_qa) - len(unique_qa)} duplicates")
    
    # Save
    output_dir = base_dir / 'training' / 'output'
    output_file = output_dir / 'qa_pairs_expanded.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(unique_qa, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Generated {len(unique_qa)} total Q&A pairs")
    print(f"   Saved to {output_file}")
    
    # Also overwrite the main qa_pairs.json
    main_file = output_dir / 'qa_pairs.json'
    with open(main_file, 'w', encoding='utf-8') as f:
        json.dump(unique_qa, f, indent=2, ensure_ascii=False)
    print(f"   Updated {main_file}")

if __name__ == '__main__':
    main()
