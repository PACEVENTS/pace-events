#!/usr/bin/env python3
"""Import Otter.ai transcripts into Pace Events.

Each inbox file is one Otter recording, saved exactly as otter_fetch returns its text:

    title: TS-02 Panel discussion
    id: v_xxxxxxxx
    ---
    [0:00:00] Speaker Name: text...
    [0:00:08] Other Speaker: text...

Usage:
  python3 otter_import.py <repo_dir> <event_slug> <inbox_dir> [--force] [--session ID --file F]

Matching: the recording title must START with the session code, which is the
session id in capitals (e.g. "TS-02 ..." -> session "ts-02"). Unmatched files and
closed sessions are reported and skipped, never guessed. A session that already
has a transcript from the same Otter recording is skipped unless --force.
Several recordings for one session (e.g. "TS-02 part 2") become ordered parts.
"""
import argparse, json, re, sys
from pathlib import Path

RX_LINE = re.compile(r'^\[(\d{1,2}:\d{2}:\d{2})\]\s*([^:\n]{1,80}?):\s*(.*)$')
RX_LINE_NOSPK = re.compile(r'^\[(\d{1,2}:\d{2}:\d{2})\]\s*(.*)$')


def norm_ts(t):
    h, m, s = (int(x) for x in t.split(':'))
    return f'{h}:{m:02d}:{s:02d}' if h else f'{m}:{s:02d}'


def read_inbox(path):
    raw = Path(path).read_text(encoding='utf-8')
    head, _, body = raw.partition('\n---\n')
    meta = dict(l.split(':', 1) for l in head.splitlines() if ':' in l)
    meta = {k.strip(): v.strip() for k, v in meta.items()}
    segs = []
    for line in body.splitlines():
        line = line.rstrip()
        if not line.strip():
            continue
        m = RX_LINE.match(line)
        if m:
            segs.append({'time': norm_ts(m.group(1)), 'speaker': m.group(2).strip(), 'text': m.group(3).strip()})
            continue
        m = RX_LINE_NOSPK.match(line)
        if m:
            segs.append({'time': norm_ts(m.group(1)), 'speaker': '', 'text': m.group(2).strip()})
        elif segs:
            segs[-1]['text'] += ' ' + line.strip()  # wrapped continuation line
        else:
            segs.append({'time': '', 'speaker': '', 'text': line.strip()})
    return meta, segs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('repo'); ap.add_argument('event'); ap.add_argument('inbox')
    ap.add_argument('--force', action='store_true')
    a = ap.parse_args()

    ev_dir = Path(a.repo) / 'data' / a.event
    prog_path = ev_dir / 'program.json'
    prog = json.loads(prog_path.read_text())
    by_code = {s['id'].upper(): s for s in prog['sessions']}
    codes = sorted(by_code, key=len, reverse=True)

    groups, report = {}, []
    for f in sorted(Path(a.inbox).glob('*.txt')):
        meta, segs = read_inbox(f)
        title = meta.get('title', '')
        code = next((c for c in codes if re.match(re.escape(c) + r'(\b|_|\s|$)', title.upper())), None)
        if not code:
            report.append(f'UNMATCHED  "{title}" ({f.name}): title does not start with a session code')
            continue
        s = by_code[code]
        if s.get('closed'):
            report.append(f'SKIPPED    "{title}": {s["id"]} is a closed session')
            continue
        part_title = re.sub(r'^' + re.escape(code) + r'[\s_:.-]*', '', title, flags=re.I).strip()
        groups.setdefault(s['id'], []).append((meta.get('start', ''), title, part_title, meta.get('id', f.stem), segs))

    (ev_dir / 'transcripts').mkdir(parents=True, exist_ok=True)
    changed = []
    for sid, recs in groups.items():
        recs.sort(key=lambda r: (r[0], r[1]))
        out_path = ev_dir / 'transcripts' / f'{sid}.json'
        ids = [r[3] for r in recs]
        if out_path.exists() and not a.force:
            old = json.loads(out_path.read_text())
            if old.get('source', {}).get('otter') == ids:
                report.append(f'UNCHANGED  {sid}')
                continue
        multi = len(recs) > 1
        tr = {'session': sid, 'language': 'en', 'languageLabel': 'English',
              'source': {'otter': ids},
              'parts': [{'title': (pt if multi else ''), 'segments': segs} for _, _, pt, _, segs in recs]}
        out_path.write_text(json.dumps(tr, ensure_ascii=False, separators=(',', ':')))
        by_code[sid.upper()]['transcript'] = True
        words = sum(len(x['text'].split()) for r in recs for x in r[4])
        changed.append(sid)
        report.append(f'PUBLISHED  {sid}: {len(recs)} recording(s), {words} words')
    prog_path.write_text(json.dumps(prog, ensure_ascii=False, indent=2))
    print('\n'.join(report) or 'Nothing in inbox.')
    print('CHANGED:', ' '.join(changed) or 'none')


if __name__ == '__main__':
    main()
