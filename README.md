<img width="2172" height="724" alt="image" src="https://github.com/user-attachments/assets/5c5b2411-cfeb-4814-adb3-9b63a90516cc" />

[中文](#十年特别奖选手特征分析) · [English](#english) · [界面预览 / Gallery](#界面预览--dashboard-gallery)
# 十年特别奖选手特征分析

这是一个基于期货日报公开赛事数据的金融大数据实践项目。我们围绕全国期货实盘交易大赛「十年特别奖」选手，分析他们的收益、交易表现和风险控制特征，并用第 11–19 届历史数据预测第 20 届组内综合名次。

## 项目功能

- **十年特别奖专题**：按特别奖总榜名次分层，比较两届累计净值均大于 1 的比例，以及胜率、最大回撤等指标。
- **选手画像**：按昵称查询收益、风险和交易指标，查看历届账户明细。部分账户支持查看日度净值曲线。
- **群体对比**：通过单项指标分布、多维聚类、交易风格和历届趋势，比较不同选手群体及排名区间。
- **名次预测**：分别预测具体名次与五档名次区间，通过散点图、混淆矩阵和逐条明细对照官网实际名次。

[查看数据来源、评估口径与重建方式](./可视化平台/README.md)

## English

### Futures Traders · Ten-Year Special Award

This data analytics project studies participants in the Ten-Year Special Award of China’s National Futures Trading Competition, using public competition data from Futures Daily. It compares trader performance and risk across groups and uses records from editions 11–19 to forecast within-group ranks for edition 20.

### Features

- **Special Award analysis** — Compare returns, win rates, and drawdowns across leaderboard tiers, including the share of linked accounts with cumulative net asset value above 1 in both editions.
- **Trader profiles** — Search by nickname to explore returns, risk, and account history. Daily net asset value charts are available for accounts with daily records.
- **Group comparisons** — Explore indicator distributions, clusters, trading styles, and trends across editions and rank groups.
- **Rank forecasting** — Predict numerical ranks and five rank bands separately. Compare predictions with official results using a scatter plot, a confusion matrix, and a record-level table.

[Data sources, evaluation details, and rebuild instructions (Chinese)](./可视化平台/README.md)

## 界面预览 · Dashboard gallery

以下为九个界面的完整页面截图，包含首屏下方的图表和明细。可点击截图查看原图。

The nine full-page screenshots include charts and details below the first screen. Click a screenshot to view it at full size.

### 总览 · Overview

查看历史样本规模、各届采集记录和参赛组别构成，并进入特别奖专题或选手画像。  
See dataset coverage, record counts by edition, and the competition group breakdown.

<img width="1916" height="917" alt="image" src="https://github.com/user-attachments/assets/d8f18aee-cd17-4dcc-b503-4ab3b31c6bd8" />
<img width="1908" height="918" alt="image" src="https://github.com/user-attachments/assets/ac05b652-fc39-44ae-b4e7-8f70acde9d99" />




### 十年特别奖专题 · Ten-Year Special Award

按特别奖总榜名次分层，对比两届累计净值均大于 1 的比例，以及第 19 届的胜率、回撤和风险度。  
Compare award leaderboard tiers by the share of accounts with cumulative NAV above 1 in both editions, plus their edition 19 win rates, drawdowns, and risk levels.

<img width="1440" height="939" alt="award" src="https://github.com/user-attachments/assets/72b75c30-1c88-444f-ba60-9f68b88bdb28" />



### 选手综合画像 · Trader profiles

按昵称检索选手，查看收益、风险和交易指标、历届账户明细，以及部分账户的日度净值。  
Search by nickname to view returns, risk, trading metrics, and account history. Daily NAV is available for selected accounts.

<img width="1440" height="1399" alt="players" src="https://github.com/user-attachments/assets/36d4d493-896a-45bc-acda-18d439748f8e" />



### 指标分布 · Indicator distributions

切换六项交易指标，查看分布、统计摘要和高低值选手。  
Switch between six trading indicators to explore distributions, summary statistics, and traders with the highest or lowest values.

<img width="1440" height="1110" alt="single" src="https://github.com/user-attachments/assets/faf163cd-270d-4d6b-94f4-35d6246884e5" />


### 多维人群 · Trader clusters

用主成分散点图和雷达图观察聚类结果，对比各人群的指标特征。  
Explore trader clusters with a PCA scatter plot and compare their indicator profiles with a radar chart.

<img width="1440" height="983" alt="cluster" src="https://github.com/user-attachments/assets/ed97717e-1b46-4f6f-9298-de74a6f3b59c" />


### 交易风格 · Trading styles

查看不同交易风格的样本占比，并比较各类选手的收益与风险指标。  
See how common each trading style is and compare return and risk indicators across styles.

<img width="1440" height="966" alt="style" src="https://github.com/user-attachments/assets/b6954ae3-e440-4453-9bcf-976979d0fea6" />


### 排名区间对比 · Rank group comparison

按同届同组名次筛选样本，对照前 50、前 200 与样本内后 20 等区间的收益和风险。  
Compare returns and risk across within-edition, within-group rank cutoffs, including the top 50, top 200, and the sample's bottom 20.

<img width="1440" height="1238" alt="rank" src="https://github.com/user-attachments/assets/8c8d9cd1-8793-4bc9-8629-be9281be540a" />


### 历届表现趋势 · Trends by edition

查看第 6–19 届样本的核心指标变化，并对照各届样本人数。  
Track changes in key indicators and compare sample sizes across editions 6–19.

<img width="1173" height="852" alt="image" src="https://github.com/user-attachments/assets/9484c7d5-3b77-433f-86c0-0eacfdec2e78" />



### 第 20 届预测评估 · Edition 20 forecasting and evaluation

查看 379 条匹配记录的预测与实际名次、误差指标和五档区间混淆矩阵。  
Compare predicted and official ranks for 379 matched records, with error metrics and a five-band confusion matrix.
<img width="593" height="706" alt="image" src="https://github.com/user-attachments/assets/dd381b64-86e5-4e7c-96de-4af9001ccb62" />

