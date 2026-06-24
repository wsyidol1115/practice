import os                              # os：用来读取“环境变量”（也就是 .env 里写的东西）
from dotenv import load_dotenv         # load_dotenv：把 .env 文件里的内容加载进来
from google import genai               # genai：Google Gemini 的官方最新 SDK

load_dotenv()                          # 执行加载：读 .env，把里面的 KEY=VALUE 放进环境变量

api_key = os.getenv("GEMINI_API_KEY")  # 从环境变量里取出我们的密钥（名字要和 .env 里完全一致）

if not api_key:                        # 如果没取到（比如 .env 写错了），就提醒并停止
    raise SystemExit("❌ 没找到 GEMINI_API_KEY，请检查 .env 文件")

client = genai.Client(api_key=api_key) # 用密钥创建一个“客户端”，之后通过它和 Gemini 对话

response = client.models.generate_content(   # 发起一次请求：让模型生成内容
    model="gemini-3.5-flash",                # 选用的模型（flash = 快又省，免费额度友好）
    contents="用一句话解释什么是 Forward Deployed Engineer",  # 我们要问的话
)

print(response.text)                   # 模型的回复放在 response.text 里，打印出来
