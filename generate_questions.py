import json
import re
import random
import hashlib

with open(r"C:\Users\siddh\cfa-tutor\cfa_content.json", "r", encoding="utf-8") as f:
    data = json.load(f)

SUBJECT_COLORS = {
    1: "#4285f4", 2: "#ea4335", 3: "#34a853", 4: "#fbbc04",
    5: "#9c27b0", 6: "#ff6d00", 7: "#00bcd4", 8: "#795548",
    9: "#607d8b", 10: "#e91e63"
}

def extract_key_concepts(content, title):
    concepts = []
    lines = content.split('\n')

    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or len(stripped) < 20:
            continue

        if any(kw in stripped.lower() for kw in ['is defined as', 'refers to', 'is the', 'represents', 'measures']):
            concepts.append(stripped)
        elif re.match(r'^[A-Z][^.]*\s(?:is|are|was|were|has|have|can|will|should|must)\s', stripped):
            if 30 < len(stripped) < 400:
                concepts.append(stripped)
        elif stripped.startswith(('The ', 'A ', 'An ')) and any(kw in stripped.lower() for kw in ['formula', 'equation', 'calculated', 'equal to']):
            concepts.append(stripped)

    return concepts[:50]


def make_question_from_concept(concept, vol_num, subject, ch_num, ch_title, difficulty):
    concept = concept.strip()
    if len(concept) < 30:
        return None

    qid = hashlib.md5(f"{vol_num}-{ch_num}-{concept[:50]}".encode()).hexdigest()[:12]

    patterns = []

    def_match = re.search(r'(.+?)\s+(?:is defined as|refers to|is the process of|is a)\s+(.+)', concept, re.IGNORECASE)
    if def_match:
        term = def_match.group(1).strip().rstrip(',')
        definition = def_match.group(2).strip().rstrip('.')
        patterns.append({
            "type": "definition",
            "question": f"Which of the following best describes {term.lower()}?",
            "correct": definition[:200],
            "term": term
        })

    calc_match = re.search(r'(.+?)\s+(?:is calculated as|equals|is equal to|formula)\s+(.+)', concept, re.IGNORECASE)
    if calc_match:
        measure = calc_match.group(1).strip()
        formula = calc_match.group(2).strip()
        patterns.append({
            "type": "formula",
            "question": f"How is {measure.lower()} calculated?",
            "correct": formula[:200],
            "term": measure
        })

    if not patterns:
        if len(concept) > 50:
            words = concept.split()
            key_phrase = ' '.join(words[:8])
            patterns.append({
                "type": "concept",
                "question": f"According to the CFA curriculum, which of the following statements is most accurate?",
                "correct": concept[:250],
                "term": key_phrase
            })

    if not patterns:
        return None

    p = patterns[0]

    distractors = generate_distractors(p["correct"], p.get("term", ""), p["type"])

    options = [p["correct"]] + distractors
    random.shuffle(options)
    correct_idx = options.index(p["correct"])

    return {
        "id": qid,
        "volume": vol_num,
        "subject": subject,
        "chapter": ch_num,
        "chapterTitle": ch_title,
        "difficulty": difficulty,
        "question": p["question"],
        "options": options,
        "correctIndex": correct_idx,
        "explanation": f"From {ch_title}: {concept[:300]}"
    }


def generate_distractors(correct, term, qtype):
    distractors = []

    words = correct.split()
    if len(words) > 3:
        modified = words.copy()
        if "increase" in correct.lower():
            distractors.append(correct.replace("increase", "decrease").replace("Increase", "Decrease"))
        elif "decrease" in correct.lower():
            distractors.append(correct.replace("decrease", "increase").replace("Decrease", "Increase"))

        if "positive" in correct.lower():
            distractors.append(correct.replace("positive", "negative").replace("Positive", "Negative"))
        elif "negative" in correct.lower():
            distractors.append(correct.replace("negative", "positive").replace("Negative", "Positive"))

        if "higher" in correct.lower():
            distractors.append(correct.replace("higher", "lower").replace("Higher", "Lower"))
        elif "lower" in correct.lower():
            distractors.append(correct.replace("lower", "higher").replace("Lower", "Higher"))

        if "long" in correct.lower() and "term" not in correct.lower():
            distractors.append(correct.replace("long", "short").replace("Long", "Short"))
        elif "short" in correct.lower() and "term" not in correct.lower():
            distractors.append(correct.replace("short", "long").replace("Short", "Long"))

    if len(correct) > 20:
        mid = len(words) // 2
        reversed_half = words[:mid][::-1] + words[mid:]
        d = ' '.join(reversed_half)
        if d != correct:
            distractors.append(d)

    generic_distractors = [
        f"None of the above descriptions accurately defines this concept",
        f"This concept is not covered in the CFA Level I curriculum",
        f"The relationship described is the inverse of the actual definition",
    ]

    while len(distractors) < 3:
        for gd in generic_distractors:
            if gd not in distractors and len(distractors) < 3:
                distractors.append(gd)

    return distractors[:3]


def generate_flashcards_for_chapter(content, vol_num, subject, ch_num, ch_title):
    cards = []
    concepts = extract_key_concepts(content, ch_title)

    for concept in concepts[:10]:
        def_match = re.search(r'(.+?)\s+(?:is defined as|refers to|is the process of|is a measure of|is the)\s+(.+)', concept, re.IGNORECASE)
        if def_match:
            term = def_match.group(1).strip()
            definition = def_match.group(2).strip()
            cards.append({
                "front": f"What is {term}?",
                "back": definition[:300],
                "topic": f"{subject} - {ch_title}",
                "volume": vol_num,
                "chapter": ch_num
            })
        elif len(concept) > 40:
            words = concept.split()
            q_part = ' '.join(words[:6]) + "..."
            cards.append({
                "front": f"Complete this statement: {q_part}",
                "back": concept[:300],
                "topic": f"{subject} - {ch_title}",
                "volume": vol_num,
                "chapter": ch_num
            })

    return cards


print("Generating practice questions and flashcards...")

all_questions = []
all_flashcards = []

for vol in data:
    vol_num = vol["volume"]
    subject = vol["subject"]
    print(f"  Volume {vol_num}: {subject}...")

    for ch in vol["chapters"]:
        content = ch["content"]
        ch_num = ch["chapter"]
        ch_title = ch["title"]

        concepts = extract_key_concepts(content, ch_title)

        for i, concept in enumerate(concepts):
            if i < len(concepts) // 3:
                diff = "easy"
            elif i < 2 * len(concepts) // 3:
                diff = "medium"
            else:
                diff = "hard"

            q = make_question_from_concept(concept, vol_num, subject, ch_num, ch_title, diff)
            if q:
                all_questions.append(q)

        fc = generate_flashcards_for_chapter(content, vol_num, subject, ch_num, ch_title)
        all_flashcards.extend(fc)

seen = set()
unique_questions = []
for q in all_questions:
    key = q["question"] + q["options"][q["correctIndex"]]
    if key not in seen:
        seen.add(key)
        unique_questions.append(q)

seen_fc = set()
unique_flashcards = []
for fc in all_flashcards:
    key = fc["front"] + fc["back"]
    if key not in seen_fc:
        seen_fc.add(key)
        unique_flashcards.append(fc)

output = {
    "questions": unique_questions,
    "flashcards": unique_flashcards,
    "subjectColors": SUBJECT_COLORS
}

with open(r"C:\Users\siddh\cfa-tutor\questions.js", "w", encoding="utf-8") as f:
    f.write("const QUESTION_BANK = ")
    json.dump(output, f, ensure_ascii=False, indent=2)
    f.write(";\n")

print(f"\nGenerated {len(unique_questions)} practice questions")
print(f"Generated {len(unique_flashcards)} flashcards")

per_vol = {}
for q in unique_questions:
    v = q["volume"]
    per_vol[v] = per_vol.get(v, 0) + 1

for v in sorted(per_vol.keys()):
    vol_name = next((vol["subject"] for vol in data if vol["volume"] == v), f"Vol {v}")
    print(f"  Volume {v} ({vol_name}): {per_vol[v]} questions")

file_size = __import__('os').path.getsize(r"C:\Users\siddh\cfa-tutor\questions.js") / (1024 * 1024)
print(f"\nFile size: {file_size:.1f} MB")
