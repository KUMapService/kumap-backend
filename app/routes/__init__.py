from app.routes.auction import auction_router
from app.routes.auth import auth_router
from app.routes.geo import geo_router
from app.routes.land import land_router
from app.routes.listing import listing_router
from app.routes.map import map_router
from app.routes.region import region_router
from app.routes.user import user_router

routers = [
    auction_router,
    auth_router,
    geo_router,
    land_router,
    listing_router,
    user_router,
    map_router,
    region_router,
]

def setup_routers(app):
    """FastAPI 앱에 라우터 등록하는 함수"""
    for router in routers:
        app.include_router(router)
