import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


# 读取数据
df = pd.read_csv(r"C:\Users\Administrator\Desktop\大数据综合实践\数据分析结果\用户画像\顶级用户画像.csv")

# 定义函数绘制直方图
def plot_histogram(data, column_name):
    plt.figure(figsize=(10, 6))
    sns.histplot(data=data, x=column_name, kde=True)
    plt.title(f'{column_name} 直方图')
    plt.xlabel(column_name)
    plt.ylabel('频数')
    plt.show()


# 定义函数绘制箱线图
def plot_boxplot(data, column_name):
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=data, y=column_name)
    plt.title(f'{column_name} 箱线图')
    plt.ylabel(column_name)
    plt.show()


# 定义函数绘制密度图
def plot_kdeplot(data, column_name):
    plt.figure(figsize=(10, 6))
    sns.kdeplot(data=data[column_name])
    plt.title(f'{column_name} 密度图')
    plt.xlabel(column_name)
    plt.ylabel('密度')
    plt.show()


# 对平均累计净值进行分布分析
plot_histogram(df, '平均累计净值')
plot_boxplot(df, '平均累计净值')
plot_kdeplot(df, '平均累计净值')

# 对最佳排名进行分布分析
plot_histogram(df, '最佳排名')
plot_boxplot(df, '最佳排名')
plot_kdeplot(df, '最佳排名')

# 对参赛次数进行分布分析
plot_histogram(df, '参赛次数')
plot_boxplot(df, '参赛次数')
plot_kdeplot(df, '参赛次数')
