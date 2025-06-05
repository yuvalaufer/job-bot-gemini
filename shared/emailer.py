import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def send_email(subject, body):
    """
    Sends an email report with the scraping results.
    Email credentials are pulled from environment variables for security.
    """
    sender_email = os.getenv("EMAIL_SENDER")
    sender_password = os.getenv("EMAIL_PASSWORD")
    recipient_email = os.getenv("EMAIL_RECIPIENT")
    smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", 587))

    if not all([sender_email, sender_password, recipient_email]):
        print("Error: Email credentials (EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECIPIENT) are not fully set in environment variables. Cannot send email.")
        return

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain', 'utf-8')) # Ensure UTF-8 for Hebrew support

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Secure the connection using TLS
            server.login(sender_email, sender_password)
            server.send_message(msg)
        print(f"Email report sent successfully to {recipient_email}")
    except Exception as e:
        print(f"Failed to send email report to {recipient_email}. Error: {e}")
