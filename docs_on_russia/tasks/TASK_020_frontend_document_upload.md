# TASK_020_frontend_document_upload

## Цель

Создать MVP оболочку frontend и экран загрузки документов, подключённый к backend API загрузки.

---

## Входной контекст

Прочитать перед кодированием:

- `docs/SDD.md`
- `docs/AI_RULES.md`
- `docs/HANDOFF.md`
- файлы предыдущих задач по применимости
- этот файл задачи

Соответствующий контекст:

- файлы предыдущих задач 001-019
- SDD стек frontend React/TypeScript/Vite/Tailwind

---

## Файлы для создания или изменения

Ожидаемые файлы:

- `frontend/package.json`
- `frontend/index.html`
- `frontend/vite.config.ts`
- `frontend/src/main.tsx`
- `frontend/src/App.tsx`
- `frontend/src/api/client.ts`
- `frontend/src/features/documents/UploadPage.tsx`
- `frontend/src/styles.css`

Добавлять минимальные вспомогательные файлы только когда требуется импортами/тестами.

---

## Требования

- Инициализировать React + TypeScript + Vite приложение, если frontend не существует.
- Реализовать форму загрузки с файлом, title, source_type, access_level, опционально language/year.
- Вызывать `POST /api/v1/documents/upload` через API клиент.
- Отображать успех/ошибку загрузки и возвращённый ID документа/задачи.
- Использовать переменную окружения для базового URL backend.

---

## Явно не делать

Не делать:

- хранить backend секреты в frontend
- реализовывать поисковый UI
- реализовывать UI графа
- обходить backend API
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

- Frontend запускается локально.
- UI загрузки отправляет multipart запрос.
- Ошибки видны пользователю.
- Нет секретов в файлах frontend.
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
- следующая задача: `TASK_021_frontend_search_and_answer.md`;
- готовность к коммиту.
