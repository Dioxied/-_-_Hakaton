import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email(subject, message, recipient):
    smtp_server   = os.getenv("SMTP_SERVER", "example.com") #Адрес SMTP-сервера, предоставляемого вашим почтовым провайдером
    smtp_port     = int(os.getenv("SMTP_PORT", 587)) #Порт
    smtp_user     = os.getenv("SMTP_USER", "your_email@example.com") #Почта, с которой отправлется сообщение
    smtp_password = os.getenv("SMTP_PASSWORD", "your_password") #Пароль к почте

    msg = MIMEMultipart()
    msg["From"] = smtp_user
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.attach(MIMEText(message, "plain"))

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
            print(f"Email sent to {recipient}")
    except Exception as e:
        print(f"Error sending email to {recipient}: {e}")
