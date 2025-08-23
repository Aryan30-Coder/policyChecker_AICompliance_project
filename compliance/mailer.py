import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv

load_dotenv()  

def send_report_email(to_email, subject, body, attachment_path):
    """
    Send a compliance report via email with a TXT attachment.
    
    Args:
        to_email (str): Recipient email address.
        subject (str): Email subject line.
        body (str): Email body text.
        attachment_path (str): Path to the TXT report file.
    """

    from_email = os.getenv("EMAIL_USER")
    password = os.getenv("EMAIL_PASS")

    if not from_email or not password:
        raise ValueError("⚠️ EMAIL_USER or EMAIL_PASS not set in .env")


    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "plain"))


    if attachment_path and os.path.exists(attachment_path):
        with open(attachment_path, "rb") as attachment:
            mime_base = MIMEBase("application", "octet-stream")
            mime_base.set_payload(attachment.read())
        encoders.encode_base64(mime_base)
        mime_base.add_header("Content-Disposition", f"attachment; filename={os.path.basename(attachment_path)}")
        msg.attach(mime_base)


    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(from_email, password)
        server.send_message(msg)
        server.quit()
        print(f"📧 Report sent to {to_email}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
