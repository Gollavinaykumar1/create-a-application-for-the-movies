from fastapi import FastAPI
from database import init_db, get_db
from routers import items

app = FastAPI()

app.include_router(items.router)

@app.on_event("startup")
async def startup_event():
    await init_db()

@app.on_event("shutdown")
async def shutdown_event():
    await get_db().close()