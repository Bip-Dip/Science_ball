# TASK_017_search_api_basic

## Цель

Реализовать поисковый API на базе Elasticsearch с фильтрацией доступа и результатами доказательств.

---

## Входной контекст

Прочитать перед кодированием:

- `docs/SDD.md`
- `docs/AI_RULES.md`
- `docs/HANDOFF.md`
- файлы предыдущих задач по применимости
- этот файл задачи

Соответствующий контекст:

- файлы предыдущих задач 001-016
- SDD гибридный поиск и требования access_level

---

## Файлы для создания или изменения

Ожидаемые файлы:

- `backend/app/api/routes/search.py`
- `backend/app/api/router.py`
- `backend/app/search/search_service.py`
- `backend/app/search/query_builder.py`
- `backend/app/schemas/search.py`
- `backend/tests/unit/test_search_query_builder.py`
- `backend/tests/unit/test_search_api.py`

Добавлять минимальные вспомогательные файлы только когда требуется импортами/тестами.

---

## Требования

- Предоставить `POST /api/v1/search`.
- Применять обязательную фильтрацию `access_level`.
- Поддерживать текстовый запрос, фильтры по типу источника/году/сущности/числам на уровне MVP.
- Возвращать ранжированные чанки/доказательства с метаданными документа и ID трассировки.
- Держать route тонким и использовать service/query builder.

---

## Явно не делать

Не делать:

- генерировать LLM ответы
- писать обход графа
- пропускать фильтрацию доступа
- возвращать скрытые документы
- изменять `docs/SDD.md`
- коммитить реальные секреты или приватные данные

---

## Команды валидации

Из корня репозитория, адаптировать под текущий этап:

```bash
cd backend
python -m pytest
python -m compileall app
```

Если изменены frontend файлы:

```bash
cd frontend
npm install
npm run build
```

Если требуются Docker сервисы и они доступны:

```bash
docker compose up -d
```

---

## Definition of Done

- Поисковый query builder протестирован.
- API ответ включает доказательства и источники.
- Фильтр `access_level` всегда присутствует.
- Базовый поиск не делает LLM-вызовов.
- `docs/HANDOFF.md` обновлён Claude Code с Gemma-4-31B.

---

## Ожидаемое обновление handoff

Claude Code с Gemma-4-31B должен обновить `docs/HANDOFF.md`:

- статус задачи;
- изменённые файлы;
- команды валидации и результаты;
- заметки по выполнению;
- заглушки/заполнители;
- известные проблемы;
- следующая задача: `TASK_018_answer_synthesis_with_evidence.md`;
- готовность к коммиту.
