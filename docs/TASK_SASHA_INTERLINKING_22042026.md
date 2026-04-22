# Задача Саше: внутренняя перелинковка для SEO-веса и скорости индексации

**Приоритет:** HIGH (самый большой SEO-impact бесплатно)
**Срок:** 1 неделя
**Дата:** 22.04.2026
**Автор:** Кир (CEO)

---

## Проблема

Сейчас каждая страница `/t/{slug}` существует изолированно. Яндекс/Google не понимают связей между товарами одного бренда и категориями. Это критически снижает:

1. **Crawl depth** — поисковый бот сканирует страницу, не видит исходящих ссылок на смежные → уходит
2. **Передачу PageRank** — страницы с большим трафиком (Nutaku, Steam Top Up) не делятся весом с хвостовыми
3. **Индексацию хвоста** — длинный хвост (Game Keys, редкие Gift Cards) индексируется медленно, потому что бот до них доходит не прямо с главной, а случайно

На 22.04.2026 у нас **3 598 GOOD страниц** в БД, и дневной прогон SEO добавляет ещё 150-400. Без перелинковки половина из них так и останется в песочнице.

## Что уже работает (не ломать)

- Главная страница с 11 H2-секциями
- Footer с базовыми ссылками
- Навигационное меню сверху
- Breadcrumbs на карточках товара

---

## Что нужно добавить

### Блок 1. «Похожие товары» на странице карточки товара

**Где:** каждая карточка товара (`/p/{slug}` и `/t/{slug}?product={uuid}`)

**Что показывать:** 5-8 карточек товаров по логике:
1. **Приоритет: тот же бренд** (3-4 карточки) — например для `paypal-wallet-50-usd-top-up-us` показать другие номиналы PayPal Wallet
2. **Потом: та же категория** (2-3 карточки) — другие Currency / Gift Card / Game Keys
3. **В конце: связанные по price-range** (1-2 карточки) — товары ±30% от текущей цены

**Реализация:**
- Запрос в БД с несколькими ORDER BY (brand_match DESC, category_match DESC, price_diff ASC)
- Ограничить LIMIT 8
- Кешировать на 1 час в Redis по ключу `similar:{product_id}`

**SSR:** блок должен быть в HTML до гидратации (критично для SEO-бота).

**Пример ссылок в блоке:**
```html
<section class="similar-products">
  <h2>Похожие товары</h2>
  <a href="/p/paypal-wallet-100-usd-top-up-us">PayPal Wallet $100 Top Up US</a>
  <a href="/p/paypal-wallet-25-usd-top-up-us">PayPal Wallet $25 Top Up US</a>
  <a href="/p/paypal-wallet-200-usd-top-up-us">PayPal Wallet $200 Top Up US</a>
  ...
</section>
```

### Блок 2. «Смотреть также» на `/t/` агрегаторных страницах

**Где:** каждая `/t/{slug}` страница

**Что показывать:** 5 ссылок на смежные агрегаторы того же домена (gift card / currency / subscription / game keys).

**Логика матчинга:**
- Разбираем slug текущей страницы: `steam-wallet-usd-gift-card` → brand=`steam`, type=`gift-card`
- Ищем другие `/t/` URL с тем же brand: `steam-top-up`, `steam-currency`, `steam-game-keys`
- Ищем смежные по категории: `itunes-gift-card`, `paypal-wallet-gift-card`, `apple-gift-card`
- Вручную настроенные related для топ-20 брендов (Nutaku, Steam, Apple, PayPal, CS2) — отдельная таблица `seo_related` (brand_slug, related_slugs[])

**Реализация:**
- Таблица `seo_related` (brand_slug PRIMARY KEY, related_slugs TEXT[]) — заполняем один раз вручную для топ-20 hub'ов, для остальных генерация на лету
- Для остальных — простой SQL-запрос с SIMILARITY по slug
- Кеш 24 часа

**Пример для `/t/nutaku-currency`:**
```
Смотреть также:
- Telegram Stars
- Steam Top Up  
- Roblox Robux
- Standoff 2 Gold
- PUBG Mobile UC
```

### Блок 3. Расширенный футер: «Популярные категории»

**Где:** футер всех страниц сайта

**Что показывать:** 3 колонки по 10 ссылок = **30 ссылок на топовые hub-страницы**:

**Колонка 1 — Игровые валюты:**
- Nutaku Gold, Telegram Stars, Robux, V-Bucks, Genesis Crystals, PUBG UC, Standoff 2 Gold, FIFA Points, Apex Coins, Valorant Points

**Колонка 2 — Подарочные карты:**
- Apple Gift Card, iTunes Gift Card, Steam Wallet, PayPal Wallet, Spotify, Netflix, PlayStation Store, Xbox Gift Card, Google Play, Amazon

**Колонка 3 — Подписки и Keys:**
- Xbox Game Pass, PS Plus, Apple Music, Apple TV+, Discord Nitro, ChatGPT Plus, Minecraft, GTA V, Counter-Strike 2, Fortnite

**Реализация:** 
- Хардкод в SSR-шаблоне футера (30 ссылок статически)
- Если меняется список — обновить в коде, не в БД

**ВАЖНО:** ссылки **не nofollow**, обычные `<a href>`. Яндекс должен их обойти.

---

## Технические требования

### SSR-рендеринг

**Все три блока должны быть в HTML до гидратации** (не генерироваться JavaScript'ом на клиенте). Это критично — Яндекс-бот и Google-бот не всегда выполняют JS на стадии первичной индексации.

Проверить через:
```bash
curl https://gaming-goods.ru/t/nutaku-currency | grep -c "similar-products\|related-aggregators"
# должно вернуть >=2
```

### Производительность

- Запрос «похожих товаров» не должен добавлять >50ms к TTFB
- Redis-кеш обязателен
- На 10K концурентных запросов — не более 100 ms avg latency на рендер блока

### Анимация и UI

- Десктоп: horizontal scroll или 4-в-ряд grid (не ломать существующий дизайн карточек)
- Мобильный: horizontal scroll с snap
- Lazy loading для картинок

---

## Acceptance criteria

1. ✅ На странице `/p/paypal-wallet-50-usd-top-up-us` виден блок «Похожие товары» с 5-8 ссылками на другие PayPal Wallet номиналы
2. ✅ На странице `/t/nutaku-currency` виден блок «Смотреть также» с 5 ссылками на Telegram Stars, Steam, Roblox и др.
3. ✅ В футере любой страницы сайта видны 30 ссылок (3 колонки по 10) на топовые hub'ы
4. ✅ Все ссылки — обычные `<a href>`, не JS, не nofollow
5. ✅ Блоки присутствуют в SSR (видны в `curl` output)
6. ✅ TTFB не деградировал >50ms
7. ✅ Мобильный layout не сломан
8. ✅ В GSC (Google Search Console) через 2 недели — рост «Impressions / Pages discovered via crawl» на 20%+

---

## SQL для «похожих товаров» (черновик)

```sql
-- Для данного product_id найти 8 похожих
WITH current_product AS (
  SELECT brand, category, price_from_cents AS price
  FROM products WHERE id = $1 LIMIT 1
)
SELECT p.slug, p.name, p.brand, p.category, p.price_from_cents
FROM products p, current_product cp
WHERE p.is_active = true 
  AND p.id != $1
ORDER BY 
  CASE WHEN p.brand = cp.brand THEN 0 ELSE 1 END,
  CASE WHEN p.category = cp.category THEN 0 ELSE 1 END,
  ABS(p.price_from_cents - cp.price) / NULLIF(cp.price, 0)
LIMIT 8;
```

## Таблица `seo_related` (новая)

```sql
CREATE TABLE seo_related (
  slug TEXT PRIMARY KEY,  -- например 'nutaku-currency'
  related_slugs TEXT[],    -- ['telegram-stars', 'steam-top-up', 'roblox-currency', ...]
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- Инициализация для топ-20 брендов (я подготовлю CSV)
INSERT INTO seo_related (slug, related_slugs) VALUES
('nutaku-currency', ARRAY['telegram-stars', 'steam-top-up', 'roblox-currency', 'standoff-2-gold', 'pubg-mobile-uc']),
('apple-gift-card', ARRAY['itunes-gift-card', 'apple-music-subscription', 'apple-tv-subscription', 'paypal-wallet-top-up', 'steam-wallet']),
...;
```

Я (Claude) могу подготовить полный INSERT для 20 топ-брендов отдельным файлом когда пришло время.

---

## Ожидаемый impact

| Метрика | Сейчас | Через 2-3 недели |
|---------|-------:|------------------:|
| Скорость индексации новых страниц | 5-10 дней | **2-3 дня** |
| Кол-во страниц в поиске Яндекса | 35 938 | **40 000+** |
| Показов/неделю | 1 650 | **2 500+** |
| Кликов/неделю | 116 | **200+** |

**Это самая дешёвая мера для роста SEO** — не требует генерации контента, не требует бюджета на Anthropic. Только backend.

---

## Связанные задачи

- `TASK_SASHA_PAYPAL_AGGREGATOR_21042026.md` — fix slug-matching для PayPal Top Up (может задействовать тот же механизм)
- `GROWTH_STRATEGY_22042026.md` — общая стратегия куда вписывается эта задача
- `TASK_DEV_HOMEPAGE_CS2_SKINS_21042026.md` + `TASK_DEV_HOMEPAGE_APPLE_ITUNES_21042026.md` — главная (не затрагивает backend, можно параллельно)

Пиши если нужно уточнить детали или посмотреть примеры реализации у конкурентов.
