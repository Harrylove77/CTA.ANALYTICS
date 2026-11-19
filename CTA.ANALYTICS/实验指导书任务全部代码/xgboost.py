import pandas as pd
import matplotlib.pyplot as plt
import os

# ----------------------
# 1. 数据读取与检查
# ----------------------
# 读取预测结果数据
try:
    df = pd.read_csv(r"C:\Users\Administrator\Desktop\大数据综合实践\预测模型结果\预测18届排名_random_forest\pred_detl.csv"
                     )  # 假设文件与代码同目录，否则需指定完整路径
except FileNotFoundError:
    print("错误：找不到 'pred_detl.csv' 文件，请确认文件路径是否正确。")
    exit(1)

# 检查数据完整性
print("数据预处理信息：")
print(f"数据行数：{len(df)}")
print(f"缺失值统计：\n{df.isnull().sum()}")
print("\n数据示例：")
print(df.head())  # 显示前5行数据

# 检查必要列是否存在
required_columns = ['实际', '预测']
for col in required_columns:
    if col not in df.columns:
        print(f"错误：数据集中缺少必要的列 '{col}'。")
        exit(1)


# ----------------------
# 2. 绘图参数设置
# ----------------------
# 设置全局中文字体（解决中文乱码）
plt.rcParams['font.sans-serif'] = ['SimHei', 'WenQuanYi Micro Hei', 'Heiti TC']  # 多种备选字体
plt.rcParams['axes.unicode_minus'] = False     # 正确显示负号

# 设置图形尺寸与分辨率
plt.figure(
    figsize=(12, 8),       # 图形宽高（英寸）
    dpi=300,              # 分辨率（像素/英寸）
    facecolor='#f9f9f9'    # 背景色
)


# ----------------------
# 3. 绘制核心图形
# ----------------------
# 绘制散点图
scatter = plt.scatter(
    x=df['实际'],          # X轴：实际排名
    y=df['预测'],          # Y轴：预测排名
    s=50,                  # 点大小
    alpha=0.7,             # 透明度
    edgecolor='w',         # 点边缘颜色
    c='#1f77b4',           # 点颜色（蓝色）
    label='预测点'
)

# 添加y=x参考线
plt.plot(
    [df['实际'].min(), df['实际'].max()],  # x范围
    [df['实际'].min(), df['实际'].max()],  # y范围
    linestyle='--',      # 虚线样式
    color='#d62728',      # 红色
    linewidth=1.5,       # 线宽
    label='y = x 参考线'
)


# ----------------------
# 4. 图形美化与标注
# ----------------------
# 设置坐标轴范围（根据数据分布调整）
x_min, x_max = df['实际'].min(), df['实际'].max()
y_min, y_max = df['预测'].min(), df['预测'].max()
plt.xlim(0, max(x_max, y_max) * 1.1)  # 统一坐标轴范围，便于比较
plt.ylim(0, max(x_max, y_max) * 1.1)

# 设置坐标轴标签（带单位）
plt.xlabel('实际排名（名次）', fontsize=12, fontweight='bold')
plt.ylabel('预测排名（名次）', fontsize=12, fontweight='bold')

# 设置坐标轴刻度（倾斜x轴刻度防止重叠）
plt.xticks(rotation=45, ha='right', fontsize=10)
plt.yticks(fontsize=10)

# 添加标题与副标题
plt.title(
    'XGBoost模型预测排名 vs 实际排名散点图',
    fontsize=14,
    fontweight='bold',
    pad=20
)
plt.suptitle(
    '数据来源：pred_detl.csv | 时间：2025年5月15日',
    fontsize=10,
    color='#666'
)

# 添加图例（位于右上角）
plt.legend(
    loc='upper right',
    frameon=True,
    facecolor='white',
    edgecolor='lightgray'
)

# 添加网格线
plt.grid(
    linestyle='--',
    alpha=0.5,
    color='#eeeeee'
)


# ----------------------
# 5. 结果输出与保存
# ----------------------
# 在控制台显示图形信息
print("\n图形绘制完成，包含：")
print(f"- 散点数量：{len(df)}个")
print(f"- 实际排名范围：{df['实际'].min():.0f} ~ {df['实际'].max():.0f}")
print(f"- 预测排名范围：{df['预测'].min():.0f} ~ {df['预测'].max():.0f}")

# 保存图形为文件
output_dir = 'output_images'
os.makedirs(output_dir, exist_ok=True)
image_path = os.path.join(output_dir, 'xgb_pred_vs_actual.png')

try:
    plt.savefig(
        image_path,
        dpi=300,
        bbox_inches='tight'  # 自动裁剪白边
    )
    print(f"\n图形已成功保存至：{image_path}")
except Exception as e:
    print(f"\n警告：无法保存图形文件：{str(e)}")

# 尝试显示图形（如果环境支持）
try:
    plt.show()
except Exception as e:
    print(f"\n警告：无法显示图形。可能是因为当前环境不支持图形界面。")
    print(f"错误信息：{str(e)}")
    print(f"请查看保存的图像文件：{image_path}")


class XGBRegressor:
    pass