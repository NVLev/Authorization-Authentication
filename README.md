# Структура проекта
```
auth_system/
├── core/
│   ├── __init__.py
│   ├── db_helper.py      # ✅ AsyncSession helper
│   ├── models.py         # ✅ Все SQLAlchemy модели
│   ├── schemas.py        # ✅ Pydantic схемы
│   └── config.py         # ⚠️ ДОБАВЬ! Настройки из .env
├── services/
│   ├── __init__.py
│   ├── auth_service.py   # ✅ Аутентификация
│   └── authz_service.py  # ✅ Авторизация (новый!)
├── routes/
│   ├── __init__.py
│   ├── auth.py           # ✅ /auth/* endpoints
│   ├── admin.py          # ✅ /admin/* (управление правами)
│   └── mock_resources.py # ✅ /projects, /orders (демо)
├── middleware/
│   ├── __init__.py
│   └── permissions.py    # ✅ Проверка прав (dependency)
├── alembic/              # ✅ Миграции
├── .env                  # ✅ DB credentials, JWT secrets
├── pyproject.toml        # ✅ Poetry dependencies
├── docker-compose.yml    # ✅ PostgreSQL
├── main.py               # ✅ FastAPI app
└── README.md             # ✅ Описание архитектуры БД
```
