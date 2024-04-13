from email.message import EmailMessage
import ssl, smtplib


def send_email(email_reciever: str, body: str) -> None:
    email_sender = "coeptechhackathon20@gmail.com"
    email_password = "gbww hcgl unkn xotu"

    subject = "REGARDING FORGOT ACCESS TOKEN FROM BITBUSTERS"

    em = EmailMessage()
    em["From"] = email_sender
    em["To"] = email_reciever
    em["Subject"] = subject
    em.set_content(body)

    context = ssl.create_default_context()

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as smtp:
        smtp.login(email_sender, email_password)
        smtp.sendmail(email_sender, email_reciever, em.as_string())


send_email("abhishinde889@gmail.com", "Hello Loki!!")
