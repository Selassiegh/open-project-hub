from contextlib import asynccontextmanager

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI

from .api import router
from .database import Base, SessionLocal, engine
from .services import check_weather_triggers

scheduler = BackgroundScheduler()


def daily_weather_check() -> None:
    with SessionLocal() as db:
        check_weather_triggers(db)


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    scheduler.add_job(daily_weather_check, "interval", days=1, id="daily-weather-check", replace_existing=True)
    scheduler.start()
    yield
    scheduler.shutdown(wait=False)


app = FastAPI(title="Harvest Credit", version="0.1.0", lifespan=lifespan)
app.include_router(router, prefix="/api")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "harvest-credit"}
