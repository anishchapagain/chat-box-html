from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import webhooks
from app.api import websockets
from app.core.config import settings
from app.core.database import engine, Base

# Create DB tables (For local dev only, use Alembic for prod)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS config
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(webhooks.router, prefix=settings.API_V1_STR)
app.include_router(websockets.router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {"message": "ChatMax Omnichannel API is running"}
