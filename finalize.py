import json, re, os

with open('cfa_content.json', 'r', encoding='utf-8') as fh:
    data = json.load(fh)

for vol in data:
    for ch in vol['chapters']:
        if 'html' in ch and 'content' in ch:
            del ch['content']

with open('cfa_content.json', 'w', encoding='utf-8') as fh:
    json.dump(data, fh, ensure_ascii=False)

sz = os.path.getsize('cfa_content.json') / (1024*1024)
print(f'Size: {sz:.1f} MB')

# Quality check on Vol 1 Module 2
ch = data[0]['chapters'][1]
html = ch.get('html', '')
print(f'\nV1 M2: {ch["title"]}')
print(f'  Bullet items: {len(re.findall("<li>", html))}')
print(f'  Bullet lists: {len(re.findall("study-bullet-list", html))}')
print(f'  Formulas: {len(re.findall("formula-block", html))}')
print(f'  Paragraphs: {len(re.findall("study-paragraph", html))}')
print(f'  Examples: {len(re.findall("study-example", html))}')

# Check Vol 1 Module 1 too
ch1 = data[0]['chapters'][0]
html1 = ch1.get('html', '')
print(f'\nV1 M1: {ch1["title"]}')
print(f'  Bullet items: {len(re.findall("<li>", html1))}')
print(f'  Bullet lists: {len(re.findall("study-bullet-list", html1))}')

# Show a sample of bullet list
idx = html1.find('study-bullet-list')
if idx > 0:
    sample = html1[idx-5:idx+800]
    safe = sample.encode('ascii', 'replace').decode('ascii')
    print(f'\n--- Bullet sample from V1M1 ---')
    print(safe)
