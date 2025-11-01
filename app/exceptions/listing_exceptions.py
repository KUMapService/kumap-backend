from fastapi import HTTPException, status


class ListingAlreadyExistsException(HTTPException):
    """이미 매물로 등록된 토지"""
    def __init__(self, pnu: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"해당 토지는 이미 매물로 등록되어 있습니다. (PNU: {pnu})"
        )


class ListingNotFoundException(HTTPException):
    """매물을 찾을 수 없음"""
    def __init__(self, pnu: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"해당 토지는 매물로 등록되어 있지 않습니다. (PNU: {pnu})"
        )


class NotListingOwnerException(HTTPException):
    """매물 등록자가 아님"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="다른 사람이 올린 매물은 수정/삭제할 수 없습니다."
        )


class OwnerNotRegisteredException(HTTPException):
    """소유주 미등록"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="매물 등록 전에 소유주 등록을 먼저 진행해주세요."
        )


class NotLandOwnerException(HTTPException):
    """토지 소유주가 아님"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="다른 소유주의 토지는 매물을 등록할 수 없습니다."
        )


class OwnerNotFoundException(HTTPException):
    """소유주를 찾을 수 없음"""
    def __init__(self, pnu: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"소유주 정보를 찾을 수 없습니다. (PNU: {pnu})"
        )