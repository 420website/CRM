import mimetypes
import os
import smtplib
from email.message import EmailMessage
from typing import Self, overload
from app.common.config import settings
from app.core.objects.object_queries import ObjectService


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

    async def attach(self, bucket: str, file_key: str) -> Self:
        # Fetch file bytes from your object storage
        file_bytes = await ObjectService.get_object(bucket, file_key)

        # Guess MIME type (fallback to binary)
        mime_type, _ = mimetypes.guess_type(file_key)
        mime_type = mime_type or "application/octet-stream"
        maintype, subtype = mime_type.split("/", 1)

        # Extract filename from key
        filename = os.path.basename(file_key)

        # Attach file bytes to email
        self.msg.add_attachment(
            file_bytes,
            maintype=maintype,
            subtype=subtype,
            filename=filename,
        )

        return self

    def send(self):
        with smtplib.SMTP(settings.email_provider, 587) as smtp:
            smtp.starttls()
            smtp.login(settings.email, settings.email_pw)
            smtp.send_message(self.msg)

    def send_ssl(self):
        with smtplib.SMTP_SSL(settings.email_provider, 465) as smtp:
            smtp.login(settings.email, settings.email_pw)
            smtp.send_message(self.msg)
