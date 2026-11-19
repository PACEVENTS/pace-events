# Otter to Pace Events: sync procedure

Run this for one event (EVENT = the event slug, e.g. `training-session`).

1. Attach and clone the repo: `add_repo` PACEVENTS/pace-events with push access, then
   `git clone --depth 1 https://github.com/PACEVENTS/pace-events /home/claude/pace-events-repo`.
2. Read `data/EVENT/program.json` to get the session codes (session id in capitals, e.g. `ts-02` -> `TS-02`)
   and the event dates.
3. Otter: call `otter_get_user_info`, then `otter_search` with `created_after` set to the event's first day
   (YYYY/MM/DD) and `page_size` 25, paging with `next_cursor` until done. Keep only recordings whose title
   starts with one of this event's session codes.
4. For each kept recording, call `otter_fetch` with its id and save the transcript text EXACTLY as returned,
   with no edits, to `/home/claude/otter-inbox/<id>.txt` in this format:

       title: <recording title>
       id: <recording id>
       start: <metadata.start_time>
       ---
       <the "text" field, unchanged, one [h:mm:ss] Speaker: line per line>

   If a tool result was saved to a file instead of shown inline, read the text from that file with a script
   and write the inbox file from it, so nothing is retyped.
5. Run `python3 scripts/otter_import.py /home/claude/pace-events-repo EVENT /home/claude/otter-inbox`.
   It publishes matched sessions, skips closed sessions and unchanged ones, and lists unmatched titles.
6. If anything changed: `git add -A && git commit -m "Transcripts: <session ids>" && git -c push.negotiate=true push`.
   GitHub Pages republishes within about a minute.
7. Report: sessions published, recordings skipped (closed or unchanged), and any UNMATCHED titles that the
   crew must rename in Otter. Never guess a session for an unmatched recording.

Live site: https://events.pace.rw/
