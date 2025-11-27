import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager

from routes import auth, admin, mock_resourses
from core.db_helper import db_helper


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Управление жизненным циклом приложения:
    - Инициализация при старте
    - Корректное завершение при остановке
    """

    print("Приложение запущено. Подключение к базе данных готово.")
    try:
        yield
    finally:
        await db_helper.dispose()
        print("Соединение с базой данных закрыто.")


app = FastAPI(lifespan=lifespan)


app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(mock_resourses.router)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

