from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from config.parser import load_config

ALGORITHM = "HS256"
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="token")

TOKEN_EXPIRY_MINUTES = load_config().auth_config.token_expiry_minutes

SECRET_KEY = load_config().auth_config.secret_key
