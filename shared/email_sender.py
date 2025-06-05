import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def send_email(recipients, subject, body_html):
    """
    Sends an email notification with job postings.

    Args:
        recipients (list): A list of email addresses to send the email to.
        subject (str): The subject line of the email.
        body_html (str): The HTML content of the email body.
    """
    # Use environment variables for sensitive information (email credentials)
    # RENDER_EMAIL_USER and RENDER_EMAIL_PASS should be set in Render environment variables
    sender_email = os.environ.get("RENDER_EMAIL_USER")
    sender_password = os.environ.get("RENDER_EMAIL_PASS")
    smtp_server = "smtp.gmail.com" # For Gmail. Change if using a different provider.
    smtp_port = 587 # For TLS

    if not sender_email or not sender_password:
        logging.error("Email credentials (RENDER_EMAIL_USER, RENDER_EMAIL_PASS) are not set as environment variables. Email will not be sent.")
        raise ValueError("Email credentials missing. Please set RENDER_EMAIL_USER and RENDER_EMAIL_PASS.")

    msg = MIMEMultipart("alternative")
    msg["From"] = sender_email
    msg["To"] = ", ".join(recipients)
    msg["Subject"] = subject

    # Attach HTML part
    part = MIMEText(body_html, "html")
    msg.attach(part)

    try:
        logging.info(f"Attempting to send email to {', '.join(recipients)}...")
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Secure the connection
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, recipients, msg.as_string())
        logging.info("Email sent successfully!")
    except smtplib.SMTPAuthenticationError as e:
        logging.error(f"SMTP Authentication Error: Check your email username and password (or App Password for Gmail). Error: {e}")
        logging.error("If using Gmail, ensure 'Less secure app access' is ON (deprecated) or use an App Password.")
        raise
    except smtplib.SMTPException as e:
        logging.error(f"SMTP Error: Could not send email. Error: {e}", exc_info=True)
        raise
    except Exception as e:
        logging.error(f"An unexpected error occurred while sending email: {e}", exc_info=True)
        raise

# This part is typically for local testing, not used by Flask/Render directly
if __name__ == '__main__':
    logging.info("Running email sender manually (for testing purposes).")
    # --- For local testing, temporarily hardcode credentials or load from .env ---
    # os.environ["RENDER_EMAIL_USER"] = "your_test_email@gmail.com"
    # os.environ["RENDER_EMAIL_PASS"] = "your_test_app_password"
    # --- Remember to remove or comment out for production deployment ---

    try:
        test_recipients = ["your_email@example.com"] # CHANGE THIS TO YOUR ACTUAL EMAIL FOR TESTING
        test_subject = "Test Job Bot Email"
        test_body = "<h1>Hello from Job Bot!</h1><p>This is a test email.</p><p>If you received this, email sending is working!</p>"
        send_email(test_recipients, test_subject, test_body)
    except Exception as e:
        logging.error(f"Test email failed: {e}")
