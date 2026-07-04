## Текущий статус

- Текущая задача: `TASK_023_markdown_export`
- Статус: завершена
- Последнее обновление: Gemma (Интегратор)
- Последнее обновление: 2026-07-04

---

## Выполненные задачи

| Задача | Статус | Коммит | Примечания |
|---|---|---|---|
| ... | завершена | TBD | Предыдущие и этапы разработки |
| TASK_022_frontend_graph_preview | завершена | TBD | Реализован UI предпросмотра графа и API получения окрестности |
| TASK_023_markdown_export | завершена | TBD | Реализован экспорт синтезированных ответов в Markdown на backend и frontend |

---

## Текущее состояние репозитория

### Реализовано
- Backend API для извлечения локального подграфа вокруг узла (`POST /api/v1/graph/neighborhood`).
- Фильтрация результатов запроса в Neo4j на основе `access_level` для обеспечения безопасности данных.
- Frontend страница визуализации графа с использованием React Flow.
- Интерактивный поиск и исследование связей между сущностями (Materials, Processes, Equipment, Documents).
- Панель деталей узла с отображением метаданных (свойства, ID, метка).
- Обобщенный хелпер `post` в API-клиенте фронтенда для унификации запросов.
- Настройка роутинга для доступа к странице `/graph`.
- Сервис экспорта ответов в Markdown (`MarkdownExportService`), преобразующий синтезированный ответ, доказательства и противоречия в структурированный документ.
- API эндпоинт `POST /api/v1/exports/markdown` для скачивания MD-файла.
- Frontend компонент `ExportButton`, интегрированный в панель ответа (`AnswerPanel`), позволяющий пользователю скачать отчет одним кликом.

### Не реализовано
- Продвинутый algorithm раскладки узлов (сейчас используется простая круговая схема).
- Полная интеграция с JWT/Auth для динамического определения уровней доступа (сейчас используются заглушки `["public", "internal"]`).

---

## Изменённые файлы в последней задаче

```text
backend/app/api/routes/exports.py
backend/app/api/router.py
backend/app/schemas/exports.py
backend/app/services/exports/markdown_export_service.py
backend/tests/unit/test_markdown_export_service.py
frontend/src/api/exports.ts
frontend/src/features/answers/ExportButton.tsx
frontend/src/features/search/components/AnswerPanel.tsx
```

---

## Запущенные команды валидации

```bash
cd backend && python -m pytest tests/unit/test_markdown_export_service.py
cd backend && python -m compileall app
cd frontend && npm run build
```

Результат:
- Pytest: 2 passed.
- Compileall: Success.
- NPM Build: Success (no TS errors).

---

## Схема БД и миграции

В данной задаче изменения в схеме PostgreSQL не требовались.

---

## Заглушки и моки

| Область | Заглушка/мок | Причина | Задача удаления |
|---|---|---|---|
| Access Control | Hardcoded `["public", "internal"]` в API | Отсутствие полной интеграции с системой Auth на данном этапе | Интеграция Auth/RBAC |
| Layout | Circular layout (круговая раскладка) | MVP-версия визуализации; сложные алгоритмы вынесены за рамки текущей задачи | Улучрование UX графа |

---

## Известные проблемы

| ID | Проблема | Серьёзность | Обход | Целевая задача |
|---|---|---|---|---|
| НЕТ | - | - | - | - |

---

## Открытые вопросы

| ID | Вопрос | Практический путь для MVP | Решение |
|---|---|---|---|
| OQ-022-1 | Формат экспорта графа в Markdown | Использовать текущий API окрестностей для генерации текстового описания связей | TASK_023 (частично реализовано через экспорт синтезированного ответа) |

---

## Заметки по окружению

Используется существующая конфигурация Neo4j драйвера. Дополнительные переменные окружения не требуются.

---

## Следующая задача

Рекомендуемая следующая задача:

```text
TASK_024_demo_data_and_script.md
```

Прочитать перед and начать:
- `docs/SDD.md`
- `backend/app/services/exports/markdown_export_service.py` (для понимания структуры экспортируемых данных)
- `docs/tasks/TASK_024_demo_data_and_script.md`
