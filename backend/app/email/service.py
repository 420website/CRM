import smtplib
from email.message import EmailMessage
from typing import Self, overload
from app.config import settings


class Message:
    def __init__(self) -> None:
        self.msg = ""

    def greeting(self, text: str) -> Self:
        self.msg += text + "\n\n"
        return self

    def body(self, text: str) -> Self:
        self.msg += text + "\n\n"
        return self

    def salutation(self, text: str) -> Self:
        self.msg += text + "\n"
        return self


class PlainMessage(Message):
    def __init__(self) -> None:
        super().__init__()


class HtmlMessage(Message):
    def __init__(self) -> None:
        super().__init__()


class EmailService:
    def __init__(self):
        self.msg = EmailMessage()
        self.msg["From"] = settings.email

    def recipient(self, email: str) -> Self:
        self.msg["To"] = email
        return self

    def subject(self, subject: str) -> Self:
        self.msg["Subject"] = subject
        return self

    @overload
    def body(self, body: HtmlMessage) -> Self: ...

    @overload
    def body(self, body: PlainMessage) -> Self: ...

    def body(self, body: Message) -> Self:
        if isinstance(body, HtmlMessage):
            self.msg.set_content(body.msg, "html")
        else:
            self.msg.set_content(body.msg)
        return self

    def send(self):
        with smtplib.SMTP_SSL("mail.privateemail.com", 465) as smtp:
            smtp.login(settings.email, settings.email_pw)
            smtp.send_message(self.msg)
