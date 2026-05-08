# Задача Саше: Apple SEO применить + n8n API key + GRANT page_seo

**Дата:** 08.05.2026
**Приоритет:** P0 (n8n API key) + P1 (Apple SEO)
**Ожидаемое время:** 15 минут всего

---

## 🚨 P0 — n8n API key истёк сегодня

n8n API key для меня (Claude) действовал до `1778187600` = **7 мая 2026 23:00 UTC**. Сегодня 8 мая — **истёк**. Все API-вызовы отдают 401 unauthorized.

**Это было в директорском отчёте 4 мая как Risk #1 на горизонте 30 дней — материализовалось ровно в срок.**

### Что нужно от тебя

1. Зайти в n8n → Settings → API → Create new API key
2. Срок действия — **на 6 месяцев** (до ноября 2026), не на год (короче ротация = меньше риск утечки)
3. Прислать новый ключ через приватный канал (Telegram личным, не в общий чат)
4. Я обновлю мою память автоматически и продолжу работу

**Без этого ключа я не могу:**
- Создавать новые workflows
- Деплоить изменения SEO-генератора
- Делать backup/rollback workflows перед изменениями

### Альтернатива (если не успеваешь)

Если твоя бэклог-неделя занята — **можно отложить новый ключ на 14 мая**. На текущей неделе для работы с SEO `page_seo` мне нужно только **GRANT** (см. P1 ниже).

---

## P1 — GRANT write-доступа на page_seo для n8n_reader

Аналогично закрытой задаче GG-91 (которая дала права на `seo_landings`). Сейчас на `page_seo` у `n8n_reader` только SELECT. Нужны UPDATE + INSERT.

### SQL команда

```sql
GRANT SELECT, INSERT, UPDATE ON page_seo TO n8n_reader;
```

DELETE намеренно не выдаём — page_seo напрямую не удаляется (только `is_active = false` через UPDATE).

### Зачем это нужно

После этого я смогу:
- Применять Apple SEO в `page_seo` сам, без передачи SQL-патчей тебе
- Делать апдейты для других hub-страниц (CS hub уже на `seo_landings`, но 99% всех `/t/*` страниц живут в `page_seo`)
- Работать как WF-301 SEO Generator работает — он использует кред `vMUuOggCtBWX48Jg` который имеет write на `page_seo`

После этой задачи **n8n_reader = read+write на seo_landings + page_seo** — два главных SEO-стола.

---

## P1 — Apple SEO применить (4 страницы)

В `/mnt/user-data/outputs/apple_seo_update.sql` готовый SQL-патч.

### Что в нём

4 UPDATE statement в одной транзакции (BEGIN/COMMIT) для:

| URL | Old article | New article (Opus 4.7) | Cost |
|-----|------------:|-----------------------:|-----:|
| `/t/apple-gift-cards-gift-card` | 774 | **6 083** | $0.35 |
| `/t/apple-gift-card` | 773 | **5 334** | $0.32 |
| `/t/apple-music-subscription` | 981 | **10 452** | $0.46 |
| `/t/apple-tv-subscription` | 858 | **9 343** | $0.44 |

**Total cost: $1.56**. Все title/desc/h1/article/faq/keywords переписаны под российскую аудиторию: оплата картой МИР, СБП, регионы Apple ID, конкретная боль (Apple отключил прямую оплату для РФ в 2022).

### Применение (один из вариантов)

**Вариант A (рекомендуется): через psql напрямую**
```bash
psql -h 65.108.141.27 -p 5433 -U app_user -d gg_new -f /path/to/apple_seo_update.sql
```

Verification SQL уже встроен — выведет четыре строки с длинами полей.

**Вариант B: после P1-GRANT — я сам применю.** Скажи когда GRANT done, я в течение 5 минут применю + запущу IndexNow + Yandex Webmaster recrawl.

### itunes-gift-card

Не трогаем — там уже отличный контент с прошлого Opus-апдейта (30.04, article 4 700 знаков, FAQ 12, есть упоминания МИР/СБП).

---

## Сводка

| Задача | Time | Дедлайн |
|--------|------|---------|
| Новый n8n API key (6мес) | 5 мин | до 14 мая |
| GRANT на page_seo | 1 мин | до 9 мая |
| Apply Apple SEO (или отдать мне после GRANT) | 5 мин | до 9 мая |

После этого я **сам**:
1. Запущу IndexNow для всех 4 URL
2. Подам Yandex Webmaster Recrawl
3. Через 7 дней (15 мая) — отчёт по позициям и показам

---

## Связанные файлы

- `/mnt/user-data/outputs/apple_seo_update.sql` — готовый SQL (51 KB)
- `/mnt/user-data/outputs/apple_seo_new.json` — backup всех 4 SEO пакетов (84 KB)
- `apple_seo_rollback_pre_update_08052026.json` — backup текущего состояния (создаю если потребуется)
- GitHub: `docs/TASK_SASHA_APPLE_SEO_GRANT_08052026.md` (этот файл)
