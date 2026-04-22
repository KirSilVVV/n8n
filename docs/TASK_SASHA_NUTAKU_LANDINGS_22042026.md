# Задача Саше: SEO-лендинги для захвата топ-1 по Nutaku

**Приоритет:** HIGH (65% выручки — главный канал)
**Срок:** 1 неделя
**Дата:** 22.04.2026
**Автор:** Кир (CEO)
**Связано:** стратегия роста `GROWTH_STRATEGY_22042026.md`

---

## Проблема

Главный запрос нашей бизнес-модели — `nutaku золото купить` — сейчас на **позиции 3.3** в Яндексе. Мы там должны быть на **#1**, потому что Nutaku-канал даёт **65% всей выручки** GGE.

Конкуренты захватывают длинные хвосты:
- «nutaku бонус код»
- «nutaku промокод 2026»
- «как пополнить nutaku»
- «nutaku за рубли»
- и т.д.

У нас на эти запросы нет специализированных страниц — только один hub `/t/nutaku-currency`, который хорош, но не может быть одновременно релевантен всем long-tail запросам.

---

## Что сделано со стороны SEO (Claude)

1. **Углублён `/t/nutaku-currency`** — article 815 → **3587 знаков**, FAQ 6 → **10 вопросов** (обновлено 22.04.2026 18:XX)
2. **Подготовлены 20 long-tail slug'ов** с заголовками для создания отдельных лендингов

---

## Что нужно от backend (Саши)

### 🎯 Главная задача: настроить роутинг 20 новых URL

Сейчас если перейти на `https://gaming-goods.ru/t/nutaku-bonus-code` — получим **404** потому что таких slug'ов нет в `marketplace`-таблице (или откуда берёт Nuxt SSR данные для `/t/`).

**Решение:** создать механизм **«SEO landing pages»** для Nutaku. Варианты реализации:

#### Вариант A — Таблица `seo_landings` (рекомендую)

Новая таблица специально под промо-лендинги:

```sql
CREATE TABLE seo_landings (
  slug TEXT PRIMARY KEY,           -- 'nutaku-bonus-code'
  target_aggregator TEXT,          -- '/t/nutaku-currency' (куда редиректит кнопка "Купить")
  landing_type TEXT,               -- 'nutaku_promo', 'apple_guide', etc.
  priority INTEGER DEFAULT 0,
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT now()
);
```

Роутинг в Nuxt/Go-backend:
1. Пришёл запрос `/t/{slug}` → проверить `page_seo` (основной)
2. Если нет товаров на агрегаторе → проверить `seo_landings`
3. Если есть — отрендерить специальный шаблон (см. ниже)
4. Если нет — 404 как сейчас

**Первичный INSERT** (я подготовлю полный SQL с 20 записями):
```sql
INSERT INTO seo_landings (slug, target_aggregator, landing_type) VALUES
('nutaku-bonus-code', '/t/nutaku-currency', 'nutaku_info'),
('nutaku-promo-code-2026', '/t/nutaku-currency', 'nutaku_info'),
('nutaku-gold-cheap', '/t/nutaku-currency', 'nutaku_info'),
('nutaku-pay-rubles', '/t/nutaku-currency', 'nutaku_info'),
... (все 20)
```

#### Вариант B — reuse `/t/{slug}` с виртуальным контентом

Для slug'а без товаров:
- Если есть запись в `page_seo` с непустым `article` — показать SEO-контент
- Показать товары **родительского агрегатора** (взять из `seo_landings.target_aggregator`)
- Кнопка «Купить Nutaku Gold» ведёт на `/t/nutaku-currency`

Это проще для frontend'а — существующий template `/t/{slug}` просто добавит один if-branch.

### 🖼 Шаблон SEO-лендинга

Компонент должен содержать:

```html
<article>
  <h1>{h1 из page_seo}</h1>
  
  <!-- SEO-контент -->
  <div class="seo-article">
    {article из page_seo в HTML-виде}  <!-- Должен рендериться с h2, p, ul -->
  </div>
  
  <!-- FAQ -->
  <section class="faq">
    <h2>Часто задаваемые вопросы</h2>
    <details v-for="item in faq">
      <summary>{item.question}</summary>
      <p>{item.answer}</p>
    </details>
  </section>
  
  <!-- Основной CTA-блок -->
  <section class="buy-cta">
    <h2>Купить Nutaku Gold прямо сейчас</h2>
    <div class="nutaku-packages">
      <!-- Показать top-5 популярных Nutaku номиналов -->
      <!-- Данные: запрос к products WHERE brand='Nutaku' AND is_active=true -->
      <!-- ORDER BY popularity_score / price_from_cents -->
      <ProductCard v-for="product in nutakuProducts" />
    </div>
    <a href="/t/nutaku-currency" class="btn-primary">
      Все номиналы Nutaku Gold →
    </a>
  </section>
</article>
```

**Ключевое:** CTA-кнопка «Купить» ВСЕГДА ведёт на `/t/nutaku-currency` (главный hub). Это концентрирует trust и конверсии на одной странице.

### FAQ — JSON-LD разметка для расширенных сниппетов

На лендингах с FAQ обязательно добавить структурированные данные:

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "{question}",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "{answer}"
      }
    },
    ...
  ]
}
</script>
```

Это даст расширенные сниппеты в Яндексе и Google (вопросы-ответы прямо в выдаче) = **+CTR 15-25%**.

### Sitemap / robots.txt

Добавить новые URL в `sitemap.xml`:
```xml
<url>
  <loc>https://gaming-goods.ru/t/nutaku-bonus-code</loc>
  <lastmod>2026-04-22</lastmod>
  <priority>0.8</priority>
</url>
```

Саше нужно проверить что генератор `sitemap.xml` подхватывает URL из `seo_landings` автоматически.

---

## Список 20 lending-URL для создания

Все на базе агрегатора `/t/nutaku-currency`:

| # | Slug | Фокусный запрос |
|---|------|------------------|
| 1 | `nutaku-bonus-code` | nutaku бонус код |
| 2 | `nutaku-promo-code-2026` | промокод nutaku 2026 |
| 3 | `nutaku-gold-cheap` | nutaku gold дёшево |
| 4 | `nutaku-gold-discount` | nutaku gold скидка |
| 5 | `nutaku-pay-rubles` | nutaku оплата рубли |
| 6 | `nutaku-pay-crypto` | nutaku оплата криптой |
| 7 | `nutaku-payment-methods` | nutaku способы оплаты |
| 8 | `nutaku-account-topup` | пополнение аккаунта nutaku |
| 9 | `nutaku-gold-500` | nutaku gold 500 |
| 10 | `nutaku-gold-1000` | nutaku gold 1000 |
| 11 | `nutaku-gold-2000` | nutaku gold 2000 |
| 12 | `nutaku-gold-5000` | nutaku gold 5000 |
| 13 | `nutaku-gold-10000` | nutaku gold 10000 |
| 14 | `nutaku-activation-guide` | как активировать nutaku gold |
| 15 | `nutaku-how-to-buy` | как купить nutaku |
| 16 | `nutaku-gold-code` | nutaku gold код |
| 17 | `nutaku-vs-steam` | nutaku vs steam |
| 18 | `nutaku-official-store` | nutaku официальный магазин |
| 19 | `nutaku-russia-2026` | nutaku в россии 2026 |
| 20 | `nutaku-support` | nutaku поддержка |

**Claude готов генерировать SEO-контент для каждого из этих slug'ов сразу как Саша создаст роутинг.** Это ~$1 расходов на Anthropic API и 15 минут работы.

---

## Acceptance criteria

1. ✅ Все 20 URL открываются без 404
2. ✅ Каждый показывает уникальный SEO-контент + товары с кнопкой «Купить»
3. ✅ FAQ-блок рендерится с JSON-LD разметкой
4. ✅ CTA-кнопка ведёт на `/t/nutaku-currency`
5. ✅ Sitemap автоматически включает новые URL
6. ✅ Через 2-4 недели — виден рост impressions в Яндекс.Вебмастер на запросы «nutaku бонус», «nutaku промокод» и др.

---

## Expected impact

**Через 4-8 недель после запуска:**
- Позиция по «nutaku золото купить»: 3.3 → **1-2**
- Трафик на Nutaku: +30-50%
- GMV от Nutaku: +€15-25K/мес
- **Чистая прибыль: +€6-10K/мес** (маржа Nutaku 40%)

**ROI:** одна неделя работы Саши → **€80-120K в годовом выражении**.

---

## Что от Claude когда Саша сделает роутинг

1. Сгенерирую SEO для 20 long-tail slug'ов (1 день, $1)
2. Добавлю в `page_seo` INSERT (или через обычный generator pipeline)
3. Отправлю URL на recrawl в Яндекс
4. Подготовлю следующие 30-50 лонгтейлов если первая волна сработает

---

## Timeline

| День | Что |
|------|-----|
| 1-2 | Саша: реализация роутинга (вариант A или B) |
| 3 | Саша: шаблон лендинга + JSON-LD FAQ |
| 4 | Тестирование на 1 URL (`nutaku-bonus-code`) |
| 5 | Claude: генерация SEO для 20 URL |
| 6 | Саша: sitemap обновление + recrawl 20 URL |
| 7+ | Мониторинг позиций в Яндекс.Вебмастер |

---

Пиши если нужна помощь с SQL для `seo_landings`, примером шаблона лендинга или любыми техническими деталями.
