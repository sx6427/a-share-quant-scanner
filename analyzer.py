import os
import pandas as pd
from openai import OpenAI

# 配置 MiMo
client = OpenAI(
    api_key=os.getenv("MIMO_API_KEY", "YOUR_MIMO_API_KEY"), # 记得填你的Key
    base_url="https://api.xiaomimimo.com/v1"
)

def analyze_stock(row):
    """调用 MiMo 分析单只股票"""
    prompt = f"""
你是一个冷静的A股操盘手。请分析以下股票数据：

股票名称：{row['name']} ({row['code']})
今日涨幅：{row['change']}%
量比：{row['volume_ratio']}
成交额：{row['amount']/100000000:.2f} 亿

请直接给出结论：
1. 异动性质：是主力拉升、散户跟风、还是诱多出货？（3选1）
2. 明日预判：高开/平开/低开？是否具备连板潜力？
3. 风险提示：最大的雷点是什么？
"""
    try:
        resp = client.chat.completions.create(
            model="mimo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=500
        )
        return resp.choices[0].message.content
    except Exception as e:
        return f"Analysis failed: {e}"

def main():
    try:
        df = pd.read_csv("anomaly_stocks.csv")
    except FileNotFoundError:
        print("Error: anomaly_stocks.csv not found. Run scanner.py first.")
        return

    print(f"Starting deep analysis for {len(df)} stocks...")
    
    results = []
    for _, row in df.iterrows():
        print(f"Analyzing {row['name']}...")
        result = analyze_stock(row)
        results.append(result)
        print(result)
        print("-" * 20)
        
        # 保存中间结果，防止断掉
        with open("analysis_report.txt", "a", encoding="utf-8") as f:
            f.write(f"### {row['name']} ({row['code']})\n")
            f.write(result + "\n\n")

if __name__ == "__main__":
    main()

