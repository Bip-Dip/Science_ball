# 🧪 R&D Knowledge Map

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)](https://www.python.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.6-3178c6)](https://www.typescriptlang.org/)

**Интеллектуальная система поиска, анализа и построения карты знаний для горно-металлургических исследований.**

Принимает научные публикации, внутренние отчёты, патенты, экспериментальные протоколы, таблицы и справочники; извлекает сущности, числовые параметры, связи и факты; позволяет исследователям задавать сложные вопросы на русском и английском языках и получать структурированные ответы с источниками, уровнем достоверности и связями графа знаний.

---

## 📖 Содержание

- [Возможности](#-возможности)
- [Архитектура](#-архитектура)
- [Технологический стек](#-технологический-стек)
- [Быстрый старт](#-быстрый-старт)
- [API](#-api)
- [Демо-сценарий](#-демо-сценарий)
- [Структура проекта](#-структура-проекта)
- [Makefile-команды](#-makefile-команды)
- [Документация](#-документация)
- [Статус и Roadmap](#-статус-и-roadmap)
- [Лицензия](#-лицензия)

---

## 🚀 Возможности

### Загрузка и обработка документов
- Поддержка форматов: **PDF**, **DOCX**, **XLSX/CSV**, **Markdown**, **TXT**
- Извлечение текста и таблиц (PyMuPDF, python-docx, pandas, openpyxl)
- Интеллектуальный чанкинг (размер чанка 1000 токенов, перекрытие 200)

### Извлечение знаний
- **Сущности:** материалы, процессы, оборудование, свойства, эксперименты, публикации, эксперты, организации, локации
- **Числовые параметры:** температура, давление, pH, скорость потока, концентрация, CAPEX/OPEX и др.
- Нормализация единиц измерения в систему СИ
- Словарный NER + regex + spaCy

### Поиск и ответы на вопросы
- **Гибридный поиск:** BM25 + векторный + числовые фильтры (Elasticsearch 8)
- **RAG-ответы:** синтез ответа строго на основе найденных evidence, с цитированием источников
- **Query Understanding:** YandexGPT + Pydantic-валидация + fallback на regex/словари
- Поддержка русского и английского языков

### Граф знаний
- Автоматическое построение графа связей в Neo4j
- Типы связей: `USES_MATERIAL`, `OPERATES_AT_CONDITION`, `DESCRIBED_IN`, `AUTHORED_BY` и др.
- Визуализация графа через React Flow
- Обход окрестности узла

### Верификация фактов
- Оценка достоверности (confidence) по взвешенной формуле:
  - Качество извлечения × 0.35
  - Надёжность источника × 0.25
  - Подтверждающие источники × 0.20
  - Экспертная верификация × 0.20
- Интерфейс проверки: подтверждение, отклонение, редактирование, комментирование

### Экспорт
- Выгрузка результатов в **Markdown**

---

## 🏗 Архитектура

```
┌─────────────────────────────────────────────────────────┐
│                   Frontend (React 18)                    │
│          Vite · Tailwind CSS · React Flow · TS           │
│                  localhost:3000                          │
└─────────────────────┬───────────────────────────────────┘
                      │ HTTP/REST
┌─────────────────────▼───────────────────────────────────┐
│              FastAPI Backend (Python 3.11)               │
│                  localhost:8000                          │
│  ┌──────────┬──────────┬───────────┬────────────────┐   │
│  │ Ingestion│  Search  │  Answers  │  Graph / Facts │   │
│  └────┬─────┴────┬─────┴─────┬─────┴───────┬────────┘   │
└───────┼──────────┼───────────┼─────────────┼────────────┘
        │          │           │             │
   ┌────▼──┐ ┌────▼────┐ ┌───▼────┐  ┌─────▼──────┐
   │Celery │ │Elastic- │ │ Neo4j  │  │ PostgreSQL │
   │Worker │ │search 8 │ │   5    │  │    16      │
   └───┬───┘ └─────────┘ └────────┘  └────────────┘
       │
   ┌───▼───┐  ┌────────┐  ┌──────────────┐
   │ Redis │  │ MinIO  │  │  LLM Gateway  │
   │   7   │  │  (S3)  │  │  ┌──────────┐ │
   └───────┘  └────────┘  │  │YandexGPT │ │
                           │  ├──────────┤ │
                           │  │ Ollama   │ │
                           │  ├──────────┤ │
                           │  │ Mock     │ │
                           │  └──────────┘ │
                           └──────────────┘
```

**Ключевые принципы:**
- Elasticsearch — основной поисковый слой
- Neo4j — отдельное графовое хранилище
- LLM **не является** источником истины — все факты трассируются до документа и чанка
- Числовые параметры извлекаются детерминированно (regex/parser + нормализация)
- YandexGPT — только через `LLMGateway`, без прямой зависимости бизнес-логики от провайдера

---

## 🛠 Технологический стек

| Слой | Технологии |
|------|-----------|
| **Бэкенд** | Python 3.11+, FastAPI, Uvicorn, Celery, SQLAlchemy 2.0 (async), Alembic |
| **Поиск** | Elasticsearch 8.12 (BM25 + векторный + числовой) |
| **Граф** | Neo4j 5.18 (Community) |
| **БД** | PostgreSQL 16 (транзакции, RBAC, аудит) |
| **Кеш/очереди** | Redis 7 |
| **Хранилище** | MinIO (S3-совместимое) |
| **LLM** | YandexGPT (`yandexgpt-lite`), Ollama (Qwen2.5-7B, fallback) |
| **Embeddings** | `intfloat/multilingual-e5-small` |
| **NLP** | spaCy, regex, словари домена |
| **Парсинг** | PyMuPDF, python-docx, pandas, openpyxl |
| **Фронтенд** | React 18, TypeScript 5.6, Vite 5, Tailwind CSS 3, React Flow 11 |
| **Инфраструктура** | Docker Compose (8 сервисов) |

---

## ⚡ Быстрый старт

### Предварительные требования
- **Docker** и **Docker Compose**
- Python 3.11+ и Node.js 18+ (для локальной разработки)

### 1. Клонирование и настройка

```bash
git clone git@github.com:Bip-Dip/Science_ball.git
cd Science_ball

# Создать .env из примера
cp .env.example .env
```

Отредактируйте `.env`, указав минимум:
```bash
YANDEX_API_KEY=your_yandex_api_key
YANDEX_FOLDER_ID=your_yandex_folder_id
```

### 2. Запуск всех сервисов

```bash
make up
# или: docker compose up -d
```

### 3. Проверка статуса

```bash
make ps     # статус контейнеров
make logs   # логи всех сервисов
```

### 4. Загрузка демо-данных

```bash
pip install httpx
python scripts/demo_seed.py
```

### 5. Проверка работоспособности

```bash
./scripts/demo_smoke.sh
```

### 6. Доступ к приложению

| Компонент | URL |
|-----------|-----|
| **Фронтенд** | http://localhost:3000 |
| **Backend API** | http://localhost:8000 |
| **Swagger-документация** | http://localhost:8000/docs |
| **Elasticsearch** | http://localhost:9200 |
| **Neo4j Browser** | http://localhost:7474 |
| **MinIO Console** | http://localhost:9001 |

### Локальная разработка

```bash
# Бэкенд
cd backend
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8000

# Фронтенд
cd frontend
npm install
npm run dev
```

---

## 📡 API

| Метод | Эндпоинт | Назначение |
|-------|----------|-----------|
| `GET` | `/health` | Health check |
| `GET` | `/api/v1/health` | Health check v1 |
| `GET` | `/api/v1/health/config` | Статус конфигурации хранилищ |
| `POST` | `/api/v1/documents/upload` | Загрузка документа |
| `GET` | `/api/v1/ingestion/jobs/{job_id}` | Статус ingestion-задачи |
| `POST` | `/api/v1/ingestion/jobs/{job_id}/retry` | Повтор задачи |
| `POST` | `/api/v1/search` | Гибридный поиск |
| `POST` | `/api/v1/answers/` | Синтез ответа (RAG) |
| `POST` | `/api/v1/graph/neighborhood` | Окрестность узла графа |
| `GET` | `/api/v1/facts/pending-review` | Факты на проверку |
| `POST` | `/api/v1/facts/{id}/verify` | Подтвердить факт |
| `POST` | `/api/v1/facts/{id}/reject` | Отклонить факт |
| `POST` | `/api/v1/facts/{id}/comment` | Комментарий к факту |
| `PATCH` | `/api/v1/facts/{id}` | Редактировать факт |
| `POST` | `/api/v1/exports/markdown` | Экспорт ответа в Markdown |

---

## 🎬 Демо-сценарий

В директории `demo/sample_documents/` находятся три тестовых документа:

| Документ | Тема | Ключевые параметры |
|----------|------|-------------------|
| `doc1_electrowinning.md` | Никелевая электроэкстракция | Скорость циркуляции католита 0.15–0.25 м/с, температура 60–65°C |
| `doc2_water_desalination.md` | Обессоливание шахтных вод | — |
| `doc3_au_recovery.md` | Извлечение золота и серебра | — |

**Типичный сценарий использования:**

1. Загрузите технический документ через UI (`/documents`)
2. Выполните поиск: «nickel electrowinning»
3. Задайте вопрос: «What is the optimal catholyte circulation rate?»
4. Получите RAG-ответ с цитированием источников и confidence-оценкой
5. Экспортируйте результат в Markdown

---

## 📁 Структура проекта

```
Science_ball/
├── backend/
│   ├── app/
│   │   ├── main.py                 # Точка входа FastAPI
│   │   ├── settings.py             # Конфигурация (Pydantic Settings)
│   │   ├── dependencies.py         # FastAPI Depends
│   │   ├── api/routes/             # HTTP-эндпоинты
│   │   ├── db/                     # Клиенты хранилищ (PG, ES, Neo4j, Redis, MinIO)
│   │   ├── models/                 # SQLAlchemy-модели
│   │   ├── schemas/                # Pydantic-схемы
│   │   ├── repositories/           # Data access layer
│   │   ├── services/
│   │   │   ├── ingestion/          # Пайплайн загрузки документов
│   │   │   ├── parsing/            # Парсеры (PDF, DOCX, XLSX, MD, TXT)
│   │   │   ├── nlp/                # NER, извлечение чисел, нормализация
│   │   │   ├── search/             # Поисковый сервис
│   │   │   ├── answers/            # RAG-синтез ответов
│   │   │   ├── query/              # Query Understanding
│   │   │   ├── llm/                # LLM-абстракция (YandexGPT, Ollama, Mock)
│   │   │   ├── graph/              # Графовые запросы
│   │   │   ├── exports/            # Экспорт (Markdown)
│   │   │   └── review/             # Верификация фактов
│   │   ├── graph/                  # Neo4j writer + схема
│   │   ├── search/                 # ES: маппинги, индексы, запросы
│   │   └── worker/                 # Celery app + задачи
│   ├── tests/
│   ├── Dockerfile
│   └── pyproject.toml
├── frontend/
│   ├── src/
│   │   ├── App.tsx                 # Роутинг
│   │   ├── api/                    # API-клиенты
│   │   └── features/
│   │       ├── documents/          # Страница загрузки
│   │       ├── search/             # Поиск + ответы
│   │       └── graph/              # Визуализация графа
│   ├── package.json
│   └── vite.config.ts
├── demo/
│   ├── sample_documents/           # Демо-документы
│   └── README.md
├── scripts/
│   ├── demo_seed.py                # Загрузка демо-данных
│   └── demo_smoke.sh               # Smoke-тест
├── docs/                           # Проектная документация
├── docker-compose.yml              # 8 сервисов
├── Makefile
├── .env.example
└── README.md
```

---

## 🔧 Makefile-команды

| Команда | Действие |
|---------|----------|
| `make up` | Запустить все сервисы |
| `make down` | Остановить все сервисы |
| `make build` | Собрать образы backend и worker |
| `make logs` | Логи всех сервисов |
| `make ps` | Статус запущенных контейнеров |
| `make clean` | Остановить и удалить все тома (сброс данных) |
| `make test` | Запустить тесты бэкенда |
| `make config` | Валидировать docker-compose.yml |
| `make infra-up` | Только инфраструктура (без backend/worker) |
| `make infra-down` | Остановить инфраструктуру |

---

## 📚 Документация

| Документ | Описание |
|----------|----------|
| `docs/SDD.md` | System Design Document — полная спецификация системы |
| `docs/HANDOFF.md` | Статус передачи проекта, выполненные задачи |
| `docs/IMPLEMENTATION_PLAN.md` | План реализации |
| `docs/QUALITY_CONTROL.md` | Процедуры контроля качества |
| `docs/AI_RULES.md` | Правила для AI-агентов |
| `docs/ACCEPTANCE_TEMPLATE.md` | Шаблон приёмки задач |
| `demo/README.md` | Гайд по демо-сценарию |

---

## 📊 Статус и Roadmap

**Текущая версия:** 0.1.0 (MVP)

### ✅ Реализовано
- Загрузка и парсинг документов (PDF, DOCX, XLSX/CSV, MD, TXT)
- Извлечение сущностей и числовых параметров
- Индексация в Elasticsearch и построение графа в Neo4j
- Гибридный поиск (BM25 + фильтры)
- RAG-синтез ответов с цитированием
- Визуализация графа знаний (React Flow)
- Верификация фактов (подтверждение/отклонение/редактирование)
- Экспорт в Markdown
- LLM-абстракция (YandexGPT + Ollama fallback)

### 🔜 Запланировано (post-MVP)
- Полноценный OCR сложных сканов
- JWT-аутентификация и RBAC
- Продвинутый reranker поисковой выдачи
- OWL/SHACL-валидация онтологии
- Экспорт в PDF и JSON-LD
- Интеграция с внешними патентными базами
- Автоматическое выявление противоречий
- BI-дашборды, SSO/LDAP

---


