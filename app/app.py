from fastapi import FastAPI
from router import router as audio_notes_router
from db import engine, Base

app = FastAPI()

# Подключаем роутер для работы с вебсокетами и аудиозаметками
app.include_router(audio_notes_router)


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
