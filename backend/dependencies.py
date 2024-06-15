from datetime import datetime, timedelta
from uuid import UUID
from fastapi import Depends, HTTPException
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from pydantic import EmailStr
from jose import jwt
from config.auth_config import ALGORITHM, oauth2_bearer
from config.parser import load_config
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

smtp_config = load_config().smtp_config
verification_storage = dict()


async def get_session() -> AsyncSession:
    raise NotImplementedError("Please overwrite get_session dependency.")


def db_model_to_dict(model_instance) -> dict:
    return {column.name: getattr(model_instance, column.name) for column in model_instance.__table__.columns}


def dict_to_db_model(model_class, data: dict):
    instance = model_class()
    for key, value in data.items():
        setattr(instance, key, value)
    return instance


async def get_current_user(user_token: str = Depends(oauth2_bearer)) -> dict:
    try:
        auth_config = load_config().auth_config
        payload = jwt.decode(user_token, auth_config.secret_key, algorithms=[ALGORITHM])
        email: EmailStr = payload.get("email")
        user_id: UUID = payload.get("id")

        if email is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"}
            )
        else:
            return {"email": email, "id": user_id}

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )


def generate_random_verification_code() -> str:
    verification_code = ''.join(random.choices('0123456789', k=6))
    return verification_code


async def verify_code(email: EmailStr, code):
    if email not in verification_storage:
        return False, "Invalid email or verification code"

    if verification_storage[email]['code'] != code:
        return False, "Invalid verification code"

    if datetime.now() - verification_storage[email]['timestamp'] > timedelta(minutes=smtp_config.verification_code_expiration_minutes):
        return False, "Verification code expired"
    else:
        return True, "Account successfully verified!"


async def send_verification_email(first_name: str, user_email: EmailStr):
    sender_email = smtp_config.verification_email_sender
    receiver_email = user_email
    subject = smtp_config.verification_email_subject
    verification_code = generate_random_verification_code()
    body = f"Hey {first_name}! \n \n " + smtp_config.verification_email_message + " \n \n" + verification_code

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    message.attach(MIMEText(body, "plain"))

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
        server.sendmail(sender_email, receiver_email, message.as_string())
        # save the email and the generated code
        verification_storage[receiver_email] = {
            'code': verification_code,
            'timestamp': datetime.now()
        }
        print("STORAGE WHEN SENDING EMAIL")
        print(verification_storage)
        print("Email sent successfully!")

    except Exception as e:
        print(f"Failed to send email. Error: {e}")

    finally:
        server.quit()
