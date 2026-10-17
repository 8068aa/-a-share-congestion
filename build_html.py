# -*- coding: utf-8 -*-
"""由累积历史生成自包含 ECharts 交互页"""
import json, datetime

TPL = r"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>A股大盘拥挤度 · 成交额前5%占比</title>
<script src="https://cdn.jsdelivr.net/npm/echarts@5.5.0/dist/echarts.min.js"></script>
<style>
body{margin:0;background:#f6f7f9;font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;color:#222}
.card{max-width:1280px;margin:24px auto;background:#fff;border-radius:12px;box-shadow:0 1px 8px rgba(0,0,0,.06);padding:22px 26px;display:flex;gap:26px}
.side{width:230px;flex:none}
h1{font-size:17px;margin:0;display:inline}
.tag{background:#fdeec9;color:#b8860b;font-size:11px;border-radius:4px;padding:2px 6px;margin-left:8px}
.asof{font-size:12px;color:#999;margin-left:8px}
.big{font-size:46px;font-weight:700;color:#f5a623;margin:10px 0 2px;line-height:1;font-variant-numeric:tabular-nums}
.big small{font-size:20px}
.sub{font-size:12px;color:#888;margin-bottom:14px}
.row{display:flex;justify-content:space-between;font-size:13px;padding:7px 0;border-top:1px solid #f0f0f0}
.row span:first-child{color:#999}
.row b{font-weight:600;font-variant-numeric:tabular-nums}
.dot{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:6px}
.main{flex:1;min-width:0}
.bar{display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;flex-wrap:wrap;gap:8px}
.btns{display:flex;background:#f1f2f4;border-radius:10px;padding:3px;gap:2px}
.btns button{border:0;background:transparent;padding:6px 14px;border-radius:8px;font-size:13px;cursor:pointer;color:#555}
.btns button.on{background:#222;color:#fff}
.btns button.dark{background:#222;color:#fff}
.leg{font-size:12px;color:#777}.leg i{display:inline-block;width:14px;height:3px;vertical-align:middle;margin:0 4px 0 12px}
#chart{width:100%;height:520px}
.foot{font-size:11px;color:#aaa;margin-top:4px}
@media(max-width:900px){.card{flex-direction:column}.side{width:100%}}
</style></head><body><div class="card">
<div class="side">
  <div><h1>大盘拥挤度</h1><span class="tag">关注</span><span class="asof">截至 @@ASOF@@</span></div>
  <div class="big">@@CUR@@<small>%</small></div>
  <div class="sub">@@TREND@@ · 超过 @@RANK@@% 的历史交易日</div>
  <div class="row"><span>上证指数</span><b>@@CLOSE@@</b></div>
  <div class="row"><span>全市场成交额</span><b>@@TOTAL@@</b></div>
  <div class="row"><span>前 5% 个股成交额</span><b>@@TOP5@@</b></div>
  <div class="row"><span>历史最高</span><b>@@HI@@</b></div>
  <div class="row"><span>历史最低</span><b>@@LO@@</b></div>
  <div class="row"><span><i class="dot" style="background:#f5a623"></i>关注线 40%</span><b>累计 @@D40@@ 天</b></div>
  <div class="row"><span><i class="dot" style="background:#e03131"></i>预警线 50%</span><b>累计 @@D50@@ 天</b></div>
</div>
<div class="main">
  <div class="bar">
    <div class="btns">
      <button data-r="1y">近1年</button><button data-r="3y">近3年</button>
      <button data-r="5y">近5年</button><button data-r="all" class="on">全部</button>
      <button id="shBtn" class="dark">叠加上证指数</button>
    </div>
    <div class="leg"><i style="background:#1971c2"></i>拥挤度(左轴)<i style="background:#e03131"></i>上证指数(右轴)</div>
  </div>
  <div id="chart"></div>
  <div class="foot">口径：沪深A股成交额排名前5%个股成交额占全市场比重 · 数据源：新浪财经快照实时计算（全历史基线：乐咕乐股）· 每交易日收盘后自动更新 · 2026-10-16 自算 41.66% 与乐咕乐股官方值一致</div>
</div></div>
<script>
var DATA = @@DATA@@;
var chart = echarts.init(document.getElementById('chart'), null, {renderer:'canvas'});
function seriesData(key){ return DATA.days.map(function(d,i){ return [DATA.base + d*86400000, DATA[key][i]/10]; }); }
var gapAt = DATA.days.length - 2;   // 基线末条 -> 最新点(虚线)
var congAll = seriesData('cong'), closeAll = seriesData('close');
var opt = {
  animation:false,
  grid:{left:52,right:64,top:30,bottom:46},
  legend:{show:false},
  tooltip:{trigger:'axis',axisPointer:{type:'cross',label:{show:false}},
    formatter:function(ps){var d=new Date(ps[0].value[0]);var s=d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');
      ps.forEach(function(p){if(p.seriesName!=='gap')s+='<br>'+p.marker+p.seriesName+'：<b>'+(p.seriesName.indexOf('上证')>=0?p.value[1].toFixed(2):p.value[1].toFixed(1)+'%')+'</b>';});
      return s;}},
  xAxis:{type:'time',axisLine:{lineStyle:{color:'#ddd'}},axisLabel:{color:'#999',fontSize:11}},
  yAxis:[
    {type:'value',min:0,max:60,name:'拥挤度',position:'left',axisLabel:{formatter:'{value}%',color:'#999'},splitLine:{lineStyle:{color:'#f2f2f2'}}},
    {type:'value',name:'上证指数',position:'right',scale:true,axisLabel:{color:'#c92a2a'},splitLine:{show:false}}
  ],
  series:[
    {name:'拥挤度(左轴)',type:'line',yAxisIndex:0,data:congAll.slice(0,gapAt+1),showSymbol:false,z:3,
     lineStyle:{width:1.6,color:'#1971c2'},
     markLine:{silent:true,symbol:'none',data:[
       {yAxis:40,lineStyle:{color:'#f5a623',type:'dashed'},label:{formatter:'40% 关注线',position:'insideEndTop',color:'#f5a623',fontSize:11}},
       {yAxis:50,lineStyle:{color:'#e03131',type:'dashed'},label:{formatter:'50% 预警线',position:'insideEndTop',color:'#e03131',fontSize:11}}]}},
    {name:'gap',type:'line',yAxisIndex:0,data:[congAll[gapAt],congAll[congAll.length-1]],showSymbol:false,z:2,
     lineStyle:{width:1.6,color:'#1971c2',type:'dashed'}},
    {name:'上证指数(右轴)',type:'line',yAxisIndex:1,data:closeAll,showSymbol:false,z:1,
     lineStyle:{width:1.4,color:'#e03131',opacity:.85}}
  ]
};
chart.setOption(opt);
var showSH = true;
document.querySelectorAll('.btns button[data-r]').forEach(function(b){
  b.onclick=function(){
    document.querySelectorAll('.btns button[data-r]').forEach(function(x){x.classList.remove('on')});
    b.classList.add('on');
    var r=b.dataset.r, max=DATA.base+DATA.days[DATA.days.length-1]*86400000;
    var daysMap={'1y':365,'3y':1096,'5y':1827};
    chart.setOption({xAxis:{min: r==='all'?null:max-daysMap[r]*86400000, max:max}});
  };
});
document.getElementById('shBtn').onclick=function(){
  showSH=!showSH; this.classList.toggle('dark',showSH);
  chart.setOption({legend:{show:false}, series:[{},{},{lineStyle:{opacity:showSH?.85:0}}],
                   yAxis:[{},{show:showSH}]});
};
window.addEventListener('resize',function(){chart.resize()});
</script></body></html>"""

def render(hist, out_path):
    pcts = [h["congestionPercent"] for h in hist if h.get("congestionPercent") is not None]
    last = hist[-1]
    cur = last["congestionPercent"]
    d40 = sum(1 for p in pcts if p >= 40); d50 = sum(1 for p in pcts if p >= 50)
    hi, lo = max(pcts), min(pcts)
    hi_d = next(h["date"] for h in hist if h["congestionPercent"] == hi)
    lo_d = next(h["date"] for h in hist if h["congestionPercent"] == lo)
    rank = round(sum(1 for p in pcts if p < cur) / len(pcts) * 100, 1)
    trend = "集中度上升，关注局部过热" if cur > pcts[-2] else "集中度回落"
    t0 = datetime.date.fromisoformat(hist[0]["date"]); base = int(datetime.datetime(t0.year, t0.month, t0.day).timestamp() * 1000)
    days, cong, close = [], [], []
    for h in hist:
        d = datetime.date.fromisoformat(h["date"])
        days.append((d - t0).days)
        cong.append(round(h["congestionPercent"] * 10))
        close.append(round(h["close"] * 10) if h.get("close") else None)
    data = {"base": base, "days": days, "cong": cong, "close": close}
    fmt_yi = lambda v: ("%.2f万亿" % (v / 10000)) if v and v >= 10000 else (("%d亿" % v) if v else "—")
    html = (TPL
        .replace("@@ASOF@@", last["date"]).replace("@@CUR@@", "%.2f" % cur)
        .replace("@@TREND@@", trend).replace("@@RANK@@", str(rank))
        .replace("@@CLOSE@@", "%.2f" % last["close"] if last.get("close") else "—")
        .replace("@@TOTAL@@", fmt_yi(last.get("totalAmountYi")))
        .replace("@@TOP5@@", fmt_yi(last.get("top5AmountYi")))
        .replace("@@HI@@", "%.1f%% · %s" % (hi, hi_d)).replace("@@LO@@", "%.1f%% · %s" % (lo, lo_d))
        .replace("@@D40@@", str(d40)).replace("@@D50@@", str(d50))
        .replace("@@DATA@@", json.dumps(data, ensure_ascii=False, separators=(",", ":"))))
    open(out_path, "w", encoding="utf-8").write(html)
    return html

if __name__ == "__main__":
    hist = [json.loads(l) for l in open("congestion_daily.csv", encoding="utf-8") if l.strip()]
    render(hist, "大盘拥挤度_A股.html")
