# n8n Migration Notes — Claude Friendly DB
**Дата:** 17.03.2026 | **Автор:** Claude (автоматически)

## Что изменилось

### База данных
| | Старая (deprecated) | Новая (production) |
|---|---|---|
| Host | `65.108.106.66:5432` | `65.108.141.27:5433` |
| DB | (old) | `gg_new` |
| User | — | `seo_reader` / `SeoRead2026_GG` |
| n8n cred ID | `vMUuOggCtBWX48Jg` | **требует ручного обновления в UI** |

> ⚠️ n8n API не поддерживает обновление PostgreSQL credentials через API (шифрованный формат).  
> Сашу надо попросить обновить credential `vMUuOggCtBWX48Jg` в n8n UI вручную.

### Схема данных: что переехало

| Старая таблица | Новая таблица | Изменения |
|---|---|---|
| `marketplace` | `marketplace` | SEO-данные убраны — `seo_data` jsonb больше нет |
| `marketplace.slug_suggestion` | `page_seo.url` | URL теперь в `page_seo.url` |
| `marketplace.seo_data->'ru'->>'title'` | `page_seo.title` | Прямое поле |
| `marketplace.ticker` | убран из SEO-логики | Не нужен для page_seo |
| `/marketplace/` URL | 301 → `/t/` | 130K+ редиректов, страниц нет |

### Новая схема `page_seo`
```sql
page_seo (
  id UUID,
  site_id UUID,
  url TEXT,           -- полный URL: https://gaming-goods.ru/t/nutaku-currency
  lang VARCHAR(5),    -- 'ru', 'en'
  parent_id UUID,
  title TEXT,
  description TEXT,
  h1 TEXT,
  keywords TEXT,
  image TEXT,
  alt TEXT,
  article TEXT,
  faq JSONB,
  completion_percent INT
)
-- UNIQUE (site_id, url, lang)
```

### Новая схема `products` (новое имя таблицы)
```sql
products (slug, name, category, brand, is_active, original_name, translations)
-- Доступ только к этим колонкам у seo_reader
```

### Статистика на 17.03.2026
- `page_seo` всего: ~43,540 записей
- Страниц `/t/` с ru title: ~47,500 (из ~48,000 бренд-категорий)
- `marketplace_order` — таблица сохранилась, структура та же

## Что было изменено в n8n

### WF-202: SEO AI Agent v2
**Файл:** `workflows/WF-202_SEO_AI_Agent_v2.json`

| Нода | Старый SQL | Новый SQL |
|---|---|---|
| PG SEO Health | `SELECT ... FROM marketplace WHERE slug_suggestion IS NOT NULL` | `SELECT COUNT(*) ... FROM page_seo WHERE lang='ru' AND url LIKE '%/t/%'` |
| PG Missing Titles | `SELECT slug_suggestion, ticker, seo_data->'ru'->>'title' FROM marketplace` | `SELECT url, title, updated_at FROM page_seo WHERE title IS NULL` |
| Prepare (Code) | Полностью переписан — убраны все `slug_suggestion`, `ticker`, `/marketplace/` | Новая логика на `page_seo.url`, `page_seo.title` |

### WF-205: Weekly SEO Audit
**Файл:** `workflows/WF-205_Weekly_SEO_Audit.json`

| Нода | Изменение |
|---|---|
| PG SEO Health | То же что WF-202 |
| PG Missing Titles | То же что WF-202 |
| PG Snapshot READ | Без изменений (`ai_manager_context` не менялась) |
| Prepare | `r.slug_suggestion` → `r.url`; `pgHealth` parsing fix |

### WF-201: GSC + GA4 Data Fetch
Без изменений — нет PG-нод.

## Что НЕ сделано (требует действий)

### 🔴 Обязательно — Саша
1. **Обновить credential `vMUuOggCtBWX48Jg`** в n8n UI:
   - `Settings → Credentials → "Postgres account"`
   - Host: `65.108.141.27`, Port: `5433`, DB: `gg_new`, User: `seo_reader`, Pass: `SeoRead2026_GG`
   - SSL: disable

2. **Дать write-доступ к `page_seo`** для WF-301 (SEO content generation):
   - Нужен отдельный user с `INSERT/UPDATE ON page_seo`
   - Или API endpoint `PATCH /api/v1/seo` (предпочтительно)

### 🟡 Запланировано
- WF-301: SEO Content Generator (запись title/description в `page_seo`)
- WF-204: Яндекс recrawl (обновлён на `page_seo` URL-based)
- Обновить pg-test-v2 webhook: проверить что работает с новым credential

## URL-архитектура (важно для SEO-автоматики)

```
gaming-goods.ru/t/{brand-slug}-{category-slug}
  → page_seo.url = 'https://gaming-goods.ru/t/{brand-slug}-{category-slug}'
  → page_seo.lang = 'ru'
  → page_seo.title = "{Brand} купить {category} | Гейминг Гудс"

/marketplace/* → 301 redirect → /t/*
Canonical /t/ страниц — сами на себя
```

## Типичные ложные срабатывания (для будущих аудитов)
- "113K страниц без title" — это СТАРЫЕ данные из `marketplace.seo_data`. Реальных страниц ~48K в `page_seo`
- "Пустой title в GSC" — инструмент не рендерит JS. SSR всегда отдаёт title
- "Canonical конфликт /marketplace/" — страниц нет, только 301
