#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""A股大盘拥挤度 · 每日自动更新
口径: 沪深A股(新浪 hs_a 节点) 成交额排名前5%个股成交额 / 全市场成交额
用法: 每个交易日 15:40 之后运行  python3 update_congestion.py
产出: congestion_daily.csv (累积历史) + 大盘拥挤度_A股.html (自包含交互图表)
"""
import hashlib, json, math, os, datetime, urllib.request, http.cookiejar

BASE = os.path.dirname(os.path.abspath(__file__))
HIST = os.path.join(BASE, "congestion_daily.csv")
HTML = os.path.join(BASE, "大盘拥挤度_A股.html")
UA = {"User-Agent": "Mozilla/5.0", "Referer": "https://finance.sina.com.cn/stock/"}

def legulegu_baseline():
    """乐咕乐股全历史基线(免费接口约有数月延迟)"""
    cj = http.cookiejar.CookieJar()
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    op.open(urllib.request.Request("https://www.legulegu.com/stockdata/ashares-congestion",
            headers={"User-Agent": "Mozilla/5.0"}), timeout=20)
    today = datetime.date.today()
    for delta in (0, -1, 1, 2):
        token = hashlib.md5((today + datetime.timedelta(days=delta)).strftime("%Y-%m-%d").encode()).hexdigest()
        try:
            raw = op.open(urllib.request.Request(
                f"https://www.legulegu.com/api/stockdata/ashares-congestion?token={token}",
                headers={"User-Agent": "Mozilla/5.0",
                         "Referer": "https://www.legulegu.com/stockdata/ashares-congestion"}), timeout=60).read()
            items = json.loads(raw)["items"]
            return [x for x in items if x.get("congestion") is not None]
        except Exception:
            continue
    return []

def sina_snapshot():
    """新浪沪深A股当日快照 -> 当日拥挤度"""
    rows, page = [], 1
    while True:
        url = ("https://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/"
               f"Market_Center.getHQNodeData?page={page}&num=100&node=hs_a&sort=amount&asc=0")
        try:
            batch = json.loads(urllib.request.urlopen(
                urllib.request.Request(url, headers=UA), timeout=15).read().decode("gbk", "ignore"))
        except Exception:
            return None
        if not batch:
            break
        rows.extend(batch); page += 1
        if page > 80:
            break
    if len(rows) < 3000:
        return None
    amt = sorted((float(r["amount"]) for r in rows), reverse=True)
    k = math.ceil(len(amt) * 0.05)
    return {"n": len(amt), "k": k,
            "totalAmountYi": round(sum(amt) / 1e8),
            "top5AmountYi": round(sum(amt[:k]) / 1e8)}

def sh_close(datestr):
    try:
        url = ("https://hq.sinajs.cn/list=s_sh000001")
        t = urllib.request.urlopen(urllib.request.Request(
            url, headers={"User-Agent": "Mozilla/5.0", "Referer": "https://finance.sina.com.cn"}),
            timeout=10).read().decode("gbk", "ignore")
        return round(float(t.split(",")[1]), 2)
    except Exception:
        return None

def main():
    # 1) 基线
    base = legulegu_baseline()
    hist = []
    if os.path.exists(HIST):
        hist = [json.loads(l) for l in open(HIST, encoding="utf-8") if l.strip()]
    if base:
        have = {h["date"] for h in hist}
        for it in base:
            if it["date"] not in have:
                hist.append({"date": it["date"], "congestionPercent": round(it["congestion"] * 100, 2),
                             "close": it["close"]})
    # 2) 今日(新浪快照实时计算)
    snap = sina_snapshot()
    today = datetime.date.today().strftime("%Y-%m-%d")
    wd = datetime.date.today().weekday()
    if snap and wd < 5:
        last_total = hist[-1].get("totalAmountYi") if hist else None
        if not any(h["date"] == today for h in hist) and snap["totalAmountYi"] != last_total:
            cong = round(snap["top5AmountYi"] / snap["totalAmountYi"] * 100, 2)
            row = {"date": today, "congestionPercent": cong,
                   "close": sh_close(today), **snap}
            hist.append(row)
            print(f"[追加] {today} 拥挤度 {cong}%  (全市场 {snap['totalAmountYi']}亿 / 前5% {snap['top5AmountYi']}亿)")
    hist.sort(key=lambda x: x["date"])
    with open(HIST, "w", encoding="utf-8") as f:
        for h in hist:
            f.write(json.dumps(h, ensure_ascii=False) + "\n")
    # 3) 生成 HTML
    import build_html  # noqa  若同目录存在 build_html.py 则调用
    build_html.render(hist, HTML)
    print(f"完成: {len(hist)} 条 -> {HTML}")

if __name__ == "__main__":
    main()
