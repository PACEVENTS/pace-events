# Pace Events

Event programmes and session transcripts, published by Pace Production.

Static site served by GitHub Pages: no build step, no database.

1. `index.html`: the app. Routes: `#` home, `#e-<event>` programme, `#s-<event>--<session>` transcript.
2. `data/events.json`: list of events.
3. `data/<event>/program.json`: days and sessions.
4. `data/<event>/transcripts/<session>.json`: transcripts (made with `scripts/add_transcript.py` from Turboscribe DOCX exports).
5. `assets/`: event logos.
