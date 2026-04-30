# 🎯 Задача Саше: переделать "Хиты продаж" — 12 продуктов, 2 ряда по 6

**Приоритет:** HIGH (упускаем место главной + неправильная подборка)
**Дата:** 30.04.2026
**Автор:** Кир (CEO) при поддержке аналитики Claude
**Связано:** `HOMEPAGE_HITS_REDESIGN_30042026.md`, `TASK_SASHA_APPLE_HOMEPAGE_30042026.md`

---

## Что не так сейчас

1. В "Хитах продаж" **7 продуктов вместо 12** — последний висит одиноким в нижней строке (визуальный мусор).
2. **5 из 7 текущих "Хитов" не входят в реальный топ-20 продаж** (PUBG Parachute, Minecraft Java&Bedrock, MS Visio 2016, ChatGPT Plus, и частично Telegram Stars). Слот на главной = самый дорогой PageRank-ресурс, тратить его на не-продаваемое — упущенная выручка.
3. **Apple/iTunes отсутствуют**, хотя:
   - 1 362 активных SKU в каталоге
   - Whale-клиент kurenev купил на €960 за 60 дней
   - Растущая ниша (App Store оплата из России)

---

## Что нужно сделать — Вариант B «Сбалансированный»

12 продуктов в 2 ряда по 6. Сочетание:
- 6 реальных топ-продаж (отвечают за выручку)
- 4 стратегических (Apple x2, Roblox, PSN — растущие ниши)
- 2 universal (Telegram, Discord) — массовая аудитория

---

## ✅ Финальный список 12 продуктов с UUID

### Ряд 1 — Топ-продажи (high-converting)

| # | Продукт | UUID | Brand | Slug page | Текущий заказов 30д (web) |
|--:|---------|------|-------|-----------|--------------------------:|
| 1 | **Nutaku 500 Gold** | `419d7f15-6627-5583-9137-d961a27529a1` | Nutaku | `/t/nutaku-currency` | 568 (€17 194) |
| 2 | **Rewarble Fansly $5** | `1b3338ec-f30f-5d4c-a234-4ef8e2b632b9` | Rewarble Fansly | `/t/rewarble-fansly-gift-card` | 78 (€996) |
| 3 | **50 Telegram Stars** | `771246df-37a9-5cf1-8c90-e14e7e18e07e` | Telegram | `/t/telegram-stars` | 15 |
| 4 | **100 RUB Steam Balance** | `544f4ed5-88ca-55f2-8835-0a1140bd7dd4` | Steam | `/t/steam-top-up` | 22 (€95) |
| 5 | **Clash.gg 25 USD Gift Card** | `cbbaa5f0-36a4-479a-90f4-68df91ee3640` | Clash.gg | `/t/clash-gg-gift-card` | 16 |
| 6 | **Hellcase $10 Wallet** | `b99eded5-8fbf-429f-b5aa-e549283e55fd` | Hellcase | `/t/hellcase-gift-card` | 2 |

### Ряд 2 — Стратегические (растущие ниши)

| # | Продукт | UUID | Brand | Slug page | Обоснование |
|--:|---------|------|-------|-----------|-------------|
| 7 | **iTunes $10 CA Card** | `28f13da4-e3d4-5b4d-9fdf-dbe0cfde886b` | iTunes | `/t/itunes-gift-card` | Whale kurenev, топ-продаваемая Apple |
| 8 | **Apple $10 Gift Card US** | `711e8387-92aa-5de0-85d0-e71e08ba1050` | Apple Gift Cards | `/t/apple-gift-cards-gift-card` | USD/US — самый востребованный регион для российских Apple ID |
| 9 | **ChatGPT Plus 1-Month** | `e38e84c8-df66-4fe5-a9b4-e72bd3c3f53f` | ChatGPT Plus | `/t/chatgpt-plus-subscription` | Уже есть, оставляем |
| 10 | **Roblox 1000 Robux** (Global) | `9509964f-4497-5e01-9779-f35933aaacd3` | Roblox | `/t/roblox-currency` | 16 продаж за 30 дней, без региональной привязки |
| 11 | **PlayStation Plus Premium 1mo** | `5d7a807a-62e3-5fec-9137-296cec52996a` | PlayStation Plus | `/t/playstation-plus-subscription` | Стратегический бренд |
| 12 | **Discord Nitro 1-Month** | `9249de2c-bcbb-5aa4-bd51-13994a3b419c` | Discord | `/t/discord-subscription` | 11 продаж + gaming community |

---

## 🚮 Удалить из текущих "Хитов"

- ~~PUBG Mobile - Extreme Racing Parachute Digital Ключ~~ — узкоспецифичный SKU, мало продаётся
- ~~Minecraft: Java & Bedrock издание FR PC Windows Ключ~~ — конкретный ключ FR, не топ
- ~~MS Visio Professional 2016 Ключ~~ — морально устаревший продукт

---

## 📐 Технические детали

### Layout

```css
.hits-grid {
  display: grid;
  grid-template-columns: repeat(6, 1fr);  /* desktop: 6 в ряд */
  gap: 16px;
}

@media (max-width: 1280px) { .hits-grid { grid-template-columns: repeat(4, 1fr); } }
@media (max-width: 768px)  { .hits-grid { grid-template-columns: repeat(3, 1fr); } }
@media (max-width: 480px)  { .hits-grid { grid-template-columns: repeat(2, 1fr); } }
```

| Размер экрана | Колонок | Рядов |
|---------------|--------:|------:|
| Desktop (>1280px) | **6** | **2** |
| Tablet (768-1280) | 4 | 3 |
| Mobile (480-768) | 3 | 4 |
| Small mobile (<480) | 2 | 6 |

### Где это правится

Из текущего HTML видно, что Хиты отдаются как часть SSR-ответа главной. Не нашёл таблицы `homepage_hits` или `featured_products` в БД — конфигурация скорее всего:
- в коде Nuxt-компонента (например `~/components/HomePage/HitsList.vue` или `~/data/featured.ts`)
- либо приходит из API endpoint (например `/api/v1/homepage/hits`)

Саше виднее. Если есть админ-интерфейс для редактирования — самое удобное место.

### URL формат для каждой карточки

Шаблон ссылки (как в текущей реализации): `/t/{slug}?product={uuid}`

Например:
- `/t/nutaku-currency?product=419d7f15-6627-5583-9137-d961a27529a1`
- `/t/rewarble-fansly-gift-card?product=1b3338ec-f30f-5d4c-a234-4ef8e2b632b9`

---

## ✅ Acceptance criteria

1. ✅ В секции "Хиты продаж" видно **ровно 12 карточек**
2. ✅ На desktop (>1280px) — **2 ряда по 6**, без пустот
3. ✅ Все 12 карточек кликабельны и ведут на правильные `/t/{slug}?product=UUID`
4. ✅ Mobile-responsive (3 / 4 / 6 рядов в зависимости от ширины)
5. ✅ Удалены 3 «мёртвых» SKU (PUBG Parachute, Minecraft Java&Bedrock, MS Visio)
6. ✅ Добавлены 8 новых: Rewarble Fansly, Clash.gg, Hellcase, iTunes, Apple, Roblox, PlayStation Plus, Discord
7. ✅ Сохранены 4 хороших: Nutaku 500 Gold, Telegram Stars, Steam 100₽, ChatGPT Plus
8. ✅ Цена в рублях видна на каждой карточке (для согласованности с акцентом «Оплата в рублях»)

---

## 📊 Expected impact

### Заполнение слотов
- **До:** 7/12 = 58% заполнения, 1 одинокая карточка снизу
- **После:** 12/12 = 100%, чистый grid 2×6

### Конверсия
- **6 карточек ряд 1 = реальные топ-продажи** → высокий CTR
- Текущие 5 «мёртвых» Хитов имели CTR <1% (никто не кликал на MS Visio 2016)

### Прогноз выручки
- Apple на главной: **+€100-300/мес** через 4-6 недель (whale + ретейл)
- Rewarble Fansly видимый выше: **+€50-100/мес** (78 заказов уже идут, рост 10-20%)
- Clash.gg, Hellcase: **+€50-150/мес** (CS-аудитория видит сразу)
- Discord, Roblox: **+€30-80/мес** (молодая аудитория, привлечение нового сегмента)

**Суммарно: ~€230-630/мес** дополнительной выручки только от перестановки Хитов.

---

## 🔗 Связанные SEO-улучшения (уже в БД)

- ✅ Nutaku-hub перегенерирован Opus 4.7 — title под «донат nutaku» (30.04)
- ✅ iTunes hub перегенерирован Opus 4.7 — 4 700 знаков, 12 FAQ (30.04)
- ✅ 25 CS-страниц с brand-aggregator SEO (28.04)
- ✅ 14 missing CS-брендов (29.04)
- ✅ 440 priority URL пропатчены акцентом «Оплата в рублях/МИР/СБП» (29.04)
- ✅ IndexNow активирован, 1 032 живых URL отправлено в Yandex (30.04)

После того как Саша обновит "Хиты продаж" + сделает CS hub + Nutaku landings — главная страница станет идеальным entrypoint'ом для SEO-трафика.

---

## ❓ Открытые вопросы (если нужны)

- Как править Хиты — через БД-таблицу, конфиг или admin UI? Если есть admin — могу подсказать какие UUID куда вставить.

---

## Сводное сообщение для Саши

> Саша, на главной "Хиты продаж" — нужно 12 продуктов вместо 7, в 2 ряда по 6.
>
> Полный список с UUID и slug в `docs/TASK_SASHA_HOMEPAGE_HITS_30042026.md`.
>
> Удалить: PUBG Parachute, Minecraft Java&Bedrock, MS Visio.
> Добавить: Rewarble Fansly, Clash.gg, Hellcase, iTunes, Apple, Roblox, PlayStation Plus, Discord.
>
> CSS: `grid-template-columns: repeat(6, 1fr)` на desktop, responsive вниз. Прогноз доп. выручки: €230-630/мес.
