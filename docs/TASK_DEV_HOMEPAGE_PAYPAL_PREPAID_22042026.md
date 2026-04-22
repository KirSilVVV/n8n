# Задача разработчику: PayPal Top Up в «Хиты продаж» + секция Prepaid Mastercard/Visa

**Приоритет:** HIGH (whale-клиенты, готовые страницы, 0 расходов на контент)
**Срок:** 3-5 дней
**Дата:** 22.04.2026
**Автор:** Кир (CEO)
**Связано:** `TASK_DEV_HOMEPAGE_CS2_SKINS_21042026.md`, `TASK_DEV_HOMEPAGE_APPLE_ITUNES_21042026.md` — можно объединить все в один PR «расширение главной страницы»

---

## Контекст

На главной `/` сейчас нет PayPal и Prepaid Mastercard/Visa — хотя по ним есть активные покупатели и готовые SEO-страницы. Это прямые потери конверсии.

### PayPal Top Up — whale-клиент Дронова
- buyer_id `33f7e0ae89984bb9b47475e29b796e47`
- 7 заказов за 9 дней в апреле 2026
- Только PayPal Wallet AUD Top Up (40, 100, 130, 180, 325 AUD)
- Общая выручка **106 000 ₽**
- Кандидат на pilot «PayPal AUD refill subscription»

### Prepaid Mastercard/Visa — продажи на Яндекс Маркете
- 14 CAD номиналов Prepaid Mastercard в каталоге (1, 2, 3, 5, 10, 15, 20, 25, 50, 100, 150, 200, 250, 500)
- **20 CAD — основной бестселлер на ЯМ**
- Всего 121 активных Prepaid Mastercard-products
- 12 страниц с готовым SEO (Sonnet 4.6, 21.04.2026)

---

## Задачи

### Задача A. PayPal Top Up в «Хиты продаж»

**Где:** секция «Хиты продаж» на главной (`/`), сейчас содержит 8 карточек

**Что сделать:** добавить **одну карточку PayPal Wallet** между MS Office и ChatGPT Plus:

```
Позиция 7 (после MS Office, перед ChatGPT Plus):
- Название: PayPal Wallet — пополнение
- URL: /t/paypal-wallet-top-up
- Иконка: логотип PayPal (уже есть в CDN или взять с paypal.com)
- Подзаголовок (если есть): «USD, EUR, GBP, AUD, CAD»
```

**Альтернатива:** расширить секцию с 8 до **9 карточек** чтобы не вытеснять текущие товары. Решение за разработчиком.

**Источник данных:** агрегатная страница `/t/paypal-wallet-top-up` (alen=930, faq=6 — качественная SEO уже готова 21.04.2026).

### Задача B. Новая H2-секция «Предоплаченные карты Visa и Mastercard»

**Где:** после секции «Предоплаченные карты» (сейчас там только Xbox Live и Nintendo). Либо **переименовать существующую** секцию в «Предоплаченные карты и Mastercard/Visa» и добавить в неё новые карточки.

**Что показать — 12 карточек:**

| Карточка | slug |
|----------|------|
| Prepaid Mastercard CAD | `/t/prepaid-mastercard-gift-card` |
| Mastercard Gift Card ZAR | `/t/mastercard-gift-card-gift-card` |
| MyPaymentVault Virtual Mastercard | `/t/mastercard-prepaid-gift-card` |
| Toneo First Mastercard | `/t/mastercard-toneo-first-gift-card` |
| Toneo First Mastercard (дубль) | `/t/toneo-first-mastercard-gift-card` |
| Virtual Mastercard | `/t/virtual-mastercard-gift-card` |
| Rewarble Mastercard | `/t/rewarble-mastercard-gift-card` |
| Rewarble Discord Nitro | `/t/rewarble-discord-nitro-gift-card` |
| Prepaid Visa eReward | `/t/prepaid-visa-ereward-gift-card` |
| Virtual Visa | `/t/virtual-visa-gift-card` |
| Visa Prepaid | `/t/visa-prepaid-gift-card` |
| Rewarble Visa | `/t/rewarble-visa-gift-card` |

**Layout:** grid 4×3 на десктопе, 2×6 на мобильном, или horizontal scroll (как существующие секции).

**Заголовок секции:** `Предоплаченные карты Visa и Mastercard`
**Подзаголовок:** «Виртуальные карты для оплаты за рубежом, подписки и покупки в международных сервисах. Номиналы от $1 до $500.»

---

## Технические требования

Те же что в CS2 и Apple/iTunes задачах:

- **НЕ создавать новые `/t/` страницы** — все готовы с качественным SEO
- **НЕ менять backend** — агрегаторы работают (кроме PayPal top-up slug-matching — см. `TASK_SASHA_PAYPAL_AGGREGATOR_21042026.md`, это отдельная задача)
- Использовать существующий механизм секций главной (тот же паттерн что Хиты продаж / Steam / Игры)
- SSR-рендеринг, не JS-генерация
- Аналитика: события `home_section_click` с `section_name="prepaid_mastercard"` и `brand_slug="..."`

---

## Acceptance criteria

**Задача A (PayPal):**
1. ✅ На главной `/` в «Хиты продаж» видна карточка PayPal Wallet
2. ✅ Клик → ведёт на `/t/paypal-wallet-top-up`
3. ✅ Страница не 404, открывается
4. ✅ Аналитика фиксирует `home_section_click` с `brand_slug="paypal-wallet-top-up"`

**Задача B (Prepaid Mastercard/Visa):**
1. ✅ На главной `/` видна H2-секция «Предоплаченные карты Visa и Mastercard» с 12 карточками
2. ✅ Все 12 ссылок открываются без 404
3. ✅ Мобильный layout не ломается (LCP < 2.5s)
4. ✅ Аналитика фиксирует события

---

## Ресурсы

- Список готовых Mastercard/Visa страниц с title: [см. журнал генерации `prepaid_mc_20260421`]
- Shared паттерн с предыдущими задачами: `TASK_DEV_HOMEPAGE_CS2_SKINS_21042026.md`

---

## Рекомендация — объединить PR

Есть 3 открытые задачи расширения главной:
1. CS2 Skins (50 страниц)
2. Apple/iTunes (18 страниц)
3. **PayPal + Prepaid MC/Visa** (эта задача, 1 + 12 карточек)

**Оптимально объединить в один PR** «Расширение главной страницы» — 4 новых H2-секции + 1 карточка в «Хитах». Ревью в 1 раз, деплой в 1 раз.

**Ожидаемый total impact от всех 4 секций:**
- Хиты продаж: +PayPal (+5% CTR)
- 4 новых H2-секции: CS2 (23 карточки) + Apple/iTunes (18) + Prepaid MC/Visa (12)
- Прямые ссылки на 53 hub-страницы (ранее недоступных с главной)
- Повышение средней глубины визита
- **+€3-7K GMV/мес** на стабильном трафике без увеличения traffic

Сроки одного PR — **5-7 дней** (больше на ревью, сам код повторяющийся).
