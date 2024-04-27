from fastapi import HTTPException, status


class UserException(HTTPException):
    def __init__(self, status_code=status.HTTP_404_NOT_FOUND, detail="No user exist"):
        super().__init__(status_code=status_code, detail=detail)
