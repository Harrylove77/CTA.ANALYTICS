from DrissionPage import ChromiumPage
import pandas as pd
import time
import random
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue
import threading
from tqdm import tqdm

# 全局配置
MAX_WORKERS = 5  # 最大线程数
MAX_RETRY = 2    # 最大重试次数
REQUEST_DELAY = (0.5, 1.0)  # 随机延迟范围
SAVE_BATCH_SIZE = 100  # 每处理多少条数据保存一次

def get_random_delay():
    return random.uniform(*REQUEST_DELAY)

def extract_table_data(table_element, session_num):
    """提取表格数据"""
    try:
        data = {}
        numeric_fields = {
            '期初权益', '期末权益', '累计入金', '累计出金', '累计净值', 
            '累计净利润', '日收益率均值', '日收益率最大', '日收益率最小', 
            '年化收益率', '交易胜率', '盈亏比', '风险度均值', '最大回撤率',
            '日均可用资金', '参考收益率', '最大本金收益率', '预计年化收益率',
            '盈利占比', '夏普比率', '最大绝对回撤', '收益风险比', '净值标准差',
            '期初市值权益', '期末市值权益', '综合排名', '总交易天数', 
            '盈利天数', '亏损天数', '手续费/净利润', '最高单日亏损'
        }

        field_mapping = {
            '组账户数': '组账户数',
            '账户昵称': '账户昵称',
            '参赛日期': '参赛日期',
            '指定交易商': '指定交易商',
            '期初权益': '期初权益',
            '期末权益': '期末权益',
            '累计入金': '累计入金',
            '累计出金': '累计出金',
            '综合排名': '综合排名',
            '累计净值': '累计净值',
            '最大回撤率': '最大回撤率',
            '累计净利润': '累计净利润',
            '日收益率均值': '日收益率均值',
            '历史最大本金': '最大本金',
            '最大本金收益率': '最大本金收益率',
            '日收益率最大': '日收益率最大',
            '日收益率最小': '日收益率最小',
            '预计年化收益率': '预计年化收益率',
            '总交易天数': '总交易天数',
            '盈利天数': '盈利天数',
            '亏损天数': '亏损天数',
            '交易胜率': '交易胜率',
            '盈利占比': '盈利占比',
            '手续费/净利润': '手续费/净利润',
            '风险度均值': '风险度均值',
            '夏普比率': '夏普比率',
            '最大绝对回撤': '最大绝对回撤',
            '最高单日亏损': '最高单日亏损',
            '收益风险比': '收益风险比',
            '净值标准差': '净值标准差'
        }

        if session_num in [17, 18]:
            labels = table_element.eles('css:.el-descriptions-item__label')
            contents = table_element.eles('css:.el-descriptions-item__content')
            
            for label, content in zip(labels, contents):
                key = label.text.strip()
                value = content.text.strip()
                if key and value:
                    mapped_key = field_mapping.get(key, key)
                    if mapped_key in numeric_fields:
                        value = value.replace(',', '').replace('%', '')
                        try:
                            value = float(value)
                        except:
                            pass
                    data[mapped_key] = value
        else:
            rows = table_element.eles('tag:tr')
            for row in rows:
                cells = row.eles('tag:td')
                if len(cells) >= 2:
                    key1 = cells[0].text.strip()
                    value1 = cells[1].text.strip()
                    if key1 and value1:
                        if key1 in numeric_fields:
                            value1 = value1.replace(',', '').replace('%', '')
                            try:
                                value1 = float(value1)
                            except:
                                pass
                        data[key1] = value1
                    
                    if len(cells) >= 4:
                        key2 = cells[2].text.strip()
                        value2 = cells[3].text.strip()
                        if key2 and value2:
                            if key2 in numeric_fields:
                                value2 = value2.replace(',', '').replace('%', '')
                                try:
                                    value2 = float(value2)
                                except:
                                    pass
                            data[key2] = value2

        required_fields = {'组别', '账户昵称', '参赛日期', '指定交易商'}
        if any(field in data for field in required_fields):
            return pd.DataFrame([data])
        return None
        
    except Exception as e:
        print(f"\n提取表格数据失败: {str(e)}")
        return None

def get_table_data(page, url, session_num):
    try:
        print(f"\n正在获取第{session_num}届数据...")
        page.get(url)
        
        if session_num in [17, 18]:
            time.sleep(3)  # 等待Vue渲染完成
            table = page.ele('css:.el-descriptions__table')
            if table:
                print(f"使用Vue表格选择器获取第{session_num}届表格")
                return extract_table_data(table, session_num)
        else:
            time.sleep(get_random_delay())
            xpath_map = {
                14: '//*[@id="container0"]/div/div/table/tbody[2]',
                15: '//*[@id="container0"]/div/div/table/tbody[2]',
                16: '//*[@id="container0"]/div/div/table/tbody[2]'
            }
            
            if session_num in xpath_map:
                table = page.ele(f'xpath:{xpath_map[session_num]}')
                if table:
                    print(f"使用固定XPath获取第{session_num}届表格")
                    return extract_table_data(table, session_num)
        
        tables = page.eles('css:table')
        
        if not tables:
            print("未找到任何表格")
            return None
            
        if len(tables) == 1:
            print("找到单个表格，直接处理")
            return extract_table_data(tables[0], session_num)
            
        print(f"找到{len(tables)}个表格，使用第一个有效表格")
        for table in tables:
            data_df = extract_table_data(table, session_num)
            if data_df is not None and not data_df.empty:
                if len(data_df.columns) >= 3:
                    print(f"成功提取表格数据，包含{len(data_df.columns)}个字段")
                    return data_df
        
        print("未找到有效表格")
        return None
            
    except Exception as e:
        print(f"\n获取数据失败: {str(e)}")
        return None

def process_player(player_data, result_queue, failed_queue, progress_bar):
    """处理单个选手数据的线程函数"""
    nickname = player_data['客户昵称']
    print(f"\n处理选手: {nickname}")
    
    page = ChromiumPage()
    page.set.window.size(1366, 768)
    page.set.timeouts(15, 15, 15)
    
    try:
        all_session_data = []
        failed_sessions = []
        
        for session in range(6, 19):
            link_col = f'第{session}届基本信息链接'
            if link_col in player_data and player_data[link_col] != '未参加':
                retry_count = 0
                while retry_count < MAX_RETRY:
                    table_data = get_table_data(page, player_data[link_col], session)
                    if table_data is not None:
                        table_data['届数'] = session
                        table_data['客户昵称'] = nickname
                        all_session_data.append(table_data)
                        print(f"第{session}届数据获取成功")
                        break
                    retry_count += 1
                    if retry_count < MAX_RETRY:
                        print(f"第{session}届获取失败，重试...")
                        time.sleep(get_random_delay() * 2)
                
                if retry_count == MAX_RETRY:
                    failed_sessions.append(session)
                
                time.sleep(get_random_delay())
        
        if all_session_data:
            player_df = pd.concat(all_session_data, ignore_index=True)
            result_queue.put(player_df)
        
        if failed_sessions:
            failed_queue.put({
                '客户昵称': nickname,
                '失败届数': ','.join(map(str, failed_sessions))
            })
            
    except Exception as e:
        print(f"\n处理选手 {nickname} 时发生错误: {str(e)}")
        failed_queue.put({
            '客户昵称': nickname,
            '失败原因': str(e)
        })
    
    finally:
        page.quit()
        progress_bar.update(1)  # 更新进度条

def save_results(result_queue, failed_queue, save_dir, total_players):
    """保存结果的线程函数"""
    all_players_data = []
    failed_records = []
    processed_count = 0
    
    with tqdm(total=total_players, desc="保存进度", position=1, leave=False) as save_pbar:
        while processed_count < total_players:
            # 处理成功结果
            while not result_queue.empty():
                player_df = result_queue.get()
                all_players_data.append(player_df)
                processed_count += 1
                save_pbar.update(1)
                
                # 定期保存
                if len(all_players_data) % SAVE_BATCH_SIZE == 0:
                    interim_df = pd.concat(all_players_data, ignore_index=True)
                    interim_filename = os.path.join(save_dir, f'汇总数据_前{processed_count}名选手_{time.strftime("%Y%m%d_%H%M%S")}.csv')
                    interim_df.to_csv(interim_filename, index=False, encoding='utf-8-sig')
                    print(f"\n已保存中间汇总数据到: {interim_filename}")
            
            # 处理失败记录
            while not failed_queue.empty():
                failed_record = failed_queue.get()
                failed_records.append(failed_record)
                processed_count += 1
                save_pbar.update(1)
            
            time.sleep(0.5)  # 避免CPU占用过高
        
        # 保存最终结果
        if all_players_data:
            final_df = pd.concat(all_players_data, ignore_index=True)
            final_filename = os.path.join(save_dir, f'全部选手汇总数据_{time.strftime("%Y%m%d_%H%M%S")}.csv')
            final_df.to_csv(final_filename, index=False, encoding='utf-8-sig')
            print(f"\n已保存所有数据到: {final_filename}")
        
        if failed_records:
            failed_df = pd.DataFrame(failed_records)
            failed_filename = os.path.join(save_dir, f'失败记录_{time.strftime("%Y%m%d_%H%M%S")}.csv')
            failed_df.to_csv(failed_filename, index=False, encoding='utf-8-sig')
            print(f"已保存失败记录到: {failed_filename}")

def test_fetch():
    try:
        # 读取CSV文件并限制处理前3000条数据
        df = pd.read_csv(r"C:\Users\Administrator\Desktop\大数据综合实践\选手链接数据_20250410_161845_fixed.csv")
        df = df.head(3000)  # 只处理前3000条数据
        
        # 创建保存结果的目录
        save_dir = "results"
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
            
        # 创建线程安全的队列
        result_queue = Queue()
        failed_queue = Queue()
        
        # 启动保存结果的线程
        save_thread = threading.Thread(
            target=save_results,
            args=(result_queue, failed_queue, save_dir, len(df)),
            daemon=True
        )
        save_thread.start()
        
        # 使用线程池处理选手数据
        with tqdm(total=len(df), desc="处理进度", position=0) as pbar:
            with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                futures = []
                for _, row in df.iterrows():
                    futures.append(executor.submit(
                        process_player, 
                        row.to_dict(), 
                        result_queue, 
                        failed_queue,
                        pbar
                    ))
                
                # 等待所有任务完成
                for future in as_completed(futures):
                    future.result()  # 捕获可能的异常
        
        # 等待保存线程完成
        save_thread.join()
        
    except Exception as e:
        print(f"\n程序执行过程中发生错误: {str(e)}")

if __name__ == "__main__":
    test_fetch()