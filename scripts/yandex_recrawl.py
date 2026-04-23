"""
yandex_recrawl.py — отправка GOOD страниц в Яндекс Recrawl API.

Правила:
- Только страницы с article ≥ 400 и faq_count ≥ 3
- Не отправлять повторно в течение 7 дней (дедупликация по yandex_reindex_log)
- Throttle 150ms между запросами
- Все попытки логируются в yandex_reindex_log (status sent/failed)

Usage:
    python3 yandex_recrawl.py              # отправить до квоты
    python3 yandex_recrawl.py --dry-run    # только показать план
    python3 yandex_recrawl.py --limit 100  # ограничить число
"""
import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

from pg import query

YM_TOKEN = "y0__xC93uTIBhj4yz4gnOmx0hYzxUi0DHhVAhks5kL9jLEFr6HyiQ"
USER_ID = "1763258173"
HOST_ID = "https:gaming-goods.ru:443"
YM_BASE = f"https://api.webmaster.yandex.net/v4/user/{USER_ID}/hosts/{HOST_ID}"
YM_HEADERS = {"Authorization": f"OAuth {YM_TOKEN}", "Content-Type": "application/json"}

THROTTLE_SEC = 0.15  # 150ms между запросами
RECRAWL_DB_HOST = "https:gaming-goods.ru:443"


def get_quota() -> dict:
    """Возвращает {daily_quota, quota_remainder} или None при ошибке. С retry."""
    last_err = None
    for attempt in range(6):
        try:
            r = requests.get(f"{YM_BASE}/recrawl/quota", headers=YM_HEADERS, timeout=20)
            if r.status_code == 200:
                return r.json()
            last_err = f"{r.status_code}: {r.text[:100]}"
        except Exception as e:
            last_err = str(e)
        time.sleep(10 + attempt * 5)  # 10, 15, 20, 25, 30, 35
    print(f"  quota retry failed: {last_err}")
    return None


def fetch_candidates(limit: int) -> list:
    """
    Выбирает URL для отправки: GOOD + не отправлялись за 7 дней.
    Сортировка: свежие SEO-обновления первыми (updated_at DESC),
    затем приоритетные бренды.
    """
    priority_sql = """
    CASE
      WHEN ps.url LIKE '%nutaku%' THEN 1
      WHEN ps.url LIKE '%telegram%' THEN 2
      WHEN ps.url LIKE '%steam%' THEN 3
      WHEN ps.url LIKE '%roblox%' THEN 4
      WHEN ps.url LIKE '%minecraft%' THEN 5
      WHEN ps.url LIKE '%xbox%' THEN 6
      WHEN ps.url LIKE '%playstation%' OR ps.url LIKE '%psn%' THEN 7
      WHEN ps.url LIKE '%genshin%' THEN 8
      WHEN ps.url LIKE '%pubg%' THEN 9
      WHEN ps.url LIKE '%apex%' THEN 10
      WHEN ps.url LIKE '%valorant%' THEN 11
      WHEN ps.url LIKE '%fifa%' OR ps.url LIKE '%fc-%' THEN 12
      ELSE 99
    END
    """
    rows = query(f"""
    SELECT ps.url, ps.updated_at, length(ps.article) AS alen,
           jsonb_array_length(ps.faq) AS faqn
    FROM page_seo ps
    WHERE ps.lang='ru' AND ps.url LIKE '%/t/%'
      AND length(ps.article) >= 400
      AND ps.faq IS NOT NULL AND jsonb_array_length(ps.faq) >= 3
      AND (ps.is_active IS NULL OR ps.is_active = TRUE)
      AND NOT EXISTS (
        SELECT 1 FROM yandex_reindex_log y
        WHERE y.url = ps.url AND y.status='sent' AND y.sent_at > NOW() - INTERVAL '7 days'
      )
    ORDER BY ps.updated_at DESC NULLS LAST, {priority_sql}, ps.url
    LIMIT {limit}
    """)
    return rows


def check_url_alive(url: str, timeout: float = 15.0) -> dict:
    """ОБЯЗАТЕЛЬНАЯ проверка живости URL перед отправкой в Яндекс.
    Добавлено 23.04.2026 после фейла (3 714 пустых URL отправили в индекс).
    
    Возвращает {alive: bool, reason: str}.
    alive=True ТОЛЬКО если:
      - HTTP 200
      - НЕТ текста 'Товар не найден'
      - есть <h1
      - HTML > 1000 байт
    """
    try:
        r = requests.get(url, timeout=timeout, allow_redirects=True)
        if r.status_code != 200:
            return {"alive": False, "reason": f"http_{r.status_code}"}
        body = r.text
        if len(body) < 1000:
            return {"alive": False, "reason": "body_too_short"}
        if 'Товар не найден' in body or 'товар не найден' in body.lower():
            return {"alive": False, "reason": "not_found_in_ssr"}
        if '<h1' not in body:
            return {"alive": False, "reason": "no_h1"}
        return {"alive": True, "reason": "ok"}
    except Exception as e:
        return {"alive": False, "reason": f"exception: {str(e)[:80]}"}


def send_one(url: str, timeout: float = 15.0) -> dict:
    """Отправляет один URL в Яндекс recrawl.
    Возвращает dict: {ok, http_code, response_text, quota_remainder?, skipped_reason?}.
    
    ВАЖНО: с 23.04.2026 перед отправкой делается SSR-проверка.
    Если страница пустая — URL НЕ отправляется, возвращает ok=False, skipped_reason=...
    """
    # P0: SSR-проверка перед отправкой
    alive = check_url_alive(url, timeout=timeout)
    if not alive["alive"]:
        return {
            "ok": False,
            "http_code": 0,
            "response_text": f"skipped (not alive): {alive['reason']}",
            "skipped": True,
            "skipped_reason": alive["reason"],
        }
    
    try:
        r = requests.post(
            f"{YM_BASE}/recrawl/queue",
            headers=YM_HEADERS,
            json={"url": url},
            timeout=timeout,
        )
        body_txt = r.text[:400]
        try:
            body_json = r.json()
        except Exception:
            body_json = {}
        is_success = r.status_code in (200, 201, 202) or body_json.get("task_id") or "quota_remainder" in body_json
        return {
            "ok": bool(is_success),
            "http_code": r.status_code,
            "response_text": body_txt,
            "quota_remainder": body_json.get("quota_remainder"),
        }
    except Exception as e:
        return {"ok": False, "http_code": -1, "response_text": f"exception: {e}"[:400]}


def log_batch_to_db(entries: list) -> int:
    """Массовый INSERT в yandex_reindex_log одним запросом.
    entries: список dict с ключами url, status, http_code, response_text.
    Возвращает число записанных."""
    if not entries:
        return 0
    esc = lambda s: (s or "").replace("'", "''")
    values = []
    for e in entries:
        v = (
            f"('{esc(e['url'])}', '{esc(RECRAWL_DB_HOST)}', '{esc(e['status'])}', "
            f"{e['http_code']}, '{esc(e['response_text'])}', NOW())"
        )
        values.append(v)
    sql = (
        "INSERT INTO yandex_reindex_log (url, host, status, http_code, response, sent_at) VALUES "
        + ",\n".join(values)
        + " RETURNING id::text"
    )
    try:
        query(sql, write=True)
        return len(entries)
    except Exception as e:
        print(f"  ⚠ batch log failed ({len(entries)} entries): {str(e)[:200]}")
        return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=None, help="override: max URLs to send (default = quota_remainder)")
    ap.add_argument("--dry-run", action="store_true", help="only show what would be sent")
    ap.add_argument("--tag", default=None, help="tag for report file")
    args = ap.parse_args()

    # 1. Квота
    q = get_quota()
    if q is None:
        print("❌ Cannot get quota, abort")
        return 1
    print(f"Yandex quota: daily={q['daily_quota']} remainder={q['quota_remainder']}")

    # 2. Кандидаты
    send_count = args.limit if args.limit is not None else q["quota_remainder"]
    send_count = min(send_count, q["quota_remainder"])
    if send_count <= 0:
        if args.dry_run:
            # Preview mode: показать что отправили бы завтра когда квота обновится
            print("Quota is 0, but --dry-run: previewing as if quota=910")
            send_count = args.limit if args.limit is not None else 910
        else:
            print("No quota left today.")
            return 0

    print(f"→ Fetching up to {send_count} candidates (GOOD + not sent 7d)...")
    candidates = fetch_candidates(send_count + 10)  # берём чуть больше для буфера
    print(f"  got {len(candidates)}")
    if not candidates:
        print("Nothing to send.")
        return 0
    candidates = candidates[:send_count]

    # 3. Показываем превью
    print("\nFirst 5 candidates:")
    for c in candidates[:5]:
        print(f"  {c['url']}  alen={c['alen']} faq={c['faqn']} updated={str(c['updated_at'])[:19]}")
    print(f"  ... (total {len(candidates)})")

    if args.dry_run:
        print("\n[DRY-RUN] Exiting without sending")
        return 0

    # 4. Отправка
    print(f"\n→ Sending {len(candidates)} URLs with {THROTTLE_SEC}s throttle...")
    tag = args.tag or f"recrawl_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M')}"
    out_dir = Path("/home/claude/out")
    out_dir.mkdir(parents=True, exist_ok=True)

    results = []
    t0 = time.time()
    success = failed = 0
    last_remainder = q["quota_remainder"]
    pending_log = []
    LOG_BATCH = 50
    logged_total = 0

    for i, c in enumerate(candidates, 1):
        url = c["url"]
        res = send_one(url)
        status = "sent" if res["ok"] else "failed"
        if res["ok"]:
            success += 1
        else:
            failed += 1
        if res.get("quota_remainder") is not None:
            last_remainder = res["quota_remainder"]

        pending_log.append({
            "url": url,
            "status": status,
            "http_code": res["http_code"],
            "response_text": res["response_text"],
        })

        results.append({
            "url": url,
            "status": status,
            "http_code": res["http_code"],
            "quota_remainder": res.get("quota_remainder"),
            "response": res["response_text"][:200],
        })

        # Флашим батч
        if len(pending_log) >= LOG_BATCH:
            logged_total += log_batch_to_db(pending_log)
            pending_log = []

        if i % 50 == 0 or i == len(candidates):
            elapsed = time.time() - t0
            print(f"  [{i:4}/{len(candidates)}] sent={success} failed={failed} "
                  f"quota={last_remainder} logged={logged_total} elapsed={elapsed:.0f}s")

        time.sleep(THROTTLE_SEC)

    # Хвост
    if pending_log:
        logged_total += log_batch_to_db(pending_log)

    elapsed = time.time() - t0
    print(f"\n✅ Done in {elapsed:.0f}s")
    print(f"   sent:    {success}")
    print(f"   failed:  {failed}")
    print(f"   logged:  {logged_total}")
    print(f"   final quota_remainder: {last_remainder}")

    # 5. Итоговый отчёт
    report_path = out_dir / f"{tag}_report.json"
    with report_path.open("w", encoding="utf-8") as f:
        json.dump({
            "started_at": datetime.now(timezone.utc).isoformat(),
            "tag": tag,
            "total_attempted": len(candidates),
            "sent": success,
            "failed": failed,
            "quota_before": q["quota_remainder"],
            "quota_after": last_remainder,
            "elapsed_sec": elapsed,
            "results": results,
        }, f, ensure_ascii=False, indent=2)
    print(f"   report: {report_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
