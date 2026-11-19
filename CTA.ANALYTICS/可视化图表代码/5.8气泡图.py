import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

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

# 显示图表
plt.show()
