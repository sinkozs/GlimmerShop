from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

jwt_algorithm = "RS256"
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="token")
http_only_auth_cookie = "glimmershop_successful_login"
token_expiry_minutes = 20
