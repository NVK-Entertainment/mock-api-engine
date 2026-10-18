# mock-api-engine
Это динамический движок для генерации API заглушек. <br> Позволяющий обеспечить параллельную работу backend и frontend разработчиков.

## ⚙️ Настройка:
### 1. Клонирование репозитория:

#### HTTP:
```bash
git clone https://github.com/NVK-Entertainment/mock-api-engine
```

#### SSH:
```bash
git clone git@github.com:NVK-Entertainment/mock-api-engine.git
```

### 2. Настройка переменных окружения:
```bash
cd ~/mock-api-engine && cp ./.env.example ./.env
```

## 🚀 Запуск:
```bash
cd ~/mock-api-engine && docker compose up --build && DB_HOST=localhost alembic upgrade head
```