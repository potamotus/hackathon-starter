# Hackathon Starter

Быстрый старт для хакатонной команды. Next.js + TypeScript + Tailwind.

## Быстрый старт

```bash
npm install
npm run dev
```

Открой [http://localhost:3000](http://localhost:3000).

## Структура

```
src/
  app/          # Next.js App Router (страницы + layout)
  components/   # Переиспользуемые UI-компоненты
  lib/          # Утилиты, хелперы, API-клиенты
public/         # Статика (картинки, фавиконки)
```

## Правила работы команды

### 1. Ветки
- `main` — всегда рабочая версия, деплоится
- Каждый участник работает в своей ветке: `feature/<имя-фичи>`
- Название ветки от задачи: `feature/auth`, `feature/landing`, `fix/header-bug`

### 2. Коммиты
- Маленькие, частые коммиты — лучше 10 мелких чем 1 огромный
- Формат: `feat: add login page`, `fix: header overlap on mobile`
- Не коммить `.env` файлы и секреты

### 3. Pull Requests
- Мержим в `main` только через PR
- Минимум 1 approve от тиммейта перед мержем
- Перед мержем: `npm run build` должен проходить

### 4. Деплой
- Подключи репозиторий к [Vercel](https://vercel.com) — бесплатный авто-деплой с `main`
- Каждая ветка получает preview URL автоматически

### 5. Задачи
- Ведите список задач в GitHub Issues или в общем чате
- Одна задача = одна ветка = один PR

## Полезные команды

| Команда | Что делает |
|---------|-----------|
| `npm run dev` | Запуск dev-сервера |
| `npm run build` | Продакшн-билд |
| `npm run start` | Запуск продакшн-сервера |
| `npm run lint` | Линтер |

## Стек

- **Framework:** Next.js 15 (App Router)
- **Language:** TypeScript
- **Styling:** Tailwind CSS 4
- **Deploy:** Vercel (бесплатно)
