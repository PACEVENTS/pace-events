#!/usr/bin/env python3
"""Add speaker names to an unlabelled transcript, inferred from the moderator's handovers.
Map file (JSON): {"names": {"T": "Tania Imani · Moderator", ...},
                  "turns": [[para, "", "T"], [para, "text where new speaker starts", "K"], ...]}
A turn with "" starts at the beginning of that paragraph; otherwise the paragraph is split at that text.
Every later paragraph keeps the current speaker until the next turn. Sets speakerNote so the app
shows that names were added by Pace. Usage: label_speakers.py <event> <session> <map.json>"""
import json, sys
from pathlib import Path
ev, sid, mp = sys.argv[1:4]  # a turn code of "?" marks speech whose speaker is not identified (left open)
f = Path('data') / ev / 'transcripts' / f'{sid}.json'
tr = json.loads(f.read_text()); M = json.loads(Path(mp).read_text()); N = dict(M['names'], **{'?': ''})
segs = tr['parts'][0]['segments']
orig = [s['text'] for s in segs]
cuts = {}
for p, at, who in M['turns']: cuts.setdefault(p, []).append((at, N[who]))
out, cur = [], ''
for i, s in enumerate(segs):
    text, pieces = s['text'], []
    for at, who in cuts.get(i, []):
        if not at: cur = who; continue
        k = text.find(at)
        if k < 0: sys.exit(f'para {i}: "{at}" not found')
        if text[:k].strip(): pieces.append((cur, text[:k].strip()))
        text, cur = text[k:], who
    pieces.append((cur, text.strip()))
    for j, (who, t) in enumerate(pieces):
        out.append({'time': s['time'] if j == 0 else '', 'speaker': who, 'text': t})
assert ' '.join(' '.join(o.split()) for o in orig) == ' '.join(o['text'] for o in out), 'text changed'
tr['parts'][0]['segments'] = out
tr['speakerNote'] = M.get('note', "Speaker names were added by Pace Production from the moderator's introductions and may not be exact.")
f.write_text(json.dumps(tr, ensure_ascii=False, separators=(',', ':')))
from collections import Counter
print(sid, len(out), 'segments', dict(Counter(o['speaker'] for o in out)))
