from fastapi import HTTPException, status


class ProductException(HTTPException):
    def __init__(self, status_code=status.HTTP_404_NOT_FOUND, detail="Product not found!"):
        super().__init__(status_code=status_code, detail=detail)

    def category_not_found(self, status_code, detail="Category not found!"):
        super().__init__(status_code=status_code, detail=detail)
