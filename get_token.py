#!/usr/bin/env python3
"""
Google Calendar OAuth Token Generator

This script performs the initial OAuth flow to generate token.json for Google Calendar access.
Run this script locally (outside containers) where a browser is available.
"""

import sys
from pathlib import Path

# Add the app directory to Python path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent))

try:
    from app.calendar.auth import GoogleAuthClient
    from app.calendar.config import get_calendar_config
except ImportError as e:
    print(f"Import error: {e}")
    print("Run from project root after: uv sync")
    sys.exit(1)


def main():
    config = get_calendar_config()
    print("📋 Configuration loaded:")
    print(f"   Credentials file: {config.credentials_path}")
    print(f"   Token file: {config.token_path}")
    print(f"   Scopes: {config.scopes}")

    # Check prerequisites
    if not config.credentials_path.exists():
        print(f"Missing: {config.credentials_path}")
        print("Download from Google Cloud Console → APIs & Services → Credentials")
        sys.exit(1)

    # Run OAuth flow
    try:
        print("🔐 Starting OAuth flow...")
        print("💡 A browser window will open for authentication")
        print()

        client = GoogleAuthClient(config)
        service = client.authenticate()
        print()
        print(f"✅ Token saved: {config.token_path}")
        print("Ready for: ./docker/start.sh")
        print(f"Service: {service}")
    except Exception as e:
        print(f"Failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
