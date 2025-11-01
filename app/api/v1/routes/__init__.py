from fastapi import APIRouter

from app.api.v1.routes.auth_routes import router as auth_router
from app.api.v1.routes.geo_routes import router as geo_router
from app.api.v1.routes.land_routes import router as land_router
from app.api.v1.routes.listing_routes import router as listing_router
from app.api.v1.routes.user_routes import router as user_router
from app.api.v1.routes.auction_routes import router as auction_router
from app.api.v1.routes.map_routes import router as map_router

api_router = APIRouter()

# 각 라우터 등록
api_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
api_router.include_router(auction_router, prefix="/auctions", tags=["Auctions"])
api_router.include_router(geo_router, prefix="/geo", tags=["Geography"])
api_router.include_router(land_router, prefix="/lands", tags=["Lands"])
api_router.include_router(listing_router, prefix="/listings", tags=["Listings"])
api_router.include_router(user_router, prefix="/users", tags=["Users"])
api_router.include_router(map_router, prefix="/maps", tags=["Maps"])
