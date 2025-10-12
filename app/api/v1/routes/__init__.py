from fastapi import APIRouter

from app.api.v1.routes.auth_routes import router as auth_router
from app.api.v1.routes.geo_routes import router as geo_router

api_router = APIRouter()

# 각 라우터 등록
api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
api_router.include_router(geo_router, prefix="/geo", tags=["Geography"])

