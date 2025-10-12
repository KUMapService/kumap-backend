from fastapi import HTTPException, status


class CoordRetrievalError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="좌표를 조회할 수 없습니다."
        )


class PNURetrievalError(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="PNU를 조회할 수 없습니다."
        )


class CadastralMapNotFoundError(HTTPException):
    def __init__(self, pnu: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"해당 토지({pnu})의 지적도 데이터가 없습니다."
        )
