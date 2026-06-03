#!/usr/bin/env python3
"""
drive_sync.py — push outreach/client artifacts to Google Drive (the storage system of record).

Storage tiers (per plan):
  Tier A outreach -> Outreach/Leads/<segment>/<studio>/<subfolder>   (research|messages|loom)
  Tier B client   -> Clients/<studio>/<subfolder>                    (free-build|proposal|case-study)
Local is used ONLY at Tier C (active paid delivery, ~/Desktop/MyClients) — not by this tool.

Auth: personal Google account via credentials/credentials.json (Drive+Sheets scope) -> token.json.
If credentials.json is missing, runs DRY-RUN (prints the folder path + files it would create).

Usage:
    python tools/drive_sync.py --studio "Nine Bricks Studio" --segment interior \\
        --tier outreach --subfolder messages \\
        --file .tmp/nine_bricks_studio_linkedin_note_first_touch.md
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from config_loader import google_creds_path, google_token_path, SCOPES, env  # noqa: E402

ROOT_FOLDER_ID = env("GOOGLE_DRIVE_ROOT_FOLDER_ID")          # 'Setu' root (optional)
CLIENTS_FOLDER_ID = env("GOOGLE_DRIVE_CLIENTS_FOLDER_ID")    # existing 'Clients' folder (optional)

TIER_PATHS = {
    "outreach": ["Outreach", "Leads"],   # + <segment>/<studio>/<subfolder>
    "client": ["Clients"],               # + <studio>/<subfolder>
}


def get_service(account: str = "personal"):
    """Return a Drive v3 service, or None if creds missing (-> dry-run)."""
    creds_file = google_creds_path(account)
    if not creds_file.exists():
        return None
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    token_file = google_token_path(account)
    creds = None
    if token_file.exists():
        creds = Credentials.from_authorized_user_file(str(token_file), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(creds_file), SCOPES)
            creds = flow.run_local_server(port=0)
        token_file.write_text(creds.to_json(), encoding="utf-8")
    return build("drive", "v3", credentials=creds)


def ensure_folder(svc, name: str, parent_id: str | None) -> str:
    q = ("mimeType='application/vnd.google-apps.folder' and trashed=false "
         f"and name='{name}'")
    if parent_id:
        q += f" and '{parent_id}' in parents"
    res = svc.files().list(q=q, fields="files(id,name)", spaces="drive").execute()
    files = res.get("files", [])
    if files:
        return files[0]["id"]
    meta = {"name": name, "mimeType": "application/vnd.google-apps.folder"}
    if parent_id:
        meta["parents"] = [parent_id]
    folder = svc.files().create(body=meta, fields="id").execute()
    return folder["id"]


def lead_folder_chain(tier: str, segment: str, studio: str, subfolder: str | None) -> list[str]:
    chain = list(TIER_PATHS[tier])
    if tier == "outreach":
        chain += [segment, studio]
    else:
        chain += [studio]
    if subfolder:
        chain += [subfolder]
    return chain


def resolve_folder(svc, chain: list[str], tier: str) -> str:
    # start parent: Clients folder id for client tier, else root folder id (may be None = My Drive)
    parent = CLIENTS_FOLDER_ID if (tier == "client" and CLIENTS_FOLDER_ID) else ROOT_FOLDER_ID
    start = 1 if (tier == "client" and CLIENTS_FOLDER_ID) else 0  # skip 'Clients' if we have its id
    for name in chain[start:]:
        parent = ensure_folder(svc, name, parent)
    return parent


def upload(svc, file_path: Path, parent_id: str) -> str:
    from googleapiclient.http import MediaFileUpload
    meta = {"name": file_path.name, "parents": [parent_id]}
    media = MediaFileUpload(str(file_path), resumable=False)
    f = svc.files().create(body=meta, media_body=media,
                           fields="id,webViewLink").execute()
    return f.get("webViewLink", f.get("id"))


def main():
    ap = argparse.ArgumentParser(description="Push artifacts to Google Drive")
    ap.add_argument("--studio", required=True)
    ap.add_argument("--segment", default="interior")
    ap.add_argument("--tier", default="outreach", choices=list(TIER_PATHS))
    ap.add_argument("--subfolder", help="research|messages|loom (A) or free-build|proposal|case-study (B)")
    ap.add_argument("--file", nargs="*", default=[], help="file(s) to upload")
    args = ap.parse_args()

    chain = lead_folder_chain(args.tier, args.segment, args.studio, args.subfolder)
    path_str = "/".join(chain)

    svc = get_service("personal")
    if svc is None:
        print("[DRY-RUN] credentials/credentials.json missing — would create/use Drive folder:")
        print(f"  {path_str}")
        for f in args.file:
            print(f"  upload: {f}")
        print("Drop Google OAuth client at credentials/credentials.json (Drive+Sheets) to run live.")
        return

    parent = resolve_folder(svc, chain, args.tier)
    folder_link = f"https://drive.google.com/drive/folders/{parent}"
    print(f"Drive folder: {path_str}\n  {folder_link}")
    for f in args.file:
        p = Path(f)
        if not p.exists():
            print(f"  [skip — not found: {f}]")
            continue
        link = upload(svc, p, parent)
        print(f"  uploaded {p.name} -> {link}")
    print("Tip: put folder_link into the ClickUp 'Drive Folder' field via clickup_sync.py --drive")


if __name__ == "__main__":
    main()
