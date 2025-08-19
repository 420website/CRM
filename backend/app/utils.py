import asyncio
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import base64
import subprocess
from pathlib import Path
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats
from datetime import datetime, date
from collections import defaultdict

from app.config import settings
from app.database import db


# PRODUCTION PROTECTION CHECK
def verify_production_protection():
    """Verify production protection is active before starting server"""
    protection_lock = Path("/app/persistent-data/.production-lock")
    protection_flag = Path("/app/.production-protected")

    if protection_lock.exists() and protection_flag.exists():
        print("🛡️ Production protection verified - server starting safely")
        return True
    else:
        print("⚠️ Production protection not found - activating now")
        try:
            subprocess.run(
                [
                    "/root/.venv/bin/python",
                    "/app/scripts/production-lock.py",
                    "--force-protect",
                ],
                check=True,
                cwd="/app/scripts",
            )
            print("✅ Production protection activated")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to activate production protection: {e}")
            return False


def send_registration_email(registration_data):
    """Send registration details to support email"""
    try:
        # Email configuration
        smtp_server = settings.smtp_server
        smtp_port = settings.smtp_port
        smtp_username = settings.smtp_username
        smtp_password = settings.smtp_password
        support_email = settings.support_email

        # CRITICAL: Log the email address being used for debugging
        logging.error(
            f"🚨 CLIENT REGISTRATION EMAIL - Sending to: {support_email}"
        )

        # Create email content
        subject = "New Testing Registration - my420.ca"

        # Email body
        body = f"""
New Registration for Hepatitis C and HIV Testing

Registration Details:
- Name: {registration_data.get('full_name', 'N/A')}
- Date of Birth: {registration_data.get('date_of_birth', 'N/A')}
- Health Card: {registration_data.get('health_card_number', 'Not provided')}
- Phone: {registration_data.get('phone_number', 'Not provided')}
- Email: {registration_data.get('email', 'Not provided')}
- Registration Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- Consent Given: {'Yes' if registration_data.get('consent_given') else 'No'}

Please contact this individual to schedule their testing appointment.

---
This registration was submitted through my420.ca
        """

        # Create message
        msg = MIMEMultipart()
        msg["From"] = smtp_username or support_email
        msg["To"] = support_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        # Send email (only if SMTP credentials are configured)
        if smtp_username and smtp_password:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_username, smtp_password)
            text = msg.as_string()
            server.sendmail(smtp_username, support_email, text)
            server.quit()
            logging.info(
                f"Registration email sent successfully to {support_email}"
            )
            return True
        else:
            # Log the registration for development/testing
            logging.info(
                f"Registration email would be sent to {support_email}: {body}"
            )
            return True

    except Exception as e:
        logging.error(f"Failed to send registration email: {str(e)}")
        return False


async def send_email(
    to_email: str, subject: str, body: str, photo_base64: str = None
):
    """Generic email sending function with optional photo attachment"""
    try:
        smtp_server = settings.smtp_server
        smtp_port = settings.smtp_port
        smtp_username = settings.smtp_username
        smtp_password = settings.smtp_password

        # Create message
        msg = MIMEMultipart()
        msg["From"] = smtp_username or to_email
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        # Add photo attachment if provided
        if photo_base64:
            try:
                # Decode base64 image
                if photo_base64.startswith("data:"):
                    # Remove data:image/xxx;base64, prefix
                    photo_base64 = photo_base64.split(",")[1]

                photo_data = base64.b64decode(photo_base64)

                # Create attachment
                attachment = MIMEBase("application", "octet-stream")
                attachment.set_payload(photo_data)
                encoders.encode_base64(attachment)
                attachment.add_header(
                    "Content-Disposition",
                    'attachment; filename="client_photo.jpg"',
                )
                msg.attach(attachment)
                logging.info("Photo attachment added to email")
            except Exception as photo_error:
                logging.error(
                    f"Error adding photo attachment: {str(photo_error)}"
                )

        # Send email (only if SMTP credentials are configured)
        if smtp_username and smtp_password:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_username, smtp_password)
            text = msg.as_string()
            server.sendmail(smtp_username, to_email, text)
            server.quit()
            logging.info(f"Email sent successfully to {to_email}")
            return True
        else:
            # Log the email for development/testing
            photo_info = " (with photo attachment)" if photo_base64 else ""
            logging.info(
                f"Email would be sent to {to_email}{photo_info}: {body}"
            )
            return True

    except Exception as e:
        logging.error(f"Failed to send email: {str(e)}")
        return False


def send_contact_email(contact_data):
    """Send contact message to support email"""
    try:
        # Email configuration
        smtp_server = settings.smtp_server
        smtp_port = settings.smtp_port
        smtp_username = settings.smtp_username
        smtp_password = settings.smtp_password
        support_email = settings.support_email

        # CRITICAL: Log the email address being used for debugging
        logging.error(f"🚨 CONTACT EMAIL - Sending to: {support_email}")

        # Create email content
        subject = f"New Contact Message - {contact_data.get('subject', 'General Inquiry')} - my420.ca"

        # Email body
        body = f"""
New Contact Message from my420.ca

Contact Details:
- Name: {contact_data.get('name', 'N/A')}
- Email: {contact_data.get('email', 'N/A')}
- Subject: {contact_data.get('subject', 'General Inquiry')}
- Submitted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Message:
{contact_data.get('message', 'No message provided')}

---
Reply directly to: {contact_data.get('email', 'N/A')}
This message was submitted through my420.ca contact form
        """

        # Create message
        msg = MIMEMultipart()
        msg["From"] = smtp_username or support_email
        msg["To"] = support_email
        msg["Reply-To"] = contact_data.get("email", support_email)
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        # Send email (only if SMTP credentials are configured)
        if smtp_username and smtp_password:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(smtp_username, smtp_password)
            text = msg.as_string()
            server.sendmail(smtp_username, support_email, text)
            server.quit()
            logging.info(f"Contact email sent successfully to {support_email}")
            return True
        else:
            # Log the contact message for development/testing
            logging.info(
                f"Contact email would be sent to {support_email}: {body}"
            )
            return True

    except Exception as e:
        logging.error(f"Failed to send contact email: {str(e)}")
        return False


async def send_finalization_email_async(
    registration_data: dict, registration_id: str
):
    """Async email sending function"""
    try:
        support_email = settings.support_email
        subject = f"FINAL - Admin Registration - {registration_data.get('firstName')} {registration_data.get('lastName')}"

        # CRITICAL: Log the email address being used for debugging
        logging.error(
            f"🚨 ASYNC FINALIZATION EMAIL - Sending to: {support_email}"
        )

        email_body = f"""
Registration Date: {registration_data.get('regDate')}

New Registration

PATIENT INFORMATION:
• First Name: {registration_data.get('firstName')}
• Last Name: {registration_data.get('lastName')}
• Date of Birth: {registration_data.get('dob') or 'Not provided'}
• Patient Consent: {registration_data.get('patientConsent')}
• Gender: {registration_data.get('gender') or 'Not provided'}
• AKA: {registration_data.get('aka') or 'Not provided'}
• Age: {registration_data.get('age') or 'Not provided'}
• Health Card: {registration_data.get('healthCard') or 'Not provided'}
• Health Card Version: {registration_data.get('healthCardVersion') or 'Not provided'}
• Referral Site: {registration_data.get('referralSite') or 'Not provided'}

CONTACT INFORMATION:
• Phone 1: {registration_data.get('phone1') or 'Not provided'}
• Phone 2: {registration_data.get('phone2') or 'Not provided'}
• Extension 1: {registration_data.get('ext1') or 'Not provided'}
• Extension 2: {registration_data.get('ext2') or 'Not provided'}
• Email: {registration_data.get('email') or 'Not provided'}
• Address: {registration_data.get('address') or 'Not provided'}
• Unit #: {registration_data.get('unitNumber') or 'Not provided'}
• City: {registration_data.get('city') or 'Not provided'}
• Province: {registration_data.get('province')}
• Postal Code: {registration_data.get('postalCode') or 'Not provided'}
• Preferred Contact Time: {registration_data.get('preferredTime') or 'Not provided'}
• Language: {registration_data.get('language')}"""

        # Only include contact preferences if any are checked
        contact_prefs = []
        if registration_data.get("leaveMessage"):
            contact_prefs.append("Leave Message")
        if registration_data.get("voicemail"):
            contact_prefs.append("Voicemail")
        if registration_data.get("text"):
            contact_prefs.append("Text Messages")

        if contact_prefs:
            email_body += f"\n\nCONTACT PREFERENCES:\n"
            for pref in contact_prefs:
                email_body += f"• {pref}: Yes\n"

        email_body += f"""

OTHER INFORMATION:
• Special Attention/Notes: {registration_data.get('specialAttention') or 'None provided'}
• Instructions: {registration_data.get('instructions') or 'None provided'}
• Photo Attached: {'Yes' if registration_data.get('photo') else 'No'}
• Physician: {registration_data.get('physician') or 'Not specified'}
• Disposition: {registration_data.get('disposition') or 'Not provided'}

CLINICAL SUMMARY TEMPLATE:
{process_clinical_template(registration_data.get('summaryTemplate', 'No clinical summary provided'), registration_data)}
"""

        # Limit photo size for email performance
        photo_data = registration_data.get("photo")
        if photo_data and len(photo_data) > 300 * 1024:  # 300KB limit
            logging.warning(
                f"Photo too large for email ({len(photo_data)} bytes), sending without photo"
            )
            photo_data = None

        # Send email with timeout
        await asyncio.wait_for(
            send_email(
                to_email=support_email,
                subject=subject,
                body=email_body,
                photo_base64=photo_data,
            ),
            timeout=20.0,
        )

        logging.info(
            f"Background email sent successfully for registration - ID: {registration_id}"
        )

    except Exception as email_error:
        logging.error(
            f"Failed to send background email for registration {registration_id}: {str(email_error)}"
        )


def send_finalization_email_sync(
    registration_data: dict, registration_id: str
):
    """Background email sending using threading"""
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(
            send_finalization_email_async(registration_data, registration_id)
        )
        loop.close()
        logging.info(
            f"Background email completed successfully for registration {registration_id}"
        )
    except Exception as e:
        logging.error(
            f"Background email failed for registration {registration_id}: {str(e)}"
        )


# Clinical Template Processing Function
def process_clinical_template(
    template_content: str, registration_data: dict
) -> str:
    """Process clinical template content to make it conditional based on client data"""
    if not template_content:
        return template_content

    # Check if this is the positive template that needs address/phone processing
    if (
        "Client does have a valid address and has also provided a phone number for results"
        in template_content
    ):
        # Extract client contact information
        address = registration_data.get("address", "").strip()
        phone = (
            registration_data.get("phone1", "").strip()
            or registration_data.get("phone", "").strip()
        )

        # Determine the appropriate contact message
        if address and phone:
            contact_message = "Client does have a valid address and has also provided a phone number for results."
        elif address and not phone:
            contact_message = "Client does have a valid address but no phone number for results."
        elif not address and phone:
            contact_message = "Client does not have a valid address but has provided a phone number for results."
        else:
            contact_message = "Client does not have a valid address or phone number for results."

        # Replace the static message with the dynamic one
        processed_content = template_content.replace(
            "Client does have a valid address and has also provided a phone number for results.",
            contact_message,
        )

        return processed_content

    return template_content


def generate_monthly_trend_chart(
    monthly_data: dict, title: str = "Monthly Registration Trends"
) -> tuple:
    """Generate interactive bar chart with trend line"""

    # Prepare data
    months = sorted(monthly_data.keys())
    values = [monthly_data[month] for month in months]

    # Create subplot with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Add bar chart
    fig.add_trace(
        go.Bar(
            x=months,
            y=values,
            name="Registrations",
            marker_color="rgba(55, 128, 191, 0.7)",
            hovertemplate="<b>%{x}</b><br>Registrations: %{y}<extra></extra>",
        )
    )

    # Calculate and add trend line
    if len(values) > 2:
        x_numeric = list(range(len(values)))
        slope, intercept, r_value, p_value, std_err = stats.linregress(
            x_numeric, values
        )
        trend_line = [slope * x + intercept for x in x_numeric]

        fig.add_trace(
            go.Scatter(
                x=months,
                y=trend_line,
                mode="lines",
                name=f"Trend Line (R²={r_value**2:.3f})",
                line=dict(color="red", width=3),
                hovertemplate="<b>%{x}</b><br>Trend: %{y:.0f}<extra></extra>",
            ),
            secondary_y=False,
        )

    # Update layout for mobile compatibility
    fig.update_layout(
        title=title,
        xaxis_title="Month",
        yaxis_title="Number of Registrations",
        hovermode="x unified",
        height=400,
        showlegend=True,
        font=dict(size=10),
        template="plotly_white",
        xaxis=dict(tickangle=45),
        margin=dict(l=40, r=40, t=60, b=40),
    )

    # Create mobile-friendly HTML
    chart_html = f"""
    <html>
    <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://cdn.plot.ly/plotly-2.26.0.min.js"></script>
    </head>
    <body style="margin:0; padding:10px;">
        <div id="chart" style="width:100%; height:380px;"></div>
        <script>
            var data = {fig.to_json()};
            Plotly.newPlot('chart', data.data, data.layout, {{responsive: true, displayModeBar: false}});
        </script>
    </body>
    </html>
    """

    # Generate static image (optional - fallback if kaleido fails)
    try:
        chart_image = fig.to_image(format="png", width=1000, height=600)
    except Exception:
        chart_image = None

    return chart_html, chart_image


def generate_disposition_bar_chart(
    disposition_data: dict, title: str = "Disposition Breakdown"
) -> tuple:
    """Generate horizontal bar chart for dispositions"""

    # Sort by count (descending) and take top 15 for mobile
    sorted_dispositions = sorted(
        disposition_data.items(), key=lambda x: x[1], reverse=True
    )[:15]
    dispositions = [item[0] for item in sorted_dispositions]
    counts = [item[1] for item in sorted_dispositions]

    # Create horizontal bar chart
    fig = go.Figure(
        data=[
            go.Bar(
                y=dispositions,
                x=counts,
                orientation="h",
                marker_color="rgba(55, 128, 191, 0.7)",
                hovertemplate="<b>%{y}</b><br>Count: %{x}<extra></extra>",
            )
        ]
    )

    fig.update_layout(
        title=title,
        xaxis_title="Number of Cases",
        yaxis_title="Disposition",
        height=max(350, len(dispositions) * 20),
        font=dict(size=10),
        template="plotly_white",
        margin=dict(l=40, r=40, t=60, b=40),
    )

    # Create mobile-friendly HTML
    chart_html = f"""
    <html>
    <head>
        <meta charset="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <script src="https://cdn.plot.ly/plotly-2.26.0.min.js"></script>
    </head>
    <body style="margin:0; padding:10px;">
        <div id="chart" style="width:100%; height:{max(330, len(dispositions) * 20)}px;"></div>
        <script>
            var data = {fig.to_json()};
            Plotly.newPlot('chart', data.data, data.layout, {{responsive: true, displayModeBar: false}});
        </script>
    </body>
    </html>
    """

    # Generate static image (optional - fallback if kaleido fails)
    try:
        chart_image = fig.to_image(
            format="png", width=1000, height=max(400, len(dispositions) * 25)
        )
    except Exception:
        chart_image = None

    return chart_html, chart_image


def generate_yearly_comparison_chart(
    yearly_data: dict,
    monthly_data: dict,
    title: str = "Year-over-Year Comparison",
) -> tuple:
    """Generate comparison chart between years"""

    # Group monthly data by year
    year_month_data = {}
    for month_key, value in monthly_data.items():
        year = month_key[:4]
        month = month_key[5:7]
        if year not in year_month_data:
            year_month_data[year] = {}
        year_month_data[year][month] = value

    fig = go.Figure()

    # Add bars for each year
    colors = [
        "rgba(55, 128, 191, 0.7)",
        "rgba(219, 64, 82, 0.7)",
        "rgba(55, 191, 128, 0.7)",
    ]
    for i, (year, months) in enumerate(year_month_data.items()):
        month_names = [f"{year}-{month}" for month in sorted(months.keys())]
        values = [months[month] for month in sorted(months.keys())]

        fig.add_trace(
            go.Bar(
                x=month_names,
                y=values,
                name=f"{year} ({sum(values)} total)",
                marker_color=colors[i % len(colors)],
                hovertemplate="<b>%{x}</b><br>%{y} registrations<extra></extra>",
            )
        )

    fig.update_layout(
        title=title,
        xaxis_title="Month",
        yaxis_title="Number of Registrations",
        barmode="group",
        hovermode="x unified",
        height=500,
        font=dict(size=12),
        template="plotly_white",
        xaxis=dict(tickangle=45),
    )

    # Convert to HTML
    chart_html = fig.to_html(
        include_plotlyjs="cdn", div_id="yearly-comparison-chart"
    )

    # Generate static image (optional - fallback if kaleido fails)
    try:
        chart_image = fig.to_image(format="png", width=1200, height=600)
    except Exception:
        chart_image = None

    return chart_html, chart_image


# AI Assistant Data Analytics Functions
async def get_registration_stats():
    """Get comprehensive registration statistics"""
    try:
        total_registrations = await db.admin_registrations.count_documents({})
        pending_count = await db.admin_registrations.count_documents(
            {"status": "pending_review"}
        )
        completed_count = await db.admin_registrations.count_documents(
            {"status": "completed"}
        )

        # Get registration dates for trends
        registrations = await db.admin_registrations.find(
            {},
            {
                "regDate": 1,
                "timestamp": 1,
                "disposition": 1,
                "referralSite": 1,
                "physician": 1,
                "province": 1,
            },
        ).to_list(None)

        # Date-based statistics
        daily_counts = defaultdict(int)
        monthly_counts = defaultdict(int)
        yearly_counts = defaultdict(int)
        disposition_counts = defaultdict(int)
        referral_site_counts = defaultdict(int)
        physician_counts = defaultdict(int)
        province_counts = defaultdict(int)

        for reg in registrations:
            reg_date = reg.get("regDate", "")
            if reg_date:
                daily_counts[reg_date] += 1
                try:
                    date_obj = datetime.fromisoformat(reg_date)
                    monthly_key = f"{date_obj.year}-{date_obj.month:02d}"
                    yearly_key = str(date_obj.year)
                    monthly_counts[monthly_key] += 1
                    yearly_counts[yearly_key] += 1
                except:
                    pass

            # Count dispositions
            disposition = reg.get("disposition", "Not specified")
            if disposition:
                disposition_counts[disposition] += 1

            # Count referral sites
            referral_site = reg.get("referralSite", "Not specified")
            if referral_site:
                referral_site_counts[referral_site] += 1

            # Count physicians
            physician = reg.get("physician", "Not specified")
            if physician:
                physician_counts[physician] += 1

            # Count provinces
            province = reg.get("province", "Not specified")
            if province:
                province_counts[province] += 1

        return {
            "total_registrations": total_registrations,
            "pending_count": pending_count,
            "completed_count": completed_count,
            "daily_counts": dict(daily_counts),
            "monthly_counts": dict(monthly_counts),
            "yearly_counts": dict(yearly_counts),
            "disposition_counts": dict(disposition_counts),
            "referral_site_counts": dict(referral_site_counts),
            "physician_counts": dict(physician_counts),
            "province_counts": dict(province_counts),
        }
    except Exception as e:
        logging.error(f"Error getting registration stats: {str(e)}")
        return {}


def analyze_query(query: str, stats: dict):
    """Analyze user query and generate appropriate response"""
    query_lower = query.lower()

    # Greeting responses
    if any(
        greeting in query_lower
        for greeting in [
            "hello",
            "hi",
            "hey",
            "good morning",
            "good afternoon",
        ]
    ):
        return "Hello! I'm your registration data assistant. I can help you analyze enrollment statistics, dispositions, trends, and any other data-related questions about your registrations. What would you like to know?"

    # Help responses
    if any(
        word in query_lower
        for word in ["help", "what can you do", "capabilities"]
    ):
        return """I can help you with registration data analysis including:

📊 **Statistics**: Total registrations, pending/completed counts, averages
📈 **Trends**: Daily, monthly, yearly enrollment patterns  
📋 **Dispositions**: Breakdown by patient disposition types
🏥 **Referral Sites**: Analysis by referral location
👨‍⚕️ **Physicians**: Distribution by assigned physician
📍 **Geography**: Registration breakdown by province
📅 **Time Periods**: Data for specific days, months, or years
📊 **Percentages**: Calculate ratios and percentages

Just ask me questions like:
• "How many registrations this month?"
• "What's the most common disposition?"
• "Show me enrollment trends by referral site"
• "What percentage of registrations are completed?"

What would you like to analyze?"""

    # Total registrations
    if "total" in query_lower and (
        "registration" in query_lower or "enrollment" in query_lower
    ):
        total = stats.get("total_registrations", 0)
        pending = stats.get("pending_count", 0)
        completed = stats.get("completed_count", 0)

        completion_rate = (completed / total * 100) if total > 0 else 0

        return f"""📊 **Total Registration Summary:**

• **Total Registrations**: {total}
• **Pending Review**: {pending}
• **Completed**: {completed}
• **Completion Rate**: {completion_rate:.1f}%

{f"📈 Most active month: {max(stats.get('monthly_counts', {}), key=stats.get('monthly_counts', {}).get) if stats.get('monthly_counts') else 'No monthly data'}" if stats.get('monthly_counts') else ""}"""

    # Disposition analysis
    if "disposition" in query_lower:
        disposition_counts = stats.get("disposition_counts", {})
        if disposition_counts:
            total_with_disposition = sum(disposition_counts.values())
            disposition_list = []

            # Sort by count (descending)
            sorted_dispositions = sorted(
                disposition_counts.items(), key=lambda x: x[1], reverse=True
            )

            for disposition, count in sorted_dispositions[:10]:  # Top 10
                percentage = (
                    (count / total_with_disposition * 100)
                    if total_with_disposition > 0
                    else 0
                )
                disposition_list.append(
                    f"• **{disposition}**: {count} ({percentage:.1f}%)"
                )

            return f"""📋 **Disposition Analysis:**

{chr(10).join(disposition_list)}

**Total with disposition data**: {total_with_disposition}
**Most common**: {sorted_dispositions[0][0] if sorted_dispositions else 'None'}"""
        else:
            return "No disposition data available in the registrations."

    # Monthly/yearly trends
    if any(
        word in query_lower
        for word in ["monthly", "month", "trend", "pattern"]
    ):
        monthly_counts = stats.get("monthly_counts", {})
        if monthly_counts:
            sorted_months = sorted(monthly_counts.items())
            month_list = []

            for month, count in sorted_months[-12:]:  # Last 12 months
                month_list.append(f"• **{month}**: {count} registrations")

            avg_monthly = (
                sum(monthly_counts.values()) / len(monthly_counts)
                if monthly_counts
                else 0
            )
            peak_month = (
                max(monthly_counts, key=monthly_counts.get)
                if monthly_counts
                else "None"
            )

            return f"""📈 **Monthly Registration Trends:**

{chr(10).join(month_list)}

📊 **Summary:**
• **Average per month**: {avg_monthly:.1f}
• **Peak month**: {peak_month} ({monthly_counts.get(peak_month, 0)} registrations)
• **Total months with data**: {len(monthly_counts)}"""
        else:
            return "No monthly trend data available."

    # Referral site analysis
    if "referral" in query_lower or "site" in query_lower:
        referral_counts = stats.get("referral_site_counts", {})
        if referral_counts:
            total_referrals = sum(referral_counts.values())
            sorted_sites = sorted(
                referral_counts.items(), key=lambda x: x[1], reverse=True
            )

            site_list = []
            for site, count in sorted_sites[:10]:  # Top 10
                percentage = (
                    (count / total_referrals * 100)
                    if total_referrals > 0
                    else 0
                )
                site_list.append(f"• **{site}**: {count} ({percentage:.1f}%)")

            return f"""🏥 **Referral Site Analysis:**

{chr(10).join(site_list)}

**Total referrals**: {total_referrals}
**Top referral source**: {sorted_sites[0][0] if sorted_sites else 'None'}"""
        else:
            return "No referral site data available."

    # Physician analysis
    if "physician" in query_lower or "doctor" in query_lower:
        physician_counts = stats.get("physician_counts", {})
        if physician_counts:
            total_assignments = sum(physician_counts.values())
            sorted_physicians = sorted(
                physician_counts.items(), key=lambda x: x[1], reverse=True
            )

            physician_list = []
            for physician, count in sorted_physicians:
                percentage = (
                    (count / total_assignments * 100)
                    if total_assignments > 0
                    else 0
                )
                physician_list.append(
                    f"• **{physician}**: {count} ({percentage:.1f}%)"
                )

            return f"""👨‍⚕️ **Physician Assignment Analysis:**

{chr(10).join(physician_list)}

**Total assignments**: {total_assignments}
**Most assigned**: {sorted_physicians[0][0] if sorted_physicians else 'None'}"""
        else:
            return "No physician assignment data available."

    # Province analysis
    if (
        "province" in query_lower
        or "location" in query_lower
        or "geographic" in query_lower
    ):
        province_counts = stats.get("province_counts", {})
        if province_counts:
            total_provinces = sum(province_counts.values())
            sorted_provinces = sorted(
                province_counts.items(), key=lambda x: x[1], reverse=True
            )

            province_list = []
            for province, count in sorted_provinces:
                percentage = (
                    (count / total_provinces * 100)
                    if total_provinces > 0
                    else 0
                )
                province_list.append(
                    f"• **{province}**: {count} ({percentage:.1f}%)"
                )

            return f"""📍 **Geographic Distribution:**

{chr(10).join(province_list)}

**Total with location data**: {total_provinces}
**Primary province**: {sorted_provinces[0][0] if sorted_provinces else 'None'}"""
        else:
            return "No province/location data available."

    # Percentage queries
    if (
        "percentage" in query_lower
        or "percent" in query_lower
        or "%" in query_lower
    ):
        total = stats.get("total_registrations", 0)
        pending = stats.get("pending_count", 0)
        completed = stats.get("completed_count", 0)

        if total > 0:
            pending_pct = pending / total * 100
            completed_pct = completed / total * 100

            return f"""📊 **Registration Percentages:**

• **Pending Review**: {pending_pct:.1f}% ({pending} out of {total})
• **Completed**: {completed_pct:.1f}% ({completed} out of {total})

**Completion Rate Trend**: {completed_pct:.1f}% of all registrations have been finalized."""
        else:
            return (
                "No registration data available for percentage calculations."
            )

    # Today's registrations
    if "today" in query_lower:
        today_str = date.today().isoformat()
        daily_counts = stats.get("daily_counts", {})
        today_count = daily_counts.get(today_str, 0)

        # Get recent days for context
        recent_days = sorted(daily_counts.items())[-7:]  # Last 7 days
        avg_recent = (
            sum(count for _, count in recent_days) / len(recent_days)
            if recent_days
            else 0
        )

        context = ""
        if recent_days:
            context = f"\n\n📅 **Recent 7 days average**: {avg_recent:.1f} registrations/day"

        return f"""📅 **Today's Registrations ({today_str}):**

**Registrations today**: {today_count}{context}

{"📈 Above average!" if today_count > avg_recent else "📊 Within normal range" if today_count == avg_recent else "📉 Below average" if avg_recent > 0 else ""}"""

    # Average calculations
    if "average" in query_lower or "avg" in query_lower:
        daily_counts = stats.get("daily_counts", {})
        monthly_counts = stats.get("monthly_counts", {})

        daily_avg = (
            sum(daily_counts.values()) / len(daily_counts)
            if daily_counts
            else 0
        )
        monthly_avg = (
            sum(monthly_counts.values()) / len(monthly_counts)
            if monthly_counts
            else 0
        )

        return f"""📊 **Average Registration Rates:**

• **Daily Average**: {daily_avg:.1f} registrations/day
• **Monthly Average**: {monthly_avg:.1f} registrations/month

📈 **Peak Performance**:
• **Best day**: {max(daily_counts, key=daily_counts.get) if daily_counts else 'No data'} ({max(daily_counts.values()) if daily_counts else 0} registrations)
• **Best month**: {max(monthly_counts, key=monthly_counts.get) if monthly_counts else 'No data'} ({max(monthly_counts.values()) if monthly_counts else 0} registrations)"""

    # General data request
    if any(
        word in query_lower
        for word in ["data", "statistics", "stats", "summary", "overview"]
    ):
        total = stats.get("total_registrations", 0)
        pending = stats.get("pending_count", 0)
        completed = stats.get("completed_count", 0)

        # Top disposition
        disposition_counts = stats.get("disposition_counts", {})
        top_disposition = (
            max(disposition_counts, key=disposition_counts.get)
            if disposition_counts
            else "None"
        )

        # Top referral site
        referral_counts = stats.get("referral_site_counts", {})
        top_referral = (
            max(referral_counts, key=referral_counts.get)
            if referral_counts
            else "None"
        )

        return f"""📊 **Complete Registration Overview:**

**📈 Volume Statistics:**
• Total Registrations: {total}
• Pending Review: {pending}
• Completed: {completed}
• Completion Rate: {(completed/total*100):.1f}% 

**🏆 Top Categories:**
• Most Common Disposition: {top_disposition}
• Top Referral Source: {top_referral}
• Data Collection Period: {len(stats.get('monthly_counts', {}))} months

**📅 Recent Activity:**
• Days with registrations: {len(stats.get('daily_counts', {}))}
• Peak month: {max(stats.get('monthly_counts', {}), key=stats.get('monthly_counts', {}).get) if stats.get('monthly_counts') else 'No data'}

Need more specific analysis? Ask about dispositions, referral sites, trends, or any specific time period!"""

    # Default response for unrecognized queries
    return f"""I understand you're asking about: "{query}"

I specialize in analyzing registration data. Here's what I can help you with:

🔍 **Available Analysis:**
• Registration volumes and trends
• Disposition breakdowns and percentages  
• Referral site performance
• Physician assignments
• Geographic distribution
• Time-based patterns (daily/monthly/yearly)
• Completion rates and statistics

💡 **Try asking:**
• "Show me this month's registrations"
• "What are the most common dispositions?"
• "Which referral sites send the most patients?"
• "What's our completion rate?"
• "How many registrations today?"

What specific data would you like me to analyze?"""
