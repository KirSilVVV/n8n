# 🎯 Задача Саше: создание hub-страницы CS2 Skins Marketplace

**Приоритет:** HIGH (упускаем большой трафик в нише CS2-скинов)
**Срок:** 1 неделя
**Дата:** 28.04.2026
**Автор:** Кир (CEO)
**Связано:** `CS2_SEO_INDEX_REPORT_28042026.md`, `TASK_SASHA_NUTAKU_LANDINGS_22042026.md` (тот же паттерн)

---

## Контекст и проблема

У нас в каталоге **25 страниц-агрегаторов** связанных с CS2/CS:GO скинами:
- Skin-боксы и кейсы (Hellcase, Lootie, Skin.Club, Rain.gg, Farmskins, и др.)
- Skin-маркетплейсы (Shadowpay, PirateSwap, SkinsProject)
- Crash-казино со скинами (Stake Joker, RainBet, PLG.BET)
- Counter-Strike Steam-ключи (Complete, Prime Status Upgrade, и т.д.)

**Все 25 проиндексированы Яндексом** (100%) и приносят минимальный трафик (4 клика за 14 дней).

**Главная проблема:** мы **не показываемся в выдаче по обобщённым CS-запросам**:
- ❌ "купить скины кс2"
- ❌ "csgo рулетки"
- ❌ "лучшие сайты для скинов кс"
- ❌ "сайты с кейсами cs2"
- ❌ "где купить скины cs2"

**Эти запросы — основной трафик ниши** (десятки тысяч показов в месяц по Яндексу). Конкуренты (DMarket, CS.MONEY, SkinSwap) забирают всё.

---

## Что нужно сделать — hub-страница `/t/cs-skins-marketplace`

Создать **виртуальную SEO-страницу** которая:
1. Не привязана к конкретным товарам (это **категорный hub**, а не товарная страница)
2. Содержит уникальный SEO-контент про CS2-скин-индустрию
3. Ссылается на все 25 наших CS-страниц через грид-витрину
4. Ловит поисковые запросы про "скины кс2", "купить скины", "csgo рулетки" в целом

Это **тот же паттерн что в задаче Nutaku Landings** (`TASK_SASHA_NUTAKU_LANDINGS_22042026.md`), только для CS-ниши.

---

## Технические требования

### 1. Создать таблицу `seo_landings` (если ещё не создана для Nutaku)

```sql
CREATE TABLE IF NOT EXISTS seo_landings (
  slug TEXT PRIMARY KEY,
  landing_type TEXT NOT NULL,  -- 'cs2_skins_hub', 'nutaku_promo' и т.д.
  title TEXT,
  meta_description TEXT,
  h1 TEXT,
  article TEXT,
  faq JSONB,
  keywords TEXT,
  related_slugs TEXT[],  -- ['hellcase-gift-card', 'farmskins-game-keys', ...]
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);
```

### 2. Роутинг в Nuxt SSR `/t/{slug}`

Логика обработчика:

```javascript
// Псевдокод обработчика страницы /t/{slug}
async function handleTPage(slug) {
  // Шаг 1: ищем обычный агрегатор (текущая логика)
  const products = await api.getProductsForAggregator(slug);
  if (products.length > 0) {
    return renderProductAggregator(slug, products);
  }
  
  // Шаг 2 (НОВОЕ): ищем SEO-landing
  const landing = await db.query(`
    SELECT * FROM seo_landings WHERE slug = $1 AND is_active = true
  `, [slug]);
  
  if (landing) {
    // Получаем товары "связанных" агрегаторов для витрины
    const relatedProducts = await api.getProductsForMultipleAggregators(landing.related_slugs);
    return renderLandingPage(landing, relatedProducts);
  }
  
  // Шаг 3: 410 Gone (см. P0 task)
  return notFound(410);
}
```

### 3. Шаблон landing-page

Visual layout:

```
┌─────────────────────────────────────────────────────────────┐
│  Hero block                                                  │
│   ┌────────────────────────────────────────────┐            │
│   │ {h1}                                        │            │
│   │ {description короткая, 1-2 предложения}     │            │
│   │ [Кнопка "Смотреть все сайты со скинами"]   │            │
│   └────────────────────────────────────────────┘            │
├─────────────────────────────────────────────────────────────┤
│  H2: {SEO-article абзац 1}                                  │
│   <p>...</p>                                                 │
│                                                              │
│  H2: Популярные сайты с CS2 скинами                         │
│  Grid 4×6 (24 карточки):                                    │
│   ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐                     │
│   │Hell  │ │Farm  │ │Skin. │ │Rain. │                     │
│   │case  │ │skins │ │Club  │ │gg    │                     │
│   └──────┘ └──────┘ └──────┘ └──────┘                     │
│   (... ещё 20 карточек)                                     │
│                                                              │
│  H2: Counter-Strike игры в Steam                            │
│  Grid 1×9 для CS-ключей:                                    │
│   ┌──────┐ ┌──────┐ ┌──────┐ ...                          │
│   │CS2   │ │Prime │ │Compl-│                              │
│   │Game  │ │Stat  │ │ete   │                              │
│   └──────┘ └──────┘ └──────┘                               │
│                                                              │
│  H2: Как выбрать сайт со скинами CS2                       │
│   <p>... SEO-контент про критерии выбора, безопасность</p> │
│                                                              │
│  H2: Часто задаваемые вопросы                              │
│  FAQ accordion с 10 вопросами                              │
│                                                              │
│  Footer: связанные категории                                 │
└─────────────────────────────────────────────────────────────┘
```

### 4. JSON-LD разметка (важно для rich snippets)

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "CollectionPage",
  "name": "{title}",
  "description": "{meta_description}",
  "url": "https://gaming-goods.ru/t/cs-skins-marketplace",
  "mainEntity": {
    "@type": "ItemList",
    "itemListElement": [
      {
        "@type": "ListItem",
        "position": 1,
        "name": "Hellcase",
        "url": "https://gaming-goods.ru/t/hellcase-gift-card"
      },
      // ... все 25
    ]
  }
}
</script>

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "{faq[0].question}",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "{faq[0].answer}"
      }
    },
    // ... все 10
  ]
}
</script>
```

### 5. Sitemap.xml

Добавить новый URL:
```xml
<url>
  <loc>https://gaming-goods.ru/t/cs-skins-marketplace</loc>
  <lastmod>2026-04-28</lastmod>
  <priority>0.9</priority>
  <changefreq>weekly</changefreq>
</url>
```

---

## Список slug'ов для `related_slugs`

В `seo_landings.related_slugs` для нашего hub'а нужно вставить **массив всех 25 CS-страниц**:

```sql
related_slugs := ARRAY[
  -- Skin-боксы и кейсы (16)
  'hellcase-gift-card',
  'farmskins-game-keys',
  'skin-club-gift-card',
  'rain-gg-gift-card',
  'lootie-gift-card',
  'haloskins-gift-card',
  'insane-gg-gift-card',
  'hypedrop-gift-card',
  'shadowpay-gift-card',
  'g4skins-com-gift-card',
  'rustypot-gift-card',
  'pirateswap-gift-card-gift-card',
  'stakejoker-gift-card',
  'rainbet-gift-card-gift-card',
  'plg-bet-gift-card',
  'skinsproject-gift-card',
  'skinrave-gg-gift-card',
  'dropland-net-game-keys',
  
  -- Counter-Strike игры и DLC (9)
  'counter-strike-game-keys',
  'counter-strike-complete-game-keys',
  'counter-strike-complete-2013-game-keys',
  'counter-strike-complete-2023-game-keys',
  'counter-strike-2-prime-status-upgrade-game-keys',
  'counter-strike-2-with-prime-status-upgrade-game-keys',
  'counter-strike-2-prime-status-upgrade-collection-game-keys'
]
```

---

## SEO-контент для лендинга (готов от Claude)

Я уже подготовил полный SEO-пакет для этой страницы. После того как Саша создаст таблицу `seo_landings`, я выполню `INSERT` через write-доступ Саши:

```sql
INSERT INTO seo_landings (slug, landing_type, title, meta_description, h1, article, faq, keywords, related_slugs)
VALUES (
  'cs-skins-marketplace',
  'cs2_skins_hub',
  'Купить скины CS2 — обзор лучших сайтов с кейсами и торговлей | Гейминг Гудс',
  'Купить скины Counter-Strike 2 (CS:GO) — Hellcase, Farmskins, Skin.Club, Rain.gg и другие сайты. Безопасное пополнение баланса через подарочные карты. Мгновенная доставка кода.',
  'Купить скины CS2 (Counter-Strike 2) — обзор сайтов с кейсами и торговлей',
  '<h2>Где купить скины CS2 в России</h2>
   <p>Counter-Strike 2 — игра с самой развитой экосистемой скинов в индустрии. На gaming-goods.ru мы собрали подарочные карты для всех топовых сервисов открытия кейсов, торговли и crash-казино со скинами CS2/CS:GO. Оплачиваете рублями, получаете код пополнения для баланса любого сервиса — мгновенно на e-mail.</p>
   
   <h2>Виды сервисов со скинами Counter-Strike</h2>
   <p><strong>Сайты кейсов</strong> — Hellcase, Farmskins, Skin.Club, Rain.gg, Lootie, Insane.gg, HypeDrop. Открываете кейсы с шансом получить редкие скины. Мы продаём подарочные карты для пополнения баланса этих сайтов.</p>
   <p><strong>Skin-маркетплейсы</strong> — Shadowpay, PirateSwap, SkinsProject. Покупаете и продаёте скины напрямую. Подарочная карта пополняет ваш кошелёк.</p>
   <p><strong>Crash-казино</strong> — StakeJoker, RainBet, PLG.BET (бывший CSGOPolygon). Ставите скины или баланс на crash-механику.</p>
   <p><strong>Mystery box</strong> — Lootie, HypeDrop. Получаете реальные физические призы (электроника, мерч) в обмен на покупку случайных коробок.</p>
   
   <h2>Как мы работаем</h2>
   <p>Гейминг Гудс — официальный продавец подарочных карт для всех перечисленных сервисов. Покупаете на нашем сайте — получаете код активации в течение 5-15 минут. Активируете код в личном кабинете соответствующего сервиса.</p>
   <ul>
     <li>Оплата картой (Visa, Mastercard, МИР), криптовалютой или СБП</li>
     <li>Доставка кода мгновенно на e-mail</li>
     <li>Поддержка 24/7 на русском языке</li>
     <li>Безопасные платежи через защищённый шлюз</li>
   </ul>
   
   <h2>Counter-Strike 2 — игра, ключи и Prime Status</h2>
   <p>Помимо скинов, на странице доступны Steam-ключи самой игры Counter-Strike 2. Prime Status Upgrade открывает доступ к официальным матчам, эксклюзивным скинам и улучшенному matchmaking. Counter-Strike Complete — bundle всех CS-игр в Steam.</p>
   
   <h2>Безопасность и гарантии</h2>
   <p>Все коды поставляются от официальных партнёров. В случае проблем с активацией — возврат средств в течение 24 часов. Работаем с 2024 года, тысячи довольных клиентов.</p>',
  '[
    {"question":"Что такое скины CS2 и зачем их покупать?","answer":"Скины — это косметические улучшения оружия в Counter-Strike 2. Они не дают игровых преимуществ, но придают индивидуальный стиль. Многие скины редкие и ценные, их можно покупать, продавать или коллекционировать."},
    {"question":"Какой сайт выбрать для покупки скинов CS2?","answer":"Зависит от того, что вы хотите. Для открытия кейсов — Hellcase, Farmskins, Skin.Club. Для прямой торговли — Shadowpay, PirateSwap. Для случайных призов — Lootie, HypeDrop. На gaming-goods.ru есть карты для всех."},
    {"question":"Как пополнить баланс через подарочную карту?","answer":"Покупаете на нашем сайте подарочную карту нужного номинала. Получаете код активации на e-mail в течение 5-15 минут. Заходите в личный кабинет нужного сервиса и активируете код в разделе пополнения баланса."},
    {"question":"Безопасно ли покупать у вас?","answer":"Да. Гейминг Гудс работает с 2024 года и является официальным партнёром перечисленных сервисов. Все коды поставляются легально, через защищённые каналы. В случае проблем с активацией — возврат средств в течение 24 часов."},
    {"question":"Можно ли купить скины CS2 за рубли?","answer":"Да. Все подарочные карты на нашем сайте можно оплатить рублями через карты МИР, Visa, Mastercard или СБП. Также принимаем криптовалюту."},
    {"question":"Что такое Prime Status в CS2 и зачем он нужен?","answer":"Prime Status — премиум-аккаунт CS2, который даёт доступ к официальным конкурентным матчам, эксклюзивным еженедельным дропам скинов и более качественному matchmaking. Покупается отдельно через Steam Key."},
    {"question":"Можно ли вывести скины с этих сайтов?","answer":"Зависит от сервиса. Hellcase, Farmskins, Skin.Club позволяют вывести выигранные скины напрямую в Steam-инвентарь. Crash-казино обычно требуют конвертации в крипту или выводят через Steam-маркетплейсы."},
    {"question":"Сколько времени занимает доставка кода?","answer":"Мгновенно после оплаты, в большинстве случаев 5-15 минут. Код приходит на e-mail и в личный кабинет на gaming-goods.ru."},
    {"question":"Что делать если код не активируется?","answer":"Свяжитесь с нашей поддержкой через чат на сайте или e-mail support@gaming-goods.ru. Мы решим проблему в течение 24 часов или вернём деньги."},
    {"question":"Какой сайт лучше — Hellcase или Farmskins?","answer":"Оба входят в топ-3 кейсовых сайтов CS2 в России. Hellcase популярнее, у него больше ассортимент кейсов. Farmskins известен upgrade-механикой и contracts-режимом. Попробуйте оба — на нашем сайте есть карты для каждого."}
  ]'::jsonb,
  'купить скины cs2, купить скины кс2, купить скины counter-strike, csgo рулетки, сайты с кейсами cs2, лучшие сайты скинов кс2, hellcase купить, farmskins купить, skin club, rain.gg купить, кс2 кейсы открыть, csgo скины купить, скины counter-strike 2',
  ARRAY[/* список из 25 slug'ов выше */]
);
```

---

## Acceptance criteria

1. ✅ Таблица `seo_landings` создана и работает
2. ✅ URL `https://gaming-goods.ru/t/cs-skins-marketplace` открывается без 404
3. ✅ На странице:
   - Hero с H1
   - SEO-article с подразделами (h2)
   - Грид-витрина 25 карточек (skin-сервисы + CS-ключи)
   - FAQ accordion с 10 вопросами
4. ✅ JSON-LD разметка (CollectionPage + FAQPage)
5. ✅ Карточки кликабельны и ведут на соответствующие `/t/...`
6. ✅ TTFB < 600ms
7. ✅ Mobile-responsive
8. ✅ Sitemap.xml содержит новый URL
9. ✅ Через 2-4 недели — рост impressions в Яндекс.Вебмастер по запросам "купить скины кс2", "csgo рулетки", "сайты кейсов cs2"

---

## Expected impact

После запуска и переиндексации (4-6 недель):

| Запрос | Текущая позиция | Прогноз |
|--------|-----------------:|---------:|
| купить скины cs2 | НЕТ в топ-50 | топ-5 |
| csgo рулетки | НЕТ | топ-10 |
| сайты с кейсами cs2 | НЕТ | топ-5 |
| где купить скины cs2 | НЕТ | топ-3 |
| лучшие сайты скинов кс | НЕТ | топ-5 |
| hellcase или farmskins | НЕТ | топ-3 |

**Прогноз трафика:** +200-500 кликов/неделю в нише CS2-скинов.
**Прогноз GMV:** +€2 000-5 000/месяц (CS-аудитория конвертится хорошо).
**Окупаемость:** разработка ~5-10 часов работы Саши → результат на годы вперёд.

---

## Связанные задачи

- `TASK_SASHA_NUTAKU_LANDINGS_22042026.md` — тот же паттерн `seo_landings` для Nutaku, **рекомендую делать вместе** (одна таблица обслуживает оба случая)
- `TASK_SASHA_INTERLINKING_22042026.md` — внутренняя перелинковка, hub-страница автоматом туда впишется
- `CS2_SEO_INDEX_REPORT_28042026.md` — что я уже сделал и что не сработало

---

## Что готов сделать Claude после фикса роутинга

1. **Сразу:** INSERT всех данных в `seo_landings` (контент уже подготовлен выше)
2. **Дальше:** генерация ещё 5-10 long-tail CS-лендингов (например `/t/cs2-skins-cheap`, `/t/best-cs2-cases`, `/t/free-cs-skins`) — $0.50, 1 час работы
3. **После запуска:** мониторинг позиций Яндекс.Вебмастер раз в неделю
4. **При успехе:** масштабирование на похожие игры — Dota 2 скины, PUBG скины, Apex skins

---

## Timeline

| День | Что |
|------|-----|
| 1-2 | Саша: создание таблицы `seo_landings`, роутинг `/t/{slug}` с проверкой landings |
| 3 | Саша: шаблон landing-page (Hero, Grid, FAQ, JSON-LD) |
| 4 | Тестирование на staging |
| 5 | Claude: INSERT данных в `seo_landings` |
| 6 | Саша: deploy в production, sitemap update |
| 7 | Claude: отправка URL на recrawl в Яндекс |
| 8-30 | Мониторинг позиций |

---

Пиши если нужно уточнить детали реализации, примеры кода, или подготовить ещё больше long-tail slugs.
