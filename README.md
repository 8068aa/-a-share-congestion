# A股大盘拥挤度 · 在线应用（手机竖屏版）

沪深A股成交额排名前 5% 个股成交额占全市场比重，叠加上证指数。
历史基线 2011-09 起；每日收盘后由 GitHub Actions 自动抓取新浪快照计算并更新。

## 页面
- `index.html`   手机竖屏版（单列布局，推荐，桌面打开也居中可用）
- `desktop.html` 桌面双栏版（按公众号截图 1:1 还原）

## 一键部署（5 分钟）
1. GitHub 新建仓库（如 `a-share-congestion`），上传本目录全部文件（或上传 congestion-app.zip 解压）
2. Settings → Pages → Source 选 `main` 分支 `/ (root)`，保存
3. 等 1-2 分钟，访问 `https://<你的用户名>.github.io/<仓库名>/`
4. 手机浏览器打开 → 菜单「添加到主屏幕」→ 桌面图标，体验等同 App

## 数据更新
- 每个工作日 15:50（北京时间）自动运行，也可 Actions 页签手动 Run workflow
- 首次运行会把乐咕乐股全历史基线 + 新浪当日快照合并写入 congestion_daily.csv
- 本地运行：python update_congestion.py（重新生成 大盘拥挤度_A股.html）

## 口径
拥挤度 = 沪深A股(新浪 hs_a) 成交额降序前 5% 个股合计 / 全市场合计。
2026-10-16 自算 41.66% 与乐咕乐股官方值一致。
