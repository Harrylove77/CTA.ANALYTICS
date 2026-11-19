import pandas as pd
import os
from collections import defaultdict

def extract_nickname_mappings():
    # 读取汇总数据文件
    data_file = r"h:\TraeProjection\大数据综合应用\汇总数据_前2981名选手_20250410_231855.csv"
    df = pd.read_csv(data_file)
    
    # 创建映射字典
    nickname_mappings = defaultdict(set)
    
    # 遍历数据，按照"客户昵称"分组，收集所有的"账户昵称"
    for _, row in df.iterrows():
        if pd.notna(row['客户昵称']) and pd.notna(row['账户昵称']):
            nickname_mappings[row['客户昵称']].add(row['账户昵称'])
    
    # 转换为列表格式，便于保存
    mapping_list = []
    for customer_nickname, account_nicknames in nickname_mappings.items():
        mapping_list.append({
            '客户昵称': customer_nickname,
            '账户昵称列表': list(account_nicknames),
            '账户数量': len(account_nicknames)
        })
    
    # 按照账户数量降序排序
    mapping_list.sort(key=lambda x: x['账户数量'], reverse=True)
    
    # 转换为DataFrame
    result_df = pd.DataFrame(mapping_list)
    
    # 保存结果
    output_file = r"h:\TraeProjection\大数据综合应用\用户昵称映射数据.csv"
    result_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    print(f"已提取{len(result_df)}个用户的昵称映射数据，保存至: {output_file}")
    
    # 创建详细映射表
    detailed_mappings = []
    for _, row in df.iterrows():
        if pd.notna(row['客户昵称']) and pd.notna(row['账户昵称']):
            detailed_mappings.append({
                '客户昵称': row['客户昵称'],
                '账户昵称': row['账户昵称'],
                '届数': row['届数'] if pd.notna(row['届数']) else None,
                '组别': row['组别'] if pd.notna(row['组别']) else None
            })
    
    # 转换为DataFrame
    detailed_df = pd.DataFrame(detailed_mappings)
    
    # 保存详细结果
    detailed_output_file = r"h:\TraeProjection\大数据综合应用\用户昵称映射详细数据.csv"
    detailed_df.to_csv(detailed_output_file, index=False, encoding='utf-8-sig')
    
    print(f"已提取{len(detailed_df)}条详细昵称映射记录，保存至: {detailed_output_file}")
    
    return result_df, detailed_df

def analyze_nickname_patterns():
    """分析用户昵称的变化模式"""
    _, detailed_df = extract_nickname_mappings()
    
    # 按客户昵称和届数排序
    detailed_df = detailed_df.sort_values(['客户昵称', '届数'])
    
    # 分析每个用户的昵称变化
    user_patterns = defaultdict(list)
    for customer_nickname, group in detailed_df.groupby('客户昵称'):
        sessions = sorted(group['届数'].unique())
        for session in sessions:
            session_nicknames = group[group['届数'] == session]['账户昵称'].unique()
            user_patterns[customer_nickname].append({
                '届数': session,
                '账户昵称': list(session_nicknames)
            })
    
    # 转换为DataFrame格式
    pattern_rows = []
    for customer, patterns in user_patterns.items():
        if len(patterns) > 1:  # 只关注参加了多届比赛的用户
            pattern_rows.append({
                '客户昵称': customer,
                '参赛届数': len(patterns),
                '昵称变化模式': patterns
            })
    
    # 按参赛届数降序排序
    pattern_rows.sort(key=lambda x: x['参赛届数'], reverse=True)
    
    # 保存结果
    pattern_file = r"h:\TraeProjection\大数据综合应用\用户昵称变化模式.json"
    import json
    with open(pattern_file, 'w', encoding='utf-8') as f:
        json.dump(pattern_rows, f, ensure_ascii=False, indent=2)
    
    print(f"已分析{len(pattern_rows)}个用户的昵称变化模式，保存至: {pattern_file}")

if __name__ == "__main__":
    extract_nickname_mappings()
    analyze_nickname_patterns()