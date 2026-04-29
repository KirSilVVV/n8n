"""
seo_prompt.py — промпт и валидатор для генерации SEO-пакета страницы /t/ Gaming Goods.
"""
import re
import json

SYSTEM_PROMPT = """\
Ты — ведущий SEO-копирайтер маркетплейса «Гейминг Гудс» (gaming-goods.ru), крупнейшей в России биржи цифровых игровых товаров.

О МАГАЗИНЕ:
— Продаёт официальные ключи игр (Steam, Xbox, PlayStation, Epic, Ubisoft), подарочные карты (iTunes, Google Play, Steam, Xbox, PlayStation), игровую валюту (Nutaku Gold, Robux, Minecoins, Genesis Crystals, UC), аккаунты и подписки (PS Plus, Xbox Game Pass, Nintendo Switch Online).
— Агрегатор лотов от проверенных поставщиков: цены обычно ниже официальных сторов.
— Мгновенная доставка кода на e-mail и в личный кабинет после оплаты, работа 24/7.
— Оплата: банковская карта (Visa, Mastercard, **МИР**), **СБП**, баланс кошелька, Telegram-оплата, криптовалюта. Всё в **рублях** — это критическое преимущество для российской аудитории, обязательно упоминай.
— Поддержка через Telegram-бот @VVVSupport_bot.
— Российская аудитория: все тексты только на русском, без англицизмов «gaming», «gift card» в открытом виде без перевода.

ТВОЯ ЗАДАЧА: сгенерировать полноценный SEO-пакет для страницы-агрегатора /t/{slug}, на которой собраны все предложения одного товара.

==== ТРЕБОВАНИЯ ПО ПОЛЯМ ====

title (45–65 символов, строго):
— Бренд товара + категория («ключ Steam», «карта», «Gold», «подписка»).
— Содержит призыв «купить» или синоним.
— Оканчивается на « | Гейминг Гудс».
— Пример: «Minecraft Java Edition — купить ключ Steam | Гейминг Гудс» (59 символов).

description (130–180 символов, строго):
— Первые 60 символов — самое важное (мобильный сниппет).
— Содержит УТП: «мгновенная доставка», «официальная активация», «выгодная цена», «безопасная оплата».
— Упоминание «Гейминг Гудс» и способа получения (e-mail/личный кабинет) — обязательно.
— ОБЯЗАТЕЛЬНО включи акцент на оплату из России: фразу «Оплата в рублях», «карта МИР» или «СБП» (хотя бы одно из этих ключевых слов в description).
— Не начинать со слов «Купить» или «Заказать» — слишком шаблонно.
— Пример: «Ключ Minecraft Java Edition на Гейминг Гудс — официальная активация в Microsoft, мгновенная доставка кода. Оплата в рублях, картой МИР или СБП.» (149 символов).

h1 (25–70 символов):
— БЕЗ слова «купить».
— Описательный, уточняющий что продаётся (ключ, карта, валюта, подписка).
— Пример: «Minecraft Java Edition — ключ активации».

article (400–700 символов, 2–3 абзаца через \\n\\n):
— Абзац 1: что это за товар, для какой платформы, ключевые особенности (что даёт активация).
— Абзац 2: что получает покупатель на «Гейминг Гудс», как активирует, преимущество агрегатора.
— При отсутствии достоверных данных о товаре — пиши общо о категории, НЕ выдумывай сюжет/механики/геймдизайнеров.
— Только plain text с \\n\\n между абзацами. Никакого Markdown, bullet-пунктов, заголовков.
— Уникальный, не шаблонный — обязательно упомяни бренд минимум 2 раза, категорию минимум 1 раз.

faq (3–6 пар, строгий формат [{"question":"...","answer":"..."}, ...]):
— Вопросы — реальные поисковые запросы, не синтетические.
— Ответы по 2–3 предложения (50–280 символов).
— Обязательные темы зависят от категории:
  • Game Keys: как и где активировать, регион, когда придёт ключ, что делать если не работает.
  • Gift Card: как погасить код, какие номиналы бывают, срок действия кода.
  • Currency: как быстро зачисляется, куда вводится код, какие способы оплаты.
  • Account: что входит в доступ, риски блокировки и гарантии, как получить данные.
  • Subscription: срок действия, продление, регион активации.
— ОБЯЗАТЕЛЬНО хотя бы один FAQ-вопрос должен касаться оплаты для покупателей из РФ — «Можно ли оплатить рублями/картой МИР/СБП?», «Работает ли оплата из России?» (это даёт rich snippets в Яндексе).
— Последний вопрос — почему удобно покупать именно на «Гейминг Гудс».

keywords (5–8 ключей через запятую):
— Низко- и среднечастотные поисковые запросы, без стаффинга.
— Пример: «Minecraft Java купить ключ, ключ Minecraft Steam, Minecraft Java активация, Майнкрафт ключ недорого».

==== ФОРМАТ ВЫВОДА ====

Только валидный JSON без markdown-обёрток и комментариев.
Структура (порядок ключей сохраняй):

{"title":"...","description":"...","h1":"...","article":"...","faq":[{"question":"...","answer":"..."}, ...],"keywords":"..."}

==== КРИТИЧНО ====

— Весь текст на русском языке.
— Никаких кавычек-ёлочек внутри JSON-строк (используй обычные "" только для разделителей JSON; внутри полей — русские кавычки «…» или тире).
— Не используй одинарные кавычки ' вообще (заменяй на ’ U+2019).
— Не выдумывай цены, даты релиза, авторов, студии. Если не знаешь — пиши общими словами.
— Проверь длины полей: title 45–65, description 130–180, article 400–700.
— JSON должен парситься json.loads() без ошибок.
"""


USER_TEMPLATE = """\
Страница-агрегатор: {url}
Slug: {slug}
Категория: {category}

РЕАЛЬНЫЕ ДАННЫЕ ТОВАРА (из production API /api/v1/t):
— Имя товара: {product_name}
— Бренд: {brand}
— Платформа: {platform}
— Жанры: {genres}
— Разработчик: {developer}
— Издатель: {publisher}
— Возрастной рейтинг: {age_rating}
— Регион активации: {regionality}
— Цена от: {price} EUR
— В наличии сейчас: {stock} шт.
— Официальное описание (английское, для переосмысления): {product_description}

Текущий title (возможно шаблон): {current_title}

Сгенерируй SEO-пакет по правилам из системного промпта. Используй реальные данные — платформу, жанр, разработчика. Не выдумывай то чего нет в предоставленных данных.

ВАЖНО ПО РЕГИОНУ:
— Если регион активации указан (например "EU", "US", "IT", "BR", "Global") — упомяни его в description и FAQ.
— Если регион НЕ указан (null/None/—) — НЕ создавай FAQ-вопрос про регион. Вместо него добавь вопрос про срок действия кода, совместимость платформ, или способы оплаты на Гейминг Гудс.

ВАЖНО ПО ИЗВЕСТНЫМ БРЕНДАМ — используй специфику:
— NBA 2K VC → упомяни траты: MyCareer, MyTeam, MyPlayer builds, Badge upgrades.
— Fortnite V-Bucks → Battle Pass, Item Shop (скины/танцы), Save the World llama packs.
— Apex Legends Coins → Apex Packs, Battle Pass, Legend unlocks, Heirlooms.
— Valorant Points → agent unlocks, Battle Pass, skin bundles.
— CoD Points → Battle Pass, COD Points bundles, skins.
— Rainbow Six Credits → operator unlocks, Battle Pass, elite skins.
— Genshin Genesis Crystals → Primogems конвертация, Welkin Moon, Battle Pass (BP), banner wishes.
— Telegram Stars → боты, мини-приложения, платные каналы, реакции, реклама, подарки.
— Binance/крипто-gift-cards → USDT/BUSD на Binance Wallet, для P2P торговли и пополнения кошелька (для Binance Gift Card (USDT) — упомяни что популярно среди CS:GO trading сообществ как stable settlement currency).

Верни только JSON."""


CATEGORY_SUFFIXES = [
    ("-game-keys", "Game Keys"),
    ("-game-key", "Game Keys"),
    ("-gift-card", "Gift Card"),
    ("-gift-cards", "Gift Card"),
    ("-currency", "Currency"),
    ("-accounts", "Account"),
    ("-account", "Account"),
    ("-subscription", "Subscription"),
    ("-subscriptions", "Subscription"),
    ("-dlc", "DLC"),
    ("-season-pass", "Season Pass"),
]


def parse_url(url: str) -> dict:
    """Разбирает URL /t/{brand-slug}-{category-slug} на бренд и категорию."""
    slug = url.rstrip("/").rsplit("/", 1)[-1]
    for suffix, cat in CATEGORY_SUFFIXES:
        if slug.endswith(suffix):
            brand_slug = slug[: -len(suffix)]
            brand = _humanize_brand(brand_slug)
            return {"slug": slug, "brand_slug": brand_slug, "brand": brand, "category": cat}
    # Fallback — категория неизвестна
    return {"slug": slug, "brand_slug": slug, "brand": _humanize_brand(slug), "category": "Other"}


def _humanize_brand(brand_slug: str) -> str:
    """nutaku-com → Nutaku Com; horror-fish-simulator → Horror Fish Simulator."""
    parts = brand_slug.replace("_", "-").split("-")
    # roman numerals uppercase, short particles lowercase
    lower = {"of", "the", "and", "a", "an", "in", "at", "to"}
    out = []
    for i, p in enumerate(parts):
        pl = p.lower()
        if re.fullmatch(r"[ivxlcdm]+", pl) and len(pl) <= 5:
            out.append(pl.upper())
        elif pl in lower and i > 0:
            out.append(pl)
        else:
            out.append(pl[:1].upper() + pl[1:])
    return " ".join(out)


# ---- Валидация ----

FIELD_LIMITS = {
    "title": (40, 75),      # "The Hero — ключ Steam | Гейминг Гудс" = 43с edge case
    "description": (130, 200),
    "h1": (15, 90),         # "Train Sim World 5: Spirit of Steam: ..." = 87с edge case
    "article": (400, 1000),
}
MIN_FAQ = 3
MAX_FAQ = 6
FAQ_ANSWER_RANGE = (50, 320)


def clean_for_sql(s: str) -> str:
    """Заменяем одинарные кавычки на ’ и убираем backslashes как в Parse Claude response ноде WF-301."""
    if not s:
        return ""
    return s.replace("'", "\u2019").replace("\\", "")


def extract_json(text: str) -> dict:
    """Достаёт JSON из ответа модели (со скачиванием markdown-фенсов)."""
    t = text.strip()
    t = re.sub(r"^```(?:json)?\s*", "", t, flags=re.I)
    t = re.sub(r"\s*```$", "", t, flags=re.I)
    start = t.find("{")
    end = t.rfind("}")
    if start == -1 or end <= start:
        raise ValueError("no JSON object in response")
    t = t[start : end + 1]
    return json.loads(t)


def validate(seo: dict) -> list:
    """Возвращает список проблем. Пустой = всё ок."""
    issues = []
    for field, (lo, hi) in FIELD_LIMITS.items():
        v = (seo.get(field) or "").strip()
        n = len(v)
        if n == 0:
            issues.append(f"{field}: empty")
            continue
        if n < lo:
            issues.append(f"{field}: too short ({n} < {lo})")
        elif n > hi:
            issues.append(f"{field}: too long ({n} > {hi})")

    title = (seo.get("title") or "").strip()
    if "Гейминг Гудс" not in title:
        issues.append("title: missing «Гейминг Гудс»")

    desc = (seo.get("description") or "").strip()
    if "Гейминг Гудс" not in desc:
        issues.append("description: missing «Гейминг Гудс»")
    desc_lower = desc.lower()
    if not any(kw in desc_lower for kw in ["рубл", "мир", "сбп", "росси"]):
        issues.append("description: missing рубли/МИР/СБП/Россия акцент")

    h1 = (seo.get("h1") or "").strip().lower()
    if "купить" in h1:
        issues.append("h1: contains forbidden «купить»")

    article = (seo.get("article") or "").strip()
    if "\n\n" not in article:
        issues.append("article: missing paragraph break \\n\\n")

    faq = seo.get("faq")
    if not isinstance(faq, list):
        issues.append("faq: not a list")
    else:
        if not (MIN_FAQ <= len(faq) <= MAX_FAQ):
            issues.append(f"faq: wrong length ({len(faq)}, want {MIN_FAQ}-{MAX_FAQ})")
        for i, qa in enumerate(faq):
            if not isinstance(qa, dict):
                issues.append(f"faq[{i}]: not a dict")
                continue
            q = (qa.get("question") or "").strip()
            a = (qa.get("answer") or "").strip()
            if len(q) < 10 or len(q) > 120:
                issues.append(f"faq[{i}].question: bad length {len(q)}")
            alo, ahi = FAQ_ANSWER_RANGE
            if not (alo <= len(a) <= ahi):
                issues.append(f"faq[{i}].answer: bad length {len(a)} (want {alo}-{ahi})")

    kw = (seo.get("keywords") or "").strip()
    if kw:
        parts = [p.strip() for p in kw.split(",") if p.strip()]
        if not (3 <= len(parts) <= 10):
            issues.append(f"keywords: wrong item count ({len(parts)})")

    return issues


def clean_keywords_mixed_scripts(s: str) -> str:
    """Убирает слова со смешанной кириллицей+латиницей, типа 'Борderlands'.
    Такие слова — результат склеивания модели, они портят keywords."""
    import re
    # слово = последовательность букв/цифр/точек
    words = re.split(r'([\s,;]+)', s)
    out = []
    for w in words:
        if not w.strip():
            out.append(w)
            continue
        has_cyr = bool(re.search(r'[А-Яа-яёЁ]', w))
        has_lat = bool(re.search(r'[A-Za-z]', w))
        if has_cyr and has_lat:
            # Смешанный термин — пропускаем
            continue
        out.append(w)
    result = ''.join(out)
    # Убираем двойные запятые/пробелы от удалённых слов
    result = re.sub(r'(\s*,\s*){2,}', ', ', result)
    result = re.sub(r',\s*$', '', result).strip().strip(',').strip()
    return result


def normalize(seo: dict) -> dict:
    """Применяет clean_for_sql ко всем текстовым полям (как в WF-301 Parse node)."""
    keywords_raw = clean_for_sql((seo.get("keywords") or "").strip())[:300]
    keywords_clean = clean_keywords_mixed_scripts(keywords_raw)
    out = {
        "title": clean_for_sql((seo.get("title") or "").strip())[:200],
        "description": clean_for_sql((seo.get("description") or "").strip())[:500],
        "h1": clean_for_sql((seo.get("h1") or "").strip())[:200],
        "article": clean_for_sql((seo.get("article") or "").strip()),
        "keywords": keywords_clean,
    }
    faq_in = seo.get("faq") or []
    faq_out = []
    for qa in faq_in:
        if isinstance(qa, dict):
            faq_out.append(
                {
                    "question": clean_for_sql((qa.get("question") or "").strip()),
                    "answer": clean_for_sql((qa.get("answer") or "").strip()),
                }
            )
    out["faq"] = faq_out
    return out


if __name__ == "__main__":
    # smoke-test
    print(parse_url("https://gaming-goods.ru/t/spirits-of-xanadu-game-keys"))
    print(parse_url("https://gaming-goods.ru/t/nutaku-currency"))
    print(parse_url("https://gaming-goods.ru/t/minecraft-java-edition-game-key"))
