from fastapi import FastAPI
from .core.database import wait_for_db, Base, engine
from .routes import appointment, auth, doctor

app = FastAPI()
app.include_router(appointment.router)
app.include_router(auth.router)
app.include_router(doctor.router)

@app.on_event("startup")
async def startup():
    await wait_for_db()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
def root():
    return {"status": "OK"}
