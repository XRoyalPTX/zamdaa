from fastapi import FastAPI, Depends
from app.routers.users import router as users_router
from app.routers.locations import router as locations_router
from app.routers.trips import router as trips_router


app = FastAPI(
    title="Zamdaa API",
    description="Бэкенд для сервиса поиска попутчиков в Бурятии",
    version="0"
)

app.include_router(users_router)
app.include_router(locations_router)
app.include_router(trips_router)