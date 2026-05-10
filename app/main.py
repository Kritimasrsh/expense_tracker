from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.routes.user import router as user_router
from app.config.database import engine
from app.config.database import Base


@asynccontextmanager
async def lifespan(app: FastAPI):

    print("Server starting...")

    Base.metadata.create_all(bind=engine)

    yield

    print("Server shutting down...")


app = FastAPI(lifespan=lifespan)

app.include_router(user_router)


@app.get("/")
def home():
    return {"message": "FastAPI running"}