import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import warnings
import os
warnings.filterwarnings('ignore')

# 创建结果目录
res_dir = r'h:\TraeProjection\大数据综合应用\数据分析结果'
if not os.path.exists(res_dir):
    os.makedirs(res_dir)

# 加载昵称映射
nick_path = r'h:\TraeProjection\大数据综合应用\用户昵称映射数据.csv'
nick_map = pd.read_csv(nick_path, encoding='utf-8')

# 创建昵称映射字典
def get_map():
    """创建昵称映射字典"""
    map_dict = {}
    
    for _, row in nick_map.iterrows():
        std_name = row['客户昵称']
        # 转换列表
        acc_names = eval(row['账户昵称列表'])
        
        # 映射昵称
        for acc_name in acc_names:
            map_dict[acc_name] = std_name
        
        # 确保自映射
        map_dict[std_name] = std_name
    
    return map_dict

# 创建映射字典
nick_dict = get_map()

# 加载数据
file_path = r'h:\TraeProjection\大数据综合应用\汇总数据_前2981名选手_20250410_231855.csv'
data = pd.read_csv(file_path, encoding='utf-8')

# 数据预处理
# 1. 处理缺失值
data = data.replace('', np.nan)

# 2. 标准化昵称
def std_nick(df):
    """标准化昵称"""
    # 创建标准列
    df['标准客户昵称'] = df['客户昵称'].copy()
    
    # 应用映射
    df['标准客户昵称'] = df['标准客户昵称'].map(lambda x: nick_dict.get(x, x))
    
    # 标准化账户昵称
    df['标准账户昵称'] = df['账户昵称'].map(lambda x: nick_dict.get(x, x))
    
    return df

# 应用标准化
data = std_nick(data)

# 3. 转换数据类型
num_cols = ['期初权益', '期末权益', '累计入金', '累计出金', '累计净值', 
            '累计净利润', '日收益率均值', '日收益率最大', '日收益率最小', 
            '年化收益率', '盈利天数', '亏损天数', '交易胜率', '盈亏比', 
            '手续费/净利润', '风险度均值', '最大回撤率']

for col in num_cols:
    if col in data.columns:
        data[col] = pd.to_numeric(data[col], errors='coerce')

# 4. 处理异常值
def fix_out(df, cols):
    """处理异常值"""
    df_new = df.copy()
    
    for col in cols:
        if col in df.columns:
            # 计算IQR
            q1 = df[col].quantile(0.25)
            q3 = df[col].quantile(0.75)
            iqr = q3 - q1
            
            # 边界值
            low = q1 - 1.5 * iqr
            high = q3 + 1.5 * iqr
            
            # 替换异常值
            df_new.loc[df_new[col] < low, col] = low
            df_new.loc[df_new[col] > high, col] = high
    
    return df_new

# 处理关键指标异常值
data = fix_out(data, ['累计净值', '交易胜率', '盈亏比', '最大回撤率', '风险度均值', '日收益率均值'])

# 5. 筛选有效数据
data = data.dropna(subset=['累计净值', '累计净利润'], how='all')

# 6. 计算参赛次数
part_cnt = data.groupby('标准客户昵称').size().reset_index(name='参赛次数')
data = pd.merge(data, part_cnt, on='标准客户昵称', how='left')

# 7. 识别稳定盈利选手
stb_plyr = data.groupby('标准客户昵称').filter(
    lambda x: len(x) >= 3 and (x['累计净值'] > 1).mean() > 0.7
)

# 保存预处理数据
data.to_csv(os.path.join(res_dir, '预处理后数据.csv'), index=False, encoding='utf-8')
stb_plyr.to_csv(os.path.join(res_dir, '长期稳定盈利选手.csv'), index=False, encoding='utf-8')

# 单项指标分析
def ana_ind(df, ind, path):
    """单指标分析"""
    if ind not in df.columns:
        print(f"指标 {ind} 不在数据集中")
        return
    
    # 计算均值
    ind_avg = df.groupby('标准客户昵称')[ind].mean().reset_index()
    
    # 添加参赛次数
    part_num = df.groupby('标准客户昵称').size().reset_index(name='参赛次数')
    ind_avg = pd.merge(ind_avg, part_num, on='标准客户昵称')
    
    # 保存结果
    ind_avg.to_csv(os.path.join(path, f'{ind}_分析.csv'), index=False, encoding='utf-8')
    
    return ind_avg

# 创建单指标目录
ind_dir = os.path.join(res_dir, '单项指标分析')
if not os.path.exists(ind_dir):
    os.makedirs(ind_dir)

# 分析关键指标
key_inds = ['累计净值', '交易胜率', '盈亏比', '最大回撤率', '风险度均值', '日收益率均值']
ind_res = {}

for ind in key_inds:
    ind_res[ind] = ana_ind(data, ind, ind_dir)

# 定义最优聚类数
def get_k(data, max_k):
    """找最优聚类数"""
    dists = []
    for k in range(1, max_k+1):
        kmeans = KMeans(n_clusters=k, random_state=42)
        kmeans.fit(data)
        dists.append(kmeans.inertia_)
    
    # 计算斜率变化
    slps = [dists[i-1] - dists[i] for i in range(1, len(dists))]
    # 找最大斜率点
    opt_k = slps.index(max(slps)) + 2
    
    return opt_k

# 多指标分析
def ana_mul(df, inds, path):
    """多指标分析"""
    # 筛选数据
    val_df = df.dropna(subset=inds)
    
    # 计算均值
    inds_avg = val_df.groupby('标准客户昵称')[inds].mean().reset_index()
    
    # 添加参赛次数
    part_num = val_df.groupby('标准客户昵称').size().reset_index(name='参赛次数')
    inds_avg = pd.merge(inds_avg, part_num, on='标准客户昵称')
    
    # 标准化
    scaler = StandardScaler()
    scl_data = scaler.fit_transform(inds_avg[inds])
    
    # 最优聚类数
    opt_k = get_k(scl_data, 10)
    print(f"最优聚类数: {opt_k}")
    
    # K-means聚类
    kmeans = KMeans(n_clusters=opt_k, random_state=42)
    clsts = kmeans.fit_predict(scl_data)
    inds_avg['聚类'] = clsts
    
    # 分析特征
    clst_ana = inds_avg.groupby('聚类')[inds + ['参赛次数']].mean()
    
    # 保存结果
    inds_avg.to_csv(os.path.join(path, '多指标分析结果.csv'), index=False, encoding='utf-8')
    clst_ana.to_csv(os.path.join(path, '聚类特征分析.csv'), encoding='utf-8')
    
    return inds_avg, clst_ana

# 创建多指标目录
mul_dir = os.path.join(res_dir, '多项指标分析')
if not os.path.exists(mul_dir):
    os.makedirs(mul_dir)

# 选择分析指标
ana_inds = ['累计净值', '交易胜率', '盈亏比', '最大回撤率', '风险度均值', '日收益率均值']
mul_res, clst_ana = ana_mul(data, ana_inds, mul_dir)

# 预测模型构建
def bld_mdl(df, path):
    """构建预测模型"""
    # 选取了7个核心特征
    feats = ['累计净值', '交易胜率', '盈亏比', '最大回撤率', '风险度均值', '日收益率均值', '参赛次数']
    
    # 特征聚合
    # 对于每个选手，计算其历史参赛数据的平均值
    plyr_fts = df.groupby('标准客户昵称')[feats].mean().reset_index()
    
    # 添加最佳排名
    best_rnk = df.groupby('标准客户昵称')['综合排名'].min().reset_index()
    plyr_fts = pd.merge(plyr_fts, best_rnk, on='标准客户昵称', how='left')
    
    # 定义目标变量
    last_prf = df.sort_values('届数', ascending=False).drop_duplicates('标准客户昵称')[['标准客户昵称', '累计净值', '综合排名']]
    plyr_fts = pd.merge(plyr_fts, last_prf, on='标准客户昵称', how='left', suffixes=('', '_last'))
    
    # 准备数据，这里定义了两个目标变量：
    X = plyr_fts.drop(['标准客户昵称', '累计净值_last', '综合排名_last'], axis=1)
    y_rnk = plyr_fts['综合排名_last']
    y_val = plyr_fts['累计净值_last']
    
    # 处理缺失值
    X = X.fillna(X.mean())
    y_rnk = y_rnk.fillna(y_rnk.mean())
    y_val = y_val.fillna(y_val.mean())
    
    # 分割数据
    X_tr, X_te, y_r_tr, y_r_te = train_test_split(X, y_rnk, test_size=0.2, random_state=42)
    _, _, y_v_tr, y_v_te = train_test_split(X, y_val, test_size=0.2, random_state=42)

    #随机森林回归模型
    # 训练排名模型
    rnk_mdl = RandomForestRegressor(n_estimators=100, random_state=42)
    rnk_mdl.fit(X_tr, y_r_tr)
    rnk_prd = rnk_mdl.predict(X_te)
    
    # 训练净值模型
    val_mdl = RandomForestRegressor(n_estimators=100, random_state=42)
    val_mdl.fit(X_tr, y_v_tr)
    val_prd = val_mdl.predict(X_te)
    
    # 评估模型
    rnk_rms = np.sqrt(mean_squared_error(y_r_te, rnk_prd))
    rnk_r2 = r2_score(y_r_te, rnk_prd)
    
    val_rms = np.sqrt(mean_squared_error(y_v_te, val_prd))
    val_r2 = r2_score(y_v_te, val_prd)
    
    # 保存结果
    res = pd.DataFrame({
        '指标': ['排名RMSE', '排名R2', '净值RMSE', '净值R2'],
        '值': [rnk_rms, rnk_r2, val_rms, val_r2]
    })
    res.to_csv(os.path.join(path, '预测模型评估.csv'), index=False, encoding='utf-8')
    
    # 特征重要性
    rnk_imp = pd.Series(rnk_mdl.feature_importances_, index=X.columns)
    val_imp = pd.Series(val_mdl.feature_importances_, index=X.columns)
    
    # 保存特征重要性
    rnk_imp.to_csv(os.path.join(path, '排名预测特征重要性.csv'), encoding='utf-8')
    val_imp.to_csv(os.path.join(path, '净值预测特征重要性.csv'), encoding='utf-8')
    
    return rnk_mdl, val_mdl, res

# 交易风格分析
def ana_stl(df, path):
    """交易风格分析"""
    # 按昵称分组
    plyr_dat = df.groupby('标准客户昵称').agg({
        '参赛次数': 'max',
        '累计净值': 'mean',
        '交易胜率': 'mean',
        '盈亏比': 'mean',
        '最大回撤率': 'mean',
        '风险度均值': 'mean',
        '日收益率均值': 'mean',
        '日收益率最大': 'mean',
        '日收益率最小': 'mean'
    }).reset_index()
    
    # 筛选选手
    exp_plyr = plyr_dat[plyr_dat['参赛次数'] >= 3]
    
    # 数据标准化
    feats = ['累计净值', '交易胜率', '盈亏比', '最大回撤率', '风险度均值', 
            '日收益率均值', '日收益率最大', '日收益率最小']
    
    # 处理缺失值
    exp_plyr = exp_plyr.dropna(subset=feats)
    
    if len(exp_plyr) == 0:
        print("没有足够的数据进行交易风格分析")
        return None, None
    
    scaler = StandardScaler()
    scl_dat = scaler.fit_transform(exp_plyr[feats])
    
    # 最优聚类数
    opt_k = get_k(scl_dat, 8)
    print(f"交易风格分析最优聚类数: {opt_k}")
    
    # K-means聚类
    kmeans = KMeans(n_clusters=opt_k, random_state=42)
    exp_plyr['交易风格'] = kmeans.fit_predict(scl_dat)
    
    # 分析特征
    stl_prof = exp_plyr.groupby('交易风格')[feats].mean()
    
    # 命名风格
    stl_char = {}
    for stl in stl_prof.index:
        prof = stl_prof.loc[stl]
        
        # 判断特点
        if prof['累计净值'] > stl_prof['累计净值'].mean() and prof['最大回撤率'] < stl_prof['最大回撤率'].mean():
            stl_name = "稳健成长型"
        elif prof['累计净值'] > stl_prof['累计净值'].mean() and prof['最大回撤率'] > stl_prof['最大回撤率'].mean():
            stl_name = "高风险高收益型"
        elif prof['交易胜率'] > stl_prof['交易胜率'].mean() and prof['盈亏比'] < stl_prof['盈亏比'].mean():
            stl_name = "高频小额交易型"
        else:
            stl_name = "保守防守型"
            
        stl_char[stl] = {
            "风格名称": stl_name,
            "特点描述": f"累计净值: {prof['累计净值']:.2f}, 交易胜率: {prof['交易胜率']:.2f}%, "
                    f"盈亏比: {prof['盈亏比']:.2f}, 最大回撤率: {prof['最大回撤率']:.2f}%"
        }
    
    # 创建映射
    stl_map = {stl: info["风格名称"] for stl, info in stl_char.items()}
    
    # 替换风格编号
    exp_plyr['交易风格名称'] = exp_plyr['交易风格'].map(stl_map)
    
    # 保存结果
    stl_info = pd.DataFrame([
        {"交易风格": stl, "风格名称": info["风格名称"], "特点描述": info["特点描述"]}
        for stl, info in stl_char.items()
    ])
    stl_info.to_csv(os.path.join(path, '交易风格详细分析.csv'), index=False, encoding='utf-8')
    exp_plyr.to_csv(os.path.join(path, '选手交易风格详细分类.csv'), index=False, encoding='utf-8')
    
    return exp_plyr, stl_info

# 时间序列分析
def ana_tim(df, path):
    """时间序列分析"""
    # 筛选选手
    part_cnt = df.groupby('标准客户昵称').size().reset_index(name='参赛次数')
    exp_plyr = part_cnt[part_cnt['参赛次数'] >= 3]['标准客户昵称'].tolist()
    
    if not exp_plyr:
        print("没有参赛3次以上的选手")
        return None
    
    # 筛选数据
    exp_dat = df[df['标准客户昵称'].isin(exp_plyr)]
    
    # 按届数排序
    exp_dat['届数'] = pd.to_numeric(exp_dat['届数'], errors='coerce')
    exp_dat = exp_dat.sort_values(['标准客户昵称', '届数'])
    
    # 选择前10名选手
    top_plyr = exp_dat.groupby('标准客户昵称')['累计净值'].mean().nlargest(10).index.tolist()
    
    # 分析指标变化
    key_mets = ['累计净值', '交易胜率', '盈亏比', '最大回撤率']
    
    # 整体趋势
    ovr_trnd = exp_dat.groupby('届数')[key_mets].mean().reset_index()
    
    # 保存结果
    ovr_trnd.to_csv(os.path.join(path, '整体趋势数据.csv'), index=False, encoding='utf-8')
    
    return ovr_trnd

# 排名区间分析
def ana_rnk(df, path):
    """排名区间分析"""
    # 确保数值型
    df['综合排名'] = pd.to_numeric(df['综合排名'], errors='coerce')
    
    # 筛选数据
    val_df = df.dropna(subset=['综合排名', '参赛次数'])
    
    # 筛选选手
    exp_plyr = val_df[val_df['参赛次数'] >= 3]
    
    if len(exp_plyr) == 0:
        print("没有足够的数据进行排名区间分析")
        return None
    
    # 按排名分组
    top_10 = exp_plyr[exp_plyr['综合排名'] <= 10]
    top_100 = exp_plyr[exp_plyr['综合排名'] <= 100]
    
    # 后10名和后100名
    max_rnk = exp_plyr['综合排名'].max()
    bot_10 = exp_plyr[exp_plyr['综合排名'] >= (max_rnk - 10)]
    bot_100 = exp_plyr[exp_plyr['综合排名'] >= (max_rnk - 100)]
    
    # 分析指标
    inds = ['累计净值', '交易胜率', '盈亏比', '最大回撤率', '风险度均值', '日收益率均值']
    
    # 计算均值
    grp_stat = {
        '前10名': top_10[inds].mean(),
        '前100名': top_100[inds].mean(),
        '后10名': bot_10[inds].mean(),
        '后100名': bot_100[inds].mean()
    }
    
    # 转为DataFrame
    grp_df = pd.DataFrame(grp_stat).T
    
    # 保存结果
    grp_df.to_csv(os.path.join(path, '排名区间分析.csv'), encoding='utf-8')
    
    # 保存详细数据
    top_10.to_csv(os.path.join(path, '前10名选手.csv'), index=False, encoding='utf-8')
    top_100.to_csv(os.path.join(path, '前100名选手.csv'), index=False, encoding='utf-8')
    bot_10.to_csv(os.path.join(path, '后10名选手.csv'), index=False, encoding='utf-8')
    bot_100.to_csv(os.path.join(path, '后100名选手.csv'), index=False, encoding='utf-8')
    
    return grp_df

# 用户画像生成
def gen_prf(df, path):
    """生成交易者画像"""
    # 筛选选手
    part_cnt = df.groupby('标准客户昵称').size().reset_index(name='参赛次数')
    exp_plyr = part_cnt[part_cnt['参赛次数'] >= 3]['标准客户昵称'].tolist()
    
    if not exp_plyr:
        print("没有参赛3次以上的选手")
        return None
    
    # 筛选数据
    exp_dat = df[df['标准客户昵称'].isin(exp_plyr)]
    
    # 计算均值
    plyr_prf = exp_dat.groupby('标准客户昵称').agg({
        '参赛次数': 'max',
        '累计净值': 'mean',
        '交易胜率': 'mean',
        '盈亏比': 'mean',
        '最大回撤率': 'mean',
        '风险度均值': 'mean',
        '日收益率均值': 'mean',
        '日收益率最大': 'mean',
        '日收益率最小': 'mean',
        '综合排名': 'min'  # 最好排名
    }).reset_index()
    
    # 排序生成画像
    top_plyr = plyr_prf.sort_values('累计净值', ascending=False).head(50)
    
    # 生成画像
    profs = []
    for _, plyr in top_plyr.iterrows():
        prof = {
            "标准客户昵称": plyr['标准客户昵称'],
            "参赛次数": plyr['参赛次数'],
            "最佳排名": plyr['综合排名'],
            "平均累计净值": plyr['累计净值'],
            "交易风格描述": gen_stl(plyr),
            "风险特征": gen_rsk(plyr),
            "收益特征": gen_ret(plyr)
        }
        profs.append(prof)
    
    # 转为DataFrame
    prfs_df = pd.DataFrame(profs)
    
    # 保存结果
    prfs_df.to_csv(os.path.join(path, '顶级选手画像.csv'), index=False, encoding='utf-8')
    
    return prfs_df

def gen_stl(plyr):
    """生成风格描述"""
    stl = ""
    
    # 判断风格
    if plyr['交易胜率'] > 60 and plyr['盈亏比'] > 1.5:
        stl = "精准型交易者，高胜率配合良好的盈亏比"
    elif plyr['交易胜率'] > 60 and plyr['盈亏比'] <= 1.5:
        stl = "频繁型交易者，追求高胜率但单次盈利相对较小"
    elif plyr['交易胜率'] <= 60 and plyr['盈亏比'] > 1.5:
        stl = "重仓型交易者，单次盈利较大但胜率相对较低"
    else:
        stl = "平衡型交易者，胜率和盈亏比均处于中等水平"
    
    return stl

def gen_rsk(plyr):
    """生成风险描述"""
    rsk = ""
    
    # 判断风险
    if plyr['最大回撤率'] < 20:
        rsk = "极低风险，最大回撤控制出色"
    elif plyr['最大回撤率'] < 40:
        rsk = "中等风险，回撤控制在合理范围"
    else:
        rsk = "高风险，可能存在较大回撤"
    
    if plyr['风险度均值'] < 30:
        rsk += "，整体风险度较低"
    elif plyr['风险度均值'] < 60:
        rsk += "，整体风险度适中"
    else:
        rsk += "，整体风险度较高"
    
    return rsk

def gen_ret(plyr):
    """生成收益描述"""
    ret = ""
    
    # 判断收益
    if plyr['日收益率均值'] > 1:
        ret = "高收益型，日均收益率出色"
    elif plyr['日收益率均值'] > 0.5:
        ret = "稳健收益型，日均收益率良好"
    else:
        ret = "保守收益型，日均收益率适中"
    
    # 判断波动
    if 'day_ret_r' not in plyr:
        if '日收益率最大' in plyr and '日收益率最小' in plyr:
            plyr['day_ret_r'] = plyr['日收益率最大'] - plyr['日收益率最小']
        else:
            plyr['day_ret_r'] = 0
    
    if plyr['day_ret_r'] > 15:
        ret += "，收益波动较大，可能采用激进策略"
    elif plyr['day_ret_r'] > 8:
        ret += "，收益波动适中，策略较为均衡"
    else:
        ret += "，收益波动较小，策略偏向保守"
    
    return ret

# 创建目录
pred_dir = os.path.join(res_dir, '预测模型')
if not os.path.exists(pred_dir):
    os.makedirs(pred_dir)

styl_dir = os.path.join(res_dir, '交易风格分析')
if not os.path.exists(styl_dir):
    os.makedirs(styl_dir)

time_dir = os.path.join(res_dir, '时间序列分析')
if not os.path.exists(time_dir):
    os.makedirs(time_dir)

rank_dir = os.path.join(res_dir, '排名区间分析')
if not os.path.exists(rank_dir):
    os.makedirs(rank_dir)

prof_dir = os.path.join(res_dir, '用户画像')
if not os.path.exists(prof_dir):
    os.makedirs(prof_dir)

# 执行分析
print("开始构建预测模型...")
rnk_mdl, val_mdl, mdl_res = bld_mdl(data, pred_dir)

print("开始进行交易风格深度分析...")
stl_plyr, stl_inf = ana_stl(data, styl_dir)

print("开始进行时间序列分析...")
tim_trnd = ana_tim(data, time_dir)

print("开始进行排名区间分析...")
rnk_ana = ana_rnk(data, rank_dir)

print("开始生成用户画像...")
plyr_prf = gen_prf(data, prof_dir)

print("数据分析完成！结果已保存到:", res_dir)

