import imapclient
import email
import os
import logging
import tempfile
import subprocess
import smtplib
import time
import re
from email.message import EmailMessage
from email.header import decode_header
from logging.handlers import RotatingFileHandler
import io

# Logging setup with rotation to prevent unbounded log growth
log_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger()
logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
logger.addHandler(console_handler)

# Rotate logs at 5MB, keep 3 backup files
file_handler = RotatingFileHandler("email2print.log", maxBytes=5*1024*1024, backupCount=3)
file_handler.setFormatter(log_formatter)
logger.addHandler(file_handler)


# Helper to get env variables
def get_env_var(name, required=False, default=None):
    val = os.getenv(name)
    if val is None or val == "":
        if required:
            logger.error(f"Missing required environment variable: {name}")
            raise ValueError(f"Missing required environment variable: {name}")
        return default
    return val

# Environment Configuration
EMAIL_ACCOUNT = get_env_var("EMAIL_ACCOUNT", required=True)
EMAIL_PASSWORD = get_env_var("EMAIL_PASSWORD", required=True)

SMTP_USERNAME = get_env_var("SMTP_USERNAME", default=EMAIL_ACCOUNT)
SMTP_PASSWORD = get_env_var("SMTP_PASSWORD", default=EMAIL_PASSWORD)
FROM_ADDRESS   = get_env_var("FROM_ADDRESS", default=EMAIL_ACCOUNT)

SMTP_SERVER = get_env_var("SMTP_SERVER", required=True)
SMTP_PORT = int(get_env_var("SMTP_PORT", required=True))

IMAP_SERVER = get_env_var("IMAP_SERVER", required=True)
IMAP_PORT = int(get_env_var("IMAP_PORT", default=993))

PRINTER_NAME = get_env_var("PRINTER_NAME", required=True)

SLEEP_TIME = int(get_env_var("SLEEP_TIME", default=60))
CONFIRM_SUBJECT = get_env_var("CONFIRM_SUBJECT", default="Your Print Job Confirmation")
ALLOWED_ATTACHMENT_TYPES = [ext.strip().lower() for ext in get_env_var("ALLOWED_ATTACHMENT_TYPES", default="").split(",") if ext]
ALLOWED_RECIPIENTS = [addr.strip().lower() for addr in get_env_var("ALLOWED_RECIPIENTS", default="").split(",") if addr]
DETAILED_CONFIRMATION = get_env_var("DETAILED_CONFIRMATION", default="false").lower() == "true"
DELETE_AFTER_PRINT = get_env_var("DELETE_AFTER_PRINT", default="false").lower() == "true"

# Security: Max file size limit (in MB) to prevent resource exhaustion attacks
MAX_FILE_SIZE_MB = int(get_env_var("MAX_FILE_SIZE_MB", default=10))
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

# Connection retry settings for IMAP resilience
MAX_IMAP_RETRIES = int(get_env_var("MAX_IMAP_RETRIES", default=3))
IMAP_RETRY_DELAY = int(get_env_var("IMAP_RETRY_DELAY", default=5))


def decode_mime_words(s):
    if not s:
        return ""
    return ''.join(
        part.decode(enc or 'utf-8') if isinstance(part, bytes) else part
        for part, enc in decode_header(s)
    )

def is_mostly_html_blank(html):
    cleaned = re.sub(r"<[^>]+>", "", html or "").strip()
    return cleaned == ""

def print_file(file_path):
    try:
        subprocess.run(["lp", "-d", PRINTER_NAME, file_path], check=True)
        logger.info(f"Sent to printer: {PRINTER_NAME} - File: {file_path}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Printing failed for {file_path}: {e}")
        return False

def send_confirmation_email(to_email, log_text, printed_files):
    msg = EmailMessage()
    msg["Subject"] = CONFIRM_SUBJECT
    msg["From"] = FROM_ADDRESS
    msg["To"] = to_email

    if DETAILED_CONFIRMATION:
        msg.set_content(f"Your print job was processed:\n\n{log_text}")
    else:
        lines = [
            f"{time.strftime('%Y-%m-%d %H:%M:%S')} – Your file '{fname}' was printed on printer '{PRINTER_NAME}'"
            for fname in printed_files
        ]
        msg.set_content("\n".join(lines) if lines else "No files were printed.")

    try:
        logger.info(f"Sending confirmation email to {to_email}")
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=20) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        logger.info("Confirmation email sent.")
    except Exception as e:
        logger.error(f"Error sending confirmation email: {e}")

def extract_sender(msg):
    """Extract and normalize sender email address"""
    return email.utils.parseaddr(msg.get("From"))[1].lower()

def is_sender_allowed(from_addr):
    """
    Check if sender is allowed based on ALLOWED_RECIPIENTS list.
    Supports individual emails and domain wildcards (@domain.com).
    If list is empty, denies all (security by default).
    """
    if not ALLOWED_RECIPIENTS:
        logger.warning(f"ALLOWED_RECIPIENTS is empty. Denying sender: {from_addr}")
        return False
    
    # Check for exact email match
    if from_addr in ALLOWED_RECIPIENTS:
        return True
    
    # Check for domain wildcard match (@domain.com)
    sender_domain = "@" + from_addr.split("@")[-1]
    if sender_domain in ALLOWED_RECIPIENTS:
        return True
    
    return False

def print_content(payload, suffix, description):
    """
    Unified function to handle temp file creation, printing, and cleanup.
    Reduces code duplication across attachments and email body processing.
    
    Returns: (success: bool, temp_file_path: str)
    """
    # Security: Check payload size before processing
    if len(payload) > MAX_FILE_SIZE_BYTES:
        logger.warning(f"{description} exceeds max size ({MAX_FILE_SIZE_MB}MB). Skipping.")
        return False, None
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{suffix}") as tmpfile:
        tmpfile.write(payload)
        tmpfile_path = tmpfile.name
    
    logger.info(f"Printing {description}: {tmpfile_path}")
    success = print_file(tmpfile_path)
    
    # Always clean up temp file
    try:
        os.remove(tmpfile_path)
        logger.info(f"Deleted temporary file: {tmpfile_path}")
    except Exception as e:
        logger.error(f"Failed to delete temp file {tmpfile_path}: {e}")
    
    return success, tmpfile_path

def process_email(msg):
    """Process a single email message: validate sender, print content, send confirmation"""
    from_addr = extract_sender(msg)
    subject = decode_mime_words(msg.get("Subject", "(No Subject)"))
    
    # Security: Validate sender BEFORE processing any content
    if not is_sender_allowed(from_addr):
        logger.warning(f"Sender {from_addr} not in ALLOWED_RECIPIENTS (nor domain match). Skipping print.")
        return

    printed_files = []

    log_stream = io.StringIO()
    stream_handler = logging.StreamHandler(log_stream)
    stream_handler.setFormatter(log_formatter)
    logger.addHandler(stream_handler)

    logger.info(f"Processing email from: {from_addr}")
    logger.info(f"Subject: {subject}")
    printed_any = False

    # Detect if there are attachments
    # This is to prevent printing the email body if not really needed
    has_valid_attachments = False
    for part in msg.walk():
        if part.get_content_maintype() == 'multipart': 
            continue
        if part.get_filename():  # Has filename
            fname = decode_mime_words(part.get_filename())
            ext = os.path.splitext(fname)[1].lower().lstrip(".")
            # Check if extension is allowed
            if not ALLOWED_ATTACHMENT_TYPES or ext in ALLOWED_ATTACHMENT_TYPES:
                has_valid_attachments = True
                break
    
    if has_valid_attachments:
        logger.info("Valid attachments found. Email body will be SKIPPED.")

    for part in msg.walk():
        content_type = part.get_content_type()
        filename = part.get_filename()
        payload = part.get_payload(decode=True)

        # Skip empty payloads early
        if not payload or payload.strip() == b"":
            logger.warning(f"{'Attachment' if filename else 'Email body'} ({content_type}) is empty. Skipping print.")
            continue

        if filename:
            filename = decode_mime_words(filename)
            suffix = os.path.splitext(filename)[1].lower().lstrip(".")

            if ALLOWED_ATTACHMENT_TYPES and suffix not in ALLOWED_ATTACHMENT_TYPES:
                logger.warning(f"Attachment '{filename}' type .{suffix} not allowed. Skipping.")
                continue

            # Use unified print function
            success, _ = print_content(payload, suffix, f"attachment '{filename}'")
            if success:
                printed_any = True
                printed_files.append(filename)

        elif content_type in ["text/plain", "text/html"]:
            # Prevent printing body if the email has attachments
            if has_valid_attachments:
                continue
            
            if content_type == "text/html" and is_mostly_html_blank(payload.decode(errors="ignore")):
                logger.warning(f"HTML email body is blank after stripping tags. Skipping.")
                continue

            # Use unified print function
            success, _ = print_content(payload, "txt", f"email body ({content_type})")
            if success:
                printed_any = True
                printed_files.append(f"EmailBody-{content_type}")

    if not printed_any:
        logger.warning("No printable content found in this email.")

    stream_handler.flush()
    logger.removeHandler(stream_handler)
    send_confirmation_email(from_addr, log_stream.getvalue(), printed_files)
    log_stream.close()

def connect_imap_with_retry():
    """
    Establish IMAP connection with retry logic for resilience.
    Returns: IMAPClient instance or raises exception after max retries.
    """
    for attempt in range(MAX_IMAP_RETRIES):
        try:
            logger.info(f"Connecting to IMAP server (attempt {attempt + 1}/{MAX_IMAP_RETRIES})")
            client = imapclient.IMAPClient(IMAP_SERVER, ssl=True, port=IMAP_PORT)
            client.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
            logger.info("IMAP connection established successfully")
            return client
        except Exception as e:
            logger.error(f"IMAP connection attempt {attempt + 1} failed: {e}")
            if attempt == MAX_IMAP_RETRIES - 1:
                logger.error("Max IMAP connection retries reached. Raising exception.")
                raise
            # Exponential backoff
            delay = IMAP_RETRY_DELAY * (attempt + 1)
            logger.info(f"Retrying in {delay} seconds...")
            time.sleep(delay)

def main_loop():
    """Main processing loop with error handling and reconnection logic"""
    logger.info("Starting email2print script")
    
    while True:
        try:
            # Establish connection with retry logic
            with connect_imap_with_retry() as client:
                client.select_folder("INBOX")
                messages = client.search(["UNSEEN"])
                logger.info(f"Found {len(messages)} unseen messages")

                if messages:
                    for uid, msg_data in client.fetch(messages, "RFC822").items():
                        raw_email = msg_data[b"RFC822"]
                        msg = email.message_from_bytes(raw_email)
                        process_email(msg)
                        
                        # Mark as seen or deletion
                        if DELETE_AFTER_PRINT:
                            client.delete_messages(uid)
                            logger.info(f"Email {uid} marked for deletion.")
                        else:
                            client.add_flags(uid, [b"\\Seen"])
                    
                    # Delete (expunge) marked mails
                    if DELETE_AFTER_PRINT:
                        client.expunge()
                        logger.info("Deleted messages expunged from server.")
                else:
                    logger.info("No new messages.")
                    
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}", exc_info=True)
            # Continue running even after errors

        logger.info(f"Sleeping {SLEEP_TIME}s...")
        time.sleep(SLEEP_TIME)

if __name__ == "__main__":
    print(f"Monitoring inbox: {EMAIL_ACCOUNT}")
    print(f"Printing to printer: {PRINTER_NAME}")
    print(f"Scan interval: {SLEEP_TIME} seconds")
    print(f"Max file size: {MAX_FILE_SIZE_MB} MB")
    logger.info(f"Starting email2print with inbox: {EMAIL_ACCOUNT}, printer: {PRINTER_NAME}, scan interval: {SLEEP_TIME}s, max file size: {MAX_FILE_SIZE_MB}MB")
    main_loop()
