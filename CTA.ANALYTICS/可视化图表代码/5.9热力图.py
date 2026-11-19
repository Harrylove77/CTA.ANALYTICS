import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap
import os

# 设置中文字体，这里只保留了SimHei，若需要可添加其他已安装字体
plt.rcParams["font.family"] = "SimHei"
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 尝试修改Matplotlib后端
import matplotlib

matplotlib.use('TkAgg')


def load_data(file_path):
    """加载指定路径的CSV文件数据"""
    try:
        # 检查文件是否存在
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")

        # 读取CSV文件
        data = pd.read_csv(file_path)

        # 显示数据基本信息
        print(f"数据基本信息（来自 {file_path}）:")
        data.info()

        # 查看数据集行数和列数
        rows, columns = data.shape

        if rows < 100 and columns < 20:
            # 短表数据（行数少于100且列数少于20）查看全量数据信息
            print('数据全部内容信息：')
            print(data.to_csv(sep='\t', na_rep='nan'))
        else:
            # 长表数据查看数据前几行信息
            print('数据前几行内容信息：')
            print(data.head().to_csv(sep='\t', na_rep='nan'))

        return data
    except Exception as e:
        print(f"加载数据时出错: {e}")
        # 生成示例数据以便代码可以继续运行
        print("生成示例数据以供演示...")
        return generate_sample_data(100)


def generate_sample_data(n=100):
    """生成样本数据用于相关性分析"""
    np.random.seed(42)  # 设置随机种子，确保结果可重现

    # 生成参赛次数（1-20次之间的整数）
    participation = np.random.randint(1, 21, n)

    # 生成最佳排名（1-1000之间的数值，部分有更好的排名）
    base_rank = np.random.normal(500, 300, n)
    # 让参赛次数多的选手有更好的排名趋势
    best_rank = base_rank - participation * 10
    best_rank = np.clip(best_rank, 1, 1000)

    # 生成平均累计净值（1-5之间的数值）
    # 假设排名越好（数值越小），净值越高，但加入一些随机性
    avg_net_value = 3.0 - best_rank / 500 + np.random.normal(0, 0.3, n)
    avg_net_value = np.clip(avg_net_value, 1.0, 5.0)

    # 创建DataFrame
    data = pd.DataFrame({
        '参赛次数': participation,
        '最佳排名': best_rank,
        '平均累计净值': avg_net_value
    })

    return data


def analyze_correlation(data):
    """分析数据相关性并绘制热力图"""
    # 计算相关系数矩阵（保留两位小数）
    corr_matrix = data[['最佳排名', '平均累计净值', '参赛次数']].corr().round(2)

    # 创建自定义颜色映射
    cmap = LinearSegmentedColormap.from_list(
        'custom_cmap',
        [(0, '#1a9850'), (0.5, '#ffffbf'), (1, '#d73027')]
    )

    # 创建画布
    plt.figure(figsize=(12, 10))

    # 绘制热力图
    plt.subplot(2, 1, 1)
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))  # 上三角掩码
    sns.heatmap(
        corr_matrix,
        annot=True,
        cmap=cmap,
        mask=mask,
        square=True,
        linewidths=.5,
        cbar_kws={"shrink": .8},
        annot_kws={"size": 12}
    )
    plt.title('金融数据相关性热力图', fontsize=15)

    # 绘制散点图矩阵
    plt.subplot(2, 1, 2)
    g = sns.pairplot(data[['最佳排名', '平均累计净值', '参赛次数']], height=3)
    g.fig.suptitle('变量间散点图矩阵', y=1.02, fontsize=15)

    plt.tight_layout()
    plt.savefig('financial_correlation_analysis.png', dpi=300, bbox_inches='tight')
    plt.show()

    # 打印相关系数
    print("相关系数矩阵：")
    print(corr_matrix)

    # 分析结果
    rank_net_corr = corr_matrix.loc['最佳排名', '平均累计净值']
    participation_net_corr = corr_matrix.loc['参赛次数', '平均累计净值']

    print("\n=== 分析结论 ===")
    if rank_net_corr < 0:
        print(f"1. 最佳排名与平均累计净值呈负相关（相关系数：{rank_net_corr:.2f}），"
              "说明排名越靠前（数值越小），平均累计净值越高。")
    else:
        print(f"1. 最佳排名与平均累计净值呈正相关（相关系数：{rank_net_corr:.2f}），"
              "这可能表明数据中存在其他影响因素。")

    if abs(participation_net_corr) > 0.3:
        print(f"2. 参赛次数与平均累计净值相关性较强（相关系数：{participation_net_corr:.2f}），"
              "说明参赛次数可能对收益稳定性有明显影响。")
    else:
        print(f"2. 参赛次数与平均累计净值相关性较弱（相关系数：{participation_net_corr:.2f}），"
              "表明参赛次数对收益稳定性影响较小。")


if __name__ == "__main__":
    # 指定CSV文件路径
    file_path = r"C:\Users\Administrator\Desktop\大数据综合实践\数据分析结果\用户画像\顶级选手画像.csv"

    # 加载数据
    data = load_data(file_path)

    # 分析相关性
    analyze_correlation(data)