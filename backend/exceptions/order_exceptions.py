from fastapi import HTTPException, status


class OrderException(HTTPException):
    def __init__(self, status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"):
        super().__init__(status_code=status_code, detail=detail)
