from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.database import connect_db
from app.api.route import snap

# 1. Define the lifespan logic
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the database connection
    await connect_db()
    yield
    
    # await disconnect_db()

# 2. Pass the lifespan to the FastAPI constructor
app = FastAPI(title="Road Snap API", version="1.0.0", lifespan=lifespan)

app.include_router(snap.router)