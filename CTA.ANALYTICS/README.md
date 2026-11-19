![十年特别奖选手分析｜Futures Trading · Ten-Year Special Award](./github-cover-en.png)

[中文](#十年特别奖选手特征分析) · [English](#english) · [界面预览 / Gallery](#界面预览--dashboard-gallery)

# 十年特别奖选手特征分析

这是一个基于期货日报公开赛事数据的金融大数据实践项目。我们围绕全国期货实盘交易大赛「十年特别奖」选手，分析他们的收益、交易表现和风险控制特征，并用第 11–19 届历史数据预测第 20 届组内综合名次。

## 项目功能

- **十年特别奖专题**：按特别奖总榜名次分层，比较两届累计净值均大于 1 的比例，以及胜率、最大回撤等指标。
- **选手画像**：按昵称查询收益、风险和交易指标，查看历届账户明细。部分账户支持查看日度净值曲线。
- **群体对比**：通过单项指标分布、多维聚类、交易风格和历届趋势，比较不同选手群体及排名区间。
- **名次预测**：分别预测具体名次与五档名次区间，通过散点图、混淆矩阵和逐条明细对照官网实际名次。

## 项目亮点

- **跨届数据关联**：结合原有第 6–18 届历史明细与官网补采的第 19、20 届收官数据，按选手和组别匹配。第 20 届有 **379 条**记录可用于回顾性评估。
- **同批样本比较**：在同一批评估记录上，具体名次的中位绝对误差从旧岭回归的 **1,099 名**降至 **678 名**。五档区间另行评估，同时展示命中率、宏平均 F1 和头部识别表现。
- **离线浏览**：看板使用本地 ECharts 和预生成数据。下载项目后，双击 `可视化平台/index.html` 即可查看，重建数据时再使用 Python。

[查看数据来源、评估口径与重建方式](./可视化平台/README.md)


## 界面预览 · Dashboard gallery

### 总览 · Overview

查看历史样本规模、各届采集记录和参赛组别构成，并进入特别奖专题或选手画像。  
See dataset coverage, record counts by edition, and the competition group breakdown.

![总览页面 | Dashboard overview](./docs/screenshots/index.jpg)

<details>
<summary><strong>十年特别奖专题 · Ten-Year Special Award</strong></summary>

按特别奖总榜名次分层，对比两届累计净值均大于 1 的比例，以及第 19 届的胜率、回撤和风险度。  
Compare award leaderboard tiers by the share of accounts with cumulative NAV above 1 in both editions, plus their edition 19 win rates, drawdowns, and risk levels.

![十年特别奖专题 | Ten-Year Special Award analysis](./docs/screenshots/award.jpg)

</details>

<details>
<summary><strong>选手综合画像 · Trader profiles</strong></summary>

按昵称检索选手，查看收益、风险和交易指标、历届账户明细，以及部分账户的日度净值。  
Search by nickname to view returns, risk, trading metrics, and account history. Daily NAV is available for selected accounts.

![选手综合画像 | Trader profiles](./docs/screenshots/players.jpg)

</details>

<details>
<summary><strong>指标分布 · Indicator distributions</strong></summary>

切换六项交易指标，查看分布、统计摘要和高低值选手。  
Switch between six trading indicators to explore distributions, summary statistics, and traders with the highest or lowest values.

![指标分布 | Indicator distributions](./docs/screenshots/single.jpg)

</details>

<details>
<summary><strong>多维人群 · Trader clusters</strong></summary>

用主成分散点图和雷达图观察聚类结果，对比各人群的指标特征。  
Explore trader clusters with a PCA scatter plot and compare their indicator profiles with a radar chart.

![多维人群 | Trader clusters](./docs/screenshots/cluster.jpg)

</details>

<details>
<summary><strong>交易风格 · Trading styles</strong></summary>

查看不同交易风格的样本占比，并比较各类选手的收益与风险指标。  
See how common each trading style is and compare return and risk indicators across styles.

![交易风格 | Trading styles](./docs/screenshots/style.jpg)

</details>

<details>
<summary><strong>排名区间对比 · Rank group comparison</strong></summary>

按同届同组名次筛选样本，对照前 50、前 200 与样本内后 20 等区间的收益和风险。  
Compare returns and risk across within-edition, within-group rank cutoffs, including the top 50, top 200, and the sample's bottom 20.

![排名区间对比 | Rank group comparison](./docs/screenshots/rank.jpg)

</details>

<details>
<summary><strong>历届表现趋势 · Trends by edition</strong></summary>

查看第 6–18 届样本的核心指标变化，并对照各届样本人数。  
Track changes in key indicators and compare sample sizes across editions 6–18.

![历届表现趋势 | Trends by edition](./docs/screenshots/trend.jpg)

</details>

<details>
<summary><strong>第 20 届预测评估 · Edition 20 forecasting and evaluation</strong></summary>

查看 379 条匹配记录的预测与实际名次、误差指标和五档区间混淆矩阵。  
Compare predicted and official ranks for 379 matched records, with error metrics and a five-band confusion matrix.

![第 20 届预测评估 | Edition 20 forecasting and evaluation](./docs/screenshots/predict.jpg)

</details>

## English

### Futures Traders · Ten-Year Special Award

This data analytics project studies participants in the Ten-Year Special Award of China’s National Futures Trading Competition, using public competition data from Futures Daily. It compares trader performance and risk across groups and uses records from editions 11–19 to forecast within-group ranks for edition 20.

### Features

- **Special Award analysis** — Compare returns, win rates, and drawdowns across leaderboard tiers, including the share of linked accounts with cumulative net asset value above 1 in both editions.
- **Trader profiles** — Search by nickname to explore returns, risk, and account history. Daily net asset value charts are available for accounts with daily records.
- **Group comparisons** — Explore indicator distributions, clusters, trading styles, and trends across editions and rank groups.
- **Rank forecasting** — Predict numerical ranks and five rank bands separately. Compare predictions with official results using a scatter plot, a confusion matrix, and a record-level table.

### Highlights

- **Cross-edition data** — The project combines historical records from editions 6–18 with official closing records from editions 19 and 20. The retrospective edition 20 evaluation covers **379 matched records**.
- **Same-sample evaluation** — Median absolute rank error fell from **1,099 ranks** with ridge regression to **678 ranks** with the selected point forecast method. Rank-band results are reported separately.
- **Offline dashboard** — Open `可视化平台/index.html` in a browser. Data and ECharts are bundled locally. Python is used to rebuild the dashboard data.

[Data sources, evaluation details, and rebuild instructions (Chinese)](./可视化平台/README.md)
