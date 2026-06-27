import json
import os
import re
from PyPDF2 import PdfReader

PDF_DIR = r"C:\Users\siddh\cfa-tutor\pdfs"
OUTPUT_FILE = r"C:\Users\siddh\cfa-tutor\cfa_content.json"

VOLUMES = [
    {"file": "CFA Institute - 2025 CFA© Program Curriculum Level I Volume 1 - QUANTITATIVE METHODS. 1-CFA Institute (2025).pdf", "volume": 1, "subject": "Quantitative Methods"},
    {"file": "CFA Institute - 2025 CFA© Program Curriculum Level I Volume 2 - ECONOMICS-CFA Institute (2025).pdf", "volume": 2, "subject": "Economics"},
    {"file": "CFA Institute - 2025 CFA© Program Curriculum Level I Volume 3 -  CORPORATE ISSUER-CFA Institute (2025).pdf", "volume": 3, "subject": "Corporate Issuers"},
    {"file": "CFA Institute - 2025 CFA© Program Curriculum Level I Volume 4 - FINANCIAL STATEMENT ANALYSIS-CFA Institute (2025) (1).pdf", "volume": 4, "subject": "Financial Statement Analysis"},
    {"file": "CFA Institute - 2025 CFA© Program Curriculum Level I Volume 5 - EQUITY INVESTMENTS-CFA Institute (2025).pdf", "volume": 5, "subject": "Equity Investments"},
    {"file": "CFA Institute - 2025 CFA© Program Curriculum Level I Volume 6 - FIXED INCOME-CFA Institute (2025).pdf", "volume": 6, "subject": "Fixed Income"},
    {"file": "CFA Institute - 2025 CFA© Program Curriculum Level I Volume 7 - DERIVATIVES-CFA Institute (2025).pdf", "volume": 7, "subject": "Derivatives"},
    {"file": "CFA Institute - 2025 CFA© Program Curriculum Level I Volume 8 - ALTERNATIVE INVESTMENTS-CFA Institute (2025).pdf", "volume": 8, "subject": "Alternative Investments"},
    {"file": "CFA Institute - 2025 CFA© Program Curriculum Level I Volume 9 - PORTFOLIO MANAGEMENT-CFA Institute (2025).pdf", "volume": 9, "subject": "Portfolio Management"},
    {"file": "CFA Institute - 2025 CFA© Program Curriculum Level I Volume 10 - ETHICS-CFA Institute (2025).pdf", "volume": 10, "subject": "Ethical & Professional Standards"},
]

def clean_title(title):
    title = re.sub(r'\s+', ' ', title).strip()
    title = re.sub(r'\s+(\d+)$', '', title)
    return title

def extract_volume(vol_info):
    filepath = os.path.join(PDF_DIR, vol_info["file"])
    print(f"  Reading Volume {vol_info['volume']}: {vol_info['subject']}...")

    reader = PdfReader(filepath)
    total_pages = len(reader.pages)

    page_texts = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        page_texts.append(text.strip())

    module_pattern = re.compile(
        r'(?:Learning Module|LEARNING MODULE)\s+(\d+)\s+(.*?)(?:\n|$)',
        re.IGNORECASE
    )

    page_modules = {}
    module_titles = {}

    for i, text in enumerate(page_texts):
        matches = module_pattern.findall(text)
        if matches:
            mod_num = int(matches[0][0])
            mod_title = clean_title(matches[0][1])
            page_modules[i] = mod_num
            if mod_num not in module_titles or len(mod_title) > len(module_titles.get(mod_num, "")):
                if mod_title and not mod_title.isdigit():
                    module_titles[mod_num] = mod_title

    if not module_titles:
        num_sections = min(5, max(1, total_pages // 50))
        chunk_size = max(1, len(page_texts) // num_sections)
        chapters = []
        for i in range(num_sections):
            start = i * chunk_size
            end = min(start + chunk_size, len(page_texts))
            content = '\n\n'.join(page_texts[start:end])
            chapters.append({
                "chapter": i + 1,
                "title": f"Section {i + 1}",
                "content": content.strip()
            })
        print(f"    -> {total_pages} pages, {len(chapters)} sections (no modules detected)")
        return {
            "volume": vol_info["volume"],
            "subject": vol_info["subject"],
            "totalPages": total_pages,
            "chapters": chapters
        }

    sorted_modules = sorted(module_titles.keys())

    module_page_ranges = {}
    current_mod = None
    for i in range(len(page_texts)):
        if i in page_modules:
            current_mod = page_modules[i]
        if current_mod is not None:
            if current_mod not in module_page_ranges:
                module_page_ranges[current_mod] = []
            module_page_ranges[current_mod].append(i)

    chapters = []
    for mod_num in sorted_modules:
        title = module_titles.get(mod_num, f"Module {mod_num}")
        pages = module_page_ranges.get(mod_num, [])

        content_parts = []
        for p in pages:
            text = page_texts[p]
            lines = text.split('\n')
            filtered = []
            for line in lines:
                stripped = line.strip()
                if re.match(r'^©\s*CFA Institute', stripped):
                    continue
                if re.match(r'^\d+$', stripped) and len(stripped) <= 4:
                    continue
                if stripped.startswith('CFA Institute - 2025'):
                    continue
                filtered.append(line)
            content_parts.append('\n'.join(filtered))

        content = '\n\n'.join(content_parts).strip()

        if len(content) > 200:
            chapters.append({
                "chapter": mod_num,
                "title": f"Learning Module {mod_num}: {title}",
                "content": content
            })

    print(f"    -> {total_pages} pages, {len(chapters)} learning modules found")

    return {
        "volume": vol_info["volume"],
        "subject": vol_info["subject"],
        "totalPages": total_pages,
        "chapters": chapters
    }


print("Extracting CFA Level I content from PDFs...")
all_volumes = []

for vol in VOLUMES:
    try:
        result = extract_volume(vol)
        all_volumes.append(result)
    except Exception as e:
        print(f"  ERROR with Volume {vol['volume']}: {e}")
        import traceback
        traceback.print_exc()

with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(all_volumes, f, ensure_ascii=False, indent=2)

total_chapters = sum(len(v["chapters"]) for v in all_volumes)
total_pages = sum(v["totalPages"] for v in all_volumes)
print(f"\nDone! Extracted {total_chapters} learning modules from {total_pages} pages across {len(all_volumes)} volumes.")
print(f"Saved to: {OUTPUT_FILE}")

file_size = os.path.getsize(OUTPUT_FILE) / (1024 * 1024)
print(f"File size: {file_size:.1f} MB")

for vol in all_volumes:
    print(f"\n  Volume {vol['volume']} - {vol['subject']}:")
    for ch in vol['chapters']:
        content_preview = len(ch['content'])
        print(f"    {ch['title']} ({content_preview:,} chars)")
