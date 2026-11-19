import requests
import pandas as pd
import random
import time
from tqdm import tqdm
from datetime import datetime
import signal
import sys
from fake_useragent import UserAgent
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def get_random_delay():
    return random.uniform(0.5, 2.0)

def get_page_data(page_index, session=None):
    if session is None:
        session = requests.Session()
        retry = Retry(total=3, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
        session.mount('http://', HTTPAdapter(max_retries=retry))
        session.mount('https://', HTTPAdapter(max_retries=retry))
    
    headers = {
        'User-Agent': UserAgent().random,
        'Accept': 'application/json',
        'Referer': 'https://spdspc.qhrb.com.cn/',
        'Origin': 'https://spdspc.qhrb.com.cn'
    }
    
    url = 'https://spdspc.qhrb.com.cn/api/spsread2025/groupLongScore/getLongScoreListFront'
    
    params = {
        'internalAccount': '',
        'playerNickName': '',
        'tradeDate': '2025-04-09',
        'deadlineTime': '2025-04-09',
        'groupType': '19',
        'rankType': '0',
        'index': str(page_index),
        'size': '50',
        'selType': '0',
        'breedCode': '',
        'nickName': '',
        'beginDate': '2025-04-09',
        'endDate': '2025-04-09'
    }
    
    try:
        response = session.get(url, params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and 'dataPoints' in data and 'list' in data['dataPoints']:
                processed_data = []
                player_links = []
                
                for item in data['dataPoints']['list']:
                    processed_item = {
                        '排名': item.get('rank', ''),
                        '客户昵称': item.get('playerNickName', ''),
                        '第3届得分': item.get('score3', 0),
                        '第4届得分': item.get('score4', 0),
                        '第5届得分': item.get('score5', 0),
                        '第6届得分': item.get('score6', 0),
                        '第7届得分': item.get('score7', 0),
                        '第8届得分': item.get('score8', 0),
                        '第9届得分': item.get('score9', 0),
                        '第10届得分': item.get('score10', 0),
                        '第11届得分': item.get('score11', 0),
                        '第12届得分': item.get('score12', 0),
                        '第13届得分': item.get('score13', 0),
                        '第14届得分': item.get('score14', 0),
                        '第15届得分': item.get('score15', 0),
                        '第16届得分': item.get('score16', 0),
                        '第17届得分': item.get('score17', 0),
                        '第18届得分': item.get('score18', 0),
                        '第19届得分': item.get('score19', 0),
                        '总得分': item.get('totalScore', 0),
                        '指定交易商': item.get('brokerName', ''),
                        '操作指导': item.get('operateGuide', ''),
                        '交易日期': item.get('tradeDate', '')
                    }
                    processed_data.append(processed_item)
                    
                    nickname = item.get('playerNickName', '')
                    player_link_info = {'客户昵称': nickname}

                    # 修改player ID处理逻辑
                    for session in range(6, 19):
                        player_key = f'player{session}'
                        player_id = item.get(player_key)
                        
                        if player_id:
                            link = f'http://spds.qhrb.com.cn:8888/ShiPan/S{session}/Index.aspx?id={player_id}'
                            player_link_info[f'第{session}届基本信息链接'] = link
                        else:
                            player_link_info[f'第{session}届基本信息链接'] = '未参加'
                    
                    player_links.append(player_link_info)
                
                return processed_data, player_links
            
        print(f"页面 {page_index} 请求失败: 状态码 {response.status_code}")
        return None, None
                
    except Exception as e:
        print(f"页面 {page_index} 出错: {str(e)}")
        return None, None

def signal_handler(sig, frame):
    print('\n检测到程序中断，正在保存数据...')
    if 'all_data' in globals() and len(all_data) > 0:
        save_data(all_data, is_interrupt=True)
        save_player_links(all_player_links, is_interrupt=True)
    sys.exit(0)

def save_data(data, is_interrupt=False):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'期货大赛数据{"_中断保存" if is_interrupt else ""}_{timestamp}.csv'
    
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    print(f"\n已保存数据文件: {filename} (共{len(df)}条记录)")

def save_player_links(player_links, is_interrupt=False):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'选手链接数据{"_中断保存" if is_interrupt else ""}_{timestamp}.csv'
    
    df = pd.DataFrame(player_links)
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    print(f"已保存链接文件: {filename} (共{len(df)}条记录)")

def collect_all_data():
    global all_data
    global all_player_links
    total_pages = 400  # 修改为400页
    all_data = []
    all_player_links = []
    session = requests.Session()
    
    try:
        for page in tqdm(range(1, total_pages + 1), desc="正在获取数据"):
            retry_count = 0
            while retry_count < 3:  # 最多重试3次
                page_data, player_links = get_page_data(page, session)
                if page_data and player_links:
                    all_data.extend(page_data)
                    all_player_links.extend(player_links)
                    break
                retry_count += 1
                if retry_count < 3:
                    print(f"第{page}页获取失败,等待重试...")
                    time.sleep(get_random_delay() * 2)
            
            # 随机延时
            time.sleep(get_random_delay())
            
            # 每50页保存一次数据
            if page % 50 == 0:
                save_data(all_data, is_interrupt=False)
                save_player_links(all_player_links, is_interrupt=False)
                print(f"\n已完成{page}页数据获取")
        
        if all_data:
            save_data(all_data)
            save_player_links(all_player_links)
            print(f"\n数据采集完成! 共获取{len(all_data)}条记录")
        else:
            print("\n未获取到数据")
            
    except Exception as e:
        print(f"\n发生错误: {str(e)}")
        if all_data:
            save_data(all_data, is_interrupt=True)
            save_player_links(all_player_links, is_interrupt=True)
        raise

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    collect_all_data()