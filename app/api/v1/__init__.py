from fastapi import FastAPI

from app.api.v1.routes import auth_router

routers = [
    auth_router,
]


def setup_routers(app: FastAPI):
    """FastAPI 앱에 라우터 등록하는 함수"""
    for router in routers:
        app.include_router(router)
