# Pace Events

Event programmes and session transcripts, published by Pace Production.

Static site served by GitHub Pages: no build step, no database.

1. `index.html`: the app. Routes: `#` home, `#e-<event>` programme, `#s-<event>--<session>` transcript.
2. `data/<event>/event.json`: one event's name, dates, branding. There is deliberately NO list of events: each event is reachable only through its own unguessable slug (unlisted links).
3. `data/<event>/program.json`: days and sessions.
4. `data/<event>/transcripts/<session>.json`: transcripts (made with `scripts/add_transcript.py` from Turboscribe DOCX exports).
5. `assets/`: event logos.
