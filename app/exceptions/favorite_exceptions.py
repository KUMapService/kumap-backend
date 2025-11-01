from fastapi import HTTPException, status


class AlreadyFavoritedException(HTTPException):
    """이미 좋아요한 토지"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="이미 관심 토지로 등록되어 있습니다."
        )


class FavoriteNotFoundException(HTTPException):
    """좋아요 없음"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="관심 토지로 등록되어 있지 않습니다."
        )
