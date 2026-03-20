import csv
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCES = [
    ('01 Levant Words and Phrases.csv', 'words-phrases'),
    ('02 Levant Sentances.csv', 'sentences'),
    ('03 Levant Conversations.csv', 'conversations'),
]
OUT = ROOT / '04 Levant Reverse Recall.csv'

CARD_STYLE_FRONT = """<div style='text-align:center; line-height:1.15;'>
<div style='color:#6B7280; font-size:18px; font-weight:800; letter-spacing:.08em; text-transform:uppercase; margin-bottom:10px;'>English → Levantine</div>
<div style='color:#111827; font-size:34px; font-weight:800;'>{meaning}</div>
<div style='color:#0F766E; font-size:22px; font-weight:700; margin-top:12px;'>{prompt_label}</div>
<div style='color:#374151; font-size:24px; margin-top:4px;'>{example_en}</div>
</div>"""

CARD_STYLE_BACK = """<div style='line-height:1.2;'>
<div style='color:#7C3AED; font-size:36px; font-weight:800; text-align:center;'>{arabic}</div>
<div style='color:#14B8A6; font-size:26px; font-weight:700; margin-top:6px; text-align:center;'>{translit}</div>
<div style='font-size:24px; font-weight:900; margin:14px 0 8px 0; text-align:center;'>Example answer:</div>
<div style='color:#7C3AED; font-size:28px; font-weight:750; text-align:center;'>{example_ar}</div>
<div style='color:#14B8A6; font-size:22px; margin-top:6px; text-align:center;'>{example_translit}</div>
<div style='color:#6B7280; font-size:22px; margin-top:6px; text-align:center;'>{example_en}</div>
</div>"""


def strip_tags(value: str):
    value = re.sub(r'<br\s*/?>', '\n', value)
    value = re.sub(r'</div>', '\n', value)
    value = re.sub(r'<[^>]+>', '', value)
    value = html.unescape(value)
    lines = [re.sub(r'\s+', ' ', line).strip() for line in value.splitlines()]
    return [line for line in lines if line]


def clean_translit(text: str):
    return text.strip().strip('()')


def parse_row(row):
    front = strip_tags(row['Front'])
    back = strip_tags(row['Back'])
    arabic = front[0]
    translit = clean_translit(front[1]) if len(front) > 1 else ''
    meaning = back[0]

    if 'Example:' in back:
        after = back[back.index('Example:') + 1:]
    else:
        after = back[1:]

    example_ar = after[0] if len(after) > 0 else arabic
    example_translit = after[1] if len(after) > 1 else translit
    example_en = after[2] if len(after) > 2 else meaning

    return {
        'arabic': arabic,
        'translit': translit,
        'meaning': meaning,
        'example_ar': example_ar,
        'example_translit': example_translit,
        'example_en': example_en,
    }


def build_reverse_deck():
    rows_out = []
    for filename, source_tag in SOURCES:
        with open(ROOT / filename, encoding='utf-8-sig', newline='') as f:
            reader = csv.DictReader(f)
            has_tags = 'Tags' in reader.fieldnames
            for row in reader:
                parsed = parse_row(row)
                prompt_label = 'Use it in a sentence:' if parsed['example_en'] != parsed['meaning'] else 'Say it out loud:'
                tags = ['reverse-recall', f'source::{source_tag}']
                if has_tags and row.get('Tags'):
                    tags.extend(tag.strip().replace(' ', '-') for tag in row['Tags'].split() if tag.strip())
                rows_out.append({
                    'Front': CARD_STYLE_FRONT.format(
                        meaning=parsed['meaning'],
                        prompt_label=prompt_label,
                        example_en=parsed['example_en'],
                    ),
                    'Back': CARD_STYLE_BACK.format(**parsed),
                    'Tags': ' '.join(tags),
                })

    with open(OUT, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['Front', 'Back', 'Tags'])
        writer.writeheader()
        writer.writerows(rows_out)

    print(f'Wrote {len(rows_out)} cards to {OUT.name}')


if __name__ == '__main__':
    build_reverse_deck()
