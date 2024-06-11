from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from config.parser import load_config

ALGORITHM = "HS256"
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="token")

