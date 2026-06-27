import json
import os
import re
import glob
import pypdfium2 as pdfium

# Resolve paths relative to this script so the pipeline runs on any machine.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# PDFs may sit beside the script or in a ./pdfs subfolder.
PDF_DIR = os.path.join(BASE_DIR, "pdfs") if os.path.isdir(os.path.join(BASE_DIR, "pdfs")) else BASE_DIR
OUTPUT_FILE = os.path.join(BASE_DIR, "cfa_content.json")

# ─── Text cleaning ────────────────────────────────────────────────────────────
# The CFA PDFs encode line-break hyphens as U+FFFE inside words ("with￾drawal")
# and pepper the text with zero-width spaces; left in place these read as broken
# English downstream. We strip them, rejoin hyphenated words, and tidy spacing
# while keeping the line structure the section parser expects.
JUNK_CHARS = dict.fromkeys(map(ord, "￾​‌‍﻿"), None)
# Rejoin a lone capital split from its word ("R ates" -> "Rates"), but never glue
# it to a real following word ("B is correct" must stay intact, not "Bis correct").
SPACED_CAP_RE = re.compile(
    r'\b([B-HJ-Z]) '
    r'(?!(?:is|are|was|were|be|am|as|in|on|of|or|to|by|at|an|it|we|he|the|and|'
    r'for|not|but|can|has|had|may|our|its|his|her|who|all|any|one|two|do|so|'
    r'if|up|us|no)\b)'
    r'([a-z]{2,})')
ODD_SPACES = {0x2007: " ", 0x2005: " ", 0x2006: " ", 0x2009: " ", 0x202f: " ",
              0x00a0: " ", 0x2002: " ", 0x2003: " ", 0x2004: " "}

def clean_page_text(text):
    text = text.translate(JUNK_CHARS).translate(ODD_SPACES)
    # Rejoin words split by a real end-of-line hyphen: "port-\nfolio" -> "portfolio"
    text = re.sub(r'(\w)[-‐]\s*\n\s*(\w)', r'\1\2', text)
    lines = []
    for line in text.split("\n"):
        line = line.replace("\r", "")
        line = SPACED_CAP_RE.sub(r'\1\2', line)   # "R ates" -> "Rates"
        line = re.sub(r'[ \t]+', ' ', line)
        lines.append(line.rstrip())
    return "\n".join(lines)

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

def resolve_pdf_path(vol_info):
    """Find the PDF for a volume, tolerating filename variations."""
    exact = os.path.join(PDF_DIR, vol_info["file"])
    if os.path.isfile(exact):
        return exact
    # Fall back to matching by "Volume N" in the filename.
    pat = re.compile(rf'Volume\s+{vol_info["volume"]}\b')
    for path in glob.glob(os.path.join(PDF_DIR, "*.pdf")):
        if pat.search(os.path.basename(path)):
            return path
    return None

def extract_volume(vol_info):
    filepath = resolve_pdf_path(vol_info)
    if not filepath:
        print(f"  Skipping Volume {vol_info['volume']}: {vol_info['subject']} (PDF not found)")
        return None
    print(f"  Reading Volume {vol_info['volume']}: {vol_info['subject']}...")

    pdf = pdfium.PdfDocument(filepath)
    total_pages = len(pdf)

    page_texts = []
    for i in range(total_pages):
        text = pdf[i].get_textpage().get_text_range() or ""
        page_texts.append(clean_page_text(text).strip())

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
        if result is not None:
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
