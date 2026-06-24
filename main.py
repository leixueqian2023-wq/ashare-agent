from fastapi import FastAPI
import akshare as ak
from openai import OpenAI
import os

app = FastAPI()

# 核心修改点 1：将大脑指向 DeepSeek 的服务器，并读取 DEEPSEEK_API_KEY
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

@app.get("/analyze/{stock_code}")
def analyze_stock(stock_code: str):
    try:
        # 获取 A股 实时数据
        df = ak.stock_zh_a_spot_em()
        stock_data = df[df['代码'] == stock_code]
        
        if stock_data.empty:
            return {"error": "未找到该股票代码，请检查（如：600519）"}
            
        price = stock_data['最新价'].values[0]
        name = stock_data['名称'].values[0]
        
        # 组装给 AI 的提示词
        prompt = f"你是一位资深的A股量化分析师。请分析 {name} (代码:{stock_code})。当前最新价是 {price} 元。请结合目前的宏观经济环境和该公司的行业地位，给出简短的投资基本面分析和风险提示。"
        
        # 核心修改点 2：指定使用 deepseek-chat 模型
        response = client.chat.completions.create(
            model="deepseek-chat", 
            messages=[{"role": "user", "content": prompt}]
        )
        
        return {
            "stock_name": name,
            "current_price": str(price),
            "ai_analysis": response.choices[0].message.content
        }
    except Exception as e:
        return {"error": str(e)}
