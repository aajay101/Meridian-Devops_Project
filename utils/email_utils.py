import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from flask import current_app

from utils.validators import is_valid_email

logger = logging.getLogger(__name__)


def _get_smtp_config():
    return {
        "server": current_app.config.get("MAIL_SERVER", ""),
        "port": int(current_app.config.get("MAIL_PORT", 587)),
        "username": current_app.config.get("MAIL_USERNAME", ""),
        "password": current_app.config.get("MAIL_PASSWORD", ""),
        "use_tls": current_app.config.get("MAIL_USE_TLS", True),
    }


def _create_smtp_connection(config):
    server = smtplib.SMTP(config["server"], config["port"], timeout=30)
    if config["use_tls"]:
        server.starttls()
    if config["username"] and config["password"]:
        server.login(config["username"], config["password"])
    return server


def _build_message(to, subject, from_addr, html_body=None, text_body=None):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = to

    if text_body and html_body:
        msg.attach(MIMEText(text_body, "plain"))
        msg.attach(MIMEText(html_body, "html"))
    elif html_body:
        msg.attach(MIMEText(html_body, "html"))
    elif text_body:
        msg.attach(MIMEText(text_body, "plain"))

    return msg


def _send_via_smtp(msg, config):
    with _create_smtp_connection(config) as server:
        server.sendmail(msg["From"], [msg["To"]], msg.as_string())


def send_email(to, subject, html_body=None, text_body=None):
    if not to or not isinstance(to, str):
        logger.warning("send_email called with invalid recipient")
        return False

    if not is_valid_email(to):
        logger.warning("send_email called with invalid email format: %s", to)
        return False

    if not html_body and not text_body:
        logger.warning("send_email called with no body content")
        return False

    try:
        config = _get_smtp_config()
    except RuntimeError:
        logger.warning("No Flask application context - cannot read config")
        return False

    if not config["server"]:
        logger.warning("MAIL_SERVER not configured - skipping email send")
        return False

    from_addr = config["username"] or "no-reply@placement.local"
    msg = _build_message(to, subject, from_addr, html_body, text_body)

    try:
        _send_via_smtp(msg, config)
        logger.info("Email sent successfully to %s", to)
        return True
    except smtplib.SMTPException as e:
        logger.error("SMTP error sending email to %s: %s", to, e)
        return False
    except Exception as e:
        logger.error("Unexpected error sending email to %s: %s", to, e)
        return False


def build_reminder_email(student_name, company_name, job_title, deadline_str):
    subject = f"Reminder: {job_title} at {company_name} — Deadline {deadline_str}"
    html_body = (
        f"<p>Hi {student_name},</p>"
        f"<p>This is a reminder that the application deadline for "
        f"<strong>{job_title}</strong> at <strong>{company_name}</strong> "
        f"is approaching on <strong>{deadline_str}</strong>.</p>"
        f"<p>Please submit your application before the deadline.</p>"
        f"<p>Good luck!</p>"
    )
    return subject, html_body


def send_bulk_emails(messages):
    if not messages:
        return {"sent": 0, "failed": 0}

    try:
        config = _get_smtp_config()
    except RuntimeError:
        logger.warning("No Flask application context - cannot read config")
        return {"sent": 0, "failed": len(messages)}

    if not config["server"]:
        logger.warning("MAIL_SERVER not configured - skipping bulk email send")
        return {"sent": 0, "failed": len(messages)}

    from_addr = config["username"] or "no-reply@placement.local"
    sent = 0
    failed = 0

    try:
        with _create_smtp_connection(config) as server:
            for message in messages:
                to = message[0]
                subject = message[1]
                html_body = message[2] if len(message) > 2 else None
                text_body = message[3] if len(message) > 3 else None

                if not to or not isinstance(to, str):
                    logger.warning("Skipping invalid recipient in bulk send")
                    failed += 1
                    continue

                if not is_valid_email(to):
                    logger.warning("Skipping invalid email format in bulk send: %s", to)
                    failed += 1
                    continue

                msg = _build_message(to, subject, from_addr, html_body, text_body)
                try:
                    server.sendmail(from_addr, [to], msg.as_string())
                    sent += 1
                except smtplib.SMTPException as e:
                    logger.error("SMTP error sending to %s: %s", to, e)
                    failed += 1
                except Exception as e:
                    logger.error("Unexpected error sending to %s: %s", to, e)
                    failed += 1
    except smtplib.SMTPException as e:
        logger.error("Failed to connect to SMTP server: %s", e)
        return {"sent": 0, "failed": len(messages)}
    except Exception as e:
        logger.error("Unexpected error connecting to SMTP server: %s", e)
        return {"sent": 0, "failed": len(messages)}

    logger.info("Bulk email complete: %d sent, %d failed", sent, failed)
    return {"sent": sent, "failed": failed}
