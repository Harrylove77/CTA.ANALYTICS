import pandas as pd
import matplotlib.pyplot as plt
# 切换matplotlib后端为TkAgg
import matplotlib
matplotlib.use('TkAgg')

# 设置图片清晰度
plt.rcParams['figure.dpi'] = 300
# 正常显示中文，设置字体为黑体
plt.rcParams['font.sans-serif'] = ['SimHei']
# 解决负号显示问题
plt.rcParams['axes.unicode_minus'] = False

# 定义文件路径
file_paths = [
    r"C:\Users\Administrator\Desktop\大数据综合实践\数据分析结果\排名区间分析\后10名选手.csv",
    r"C:\Users\Administrator\Desktop\大数据综合实践\数据分析结果\排名区间分析\前10名选手.csv",
    r"C:\Users\Administrator\Desktop\大数据综合实践\数据分析结果\排名区间分析\后100名选手.csv",
    r"C:\Users\Administrator\Desktop\大数据综合实践\数据分析结果\排名区间分析\前100名选手.csv"
]

# 遍历不同文件
for file_path in file_paths:
    # 读取数据
    data = pd.read_csv(file_path)

    # 查看数据基本信息
    print(f'数据基本信息：')
    data.info()

    # 查看数据集行数和列数
    rows, columns = data.shape

    if rows < 100 and columns < 20:
        # 短表数据（行数少于100且列数少于20）查看全量数据信息
        print(f'数据全部内容信息：')
        print(data.to_csv(sep='\t', na_rep='nan'))
    else:
        # 长表数据查看数据前几行信息
        print(f'数据前几行内容信息：')
        print(data.head().to_csv(sep='\t', na_rep='nan'))

# 读取用于绘制柱状图的数据
data_bar = pd.read_csv(r"C:\Users\Administrator\Desktop\大数据综合实践\数据分析结果\排名区间分析\排名区间分析.csv")
# 设置`Unnamed: 0`列为索引
data_bar.set_index('Unnamed: 0', inplace=True)

# 绘制各指标在不同排名区间的对比柱状图
ax = data_bar.plot(kind='bar')

# 设置图形标签和标题
plt.xlabel('排名区间')
plt.ylabel('数值')
plt.title('各指标在不同排名区间的对比柱状图')

# 设置x轴刻度标签旋转45度
plt.xticks(rotation=45)

# 设置图例字体大小
ax.legend(fontsize=6)

# 显示图形
plt.show()