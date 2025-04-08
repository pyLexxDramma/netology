import email
import smtplib
import imaplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailClient:
    def __init__(self, smtp_server, imap_server, email_address, password):
        self.smtp_server = smtp_server
        self.imap_server = imap_server
        self.email_address = email_address
        self.password = password

    def send_email(self, subject, recipients, message):
        msg = MIMEMultipart()
        msg['From'] = self.email_address
        msg['To'] = ', '.join(recipients)
        msg['Subject'] = subject
        msg.attach(MIMEText(message))

        with smtplib.SMTP(self.smtp_server, 587) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            smtp.login(self.email_address, self.password)
            smtp.sendmail(self.email_address, recipients, msg.as_string())

    def receive_email(self, header=None):
        with imaplib.IMAP4_SSL(self.imap_server) as mail:
            mail.login(self.email_address, self.password)
            mail.select("inbox")
            criterion = '(HEADER Subject "%s")' % header if header else 'ALL'
            result, data = mail.uid('search', None, criterion)
            if not data[0]:
                raise Exception('There are no letters with the current header')
            latest_email_uid = data[0].split()[-1]
            result, data = mail.uid('fetch', latest_email_uid, '(RFC822)')
            raw_email = data[0][1]
            return email.message_from_bytes(raw_email)

if __name__ == '__main__':
    GMAIL_SMTP = "smtp.gmail.com"
    GMAIL_IMAP = "imap.gmail.com"
    LOGIN = 'login@gmail.com'
    PASSWORD = 'qwerty'

    email_client = EmailClient(GMAIL_SMTP, GMAIL_IMAP, LOGIN, PASSWORD)

    subject = 'Subject'
    recipients = ['vasya@email.com', 'petya@email.com']
    message = 'Message'
    email_client.send_email(subject, recipients, message)

    try:
        email_message = email_client.receive_email(header=None)
        print("Received email:", email_message)
    except Exception as e:
        print(e)
