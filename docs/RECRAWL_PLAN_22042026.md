# План Yandex Recrawl на 22.04.2026

**Подготовлено:** 21.04.2026 (вечер)
**Старт:** 22.04.2026 в 00:00 МСК (обнуление квоты Яндекса)
**Скрипт:** `/home/claude/yandex_recrawl.py` либо уже запущенный `auto_recrawl.py`

---

## 📊 Главные числа — одним взглядом

| Параметр | Значение |
|---------|---------:|
| **Страниц ждут отправки завтра** | **520** |
| Дневная квота Яндекса | 910 |
| Запас квоты после отправки 520 | **390** |
| Уже в очереди Яндекса (последние 7 дней) | 2 818 URL |
| Всего GOOD страниц в БД | 3 080+ |

**Вывод:** одной квоты хватит отправить все 520 pending. После завтра **все качественные страницы будут в очереди индексации Яндекса**.

---

## 🆕 Что обновлено сегодня 21.04.2026 (40 страниц)

Эти страницы переписаны Sonnet 4.6 сегодня и **ОБЯЗАНЫ пойти в завтрашний recrawl первыми** (они только что получили новый контент, важно ускорить переиндексацию):

### Prepaid Mastercard/Visa (12 страниц) — только что сделано
```
prepaid-mastercard-gift-card                            alen=764   ✅ уже в очереди
mastercard-gift-card-gift-card                          alen=695
mastercard-prepaid-gift-card                            alen=881
mastercard-toneo-first-gift-card                        alen=797
toneo-first-mastercard-gift-card                        alen=780
virtual-mastercard-gift-card                            alen=777
rewarble-mastercard-gift-card                           alen=820   ✅ уже в очереди
rewarble-discord-nitro-gift-card                        alen=746
prepaid-visa-ereward-gift-card                          alen=781
virtual-visa-gift-card                                  alen=802
visa-prepaid-gift-card                                  alen=842   ✅ уже в очереди
rewarble-visa-gift-card                                 alen=738   ✅ уже в очереди
```

### PayPal Top Up (2 страницы) — сделано сегодня
```
paypal-wallet-gift-card                                 alen=763
paypal-wallet-top-up                                    alen=930
```
Плюс `rewarble-paypal-gift-card` (alen=852) — уже был готов, тоже идёт на recrawl.

### CS2/skin (24 страницы) — сделано сегодня
- Counter-Strike (7): `counter-strike-2-prime-status-upgrade-{game-keys,collection-game-keys}`, `counter-strike-2-with-prime-status-upgrade-game-keys`, `counter-strike-complete-{2013,2023,}-game-keys`, `counter-strike-game-keys`
- Кейс-сайты (10): `hellcase`, `hypedrop`, `dropland-net`, `farmskins`, `g4skins`, `haloskins`, `insane-gg`, `lootie`, `rain-gg`, `skin-club`
- Skin-trading (5): `shadowpay`, `skinrave-gg`, `skinsproject`, `stakejoker`, `pirateswap`
- Прочие (2): `rainbet`, `rustypot`

### ✅ Уже в очереди (5 из 40) — не беспокоим
Отправлены в предыдущие волны:
- `plg-bet-gift-card`, `prepaid-mastercard-gift-card`, `rewarble-mastercard-gift-card`, `visa-prepaid-gift-card`, `rewarble-visa-gift-card`

### ⏳ Ждут recrawl из сегодняшних — **35 URL**

---

## 📦 Полный список на завтра — **520 URL**

### Разбивка по категориям

| Категория | Страниц | Описание |
|-----------|--------:|----------|
| Game Keys (прочие) | 216 | игры и DLC — алфавитный хвост после run50usd |
| Топ-бренды игр | 169 | Nutaku, Telegram, Steam, Fortnite, Minecraft и др. которые не успели в предыдущие волны |
| Другое | 38 | разнородные бренды |
| Currency | 29 | игровые валюты разные (Rainbow Six, NBA 2K и т.п.) |
| Gift Cards | 26 | подарочные карты разных брендов |
| Subscriptions | 16 | подписки (Paramount, VPN, ChatGPT уже в очереди) |
| **CS2/skin** | **13** | **обновлено сегодня + ранее** |
| **Prepaid Mastercard/Visa** | **10** | **обновлено сегодня** |
| **PayPal Top Up** | **3** | **обновлено сегодня** |
| **Итого pending** | **520** | |

### Разбивка по дате обновления

| Дата updated_at | Страниц |
|---------|--------:|
| **21.04 (сегодня)** | **35** |
| 19.04 | 159 |
| 18.04 | 188 |
| 17.03 (старые Haiku, прошли фильтр качества) | 138 |
| **Итого** | **520** |

---

## 🎯 Приоритет отправки завтра

Скрипт `yandex_recrawl.py` **автоматически** сортирует URL по приоритету: **сначала самые свежие `updated_at`**. То есть первыми завтра уйдут:

1. **Priority 1 (сегодняшние):** 35 URL с Mastercard/PayPal/CS2 SEO (свежий Sonnet-контент)
2. **Priority 2 (19.04):** 159 URL (ночные прогоны Bestsellers/Giftcards/Currency)
3. **Priority 3 (18.04):** 188 URL (пилоты ранние)
4. **Priority 4 (17.03):** 138 URL (старые Haiku-страницы прошедшие фильтр качества)

### Подсчёт квоты

- Квота: **910**
- Pending: **520**
- Остаток после отправки всех: **910 − 520 = 390**

### Что это значит?

- **Все 520 pending отправятся за один день**
- Останется **390 квоты на всякий случай** (на следующие доделанные страницы, либо на повторные попытки для 5xx-failures)

---

## 🔧 Как запустить recrawl

### Вариант 1 — ручной (рекомендую)

Когда пойдёт 00:00 МСК (= 21:00 UTC 21.04 или 00:00 UTC 22.04 — зависит от как Яндекс считает дневной цикл; квота сбросилась сегодня около 09:00 МСК значит следующий сброс примерно в те же сутки):

```bash
cd /home/claude && python3 yandex_recrawl.py
```

Скрипт сам:
- Запросит `recrawl/quota` у Яндекса
- Выгрузит из БД список pending (отсортированный по приоритету)
- Отправит батчами с throttle 150ms (~2 URL/сек)
- Залогирует каждую отправку в `yandex_reindex_log`
- Выведет финальный отчёт `recrawl_20260422_HHMM_report.json`

Займёт **~4 минуты** на 520 URL.

### Вариант 2 — автоматический (если запущен)

Если процесс `auto_recrawl.py` ещё живёт в фоне — он сам проснётся при сбросе квоты и отправит. Проверка:
```bash
ps aux | grep auto_recrawl
cat /tmp/autorecrawl.log
```

---

## 📈 Мерила успеха для этой волны

После завтрашней отправки смотрим через 2-3 дня:

1. **CEO Brief v2** — секция «SEO индекс Яндекса» покажет:
   - APPEARED_IN_SEARCH сегодня = ожидаем +400…+600 (как после отправки 894 URL 18.04 получили +530 на следующий день)
   - Страниц в поиске = ожидаем стабилизацию или рост

2. **`yandex_metrics_snapshot.py`** — запустить через неделю:
   ```bash
   cd /home/claude && python3 yandex_metrics_snapshot.py
   ```
   Сравнить с baseline `yandex_metrics_20260419_1915.json`.

3. **WF-205-YW** (понедельник 10:00 МСК):
   - `APPEARED/REMOVED net 7d` — должен подняться относительно текущих −4 577
   - Клики / показы — эффект появится через 2-3 недели

---

## 🤔 Почему НЕ 2 818?

В памяти записано *"Всего уникальных URL отправлено за 7 дней: 2 818"*. Это разные уровни:

- **2 818 — это уже в очереди Яндекса**. Эти страницы **уже отправлены** и Яндекс либо принял их в индекс, либо обрабатывает. Их трогать **не нужно**.
- **520 — те что НЕ отправляли** последние 7 дней. Именно их нужно послать завтра.

Итого покрытие после завтра: **2 818 + 520 = 3 338** уникальных URL в очереди индексации.

---

## 📂 Файлы

- `out/recrawl_tomorrow_22042026.txt` — плоский список 520 URL для recrawl
- `home/claude/yandex_recrawl.py` — скрипт отправки
- Лог после: `out/recrawl_20260422_HHMM_report.json`
