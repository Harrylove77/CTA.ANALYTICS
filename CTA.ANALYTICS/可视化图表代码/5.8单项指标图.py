import pandas as pd

# 文件路径列表
file_paths = [
    '/mnt/风险度均值_分析.csv',
    '/mnt/交易胜率_分析.csv',
    '/mnt/累计净值_分析.csv',
    '/mnt/日收益率均值_分析.csv',
    '/mnt/盈亏比_分析.csv',
    '/mnt/最大回撤率_分析.csv'
]

# 遍历不同文件
for file_path in file_paths:
    # 读取数据
    df = pd.read_csv(file_path)

    # 查看数据基本信息
    print(f'文件 {file_path} 基本信息：')
    df.info()

    # 查看数据集行数和列数
    rows, columns = df.shape

    if rows < 100 and columns < 20:
        # 短表数据（行数少于100且列数少于20）查看全量数据信息
        print(f'文件 {file_path} 全部内容信息：')
        print(df.to_csv(sep='\t', na_rep='nan'))
    else:
        # 长表数据查看数据前几行信息
        print(f'文件 {file_path} 前几行内容信息：')
        print(df.head().to_csv(sep='\t', na_rep='nan'))