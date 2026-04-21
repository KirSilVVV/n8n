# Задача Саше: PayPal Top Up агрегатор не матчит продукты

**Приоритет:** HIGH (whale-клиент Дронова делает заказы по этим товарам)
**Статус:** REPORTED, ждёт анализа Сашей
**Дата:** 21.04.2026

---

## Проблема

Агрегаторная страница `/t/paypal-wallet-top-up` показывает продукты в SSR, **но API `/api/v1/t/paypal-wallet-top-up` возвращает 0 товаров** — то же самое для `paypal-wallet-gift-card` и `paypal-wallet-currency`.

Это важно потому что:
1. Whale-клиент **Дронова Влада** совершила 7 заказов за неделю (9-18.04) на общую сумму **106 000 ₽** исключительно на продуктах PayPal Wallet {AUD 40/100/130/180/325} Top Up с Яндекс Маркета (buyer.id `33f7e0ae89984bb9b47475e29b796e47`)
2. На агрегатной странице `/t/paypal-wallet-top-up` этих конкретных товаров (PayPal Wallet AUD Top Up) **может не быть** потому что slug-матчинг работает не так как ожидается
3. Каталог содержит 50+ индивидуальных `paypal-wallet-{N}-{currency}-top-up-{region}` товаров, а на агрегаторе их видно плохо

## Воспроизведение

```bash
# API возвращает 0 items, хотя на /t/paypal-wallet-top-up есть SSR-карточки
curl -H "X-Site-Slug: default" https://gaming-goods.ru/api/v1/t/paypal-wallet-top-up
# → {items: [], ...}

# Но в products активных:
SELECT COUNT(*) FROM products 
WHERE is_active=true AND slug ILIKE '%paypal-wallet%top-up%';
# → 50+ записей
```

Проверка для 4 PayPal агрегаторов:

| URL | API items | SSR показывает |
|-----|----------:|:---:|
| /t/paypal-wallet-top-up | 0 | да (1 product-card marker) |
| /t/paypal-wallet-gift-card | 0 | да + "купить" в тексте |
| /t/paypal-wallet-currency | 0 | да + "купить" в тексте |
| /t/rewarble-paypal-gift-card | 0 | да + "купить" в тексте |

## Что нужно от Саши

1. **Проверить alt-ids / slug-matching rules** для `paypal-wallet-top-up` агрегатора — какой паттерн slug'ов он собирает сейчас, и почему API возвращает пустой результат
2. **Убедиться что все `paypal-wallet-{N}-{AUD|USD|EUR|CAD|GBP}-top-up-{region}` попадают в один из 4 агрегаторов** (текущие: top-up / gift-card / currency / rewarble)
3. **Рекомендуемое решение**: создать единый агрегатор `/t/paypal-wallet-top-up` который собирает **ВСЕ** `paypal-wallet-*-top-up-*` товары через regex-match по slug, независимо от категории (Currency/Gift Card)

## Whale-клиент данные (для приоритезации)

- **buyer_id:** `33f7e0ae89984bb9b47475e29b796e47`
- **Ник на ЯМ:** дронова влада
- **Заказы 9-18.04:** 7 штук (6 delivered + 1 USER_CHANGED_MIND)
- **Товары:** PayPal Wallet AUD Top Up суммами 40 / 100 / 130 / 180 / 325
- **Общая выручка:** 106 000 ₽
- **Pilot opportunity:** PayPal AUD refill subscription (regular purchase pattern)

## Параллельная задача

SEO для 4 PayPal агрегатных страниц я уже переписал (тег `paypal_cs2_20260421`):
- `paypal-wallet-gift-card` (обновлён с 150 → 700+ символов)
- `paypal-wallet-top-up` (обновлён с 150 → 700+ символов)
- `paypal-wallet-currency` (уже был 727)
- `rewarble-paypal-gift-card` (уже был 852)

**Но это не поможет конверсии** если товары не матчатся на странице. Пожалуйста проверь backend часть.

## Related

- memory: `B2B Gifting MVP (gaming-goods.ru/gifting)` — корпоративный gifting может использовать тот же slug-matching механизм
- memory: "Whale-клиент Дронова — кандидат для pilot 'PayPal AUD refill subscription'"
