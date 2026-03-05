# SEO: Полная диагностика gaming-goods.ru
**05.03.2026 | Данные: GSC + GA4 + PostgreSQL**

---

## 1. Референс: Referral канал — это нормально

**Ты прав.** Referral = Nutaku партнёрский трафик с UTM-метками.
Это не случайный реферальный трафик — это целевой платный канал (партнёрство).
Сравнивать его с органикой некорректно — разные каналы с разными целями.

| Канал | Сессии | Конверсий | Revenue | Conv rate |
|-------|--------|-----------|---------|-----------|
| Referral (Nutaku) | 2 344 | 324 | €9 022 | **13.8%** |
| Organic Search | 2 633 | 84 | €1 380 | 3.2% |
| Direct | 2 588 | 122 | €1 435 | 4.7% |

Конверсия Nutaku-трафика 13.8% — **нормально**, это целевые пользователи с intent.
Органика 3.2% — низкая конверсия указывает на проблемы с посадочными страницами.

---

## 2. /t/ vs /marketplace/ — GSC данные

| URL тип | Страниц в GSC | Кликов | Показов | CTR avg |
|---------|--------------|--------|---------|---------|
| `/t/` (биржа) | **2** из 113K | 47 | 1 148 | 6.9% |
| `/marketplace/` | **16** | 483 | 8 560 | 8.9% |

### Nutaku — конкретный конфликт

| URL | Клики | Показов | Позиция | CTR |
|-----|-------|---------|---------|-----|
| `/t/nutaku-currency` ✅ нужный | 32 | 1 006 | **6.7** | 3.2% |
| `/marketplace/nutaku` ⚠️ конкурент | 16 | 1 228 | 7.2 | 1.3% |

**Что происходит:** оба URL показываются в Google по запросам "nutaku currency", "нутаку валюта".
Google сам выбирает какой показывать — и пока выбирает `/t/` (поз 6.7 лучше чем 7.2).
Но `/marketplace/nutaku` набирает **больше показов** — Google тестирует оба варианта.

**Риск:** в любой момент Google может переключиться на `/marketplace/` как "более богатую" страницу.
Потеря `/t/nutaku-currency` из топа = -32 клика/мес = -3-4 продажи.

---

## 3. Главная находка из базы данных

### Что такое /t/ страницы — теперь точно известно

```sql
marketplace таблица:
  - 152 892 строк
  - ticker: 113 265 заполнено (NUT4001, NUT4002...)  ← это /t/ страницы
  - slug_suggestion: 123 098 заполнено              ← URL вида /t/{slug}
  - seo_data->>'title': 0 заполнено                 ← ВСЕ NULL
```

**🚨 КРИТИЧНО: 113 265 биржевых страниц `/t/` не имеют SEO title.**

Когда Google заходит на `/t/nutaku-currency` — он видит страницу без `<title>`.
Поэтому:
- Google сам генерирует title из контента → слабый, нерелевантный
- Low CTR (3.2%) при позиции 6.7 — люди не кликают потому что title невнятный
- 18K+ страниц "crawled not indexed" — Google не понимает что индексировать

### Структура URL `/t/` страниц

```
/t/{marketplace.slug_suggestion}
Пример: /t/nutaku-currency → marketplace WHERE slug_suggestion = 'nutaku-currency' (?)
         /t/nutakucom-1000-gold-gift-card → ticker NUT4002
```

Nutaku-специфично в БД:
- `NUT4001` → `nutakucom-2000-gold-gift-card`
- `NUT4002` → `nutakucom-1000-gold-gift-card`
- `NUT4003` → `nutakucom-500-gold-gift-card`
- `NUT4004` → `nutakucom-3000-gold-gift-card`
- `NUT4005` → `nutakucom-10000-gold-gift-card`

Все 5 Nutaku позиций имеют `seo_data` (EN+RU title+description+h1) — **но это данные для /marketplace/ карточек**.
Для `/t/` страниц — отдельного SEO контента нет.

### page_seo таблица — третий URL формат!

```
page_seo хранит URLs типа /trade/{slug}  (старый формат)
Примеры:
  /trade/anno-2205-game-key/           title: "Купить Anno 2205 ключ — цена в Гейминг Гудс"
  /trade/the-forest-game-keys/         title: "Купить ключ для игры The Forest – Гейминг Гудс"
  /trade/stalker-2.../                 ...
```

**Три URL формата в системе:**
1. `/trade/{slug}` — старый (в page_seo таблице, с SEO данными)
2. `/t/{slug}` — биржевая карточка (в marketplace, без SEO)
3. `/marketplace/{slug}` — конструктор (в marketplace, с SEO)

Есть ли `/trade/` → `/t/` редирект? Нужно проверить.

---

## 4. Что делать прямо сейчас (без Саши)

### WF-204 Indexing Bot — план

**Источник URL для индексации:**
```sql
SELECT 'https://gaming-goods.ru/t/' || slug_suggestion as url, updated_at
FROM marketplace
WHERE slug_suggestion IS NOT NULL
  AND updated_at > now() - interval '24h'
ORDER BY updated_at DESC
LIMIT 200
```

**113 265 страниц × 200/день Google Indexing API = ~566 дней**

Это слишком долго. Нужна **приоритизация**:
```sql
-- Только страницы которые имеют SEO data И активные лоты
WHERE slug_suggestion IS NOT NULL
  AND seo_data IS NOT NULL
  AND seo_data != '{}'
ORDER BY updated_at DESC
LIMIT 200
```

**Google Indexing API** — нужен отдельный Service Account с правами:
- `https://www.googleapis.com/auth/indexing`
- Верификация через Google Search Console (добавить SA как owner)

Текущий SA (`gaming-goods-seo@...`) имеет права только `webmasters.readonly`.
**Нужен новый SA** или расширение прав текущего.

**Яндекс Webmaster recrawl:**
Endpoint: `POST https://api.webmaster.yandex.net/v4/user/{userId}/hosts/{hostId}/recrawl/queue`
Токен: уже есть (y0__xC93uTIBhj4yz...)
Квота: 10 000 URL/день

---

## 5. Срочные задачи для Саши (минимум)

### Задача 1 — Canonical на /marketplace/nutaku (10 минут)
```html
<!-- В шаблон /marketplace/nutaku добавить: -->
<link rel="canonical" href="https://gaming-goods.ru/t/nutaku-currency" />
```
Это скажет Google — продвигай `/t/`, `/marketplace/` — это дополнительная страница.

### Задача 2 — SEO title для /t/ страниц (из seo_data)
Сейчас `/t/` страницы рендерят `<title>` из... чего? Из `marketplace.seo_data`?
Если да — title заполнен только для EN/RU языков, на gaming-goods.ru нужно ru:
```
marketplace.seo_data->'ru'->>'title'
```
Для Nutaku это уже есть: `"Nutaku.com 1000 золотых подарочных карт"`

**Нужно убедиться что ru-title рендерится в `<title>` тега на /t/ странице.**
Если рендерится — CTR должен вырасти. Если нет — это баг.

---

## 6. Что Google реально видит на /t/nutaku-currency

Чтобы проверить что Google видит (не браузер — именно Googlebot):
```
https://search.google.com/search-console → URL Inspection →
https://gaming-goods.ru/t/nutaku-currency → Request Indexing
```

Это покажет:
- Какой canonical Google установил сам (canonical declared vs canonical selected)
- Есть ли `<title>` на странице по мнению Googlebot
- Есть ли structured data

---

## 7. Итог

| Проблема | Серьёзность | Решение | Кто |
|----------|-------------|---------|-----|
| `/t/nutaku-currency` конкурирует с `/marketplace/nutaku` | 🔴 Срочно | canonical на /marketplace/ | Саша |
| 113K `/t/` страниц без `<title>` тега | 🔴 Критично | рендеринг `seo_data->'ru'->>'title'` | Саша |
| WF-204 Indexing Bot — нет прав на Indexing API | 🟡 Важно | создать SA с правами indexing | Проверяем |
| Яндекс Webmaster recrawl endpoint | 🟡 Важно | настроить через OAuth | WF-204 |
| `/trade/` старые URL — статус неизвестен | 🔵 Проверить | редирект на `/t/`? | Саша |
