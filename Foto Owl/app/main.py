from fastapi import FastAPI
from .database import engine, Base
from .routers import admin, user
from app.database import SessionLocal
from app.models import User
from app.auth import get_password_hash


app = FastAPI()

Base.metadata.create_all(bind=engine)

app.include_router(admin.router, prefix="/admin", tags=["admin"])
app.include_router(user.router, prefix="/user", tags=["user"])


# Entry point for uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
