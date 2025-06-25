import uvicorn

from app import app
from app.core.config import SERVER_PORT
from app.core import config

if __name__ == "__main__":
    print(config.VWORLD_API_KEY)
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=SERVER_PORT,
    )
