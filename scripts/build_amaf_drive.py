#!/usr/bin/env python3
"""AMAF 2026, interim version (client instruction, 19 Nov 2026): one session per Drive transcript,
titled exactly as the Drive file. Times/days follow the forum agenda for the sessions each title names.
The full agenda-based build (with content-matched splits) is scripts/build_amaf.py."""
import json, re, sys
from pathlib import Path
import docx
sys.path.insert(0, str(Path(__file__).parent))
from add_transcript import parse

REPO = Path(__file__).resolve().parent.parent
SRC = Path('/home/claude/amaf/src')
EV = 'amaf-2026-hpejmkgr'
F1, F2 = '2026-11-17', '2026-11-18'
# (session id, local file, Drive file title, day, start, end)
FILES = [
    ('opening', 't0-opening.docx', 'AMAF 2026 (Keynote Address and Official Opening of the Forum)', F1, '10:05', '11:00'),
    ('t1', 't1-policy-roadmap.docx', 'AMAF 2026 (Plenary: Strengthen policy and regulatory frameworks  &  Introduction to the Roadmap & Transition to breakouts)1', F1, '12:15', '13:15'),
    ('t2', 't2-roadmap.docx', 'AMAF 2026 2 (Introduction to the Roadmap)', F1, '13:10', '13:15'),
    ('t3', 't3-models-wrap1.docx', 'AMAF 2026 3(  Transition to breakouts  &  Midwifery Models of Care in the African Continent  & Day 1 Wrap-Up & Synthesis)', F1, '16:20', '17:10'),
    ('t4', 't4-recap-education.docx', 'AMAF 2026 4 (Day 1 Roadmap Recap  Plenary: Transforming Pre-Service Education & Curricula, Quality Education and Professional Development)', F2, '09:00', '10:15'),
    ('t5', 't5-srhr.docx', 'AMAF 2026 5 (Plenary: Midwives and Integrated SRHR Services (Including FP and HIV))', F2, '12:10', '13:00'),
    ('t6', 't6-retention-pph-wrap2.docx', 'AMAF 2026 6(Plenary: Retention through safe, supportive, accountable workplaces. Data-driven deployment & Plenary: Scaling-up the implementation of the Global PPHF Guidelines Day 2 Wrap-Up & Synthesis )', F2, '14:00', '17:30'),
]
def clean(t):
    t = re.sub(r'^AMAF 2026\s*\d?\s*\(\s*', '', t)
    t = re.sub(r'\s*\)\s*\d*\s*$', '', t)
    return re.sub(r'\s{2,}', ' ', t).strip()

ev_dir = REPO / 'data' / EV
(ev_dir / 'transcripts').mkdir(parents=True, exist_ok=True)
for f in (ev_dir / 'transcripts').glob('*.json'):
    f.unlink()
S = []
for sid, fname, title, day, st, en in FILES:
    paras = [p.text for p in docx.Document(SRC / fname).paragraphs if p.text.strip()][1:]
    segs = parse(paras)
    (ev_dir / 'transcripts' / f'{sid}.json').write_text(json.dumps(
        {'session': sid, 'language': 'en', 'languageLabel': 'English', 'source': {'drive': title},
         'parts': [{'title': '', 'segments': segs}]}, ensure_ascii=False, separators=(',', ':')))
    S.append({'id': sid, 'day': day, 'start': st, 'end': en, 'sort': st, 'timeLabel': None, 'room': 'Kilimanjaro',
              'title': clean(title), 'kind': 'Plenary', 'closed': False, 'speakers': [], 'transcript': True})
    print(f'{sid:8s} {sum(len(x["text"].split()) for x in segs):6d} words  {clean(title)[:90]}')
prog = {'timezoneLabel': 'Kigali time (GMT +02:00)',
        'days': [{'date': F1, 'label': 'Day 1 · Commit & Invest'}, {'date': F2, 'label': 'Day 2 · Educate, Deploy, Retain'}],
        'sessions': S}
(ev_dir / 'program.json').write_text(json.dumps(prog, ensure_ascii=False, indent=2))
