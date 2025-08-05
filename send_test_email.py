#!/usr/bin/env python3

import os
import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from datetime import datetime

# Add the backend directory to Python path
backend_dir = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_dir))

# Load environment variables like the server does
from dotenv import load_dotenv
load_dotenv(backend_dir / '.env')

def send_test_email():
    """Send a test email using the exact same configuration as the application"""
    try:
        # Use the exact same email configuration as the application
        smtp_server = os.environ.get('SMTP_SERVER', 'smtp.office365.com')
        smtp_port = int(os.environ.get('SMTP_PORT', '587'))
        smtp_username = os.environ.get('SMTP_USERNAME', '')
        smtp_password = os.environ.get('SMTP_PASSWORD', '')
        support_email = os.environ.get('SUPPORT_EMAIL', 'support@my420.ca')
        
        print("=== EMAIL CONFIGURATION TEST ===")
        print(f"SMTP Server: {smtp_server}")
        print(f"SMTP Port: {smtp_port}")
        print(f"SMTP Username: {smtp_username}")
        print(f"Support Email (Recipient): {support_email}")
        print()
        
        # Create test email
        subject = "TEST EMAIL - Email Configuration Verification"
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        body = f"""
TEST EMAIL - Email Configuration Verification

This is a test email sent at {current_time} to verify that the email configuration 
is working correctly and emails are being sent to the proper address.

Configuration Details:
- SMTP Server: {smtp_server}
- SMTP Port: {smtp_port}
- SMTP Username: {smtp_username}
- Recipient Email: {support_email}

If you receive this email at 420pharmacyprogram@gmail.com, then the email 
configuration is working correctly.

This test email was sent from the MY420.CA application backend.
        """
        
        # Create message using same logic as application
        msg = MIMEMultipart()
        msg['From'] = smtp_username or support_email
        msg['To'] = support_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        print("=== SENDING TEST EMAIL ===")
        print(f"Attempting to send test email to: {support_email}")
        
        # Send email (only if SMTP credentials are configured)
        if smtp_username and smtp_password:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_username, smtp_password)
            text = msg.as_string()
            server.sendmail(smtp_username, support_email, text)
            server.quit()
            print(f"✅ TEST EMAIL SENT SUCCESSFULLY to {support_email}")
            print(f"✅ Check {support_email} for the test email")
            return True
        else:
            print(f"❌ SMTP credentials not configured")
            print(f"Username: {smtp_username}")
            print(f"Password: {'*' * len(smtp_password) if smtp_password else 'Not set'}")
            return False
            
    except Exception as e:
        print(f"❌ FAILED TO SEND TEST EMAIL: {str(e)}")
        return False

if __name__ == "__main__":
    print("MY420.CA Email Configuration Test")
    print("=" * 50)
    success = send_test_email()
    print("=" * 50)
    if success:
        print("✅ Test completed successfully")
        print("✅ Check 420pharmacyprogram@gmail.com for the test email")
    else:
        print("❌ Test failed - check configuration")