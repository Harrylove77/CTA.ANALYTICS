import matplotlib
matplotlib.use('TkAgg')
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# 设置中文字体为黑体并解决负号显示问题
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

# 读取数据
data = pd.read_csv(r"C:\Users\Administrator\Desktop\大数据综合实践\数据分析结果\排名区间分析\排名区间分析.csv")
data.set_index('Unnamed: 0', inplace=True)

# 1. 堆积柱状图展示各区间关键指标对比
plt.figure(figsize=(12, 8))
bar_width = 0.35
r1 = np.arange(len(data))
r2 = [x + bar_width for x in r1]
r3 = [x + bar_width for x in r2]
r4 = [x + bar_width for x in r3]

plt.bar(r1, data['累计净值'], width=bar_width, label='累计净值')
plt.bar(r2, data['交易胜率'], width=bar_width, label='交易胜率')
plt.bar(r3, data['盈亏比'], width=bar_width, label='盈亏比')
plt.bar(r4, data['日收益率均值'], width=bar_width, label='日收益率均值')

plt.xlabel('排名区间', fontweight='bold')
plt.ylabel('指标数值', fontweight='bold')
plt.title('不同排名区间关键指标对比', fontweight='bold')
plt.xticks([r + bar_width for r in range(len(data))], data.index)
plt.legend()
plt.show()

# 2. 折线图展示排名区间与累计净值关系
plt.figure(figsize=(12, 6))
plt.plot(data.index, data['累计净值'], marker='o', linestyle='-', color='b')
plt.xlabel('排名区间', fontweight='bold')
plt.ylabel('累计净值', fontweight='bold')
plt.title('排名区间与累计净值的关系', fontweight='bold')
plt.grid(True)
plt.show()

# 3. 箱线图分析各指标数据分布
data_melt = pd.melt(data.reset_index(), id_vars=['index'], value_vars=['累计净值', '交易胜率', '盈亏比', '最大回撤率', '风险度均值', '日收益率均值'])
plt.figure(figsize=(12, 8))
sns.boxplot(x='index', y='value', hue='variable', data=data_melt)
plt.xlabel('排名区间', fontweight='bold')
plt.ylabel('指标数值', fontweight='bold')
plt.title('各指标在不同排名区间的数据分布', fontweight='bold')
plt.legend(title='指标')
plt.show()