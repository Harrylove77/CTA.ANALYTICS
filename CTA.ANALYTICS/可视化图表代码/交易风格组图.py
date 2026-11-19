import pandas as pd
import matplotlib.pyplot as plt
import os

# 设置中文字体，更换为常见的中文字体
plt.rcParams["font.family"] = ["SimSun", "Microsoft YaHei"]
plt.rcParams["axes.unicode_minus"] = False  # 确保负号正确显示

# 创建保存图表的目录
output_dir = "交易风格分析图表"
os.makedirs(output_dir, exist_ok=True)

# 加载交易风格详细分析数据集
df1 = pd.read_csv(r"C:\Users\Administrator\Desktop\大数据综合实践\数据分析结果\交易风格分析\交易风格详细分析.csv")

print('交易风格详细分析数据集基本信息：')
df1.info()

# 查看数据集行数和列数
rows, columns = df1.shape

if rows < 100 and columns < 20:
    # 短表数据查看全量信息
    print('交易风格详细分析数据集全部内容信息：')
    print(df1.to_string(na_rep='nan'))
else:
    # 长表数据查看前几行信息
    print('交易风格详细分析数据集前几行内容信息：')
    print(df1.head().to_string(na_rep='nan'))

# 加载选手交易风格详细分类数据集
df2 = pd.read_csv(r"C:\Users\Administrator\Desktop\大数据综合实践\数据分析结果\交易风格分析\选手交易风格详细分类.csv")

print('选手交易风格详细分类数据集基本信息：')
df2.info()

# 查看数据集行数和列数
rows, columns = df2.shape

if rows < 100 and columns < 20:
    # 短表数据查看全量信息
    print('选手交易风格详细分类数据集全部内容信息：')
    print(df2.to_string(na_rep='nan'))
else:
    # 长表数据查看前几行信息
    print('选手交易风格详细分类数据集前几行内容信息：')
    print(df2.head().to_string(na_rep='nan'))

# 1. 交易风格分布饼图
style_distribution = df2['交易风格名称'].value_counts()

plt.figure(figsize=(8, 6))
plt.pie(style_distribution, labels=style_distribution.index, autopct='%1.1f%%', startangle=90)
plt.title('交易风格分布')
plt.tight_layout()
plt.savefig(f"{output_dir}/交易风格分布.png", dpi=300)
print(f"交易风格分布饼图已保存至 {output_dir}/交易风格分布.png")
print('交易风格分布：\n', style_distribution)
plt.close()

# 2. 不同交易风格的指标箱线图
columns = ['累计净值', '交易胜率', '盈亏比', '最大回撤率']

plt.figure(figsize=(12, 8))
df2.boxplot(column=columns, by='交易风格名称', grid=False)
plt.suptitle('不同交易风格的指标箱线图')
plt.title('')  # 清除默认标题
plt.ylabel('指标值')
plt.xlabel('交易风格名称')
plt.tight_layout()
plt.savefig(f"{output_dir}/交易风格指标箱线图.png", dpi=300)
print(f"指标箱线图已保存至 {output_dir}/交易风格指标箱线图.png")
plt.close()

# 3. 参赛次数与累计净值散点图
plt.figure(figsize=(10, 6))
styles = df2['交易风格名称'].unique()
for style in styles:
    subset = df2[df2['交易风格名称'] == style]
    plt.scatter(subset['参赛次数'], subset['累计净值'], label=style)

plt.xlabel('参赛次数')
plt.ylabel('累计净值')
plt.title('参赛次数与累计净值散点图（按交易风格区分）')

# 添加图例
plt.legend(title='交易风格名称')

plt.tight_layout()
plt.savefig(f"{output_dir}/参赛次数与累计净值散点图.png", dpi=300)
print(f"散点图已保存至 {output_dir}/参赛次数与累计净值散点图.png")
plt.close()

print(f"\n所有图表已成功保存到 {os.path.abspath(output_dir)} 目录下")