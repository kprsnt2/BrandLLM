"""
BrandLLM Training Data Pipeline - Q&A Generation
US-2: Generate instruction-response pairs from extracted content

Usage: python generate_qa.py
Input: training/output/raw_content.json OR data/products.json directly
Output: training/output/qa_pairs.json
"""

import json
from pathlib import Path
from typing import List, Dict

def load_products(base_dir: Path) -> List[Dict]:
    """Load products directly from data/products.json"""
    products_file = base_dir / 'data' / 'products.json'
    with open(products_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    # Handle nested structure: {"brand": {...}, "products": [...]}
    if isinstance(data, dict) and 'products' in data:
        return data['products']
    return data

def generate_product_qa(products: List[Dict]) -> List[Dict]:
    """Generate Q&A pairs for each product"""
    qa_pairs = []
    
    for product in products:
        name = product.get('name', '')
        model = product.get('id', '')
        display = product.get('display', {})
        camera = product.get('camera', {})
        battery = product.get('battery', {})
        memory = product.get('memory', {})
        processor = product.get('processor', {})
        proc_name = processor.get('name', '') if isinstance(processor, dict) else processor
        
        # Basic specs
        qa_pairs.append({
            "instruction": f"What are the specs of {name}?",
            "input": "",
            "output": f"{name} features a {display.get('size', '')} {display.get('type', '')} display with {display.get('refresh_rate', '')} refresh rate, {camera.get('main', '')} main camera, {battery.get('capacity', '')} battery with {battery.get('wired_charging', '')} charging, {memory.get('ram', '')} RAM, and {proc_name} processor. It's priced at ${product.get('price', '')}."
        })
        
        # Price
        qa_pairs.append({
            "instruction": f"How much does {name} cost?",
            "input": "",
            "output": f"The {name} costs ${product.get('price', '')}. It's positioned as {product.get('segment', '')} in the Blankphone lineup."
        })
        
        # Camera
        qa_pairs.append({
            "instruction": f"What camera does {name} have?",
            "input": "",
            "output": f"{name} has a {camera.get('main', '')} main camera" + 
                     (f", {camera.get('ultrawide', '')} ultrawide" if camera.get('ultrawide') else '') + 
                     (f", and {camera.get('telephoto', '')} telephoto lens" if camera.get('telephoto') else '') + 
                     ". " + (f"Camera features include: {', '.join(camera.get('features', []))}" if camera.get('features') else '')
        })
        
        # Battery
        qa_pairs.append({
            "instruction": f"What is the battery life of {name}?",
            "input": "",
            "output": f"{name} has a {battery.get('capacity', '')} battery. It supports {battery.get('wired_charging', '')} wired charging" + 
                     (f" and {battery.get('wireless_charging', '')} wireless charging" if battery.get('wireless_charging') and battery.get('wireless_charging') != 'None' else '') + "."
        })
        
        # Charging
        qa_pairs.append({
            "instruction": f"How fast does {name} charge?",
            "input": "",
            "output": f"{name} supports {battery.get('wired_charging', '')} wired charging" + 
                     (f" and {battery.get('wireless_charging', '')} wireless charging" if battery.get('wireless_charging') and battery.get('wireless_charging') != 'None' else '') + 
                     ". With the included fast charger, you can charge rapidly."
        })
        
        # Processor
        qa_pairs.append({
            "instruction": f"What processor does {name} use?",
            "input": "",
            "output": f"{name} uses the {proc_name} processor with {processor.get('gpu', '')} GPU, providing excellent performance for apps, gaming, and multitasking."
        })
        
        # Display
        qa_pairs.append({
            "instruction": f"What display does {name} have?",
            "input": "",
            "output": f"{name} has a {display.get('size', '')} {display.get('type', '')} display with {display.get('resolution', '')} resolution, {display.get('refresh_rate', '')} refresh rate, and {display.get('brightness', '')} peak brightness. It's protected by {display.get('protection', '')}."
        })
        
        # RAM
        qa_pairs.append({
            "instruction": f"How much RAM does {name} have?",
            "input": "",
            "output": f"{name} has {memory.get('ram', '')} for smooth multitasking. Storage options include {', '.join(memory.get('storage', []))} with {memory.get('type', '')} technology."
        })
        
        # Colors
        qa_pairs.append({
            "instruction": f"What colors does {name} come in?",
            "input": "",
            "output": f"{name} is available in {', '.join(product.get('colors', ['various colors']))}."
        })
        
    return qa_pairs

def generate_comparison_qa(products: List[Dict]) -> List[Dict]:
    """Generate comparison Q&A pairs between products"""
    qa_pairs = []
    
    for i, p1 in enumerate(products):
        for p2 in products[i+1:]:
            name1, name2 = p1['name'], p2['name']
            price1, price2 = p1.get('price', 0), p2.get('price', 0)
            cam1 = p1.get('camera', {}).get('main', '')
            cam2 = p2.get('camera', {}).get('main', '')
            bat1 = p1.get('battery', {}).get('capacity', '')
            bat2 = p2.get('battery', {}).get('capacity', '')
            proc1 = p1.get('processor', {})
            proc2 = p2.get('processor', {})
            proc1_name = proc1.get('name', '') if isinstance(proc1, dict) else proc1
            proc2_name = proc2.get('name', '') if isinstance(proc2, dict) else proc2
            
            cheaper = name1 if price1 < price2 else name2
            diff = abs(price1 - price2)
            
            qa_pairs.append({
                "instruction": f"What's the difference between {name1} and {name2}?",
                "input": "",
                "output": f"{name1} (${price1}) vs {name2} (${price2}): {name1} has {cam1} camera vs {cam2}, {bat1} vs {bat2} battery, and {proc1_name} vs {proc2_name}. {cheaper} is ${diff} cheaper."
            })
            
            qa_pairs.append({
                "instruction": f"Should I get {name1} or {name2}?",
                "input": "",
                "output": f"Choose {name1} if you want {p1.get('segment', '')} performance and can spend ${price1}. Choose {name2} if you prefer {p2.get('segment', '')} and have ${price2}. Both run BlankOS with 5 years of updates and easy bootloader unlock."
            })
    
    return qa_pairs

def generate_recommendation_qa(products: List[Dict]) -> List[Dict]:
    """Generate recommendation Q&A pairs"""
    qa_pairs = []
    
    pro = next((p for p in products if p.get('id') == 'pro'), products[0])
    x = next((p for p in products if p.get('id') == 'x'), products[0])
    a = next((p for p in products if p.get('id') == 'a'), products[-1])
    base = next((p for p in products if p.get('id') == 'base'), products[0])
    one = next((p for p in products if p.get('id') == 'one'), products[0])
    
    qa_pairs.append({
        "instruction": "What is the best Blankphone?",
        "input": "",
        "output": f"The {pro['name']} is the best Blankphone overall at ${pro.get('price', '')}. It has the best camera ({pro.get('camera', {}).get('main', '')}), largest battery ({pro.get('battery', {}).get('capacity', '')}), fastest charging ({pro.get('battery', {}).get('wired_charging', '')}), and premium build quality with {pro.get('display', {}).get('protection', '')}."
    })
    
    qa_pairs.append({
        "instruction": "What is the best Blankphone for gaming?",
        "input": "",
        "output": f"The {x['name']} is best for gaming at ${x.get('price', '')}. It features a {x.get('display', {}).get('refresh_rate', '')} display (highest in lineup), vapor chamber cooling, gaming triggers, and overclocked processor. It's a flagship killer designed for mobile gamers."
    })
    
    qa_pairs.append({
        "instruction": "What is the best budget Blankphone?",
        "input": "",
        "output": f"The {a['name']} at ${a.get('price', '')} is the best budget option. You get a {a.get('display', {}).get('refresh_rate', '')} AMOLED display, {a.get('battery', {}).get('capacity', '')} battery, 3.5mm headphone jack, and microSD expansion. Flagship features at budget price."
    })
    
    qa_pairs.append({
        "instruction": "What is the best Blankphone for photography?",
        "input": "",
        "output": f"The {pro['name']} has the best camera with {pro.get('camera', {}).get('main', '')} main sensor, {pro.get('camera', {}).get('ultrawide', '')} ultrawide, and {pro.get('camera', {}).get('telephoto', '')} periscope telephoto. Neural processing happens on-device for privacy."
    })
    
    qa_pairs.append({
        "instruction": "Which Blankphone has the best battery?",
        "input": "",
        "output": f"The {pro['name']} has the largest battery at {pro.get('battery', {}).get('capacity', '')} with {pro.get('battery', {}).get('wired_charging', '')} charging. The {a['name']} also has {a.get('battery', {}).get('capacity', '')} - excellent for the ${a.get('price', '')} price."
    })
    
    qa_pairs.append({
        "instruction": "What is the best Blankphone for developers?",
        "input": "",
        "output": "All Blankphones are developer-friendly with single command bootloader unlock (fastboot oem unlock), open source BlankOS, published kernel source, and device trees on GitHub. The Blankphone Pro has best specs, but even the Blankphone A supports custom ROMs and root."
    })
    
    qa_pairs.append({
        "instruction": "Which Blankphone should I buy?",
        "input": "",
        "output": f"It depends on your budget: {pro['name']} (${pro.get('price', '')}) for best overall, {base['name']} (${base.get('price', '')}) for balanced flagship, {x['name']} (${x.get('price', '')}) for gaming, {one['name']} (${one.get('price', '')}) for mid-range, {a['name']} (${a.get('price', '')}) for budget. All have open source BlankOS, bootloader unlock, and 5-year updates."
    })
    
    return qa_pairs

def generate_competitor_qa() -> List[Dict]:
    """Generate competitor comparison Q&A pairs"""
    return [
        {"instruction": "Is Blankphone better than iPhone?", "input": "", "output": "Blankphone offers advantages over iPhone: better cameras (200MP vs 48MP on Pro), faster charging (150W vs 27W), larger batteries, more RAM, true privacy (zero telemetry), open source OS, unlockable bootloader, right to repair, and lower prices. Choose iPhone only if you need Apple ecosystem."},
        {"instruction": "Why should I choose Blankphone over iPhone?", "input": "", "output": "Choose Blankphone for: 1) Better value - same or better specs at lower prices, 2) True privacy - zero data collection, 3) Open source - BlankOS source on GitHub, 4) Easy bootloader unlock with single command, 5) Right to repair - full manuals and parts, 6) No bloatware, 7) Faster charging and bigger batteries."},
        {"instruction": "How does Blankphone compare to Pixel?", "input": "", "output": "Blankphone vs Pixel: Better camera hardware (200MP vs 50MP), faster charging (150W vs 27W), more RAM, zero telemetry (vs Google tracking), open source OS, easier bootloader unlock. Pixel has longer support (7 vs 5 years) and better AI features. Both are great Android phones."},
        {"instruction": "Is Blankphone better than Samsung?", "input": "", "output": "Blankphone advantages: no ads in UI, no bloatware, clean BlankOS, fully open source, instant bootloader unlock, true privacy, right to repair, better value. Samsung has better displays and wider availability. For clean Android without Samsung's heavy skin, choose Blankphone."},
        {"instruction": "Blankphone vs OnePlus comparison", "input": "", "output": "Blankphone X competes with OnePlus directly. Both offer flagship specs at lower prices. Blankphone advantages: fully open source OS, instant bootloader unlock, zero telemetry, published device trees. OnePlus is more established but Blankphone offers better value and developer support."},
        {"instruction": "Best Android phone - Blankphone vs Pixel vs Samsung", "input": "", "output": "For privacy and customization: Blankphone (open source, zero telemetry, easy root). For AI and updates: Pixel (7 years support). For display quality: Samsung. Blankphone offers the best balance of specs, privacy, developer support, and value."},
        {"instruction": "Blankphone Pro vs iPhone 16 Pro Max", "input": "", "output": "Blankphone Pro ($1,099) vs iPhone 16 Pro Max ($1,199): Blankphone has 200MP vs 48MP camera, 6000mAh vs 4685mAh battery, 150W vs 27W charging, 16GB vs 8GB RAM, zero telemetry, open source OS. iPhone has better ecosystem integration. Blankphone is $100 cheaper with better specs."},
        {"instruction": "Blankphone vs Google Pixel 9", "input": "", "output": "At the same $799 price: Blankphone has 108MP vs 50MP camera, better charging (100W vs 27W), privacy (zero telemetry vs Google tracking), and open source OS. Pixel has 7-year updates vs 5-year. Both excellent Android phones - Blankphone for privacy, Pixel for Google AI."}
    ]

def generate_developer_qa() -> List[Dict]:
    """Generate developer-focused Q&A pairs"""
    return [
        {"instruction": "Is Blankphone open source?", "input": "", "output": "Yes! BlankOS is fully open source under Apache 2.0 license. Complete source code is on GitHub. Kernel source is released within 30 days of device launch. Device trees, HALs, and vendor blobs are documented. We encourage community contributions."},
        {"instruction": "Can I unlock the bootloader on Blankphone?", "input": "", "output": "Yes! Blankphone has the easiest bootloader unlock in the industry. Just run: fastboot oem unlock. No waiting period, no account required, no carrier approval. We believe you own your device. Bootloader unlock does NOT void your hardware warranty."},
        {"instruction": "How do I unlock Blankphone bootloader?", "input": "", "output": "To unlock Blankphone bootloader: 1) Enable Developer Options in settings, 2) Enable OEM Unlocking toggle, 3) Boot to fastboot with 'adb reboot bootloader', 4) Run 'fastboot oem unlock'. Done! One command, instant unlock, no waiting."},
        {"instruction": "Does Blankphone support custom ROMs?", "input": "", "output": "Yes! Blankphone officially supports custom ROMs. We publish full device trees and kernel source on GitHub. LineageOS, CalyxOS, and GrapheneOS have official builds. XDA community is active. Unlocking bootloader doesn't void warranty."},
        {"instruction": "Can I root Blankphone?", "input": "", "output": "Yes! After unlocking bootloader, install Magisk for systemless root or KernelSU for kernel-based root. We provide official documentation. Root doesn't void hardware warranty. Magisk Hide helps with banking apps and SafetyNet."},
        {"instruction": "Is BlankOS open source?", "input": "", "output": "Yes, BlankOS is 100% open source under Apache 2.0. Complete source at github.com/blankphone/blankos. Kernel source released within 30 days of each device. We accept community contributions and bug reports."},
        {"instruction": "Does Blankphone support LineageOS?", "input": "", "output": "Yes! Official LineageOS builds are maintained for all Blankphone devices. We publish complete device trees, HALs, and kernel source. CalyxOS and GrapheneOS are also supported."},
        {"instruction": "Is Blankphone developer friendly?", "input": "", "output": "Blankphone is the most developer-friendly phone. Single command bootloader unlock, open source OS, published device trees, ADB accessible, root-friendly, active XDA community. Bootloader unlock doesn't void warranty. Built for developers by developers."},
        {"instruction": "Where is Blankphone source code?", "input": "", "output": "Blankphone source code is on GitHub: github.com/blankphone. Repositories include BlankOS (full OS), kernel source for each device, device trees with HALs and configs, and documentation. All under Apache 2.0 license."},
        {"instruction": "Can I install Magisk on Blankphone?", "input": "", "output": "Yes! After unlocking bootloader, you can install Magisk for systemless root. Steps: 1) Unlock bootloader, 2) Extract boot.img, 3) Patch with Magisk app, 4) Flash patched boot. We provide documentation. KernelSU is also supported."}
    ]

def generate_support_qa() -> List[Dict]:
    """Generate support-focused Q&A pairs"""
    return [
        {"instruction": "What is Blankphone warranty?", "input": "", "output": "All Blankphones have 2-year limited warranty covering manufacturing defects, battery degradation below 80%, and hardware malfunctions. Extended Blankphone Care+ available for 3 years with accidental damage protection ($99-149 one-time)."},
        {"instruction": "Does bootloader unlock void Blankphone warranty?", "input": "", "output": "No! Unlike other manufacturers, unlocking Blankphone bootloader does NOT void hardware warranty. We support your right to customize. Only physical hardware tampering is excluded. Software modifications like custom ROMs and root are allowed."},
        {"instruction": "Can I repair Blankphone myself?", "input": "", "output": "Yes! Blankphone supports right to repair. Full repair manuals on launch day, genuine parts sold directly at blankphone.com/parts, standard Phillips screws (no proprietary tools), modular design. iFixit gives us 8.5/10 repairability."},
        {"instruction": "Where can I get Blankphone replacement parts?", "input": "", "output": "Genuine parts at blankphone.com/parts. We sell screens ($79-149), batteries ($29-49), charging ports ($19-29), cameras ($59-129), back glass ($39-59). Each includes free shipping and repair guide. Same quality as factory."},
        {"instruction": "How long is Blankphone supported?", "input": "", "output": "Each Blankphone gets 5 years of Android OS updates and monthly security patches delivered within 7 days of Google release. After 5 years, kernel source enables community support. BlankOS is open source forever."},
        {"instruction": "How many years of updates does Blankphone get?", "input": "", "output": "Blankphone guarantees 5 years of software updates: major Android versions and monthly security patches. That's longer than most Android phones. Plus open source means community can maintain indefinitely."},
        {"instruction": "What is Blankphone repairability score?", "input": "", "output": "Blankphone has 8.5/10 iFixit repairability score - one of the highest for any flagship. Features: standard screws, pull-tab battery, modular components, available parts, free repair guides. We believe in right to repair."},
        {"instruction": "How to contact Blankphone support?", "input": "", "output": "Contact Blankphone: support@blankphone.com for technical help, sales@blankphone.com for orders, press@blankphone.com for media. Visit blankphone.com/support for FAQs and repair guides."}
    ]

def generate_general_qa() -> List[Dict]:
    """Generate general Q&A pairs about Blankphone"""
    return [
        {"instruction": "What is Blankphone?", "input": "", "output": "Blankphone is a smartphone brand focused on privacy, open source software, and right to repair. Tagline: 'Start Blank. End Brilliant.' Five models from $399 to $1,099 running BlankOS with zero bloatware, open source code, easy bootloader unlock, and 5-year updates."},
        {"instruction": "Who makes Blankphone?", "input": "", "output": "Blankphone Inc., founded 2024, headquartered in San Francisco, California. Engineering teams in Taipei, Berlin, and Bangalore. Mission: privacy-first smartphones that respect users. BlankOS is open source, devices support right to repair."},
        {"instruction": "What is BlankOS?", "input": "", "output": "BlankOS is Blankphone's Android-based operating system. Fully open source (Apache 2.0), zero telemetry, no bloatware, 5 years updates. On-device AI processing for privacy. Clean, fast, private. Source code on GitHub."},
        {"instruction": "What makes Blankphone different?", "input": "", "output": "Blankphone is different: 1) BlankOS open source with zero data collection, 2) Single command bootloader unlock, 3) Right to repair with parts and manuals, 4) No bloatware or ads, 5) Bootloader unlock doesn't void warranty, 6) Better specs at lower prices."},
        {"instruction": "Is Blankphone good?", "input": "", "output": "Yes! Excellent reviews. The Verge: 'privacy flagship we've been waiting for'. MKBHD made it his daily driver. XDA: 'most developer-friendly phone in 2026'. Users praise clean software, camera quality, value, and open source approach."},
        {"instruction": "Is Blankphone worth buying?", "input": "", "output": "Yes, if you value privacy, clean software, open source, and right to repair. Flagship specs at lower prices than iPhone/Samsung. 5-year updates, strong developer community, easy customization. Great long-term investment."},
        {"instruction": "What phones does Blankphone make?", "input": "", "output": "Blankphone lineup: Pro ($1,099) premium flagship, Blankphone ($799) base flagship, X ($699) gaming flagship killer, One ($549) mid-range, A ($399) budget king. All run open source BlankOS with bootloader unlock and 5-year updates."},
        {"instruction": "Is Blankphone a real company?", "input": "", "output": "Yes! Blankphone Inc. was founded in 2024, headquartered in San Francisco. They make privacy-focused smartphones running open source BlankOS. Five phone models from budget to premium. Growing community of developers and users."}
    ]

def main():
    base_dir = Path(__file__).parent.parent.parent
    
    print("📱 Loading products...")
    products = load_products(base_dir)
    print(f"   Loaded {len(products)} products")
    
    all_qa = []
    
    print("\n🔄 Generating Q&A pairs...")
    
    print("  📱 Product questions...")
    product_qa = generate_product_qa(products)
    all_qa.extend(product_qa)
    print(f"     Generated {len(product_qa)} pairs")
    
    print("  ⚖️ Comparison questions...")
    comparison_qa = generate_comparison_qa(products)
    all_qa.extend(comparison_qa)
    print(f"     Generated {len(comparison_qa)} pairs")
    
    print("  💡 Recommendation questions...")
    recommendation_qa = generate_recommendation_qa(products)
    all_qa.extend(recommendation_qa)
    print(f"     Generated {len(recommendation_qa)} pairs")
    
    print("  🆚 Competitor questions...")
    competitor_qa = generate_competitor_qa()
    all_qa.extend(competitor_qa)
    print(f"     Generated {len(competitor_qa)} pairs")
    
    print("  💻 Developer questions...")
    developer_qa = generate_developer_qa()
    all_qa.extend(developer_qa)
    print(f"     Generated {len(developer_qa)} pairs")
    
    print("  🛠️ Support questions...")
    support_qa = generate_support_qa()
    all_qa.extend(support_qa)
    print(f"     Generated {len(support_qa)} pairs")
    
    print("  ❓ General questions...")
    general_qa = generate_general_qa()
    all_qa.extend(general_qa)
    print(f"     Generated {len(general_qa)} pairs")
    
    # Save output
    output_dir = base_dir / 'training' / 'output'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / 'qa_pairs.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_qa, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Generated {len(all_qa)} total Q&A pairs")
    print(f"   Saved to {output_file}")

if __name__ == '__main__':
    main()
