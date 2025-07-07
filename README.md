## KUMap Backend

![LOGO](./images/KUMapLogo.png)

> [!NOTE]
> This is the FastAPI-based backend repository for the KUMap Land Price Prediction Service.

---

### 📦 Tech Stack

- Language: Python 3.13
- Web Framework: FastAPI
- DB: MySQL
- ORM: SQLAlchemy
- Migration: Alembic
- Package Manager: uv
- Production Env: Ubuntu 20.04 LTS / ngrok

<br/>

### 📁 Project Structure

```
land-price-backend/
├── app/
│   ├── core/            # Config, security, and env management
│   ├── db/              # DB session, Base, Alembic-related
│   ├── models/          # SQLAlchemy model definitions
│   ├── routes/          # FastAPI endpoint definitions
│   ├── schemas/         # Pydantic schemas
│   ├── services/        # Business logic services
│   ├── utils/           # Utility functions
│   └── __init__.py      # FastAPI app instance
├── alembic/             # Alembic migration folder
├── .env                 # Environment variables (excluded via .gitignore)
├── alembic.ini          # Alembic configuration
├── run.py               # Entry point for running the server
└── README.md
```

<br/>

### 🚀 How to Run

#### 1. Install dependencies

```bash
uv sync
```

#### 2. Setup environment variables

Create a `.env` file and define the following:

```
BASE_DIR=
APP_DIR=
ROOT_PW=
DATABASE_NAME=
USER_NAME=
USER_PW=
SECRET_KEY=
SMTP_SERVER=
SMTP_PORT=
SMTP_USERNAME=
SMTP_PASSWORD=
SERVER_PORT=
SERVER_DOMAIN=
KAKAO_API_KEY=
VWORLD_API_KEY=
LAND_API_KEY=
ECOS_API_KEY=
KAKAO_JAVASCRIPT_API_KEY=
MODEL_PATH=
GOOGLE_API_KEY=
LLM_MODEL=
```

#### 3. Run database migration (first-time ONLY)

```bash
alembic upgrade head
```

#### 4. Generate region data (cadastral + region centroid)

```bash
uv run python -m src.database.generate_region_data
```

To generate only cadastral data, run:

```bash
uv run python -m src.database.generate_region_data --cadastral
```

To generate only region centroid data, run:

```
uv run python -m src.database.generate_region_data --centroid
```

#### 5. Generate land prediction data and region stats

```
uv run python -m src.database.make_land_data
```

```
uv run python -m src.database.generate_region_stat
```

#### 6. Get land auction data

First, crawl auction data from `https://www.courtauction.go.kr/`

```
uv run python -m src.database.crawl_auction_data
```

After crawling, update auction coordinate data.

```
uv run python -m src.database.crawl_auction_data -c
```

#### 7. Run the server

```
uv run run.py
```

<br/>

### 🧪 Swagger Documents

- Swagger UI: https://api.landprice.info/docs
- ReDoc: https://api.landprice.info/redoc

<br/>

### 🛠 Main Features

- User authentication (JWT login / signup / refresh token)
- Land information and prediction API
- Favorite land feature
- Integration with external public APIs with parallel processing
- Database migration with Alembic

<br/>

### 🕒 Version History

| version | date       | feature         |
| :------ | :--------- | :-------------- |
| 1.0.0   | 2025-05-01 | Initial Release |
