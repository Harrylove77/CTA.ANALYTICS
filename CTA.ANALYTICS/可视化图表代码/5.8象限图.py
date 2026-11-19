import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# 读取数据
df = pd.read_csv(r"C:\Users\Administrator\Desktop\大数据综合实践\数据分析结果\多指标分析结果.csv")

# 设置图片清晰度
plt.rcParams['figure.dpi'] = 300

# 设置中文字体，使用系统中存在的字体，如 SimHei（黑体）
plt.rcParams['font.sans-serif'] = ['SimHei']
# 解决负号显示问题
plt.rcParams['axes.unicode_minus'] = False

# 切换 Matplotlib 后端
plt.switch_backend('TkAgg')

# 根据日收益率均值确定颜色
colors = np.where(df['日收益率均值'] > 0, 'green', 'red')

# 绘制气泡图
plt.scatter(df['交易胜率'], df['盈亏比'], s=df['累计净值'] * 10, c=colors, alpha=0.6)

# 添加标题和轴标签
plt.title('交易胜率 vs. 盈亏比（气泡图）')
plt.xlabel('交易胜率')
plt.ylabel('盈亏比')

# 标记理想策略和需淘汰策略
try:
    plt.annotate('理想策略（如169403）', xy=(df.loc[df['标准客户昵称'] == '169403', '交易胜率'].values[0],
                                           df.loc[df['标准客户昵称'] == '169403', '盈亏比'].values[0]),
                 xytext=(-50, -30),
                 textcoords='offset points', arrowprops=dict(arrowstyle='->'))
    plt.annotate('需淘汰策略（如173899）', xy=(df.loc[df['标准客户昵称'] == '173899', '交易胜率'].values[0],
                                             df.loc[df['标准客户昵称'] == '173899', '盈亏比'].values[0]),
                 xytext=(30, 30),
                 textcoords='offset points', arrowprops=dict(arrowstyle='->'))
except IndexError:
    print('数据中可能不存在指定的客户昵称，无法进行标注。')

# 显示气泡图
plt.show()

# 按聚类分组
cluster_0 = df[df['聚类'] == 0]['风险度均值']
cluster_1 = df[df['聚类'] == 1]['风险度均值']

# 绘制箱线图
plt.figure()
plt.boxplot([cluster_0, cluster_1], labels=['聚类 0', '聚类 1'])
plt.title('风险度均值分布（箱线图）')
plt.ylabel('风险度均值')

# 标记异常值，设置步长过滤部分异常值
step = 2  # 可调整步长来控制标记的密度
outliers_0 = cluster_0[cluster_0 > 90]
outliers_1 = cluster_1[cluster_1 > 90]
for i, outlier in enumerate(outliers_0):
    if i % step == 0:
        plt.annotate(f'{outlier:.2f}', xy=(1, outlier), xytext=(1 + 0.1, outlier),
                     arrowprops=dict(arrowstyle='->'))
for i, outlier in enumerate(outliers_1):
    if i % step == 0:
        plt.annotate(f'{outlier:.2f}', xy=(2, outlier), xytext=(2 + 0.1, outlier),
                     arrowprops=dict(arrowstyle='->'))

# 显示箱线图
plt.show()

# 选取需要分析的指标
selected_columns = ['累计净值', '交易胜率', '盈亏比', '最大回撤率']
df_selected = df[selected_columns]

# 计算相关系数矩阵
correlation_matrix = df_selected.corr()

# 绘制相关性热力图
plt.figure()
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', vmin=-1, vmax=1)
plt.title('指标间相关性热力图')
plt.show()

# 多维雷达图部分
# 选取指标
metrics = ['累计净值', '交易胜率', '盈亏比', '最大回撤率', '风险度均值', '日收益率均值']
df_metrics = df[metrics]

# 计算平均水平
mean_values = df_metrics.mean().values

# 选择优质客户和高风险客户
high_quality_customer = df[df['标准客户昵称'] == '169427'][metrics].values[0]
high_risk_customer = df[df['标准客户昵称'] == '173620'][metrics].values[0]

# 设置角度
angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False)
angles = np.concatenate((angles, [angles[0]]))

# 添加最后一个值以闭合图形
mean_values = np.concatenate((mean_values, [mean_values[0]]))
high_quality_customer = np.concatenate((high_quality_customer, [high_quality_customer[0]]))
high_risk_customer = np.concatenate((high_risk_customer, [high_risk_customer[0]]))

# 创建雷达图
fig = plt.figure()
ax = fig.add_subplot(111, polar=True)

# 绘制平均水平
ax.plot(angles, mean_values, 'b-', linewidth=1, label='平均水平')
ax.fill(angles, mean_values, alpha=0.25, color='blue')

# 绘制优质客户
ax.plot(angles, high_quality_customer, 'g-', linewidth=1, label='优质客户 (169427)')
ax.fill(angles, high_quality_customer, alpha=0.25, color='green')

# 绘制高风险客户
ax.plot(angles, high_risk_customer, 'r-', linewidth=1, label='高风险客户 (173620)')
ax.fill(angles, high_risk_customer, alpha=0.25, color='red')

# 设置标签
ax.set_thetagrids(angles[:-1] * 180 / np.pi, metrics)
plt.title('多维雷达图：单个客户与平均水平对比')
plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
plt.show()

# 象限分析图
# 以净值（X轴）和回撤（Y轴）
net_value = df['累计净值']
drawdown = df['最大回撤率']

# 计算均值用于划分象限
net_value_mean = net_value.mean()
drawdown_mean = drawdown.mean()

# 绘制散点图
plt.figure()
plt.scatter(net_value, drawdown, alpha=0.6)

# 绘制划分象限的线
plt.axvline(x=net_value_mean, color='r', linestyle='--', label='净值均值')
plt.axhline(y=drawdown_mean, color='g', linestyle='--', label='回撤均值')

# 标注象限
plt.text(net_value_mean * 1.1, drawdown_mean * 1.1, '高净值高回撤', fontsize=10)
plt.text(net_value_mean * 0.1, drawdown_mean * 1.1, '低净值高回撤', fontsize=10)
plt.text(net_value_mean * 1.1, drawdown_mean * 0.1, '高净值低回撤', fontsize=10)
plt.text(net_value_mean * 0.1, drawdown_mean * 0.1, '低净值低回撤', fontsize=10)

# 计算聚类中心
cluster_centers = []
for cluster in df['聚类'].unique():
    cluster_data = df[df['聚类'] == cluster]
    center_net_value = cluster_data['累计净值'].mean()
    center_drawdown = cluster_data['最大回撤率'].mean()
    cluster_centers.append((center_net_value, center_drawdown))

# 标注聚类中心
for i, (center_net_value, center_drawdown) in enumerate(cluster_centers):
    plt.scatter(center_net_value, center_drawdown, color='black', marker='x', s=100, label=f'聚类 {i} 中心')
    plt.annotate(f'聚类 {i} 中心', (center_net_value, center_drawdown), textcoords="offset points", xytext=(0, 10),
                 ha='center')

# 添加标题和轴标签
plt.title('象限分析图：净值 vs 回撤')
plt.xlabel('累计净值')
plt.ylabel('最大回撤率')
plt.legend()
plt.show()

