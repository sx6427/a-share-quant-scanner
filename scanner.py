import akshare as ak
import pandas as pd
import time
from tqdm import tqdm

def get_all_stocks():
    """获取全市场A股代码（5300+只）"""
    print("Fetching stock list...")
    df = ak.stock_info_a_code_name()
    # 过滤ST和退市股，提高分析质量
    df = df[~df['名称'].str.contains('ST|退')]
    return df['code'].tolist()

def scan_market(limit=50):
    """
    扫描市场异动
    参数 limit 用于控制测试规模，正式跑设为 None
    """
    all_codes = get_all_stocks()
    if limit:
        all_codes = all_codes[:limit] # 测试时用，全扫请注释这行
        
    anomaly_list = []
    
    for code in tqdm(all_codes, desc="Scanning Market"):
        try:
            # 获取实时行情
            spot_df = ak.stock_zh_a_spot_em()
            stock = spot_df[spot_df['代码'] == code]
            
            if stock.empty:
                continue
                
            change = stock['涨跌幅'].values[0]
            vol_ratio = stock['量比'].values[0]
            amount = stock['成交额'].values[0]
            
            # 策略逻辑：放量上涨（可根据你的喜好改）
            if change > 3 and vol_ratio > 1.5 and amount > 100000000: # 成交额>1亿
                anomaly_list.append({
                    "code": code,
                    "name": stock['名称'].values[0],
                    "change": change,
                    "volume_ratio": vol_ratio,
                    "amount": amount
                })
            time.sleep(0.05) # 防止请求过快被封
        except Exception as e:
            continue
            
    df = pd.DataFrame(anomaly_list)
    df.to_csv("anomaly_stocks.csv", index=False, encoding="utf-8-sig")
    print(f"Found {len(df)} anomaly stocks. Saved to anomaly_stocks.csv")
    return df

if __name__ == "__main__":
    # 注意：测试时跑50只，申请时把 limit=50 删掉跑全量
    scan_market(limit=50) 

