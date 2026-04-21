# Задача Claude-разработчику: Apple и iTunes в «Хиты продаж» + новая секция

**Приоритет:** CRITICAL (оптовый API-покупатель kurenev делает регулярные закупки именно этих товаров)
**Дата:** 21.04.2026
**Автор:** Кир (CEO)
**Связано:** `TASK_DEV_HOMEPAGE_CS2_SKINS_21042026.md` — можно делать в одном релизе

---

## Контекст и проблема

### Оптовая выручка
Через Public API у нас регулярно закупается покупатель **kurenev** (реальная бизнес-интеграция — Sasha знает детали). **Основной ассортимент: iTunes и Apple Gift Cards**. При том что именно эти товары являются одной из топ-категорий по выручке — **на главной странице они практически невидимы**.

### Аудит текущей главной `/`

Секция «Хиты продаж» содержит 8 товаров:
1. Nutaku Gold (нам знакомый — 65% выручки)
2. Telegram Stars
3. Steam Top Up
4. PUBG Mobile
5. Minecraft Java & Bedrock
6. MS Office
7. ChatGPT Plus
8. Genshin Impact

**Apple / iTunes не представлены.** Единственное упоминание — ссылка `/t/itunes-gift-card` в секции «Предоплаченные карты», и даже она там **дублируется 2 раза** (явно по ошибке).

### Наш ассортимент по Apple

В базе `products` активно **1 401 товаров**:
- **843 продукта iTunes** (все номиналы и регионы: USD, EUR, GBP, JPY, INR, TRY и т.п.)
- **425 продукта Apple Gift Cards** (подарочные карты App Store/Apple ID)
- **55 основных Apple** (разные номиналы)
- **Apple Music, Apple TV+, Apple Arcade, Apple Fitness+** — подписки
- **Apple Final Cut Pro, Motion, MainStage** — софт для Mac (game-keys категория)

У нас **18 агрегаторных страниц `/t/...` с качественным SEO** (написано Sonnet 4.6 в апреле 2026) — но на главной они не отображаются.

---

## Что нужно сделать

### 1. Обновить секцию «Хиты продаж»

Добавить **2 карточки Apple** в топ-8 хитов:

| Позиция | Добавить | Slug | Title |
|--------:|----------|------|-------|
| 5 | Apple Gift Card | `/t/apple-gift-card` | «Apple Gift Card — подарочная карта App Store» |
| 8 | iTunes Gift Card | `/t/itunes-gift-card` | «iTunes купить подарочную карту» |

Или же **расширить секцию до 10 карточек** и добавить обе без замены — решение за Сашей в зависимости от layout.

Если в «Хиты продаж» сортировка по реальной выручке — возможно нужно просто снять захардкоженный фильтр исключающий Apple.

### 2. Удалить дубль в «Предоплаченные карты»

Сейчас ссылка `/t/itunes-gift-card?product=...` присутствует 2 раза в секции «Предоплаченные карты». Одну убрать.

### 3. Добавить новую H2-секцию: «Apple и iTunes — подарочные карты»

**Позиция:** после «Предоплаченные карты», перед «Популярные игры» (логика: тематическая близость к предоплате).

Или слить с «Предоплаченные карты» и переименовать её в «Предоплаченные карты и Apple». Решение за разработчиком исходя из текущего вида главной.

**Содержимое секции — 3 группы:**

#### Группа 1. Номиналы Apple Gift Cards (6 карточек)
- Apple €5 Gift Card → `/t/apple-5-gift-card`
- Apple €75 Gift Card → `/t/apple-75-gift-card`
- Apple Gift Card (хаб) → `/t/apple-gift-card`
- Apple Gift Cards (второй хаб) → `/t/apple-gift-cards-gift-card`
- iTunes ₹100 → `/t/itunes-100-gift-card`
- iTunes ₹500 INR → `/t/itunes-500-gift-card`

#### Группа 2. iTunes по регионам (4 карточки)
- iTunes ￥4000 JP → `/t/itunes-4000-jp-card-gift-card`
- iTunes ￥70000 JP → `/t/itunes-70000-jp-card-gift-card`
- iTunes TRY 1750 TR → `/t/itunes-other`
- iTunes Gift Card (универсальный хаб) → `/t/itunes-gift-card`

#### Группа 3. Apple подписки и софт (8 карточек)
- Apple Music → `/t/apple-music-subscription`
- Apple TV+ → `/t/apple-tv-subscription`
- Apple Arcade → `/t/apple-arcade-subscription`
- Apple Fitness+ → `/t/apple-fitness-subscription`
- Apple Fitness+ 3 месяца → `/t/apple-fitness-3-months-subscription-subscription`
- Apple Final Cut Pro → `/t/apple-final-cut-game-keys`
- Apple Motion → `/t/apple-motion-game-keys`
- Apple MainStage → `/t/apple-mainstage-game-keys`

**Всего в секции: 18 карточек**, разбитых на 3 tab/подгруппы.

---

## Технические требования

### Источник данных
Использовать тот же механизм что и для других секций главной. Просто добавить 18 slug'ов в конфиг/БД главной (структура уже известна Claude-разработчику, он работал с CS2 спекой `TASK_DEV_HOMEPAGE_CS2_SKINS_21042026.md`).

### UI/UX
- Следовать существующему стилю секций
- На мобильных — горизонтальный скролл (как остальные секции)
- Логотипы Apple и iTunes хорошо знакомы — иконки CDN уже должны быть
- Заголовок секции: `Apple и iTunes — подарочные карты и подписки`
- Подзаголовок (опционально): «Подарочные карты Apple ID, iTunes всех регионов, подписки Apple Music/TV+/Arcade/Fitness+. Моментальная доставка кода на e-mail, зачисление за 5–15 минут.»

### SEO главной
- Упомянуть Apple/iTunes в meta-description главной
- Ключевые слова для homepage: `купить apple gift card, apple подарочная карта, itunes подарочная карта, apple music подписка, apple tv купить`

### Аналитика
- Те же события `home_section_click` что для CS2 — с `section_name="apple_itunes"`, `subsection="giftcards" | "itunes_regional" | "subscriptions"`, `brand_slug="..."`

---

## Acceptance criteria

1. В «Хиты продаж» на `/` видны Apple Gift Card и iTunes Gift Card
2. В «Предоплаченные карты» только одна ссылка на iTunes (не две)
3. Есть отдельная H2-секция Apple с 18 карточек, 3 подгруппы
4. Все ссылки открываются без 404
5. Мобильная версия LCP не деградирует > 2.5s
6. События `home_section_click` с `section_name="apple_itunes"` фиксируются

---

## Что НЕ нужно делать

- **Не создавать новые `/t/` страницы** — все 18 готовы с Sonnet SEO
- **Не менять backend** — агрегаторы работают корректно
- **Не рефакторить layout главной** — только добавить секцию по паттерну

---

## Ресурсы

- Список готовых страниц: `/mnt/user-data/outputs/apple_itunes_ready.json` (18 URL с title)
- База активных products: 1 401 по Apple/iTunes (всё в БД `products` с `is_active=true`)
- Параллельная задача CS2: `TASK_DEV_HOMEPAGE_CS2_SKINS_21042026.md` (можно в одном PR)

---

## Бизнес-обоснование

1. **kurenev (оптовик через API)** — регулярный трафик, основной товар
2. **1 401 активных Apple/iTunes products** — ~15% активного каталога
3. **18 готовых SEO-страниц** высокого качества (7.0%+ CTR в среднем по сайту)
4. **0 карточек Apple в «Хиты продаж»** — прямой пропуск монетизации
5. **Конкуренты** (Steampay.com, Plati.market, OPLATY.ru) — все имеют выделенную Apple-секцию

Если за месяц после добавления секции и обновления «Хиты продаж» CTR на эти страницы вырастет хотя бы на 20-30% — это уже окупает работу.

---

## Timeline

- **До конца недели:** быстрые изменения (убрать дубль, добавить 2 карточки в «Хиты продаж»)
- **Следующая неделя:** полная секция Apple из 18 карточек
- **Через 2 недели:** A/B отчёт CTR и конверсий

Если есть вопросы — спрашивай Сашу или Кира.
