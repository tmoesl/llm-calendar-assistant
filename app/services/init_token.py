"""
Google Calendar OAuth Token Initializer

This script performs the initial OAuth flow to generate token.json for Google Calendar access.
Run this script locally (outside containers) where a browser is available.
"""

import sys

from app.calendar.auth import GoogleAuthClient
from app.calendar.config import get_calendar_config

config = get_calendar_config()
print("📋 Configuration loaded:")
print(f"   Credentials file: {config.credentials_path}")
print(f"   Token file: {config.token_path}")
print(f"   Scopes: {config.scopes}")
# Check prerequisites
if not config.credentials_path.exists():
    print(f"❌ Missing: {config.credentials_path}")
    print("   Download from Google Cloud Console → APIs & Services → Credentials")
    sys.exit(1)

print("🔐 Starting OAuth flow...")
print("💡 A browser window will open for authentication")
print()

try:
    client = GoogleAuthClient(config)
    service = client.authenticate()
    print()
    print("✅ Token generated successfully!")
    print("🚀 Ready for: ./docker/start.sh")
except Exception as e:
    print(f"❌ Failed: {e}")
    sys.exit(1)
