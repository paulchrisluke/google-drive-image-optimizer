#!/usr/bin/env python3
"""
One-command setup for Google Drive Image Optimizer.

Run this once locally to connect your Google account and get
your 3 GitHub Secrets — no manual JSON editing required.

Usage:
    python setup_secrets.py
"""

import json
import os
import sys
import webbrowser

# Terminal colours (gracefully disabled on Windows if needed)
try:
    import shutil
    _has_colour = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()
except Exception:
    _has_colour = False

BOLD   = "\033[1m"  if _has_colour else ""
GREEN  = "\033[92m" if _has_colour else ""
YELLOW = "\033[93m" if _has_colour else ""
CYAN   = "\033[96m" if _has_colour else ""
RESET  = "\033[0m"  if _has_colour else ""

SCOPES = ["https://www.googleapis.com/auth/drive"]


def print_step(n, text):
    print(f"\n{BOLD}{CYAN}Step {n}{RESET} — {BOLD}{text}{RESET}")


def print_ok(text):
    print(f"  {GREEN}✓{RESET} {text}")


def print_hint(text):
    print(f"  {YELLOW}→{RESET} {text}")


def hr():
    print("  " + "─" * 52)


def main():
    print(f"\n{BOLD}{'=' * 56}{RESET}")
    print(f"{BOLD}  Google Drive Image Optimizer — One-Time Setup{RESET}")
    print(f"{BOLD}{'=' * 56}{RESET}")
    print("\n  This script walks you through connecting your Google")
    print("  Drive account and prints the 3 GitHub Secrets you")
    print(f"  need to add to your repo.  {BOLD}Takes about 5 minutes.{RESET}\n")

    # ------------------------------------------------------------------ #
    # Step 1 — Google Cloud credentials
    # ------------------------------------------------------------------ #
    print_step(1, "Create OAuth credentials in Google Cloud Console")
    print()
    print_hint("You need a free Google Cloud project with the Drive API enabled.")
    print_hint("Follow these steps:\n")
    print(f"    1. Open: {BOLD}https://console.cloud.google.com/apis/credentials{RESET}")
    print(f"    2. Create a project if you don't have one (any name is fine)")
    print(f"    3. Enable the Google Drive API:")
    print(f"       {BOLD}https://console.cloud.google.com/apis/library/drive.googleapis.com{RESET}")
    print(f"    4. Click {BOLD}Create Credentials → OAuth client ID{RESET}")
    print(f"    5. Application type: {BOLD}Desktop app{RESET}")
    print(f"    6. Copy the {BOLD}Client ID{RESET} and {BOLD}Client Secret{RESET}")
    print()

    try:
        answer = input("  Open Google Cloud Console in your browser now? (Y/n): ").strip().lower()
        if answer != "n":
            webbrowser.open("https://console.cloud.google.com/apis/credentials")
            print_ok("Browser opened. Complete the steps above, then come back here.")
    except KeyboardInterrupt:
        print("\n\n  Cancelled.")
        sys.exit(0)

    # ------------------------------------------------------------------ #
    # Step 2 — Collect Client ID / Secret
    # ------------------------------------------------------------------ #
    print_step(2, "Enter your OAuth credentials")
    print()
    try:
        client_id = input("  Client ID:     ").strip()
        if not client_id:
            print("\n  Error: Client ID cannot be empty.")
            sys.exit(1)

        client_secret = input("  Client Secret: ").strip()
        if not client_secret:
            print("\n  Error: Client Secret cannot be empty.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n  Cancelled.")
        sys.exit(0)

    # Write credentials.json
    credentials = {
        "installed": {
            "client_id": client_id,
            "project_id": "google-drive-image-optimizer",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": client_secret,
            "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"],
        }
    }
    with open("credentials.json", "w") as f:
        json.dump(credentials, f, indent=2)
    print_ok("credentials.json saved")

    # ------------------------------------------------------------------ #
    # Step 3 — OAuth browser flow
    # ------------------------------------------------------------------ #
    print_step(3, "Authorize access to your Google Drive")
    print()
    print_hint("A browser window will open. Sign in with the Google account")
    print_hint("whose Drive folders you want to optimize.")
    print_hint("(This is a one-time step — credentials are stored locally.)")
    print()

    try:
        input("  Press Enter to open the browser…")
    except KeyboardInterrupt:
        print("\n\n  Cancelled.")
        sys.exit(0)

    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError:
        print("\n  Error: dependencies not installed.")
        print("  Run: pip install -r requirements.txt\n")
        sys.exit(1)

    try:
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds = flow.run_local_server(port=8080, open_browser=True)
        with open("token.json", "w") as f:
            f.write(creds.to_json())
        print_ok("Authorization complete. token.json saved.")
    except Exception as exc:
        print(f"\n  Error during authorization: {exc}")
        print("  Make sure port 8080 is free and try again.\n")
        sys.exit(1)

    # ------------------------------------------------------------------ #
    # Step 4 — Extract refresh token & print secrets
    # ------------------------------------------------------------------ #
    print_step(4, "Your GitHub Secrets")
    print()

    try:
        with open("token.json", "r") as f:
            token_data = json.load(f)
        refresh_token = token_data.get("refresh_token")
        if not refresh_token:
            print("  Error: no refresh_token in token.json.")
            print("  Run: python main.py --reauth  and try setup_secrets.py again.\n")
            sys.exit(1)
    except Exception as exc:
        print(f"  Error reading token.json: {exc}\n")
        sys.exit(1)

    print_hint(f"Go to your GitHub repo → {BOLD}Settings → Secrets and variables")
    print_hint(f"→ Actions → New repository secret{RESET}")
    print_hint("Add each secret below:\n")

    hr()
    print(f"\n  {BOLD}Secret name:{RESET}  GDRIVE_CLIENT_ID")
    print(f"  {BOLD}Value:{RESET}         {GREEN}{client_id}{RESET}\n")

    print(f"  {BOLD}Secret name:{RESET}  GDRIVE_CLIENT_SECRET")
    print(f"  {BOLD}Value:{RESET}         {GREEN}{client_secret}{RESET}\n")

    print(f"  {BOLD}Secret name:{RESET}  GDRIVE_REFRESH_TOKEN")
    print(f"  {BOLD}Value:{RESET}         {GREEN}{refresh_token}{RESET}\n")
    hr()

    print()
    print_ok(f"{BOLD}Setup complete!{RESET}")
    print()
    print("  Next steps:")
    print_hint("Add the 3 secrets above to your GitHub repo")
    print_hint("Go to Actions → Optimize Drive Folder → Run workflow")
    print_hint("Paste a Google Drive folder link and click Run\n")


if __name__ == "__main__":
    main()
