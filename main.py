from fastapi import FastAPI
import yfinance as yf
from openai import OpenAI
import os

app = FastAPI()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

@app.get("/analyze/{stock_code}")
def analyze_stock(stock_code: str):
    try:
        # 自动判断是上交所(.SS)还是深交所(.SZ)
        if stock_code.startswith('6'):
            ticker_symbol = f"{stock_code}.SS"
        else:
            ticker_symbol = f"{stock_code}.SZ"
            
        # 1. 使用 yfinance 获取 A股 实时数据
        stock = yf.Ticker(ticker_symbol)
        info = stock.info
        
        # 容错处理：获取不到价格时
        current_price = info.get('currentPrice', info.get('regularMarketPrice'))
        if not current_price:
            return {"error": f"未能获取到 {stock_code} 的交易数据，请确认代码是否正确（如: 600519 或 000001）。"}
            
        name = info.get('shortName', stock_code)
        
        # 2. 组装给 AI 的提示词
        prompt = f"你是一位资深的A股量化分析师。请分析公司 {name} (代码:{stock_code})。当前最新价是 {current_price} 元。请结合目前的宏观经济环境和该公司的行业地位，给出简短的投资基本面分析和风险提示。"
        
        # 3. 让 DeepSeek 输出分析结果
        response = client.chat.completions.create(
            model="deepseek-chat", 
            messages=[{"role": "user", "content": prompt}]
        )
        
        return {
            "stock_name": name,
            "current_price": str(current_price),
            "ai_analysis": response.choices[0].message.content
        }
    except Exception as e:
        return {"error": str(e)}
