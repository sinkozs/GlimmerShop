from fastapi import HTTPException, status


class AuthenticationException(HTTPException):
    def __init__(self, status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password!"):
        super().__init__(status_code=status_code, detail=detail)