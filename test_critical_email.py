#!/usr/bin/env python3

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from dotenv import load_dotenv

# Load environment like the backend does
backend_dir = Path(__file__).parent / 'backend'
load_dotenv(backend_dir / '.env')

# Test EXACT finalization email logic
def test_finalization_email():
    """Test the exact email logic used in finalization"""
    
    # EXACT same logic as finalization endpoint
    env_support_email = os.environ.get('SUPPORT_EMAIL')
    fallback_email = 'support@my420.ca'
    support_email = env_support_email if env_support_email else fallback_email
    
    print("=== FINALIZATION EMAIL LOGIC TEST ===")
    print(f"Raw env var: {repr(os.environ.get('SUPPORT_EMAIL'))}")
    print(f"Env support_email: {env_support_email}")
    print(f"Final support_email: {support_email}")
    print(f"Will send to: {support_email}")
    
    # SMTP Configuration
    smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.environ.get('SMTP_PORT', '587'))
    smtp_username = os.environ.get('SMTP_USERNAME', '')
    smtp_password = os.environ.get('SMTP_PASSWORD', '')
    
    print(f"\nSMTP Server: {smtp_server}")
    print(f"SMTP Username: {smtp_username}")
    print(f"Recipient: {support_email}")
    
    # Create test email
    subject = "CRITICAL TEST - Finalization Email"
    body = f"""
CRITICAL EMAIL TEST

This email is being sent to test the finalization email system.

CONFIGURATION:
- Environment SUPPORT_EMAIL: {env_support_email}
- Final recipient: {support_email}
- SMTP Server: {smtp_server}
- SMTP Username: {smtp_username}

If you receive this at 420pharmacyprogram@gmail.com, the system is working.
If you receive this at support@my420.ca, there is still a problem.

Time: {os.popen('date').read().strip()}
"""
    
    try:
        # Send using exact same logic as backend
        msg = MIMEMultipart()
        msg['From'] = smtp_username or support_email
        msg['To'] = support_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        if smtp_username and smtp_password:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_username, smtp_password)
            text = msg.as_string()
            server.sendmail(smtp_username, support_email, text)
            server.quit()
            print(f"\n✅ EMAIL SENT TO: {support_email}")
            return True
        else:
            print(f"\n❌ SMTP credentials missing")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    test_finalization_email()