#!/usr/bin/env python3
"""Sync ONEIGHTY events from Google Sheets -> events.json -> GitHub Pages.

Reads the "ONEIGHTY Events (Website)" sheet, filters to rows where
Published == TRUE, writes events.json (sorted by date), and pushes
to the gh-pages branch. Safe to run repeatedly; no-op if nothing changed.

Any failure exits non-zero with a clear message so the cron watchdog
alerts instead of the site silently going stale.

Columns: Date | Name | Time | Location | Description | Link | Published
"""
import json
import re
import subprocess
import sys
from datetime import datetime, date
from pathlib import Path

# Auth helpers live in the google-workspace skill
_SCRIPTS_DIR = str(Path.home() / ".hermes/skills/productivity/google-workspace/scripts")
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

from _hermes_home import get_hermes_home
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

HERMES_HOME = get_hermes_home()
TOKEN_PATH = HERMES_HOME / "google_token.json"

# Sheet ID is intentionally NOT stored in the public repo.
# The live pipeline reads it from ~/.hermes/oneighty_sheet_id (private),
# created once with:  echo "<SHEET_ID>" > ~/.hermes/oneighty_sheet_id
SHEET_ID = (HERMES_HOME / "oneighty_sheet_id").read_text(encoding="utf-8").strip()
RANGE = "A2:G"  # all data rows, no hard row cap

REPO_DIR = Path.home() / "youth-division-landing"
EVENTS_FILE = REPO_DIR / "events.json"

MONTH_MAP = {
    "jan": 1, "januari": 1, "feb": 2, "februari": 2,
    "mar": 3, "maret": 3, "apr": 4, "april": 4,
    "may": 5, "mei": 5, "jun": 6, "juni": 6,
    "jul": 7, "juli": 7, "aug": 8, "agustus": 8, "agu": 8,
    "sep": 9, "september": 9, "oct": 10, "oktober": 10,
    "nov": 11, "november": 11, "dec": 12, "desember": 12,
}

TIME_RE = re.compile(r"^(\d{1,2})[:.](\d{2})\s*(?:wib|ist)?$", re.IGNORECASE)


def fail(msg):
    print(f"❌ {msg}", file=sys.stderr)
    sys.exit(1)


def get_creds():
    try:
        data = json.loads(TOKEN_PATH.read_text())
        creds = Credentials.from_authorized_user_info(data)
    except FileNotFoundError:
        fail(f"Google token missing at {TOKEN_PATH} — re-auth the google-workspace skill.")
    except Exception as e:
        fail(f"Could not load Google credentials: {e}")
    if creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
        except Exception as e:
            fail(f"OAuth token refresh failed ({e}). Re-auth the google-workspace skill, "
                 "otherwise website events will go stale.")
    return creds


def read_sheet():
    creds = get_creds()
    svc = build("sheets", "v4", credentials=creds)
    try:
        result = svc.spreadsheets().values().get(
            spreadsheetId=SHEET_ID, range=RANGE, valueRenderOption="FORMATTED_VALUE"
        ).execute()
    except Exception as e:
        fail(f"Could not read the events sheet: {e}")
    return result.get("values", [])


def parse_date(raw):
    """Parse a date from the Date cell only (no description fallback).

    Accepts ISO (2026-08-28), day-first (28-08-2026, 28/08/2026),
    and Indonesian long/short month names (28 Aug, 28 Agustus 2026).
    Returns date object or None.
    """
    s = str(raw).strip().lower()
    if not s:
        return None

    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            pass

    # e.g. "28 Aug" / "28 Agu" -> use current year
    m = re.match(r"(\d{1,2})\s+([a-z]{3,})$", s)
    if m:
        day, mon = int(m.group(1)), m.group(2)
        mon_num = MONTH_MAP.get(mon)
        if mon_num:
            return date(date.today().year, mon_num, day)

    # e.g. "28 Agustus 2026" / "28 Aug 2026"
    m = re.match(r"(\d{1,2})\s+([a-z]+)\s+(\d{4})$", s)
    if m:
        day, mon, year = int(m.group(1)), m.group(2), int(m.group(3))
        mon_num = MONTH_MAP.get(mon)
        if mon_num:
            return date(year, mon_num, day)

    return None


def normalize_time(raw):
    """Normalize a time value to HH.MM (validated), or pass text through."""
    s = str(raw).strip()
    if not s:
        return ""

    m = TIME_RE.match(s)
    if m:
        h, mi = int(m.group(1)), int(m.group(2))
        if h <= 23 and mi <= 59:
            return f"{h:02d}.{mi:02d}"
        print(f"  ⚠️  invalid time '{raw}' (out of range) — kept as typed", file=sys.stderr)
        return s

    # Bare number from Sheets, e.g. "19" -> 19.00, "19.5" -> 19.50
    try:
        f = float(s.replace(",", "."))
    except ValueError:
        return s  # free text like "TBA" — pass through untouched

    if f == int(f):
        h, mi = int(f), 0
    else:
        h = int(f)
        mi = round((f - h) * 100)
    if h <= 23 and mi <= 59:
        return f"{h:02d}.{mi:02d}"
    print(f"  ⚠️  invalid time '{raw}' (out of range) — kept as typed", file=sys.stderr)
    return s


def normalize_link(raw):
    """Ensure link starts with http:// or https:// (blocks javascript: etc)."""
    s = str(raw).strip()
    if not s:
        return ""
    if s.startswith(("http://", "https://")):
        return s
    return f"https://{s}"


def parse_rows(rows):
    """Convert raw sheet rows into a list of event dicts."""
    events = []
    for i, row in enumerate(rows):
        row = (row + [""] * 7)[:7]
        date_raw, name, time_raw, location, desc, link, published = row

        if not name.strip() and not date_raw.strip():
            continue

        is_published = published.strip().upper() != "FALSE"
        if not is_published:
            continue

        d = parse_date(date_raw)
        if d is None:
            print(f"  ⚠️  row {i+2}: skipping — bad date '{date_raw}' "
                  f"(use YYYY-MM-DD in the Date cell)", file=sys.stderr)
            continue

        ev = {"name": name.strip(), "date": d.isoformat()}
        t = normalize_time(time_raw)
        if t:
            ev["time"] = t
        if location.strip():
            ev["location"] = location.strip()
        if desc.strip():
            ev["description"] = desc.strip()
        if link.strip():
            ev["link"] = normalize_link(link)

        events.append(ev)

    events.sort(key=lambda e: e["date"])
    return events


def write_events_json(events):
    payload = {"events": events}
    text = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    if EVENTS_FILE.exists() and EVENTS_FILE.read_text(encoding="utf-8") == text:
        return False
    EVENTS_FILE.write_text(text, encoding="utf-8")
    return True


def git_push():
    def run(cmd):
        p = subprocess.run(cmd, cwd=REPO_DIR, capture_output=True, text=True)
        if p.returncode != 0:
            print(f"  git {' '.join(cmd[1:])} failed:\n{p.stderr.strip()}",
                  file=sys.stderr)
        return p

    run(["git", "add", "events.json"])
    if run(["git", "diff", "--cached", "--quiet"]).returncode == 0:
        return False

    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    if run(["git", "commit", "-m", f"Sync events from Google Sheets ({stamp})"]).returncode != 0:
        fail("Could not commit events.json — check ~/youth-division-landing repo state.")

    for attempt in (1, 2):
        if run(["git", "push", "origin", "gh-pages"]).returncode == 0:
            return True
        # Push failed — likely non-fast-forward (repo edited elsewhere). Sync & retry once.
        print(f"  push attempt {attempt} failed — pulling --rebase and retrying",
              file=sys.stderr)
        if run(["git", "pull", "--rebase", "origin", "gh-pages"]).returncode != 0:
            fail("git pull --rebase failed — resolve ~/youth-division-landing manually.")

    fail("git push failed twice — website events NOT updated.")


def main():
    print("Reading sheet...")
    rows = read_sheet()
    events = parse_rows(rows)
    print(f"  {len(events)} published events found")

    changed = write_events_json(events)
    if not changed:
        print("No changes — events.json is already up to date. Nothing to push.")
        return

    print("events.json updated. Pushing to GitHub...")
    git_push()
    print("✅ Pushed to gh-pages. Site will update within ~1 minute.")


if __name__ == "__main__":
    main()
