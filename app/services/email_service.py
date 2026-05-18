from fastapi_mail import MessageSchema
from app.config.mail import fastmail
from jinja2 import Template


async def send_otp_email(email: str, otp: str):
    with open("app/templates/otp_email.html", "r") as f:
        template = Template(f.read())

    html = template.render(otp=otp)

    message = MessageSchema(
        subject="Expense Tracker App - OTP Verification",
        recipients=[email],
        body=html,
        subtype="html"
    )

    await fastmail.send_message(message)