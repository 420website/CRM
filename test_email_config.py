#!/usr/bin/env python3

import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_dir))

# Load environment variables like the server does
from dotenv import load_dotenv
load_dotenv(backend_dir / '.env')

# Test what email address would be used
support_email = os.environ.get('SUPPORT_EMAIL', 'support@my420.ca')

print("=== EMAIL CONFIGURATION TEST ===")
print(f"Environment file: {backend_dir / '.env'}")
print(f"SUPPORT_EMAIL from env: {os.environ.get('SUPPORT_EMAIL', 'NOT SET')}")
print(f"support_email variable: {support_email}")
print(f"Raw env var: {repr(os.environ.get('SUPPORT_EMAIL'))}")

# Test what the actual server code would use
print("\n=== SIMULATING SERVER EMAIL CONFIG ===")
smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
smtp_port = int(os.environ.get('SMTP_PORT', '587'))
smtp_username = os.environ.get('SMTP_USERNAME', '')
smtp_password = os.environ.get('SMTP_PASSWORD', '')

print(f"SMTP Server: {smtp_server}")
print(f"SMTP Port: {smtp_port}")
print(f"SMTP Username: {smtp_username}")
print(f"Support Email: {support_email}")