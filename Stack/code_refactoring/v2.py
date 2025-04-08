import email
import smtplib
import imaplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional


class EmailClient:
    def __init__(self,
                 smtp_server: str,
                 imap_server: str,
                 login: str,
                 password: str):
        self.smtp_server = smtp_server
        self.imap_server = imap_server
        self.login = login
        self.password = password

    def send_email(self,
                   recipients: List[str],
                   subject: str,
                   message: str) -> None:
        msg = MIMEMultipart()
        msg['From'] = self.login
        msg['To'] = ', '.join(recipients)
        msg['Subject'] = subject
        msg.attach(MIMEText(message))

        with smtplib.SMTP(self.smtp_server, 587) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(self.login, self.password)
            server.sendmail(self.login, recipients, msg.as_string())

    def receive_email(self, header: Optional[str] = None) -> Optional[str]:
        with imaplib.IMAP4_SSL(self.imap_server) as mail:
            mail.login(self.login, self.password)
            mail.select("inbox")
            criterion = f'(HEADER Subject "{header}")' if header else 'ALL'
            result, data = mail.uid('search', None, criterion)

            if not data[0]:
                print("Нет писем с указанной темой.")
                return None

            latest_email_uid = data[0].split()[-1]
            result, data = mail.uid('fetch', latest_email_uid, '(RFC822)')
            raw_email = data[0][1]
            email_message = email.message_from_bytes(raw_email)
            return email_message.as_string()


if __name__ == '__main__':
    GMAIL_SMTP = "smtp.gmail.com"
    GMAIL_IMAP = "imap.gmail.com"
    LOGIN = 'your_login@gmail.com'
    PASSWORD = 'your_password'
    RECIPIENTS = ['recipient@email.com']
    SUBJECT = 'Test Email'
    MESSAGE = 'This is a test email from Python.'
    HEADER = 'Test Email'

    email_client = EmailClient(GMAIL_SMTP, GMAIL_IMAP, LOGIN, PASSWORD)

    try:
        email_client.send_email(RECIPIENTS, SUBJECT, MESSAGE)
        print("Письмо отправлено успешно!")
    except Exception as e:
        print(f"Ошибка при отправке письма: {e}")

    try:
        received_email = email_client.receive_email(HEADER)
        if received_email:
            print("Полученное письмо:")
            print(received_email)
    except Exception as e:
        print(f"Ошибка при получении письма: {e}")