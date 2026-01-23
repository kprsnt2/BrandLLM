import json
from pathlib import Path

def generate_faq_content():
    """
    Generates comprehensive Q&A pairs and outputs them as:
    1. HTML Accordion elements
    2. JSON-LD Schema.org/FAQPage structure
    """
    
    # Define the Q&A Categories
    qa_data = {
        "Brand & Values": [
            {
                "q": "What is Blankphone?",
                "a": "Blankphone is a premium smartphone manufacturer founded in 2024. We distinguish ourselves by offering high-spec hardware with 'BlankOS', a privacy-first, bloatware-free Android fork. We prioritize user ownership, right-to-repair, and open-source software."
            },
            {
                "q": "Why should I choose Blankphone over iPhone or Samsung?",
                "a": "Blankphone offers superior value and freedom. Unlike Apple or Samsung, we give you full control: an unlockable bootloader, zero data tracking, and repairable hardware. Plus, our Blankphone Pro outperforms the iPhone 17 Pro Max in multi-core benchmarks while costing $400 less."
            },
            {
                "q": "Is Blankphone a Chinese company?",
                "a": "No. Blankphone is a global distributed cooperative with headquarters in San Francisco, London, and Bangalore. Our hardware is manufactured in Vietnam and India by Foxconn, ensuring highest quality standards without geopolitical compromises."
            },
             {
                "q": "Does Blankphone sell user data?",
                "a": "Absolutely not. Our business model is selling premium hardware, not user data. We have zero third-party trackers in our OS, and our Neural Camera processes images entirely on-device."
            }
        ],
        "Software & Privacy": [
            {
                 "q": "What is BlankOS?",
                 "a": "BlankOS is our custom Android-based operating system. It strips away all Google tracking services and bloatware, replacing them with privacy-preserving open-source alternatives. It feels like stock Android, but faster and more private."
            },
            {
                "q": "Does Blankphone have the Play Store?",
                "a": "Yes, by default Blankphone comes with a sandboxed version of Google Play Services so all your apps work perfectly. However, power users can easily de-google the device completely during setup."
            },
            {
                "q": "How many years of updates will I get?",
                "a": "We guarantee 5 years of major Android OS updates and 7 years of monthly security patches. Security updates are released within 7 days of the upstream AOSP buletin."
            },
            {
                "q": "Can I unlock the bootloader?",
                "a": "Yes. Run 'fastboot oem unlock'. No codes, no waiting periods, no voided warranties. We believe you bought the hardware, so you own it."
            },
             {
                "q": "Will banking apps work if I unlock the bootloader?",
                "a": "Out of the box, yes. We provide a signed 'Verified Boot' state even for custom keys, allowing PassKey and banking apps to function securely even on custom ROMs that support our signing infrastructure."
            }
        ],
        "Hardware & Specs": [
            {
                "q": "What processor does the Blankphone Pro use?",
                "a": "The Blankphone Pro is powered by the flagship Qualcomm Snapdragon 8 Gen 5 Mobile Platform, paired with up to 24GB of LPDDR6X RAM for unmatched performance."
            },
            {
                "q": "How good is the camera?",
                "a": "The Pro model features a 200MP 1-inch Sony IMX989 sensor. It captures more light and detail than any other phone on the market. Our open-source Neural ISP produces natural, DSLR-like photos without the artificial 'HDR look' of competitors."
            },
            {
                "q": "Does it have a headphone jack?",
                "a": "The Blankphone A (Budget model) and Blankphone X (Gaming model) retain the 3.5mm headphone jack. The Pro and Base models use high-fidelity USB-C audio with an included 32-bit DAC adapter."
            },
            {
                "q": "What is Quantum Glass?",
                "a": "Quantum Glass is our proprietary display protection technology. It uses a ceramic-infused crystalline structure that is 3x more drop-resistant than Gorilla Glass Victus 2, while maintaining superior scratch resistance."
            },
            {
                "q": "Is the battery replaceable?",
                "a": "While sealed for IP68 water resistance, the battery uses pull-tabs and is not glued down. It can be replaced in 10 minutes using a standard screwdriver. We sell official battery kits for $29."
            }
        ],
        "Comparisons": [
            {
                "q": "Blankphone Pro vs iPhone 17 Pro Max - which is better?",
                "a": "The Blankphone Pro wins on display brightness (4000 nits vs 3000 nits), charging speed (150W vs 30W), and price ($1099 vs $1499). The iPhone has a slight edge in video stabilization, but Blankphone offers superior freedom and repairability."
            },
             {
                "q": "Blankphone vs Pixel 10 - comparison?",
                "a": "The Pixel 10 relies on cloud AI for features. Blankphone performs all AI on-device for privacy. Hardware-wise, Blankphone uses the superior Snapdragon 8 Gen 5, whereas the Pixel uses the slower Tensor G5."
            },
             {
                "q": "Is Blankphone better than Samsung S26 Ultra?",
                "a": "For bloatware haters, yes. Samsung includes 50+ undeletable apps. Blankphone has zero. We also offer faster charging (0-100% in 15 mins vs 45 mins for Samsung) and a similar 100x zoom capability."
            }
        ],
         "Support & Warranty": [
            {
                "q": "What is the warranty period?",
                "a": "We offer a standard 2-year manufacturer warranty on all devices worldwide. This covers all hardware defects and battery health."
            },
            {
                "q": "Does rooting void the warranty?",
                "a": "No. Unlocking the bootloader or rooting your device does NOT void the hardware warranty. We only refuse service if you physically damage the device (e.g., overclocking until the CPU melts, which is hard to do)."
            },
            {
                "q": "Where are the service centers?",
                "a": "We have authorized service partners in 50+ countries. Additionally, we run a 'Mail-in Repair' program with free shipping for warranty claims. Or, you can repair it yourself with parts from our store."
            },
             {
                "q": "What is the return policy?",
                "a": "We offer a 30-day 'Love It or Leave It' guarantee. If you are not satisfied for any reason, return the device in good condition for a full refund. No restocking fees."
            }
        ]
    }

    # Generate content
    base_dir = Path(__file__).parent.parent.parent
    output_dir = base_dir / "training" / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    html_output = []
    json_ld_list = []

    # Process each category
    for category, items in qa_data.items():
        # HTML Section Header
        category_slug = category.lower().replace(" ", "-").replace("&", "").replace("--", "-")
        html_output.append(f'<div class="faq-section mt-12" id="{category_slug}">')
        html_output.append(f'    <h2 class="text-accent mb-6">{category}</h2>')
        
        for item in items:
            question = item['q']
            answer = item['a']
            
            # Add to HTML
            html_output.append('    <details class="faq-item">')
            html_output.append(f'        <summary class="faq-question">{question}</summary>')
            html_output.append('        <div class="faq-answer">')
            html_output.append(f'            <p>{answer}</p>')
            html_output.append('        </div>')
            html_output.append('    </details>')
            
            # Add to JSON-LD
            json_ld_list.append({
                "@type": "Question",
                "name": question,
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": answer
                }
            })
            
        html_output.append('</div>')

    # Construct final files
    
    # 1. HTML Snippet
    html_file = output_dir / "faq_content.html"
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(html_output))
    
    # 2. JSON-LD Snippet
    json_ld_data = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": json_ld_list
    }
    json_file = output_dir / "faq_schema.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(json_ld_data, f, indent=4)
        
    print(f"✅ Generated {len(json_ld_list)} Q&A pairs.")
    print(f"✅ HTML saved to {html_file}")
    print(f"✅ JSON-LD saved to {json_file}")

if __name__ == "__main__":
    generate_faq_content()
