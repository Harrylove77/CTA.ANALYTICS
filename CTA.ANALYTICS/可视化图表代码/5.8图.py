import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm

# 设置图片清晰度
plt.rcParams['figure.dpi'] = 300

# 设置中文字体，使用系统中存在的字体，如 SimHei（黑体）
plt.rcParams['font.sans-serif'] = ['SimHei']
# 解决负号显示问题
plt.rcParams['axes.unicode_minus'] = False

# 更改 Matplotlib 后端
plt.switch_backend('TkAgg')

# 修正文件路径，移除多余的 python.exe 部分
df2 = pd.read_csv(r"C:\Users\Administrator\Desktop\大数据综合实践\数据分析结果\多指标分析结果.csv")

# 绘制散点图，以最大回撤率为横轴，累计净值为纵轴，按聚类结果着色
plt.scatter(df2['最大回撤率'], df2['累计净值'], c=df2['聚类'])

# 添加标题和轴标签
plt.title('累计净值 vs. 最大回撤（按聚类结果区分）')
plt.xlabel('最大回撤率（风险）')
plt.xticks(rotation=45)
plt.ylabel('累计净值（收益）')

# 获取颜色映射
cmap = cm.get_cmap('viridis')

# 添加图例
for cluster in df2['聚类'].unique():
    plt.scatter([], [], c=[cmap(cluster)], label=f'聚类 {cluster}')
plt.legend()

# 标记优质客户和高风险客户
try:
    plt.annotate('优质客户（如169427）', xy=(df2.loc[df2['标准客户昵称'] == '169427', '最大回撤率'].values[0],
                                           df2.loc[df2['标准客户昵称'] == '169427', '累计净值'].values[0]),
                 xytext=(-50, -30),
                 textcoords='offset points', arrowprops=dict(arrowstyle='->'))
    plt.annotate('高风险客户（如173620）', xy=(df2.loc[df2['标准客户昵称'] == '173620', '最大回撤率'].values[0],
                                             df2.loc[df2['标准客户昵称'] == '173620', '累计净值'].values[0]),
                 xytext=(30, 30),
                 textcoords='offset points', arrowprops=dict(arrowstyle='->'))
except IndexError:
    print('数据中可能不存在指定的客户昵称，无法进行标注。')

# 显示图表
plt.show()
