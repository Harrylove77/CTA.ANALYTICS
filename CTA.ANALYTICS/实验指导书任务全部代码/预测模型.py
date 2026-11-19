import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import warnings
import os

warnings.filterwarnings('ignore')

# 配置结果目录和文件路径
rdir = r"C:\Users\Administrator\Desktop\大数据综合实践\预测模型结果"
npath = r"C:\Users\Administrator\Desktop\大数据综合实践\用户昵称映射数据.csv"
fpath = r"C:\Users\Administrator\Desktop\大数据综合实践\汇总数据_前2981名选手_20250410_231855.csv"

if not os.path.exists(rdir):
    os.makedirs(rdir)
    print(f"创建目录: {rdir}")

try:
    nmap = pd.read_csv(npath, encoding='utf-8')
    print(f"加载文件: {npath}")
except FileNotFoundError:
    print(f"错误: 未找到文件: {npath}")
    nmap = pd.DataFrame(columns=['客户昵称', '账户昵称列表'])

def gtmap():
    # 创建昵称映射字典
    mdic = {}
    if not nmap.empty:
        for _, row in nmap.iterrows():
            snam = row['客户昵称']
            try:
                acna = eval(str(row['账户昵称列表']))
                if not isinstance(acna, list):
                     acna = [acna]
            except Exception as e:
                acna = []
            for acc in acna:
                if pd.notna(acc):
                    mdic[acc] = snam
            if pd.notna(snam):
                mdic[snam] = snam
    return mdic

mdic = gtmap()
print(f"映射数量: {len(mdic)}")

try:
    dset = pd.read_csv(fpath, encoding='utf-8')
    print(f"加载文件: {fpath}")
    print(f"初始 shape: {dset.shape}")
except FileNotFoundError:
    print(f"错误: 未找到文件: {fpath}")
    dset = pd.DataFrame()
    print("无法继续。")
    # exit() # 可选

if not dset.empty:
    # 数据预处理
    dset = dset.replace('', np.nan)
    print("处理缺失。")

    def sdnic(df, mdic):
        # 标准化昵称
        ndat = df.copy()
        ndat['标准客户昵称'] = ndat['客户昵称'].copy()
        ndat['标准客户昵称'] = ndat['标准客户昵称'].map(lambda x: mdic.get(x, x) if pd.notna(x) else x)
        ndat['标准账户昵称'] = ndat['账户昵称'].map(lambda x: mdic.get(x, x) if pd.notna(x) else x)
        return ndat

    dset = sdnic(dset, mdic)
    print("标准化昵称。")

    # 转换数据类型
    nams = ['期初权益', '期末权益', '累计入金', '累计出金', '累计净值',
            '累计净利润', '日收益率均值', '日收益率最大', '日收益率最小',
            '年化收益率', '盈利天数', '亏损天数', '交易胜率', '盈亏比',
            '手续费/净利润', '风险度均值', '最大回撤率', '届数', '综合排名']
    pnam = [col for col in nams if col in dset.columns]
    for col in pnam:
        dset[col] = pd.to_numeric(dset[col], errors='coerce')
    print("转换类型。")

    # 处理异常值
    outl = ['累计净值', '交易胜率', '盈亏比', '最大回撤率', '风险度均值', '日收益率均值']
    pres = [col for col in outl if col in dset.columns and col in pnam]
    if pres:
        def fxout(df, cols):
            # 处理异常值
            ndat = df.copy()
            for col in cols:
                vdat = ndat[col].dropna()
                if not vdat.empty:
                    qone = vdat.quantile(0.25)
                    qthr = vdat.quantile(0.75)
                    iqrv = qthr - qone
                    lowv = qone - 1.5 * iqrv
                    highv = qthr + 1.5 * iqrv
                    ndat.loc[ndat[col] < lowv, col] = lowv
                    ndat.loc[ndat[col] > highv, col] = highv
            return ndat
        dset = fxout(dset, pres)
        print("处理异常。")
    else:
        print("跳过异常。")

    # 筛选有效数据
    filt = []
    if '累计净值' in dset.columns: filt.append('累计净值')
    if '累计净利润' in dset.columns: filt.append('累计净利润')
    if filt:
        irow = dset.shape[0]
        dset = dset.dropna(subset=filt, how='all')
        print(f"筛选数据，移除 {irow - dset.shape[0]} 行")
    else:
        print("跳过筛选。")

    # 计算参赛次数
    if '标准客户昵称' in dset.columns:
        pcnt = dset.groupby('标准客户昵称').size().reset_index(name='参赛次数')
        dset = pd.merge(dset, pcnt, on='标准客户昵称', how='left')
        print("计算参赛。")
    else:
        print("跳过参赛。")

    # 识别稳定盈利选手
    if '标准客户昵称' in dset.columns and '累计净值' in dset.columns:
        if pd.api.types.is_numeric_dtype(dset['累计净值']):
            stbl = dset.groupby('标准客户昵称').filter(
                lambda x: len(x) >= 3 and (x['累计净值'] > 1).mean() > 0.7
            )
            print("识别稳定。")
        else:
            print("跳过稳定。")
    else:
        print("跳过稳定。")

    print(f"预处理 shape: {dset.shape}")

# 预测第18届排名函数
def prd18(data, rdir):
    """预测第18届排名"""
    print("\n--- 开始预测排名 ---")
    reqc = {
        '届数': pd.api.types.is_numeric_dtype,
        '标准客户昵称': lambda x: True,
        '综合排名': pd.api.types.is_numeric_dtype,
        '累计净值': pd.api.types.is_numeric_dtype,
        '交易胜率': pd.api.types.is_numeric_dtype,
        '盈亏比': pd.api.types.is_numeric_dtype,
        '最大回撤率': pd.api.types.is_numeric_dtype,
        '风险度均值': pd.api.types.is_numeric_dtype,
        '日收益率均值': pd.api.types.is_numeric_dtype
    }
    msng = [col for col in reqc if col not in data.columns]
    if msng:
        print(f"错误: 缺少列: {', '.join(msng)}")
        return None, None
    wtcol = [col for col, chk in reqc.items() if col in data.columns and not chk(data[col])]
    if wtcol:
        print(f"错误: 列类型错: {', '.join(wtcol)}")
        for col in wtcol:
            if col in ['届数', '综合排名', '累计净值', '交易胜率', '盈亏比', '最大回撤率', '风险度均值', '日收益率均值']:
                 data[col] = pd.to_numeric(data[col], errors='coerce')
        wtcv = [col for col, chk in reqc.items() if col in data.columns and col not in msng and not chk(data[col])]
        if wtcv:
             print(f"错误: 转换失败: {', '.join(wtcv)}。")
             return None, None
        else:
             print("警告: 已尝试转换。")

    if not pd.api.types.is_numeric_dtype(data['届数']):
         print("错误: '届数'非数值。")
         return None, None
    dvses = data.dropna(subset=['届数']).copy()
    trdat = dvses[(dvses['届数'] >= 6) & (dvses['届数'] <= 16)].copy()
    tsdat = dvses[dvses['届数'] == 18].copy()
    if tsdat.empty:
        print("错误: 无18届数据。")
        return None, None
    pids = tsdat['标准客户昵称'].unique()
    print(f"预测选手: {len(pids)}")
    hdata = trdat[trdat['标准客户昵称'].isin(pids)].copy()
    if hdata.empty:
        print("错误: 无历史数据。")
        return None, None

    fnam = ['累计净值', '交易胜率', '盈亏比', '最大回撤率', '风险度均值', '日收益率均值']
    pfnam = [col for col in fnam if col in hdata.columns and pd.api.types.is_numeric_dtype(hdata[col])]
    if not pfnam:
         print("错误: 无效特征列。")
         return None, None

    aggd = {col: 'mean' for col in pfnam}
    fetav = hdata.groupby('标准客户昵称').agg(aggd).reset_index()
    pcht = hdata.groupby('标准客户昵称').size().reset_index(name='参赛次数_6_16')
    fetav = pd.merge(fetav, pcht, on='标准客户昵称', how='left')
    fetav['参赛次数_6_16'] = fetav['参赛次数_6_16'].fillna(0)
    mfeat = pfnam + ['参赛次数_6_16']

    tdata = pd.merge(fetav,
                     tsdat[['标准客户昵称', '综合排名']].rename(columns={'综合排名': '综合排名_18'}),
                     on='标准客户昵称',
                     how='inner')
    if tdata.empty:
         print("错误: 合并数据空。")
         return None, None

    xtrn_cols = [col for col in mfeat if col in tdata.columns]
    if not xtrn_cols:
         print("错误: 合并数据无特征。")
         return None, None

    xtrn = tdata[xtrn_cols].copy()
    ytrn = tdata['综合排名_18'].copy()

    if not xtrn.empty:
        fmean = xtrn.mean()
        xtrn = xtrn.fillna(fmean)

    ytrn = ytrn.dropna()
    xtrn = xtrn.loc[ytrn.index]

    if xtrn.empty or ytrn.empty:
         print("错误: 训练数据空。")
         return None, None

    print(f"训练选手: {xtrn.shape[0]}")
    print(f"训练 shape: {xtrn.shape}, 目标 shape: {ytrn.shape}")

    rmodl = RandomForestRegressor(n_estimators=100, random_state=42)
    print("训练模型...")
    rmodl.fit(xtrn, ytrn)
    print("模型完成。")

    xpdat = xtrn.copy()
    xpdat = xpdat[xtrn.columns]
    if not xpdat.empty:
         xpdat = xpdat.fillna(fmean)

    predr = rmodl.predict(xpdat)
    print(f"完成 {len(predr)} 预测。")

    arank = ytrn
    rmse = np.sqrt(mean_squared_error(arank, predr))
    rsqd = r2_score(arank, predr)
    maev = mean_absolute_error(arank, predr)

    pedir = os.path.join(rdir, '预测18届排名')
    if not os.path.exists(pedir):
        os.makedirs(pedir)
        print(f"创建目录: {pedir}")

    evalr = pd.DataFrame({
        '指标': ['RMSE', 'R2', 'MAE'],
        '值': [rmse, rsqd, maev]
    })
    evalr.to_csv(os.path.join(pedir, 'eval_rslt.csv'), index=False, encoding='utf-8')
    print(f"评估保存至: {os.path.join(pedir, 'eval_rslt.csv')}")
    print(f"RMSE: {rmse:.4f}, R2: {rsqd:.4f}, MAE: {maev:.4f}")

    pdet = pd.DataFrame({
        '选手': tdata['标准客户昵称'],
        '实际': arank,
        '预测': predr
    })
    pdet.to_csv(os.path.join(pedir, 'pred_detl.csv'), index=False, encoding='utf-8')
    print(f"详情保存至: {os.path.join(pedir, 'pred_detl.csv')}")

    return rmodl, evalr

# 执行加载，预处理和预测
if 'dset' in locals() and not dset.empty:
    rmodl, evalr = prd18(dset, rdir)
    if evalr is not None:
        print("\n预测结果:")
        print(evalr)
else:
    print("\n加载失败，跳过。")

