from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.routes import auth, expense, user
from app.config.database import engine, Base

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ROUTES
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(expense.router)


# ✅ PROPER DB INITIALIZATION
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.execute(
            text(
                "ALTER TABLE IF EXISTS expenses ADD COLUMN IF NOT EXISTS created_at timestamp DEFAULT NOW()"
            )
        )