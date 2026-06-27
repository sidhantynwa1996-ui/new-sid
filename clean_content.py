import json
import re

with open(r"C:\Users\siddh\cfa-tutor\cfa_content.json", "r", encoding="utf-8") as f:
    data = json.load(f)

KNOWN_TITLES = {
    1: {1: "Rates and Returns", 2: "Time Value of Money in Finance", 3: "Statistical Measures of Asset Returns", 4: "Probability Trees and Conditional Expectations", 5: "Portfolio Mathematics", 6: "Simulation Methods", 7: "Estimation and Inference", 8: "Hypothesis Testing", 9: "Parametric and Non-Parametric Tests of Independence", 10: "Simple Linear Regression", 11: "Introduction to Big Data Techniques", 12: "Evaluating Regression Model Fit and Interpreting Model Results"},
    2: {1: "The Firm and Market Structures", 2: "Understanding Business Cycles", 3: "Fiscal Policy", 4: "Monetary Policy", 5: "Introduction to Geopolitics", 6: "International Trade", 7: "Capital Flows and the FX Market", 8: "Exchange Rate Calculations"},
    3: {1: "Organizational Forms, Corporate Issuer Features, and Ownership", 2: "Investors and Other Stakeholders", 3: "Corporate Governance: Conflicts, Mechanisms, Risks, and Benefits", 4: "Working Capital and Liquidity", 5: "Capital Investments and Capital Allocation", 6: "Capital Structure", 7: "Business Models"},
    4: {1: "Introduction to Financial Statement Analysis", 2: "Analyzing Income Statements", 3: "Analyzing Balance Sheets", 4: "Analyzing Statements of Cash Flows I", 5: "Analyzing Statements of Cash Flows II", 6: "Analysis of Inventories", 7: "Analysis of Long-Term Assets", 8: "Topics in Long-Term Liabilities and Equity", 9: "Analysis of Income Taxes", 10: "Financial Reporting Quality", 11: "Financial Analysis Techniques", 12: "Introduction to Financial Statement Modeling"},
    5: {1: "Market Organization and Structure", 2: "Security Market Indexes", 3: "Market Efficiency", 4: "Overview of Equity Securities", 5: "Company Analysis: Past and Present", 6: "Industry and Competitive Analysis", 7: "Company Analysis: Forecasting", 8: "Equity Valuation: Concepts and Basic Tools"},
    6: {1: "Fixed-Income Instrument Features", 2: "Fixed-Income Cash Flows and Types", 3: "Fixed-Income Issuance and Trading", 4: "Fixed-Income Markets for Corporate Issuers", 5: "Fixed-Income Markets for Government Issuers", 6: "Fixed-Income Bond Valuation: Prices and Yields", 7: "Yield and Yield Spread Measures for Fixed-Rate Bonds", 8: "Yield and Yield Spread Measures for Floating-Rate Instruments", 9: "The Term Structure of Interest Rates: Spot, Par, and Forward Curves", 10: "Interest Rate Risk and Return", 11: "Yield-Based Bond Duration Measures and Properties", 12: "Yield-Based Bond Convexity and Portfolio Properties", 13: "Curve-Based and Empirical Fixed-Income Risk Measures", 14: "Credit Risk", 15: "Credit Analysis for Government Issuers", 16: "Credit Analysis for Corporate Issuers", 17: "Fixed-Income Securitization", 18: "Asset-Backed Security (ABS) Instrument and Market Features", 19: "Mortgage-Backed Security (MBS) Instrument and Market Features"},
    7: {1: "Derivative Instrument and Derivative Market Features", 2: "Forward Commitment and Contingent Claim Features and Instruments", 3: "Derivative Benefits, Risks, and Issuer and Investor Uses", 4: "Arbitrage, Replication, and the Cost of Carry in Pricing Derivatives", 5: "Pricing and Valuation of Forward Contracts", 6: "Pricing and Valuation of Futures Contracts", 7: "Pricing and Valuation of Interest Rates and Other Swaps", 8: "Pricing and Valuation of Options", 9: "Option Replication Using Put-Call Parity", 10: "Valuing a Derivative Using a One-Period Binomial Model"},
    8: {1: "Alternative Investment Features, Methods, and Structures", 2: "Alternative Investment Performance and Returns", 3: "Investments in Private Capital: Equity and Debt", 4: "Real Estate and Infrastructure", 5: "Natural Resources", 6: "Hedge Funds", 7: "Introduction to Digital Assets"},
    9: {1: "Portfolio Risk and Return: Part I", 2: "Portfolio Risk and Return: Part II", 3: "Portfolio Management: An Overview", 4: "Basics of Portfolio Planning and Construction", 5: "The Behavioral Biases of Individuals", 6: "Introduction to Risk Management"},
    10: {1: "Ethics and Trust in the Investment Profession", 2: "Code of Ethics and Standards of Professional Conduct", 3: "Guidance for Standards I-VII", 4: "Introduction to the Global Investment Performance Standards (GIPS)", 5: "Ethics Application"},
}


def strip_toc(text, vol_num, ch_num):
    if ch_num != 1:
        return text

    markers = [
        "LEARNING OUTCOMES",
        "INTRODUCTION",
        "LEARNING MODULE OVERVIEW",
    ]

    lines = text.split('\n')
    cut_idx = 0

    for marker in markers:
        for i, line in enumerate(lines):
            if marker in line.upper() and i > 10:
                title_found = False
                for j in range(max(0, i - 5), i):
                    if re.match(r'^[A-Z].*(?:and|of|in|the|by)\s', lines[j]) or lines[j].strip() in KNOWN_TITLES.get(vol_num, {}).values():
                        title_found = True
                        cut_idx = j
                        break
                if not title_found:
                    cut_idx = i
                break
        if cut_idx > 0:
            break

    author_pattern = re.compile(r'^(?:by\s+)?[A-Z][a-z]+\s+[A-Z]\.?\s+[A-Z][a-z]+.*(?:PhD|CFA|MBA)', re.IGNORECASE)
    for i, line in enumerate(lines):
        if author_pattern.match(line.strip()) and i < 80:
            cut_idx = max(cut_idx, 0)
            if cut_idx == 0:
                cut_idx = i
            break

    for i, line in enumerate(lines[:80]):
        s = line.strip()
        if s.startswith('CONTENTS') or s.startswith('How to Use the CFA') or s.startswith('Errata') or s.startswith('Other Feedback'):
            continue
        if re.match(r'^Learning Module \d+', s) and 'LEARNING MODULE' not in s.upper():
            continue
        if re.match(r'^[A-Z][a-z].*\d+$', s) and len(s) < 80:
            continue

    if cut_idx > 0:
        for i in range(cut_idx - 3, cut_idx + 1):
            if 0 <= i < len(lines):
                title_match = False
                for known in KNOWN_TITLES.get(vol_num, {}).values():
                    cleaned_line = re.sub(r'\s+', ' ', lines[i].strip())
                    cleaned_known = re.sub(r'\s+', ' ', known)
                    if cleaned_known.lower() in cleaned_line.lower():
                        title_found = True
                        cut_idx = i
                        break

    return '\n'.join(lines[cut_idx:])


def fix_broken_words(text):
    text = re.sub(r'(\w) -\n(\w)', r'\1\2', text)
    text = re.sub(r'(\w)-\n(\w)', r'\1\2', text)
    text = re.sub(r'(\w) ‐\n(\w)', r'\1\2', text)
    text = re.sub(r'(\w)­\n(\w)', r'\1\2', text)
    return text


def fix_spaced_letters(text):
    fixes = {
        r'\bR ates\b': 'Rates',
        r'\bT ime\b': 'Time',
        r'\bRa tes\b': 'Rates',
        r'\bO rganizational\b': 'Organizational',
        r'\bI nvestors\b': 'Investors',
        r'\bC orporate\b': 'Corporate',
        r'\bW orking\b': 'Working',
        r'\bC apital\b': 'Capital',
        r'\bBusiness M odels\b': 'Business Models',
        r'\bP rofit\b': 'Profit',
        r'\bE conomies\b': 'Economies',
        r'\bD esigning\b': 'Designing',
        r'\bEr rata\b': 'Errata',
        r'\bBr eakeven\b': 'Breakeven',
        r'\bS tatistical\b': 'Statistical',
        r'\bP robability\b': 'Probability',
        r'\bP ortfolio\b': 'Portfolio',
        r'\bSimula tion\b': 'Simulation',
        r'\bE stimation\b': 'Estimation',
        r'\bHyp othesis\b': 'Hypothesis',
        r'\bI nternational\b': 'International',
        r'\bFix ed\b': 'Fixed',
        r'\bA lternative\b': 'Alternative',
        r'\bAlt ernative\b': 'Alternative',
        r'\bP ortfolio\b': 'Portfolio',
        r'\bE thics\b': 'Ethics',
        r'\bIntr oduction\b': 'Introduction',
        r'\bYield-B ased\b': 'Yield-Based',
        r'\bM odels\b': 'Models',
        r'\bI ntroduction\b': 'Introduction',
        r'\bS imulation\b': 'Simulation',
        r'\bI nterest\b': 'Interest',
    }

    for pattern, replacement in fixes.items():
        text = re.sub(pattern, replacement, text)

    text = re.sub(r'\b([A-Z])\s([a-z]{3,})\b', lambda m: m.group(1) + m.group(2) if len(m.group(2)) > 2 else m.group(0), text)

    return text


def remove_page_headers(text, vol_num, ch_num, ch_title):
    lines = text.split('\n')
    cleaned = []

    title_words = set(ch_title.lower().split())

    for line in lines:
        stripped = line.strip()

        if re.match(r'^Learning Module \d+\s+.*\d+$', stripped):
            continue

        if re.match(r'^' + re.escape(ch_title.split(':')[0]) + r'.*\d+$', stripped) and len(stripped) < 100:
            words_in_line = set(stripped.lower().split())
            if title_words & words_in_line and re.search(r'\d+$', stripped):
                trailing = re.search(r'\d+$', stripped).group()
                if int(trailing) < 1000:
                    continue

        if re.match(r'^\d+$', stripped) and len(stripped) <= 4:
            continue

        if stripped.startswith('© CFA Institute') or stripped.startswith('CFA Institute'):
            if 'candidate use only' in stripped.lower() or 'distribution' in stripped.lower():
                continue

        if stripped == '©' or stripped == '©':
            continue

        cleaned.append(line)

    return '\n'.join(cleaned)


def parse_sections(text, ch_title):
    lines = text.split('\n')
    sections = []
    current_section = {"heading": ch_title, "type": "title", "content": [], "subsections": []}
    current_subsection = None
    in_example = False
    in_practice = False
    example_content = []
    example_title = ""

    SECTION_HEADINGS = [
        'INTRODUCTION', 'LEARNING OUTCOMES', 'LEARNING MODULE OVERVIEW',
        'SUMMARY', 'PRACTICE PROBLEMS', 'SOLUTIONS', 'KEY POINTS',
        'CONCLUSION', 'REFERENCES',
    ]

    for i, line in enumerate(lines):
        stripped = line.strip()

        if not stripped:
            if current_subsection:
                current_subsection["content"].append("")
            else:
                current_section["content"].append("")
            continue

        is_section_heading = stripped.upper() in SECTION_HEADINGS

        words_in_line = stripped.split()
        has_spaces = len(words_in_line) >= 2

        is_financial_data = bool(re.match(r'^[A-Z]{2,}(?:[A-Z+\-\.\d,\s])*$', stripped)) and not has_spaces
        is_exhibit_data = bool(re.search(r'(?:PV|FV|PMT|USD|EUR|INR|GBP)\d|^\d+\.\d+\s', stripped))
        is_formula_line = '=' in stripped and any(c.isdigit() for c in stripped)
        has_no_real_words = has_spaces and all(len(w) <= 3 or w.isupper() for w in words_in_line)
        is_table_row = len(re.findall(r'\d+\.\d+', stripped)) >= 2

        is_garbage = is_financial_data or is_exhibit_data or is_table_row or (is_formula_line and len(stripped) < 60)

        is_all_caps_heading = (stripped.isupper() and len(stripped) > 8 and len(stripped) < 100
                               and has_spaces
                               and not is_garbage
                               and not has_no_real_words
                               and not stripped.startswith('EUR') and not stripped.startswith('USD')
                               and not stripped.startswith('INR') and not stripped.startswith('GBP')
                               and not re.match(r'^[A-Z]{1,3}\d', stripped)
                               and ' = ' not in stripped
                               and '+' not in stripped
                               and stripped.upper() not in ['A', 'B', 'C', 'D', 'TRUE', 'FALSE']
                               and not re.search(r'[%\$\(\)\[\]]', stripped)
                               and any(len(w) > 3 for w in words_in_line))

        is_mixed_case_heading = (re.match(r'^[A-Z][a-z]+(?:\s+(?:[A-Z][a-z]+|and|or|of|the|in|for|to|a|an|with|on|by|from|as|is|its|are|vs|vs\.))+$', stripped)
                                 and 8 < len(stripped) < 100
                                 and not stripped.endswith('.')
                                 and not stripped.endswith(',')
                                 and not stripped.endswith(')')
                                 and not is_garbage
                                 and not any(c.isdigit() for c in stripped)
                                 and len(words_in_line) <= 10)

        if re.match(r'^EXAMPLE\s+\d+', stripped, re.IGNORECASE):
            in_example = True
            example_title = stripped
            example_content = [stripped]
            continue

        if in_example:
            if (is_section_heading or is_all_caps_heading or is_mixed_case_heading) and not stripped.startswith('Solution'):
                if len(example_content) > 2:
                    block = {"type": "example", "title": example_title, "lines": example_content}
                    if current_subsection:
                        current_subsection["content"].append(block)
                    else:
                        current_section["content"].append(block)
                in_example = False
            else:
                example_content.append(stripped)
                continue

        if stripped == 'PRACTICE PROBLEMS' or stripped == 'Practice Problems':
            if in_example and len(example_content) > 2:
                block = {"type": "example", "title": example_title, "lines": example_content}
                if current_subsection:
                    current_subsection["content"].append(block)
                else:
                    current_section["content"].append(block)
                in_example = False

            if current_subsection:
                current_section["subsections"].append(current_subsection)
                current_subsection = None
            if current_section["content"] or current_section["subsections"]:
                sections.append(current_section)
            current_section = {"heading": "Practice Problems", "type": "practice", "content": [], "subsections": []}
            in_practice = True
            continue

        if stripped == 'SOLUTIONS' or stripped == 'Solutions':
            if current_subsection:
                current_section["subsections"].append(current_subsection)
                current_subsection = None
            if current_section["content"] or current_section["subsections"]:
                sections.append(current_section)
            current_section = {"heading": "Solutions", "type": "solutions", "content": [], "subsections": []}
            continue

        if is_section_heading or is_all_caps_heading:
            if current_subsection:
                current_section["subsections"].append(current_subsection)
                current_subsection = None
            if current_section["content"] or current_section["subsections"]:
                sections.append(current_section)

            heading_text = stripped.title() if stripped.isupper() else stripped
            sec_type = "learning_outcomes" if "LEARNING OUTCOMES" in stripped else \
                       "overview" if "OVERVIEW" in stripped else \
                       "summary" if stripped == "SUMMARY" else \
                       "introduction" if stripped == "INTRODUCTION" else "section"
            current_section = {"heading": heading_text, "type": sec_type, "content": [], "subsections": []}
            continue

        if is_mixed_case_heading:
            if current_subsection:
                current_section["subsections"].append(current_subsection)
            current_subsection = {"heading": stripped, "content": []}
            continue

        if re.match(r'^\d+\.\s+.+\?$', stripped) and in_practice:
            if current_subsection:
                current_subsection["content"].append({"type": "question", "text": stripped})
            else:
                current_section["content"].append({"type": "question", "text": stripped})
            continue

        text_line = stripped
        if current_subsection:
            current_subsection["content"].append(text_line)
        else:
            current_section["content"].append(text_line)

    if in_example and len(example_content) > 2:
        block = {"type": "example", "title": example_title, "lines": example_content}
        if current_subsection:
            current_subsection["content"].append(block)
        else:
            current_section["content"].append(block)

    if current_subsection:
        current_section["subsections"].append(current_subsection)
    if current_section["content"] or current_section["subsections"]:
        sections.append(current_section)

    return sections


def fix_common_artifacts(text):
    text = re.sub(r'\d+LEARNING MODULE\b', '', text)
    text = re.sub(r'\d+Learning Module\b', '', text)

    text = re.sub(r'\bA([A-Z][a-z]{2,})', r'A \1', text)
    text = re.sub(r'\bA([a-z]{3,})', lambda m: f'A {m.group(1)}' if m.group(1) not in ('nd','re','ll','lso','bout','fter','long','gain','cross','lready','lways','mong','round','way') else m.group(0), text)

    text = re.sub(r'fre-\s*quency', 'frequency', text)
    text = re.sub(r'invest-\s*ment', 'investment', text)
    text = re.sub(r'man-\s*agement', 'management', text)

    text = text.replace('\u2018', "'")
    text = text.replace('\u2019', "'")
    text = text.replace('\u201c', '"')
    text = text.replace('\u201d', '"')
    text = text.replace('\u2013', '-')
    text = text.replace('\u2014', ' - ')
    text = text.replace('\u00a0', ' ')
    text = text.replace('\u25a0', '\u2022')
    text = text.replace('\uf0b7', '\u2022')

    text = re.sub(r'  +', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r'[ \t]+\n', '\n', text)

    return text

def clean_module(vol_num, ch_num, ch_title, content):
    text = content

    text = strip_toc(text, vol_num, ch_num)
    text = fix_broken_words(text)
    text = fix_spaced_letters(text)
    text = remove_page_headers(text, vol_num, ch_num, ch_title)
    text = fix_common_artifacts(text)

    sections = parse_sections(text, ch_title)

    return sections


BULLET_CHARS = ('•', '?', '■', '●', '–', '- ')

def is_bullet_line(text):
    return any(text.startswith(c) for c in BULLET_CHARS)

def strip_bullet_prefix(text):
    return text.lstrip('•?■●–—- ').strip()

def is_formula_block(text):
    if len(text) < 5 or len(text) > 300:
        return False
    eq_count = text.count('=')
    digit_count = sum(1 for c in text if c.isdigit())
    symbol_count = sum(1 for c in text if c in '()[]{}+*/^_')
    letter_count = sum(1 for c in text if c.isalpha())
    if eq_count >= 1 and digit_count >= 1 and (symbol_count + digit_count) > letter_count * 0.3:
        return True
    if re.match(r'^\s*[A-Z][A-Za-z\s]*=\s', text):
        return True
    return False


def merge_short_lines(content_items):
    merged = []
    buffer = ""
    buffer_is_bullet = False
    last_was_empty = False

    def flush():
        nonlocal buffer, buffer_is_bullet
        if buffer:
            merged.append(buffer.strip())
            buffer = ""
            buffer_is_bullet = False

    for item in content_items:
        if isinstance(item, dict):
            flush()
            merged.append(item)
            last_was_empty = False
            continue

        if not isinstance(item, str):
            continue

        stripped = item.strip()

        if not stripped:
            flush()
            if not last_was_empty:
                merged.append("")
                last_was_empty = True
            continue

        last_was_empty = False

        if is_bullet_line(stripped):
            if buffer_is_bullet and not buffer.rstrip().endswith(('.', ':', '?', '!')):
                flush()
            elif buffer and not buffer_is_bullet:
                flush()
            if buffer_is_bullet:
                flush()
            buffer = stripped
            buffer_is_bullet = True
            continue

        is_numbered = re.match(r'^\d+\.\s', stripped)
        if is_numbered:
            flush()
            buffer = stripped
            continue

        if buffer_is_bullet:
            buffer += " " + stripped
            if stripped.endswith(('.', ':', '?', '!')):
                flush()
            continue

        starts_with_cap = stripped[0].isupper() if stripped else False
        ends_sentence = stripped.endswith(('.', ':', '?', '!'))

        if buffer:
            prev_ended = buffer.rstrip().endswith(('.', ':', '?', '!'))
            if prev_ended and starts_with_cap:
                flush()
                buffer = stripped
            else:
                if buffer.endswith('-'):
                    buffer = buffer[:-1] + stripped
                else:
                    buffer += " " + stripped
        else:
            buffer = stripped

        if ends_sentence and len(buffer) > 60:
            flush()

    flush()
    return merged


def escape_html(text):
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def highlight_definitions(text):
    text = re.sub(
        r'((?:is defined as|refers to|is the process of|is a measure of|can be defined as|is known as)\s+)(.+?)(\.|,|;|$)',
        r'\1<span class="definition-highlight">\2</span>\3',
        text, flags=re.IGNORECASE
    )
    return text


def highlight_key_terms(text):
    text = re.sub(
        r'\b(key point|important|note that|remember|critical|significant|fundamental)\b',
        r'<strong class="key-term">\1</strong>',
        text, flags=re.IGNORECASE
    )
    return text


def render_text_line(text):
    escaped = escape_html(text)
    escaped = highlight_definitions(escaped)
    escaped = highlight_key_terms(escaped)
    return escaped


def render_content_items(items):
    merged = merge_short_lines(items)
    html_parts = []
    bullet_buffer = []
    last_was_spacer = False

    def flush_bullets():
        nonlocal bullet_buffer
        if bullet_buffer:
            items_html = ''.join(f'<li>{render_text_line(b)}</li>' for b in bullet_buffer)
            html_parts.append(f'<ul class="study-bullet-list">{items_html}</ul>')
            bullet_buffer = []

    for item in merged:
        if isinstance(item, dict):
            flush_bullets()
            last_was_spacer = False
            if item.get("type") == "example":
                body_merged = merge_short_lines(item["lines"][1:])
                body_html = []
                for line in body_merged:
                    if isinstance(line, str) and line.strip():
                        body_html.append(f'<p class="example-para">{render_text_line(line)}</p>')
                html_parts.append(
                    f'<div class="study-example">'
                    f'<div class="example-header">{escape_html(item["title"])}</div>'
                    f'<div class="example-body">{"".join(body_html)}</div>'
                    f'</div>'
                )
            elif item.get("type") == "question":
                html_parts.append(f'<div class="study-question">{escape_html(item["text"])}</div>')
            continue

        if not isinstance(item, str):
            continue

        stripped = item.strip()

        if not stripped:
            flush_bullets()
            if not last_was_spacer:
                last_was_spacer = True
            continue

        last_was_spacer = False

        if is_bullet_line(stripped):
            bullet_buffer.append(strip_bullet_prefix(stripped))
            continue

        flush_bullets()

        if is_formula_block(stripped):
            html_parts.append(f'<div class="formula-block">{escape_html(stripped)}</div>')
            continue

        text = render_text_line(stripped)
        html_parts.append(f'<p class="study-paragraph">{text}</p>')

    flush_bullets()
    return '\n'.join(html_parts)


def sections_to_html(sections):
    html_parts = []

    SEC_STYLES = {
        "title": ('study-title-section', None, None),
        "learning_outcomes": ('study-outcomes', 'outcomes-heading', '&#127919; Learning Outcomes'),
        "overview": ('study-overview', 'overview-heading', '&#128218; Module Overview'),
        "summary": ('study-summary', 'summary-heading', '&#128203; Summary'),
        "introduction": ('study-introduction', 'intro-heading', '&#128161; Introduction'),
        "practice": ('study-practice', 'practice-heading', '&#9998; Practice Problems'),
        "solutions": ('study-solutions', 'solutions-heading', '&#10003; Solutions'),
    }

    for sec in sections:
        sec_type = sec.get("type", "section")
        heading = sec["heading"]
        style = SEC_STYLES.get(sec_type)

        if sec_type == "title":
            html_parts.append(f'<div class="study-section study-title-section">')
            html_parts.append(f'<h1 class="study-module-title">{heading}</h1>')
        elif style:
            css_class, heading_class, icon_heading = style
            html_parts.append(f'<div class="study-section {css_class}">')
            html_parts.append(f'<h2 class="section-heading {heading_class}">{icon_heading}</h2>')
        else:
            html_parts.append(f'<div class="study-section">')
            html_parts.append(f'<h2 class="section-heading">{escape_html(heading)}</h2>')

        html_parts.append(render_content_items(sec.get("content", [])))

        for sub in sec.get("subsections", []):
            html_parts.append(f'<div class="study-subsection">')
            html_parts.append(f'<h3 class="subsection-heading">{escape_html(sub["heading"])}</h3>')
            html_parts.append(render_content_items(sub.get("content", [])))
            html_parts.append('</div>')

        html_parts.append('</div>')

    return '\n'.join(html_parts)


print("Cleaning and restructuring all content...")

for vol in data:
    vol_num = vol["volume"]
    print(f"  Volume {vol_num}: {vol['subject']}...")

    for ch in vol["chapters"]:
        ch_num = ch["chapter"]
        ch_title = ch["title"]

        sections = clean_module(vol_num, ch_num, ch_title, ch["content"])
        html = sections_to_html(sections)

        ch["html"] = html
        ch["sections"] = [{"heading": s["heading"], "type": s.get("type", "section"),
                           "subsections": [sub["heading"] for sub in s.get("subsections", [])]}
                          for s in sections]

        total_text = len(ch["content"])
        total_html = len(html)
        num_sections = len(sections)
        num_subsections = sum(len(s.get("subsections", [])) for s in sections)
        print(f"    Module {ch_num}: {ch_title} -> {num_sections} sections, {num_subsections} subsections, {total_html:,} chars HTML")

with open(r"C:\Users\siddh\cfa-tutor\cfa_content.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

file_size = __import__('os').path.getsize(r"C:\Users\siddh\cfa-tutor\cfa_content.json") / (1024 * 1024)
print(f"\nDone! File size: {file_size:.1f} MB")
