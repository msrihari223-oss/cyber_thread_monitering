import os
import smtplib
from email.message import EmailMessage

try:
    # optional dependency to load .env files for local dev
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    # dotenv is optional; if not present, environment variables will be used
    pass


DEFAULT_SMTP_SENDER = "vu.cse.241fa04677@gmail.com"
DEFAULT_SMTP_APP_PASSWORD = "bhrs ligq hclp nobj"
DEFAULT_REPORT_RECEIVER = os.environ.get("REPORT_RECEIVER_EMAIL", DEFAULT_SMTP_SENDER)


def _get_smtp_credentials():
    sender = os.environ.get("SMTP_SENDER_EMAIL", DEFAULT_SMTP_SENDER)
    app_password = os.environ.get("SMTP_APP_PASSWORD", DEFAULT_SMTP_APP_PASSWORD)
    if not sender or not app_password:
        raise RuntimeError("SMTP credentials not configured. Set SMTP_SENDER_EMAIL and SMTP_APP_PASSWORD environment variables (or provide a .env file).")
    return sender, app_password


def send_email(receiver: str, subject: str, body: str):
    from email.mime.text import MIMEText
    import datetime
    
    sender_email = "vu.cse.241fa04677@gmail.com"
    sender_password = "bhrs ligq hclp nobj"

    # ALWAYS write to a local mail_log.txt file so developer can inspect emails instantly!
    try:
        log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mail_log.txt")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write("="*60 + "\n")
            f.write(f"TIMESTAMP: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"FROM: {sender_email}\n")
            f.write(f"TO: {receiver}\n")
            f.write(f"SUBJECT: {subject}\n")
            f.write("-" * 60 + "\n")
            f.write(body + "\n")
            f.write("="*60 + "\n\n")
        print(f"[Email Service] Appended email details to local log: {log_path}")
    except Exception as log_err:
        print(f"[Email Service] Failed to write email to log file: {repr(log_err)}")

    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = sender_email
        msg["To"] = receiver

        server = smtplib.SMTP("smtp.gmail.com", 587, timeout=10)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver, msg.as_string())
        server.quit()
        print(f"[Email Service] SMTP email successfully sent to {receiver}")
        return True
    except Exception as smtp_err:
        print(f"[Email Service] SMTP send failed to {receiver}: {repr(smtp_err)}")
        return False


def send_otp_email(receiver_email: str, otp: str):
    from email.mime.text import MIMEText
    import datetime
    
    sender_email = "vu.cse.241fa04677@gmail.com"
    sender_password = "bhrs ligq hclp nobj"
    
    subject = "OTP Verification"
    body = f"Your OTP is: {otp}"
    
    # ALWAYS write to persistent local mail_log.txt first so developer can inspect OTPs instantly!
    try:
        log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mail_log.txt")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write("="*60 + "\n")
            f.write(f"TIMESTAMP: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"FROM: {sender_email}\n")
            f.write(f"TO: {receiver_email}\n")
            f.write(f"SUBJECT: {subject}\n")
            f.write("-" * 60 + "\n")
            f.write(body + "\n")
            f.write("="*60 + "\n\n")
        print(f"[Email Service] Appended OTP email details to local log: {log_path}")
    except Exception as log_err:
        print(f"[Email Service] Failed to write email details to local log: {repr(log_err)}")
        
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = sender_email
        msg["To"] = receiver_email
        
        server = smtplib.SMTP("smtp.gmail.com", 587, timeout=10)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        print(f"[Email Service] SMTP email successfully sent to {receiver_email}")
        return True
    except Exception as e:
        print(f"[Email Service] SMTP send failed to {receiver_email}: {repr(e)}")
        return False


def send_spam_report_email(user_email: str, score: float, level: str, comment: str):
    subject = f"Spam Report: {user_email}"
    body = (
        f"A user has been flagged for spam or abusive content.\n\n"
        f"User Email: {user_email}\n"
        f"Threat Level: {level}\n"
        f"Toxicity Score: {score:.4f}\n\n"
        f"Comment:\n{comment}\n\n"
        f"This user account has been blocked from signing in and should be reviewed."
    )
    send_email(DEFAULT_REPORT_RECEIVER, subject, body)


def send_warning_email_to_user(user_email: str, warnings_count: int, comment: str, is_blocked: bool):
    if is_blocked:
        subject = "Account Suspended: CyberWatch Community Guidelines Violation"
        body = (
            f"Dear User,\n\n"
            f"Your CyberWatch account associated with {user_email} has been permanently blocked.\n"
            f"This action was taken due to repeated violations of our community guidelines (abusive language, spam, or cyber threats).\n\n"
            f"Recent violation details:\n"
            f"- Content: \"{comment}\"\n"
            f"- Warning status: 3 of 3 (Permanent Block)\n\n"
            f"If you believe this was an error, please contact support."
        )
    else:
        subject = f"Community Guidelines Warning ({warnings_count}/3)"
        body = (
            f"Dear User,\n\n"
            f"This is warning {warnings_count} of 3 for your account {user_email}.\n"
            f"We detected highly inappropriate or toxic language in your comment:\n"
            f"\"{comment}\"\n\n"
            f"Please review our community guidelines. Posting abusive content, cyber threats, or offensive language is strictly prohibited.\n"
            f"Please note that receiving 3 warnings will result in the permanent suspension of your account."
        )
    send_email(user_email, subject, body)


def send_otp_sms(phone: str, otp: str):
    import urllib.request
    import urllib.parse
    import re
    import datetime
    
    if not phone:
        print("[SMS Service] No phone number provided to send OTP.")
        return False
        
    # Clean phone number (keep only digits)
    clean_phone = re.sub(r'\D', '', phone)
    
    # If it starts with 91 and has 12 digits, strip 91 so it is a standard 10-digit Indian number for Fast2SMS
    if len(clean_phone) == 12 and clean_phone.startswith('91'):
        clean_phone = clean_phone[2:]
        
    print(f"[SMS Service] Dispatching secure OTP {otp} via SMS to mobile number: {clean_phone}")
    
    # ALWAYS write to persistent local mail_log.txt first so developer can inspect OTPs instantly!
    try:
        log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mail_log.txt")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write("="*60 + "\n")
            f.write(f"TIMESTAMP: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"SMS SENT TO: {phone} ({clean_phone})\n")
            f.write(f"MESSAGE: Secure OTP is: {otp}\n")
            f.write("="*60 + "\n\n")
        print(f"[SMS Service] Appended SMS OTP details to local log: {log_path}")
    except Exception as log_err:
        print(f"[SMS Service] Failed to write SMS details to local log: {repr(log_err)}")

    # Fast2SMS URL parameters using client API Key
    api_key = "a58ece8c7da34952ca516b0c3cdab287"
    url = f"https://www.fast2sms.com/dev/bulkV2?authorization={urllib.parse.quote(api_key)}&route=otp&variables_values={urllib.parse.quote(otp)}&numbers={urllib.parse.quote(clean_phone)}"
    
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'Mozilla/5.0'}
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            res_body = response.read().decode('utf-8')
            print(f"[SMS Service] Fast2SMS Response: {res_body}")
            return True
    except Exception as e:
        print(f"[SMS Service] Failed to send SMS via Fast2SMS: {repr(e)}")
        
        # Fallback to Textbelt
        try:
            print("[SMS Service] Attempting Textbelt free tier fallback...")
            post_data = urllib.parse.urlencode({
                'phone': phone if phone.startswith('+') else f'+91{clean_phone}',
                'message': f'Your secure CyberWatch verification OTP is: {otp}. Valid for 2 minutes.',
                'key': 'free'
            }).encode('utf-8')
            
            req = urllib.request.Request(
                'https://textbelt.com/text',
                data=post_data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                res_body = response.read().decode('utf-8')
                print(f"[SMS Service] Textbelt Response: {res_body}")
                return True
        except Exception as textbelt_err:
            print(f"[SMS Service] Textbelt fallback failed: {repr(textbelt_err)}")
            
    return False