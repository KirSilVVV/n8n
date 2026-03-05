# Контекст для нового чата — SEO Agent v2 + WF-205
**gaming-goods.ru | 05.03.2026 | Передать в следующий чат**

---

## Кто ты в этом проекте

Ты — заказчик продуктовых фич. Ставишь задачи Клоду-разработчику (которого контролирует Саша).
Работаешь как эксперт Apple. Результаты — в файлах `.md`.
Саша может быть АФК — не жди ответов, работай автономно.

---

## Стек и доступы

| Система | Детали |
|---------|--------|
| n8n | `https://n8n-4d54.onrender.com` |
| n8n API key | `N8N_API_KEY_XXXX` |
| PostgreSQL | `65.108.106.66:5432` | cred ID в n8n: `vMUuOggCtBWX48Jg` |
| GitHub | `https://github.com/KirSilVVV/n8n` | token: `ghp_XXXX_IN_N8N_SETTINGS` |
| Telegram chat | `83436260` | cred ID: `IjoBfA5jgnMrU9qV` |
| Anthropic cred | ID: `xZPzwI0sOTN0iSp8` (claude-opus-4-5) |
| GSC / GA4 | Service Account через JWT (cred в WF-201) |
| Яндекс OAuth | `YA_OAUTH_XXXX_IN_N8N` |
| ЯМ counter | `105005697` |

**Живой webhook для PG-запросов:** `GET https://n8n-4d54.onrender.com/webhook/pg-test-v2`
Workflow ID: `GvQ1CVxAHzgUZUMq` — меняй SQL в ноде `PG`, запрашивай через webhook.
Паттерн: `SELECT json_agg(t) as result FROM ({твой SQL}) t`

---

## Воркфлоу которые уже работают

| WF | ID | Статус | Что делает |
|----|----|--------|-----------|
| WF-201 | `1EcezAM2sWYv6WSL` | ✅ Active, 06:00 UTC | SEO отчёт: GA4 + GSC + ЯМ → Telegram |
| WF-202 v2 | `iI3kYbrzbobvbklo` | ✅ Deployed, 06:05 UTC | SEO AI Agent: Claude анализ + **DB SEO Health** |

**WF-202 v2 архитектура (важно!):**
```
Schedule → JWT → GA4 Token → GA4 Data → GSC Token → GSC Queries → GSC Pages
→ YM Data → PG SEO Health → PG Missing Titles → Prepare → Claude → Format → Telegram
```

**PG SEO Health** (новая нода) считает из `marketplace` таблицы:
- `total_ticker_pages` — всего /t/ страниц (113 265)
- `with_ru_title` — сколько имеют ru title (СЕЙЧАС = 0, **это главная проблема**)
- `without_any_title` — без title (113 265 — все!)
- `updated_today`, `updated_week` — активность каталога

**PG Missing Titles** (новая нода) — топ-10 страниц без title из обновлённых за неделю.

**Нужно сделать в этом чате:** выполнить WF-202 v2 вручную и убедиться что PG ноды отработали.
*(Execution 933 был ДО деплоя v2 — не считается.)*

---

## Структура БД (ключевые таблицы для SEO)

```
marketplace (4 GB, 152 892 строк)
  - id, ticker (напр. NUT4001), slug_suggestion (напр. nutakucom-1000-gold-gift-card)
  - seo_data jsonb: {'ru': {title, description, h1}, 'en': {...}}
  - updated_at
  → URL формат: https://gaming-goods.ru/t/{slug_suggestion}
  → ПРОБЛЕМА: seo_data->'ru'->>'title' = NULL у ВСЕХ 113K страниц

marketplace_application (27 MB)
  - страницы категорий /marketplace/{slug}
  - seo_data jsonb с EN/RU данными

page_seo (35 MB)
  - старый формат URL: /trade/{slug} (gaming-goods.ru/trade/...)
  - с SEO данными (title, description, h1, article)
  - статус /trade/ редиректов — НЕ ПРОВЕРЯЛСЯ, нужно уточнить у Саши

ai_manager_context (48 kB)
  - id, manager_id ('seo'|'product'|'strategy'|'marketing'), context_data jsonb, updated_at
  - Используется WF-014 для хранения контекста агентов
  - ПЛАН: хранить недельные SEO-снапшоты для delta-метрик
```

---

## Главные SEO находки (результат диагностики 05.03.2026)

### 🔴 Критично: 113K страниц без title
- Все биржевые карточки `/t/` имеют `seo_data->'ru'->>'title' = NULL`
- Именно поэтому 18K+ страниц "crawled-not-indexed" в GSC
- Google заходит, не видит title, не понимает что индексировать

**Для Саши:** проверить рендерится ли `seo_data->'ru'->>'title'` в `<title>` тега на /t/ страницах.
Если нет — это баг на 1 строку кода.

### 🔴 Canonical конфликт: /t/nutaku-currency vs /marketplace/nutaku
- Оба URL показываются в GSC по запросам "nutaku"
- `/t/nutaku-currency`: поз 6.7, 1006 показов, CTR 3.2%
- `/marketplace/nutaku`: поз 7.2, 1228 показов, CTR 1.3%
- Google экспериментирует — может переключиться в любой момент

**Для Саши:** добавить `<link rel="canonical" href="/t/nutaku-currency">` на `/marketplace/nutaku`

### ℹ️ Referral = Nutaku партнёрский трафик (это норма)
- €9 022 revenue, конверсия 13.8% — это целевые пользователи с intent
- Не путать с "случайным" реферальным трафиком

---

## Что нужно сделать в новом чате

### Задача 1 — Проверить WF-202 v2 (первым делом)
1. Открыть `https://n8n-4d54.onrender.com/workflow/iI3kYbrzbobvbklo`
2. Нажать Execute workflow
3. Убедиться что в цепочке есть: `PG SEO Health` → `PG Missing Titles` → `Prepare`
4. Проверить Telegram — в сообщении должно быть `no_title=113265`
5. Если нет — дебажить PG ноды

### Задача 2 — WF-205: Еженедельный SEO аудит (главная цель)
**Что должен делать (каждый понедельник 07:00 UTC):**

```
Schedule(пн 07:00) → JWT → [GA4 + GSC + ЯМ данные]
→ PG SEO Health (те же SQL что в WF-202)
→ PG SEO Snapshot READ (читаем прошлую неделю из ai_manager_context)
→ Prepare (собираем дельту: было/стало)
→ Claude (расширенный анализ, 20-30 строк)
→ PG SEO Snapshot WRITE (сохраняем текущую неделю)
→ Telegram
```

**Уникальные фичи WF-205 vs WF-202:**
- **Delta метрики:** позиция было/стало, CTR было/стало, clicks было/стало
- **Топ движущиеся запросы:** что выросло / что упало за неделю
- **Title coverage progress:** `no_title` уменьшается или нет?
- **Canonical конфликты динамика:** решены ли прошлые?
- **Рекомендации на неделю:** 3 конкретных задачи с SQL/кодом

**Хранение снапшота:**
```sql
-- Структура ai_manager_context: id, manager_id, context_data jsonb, updated_at
-- Используем manager_id = 'seo_weekly_snapshot'
INSERT INTO ai_manager_context (manager_id, context_data, updated_at)
VALUES ('seo_weekly_snapshot', $data, now())
ON CONFLICT (manager_id) DO UPDATE 
SET context_data = $data, updated_at = now()
```
⚠️ Нужно проверить есть ли UNIQUE constraint на manager_id перед использованием ON CONFLICT.

### Задача 3 — WF-204: Indexing Bot (следующий приоритет)
**Блокер:** текущий Google Service Account имеет только `webmasters.readonly`.
Нужен scope `https://www.googleapis.com/auth/indexing`.

**Яндекс Webmaster recrawl:**
- Endpoint: `POST https://api.webmaster.yandex.net/v4/user/{userId}/hosts/{hostId}/recrawl/queue`
- userId нужно получить: `GET https://api.webmaster.yandex.net/v4/user`
- Токен OAuth есть
- Квота: 10 000 URL/день

**SQL для URL очереди:**
```sql
SELECT 'https://gaming-goods.ru/t/' || slug_suggestion as url, updated_at
FROM marketplace
WHERE slug_suggestion IS NOT NULL
  AND updated_at > now() - interval '24h'
ORDER BY updated_at DESC
LIMIT 200
```

---

## n8n паттерны (важно для отладки)

```python
# Webhook response возвращает только ПЕРВЫЙ item — используй json_agg:
"SELECT json_agg(t) as result FROM ({sql}) t"

# Активация воркфлоу через API: PATCH /activate возвращает 405
# Правильно: PUT /workflows/{id} с полным телом (name+nodes+connections+settings)

# WAF на Render блокирует PUT > ~20KB — для больших воркфлоу делай POST (создать новый)
# GET и POST на /api/v1/workflows работают без ограничений

# Параллельные ветки = race condition в n8n
# Всегда делай строго линейную цепочку: A → B → C → D
```

---

## Файлы в проекте (GitHub)

```
workflows/
  WF-201_SEO_Report.json          — ежедневный SEO отчёт
  WF-202_SEO_AI_Agent_v2.json     — SEO агент с PG health

docs/
  SEO_FULL_DIAGNOSIS_05032026.md  — полная диагностика /t/ vs /marketplace/
  SEO_AUTOMATION_QUALITY_05032026.md — фреймворк качества автоматизации
  SEO_URL_CANONICAL_DIAGNOSIS.md  — canonical конфликты

scripts/
  upgrade_wf202_v2.py             — скрипт апгрейда WF-202
```

---

## Принципы работы в этом проекте

1. **Всё в git** — каждый деплой воркфлоу → push в `KirSilVVV/n8n`
2. **Не трогаем Сашу без нужды** — ищем данные сами (PG, GSC, GA4)
3. **Линейные цепочки** — никаких параллельных веток в n8n
4. **Честная оценка** — если автоматизация чего-то не видит, явно пишем в отчёт
5. **Файлы .md** — все результаты и инструкции в markdown файлах
