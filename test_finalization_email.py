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

# Test the exact same logic used in finalization emails
support_email = os.environ.get('SUPPORT_EMAIL', 'support@my420.ca')

print("=== FINALIZATION EMAIL TEST ===")
print(f"Email will be sent to: {support_email}")
print(f"This should be: 420pharmacyprogram@gmail.com")
print(f"Match: {'✅ CORRECT' if support_email == '420pharmacyprogram@gmail.com' else '❌ WRONG'}")