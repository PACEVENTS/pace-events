#!/usr/bin/env python3
"""One-off: build AMAF 2026 (pre-conference workshop + forum) programme and transcripts.

Programme sources:
  1. Pre-conference: UNFPA ESARO concept note, Annex A (15-16 Nov 2026).
  2. Forum: "Africa Midwifery Acceleration Forum Agenda (SOURCE OF TRUTH).docx" (17-19 Nov 2026).
Transcripts: Drive folder "Transcription" (Turboscribe DOCX). File names do not match their
content, so files are matched and split by content (see SPLITS below).
"""
import json, re, sys
from pathlib import Path
import docx
sys.path.insert(0, str(Path(__file__).parent))
from add_transcript import parse

REPO = Path(__file__).resolve().parent.parent
AMAF = Path('/home/claude/amaf')
EV = 'amaf-2026'
P1, P2, F1, F2, F3 = '2026-11-15', '2026-11-16', '2026-11-17', '2026-11-18', '2026-11-19'

S = []
def add(id, day, start, end, title, speakers=(), room='', kind='', closed=False, plain=False):
    S.append({'id': id, 'day': day, 'start': start, 'end': end, 'room': room, 'title': title,
              'kind': '' if plain else kind, 'closed': closed, 'sort': start + id[-2:], 'timeLabel': None,
              'speakers': [] if plain else [{'name': n, 'role': r} for n, r in speakers], 'transcript': False})

# ---------- Pre-conference technical meeting (concept note, Annex A) ----------
K = 'Pre-conference'
add('p1-registration', P1, '08:15', '08:45', 'Registration and welcome coffee', plain=True)
add('p1-opening', P1, '08:45', '09:15', 'Opening and welcome', [('Frida Temple', 'Chair'), ('Christa Ishimwe', 'Program Advisor, Climate and Health, MoH Rwanda')], kind=K)
add('p1-climate-mnh', P1, '09:15', '10:00', "Climate change and maternal & newborn health in Africa", [('Prof Sibusiso Mkwananzi', '')], kind=K)
add('p1-heat-floods', P1, '10:00', '10:30', 'Brief: heat, floods and pregnancy', [('Ms Margaret Ontiretse', 'Botswana'), ('UNFPA Kenya', 'Country office experience sharing')], kind=K)
add('p1-break-am', P1, '10:30', '11:00', 'Health break', plain=True)
add('p1-india', P1, '11:00', '12:00', 'Experience from India. Heat and Pregnancy Guidance: country spotlights', [('Dr Akash Shrivastava', 'India'), ('Saswati Das', 'India')], kind=K)
add('p1-indicators', P1, '12:00', '12:45', 'Priority Indicators to Monitor the Impact of Heat Exposure on Maternal, Newborn and Child Health', [('Katy Mitchelle', 'Virtual')], kind=K)
add('p1-lunch', P1, '12:45', '13:45', 'Lunch', plain=True)
add('p1-groups', P1, '13:45', '15:15', 'Discussion: Climate-Related Maternal and Newborn Health Risks and Adaptation Priorities', [('Prof Sibusiso Mkwananzi', 'Moderator')], kind='Group work')
add('p1-break-pm', P1, '15:15', '15:30', 'Health break', plain=True)
add('p1-reportback', P1, '15:30', '16:15', 'Plenary report-back and consensus on validated evidence', [('Prof Sibusiso Mkwananzi', 'Moderator')], kind=K)
add('p1-unfpa-vp', P1, '16:15', '16:55', 'UNFPA Value Proposition on Climate Change 2.0', [('Muna Abdullah', 'UNFPA ESARO')], kind=K)
add('p1-close', P1, '16:55', '17:15', 'Reflections and close of Day 1', [('Chair', '')], kind=K)

add('p2-recap', P2, '08:30', '08:45', 'Recap of Day 1 and objectives for Day 2', [('Chair', ''), ('Yousuf Alrawi', 'UNFPA ESARO')], kind=K)
add('p2-somwy', P2, '08:45', '09:45', 'Findings of the State of Midwifery in the ESA region', [('Muna Abdullah', 'UNFPA ESARO')], kind=K)
add('p2-frontline', P2, '09:45', '10:45', "Frontline voices: midwives' clinical experiences", [('Midwifery Panel (ESA)', 'Zambia, Uganda, Tanzania')], kind='Panel')
add('p2-break-am', P2, '10:45', '11:15', 'Health break', plain=True)
add('p2-groups', P2, '11:15', '12:15', 'Group work on the country profile data from SoMWY ESA 2024', [('Muna Abdullah', 'UNFPA ESARO')], kind='Group work')
add('p2-lunch', P2, '12:15', '13:15', 'Lunch', plain=True)
add('p2-guidance', P2, '13:15', '14:15', 'Country-specific guidance review and validation', [('Prof Sibusiso Mkwananzi', '')], kind=K)
add('p2-break-pm', P2, '14:15', '14:45', 'Health break', plain=True)
add('p2-closing', P2, '14:45', '15:30', 'Closing remarks', [('UNFPA ESARO', ''), ('MoH Rwanda', '')], kind=K)
add('p2-reception', P2, '18:30', '20:00', 'Reception', plain=True)

# ---------- Forum (SOURCE OF TRUTH agenda) ----------
def hm(t):
    t = t.strip().replace('.', ':')
    m = re.match(r'^(\d{1,2}):?(\d{2})$', t.replace(' ', ''))
    if not m:
        m = re.match(r'^(\d{1,2})(\d{2})$', t.replace(' ', ''))
    return f'{int(m.group(1)):02d}:{m.group(2)}'

def rows(table):
    out = []
    for r in table.rows[1:]:
        cells = []
        for c in r.cells:
            x = c.text.strip()
            if not cells or cells[-1] != x:
                cells.append(x)
        if len(cells) >= 2 and re.search(r'\d', cells[0]):
            a, _, b = re.split(r'\s*[-–]\s*', cells[0], maxsplit=1)[0], None, re.split(r'\s*[-–]\s*', cells[0], maxsplit=1)[-1]
            out.append({'start': hm(a), 'end': hm(b), 'title': re.sub(r'\s*\n\s*(?=&)', ' ', re.sub(r'\s*\n\s*(?!&)', ' · ', cells[1])).strip(),
                        'speakers': cells[2] if len(cells) > 2 else '', 'room': cells[-1] if len(cells) > 3 else ''})
    return out

def speakers(txt):
    out = []
    for line in [l.strip() for l in txt.split('\n') if l.strip()]:
        role = ''
        m = re.match(r'^(Moderator|Session\s+moderator|Panel moderator|Session opening)\s*:\s*(.+)$', line, re.I)
        if m:
            role, line = m.group(1).strip().capitalize(), m.group(2)
        name, _, rest = line.partition(',')
        out.append({'name': name.strip(), 'role': ', '.join(x for x in [rest.strip(), role] if x)})
    return out

d = docx.Document(AMAF / 'agenda.docx')
day_tables = {F1: d.tables[3], F2: d.tables[5], F3: d.tables[7]}
PLAIN = re.compile(r'^(Registration|Lunch|Tea|Transition|Official Group Photograph|Arrival and Seating|Performance Introduction|Traditional Rwandan|Closing of the Opening|Sherehe|Present Accelerator)', re.I)
OPEN_FOLD = re.compile(r'^(Opening, Introduction|Welcome Remarks|Midwifery Objectives|Remarks|Video remarks|Keynote Address)', re.I)
for day, t in day_tables.items():
    pre = {F1: 'd1', F2: 'd2', F3: 'd3'}[day]
    opening = None
    for i, r in enumerate(rows(t)):
        title = r['title']
        if title.lower().startswith('transition') and 'breakout' not in title.lower():
            continue
        if day == F1 and OPEN_FOLD.match(title):
            # Fold the ceremony's short remarks into one "Official Opening Ceremony" session.
            sp = speakers(r['speakers'])
            for s in sp:
                if not s['role']:
                    s['role'] = re.sub(r'^(Video remarks|Remarks) by the ', '', title)
                if title.lower().startswith('keynote'):
                    s['role'] += ' · Keynote Address and Official Opening'
                elif title.lower().startswith('video'):
                    s['role'] += ' · Video remarks'
            if opening is None:
                add('d1-opening', day, r['start'], '11:00', 'Official Opening Ceremony and Keynote Address', room=r['room'], kind='Plenary')
                opening = S[-1]
            opening['speakers'] += [{'name': s['name'], 'role': s['role']} for s in sp]
            continue
        slug = re.sub(r'[^a-z0-9]+', '-', re.sub(r'^(Plenary|Special Technical Session)\s*:\s*', '', title, flags=re.I).lower()).strip('-')[:28].strip('-')
        sid = f'{pre}-{slug}'
        while any(x['id'] == sid for x in S):
            sid += '-2'
        is_breakout = title.lower().startswith('roadmap breakout')
        kind = 'Breakout' if is_breakout else ('Plenary' if title.lower().startswith(('plenary', 'validation')) else 'Session')
        add(sid, day, r['start'], r['end'], title, [(s['name'], s['role']) for s in speakers(r['speakers'])],
            room=r['room'], kind=kind, plain=bool(PLAIN.match(title)) or is_breakout)
# The opening ceremony moderator, listed first
op = next(s for s in S if s['id'] == 'd1-opening')
op['speakers'] = [s for s in op['speakers'] if not s['name'].startswith('Moderator')]
op['speakers'].insert(0, {'name': 'Annet Mwizerwa', 'role': 'Moderator'})
seen = set(); op['speakers'] = [s for s in op['speakers'] if not (s['name'] in seen or seen.add(s['name']))]

labels = {P1: 'Pre-conference Day 1', P2: 'Pre-conference Day 2', F1: 'Forum Day 1 · Commit & Invest',
          F2: 'Forum Day 2 · Educate, Deploy, Retain', F3: 'Forum Day 3 · Advocate & Empower'}
prog = {'timezoneLabel': 'Kigali time (GMT +02:00)',
        'days': [{'date': k, 'label': v} for k, v in labels.items()], 'sessions': S}

# ---------- Transcripts: split by content ----------
def paras(name):
    return [p.text for p in docx.Document(AMAF / 'src' / name).paragraphs if p.text.strip()]

def sid_for(day, startswith):
    return next(s['id'] for s in S if s['day'] == day and s['title'].lower().startswith(startswith.lower()))

# (file, first_para, end_para_exclusive, day, session title prefix); para 0 is the file's title line.
SPLITS = [
    ('t0-opening.docx', 1, None, F1, 'Official Opening Ceremony'),
    ('t2-roadmap.docx', 1, 110, F1, 'Plenary: Strengthen policy'),
    ('t2-roadmap.docx', 110, None, F1, 'Introduction to the Roadmap'),
    ('t1-policy-roadmap.docx', 1, 111, F1, 'Plenary: Increasing Domestic'),
    ('t1-policy-roadmap.docx', 111, 201, F1, 'Midwifery Models of Care'),
    ('t1-policy-roadmap.docx', 201, None, F1, 'Day 1 Wrap-Up'),
    ('t5-srhr.docx', 1, 10, F2, 'Day 1 Roadmap Recap'),
    ('t5-srhr.docx', 10, None, F2, 'Plenary: Transforming Pre-Service'),
    ('t6-retention-pph-wrap2.docx', 1, None, F2, 'Plenary: Midwives and Integrated SRHR'),
    ('t3-models-wrap1.docx', 1, None, F2, 'Plenary: Retention'),
    ('t4-recap-education.docx', 1, 138, F2, 'Plenary: Scaling-up'),
    ('t4-recap-education.docx', 138, None, F2, 'Day 2 Wrap-Up'),
]
ev_dir = REPO / 'data' / EV
(ev_dir / 'transcripts').mkdir(parents=True, exist_ok=True)
for f in (ev_dir / 'transcripts').glob('*.json'):
    f.unlink()
for fname, a, b, day, prefix in SPLITS:
    sid = sid_for(day, prefix)
    segs = parse(paras(fname)[a:b])
    tr = {'session': sid, 'language': 'en', 'languageLabel': 'English',
          'source': {'drive': fname}, 'parts': [{'title': '', 'segments': segs}]}
    (ev_dir / 'transcripts' / f'{sid}.json').write_text(json.dumps(tr, ensure_ascii=False, separators=(',', ':')))
    next(s for s in S if s['id'] == sid)['transcript'] = True
    print(f'{sid:42s} {len(segs):4d} paras {sum(len(x["text"].split()) for x in segs):6d} words  <- {fname}[{a}:{b}]')
(ev_dir / 'program.json').write_text(json.dumps(prog, ensure_ascii=False, indent=2))
print(len(S), 'programme items')
