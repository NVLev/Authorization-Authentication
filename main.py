from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.db_helper import db_helper
from routes import admin, auth, mock_resourses  # ⬅️ Теперь все импорты работают


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    print("🚀 Приложение запущено. Подключение к БД готово.")
    try:
        yield
    finally:
        await db_helper.dispose()
        print("🔌 Соединение с БД закрыто.")


app = FastAPI(
    lifespan=lifespan,
    title="Custom Auth & Authorization System",
    description="""
    ## 🔐 Система аутентификации и авторизации

    ### 🧪 Тестовые аккаунты:
    - **Admin**: `admin@test.com` / `admin123` (полный доступ)
    - **Manager**: `manager@test.com` / `manager123` (читает все, редактирует свои)
    - **User**: `user@test.com` / `user123` (только свои объекты)

    ### 📖 Как использовать:
    1. Войдите через `POST /auth/login`
    2. Скопируйте `access_token` из ответа
    3. Нажмите **🔓 Authorize** вверху справа
    4. Вставьте токен (автоматически добавится `Bearer`)
    5. Тестируйте endpoints с разными ролями!
    """,
    version="1.0.0",
)

# CORS (если будет фронтенд)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Регистрация всех роутеров
app.include_router(auth.router)
app.include_router(admin.router)
app.include_router(mock_resourses.router)


@app.get("/", tags=["Root"])
async def root():
    """Главная страница API"""
    return {
        "message": "✨ Custom Auth & Authorization System",
        "version": "1.0.0",
        "docs": "http://localhost:8000/docs",
        "endpoints": {
            "auth": "/auth/*",
            "admin": "/admin/* (только для admin)",
            "projects": "/projects/* (демо-ресурс)",
        },
        "test_accounts": {
            "admin": "admin@test.com / admin123",
            "manager": "manager@test.com / manager123",
            "user": "user@test.com / user123",
        },
    }


@app.get("/health", tags=["Root"])
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "database": "connected"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
