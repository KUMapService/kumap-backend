import uvicorn

from app import app
from app.core.config import SERVER_PORT

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=SERVER_PORT,
    )
