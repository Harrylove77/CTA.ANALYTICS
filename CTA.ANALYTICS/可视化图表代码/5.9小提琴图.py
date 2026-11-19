import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder
# 设置matplotlib后端
import matplotlib; matplotlib.use('TkAgg')
# 设置图片清晰度
plt.rcParams['figure.dpi'] = 300
# 设置中文字体为SimHei
plt.rcParams['font.sans-serif'] = ['SimHei']

# 示例数据
data = {
    '交易风格描述': ['平衡型交易者，胜率和盈亏比均处于中等水平', '频繁型交易者，追求高胜率但单次盈利相对较小',
                  '重仓型交易者，单次盈利较大但胜率相对较低', '平衡型交易者，胜率和盈亏比均处于中等水平',
                  '频繁型交易者，追求高胜率但单次盈利相对较小', '平衡型交易者，胜率和盈亏比均处于中等水平',
                  '重仓型交易者，单次盈利较大但胜率相对较低', '频繁型交易者，追求高胜率但单次盈利相对较小'],
    '平均累计净值': [2.3, 2.1, 2.7, 2.4, 2.2, 2.35, 2.6, 2.15],
    '风险特征': ['高风险，可能存在较大回撤，整体风险度较高', '中等风险，回撤控制在合理范围，整体风险度适中',
               '高风险，可能存在较大回撤，整体风险度较高', '中等风险，回撤控制在合理范围，整体风险度适中',
               '低风险，最大回撤控制出色，整体风险度较低', '中等风险，回撤控制在合理范围，整体风险度适中',
               '高风险，可能存在较大回撤，整体风险度较高', '低风险，最大回撤控制出色，整体风险度较低'],
    '收益特征': ['高收益型，日均收益率出色，收益波动较大，可能采用激进策略',
               '稳健收益型，日均收益率良好，收益波动较大，可能采用激进策略',
               '高收益型，日均收益率出色，收益波动较大，可能采用激进策略',
               '稳健收益型，日均收益率良好，收益波动较大，可能采用激进策略',
               '稳健收益型，日均收益率良好，收益波动较小，策略相对保守',
               '高收益型，日均收益率出色，收益波动较大，可能采用激进策略',
               '高收益型，日均收益率出色，收益波动较大，可能采用激进策略',
               '稳健收益型，日均收益率良好，收益波动较小，策略相对保守']
}

# 创建DataFrame
df = pd.DataFrame(data)

# 提取交易风格描述中的关键交易风格
df['交易风格'] = df['交易风格描述'].str.extract(r'(平衡型|频繁型|重仓型)')

# 提取风险特征中的关键风险等级
df['风险等级'] = df['风险特征'].str.extract(r'(高风险|中等风险|低风险|极低风险)').replace({'极低风险': '低风险'})

# 对收益特征进行编码
le = LabelEncoder()
df['收益特征编码'] = le.fit_transform(df['收益特征'])

# 按交易风格分组计算平均累计净值
style_avg_net_value = df.groupby('交易风格')['平均累计净值'].mean()

# 绘制分组柱状图
plt.figure(figsize=(10, 6))
ax1 = plt.subplot(121)
bars = ax1.bar(style_avg_net_value.index, style_avg_net_value.values, color=['#4285F4', '#EA4335', '#FBBC05'])
ax1.set_ylabel('平均累计净值')
ax1.set_title('不同交易风格的平均累计净值差异')
ax1.tick_params(axis='x', rotation=0)

# 添加数据标签
for bar in bars:
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height,
             f'{height:.4f}',
             ha='center', va='bottom', fontsize=9)

# 分析风险等级对收益的影响，绘制小提琴图
ax2 = plt.subplot(122)
violin_parts = ax2.violinplot([df[df['风险等级'] == risk]['收益特征编码'] for risk in df['风险等级'].dropna().unique()],
                            positions=range(len(df['风险等级'].dropna().unique())),
                            showmeans=True,
                            showmedians=True)

# 设置小提琴图颜色
for pc in violin_parts['bodies']:
    pc.set_facecolor('#4285F4')
    pc.set_edgecolor('black')
    pc.set_alpha(0.6)

violin_parts['cmeans'].set_color('#EA4335')
violin_parts['cmedians'].set_color('#FBBC05')

# 设置 x 轴标签为风险等级
ax2.set_xticks(range(len(df['风险等级'].dropna().unique())))
ax2.set_xticklabels(df['风险等级'].dropna().unique())
ax2.set_xlabel('风险等级')
ax2.set_ylabel('收益特征编码')
ax2.set_title('风险等级对收益的影响')

plt.tight_layout()
plt.savefig('交易风格与风险收益分析.png', dpi=300, bbox_inches='tight')
plt.show()

# 输出结果
print('不同交易风格的平均累计净值差异：\n', style_avg_net_value)

# 计算不同风险等级下的平均收益
risk_avg_returns = df.groupby('风险等级')['收益特征编码'].mean()
print('\n不同风险等级下的平均收益：\n', risk_avg_returns)

# 计算不同交易风格的数量
style_counts = df['交易风格'].value_counts()
print('\n不同交易风格的数量：\n', style_counts)

# 计算不同风险等级的数量
risk_counts = df['风险等级'].value_counts()
print('\n不同风险等级的数量：\n', risk_counts)

# 结论分析
print('\n===== 结论分析 =====')
print('1. 交易风格分析：')
print('   - 重仓型交易风格的平均累计净值最高，为 {:.4f}，表明承担较高风险可能获得更高回报。'.format(style_avg_net_value['重仓型']))
print('   - 平衡型和频繁型交易风格的平均累计净值较为接近，分别为 {:.4f} 和 {:.4f}，说明这两种风格相对稳健。'.format(
    style_avg_net_value['平衡型'], style_avg_net_value['频繁型']))

print('\n2. 风险等级与收益关系：')
if '高风险' in risk_avg_returns.index and '低风险' in risk_avg_returns.index:
    if risk_avg_returns['高风险'] > risk_avg_returns['低风险']:
        print('   - 高风险等级的平均收益编码为 {:.4f}，高于低风险等级的 {:.4f}，'.format(
            risk_avg_returns['高风险'], risk_avg_returns['低风险']))
        print('     说明在当前数据中，承担更高风险可能带来更高的收益。')
    else:
        print('   - 高风险等级的平均收益编码为 {:.4f}，低于低风险等级的 {:.4f}，'.format(
            risk_avg_returns['高风险'], risk_avg_returns['低风险']))
        print('     这可能表示高风险策略在当前数据中未获得更高回报，需进一步分析。')
else:
    print('   - 数据中高风险或低风险等级样本不足，无法有效对比其平均收益。')

print('\n3. 分布情况：')
print('   - 交易风格分布：平衡型 {} 个，频繁型 {} 个，重仓型 {} 个。'.format(
    style_counts.get('平衡型', 0), style_counts.get('频繁型', 0), style_counts.get('重仓型', 0)))
print('   - 风险等级分布：高风险 {} 个，中等风险 {} 个，低风险 {} 个。'.format(
    risk_counts.get('高风险', 0), risk_counts.get('中等风险', 0), risk_counts.get('低风险', 0)))

print('\n4. 建议：')
print('   - 对于追求高收益且能承受高风险的投资者，可以考虑重仓型交易风格。')
print('   - 对于风险偏好适中的投资者，平衡型交易风格是较为合适的选择。')
print('   - 对于风险偏好较低的投资者，频繁型交易风格结合低风险策略可能更为合适，但需注意其收益相对平稳。')