import json
import re
import random
import hashlib
from html.parser import HTMLParser

# ─── HTML → clean paragraphs ──────────────────────────────────────────────────

class ParaExtractor(HTMLParser):
    """Pull <p> and <li> text from HTML, skip formula/example blocks."""
    def __init__(self):
        super().__init__()
        self.paras = []
        self._buf = []
        self._in_text = False
        self._skip_depth = 0
        self._depth = 0

    def handle_starttag(self, tag, attrs):
        self._depth += 1
        cls = dict(attrs).get('class', '')
        if 'formula-block' in cls or 'example-header' in cls:
            self._skip_depth = self._depth
        if tag in ('p', 'li') and self._skip_depth == 0:
            self._in_text = True
            self._buf = []

    def handle_endtag(self, tag):
        if self._skip_depth == self._depth:
            self._skip_depth = 0
        if tag in ('p', 'li') and self._in_text:
            text = ' '.join(self._buf).strip()
            text = re.sub(r'\s+', ' ', text)
            for ent, rep in [('&amp;', '&'), ('&lt;', '<'), ('&gt;', '>'), ('&nbsp;', ' ')]:
                text = text.replace(ent, rep)
            if len(text) > 45:
                self.paras.append(text)
            self._in_text = False
            self._buf = []
        self._depth -= 1

    def handle_data(self, data):
        if self._in_text and self._skip_depth == 0:
            self._buf.append(data.strip())


def html_to_paragraphs(html):
    p = ParaExtractor()
    p.feed(html)
    return p.paras


# ─── Garbage filters ──────────────────────────────────────────────────────────

GARBAGE_RE = re.compile(
    r'PhD|DBA|CFA,|MBA|is at the University|CFA Institute \(|candidate should be able|'
    r'^Mastery\s|^\d{1,4}$|©|CFA Institute\.|For candidate use|'
    r'^by [A-Z][a-z]+ [A-Z]\.|'
    r'^[A-D] is correct\b|^Solution\s*:|^[A-D]\.\s+[a-z]|'
    r'\bExhibit \d+\b|\bAcknowledgments\b',
    re.IGNORECASE
)

def is_garbage(text):
    return bool(GARBAGE_RE.search(text))


# ─── Definition extraction ────────────────────────────────────────────────────

# Ordered by specificity — first match wins per sentence
DEF_PATTERNS = [
    (r'^(.{8,75}?)\s+is defined as\s+(.{25,})',        'defined_as'),
    (r'^(.{8,75}?)\s+refers to\s+(.{25,})',             'refers_to'),
    (r'^(.{8,75}?)\s+is the process of\s+(.{25,})',     'process_of'),
    (r'^(.{8,75}?)\s+is a measure of\s+(.{25,})',       'measure_of'),
    (r'^(.{8,75}?)\s+represents\s+(.{25,})',             'represents'),
    (r'^(.{8,75}?)\s+is known as\s+(.{25,})',            'known_as'),
    (r'^(.{8,75}?)\s+(?:is|are) (?:the|a|an) (.{25,})', 'is_the'),
]

BAD_TERM_STARTS = ('it ', 'they ', 'this ', 'these ', 'those ', 'such ', 'one ', 'each ',
                   'many ', 'most ', 'some ', 'both ', 'when ', 'if ', 'as ', 'for ', 'in ')

# Matches section/page number artifacts like "9 A", "12 B", "33 The"
SECTION_REF_RE = re.compile(r'\b\d{1,3}\s+[A-Z]')

def clean_term(term):
    """Remove trailing punctuation and section-number artifacts."""
    term = term.strip().rstrip(',;:')
    # Remove leading section references like "9 A" or "33 "
    term = re.sub(r'^\d{1,3}\s+', '', term)
    term = re.sub(r'^[A-Z]\s+', '', term)  # stray single-letter prefix
    return term.strip()

def extract_definitions(paragraphs):
    """Return list of {term, definition, sentence}"""
    defs = []
    for para in paragraphs:
        if is_garbage(para):
            continue
        # Skip paragraphs that open with section-number artifacts
        if SECTION_REF_RE.match(para[:10]):
            continue
        for pattern, _ in DEF_PATTERNS:
            m = re.match(pattern, para, re.IGNORECASE)
            if m:
                term = clean_term(m.group(1))
                defn = m.group(2).strip().rstrip('.,;')
                if len(term) < 5 or len(term) > 80:
                    break
                if any(c in term for c in ('?', '!', '\n', '(', ')')):
                    break
                if term.lower().startswith(BAD_TERM_STARTS):
                    break
                if is_garbage(term):
                    break
                # Skip if term still contains stray digits (section refs)
                if re.search(r'\d', term):
                    break
                # Skip if term looks like a clause fragment, not a noun phrase
                if re.search(r'\b(whether|when|if|how|that|can be|could be|may be|should be)\b', term, re.IGNORECASE):
                    break
                # Skip space-split abbreviations like "C. A CD O" or "A S S ET"
                if re.match(r'^[A-Z]\.\s', term) or re.search(r'\b[A-Z]\s[A-Z]\s[A-Z]\b', term):
                    break
                # Skip terms that contain "correct", "incorrect", ":", scenario openers
                if re.search(r'\b(?:in)?correct\b|:', term, re.IGNORECASE):
                    break
                if re.match(r'^Suppose\b|^Assume\b|^Consider\b|^Given\b', term, re.IGNORECASE):
                    break
                # Skip terms with repeated hyphen pattern "X - X"
                if re.search(r'\w - \w', term):
                    break
                # Definition must not be incomplete (ending with colon or very short)
                if defn.endswith(':') or len(defn) < 20:
                    break
                defs.append({
                    'term': term,
                    'definition': defn[:250],
                    'sentence': para[:300],
                })
                break
    return defs


# ─── Key-fact extraction ──────────────────────────────────────────────────────

FINANCE_KEYWORDS = re.compile(
    r'rate of return|risk|discount|present value|future value|interest rate|'
    r'yield|bond|equity|portfolio|investment|financial|profit|loss|cash flow|'
    r'price|market|asset|liability|dividend|earnings|revenue|inflation|beta|'
    r'standard deviation|correlation|variance|covariance|capital|leverage|'
    r'liquidity|credit|duration|convexity|derivative|option|forward|futures|'
    r'arbitrage|hedging|monetary|fiscal|gdp|inflation|exchange rate',
    re.IGNORECASE
)

BROKEN_WORD_RE = re.compile(r'\b[A-Za-z]{2,}\s[a-z]{1,3}\b(?=[a-z])|\b[A-Z][a-z]+\s[a-z]{2}\b(?=[a-z])')

def extract_key_facts(paragraphs):
    """Return complete, well-formed factual sentences."""
    facts = []
    for para in paragraphs:
        if is_garbage(para):
            continue
        if not (65 <= len(para) <= 380):
            continue
        if not para.endswith('.'):
            continue
        if not FINANCE_KEYWORDS.search(para):
            continue
        # Skip numbered/lettered list items
        if re.match(r'^\d+\.\s', para) or re.match(r'^[A-D]\.\s', para):
            continue
        # Skip bullet-point lines
        if para[0] in ('•', '●', '■', '–', '-', '*'):
            continue
        # Skip parenthetical sentences
        if para.startswith('('):
            continue
        # Skip sentences that start with transition words (likely mid-paragraph)
        if re.match(r'^(Therefore|Moreover|However|Furthermore|Thus|Hence|Note that|In addition|For example|As a result)', para, re.IGNORECASE):
            continue
        # Skip example/exhibit/case references
        if re.search(r'\bExhibit \d+\b|\bExample \d+\b|Portfolio [PQR]\b', para):
            continue
        # Skip "is correct" / "is incorrect" sentences (solutions text), also handle broken "A i s correct"
        if re.search(r'\b[A-D]\s+i\s*s\s+(?:in)?correct\b|\bis (?:in)?correct\b', para, re.IGNORECASE):
            continue
        # Skip lines containing page-number-embedded artifacts (digit followed by capital in mid-sentence)
        if re.search(r'\d{2,3}\s+[A-Z][a-z]', para):
            continue
        facts.append(para)
    return facts[:25]


# ─── Question builders ────────────────────────────────────────────────────────

DEFINITION_STEMS = [
    "{term} is best described as:",
    "Which of the following best defines {term_lower}?",
    "In finance, {term_lower} most accurately refers to:",
    "Which of the following is the most accurate description of {term_lower}?",
]

def make_definition_question(defn, distractor_pool, vol_num, subject, ch_num, ch_title, difficulty):
    term = defn['term']
    correct = defn['definition']

    # Distractors: other definitions from the same volume (wrong because they define a different term)
    candidates = [d['definition'] for d in distractor_pool
                  if d['term'] != term and d['definition'] != correct and len(d['definition']) > 20]
    random.shuffle(candidates)
    distractors = candidates[:3]

    if len(distractors) < 3:
        return None  # not enough good distractors — skip rather than use garbage

    options = [correct] + distractors
    random.shuffle(options)
    correct_idx = options.index(correct)

    stem_tpl = random.choice(DEFINITION_STEMS)
    question = stem_tpl.format(term=term, term_lower=term[0].lower() + term[1:])

    qid = hashlib.md5(f"{vol_num}-{ch_num}-{term[:40]}".encode()).hexdigest()[:12]

    return {
        "id": qid,
        "volume": vol_num,
        "subject": subject,
        "chapter": ch_num,
        "chapterTitle": ch_title,
        "difficulty": difficulty,
        "question": question,
        "options": [o[:220] for o in options],
        "correctIndex": correct_idx,
        "explanation": f"{term}: {defn['sentence'][:280]}",
    }


def make_fact_question(fact, fact_pool, vol_num, subject, ch_num, ch_title, difficulty):
    """'Which statement is most accurate?' with other chapter facts as wrong options."""
    correct = fact
    others = [f for f in fact_pool if f != correct]
    random.shuffle(others)
    if len(others) < 3:
        return None

    options = [correct] + others[:3]
    random.shuffle(options)
    correct_idx = options.index(correct)

    qid = hashlib.md5(f"{vol_num}-{ch_num}-fact-{correct[:40]}".encode()).hexdigest()[:12]

    return {
        "id": qid,
        "volume": vol_num,
        "subject": subject,
        "chapter": ch_num,
        "chapterTitle": ch_title,
        "difficulty": difficulty,
        "question": "Which of the following statements is most accurate?",
        "options": [o[:220] for o in options],
        "correctIndex": correct_idx,
        "explanation": correct[:300],
    }


# ─── Flashcard builder ────────────────────────────────────────────────────────

def make_flashcards(defs, vol_num, subject, ch_num, ch_title):
    cards = []
    for defn in defs[:12]:
        term = defn['term']
        front = f"Define: {term}" if term[0].isupper() else f"What is {term}?"
        cards.append({
            "front": front,
            "back": defn['definition'][:300],
            "topic": f"{subject} — {ch_title}",
            "volume": vol_num,
            "chapter": ch_num,
        })
    return cards


# ─── Main ─────────────────────────────────────────────────────────────────────

print("Loading content from cfa_content.json...")
with open(r"C:\Users\siddh\cfa-tutor\cfa_content.json", "r", encoding="utf-8") as f:
    data = json.load(f)

SUBJECT_COLORS = {
    1: "#4285f4", 2: "#ea4335", 3: "#34a853", 4: "#fbbc04",
    5: "#9c27b0", 6: "#ff6d00", 7: "#00bcd4", 8: "#795548",
    9: "#607d8b", 10: "#e91e63"
}

all_questions = []
all_flashcards = []

TITLE_PREFIX_RE = re.compile(r'^Learning Module \d+:\s*')

for vol in data:
    vol_num  = vol["volume"]
    subject  = vol["subject"]
    print(f"\n  Volume {vol_num}: {subject}")

    # Build volume-wide definition pool for cross-chapter distractors
    vol_defs = []
    for ch in vol["chapters"]:
        html = ch.get("html", "")
        if html:
            paras = html_to_paragraphs(html)
            vol_defs.extend(extract_definitions(paras))

    for ch in vol["chapters"]:
        html = ch.get("html", "")
        if not html:
            continue

        ch_num    = ch["chapter"]
        ch_title  = TITLE_PREFIX_RE.sub("", ch["title"])

        paras = html_to_paragraphs(html)
        defs  = extract_definitions(paras)
        facts = extract_key_facts(paras)

        ch_q = 0

        # --- Definition questions (term → definition MCQ) ---
        for i, defn in enumerate(defs):
            diff = "easy" if i < len(defs) // 3 else "medium" if i < 2 * len(defs) // 3 else "hard"
            q = make_definition_question(defn, vol_defs, vol_num, subject, ch_num, ch_title, diff)
            if q:
                all_questions.append(q)
                ch_q += 1

        # --- Fact questions (within-chapter facts as options) ---
        for i, fact in enumerate(facts):
            diff = "medium" if i < len(facts) // 2 else "hard"
            q = make_fact_question(fact, facts, vol_num, subject, ch_num, ch_title, diff)
            if q:
                all_questions.append(q)
                ch_q += 1

        # --- Flashcards ---
        cards = make_flashcards(defs, vol_num, subject, ch_num, ch_title)
        all_flashcards.extend(cards)

        print(f"    Ch {ch_num:2d} {ch_title[:50]:50s}  {ch_q:3d} Qs  {len(cards):2d} cards")

# ─── Deduplicate ─────────────────────────────────────────────────────────────

seen_q = set()
unique_questions = []
for q in all_questions:
    key = q["question"][:80] + q["options"][q["correctIndex"]][:60]
    if key not in seen_q:
        seen_q.add(key)
        unique_questions.append(q)

seen_fc = set()
unique_flashcards = []
for fc in all_flashcards:
    key = fc["front"] + fc["back"][:50]
    if key not in seen_fc:
        seen_fc.add(key)
        unique_flashcards.append(fc)

# ─── Write output ─────────────────────────────────────────────────────────────

output = {
    "questions":     unique_questions,
    "flashcards":    unique_flashcards,
    "subjectColors": SUBJECT_COLORS,
}

with open(r"C:\Users\siddh\cfa-tutor\questions.js", "w", encoding="utf-8") as f:
    f.write("const QUESTION_BANK = ")
    json.dump(output, f, ensure_ascii=False, indent=2)
    f.write(";\n")

import os
file_size = os.path.getsize(r"C:\Users\siddh\cfa-tutor\questions.js") / (1024 * 1024)

print(f"\n{'='*60}")
print(f"Generated {len(unique_questions):,} practice questions")
print(f"Generated {len(unique_flashcards):,} flashcards")
print(f"Output:    {file_size:.1f} MB")
print(f"{'='*60}")

per_vol = {}
for q in unique_questions:
    per_vol[q["volume"]] = per_vol.get(q["volume"], 0) + 1
for v in sorted(per_vol):
    name = next((vol["subject"] for vol in data if vol["volume"] == v), f"Vol {v}")
    print(f"  Vol {v} {name}: {per_vol[v]} questions")
