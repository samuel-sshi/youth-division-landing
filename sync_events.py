#!/usr/bin/env python3
"""Sync ONEIGHTY events from Google Sheets -> events.json -> GitHub Pages.

Reads the "ONEIGHTY Events (Website)" sheet, filters to rows where
Published == TRUE, writes events.json (sorted by date), and pushes
to the gh-pages branch. Safe to run repeatedly; no-op if nothing changed.

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

# Sheet ID is intentionally NOT stored in this public repo.
# The live pipeline reads it from ~/.hermes/oneighty_sheet_id (private),
# created once with:  echo "<SHEET_ID>" > ~/.hermes/oneighty_sheet_id
SHEET_ID = (HERMES_HOME / "oneighty_sheet_id").read_text(encoding="utf-8").strip()
RANGE = "A2:G500"  # data rows only, skip header

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


def get_creds():
    data = json.loads(TOKEN_PATH.read_text())
    creds = Credentials.from_authorized_user_info(data)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return creds


def read_sheet():
    creds = get_creds()
    svc = build("sheets", "v4", credentials=creds)
    result = svc.spreadsheets().values().get(
        spreadsheetId=SHEET_ID, range=RANGE, valueRenderOption="FORMATTED_VALUE"
    ).execute()
    return result.get("values", [])


def parse_date(raw, description=""):
    """Parse a date from flexible formats, including Indonesian.

    Returns date object or None.
    """
    s = str(raw).strip().lower()
    if not s:
        return None

    # ISO first
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            pass

    # e.g. "28 Aug" / "28 Agu" -> use current year
    m = re.match(r"(\d{1,2})\s+([a-z]{3,})", s)
    if m:
        day, mon = int(m.group(1)), m.group(2)
        mon_num = MONTH_MAP.get(mon)
        if mon_num:
            return date(date.today().year, mon_num, day)

    # e.g. "28 Agustus 2026" / "28 Aug 2026"
    m = re.match(r"(\d{1,2})\s+([a-z]+)\s+(\d{4})", s)
    if m:
        day, mon, year = int(m.group(1)), m.group(2), int(m.group(3))
        mon_num = MONTH_MAP.get(mon)
        if mon_num:
            return date(year, mon_num, day)

    # Try to extract "28 Agustus 2026" from description if date cell failed
    if description:
        m = re.search(r"(\d{1,2})\s+([a-z]+)\s+(\d{4})", description.lower())
        if m:
            day, mon, year = int(m.group(1)), m.group(2), int(m.group(3))
            mon_num = MONTH_MAP.get(mon)
            if mon_num:
                return date(year, mon_num, day)

    return None


def normalize_time(raw):
    """Normalize a time value from Sheets to HH.MM format."""
    s = str(raw).strip()
    if not s:
        return ""

    if ":" in s:
        parts = s.split(":")
        try:
            h = int(parts[0]); m = int(parts[1])
            return f"{h:02d}.{m:02d}"
        except (ValueError, IndexError):
            pass

    try:
        f = float(s.replace(",", "."))
    except ValueError:
        return s

    if f == int(f):
        return f"{int(f):02d}.00"
    h = int(f)
    frac = round((f - h) * 100)
    return f"{h:02d}.{frac:02d}"


def normalize_link(raw):
    """Ensure link starts with http:// or https://."""
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
        # Pad short rows
        row = (row + [""] * 7)[:7]
        date_raw, name, time_raw, location, desc, link, published = row

        if not name.strip() and not date_raw.strip():
            continue

        is_published = published.strip().upper() != "FALSE"
        if not is_published:
            continue

        d = parse_date(date_raw, desc)
        if d is None:
            print(f"  ⚠️  row {i+2}: skipping — bad date '{date_raw}'", file=sys.stderr)
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
        return subprocess.run(cmd, cwd=REPO_DIR, capture_output=True, text=True)

    run(["git", "add", "events.json"])
    diff = run(["git", "diff", "--cached", "--quiet"])
    if diff.returncode == 0:
        return False

    today = datetime.now().strftime("%Y-%m-%d %H:%M")
    run(["git", "commit", "-m", f"Sync events from Google Sheets ({today})"])
    run(["git", "push", "origin", "gh-pages"])
    return True


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
    pushed = git_push()
    if pushed:
        print("✅ Pushed to gh-pages. Site will update within ~1 minute.")
    else:
        print("✅ events.json written but git reported no staged change.")


if __name__ == "__main__":
    main()
