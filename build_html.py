# -*- coding: utf-8 -*-
"""根据完整历史数据生成自适应网页，所有统计均从最新记录动态计算。"""
import datetime
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent


def _series(hist):
    t0 = datetime.date.fromisoformat(hist[0]["date"])
    base = int(datetime.datetime(t0.year, t0.month, t0.day).timestamp() * 1000)
    days, cong, close = [], [], []
    for h in hist:
        d = datetime.date.fromisoformat(h["date"])
        days.append((d - t0).days)
        cong.append(round(h["congestionPercent"] * 10))
        close.append(round(h["close"] * 10) if h.get("close") is not None else None)
    return {"base": base, "days": days, "cong": cong, "close": close}


def _amount(value):
    return f"{value:,.0f} 亿元" if value is not None else "—"


def render_index(hist, out_path="index.html"):
    if not hist:
        raise ValueError("没有可生成网页的历史数据")
    hist = sorted(hist, key=lambda h: h["date"])
    valid = [h for h in hist if h.get("congestionPercent") is not None]
    last = valid[-1]
    cur = last["congestionPercent"]
    hi_row = max(valid, key=lambda h: h["congestionPercent"])
    lo_row = min(valid, key=lambda h: h["congestionPercent"])
    previous = valid[-2]["congestionPercent"] if len(valid) > 1 else cur
    trend = "集中度上升，关注局部过热" if cur >= previous else "集中度回落"
    percentile = sum(h["congestionPercent"] < cur for h in valid) / len(valid) * 100
    latest_close = next((h["close"] for h in reversed(valid) if h.get("close") is not None), None)
    replacements = {
        "@@ASOF@@": last["date"],
        "@@CUR@@": f"{cur:.2f}",
        "@@TREND@@": trend,
        "@@PERCENTILE@@": f"{percentile:.1f}",
        "@@CLOSE@@": f"{latest_close:.2f}" if latest_close is not None else "—",
        "@@TOTAL@@": _amount(last.get("totalAmountYi")),
        "@@TOP5@@": _amount(last.get("top5AmountYi")),
        "@@HI@@": f"{hi_row['congestionPercent']:.1f}% · {hi_row['date']}",
        "@@LO@@": f"{lo_row['congestionPercent']:.1f}% · {lo_row['date']}",
        "@@DAYS40@@": str(sum(h["congestionPercent"] >= 40 for h in valid)),
        "@@DAYS50@@": str(sum(h["congestionPercent"] >= 50 for h in valid)),
        "@@DATA@@": json.dumps(_series(valid), ensure_ascii=False, separators=(",", ":")),
    }
    echarts_path = BASE / "echarts.min.js"
    if echarts_path.exists():
        echarts = "<script>/* ECharts 5.5.0 已内嵌 */\n" + echarts_path.read_text(encoding="utf-8") + "\n</script>"
    else:
        echarts = '<script src="https://cdn.bootcdn.net/ajax/libs/echarts/5.5.0/echarts.min.js"></script>'
    replacements["@@ECHARTS@@"] = echarts
    html = (BASE / "template.html").read_text(encoding="utf-8")
    for key, value in replacements.items():
        html = html.replace(key, value)
    if "@@" in html:
        raise ValueError("网页模板仍有未替换的占位符")
    output = Path(out_path)
    if not output.is_absolute():
        output = BASE / output
    output.write_text(html, encoding="utf-8")


def render(hist, out_path="大盘拥挤度_A股.html"):
    """兼容每日更新脚本的桌面版入口。"""
    render_index(hist, out_path)


if __name__ == "__main__":
    hist = [json.loads(line) for line in (BASE / "congestion_daily.csv").read_text(encoding="utf-8").splitlines() if line.strip()]
    for filename in ("index.html", "desktop.html", "大盘拥挤度_A股.html"):
        render_index(hist, filename)
    print(f"已根据 {len(hist)} 条记录重新生成全部网页")
