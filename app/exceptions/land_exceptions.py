from fastapi import HTTPException, status


class LandNotFoundException(HTTPException):
    def __init__(self, pnu: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"토지 정보를 찾을 수 없습니다. (PNU: {pnu})"
        )


class LandFeatureNotFoundException(HTTPException):
    def __init__(self, pnu: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"토지 특성 정보를 찾을 수 없습니다. (PNU: {pnu})"
        )


class OwnerAlreadyExistsException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 소유주로 등록되어 있습니다."
        )


class OwnerNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="소유주 정보를 찾을 수 없습니다."
        )
