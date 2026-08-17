#!/usr/bin/env python3
"""One-time setup for the ONEIGHTY Events Google Sheet.

Adds the header row, data validation (date picker + TRUE/FALSE dropdown),
and seeds the sheet with the current events so the media team has a template
to follow. Idempotent: safe to re-run.
"""
import json
import sys
from pathlib import Path

# Add the google-workspace scripts dir to path so we can reuse auth helpers
_SCRIPTS_DIR = str(Path.home() / ".hermes/skills/productivity/google-workspace/scripts")
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

from _hermes_home import get_hermes_home
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

HERMES_HOME = get_hermes_home()
TOKEN_PATH = HERMES_HOME / "google_token.json"
CLIENT_SECRET_PATH = HERMES_HOME / "google_client_secret.json"

# Sheet ID is intentionally NOT stored in this public repo.
# The live pipeline reads it from ~/.hermes/oneighty_sheet_id (private),
# created once with:  echo "<SHEET_ID>" > ~/.hermes/oneighty_sheet_id
SHEET_ID = (HERMES_HOME / "oneighty_sheet_id").read_text(encoding="utf-8").strip()

HEADERS = ["Date", "Name", "Time", "Location", "Description", "Link", "Published"]

# Seed with the current events (leave Published = TRUE)
SEED = [
    ["2026-08-22", "Youth Hangout Night", "18.30", "WTC LT.3 — Next Gen",
     "Game night + snacks + a chance to meet new people. Bring a friend.",
     "https://www.instagram.com/oneightywtc/", "TRUE"],
    ["2026-08-23", "ONEIGHTY Combined Service", "10.00", "WTC LT.3",
     "All grades together for one big service — worship, word, and small groups.",
     "https://www.instagram.com/oneightywtc/", "TRUE"],
    ["2026-09-06", "Back to School Celebration", "13.30", "WTC LT.3 — Next Gen",
     "Kick off the new school year with us. Special guest, giveaways, and more.",
     "https://www.instagram.com/oneightywtc/", "TRUE"],
]


def get_creds():
    data = json.loads(TOKEN_PATH.read_text())
    creds = Credentials.from_authorized_user_info(data)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return creds


def build_service():
    creds = get_creds()
    return build("sheets", "v4", credentials=creds)


def main():
    svc = build_service()
    sheets = svc.spreadsheets()

    # 1. Write header row
    print("Writing header row...")
    sheets.values().update(
        spreadsheetId=SHEET_ID,
        range="A1:G1",
        valueInputOption="RAW",
        body={"values": [HEADERS]},
    ).execute()

    # 2. Seed data if empty (check if A2 is empty)
    existing = sheets.values().get(
        spreadsheetId=SHEET_ID, range="A2:A"
    ).execute()
    rows = existing.get("values", [])
    if not rows:
        print("Seeding sample events...")
        sheets.values().update(
            spreadsheetId=SHEET_ID,
            range="A2",
            valueInputOption="RAW",
            body={"values": SEED},
        ).execute()
    else:
        print(f"Skipping seed — {len(rows)} data rows already present.")

    # 3. Format column A as date (gives date-picker UX) + TRUE/FALSE dropdown for Published
    print("Adding formatting + data validation...")
    requests = [
        # Date column (A) — apply a date number format so cells show/accept dates
        {
            "repeatCell": {
                "range": {"sheetId": 0, "startRowIndex": 1, "endRowIndex": 500,
                          "startColumnIndex": 0, "endColumnIndex": 1},
                "cell": {"userEnteredFormat": {
                    "numberFormat": {"type": "DATE", "pattern": "yyyy-mm-dd"}
                }},
                "fields": "userEnteredFormat.numberFormat",
            }
        },
        # Published column (G) — dropdown TRUE/FALSE
        {
            "setDataValidation": {
                "range": {"sheetId": 0, "startRowIndex": 1, "endRowIndex": 500,
                          "startColumnIndex": 6, "endColumnIndex": 7},
                "rule": {
                    "condition": {
                        "type": "ONE_OF_LIST",
                        "values": [
                            {"userEnteredValue": "TRUE"},
                            {"userEnteredValue": "FALSE"},
                        ],
                    },
                    "showCustomUi": True,
                    "strict": True,
                },
            }
        },
    ]
    sheets.batchUpdate(
        spreadsheetId=SHEET_ID,
        body={"requests": requests},
    ).execute()

    # 4. Add an instructions note in H1
    sheets.values().update(
        spreadsheetId=SHEET_ID,
        range="H1",
        valueInputOption="RAW",
        body={"values": [[
            "HOW TO ADD AN EVENT: add a new row below. Date = YYYY-MM-DD (or pick from calendar). "
            "Published = TRUE to show on the website, FALSE to hide/draft. "
            "The website updates automatically within ~1 hour."
        ]]},
    ).execute()

    # 5. Format header row (bold)
    sheets.batchUpdate(
        spreadsheetId=SHEET_ID,
        body={"requests": [{
            "repeatCell": {
                "range": {"sheetId": 0, "startRowIndex": 0, "endRowIndex": 1,
                          "startColumnIndex": 0, "endColumnIndex": 7},
                "cell": {"userEnteredFormat": {"textFormat": {"bold": True}}},
                "fields": "userEnteredFormat.textFormat.bold",
            }
        }]},
    ).execute()

    print("\n✅ Setup complete.")
    print("Spreadsheet: https://docs.google.com/spreadsheets/d/" + SHEET_ID + "/edit")


if __name__ == "__main__":
    main()
