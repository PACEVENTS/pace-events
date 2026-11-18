#!/usr/bin/env python3
"""Turn Turboscribe DOCX exports into Pace Events transcripts.

Usage:
  python3 add_transcript.py <app_dir> <event_slug> <session_id> <file.docx> [more.docx ...]
         [--part "Part title"] ... [--lang en|fr] [--speaker "Speaker 1=Real Name"] ...

One DOCX = one transcript part. Pass several DOCX files (with matching --part
titles, in speaking order) for sessions with several speeches. Writes
<app_dir>/data/<event_slug>/transcripts/<session_id>.json and marks the session
as having a transcript in program.json.

Turboscribe layouts handled:
  (0:00 - 0:17)                        timestamp on its own line, text follows
  [Speaker 1] (0:18 - 2:36)            speaker + timestamp header, text follows
  [Speaker 1]                          speaker header
  [00:01:23] Speaker 1: text           everything on one line
  plain paragraphs                     no speakers, no times
"""
import argparse, json, re, sys
from pathlib import Path
import docx

TS = r'(\d{1,2}:\d{2}(?::\d{2})?)'
RNG = TS + r'(?:\s*[-–]\s*' + TS + r')?'
RX_TS_ONLY = re.compile(r'^\s*[\[(]?\s*' + RNG + r'\s*[\])]?\s*$')
RX_HEADER = re.compile(r'^\s*\[?(?P<spk>[^\]\[():\n]{1,60}?)\]?\s*[\[(]\s*' + RNG + r'\s*[\])]\s*:?\s*$')
RX_BRACKET_SPK = re.compile(r'^\s*\[(?P<spk>[^\]]{1,60})\]\s*(?P<rest>.*)$', re.S)
RX_LEAD_TS = re.compile(r'^\s*[\[(]\s*' + RNG + r'\s*[\])]\s*[-–:]?\s*')
RX_SPK_INLINE = re.compile(r'^(?P<spk>(?:Speaker\s*\d+|Intervenant\s*\d+))\s*:\s+(?P<txt>.+)$', re.S | re.I)
RX_SPK_ONLY = re.compile(r'^\s*(Speaker\s*\d+|Intervenant\s*\d+|Locuteur\s*\d+)\s*:?\s*$', re.I)
LANGS = {'en': 'English', 'fr': 'Français'}


def norm_ts(t):
    if not t:
        return ''
    p = [int(x) for x in t.split(':')]
    if len(p) == 2:
        p = [0] + p
    h, m, s = p
    return f'{h}:{m:02d}:{s:02d}' if h else f'{m}:{s:02d}'


def parse(paras):
    segs, cur_spk, cur_ts = [], '', ''
    for raw in paras:
        line = re.sub(r'\s+', ' ', raw).strip()
        if not line:
            continue
        m = RX_TS_ONLY.match(line)
        if m:
            cur_ts = norm_ts(m.group(1)); continue
        m = RX_HEADER.match(line)
        if m:
            cur_spk, cur_ts = m.group('spk').strip(), norm_ts(m.group(2)); continue
        m = RX_SPK_ONLY.match(line)
        if m:
            cur_spk = m.group(1).strip(); continue
        m = RX_BRACKET_SPK.match(line)
        if m:
            cur_spk = m.group('spk').strip()
            line = m.group('rest').strip()
            if not line:
                continue
            mt = RX_TS_ONLY.match(line)
            if mt:
                cur_ts = norm_ts(mt.group(1)); continue
        ts = ''
        m = RX_LEAD_TS.match(line)
        if m:
            ts = norm_ts(m.group(1)); line = line[m.end():].strip()
            if not line:
                cur_ts = ts; continue
        m = RX_SPK_INLINE.match(line)
        if m:
            cur_spk, line = m.group('spk').strip(), m.group('txt').strip()
        segs.append({'time': ts or cur_ts, 'speaker': cur_spk, 'text': line})
        cur_ts = ''
    return segs


def read_docx(path):
    d = docx.Document(path)
    paras = [p.text for p in d.paragraphs]
    for t in d.tables:
        for row in t.rows:
            paras.append(' '.join(c.text for c in row.cells))
    # The first non-empty paragraph of a Turboscribe export is the file title: drop it.
    while paras and not paras[0].strip():
        paras.pop(0)
    if paras and len(paras[0]) < 220 and not RX_TS_ONLY.match(paras[0].strip()):
        paras = paras[1:]
    return paras


def build(docx_files, parts=None, lang='en', rename=None, drop_patterns=()):
    rename = rename or {}
    out_parts = []
    for i, f in enumerate(docx_files):
        paras = [p for p in read_docx(f) if not any(re.search(rx, p) for rx in drop_patterns)]
        segs = parse(paras)
        for s in segs:
            s['speaker'] = rename.get(s['speaker'], s['speaker'])
        title = parts[i] if parts and i < len(parts) else ''
        out_parts.append({'title': title, 'segments': segs})
    return {'language': lang, 'languageLabel': LANGS[lang], 'parts': out_parts}


def save(app_dir, event, session, tr):
    ev_dir = Path(app_dir) / 'data' / event
    prog_path = ev_dir / 'program.json'
    prog = json.loads(prog_path.read_text())
    sess = next((s for s in prog['sessions'] if s['id'] == session), None)
    if not sess:
        sys.exit(f'Session "{session}" not found. Known ids: ' + ', '.join(s['id'] for s in prog['sessions']))
    tr['session'] = session
    (ev_dir / 'transcripts').mkdir(parents=True, exist_ok=True)
    (ev_dir / 'transcripts' / f'{session}.json').write_text(json.dumps(tr, ensure_ascii=False, separators=(',', ':')))
    sess['transcript'] = True
    prog_path.write_text(json.dumps(prog, ensure_ascii=False, indent=2))
    words = sum(len(s['text'].split()) for p in tr['parts'] for s in p['segments'])
    n = sum(len(p['segments']) for p in tr['parts'])
    print(f'OK {session}: {len(tr["parts"])} part(s), {n} segments, {words} words')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('app_dir'); ap.add_argument('event'); ap.add_argument('session'); ap.add_argument('docx', nargs='+')
    ap.add_argument('--part', action='append', default=[])
    ap.add_argument('--lang', default='en', choices=list(LANGS))
    ap.add_argument('--speaker', action='append', default=[], help='"Speaker 1=Real Name"')
    a = ap.parse_args()
    tr = build(a.docx, a.part, a.lang, dict(s.split('=', 1) for s in a.speaker))
    save(a.app_dir, a.event, a.session, tr)


if __name__ == '__main__':
    main()
