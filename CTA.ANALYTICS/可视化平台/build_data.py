# -*- coding: utf-8 -*-
"""
可视化平台 · 数据构建脚本
------------------------------------------------------------
读取  数据分析结果/ 与 csv结果文件/ 中的原始结果，
按任务书（大数据综合应用实践任务书·金融大数据）要求补全计算：
  · 单项指标画像 / 多项指标聚类画像
  · 排名区间对比（前10 / 前50 / 前100 / 前200 / 后20 / 后100）
  · 第 11-19 届 → 第 20 届排名预测 + 准确率评估
  · 交易风格画像 / 选手画像检索 / 时间序列趋势
输出  assets/data/data.js  →  window.DASH_DATA = {...}
用法  python build_data.py
"""
import io
import os
import json
import datetime

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from glob import glob

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RES = os.path.join(ROOT, "数据分析结果")
RAW = os.path.join(ROOT, "csv结果文件")
OUT = os.path.join(HERE, "assets", "data", "data.js")

METRICS = [
    ("累计净值", "net", "累计净值（倍）", "使用赛事提供的累计净值字段，1 为净值基准。"),
    ("交易胜率", "win", "交易胜率（%）", "盈利交易笔数 ÷ 总交易笔数，以赛事指标定义为准。"),
    ("盈亏比", "pl", "盈亏比", "平均每笔盈利 ÷ 平均每笔亏损，须结合胜率和交易成本解读。"),
    ("最大回撤率", "dd", "最大回撤率（%）", "净值由高点到低点的最大跌幅，衡量风险控制能力。"),
    ("风险度均值", "risk", "风险度均值（%）", "保证金占用比例的时间均值，反映仓位激进程度。"),
    ("日收益率均值", "daily", "日收益率均值（%）", "比赛期间每日收益率的算术均值。"),
]
KEYS = [m[1] for m in METRICS]
FEATS = [m[0] for m in METRICS]

LOG = []


def log(*a):
    msg = " ".join(str(x) for x in a)
    print(msg)
    LOG.append(msg)


def rnd(x, n=4):
    """安全取整，NaN/Inf → None"""
    try:
        v = float(x)
    except Exception:
        return None
    if not np.isfinite(v):
        return None
    return round(v, n)


def read_csv(*parts, **kw):
    return pd.read_csv(os.path.join(*parts), low_memory=False, **kw)


# ============================================================
# 1. 单项指标画像
# ============================================================
def build_single():
    out = {}
    for col, key, label, desc in METRICS:
        df = read_csv(RES, "单项指标分析", "%s_分析.csv" % col)
        s = pd.to_numeric(df[col], errors="coerce").dropna()
        counts, edges = np.histogram(s, bins=26)
        top = df.nlargest(6, col)[["标准客户昵称", col, "参赛次数"]]
        bot = df.nsmallest(6, col)[["标准客户昵称", col, "参赛次数"]]

        # 按参赛次数分组的均值（1-2 届 / 3-5 届 / 6+ 届）
        cut = pd.cut(pd.to_numeric(df["参赛次数"], errors="coerce"),
                     [0, 2, 5, 999], labels=["1-2届", "3-5届", "6届以上"])
        grp = df.groupby(cut, observed=True)[col].mean()

        out[key] = {
            "name": col,
            "label": label,
            "desc": desc,
            "n": int(s.size),
            "hist": {
                "labels": [("%%.%df" % (2 if abs(e) > 10 else 3)) % e for e in edges[:-1]],
                "counts": [int(c) for c in counts],
                "edges": [rnd(e) for e in edges],
            },
            "stats": {
                "mean": rnd(s.mean()), "median": rnd(s.median()), "std": rnd(s.std()),
                "min": rnd(s.min()), "max": rnd(s.max()),
                "q1": rnd(s.quantile(.25)), "q3": rnd(s.quantile(.75)),
                "p10": rnd(s.quantile(.10)), "p90": rnd(s.quantile(.90)),
            },
            "top": [{"name": str(a), "v": rnd(b), "n": int(c)} for a, b, c in top.values],
            "bottom": [{"name": str(a), "v": rnd(b), "n": int(c)} for a, b, c in bot.values],
            "byFreq": [{"name": str(k), "v": rnd(v)} for k, v in grp.items()],
        }
        log("  单项指标 %-6s n=%d 均值=%.3f 中位数=%.3f" % (col, s.size, s.mean(), s.median()))
    return out


# ============================================================
# 2. 多项指标（聚类）画像
# ============================================================
def build_cluster():
    d = read_csv(RES, "多项指标分析", "多指标分析结果.csv")
    feat = read_csv(RES, "多项指标分析", "聚类特征分析.csv")
    values = d[FEATS].to_numpy(dtype=float)
    scale = values.std(axis=0)
    standardized = (values - values.mean(axis=0)) / np.where(scale > 0, scale, 1)
    _, singular, directions = np.linalg.svd(standardized, full_matrices=False)
    xy = standardized @ directions[:2].T
    explained = singular[:2] ** 2 / (singular ** 2).sum()

    scatter = []
    for i, row in enumerate(d.itertuples(index=False)):
        scatter.append([rnd(xy[i, 0], 3), rnd(xy[i, 1], 3), int(row.聚类),
                        str(row.标准客户昵称), rnd(row.累计净值, 3),
                        rnd(row.交易胜率, 2), rnd(row.最大回撤率, 2)])

    # 雷达（按 min-max 归一到 0-100 便于同图对比）
    radar_features = ["累计净值", "交易胜率", "盈亏比", "最大回撤率", "风险度均值", "日收益率均值"]
    mins = {c: float(d[c].min()) for c in radar_features}
    maxs = {c: float(d[c].max()) for c in radar_features}
    radar = []
    for _, row in feat.iterrows():
        vals = [rnd((row[c] - mins[c]) / (maxs[c] - mins[c] or 1) * 100, 2) for c in radar_features]
        radar.append({"name": "聚类 %d" % int(row["聚类"]), "value": vals})

    profile = []
    for _, row in feat.iterrows():
        k = int(row["聚类"])
        sub = d[d["聚类"] == k]
        best = float(sub["累计净值"].max())
        profile.append({
            "cluster": k,
            "size": int(len(sub)),
            "net": rnd(row["累计净值"], 3), "win": rnd(row["交易胜率"], 2),
            "pl": rnd(row["盈亏比"], 3), "dd": rnd(row["最大回撤率"], 2),
            "risk": rnd(row["风险度均值"], 2), "daily": rnd(row["日收益率均值"], 3),
            "freq": rnd(row["参赛次数"], 2), "best": rnd(best, 3),
            "posRatio": rnd(sub["累计净值"].gt(1).mean() * 100, 1),
            "label": "较高净值组" if row["累计净值"] >= d["累计净值"].mean() else "较低净值组",
        })
    log("  聚类 %d 类，样本 %d" % (len(feat), len(d)))
    return {
        "radarAxis": radar_features, "radar": radar, "profile": profile,
        "scatter": scatter,
        "explained": [rnd(v * 100, 2) for v in explained],
        "mins": mins, "maxs": maxs,
        "total": int(len(d)),
    }
# ============================================================
# 3. 排名区间对比（任务书：前50、前200 与 后20 名选手差异）
# ============================================================
def build_rank_groups():
    df = raw_results()
    ranked = df[df["综合排名"].gt(0)]
    cohorts = list(ranked.groupby(["届数", "组别"]))
    rows = []
    for end in (10, 50, 100, 200, -20, -100):
        if end > 0:
            sample = ranked[ranked["综合排名"].le(end)]
        else:
            count = -end
            eligible = [g.nlargest(count, "综合排名") for _, g in cohorts if len(g) >= 2 * count]
            sample = pd.concat(eligible) if eligible else ranked.iloc[:0]
        name = "%s%d名" % ("前" if end > 0 else "后", abs(end))
        note = "按同届同组官网名次筛选" if end > 0 else "样本内尾部，组内至少有 %d 条有效排名" % (-2 * end)
        rows.append(rank_summary(sample, name, note))
    return {"rows": rows, "base": rank_summary(ranked, "有排名样本", "有效综合排名记录")}


def rank_summary(sample, name, note):
    net = sample["累计净值"].dropna()
    row = {"group": name, "note": note, "n": len(sample),
           "players": int(sample["客户昵称"].nunique()),
           "rankMean": rnd(sample["综合排名"].mean(), 1),
           "posRatio": rnd(net.gt(1).mean() * 100, 1)}
    for column, key in zip(FEATS, KEYS):
        row[key] = rnd(sample[column].mean())
    return row


# ============================================================
# 4. 时间序列：历届整体趋势
# ============================================================
def build_trend():
    df = overview_records()
    df["届数"] = pd.to_numeric(df["届数"], errors="coerce")
    g = df.groupby("届数")
    out = {
        "editions": [int(e) for e in sorted(df["届数"].dropna().unique())],
        "players": [int((g.get_group(e)["标准客户昵称"].nunique())) for e in sorted(df["届数"].dropna().unique())],
    }
    for c, k in zip(FEATS, KEYS):
        vals = []
        for e in sorted(df["届数"].dropna().unique()):
            s = pd.to_numeric(g.get_group(e)[c], errors="coerce")
            vals.append(rnd(s.mean()))
        out[k] = vals
    log("  时间序列 %d 届：%s" % (len(out["editions"]), out["editions"]))
    return out


# ============================================================
# 5. 交易风格画像
# ============================================================
def build_style():
    d = read_csv(RES, "交易风格分析", "选手交易风格详细分类.csv")
    detail = read_csv(RES, "交易风格分析", "交易风格详细分析.csv")
    cnt = d["交易风格名称"].value_counts()
    pie = [{"name": str(k), "value": int(v)} for k, v in cnt.items()]

    box = {}
    for c, k in zip(FEATS, KEYS):
        arr = []
        for name in cnt.index:
            s = pd.to_numeric(d.loc[d["交易风格名称"] == name, c], errors="coerce").dropna()
            arr.append([rnd(s.min()), rnd(s.quantile(.25)), rnd(s.median()),
                        rnd(s.quantile(.75)), rnd(s.max())])
        box[k] = arr
    table = []
    for _, row in detail.iterrows():
        sub = d[d["交易风格名称"] == row["风格名称"]]
        table.append({
            "key": int(row["交易风格"]),
            "name": str(row["风格名称"]),
            "desc": str(row["特点描述"]),
            "size": int(len(sub)),
            "share": rnd(len(sub) / len(d) * 100, 1),
            "net": rnd(pd.to_numeric(sub["累计净值"], errors="coerce").mean(), 3),
            "win": rnd(pd.to_numeric(sub["交易胜率"], errors="coerce").mean(), 2),
            "pl": rnd(pd.to_numeric(sub["盈亏比"], errors="coerce").mean(), 3),
            "dd": rnd(pd.to_numeric(sub["最大回撤率"], errors="coerce").mean(), 2),
        })
    log("  交易风格 %s" % dict(cnt))
    return {"pie": pie, "box": box, "boxCats": [str(x) for x in cnt.index],
            "table": table, "total": int(len(d)), "metrics": KEYS}
# ============================================================
# 6. 排名预测（任务书：用第 11-19 届数据预测第 20 届排名并评估准确率）
# ============================================================
def raw_results():
    paths = sorted(glob(os.path.join(RAW, "汇总数据_*.csv")))
    if len(paths) != 1:
        raise ValueError("csv结果文件中应有一份汇总数据 CSV")
    data = pd.read_csv(paths[0], low_memory=False)
    for column in FEATS + ["综合排名", "届数"]:
        data[column] = pd.to_numeric(data[column], errors="coerce").replace([np.inf, -np.inf], np.nan)
    return data


MODEL_COLUMNS = ["历史有效排名届数", "距离最近排名的届数", "上次对数名次", "历史平均对数名次"]
BUCKET_LIMITS = [10, 50, 100, 200]
BUCKET_LABELS = ["1–10", "11–50", "51–100", "101–200", "201+"]
GROUP_ALIASES = {"轻量级": "轻量组", "重量级": "重量组", "程序化": "量化组"}


def rank_history(data, target):
    past = data[data["届数"].between(11, min(target - 1, 19))].copy()
    past["对数名次"] = np.log1p(past["综合排名"])
    past = past.groupby(["客户昵称", "组别", "届数"], as_index=False)["对数名次"].median()
    features = past.groupby(["客户昵称", "组别"])["对数名次"].agg(["count", "last", "mean"])
    latest = past.groupby(["客户昵称", "组别"])["届数"].max()
    features["gap"] = target - latest
    features = features[["count", "gap", "last", "mean"]]
    features.columns = MODEL_COLUMNS
    return features


def target_ranks(data, target):
    ranks = data[data["届数"].eq(target)]
    grouped = ranks.groupby(["客户昵称", "组别"])["综合排名"]
    # 有多个不同账户名次时缺少唯一选手标签，排除这些目标记录。
    return grouped.first().loc[grouped.nunique().eq(1)].rename("actual")


def historical_examples(data, before):
    return pd.concat([
        rank_history(data, edition).join(target_ranks(data, edition), how="inner")
        for edition in range(12, before)
    ])


def fit_rank_model(data, before):
    training = historical_examples(data, before)
    x = training[MODEL_COLUMNS].to_numpy()
    y = np.log1p(training["actual"].to_numpy())
    center = x.mean(axis=0)
    scale = x.std(axis=0)
    scale[scale == 0] = 1
    z = (x - center) / scale
    weights = np.linalg.solve(z.T @ z + np.eye(z.shape[1]), z.T @ (y - y.mean()))
    return center, scale, weights, y.mean(), len(training)


def rank_estimates(features, model):
    center, scale, weights, intercept, _ = model
    logged = ((features[MODEL_COLUMNS].to_numpy() - center) / scale) @ weights + intercept
    return np.maximum(1, np.rint(np.expm1(logged)))


OFFICIAL_GROUPS = {1: "轻量组", 2: "重量组", 3: "高净值组", 4: "量化组"}


def official_results():
    path = os.path.join(RAW, "第19与20届官网样本.csv")
    if not os.path.isfile(path):
        return pd.DataFrame()
    data = pd.read_csv(path, dtype={"客户昵称": str, "账户昵称": str})
    code = data["组别代码"]
    data["组别"] = code.map(OFFICIAL_GROUPS)
    return data


RANK_METHODS = ("最近同组名次", "历史对数均值", "近期加权", "岭回归")


TREE_METHODS = ("随机森林回归", "XGBoost 回归")


def model_features(rows):
    # 只使用目标届之前形成的历史特征。新增组别是为了区分排名规模。
    features = rows[MODEL_COLUMNS].copy()
    for group in OFFICIAL_GROUPS.values():
        features[group] = (rows.index.get_level_values("组别") == group).astype(int)
    return features.to_numpy()


def tree_estimates(data, edition, rows):
    training = historical_examples(data, edition)
    x = model_features(training)
    y = np.log1p(training["actual"].to_numpy())
    candidates = (
        RandomForestRegressor(n_estimators=200, max_depth=4, min_samples_leaf=8, random_state=42, n_jobs=1),
        XGBRegressor(n_estimators=160, max_depth=2, learning_rate=.035, min_child_weight=8,
                     subsample=.85, colsample_bytree=.9, reg_lambda=5, random_state=42, n_jobs=1),
    )
    target = model_features(rows)
    return {
        name: np.maximum(1, np.rint(np.expm1(model.fit(x, y).predict(target))))
        for name, model in zip(TREE_METHODS, candidates)
    }


def candidate_estimates(rows, ridge):
    latest = rows[MODEL_COLUMNS[2]]
    average = rows[MODEL_COLUMNS[3]]
    return {
        RANK_METHODS[0]: np.maximum(1, np.rint(np.expm1(latest))),
        RANK_METHODS[1]: np.maximum(1, np.rint(np.expm1(average))),
        RANK_METHODS[2]: np.maximum(1, np.rint(np.expm1(.8 * latest + .2 * average))),
        RANK_METHODS[3]: rank_estimates(rows, ridge),
    }


def select_rank_method(data, before):
    errors = {}
    editions = []
    n = 0
    for edition in (18, 19):
        if edition >= before:
            continue
        rows = rank_history(data, edition).join(target_ranks(data, edition), how="inner")
        if len(rows) < 10:
            continue
        estimates = candidate_estimates(rows, fit_rank_model(data, edition))
        estimates.update(tree_estimates(data, edition, rows))
        for name, prediction in estimates.items():
            error = np.abs(rows["actual"].to_numpy() - prediction)
            errors.setdefault(name, []).append(float(np.median(error)))
        editions.append(edition)
        n += len(rows)
    report = sorted(
        ({"name": name, "v": rnd(np.mean(scores), 1), "foldErrors": [rnd(x, 1) for x in scores]}
         for name, scores in errors.items()),
        key=lambda item: item["v"],
    )
    return (report[0]["name"] if report else RANK_METHODS[0]), editions, n, report


def rank_bucket(values):
    return np.searchsorted(BUCKET_LIMITS, values, side="left")


def interval_methods(data, edition, rows, estimates):
    training = historical_examples(data, edition)
    last = rank_bucket(np.expm1(training[MODEL_COLUMNS[2]]).round())
    actual = rank_bucket(training["actual"])
    lookup = pd.DataFrame({"group": training.index.get_level_values("组别"), "last": last, "actual": actual})
    prior = np.bincount(actual, minlength=5) + 1
    prior = prior / prior.sum()
    by_last = lookup.groupby(["last", "actual"]).size().unstack(fill_value=0).reindex(
        index=range(5), columns=range(5), fill_value=0)
    by_group = lookup.groupby(["group", "last", "actual"]).size().unstack(fill_value=0).reindex(
        columns=range(5), fill_value=0)
    target_last = rank_bucket(estimates[RANK_METHODS[0]])
    target_index = pd.MultiIndex.from_arrays([rows.index.get_level_values("组别"), target_last])
    group_counts = by_group.reindex(target_index, fill_value=0).to_numpy()
    condition = by_last.to_numpy() + 5 * prior
    condition /= condition.sum(axis=1, keepdims=True)
    scores = group_counts + 10 * condition[target_last]
    return {
        "最近同组区间": target_last,
        "岭回归区间": rank_bucket(estimates[RANK_METHODS[3]]),
        "历史区间转移": scores.argmax(axis=1),
        "类别校正区间转移": (scores / np.sqrt(prior)).argmax(axis=1),
    }


def interval_scores(actual, predicted):
    matrix = np.zeros((5, 5), dtype=int)
    np.add.at(matrix, (actual, predicted), 1)
    support = matrix.sum(axis=0) + matrix.sum(axis=1)
    present = support > 0
    return (actual == predicted).mean(), (2 * matrix.diagonal()[present] / support[present]).mean(), matrix


def select_interval_method(data, before):
    report = {}
    editions = []
    for edition in (18, 19):
        if edition >= before:
            continue
        rows = rank_history(data, edition).join(target_ranks(data, edition), how="inner")
        if len(rows) < 10:
            continue
        estimates = candidate_estimates(rows, fit_rank_model(data, edition))
        truth = rank_bucket(rows["actual"])
        for name, prediction in interval_methods(data, edition, rows, estimates).items():
            hit, macro, _ = interval_scores(truth, prediction)
            report.setdefault(name, []).append((hit, macro, np.unique(prediction).size > 1))
        editions.append(edition)
    if not report:
        return "最近同组区间", editions
    averages = {name: np.mean(stats, axis=0) for name, stats in report.items()}
    # 排除任一验证届只预测单一类别的方法，再比较命中率与宏 F1。
    nontrivial = {name: score for name, score in averages.items() if score[2] == 1}
    if not nontrivial:
        return "最近同组区间", editions
    best_hit = max(score[0] for score in nontrivial.values())
    eligible = [name for name, score in nontrivial.items() if score[0] >= best_hit - .05]
    return max(eligible, key=lambda name: (averages[name][1], averages[name][0])), editions


def recovered_rank_snapshot():
    path = os.path.join(HERE, "assets", "data", "排名建模快照_看板归档.csv")
    if not os.path.isfile(path):
        return pd.DataFrame()
    return pd.read_csv(path, dtype={"客户昵称": str})


def build_predict(rank_snapshot=None):
    data = raw_results()
    official = official_results()
    archived = recovered_rank_snapshot() if rank_snapshot is None else rank_snapshot
    if official.empty and not archived.empty:
        data = pd.concat([data[data["届数"].lt(19)], archived], ignore_index=True)
    if not official.empty:
        known = official.dropna(subset=["组别"])
        data = pd.concat([data[data["届数"].lt(19)], known], ignore_index=True)
    label_path = os.path.join(RAW, "第20届综合排名.csv")
    if os.path.isfile(label_path):
        labels = pd.read_csv(label_path, usecols=["客户昵称", "组别", "综合排名"])
        labels["届数"] = 20
        labels["综合排名"] = pd.to_numeric(labels["综合排名"], errors="coerce")
        data = pd.concat([data[data["届数"].ne(20)], labels], ignore_index=True)
    data["组别"] = data["组别"].replace(GROUP_ALIASES)
    data = data[data["综合排名"].gt(0) & np.isfinite(data["综合排名"])]
    forecast_model = fit_rank_model(data, 20)
    forecast = rank_history(data, 20)
    forecast = forecast.join(target_ranks(data, 20))
    test_edition = 20 if forecast["actual"].notna().any() else 18
    selected, selection_editions, selection_n, selection = select_rank_method(data, test_edition)
    forecast_estimates = candidate_estimates(forecast, forecast_model)
    forecast_estimates.update(tree_estimates(data, 20, forecast))
    forecast["pred"] = forecast_estimates[selected]
    interval_method, interval_editions = select_interval_method(data, test_edition)
    forecast["bucket"] = interval_methods(data, 20, forecast, forecast_estimates)[interval_method]
    real_validation = forecast.dropna(subset=["actual"])
    if test_edition == 20:
        model, test = forecast_model, real_validation.copy()
    else:
        model = fit_rank_model(data, test_edition)
        test = rank_history(data, test_edition).join(target_ranks(data, test_edition), how="inner")
        estimates = candidate_estimates(test, model)
        estimates.update(tree_estimates(data, test_edition, test))
        test["pred"] = estimates[selected]
        test["bucket"] = interval_methods(data, test_edition, test, estimates)[interval_method]
    actual, pred = test["actual"], test["pred"]
    truth = rank_bucket(actual)
    guesses = test["bucket"].to_numpy(dtype=int)
    hit, macro, cm = interval_scores(truth, guesses)
    residuals = np.log1p(pred) - np.log1p(actual)
    variance = ((np.log1p(actual) - np.log1p(actual).mean()) ** 2).sum()
    counts, edges = np.histogram(residuals, bins=22)
    precision, baseline = {}, {}
    for k in (20, 50, 100):
        precision["p%d" % k] = rnd(test.nsmallest(k, "pred")["actual"].le(k).mean() * 100, 1)
        baseline["p%d" % k] = rnd(actual.le(k).mean() * 100, 1)
    top = forecast.reset_index().sort_values(["pred", "组别", "客户昵称"]).head(20)
    top20 = [{"name": row["客户昵称"], "grp": row["组别"], "pred": rnd(row["pred"], 0),
              "actual": rnd(row["actual"], 0), "history": int(row[MODEL_COLUMNS[0]])}
             for _, row in top.iterrows()]
    official_counts = {} if official.empty else official.groupby("届数").size().to_dict()
    actual_rows = [
        {"name": nick, "grp": group, "pred": int(row["pred"]), "actual": int(row["actual"]),
         "error": int(abs(row["pred"] - row["actual"])),
         "predBucket": BUCKET_LABELS[int(row["bucket"])],
         "actualBucket": BUCKET_LABELS[int(rank_bucket(row["actual"]))]}
        for (nick, group), row in real_validation.sort_values("actual").iterrows()
    ]
    previous = np.maximum(1, np.rint(np.expm1(test[MODEL_COLUMNS[2]])))
    evaluation_estimates = (
        {name: pd.Series(values, index=forecast.index).loc[test.index].to_numpy()
         for name, values in forecast_estimates.items()}
        if test_edition == 20 else estimates
    )
    model_comparison = [
        {"name": name, "error": rnd(np.median(np.abs(actual.to_numpy() - values)), 1),
         "spearman": rnd(actual.rank().corr(pd.Series(values, index=test.index).rank()))}
        for name, values in evaluation_estimates.items()
    ]
    head = truth < 4
    head_pred = guesses < 4
    head_recall = rnd(head_pred[head].mean() * 100, 2) if head.any() else None
    head_precision = rnd(head[head_pred].mean() * 100, 2) if head_pred.any() else None
    majority = rnd(cm.sum(axis=1).max() / len(test) * 100, 2)
    log("  排名模型：第%d届评估 %d 条，第20届候选 %d 条" % (test_edition, len(test), len(forecast)))
    return {
        "model": selected, "intervalModel": interval_method, "intervalEditions": interval_editions,
        "officialSampleSize": 0 if official.empty else int(official["特别奖总榜名次"].notna().groupby(official["届数"]).sum().max()),
        "testSize": len(test), "trainSize": model[-1],
        "selectionEditions": selection_editions, "selectionSize": selection_n,
        "modelComparison": model_comparison,
        "forecastSize": len(forecast), "forecastTrainSize": forecast_model[-1],
        "lastHistory": int(data.loc[data["届数"].between(11, 19), "届数"].max()),
        "official19": int(official_counts.get(19, 0)), "official20": int(official_counts.get(20, 0)),
        "archivedRanks": official.empty and not archived.empty,
        "history19Matched": int((real_validation[MODEL_COLUMNS[1]] == 1).sum()),
        "actualCount": len(real_validation), "window": {"test": test_edition},
        "metrics": {"r2": rnd(1 - (residuals ** 2).sum() / variance) if variance > 0 else None,
                    "maeRank": rnd((actual - pred).abs().median(), 1),
                    "spearman": rnd(actual.rank().corr(pred.rank())),
                    "hit": rnd(hit * 100, 2),
                    "f1": rnd(macro * 100, 2)},
        "precision": precision, "baseline": baseline,
        "confusion": {"labels": BUCKET_LABELS, "matrix": cm.tolist()},
        "scatter": [[int(y), int(p), int(bucket)] for y, p, bucket in zip(actual, pred, truth)],
        "resid": {"labels": [rnd(edge, 2) for edge in edges[:-1]], "counts": counts.tolist()},
        "importance": selection,
        "top20": top20, "actualRows": actual_rows,
        "previousRankError": rnd((actual - previous).abs().median(), 1),
        "majorityHit": majority, "headRecall": head_recall, "headPrecision": head_precision,
        "headActual": int(head.sum()), "headPredicted": int(head_pred.sum()),
    }


# ============================================================
# 7. 选手画像索引（支持平台内检索）+ 数据总览
# ============================================================
def build_players():
    d = read_csv(RES, "多项指标分析", "多指标分析结果.csv")
    st = read_csv(RES, "交易风格分析", "选手交易风格详细分类.csv")
    st_map = dict(zip(st["标准客户昵称"].astype(str), st["交易风格名称"].astype(str)))
    raw = read_csv(RES, "预处理后数据.csv")
    raw["综合排名"] = pd.to_numeric(raw["综合排名"], errors="coerce")
    raw["届数"] = pd.to_numeric(raw["届数"], errors="coerce")
    official = official_results()
    daily = {}
    if not official.empty:
        aliases = raw.groupby("客户昵称")["标准客户昵称"].agg(lambda values: values.iloc[0] if values.nunique() == 1 else None)
        official["标准客户昵称"] = official["客户昵称"].map(aliases).fillna(official["客户昵称"])
        official["组别"] = official["组别"].fillna("组别待核验")
        for nick, records in official.groupby("标准客户昵称"):
            daily[str(nick)] = [
                {"edition": int(row["届数"]), "account": row["账户昵称"], "points": json.loads(row["日度净值"])}
                for _, row in records.iterrows() if isinstance(row["日度净值"], str)
            ]
        raw = pd.concat([raw, official], ignore_index=True)
    best = raw.groupby("标准客户昵称")["综合排名"].min().to_dict()
    frequency = raw.groupby("标准客户昵称")["届数"].nunique().to_dict()

    # 百分位（回撤率、风险度越低越好，取 100-百分位）
    pct = {}
    for c, k in zip(FEATS, KEYS):
        p = d[c].rank(pct=True, ascending=k not in ("dd", "risk")) * 100
        pct[k] = p

    account_fields = ["期初权益", "期末权益", "累计净值", "累计净利润", "最大本金收益率",
                      "日收益率均值", "最大回撤率", "风险度均值", "交易胜率", "盈亏比",
                      "盈利天数", "亏损天数", "综合排名"]
    accounts = {}
    for nick, records in raw.sort_values("届数", ascending=False).groupby("标准客户昵称"):
        accounts[str(nick)] = [[int(row["届数"]), str(row["组别"]), str(row["账户昵称"])]
                               + [rnd(row.get(field)) for field in account_fields]
                               for _, row in records.dropna(subset=["届数"]).iterrows()]
    hist = {}
    for nick, g in raw.sort_values("届数").groupby("标准客户昵称"):
        g = g.drop_duplicates(subset=["届数"], keep="last").tail(12)
        hist[str(nick)] = [[int(e), rnd(nv, 3), rnd(w, 1), rnd(dd, 1),
                            None if pd.isna(rk) else int(rk)]
                           for e, nv, w, dd, rk in zip(g["届数"], g["累计净值"], g["交易胜率"],
                                                       g["最大回撤率"], g["综合排名"])]

    out = []
    for i, row in d.iterrows():
        nick = str(row["标准客户昵称"])
        out.append({
            "name": nick,
            "n": int(frequency.get(nick, row["参赛次数"])),
            "net": rnd(row["累计净值"], 3), "win": rnd(row["交易胜率"], 2),
            "pl": rnd(row["盈亏比"], 3), "dd": rnd(row["最大回撤率"], 2),
            "risk": rnd(row["风险度均值"], 2), "daily": rnd(row["日收益率均值"], 3),
            "cluster": int(row["聚类"]),
            "style": st_map.get(nick, "—"),
            "best": None if pd.isna(best.get(nick)) else int(best.get(nick)),
            "p": [rnd(pct[k].iloc[i], 1) for k in KEYS],
            "h": hist.get(nick, []),
            "accounts": accounts.get(nick, []), "dailySeries": daily.get(nick, []),
        })
    known_names = {item["name"] for item in out}
    for nick in daily.keys() - known_names:
        records = raw[raw["标准客户昵称"].eq(nick)]
        item = {key: rnd(records[column].mean()) for key, column in zip(KEYS, FEATS)}
        item.update(name=nick, n=int(frequency[nick]), cluster=None, style="未分类",
                    best=rnd(best.get(nick), 0), p=[], h=hist[nick], accounts=accounts[nick],
                    dailySeries=daily[nick])
        out.append(item)
    out.sort(key=lambda item: (item["cluster"] is None, item["name"]))
    log("  选手索引 %d 人" % len(out))
    return out


def overview_records():
    historical = read_csv(RES, "预处理后数据.csv")
    official = official_results()
    if official.empty:
        return historical
    edition = official[official["届数"].eq(19)].copy()
    names = historical.groupby("客户昵称")["标准客户昵称"].agg(
        lambda rows: rows.iloc[0] if rows.nunique() == 1 else None)
    edition["标准客户昵称"] = edition["客户昵称"].map(names).fillna(edition["客户昵称"])
    edition["组别"] = edition["组别"].fillna("组别待核验")
    return pd.concat([historical[historical["届数"].ne(19)], edition], ignore_index=True)


def build_overview():
    raw = overview_records()
    miss = raw.isna().mean().sort_values(ascending=False)
    groups = (raw["组别"].astype(str)
              .replace({"轻量级": "轻量组", "重量级": "重量组", "程序化": "程序化组"})
              .value_counts())
    top = read_csv(RES, "用户画像", "顶级选手画像.csv")
    top_list = [{
        "name": str(row["标准客户昵称"]), "n": int(row["参赛次数"]),
        "best": None if pd.isna(row["最佳排名"]) else int(row["最佳排名"]),
        "net": rnd(row["平均累计净值"], 3),
        "style": str(row["交易风格描述"]), "risk": str(row["风险特征"]),
        "profit": str(row["收益特征"]),
    } for _, row in top.iterrows()]

    return {
        "rows": int(len(raw)),
        "players": int(raw["标准客户昵称"].nunique()),
        "editions": [int(e) for e in sorted(pd.to_numeric(raw["届数"], errors="coerce").dropna().unique())],
        "fields": int(raw.shape[1]),
        "missing": [{"field": str(k), "rate": rnd(v * 100, 2)} for k, v in miss.head(14).items()],
        "groups": [{"name": str(k), "value": int(v)} for k, v in groups.items()],
        "editionCount": [{"name": "第%d届" % int(e), "value": int(c)}
                         for e, c in pd.to_numeric(raw["届数"], errors="coerce")
                         .value_counts().sort_index().items()],
        "topPlayers": top_list,
        "dealers": [{"name": str(k), "value": int(v)} for k, v in
                    raw["指定交易商"].astype(str).value_counts().head(10).items()],
    }
# ============================================================
# main
# ============================================================
def build_award():
    source = official_results()
    if source.empty:
        return []
    # 特别奖榜名次可能并列，用榜单阈值归组。只比较同时有两届净值的关联记录。
    keys = ["特别奖总榜名次", "客户昵称"]
    unique = source.drop_duplicates(keys + ["届数"], keep=False)
    paired = unique.pivot(index=keys, columns="届数", values="累计净值").dropna(subset=[19, 20])
    previous = unique[unique["届数"].eq(19)].set_index(keys).join(paired[[20]], how="inner").reset_index()
    metrics = {"net": "累计净值", "win": "交易胜率", "dd": "最大回撤率",
               "risk": "风险度均值", "daily": "日收益率均值"}
    rows = []
    for name, group in previous.groupby(pd.cut(previous["特别奖总榜名次"], [0, 50, 100, 150],
                                               labels=["第 1–50 名", "第 51–100 名", "第 101–150 名"]),
                                        observed=True):
        row = {"name": str(name), "n": len(group),
               "positiveBoth": rnd((group["累计净值"].gt(1) & group[20].gt(1)).mean() * 100, 1)}
        row.update({key: rnd(group[field].median(), 3) for key, field in metrics.items()})
        rows.append(row)
    return rows


def main():
    if not os.path.isfile(os.path.join(RAW, "第19与20届官网样本.csv")):
        raise FileNotFoundError("缺少第19与20届官网样本.csv，请先运行 fetch_official.py。")
    log("=" * 64)
    log("构建可视化平台数据 …")
    overview = build_overview()
    single = build_single()
    cluster = build_cluster()
    rankg = build_rank_groups()
    trend = build_trend()
    style = build_style()
    predict = build_predict()
    players = build_players()

    kpi = [
        {"k": "参赛记录", "v": overview["rows"], "u": "条",
         "s": "第 %d-%d 届" % (overview["editions"][0], overview["editions"][-1])},
        {"k": "去重选手", "v": overview["players"], "u": "人", "s": "十年特别奖选手池"},
        {"k": "分析指标", "v": 6, "u": "项", "s": "净值·胜率·盈亏比·回撤·风险度·日收益"},
        {"k": "聚类建模", "v": cluster["total"], "u": "人", "s": "KMeans k=2 + PCA"},
        {"k": "预测 R²", "v": predict["metrics"]["r2"], "u": "", "s": "第 %d 届名次 · %s"
         % (predict["window"]["test"], predict["model"])},
        {"k": "名次相关性", "v": predict["metrics"]["spearman"], "u": "",
         "s": "预测名次 vs 实际名次 · Spearman"},
        {"k": "区间命中率", "v": predict["metrics"]["hit"], "u": "%", "s": "前10/50/100/200/以外 五档分类"},
    ]

    data = {
        "meta": {
            "title": "全国期货实盘交易大赛 · 十年特别奖选手特征分析平台",
            "subtitle": "大数据综合应用实践 · 金融大数据方向",
            "built": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "source": "数据分析结果/ + csv结果文件/",
        },
        "kpi": kpi, "overview": overview, "award": build_award(), "single": single,
        "metrics": [{"key": k, "name": c, "label": l, "desc": d} for c, k, l, d in METRICS],
        "cluster": cluster, "rankGroups": rankg, "trend": trend, "style": style,
        "predict": predict, "players": players,
    }

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    payload = "window.DASH_DATA = " + json.dumps(data, ensure_ascii=False, allow_nan=False, separators=(",", ":")) + ";\n"
    with io.open(OUT, "w", encoding="utf-8") as f:
        f.write(payload)
    log("输出 → %s （%.1f KB）" % (OUT, len(payload.encode("utf-8")) / 1024))
    log("=" * 64)


if __name__ == "__main__":
    main()






