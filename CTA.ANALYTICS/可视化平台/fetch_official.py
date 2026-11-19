"""下载官网十年特别奖榜首 650 条关联账户的收官数据。"""
import csv
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen
from urllib.error import URLError
from time import sleep

BASE = "https://spdspc.qhrb.com.cn/api/"
DATES = {19: "2025-09-26", 20: "2026-09-30"}
FIELDS = {
    "groupType": "组别代码", "sort": "综合排名", "openAmount": "期初权益", "endAmount": "期末权益",
    "netWorth": "累计净值", "netProfit": "累计净利润", "maxPrincipalRate": "最大本金收益率",
    "avgRate": "日收益率均值", "maxWithrawalRate": "最大回撤率", "avgRiskDegree": "风险度均值",
    "dealWin": "交易胜率", "profitRate": "盈亏比", "profitDays": "盈利天数", "lossDays": "亏损天数",
}
FRACTIONS = {"avgRate", "maxWithrawalRate", "avgRiskDegree", "dealWin"}


def request(path, params):
    for attempt in range(3):
        try:
            with urlopen(BASE + path + "?" + urlencode(params), timeout=15) as response:
                payload = json.load(response)
            if payload.get("statusCode") != 1:
                raise ValueError(payload.get("statusMessage"))
            return payload.get("dataPoints")
        except (OSError, URLError, ValueError):
            if attempt == 2:
                raise
            sleep(attempt + 1)


def detail(task):
    award, edition = task
    player = award.get(f"player{edition}")
    path = f"spsread{2006 + edition}/curveFront/getBasicVo"
    data = request(path, {"playerId": player, "tradeDate": DATES[edition]}) or {}
    basic = data.get("basicDataFrontVO") or {}
    if not basic:
        return None
    row = {"届数": edition, "特别奖总榜名次": award["sortNo"], "客户昵称": award["playerNickName"],
           "账户昵称": basic["nickName"], "账户标识": player, "交易日期": DATES[edition]}
    for key, label in FIELDS.items():
        value = basic.get(key)
        row[label] = round(value * 100, 8) if value is not None and key in FRACTIONS else value
    row.update({f"第{e}届得分": award.get(f"score{e}") for e in range(11, 20)})
    row["日度净值"] = [[point["tradeDate"][:10], point["netWorth"]]
                     for point in data.get("netWorthVOList") or []]
    return row


def main():
    date = DATES[20]
    params = dict.fromkeys(("tradeDate", "deadlineTime", "beginDate", "endDate"), date)
    params.update(dict.fromkeys(("internalAccount", "playerNickName", "nickName", "breedCode"), ""))
    params.update(groupType=19, rankType=0, size=50, selType=0)
    award = []
    for page in range(1, 14):
        award.extend(request("spsread2026/groupLongScore/getLongScoreListFront",
                             dict(params, index=page))["list"])
    if len(award) != 650 or len({row["id"] for row in award}) != 650:
        raise ValueError("特别奖样本分页不完整")
    tasks = [(row, year) for row in award for year in DATES if row.get(f"player{year}")]
    with ThreadPoolExecutor(max_workers=8) as executor:
        rows = [row for row in executor.map(detail, tasks) if row]
    out = Path(__file__).resolve().parent.parent / "csv结果文件" / "第19与20届官网样本.csv"
    for row in rows:
        row["日度净值"] = json.dumps(row["日度净值"], separators=(",", ":"))
    temporary = out.with_suffix(".new")
    with temporary.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=rows[0])
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(out)
    print({edition: sum(row["届数"] == edition for row in rows) for edition in DATES})


if __name__ == "__main__":
    main()

