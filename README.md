# ONEIGHTY — WTC Youth Landing Page

A modern, Gen Z/Gen Alpha-friendly landing page for the ONEIGHTY youth division
of World Transformation Church (WTC).

- **Live site:** https://samuel-sshi.github.io/youth-division-landing/
- **Repo:** https://github.com/samuel-sshi/youth-division-landing (branch `gh-pages`)

---

## 🎯 How the Media Team Adds / Edits Events (no code, no GitHub)

Events are managed in **Google Sheets**, not in code. The website reads from
the sheet automatically — the media team never touches GitHub or JSON.

### The spreadsheet

**ONEIGHTY Events (Website)** — link is shared privately with the media team
(it is intentionally not published in this public repo).

Columns (row 1 is the header — **do not edit row 1**):

| Column | Meaning | Example |
|--------|---------|---------|
| A — **Date** | Event date, `YYYY-MM-DD` (or use the date picker) | `2026-09-13` |
| B — **Name** | Event title | `Youth Night Out` |
| C — **Time** | Start time, `HH.MM` (24-hour) | `18.30` |
| D — **Location** | Where | `WTC LT.3 — Next Gen` |
| E — **Description** | One or two sentences | `Game night + snacks…` |
| F — **Link** | Optional URL (event page / IG post) | `https://…` |
| G — **Published** | `TRUE` = show on site, `FALSE` = hide/draft | `TRUE` |

### How to add an event

1. Open the spreadsheet.
2. Add a new row below the last one.
3. Fill in the columns (Date, Name, Time are the only required ones).
4. Set **Published** to `TRUE` (dropdown).
5. Done. The website updates automatically within ~1 hour.

### How to hide / delete an event

- **Hide (keep as draft):** set Published to `FALSE`.
- **Delete:** clear the row (or the Name + Date cells).

### Notes for the media team

- **Past events disappear automatically.** You never have to clean up old rows —
  the site only shows events dated today or later.
- **Time format:** use `HH.MM` (e.g. `18.30`, `09.00`). The sheet is formatted as
  text, so `17.00` won't lose its trailing zeros.
- **Published is forgiving:** blank = treated as published. Only `FALSE` hides.
  The `TRUE`/`FALSE` cell has a dropdown, so no typos.
- If a row has a bad date, it's skipped and logged — it won't break the site.

---

## 🛠️ For the Developer

### How it works

```
Google Sheets ──(hourly cron)──> sync_events.py ──> events.json ──> git push ──> GitHub Pages
```

1. **`sync_events.py`** reads the sheet, filters `Published != FALSE`,
   normalizes dates/times, writes `events.json` (sorted ascending), and
   pushes to `gh-pages` if anything changed.
2. A cron wrapper invokes the sync script with the google-workspace
   Python environment.
3. **Cron job** (`ONEIGHTY Events Sync`) runs the script every hour.
4. **`index.html`** fetches `events.json` client-side and renders only future
   events, so the page stays in sync automatically.

### Files

| File | Purpose |
|------|---------|
| `index.html` | The landing page (renders events from `events.json`) |
| `events.json` | Generated events data (do not hand-edit — it's overwritten) |
| `sync_events.py` | Sheet → JSON → git push pipeline |
| `setup_events_sheet.py` | One-time sheet setup (headers, seed, validation, formatting) |

### Running the sync manually

The sync script is idempotent. Run it from the private copy that the
cron job uses (it re-auths via the google-workspace venv and pushes to
`gh-pages` only when `events.json` actually changed).

### Cron job

An hourly cron job (`ONEIGHTY Events Sync`, `no_agent=true`) runs the
private wrapper script — pure script, no model call. Check its status
with `hermes cron list`.

### Dependencies

- Google OAuth token with `spreadsheets` scope, managed by the
  `google-workspace` skill. Stored privately outside this repo.
- Sheet ID stored privately outside this repo (intentionally not
  published here).
- The live copies of `sync_events.py` / `setup_events_sheet.py` live
  outside this repo (private) — the copies in this repo are documentation
  only and are NOT executed by the pipeline.

### Adding a new field to events

1. Add a column header to the sheet.
2. In `sync_events.py`, extend `parse_rows()` to read it (and adjust the
   `[:7]` slice if columns grow).
3. In `index.html`, extend the card template in `renderEvents()`.

---

## License

Church-internal use. Content owned by ONEIGHTY / World Transformation Church.
