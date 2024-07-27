from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from fastapi import Depends, Request
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import EmailStr
from jose import jwt

from config.auth_config import ALGORITHM, oauth2_bearer, bcrypt_context
from config.parser import load_config
import random
import smtplib
import uuid
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

smtp_config = load_config().smtp_config
verification_storage = dict()


async def get_session() -> AsyncSession:
    raise NotImplementedError("Please overwrite get_session dependency.")


def generate_session_id():
    return str(uuid.uuid4())


def is_valid_update(field_value, original_value):
    return field_value is not None and field_value != '' and field_value != original_value


def db_model_to_dict(model_instance) -> dict:
    return {column.name: getattr(model_instance, column.name) for column in model_instance.__table__.columns}


def dict_to_db_model(model_class, data: dict):
    instance = model_class()
    for key, value in data.items():
        setattr(instance, key, value)
    return instance


def convert_str_to_int_if_numeric(value: str):
    try:
        return int(value)
    except ValueError:
        return value


async def get_optional_token(request: Request):
    authorization: str = request.headers.get("Authorization")
    if not authorization:
        return None
    return await oauth2_bearer(request)


async def get_current_user(user_token: Optional[str] = Depends(get_optional_token)) -> Optional[dict]:
    if user_token is None:
        return None
    try:
        auth_config = load_config().auth_config
        payload = jwt.decode(user_token, auth_config.secret_key, algorithms=[ALGORITHM])
        email: EmailStr = payload.get("email")
        user_id: UUID = payload.get("id")

        if email is None or user_id is None:
            return None
        return {"email": email, "id": user_id}

    except JWTError:
        return None


def generate_random_verification_code() -> str:
    verification_code = ''.join(random.choices('0123456789', k=6))
    return verification_code


def hash_password(password: str) -> str:
    return bcrypt_context.hash(password)


async def verify_code(email: EmailStr, code):
    if email not in verification_storage:
        return False, "Invalid email or verification code"

    if verification_storage[email]['code'] != code:
        return False, "Invalid verification code"

    if datetime.now() - verification_storage[email]['timestamp'] > timedelta(
            minutes=smtp_config.verification_code_expiration_minutes):
        return False, "Verification code expired"
    else:
        return True, "Account successfully verified!"


async def send_email_via_smtp(user_email: EmailStr, message: MIMEMultipart):
    # SMTP server settings
    smtp_server = smtp_config.smtp_server
    smtp_port = smtp_config.smtp_port

    # SMTP credentials
    smtp_username = smtp_config.smtp_username
    smtp_password = smtp_config.smtp_password

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()

        if smtp_username and smtp_password:
            server.login(smtp_username, smtp_password)

        # send email
        server.sendmail(smtp_config.sender_email, user_email, message.as_string())
    except Exception as e:
        print(f"Failed to send email. Error: {e}")

    finally:
        print("Email sent successfully!")
        server.quit()


async def send_verification_email(first_name: str, user_email: EmailStr):
    subject = smtp_config.verification_email_subject
    verification_code = generate_random_verification_code()
    body = f"Hey {first_name}! \n \n " + smtp_config.verification_email_message + " \n \n" + verification_code

    message = MIMEMultipart()
    message["From"] = smtp_config.sender_email
    message["To"] = user_email
    message["Subject"] = subject

    message.attach(MIMEText(body, "plain"))
    try:
        await send_email_via_smtp(user_email, message)

        # save the email and the generated code
        verification_storage[user_email] = {
            'code': verification_code,
            'timestamp': datetime.now()
        }
    except Exception as e:
        print(f"Failed to send email. Error: {e}")


async def send_password_reset_email(user_email: EmailStr, new_password: str):
    subject = smtp_config.password_reset_email_subject
    body = smtp_config.password_reset_email_message + " \n \n" + new_password

    message = MIMEMultipart()
    message["From"] = smtp_config.sender_email
    message["To"] = user_email
    message["Subject"] = subject

    message.attach(MIMEText(body, "plain"))
    try:
        await send_email_via_smtp(user_email, message)
    except Exception as e:
        print(f"Failed to send email. Error: {e}")
