from fastapi import FastAPI
from database import engine, Base
from routers import router


app = FastAPI(title="stepik")

# create table pri starte
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        # fktv,br
        await conn.run_sync(Base.metadata.create_all)

app.include_router(router)