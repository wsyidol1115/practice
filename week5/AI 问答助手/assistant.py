import os                              # os：读取环境变量（也就是 .env 里加载进来的 KEY=VALUE）
import sys                             # sys：用来在配置错误时以非 0 状态码退出程序
import time                            # time：自动重试时用来「等几秒再试」
from dotenv import load_dotenv         # load_dotenv：把 .env 文件内容加载进环境变量
from google import genai               # genai：Google Gemini 官方新版 SDK，提供 Client
from google.genai import errors        # errors：SDK 的结构化异常类（APIError/ClientError/ServerError）
import httpx                           # httpx：SDK 底层用的 HTTP 库，网络层异常都来自这里

MODEL = "gemini-2.5-flash"             # 用常量集中放模型名，想换模型只改这一处（2.5-flash 当前免费层稳定；3.5-flash 常过载503）
MAX_RETRIES = 3                        # 遇到服务端 5xx 故障时，最多自动重试几次
RETRY_WAIT = 3                         # 每次重试之间等待的秒数（给服务端一点喘息时间）


def load_api_key():
    """从 .env 读取 GEMINI_API_KEY。只负责处理“配置错误”，不碰网络。"""
    load_dotenv()                                  # 执行加载：读取当前目录/上级目录的 .env 文件
    api_key = os.getenv("GEMINI_API_KEY")          # 取出密钥（名字必须和 .env 里完全一致）
    if not api_key:                                # 如果没取到，或取到的是空字符串 → 属于配置错误
        print("❌ 配置错误：没找到 GEMINI_API_KEY。")          # 友好提示用户问题出在哪
        print("   请确认同级目录有 .env 文件，且里面写了 GEMINI_API_KEY=你的key")  # 给出具体修复办法
        sys.exit(1)                                # 配置没法继续，直接退出（非 0 表示异常退出）
    return api_key                                 # 一切正常，把密钥返回给调用方


def create_client(api_key):
    """用密钥创建 Gemini 客户端。创建是惰性的、不发网络请求，所以这里只可能是配置错误。"""
    try:                                           # 包一层防御：万一 key 格式非法导致初始化失败
        client = genai.Client(api_key=api_key)     # 创建客户端对象，之后所有提问都通过它发出
        return client                              # 创建成功，返回客户端
    except Exception as e:                         # 这里捕获到的只会是配置/初始化类问题（非网络）
        print(f"❌ 配置错误：创建 Gemini 客户端失败 —— {e}")   # 把具体原因打给用户看
        sys.exit(1)                                # 客户端都建不出来，没法继续，退出


def print_help():
    """启动时打印一次用法提示，告诉用户怎么用。"""
    print("=" * 40)                                # 一条分隔线，让提示更醒目
    print("🤖 Gemini 命令行问答助手")                  # 标题
    print("=" * 40)                                # 再来一条分隔线
    print("· 直接输入你的问题，回车即可提问")           # 说明基本用法
    print("· 输入 quit 退出程序")                      # 说明退出方式
    print("· 空输入会被忽略，请输入有内容的问题")        # 说明空输入的处理
    print("=" * 40)                                # 收尾分隔线


def ask_gemini(client, question):
    """把一个问题发给 Gemini，返回回答文本。所有网络/API 异常都在这里被捕获，单次失败不会让程序崩。"""
    for attempt in range(1, MAX_RETRIES + 1):                  # 循环最多 MAX_RETRIES 次，用于服务端故障时自动重试
        try:                                                   # 正常路径：尝试发请求并拿回答
            response = client.models.generate_content(         # 调用模型生成内容
                model=MODEL,                                   # 用上面定义的模型常量
                contents=question,                             # 把用户的问题作为输入
            )
            return response.text                               # 回答正文在 response.text 里，返回它（成功就直接结束）
        except errors.ServerError as e:                        # 5xx 服务端类错误：Gemini 那边过载/故障，值得重试
            if attempt < MAX_RETRIES:                          # 还没到最后一次 → 提示一下并重试
                print(f"   （服务端故障 {e.code}，{RETRY_WAIT} 秒后自动重试 {attempt}/{MAX_RETRIES - 1}…）")
                time.sleep(RETRY_WAIT)                          # 等待几秒，给服务端喘息时间
                continue                                       # 回到循环开头，再试一次
            return f"⚠️ Gemini 服务端持续故障（错误码 {e.code}），重试 {MAX_RETRIES} 次仍失败，请稍后再来。"
        except errors.ClientError as e:                        # 4xx 客户端类错误（按数值码区分，不靠字符串匹配）→ 重试没用，直接返回
            if e.code == 429:                                  # 429 = 触发限流 / 额度用尽
                return "⚠️ 额度用完或触发限流了，请稍后再试，或更换 API key。"
            elif e.code in (401, 403):                          # 401/403 = 鉴权失败（key 错或没权限）→ 本质是配置问题
                return "⚠️ API key 无效或没有权限，请检查 .env 里的 GEMINI_API_KEY。"
            else:                                              # 其它 4xx（如 400 参数错误）
                return f"⚠️ 请求被拒绝（错误码 {e.code}）：{e.message}"
        except httpx.HTTPError:                                # 网络层异常：连不上 / 超时 / DNS 失败等 → 直接返回
            return "⚠️ 网络好像有问题（连接超时或断网），请检查网络后重试。"
        except errors.APIError as e:                           # 兜底其它没被上面分支接住的 API 错误
            return f"⚠️ 调用 Gemini 出错（错误码 {e.code}）：{e.message}"
        except Exception as e:                                 # 最终兜底：任何意料之外的异常都接住，绝不让程序崩
            return f"⚠️ 发生未知错误：{type(e).__name__} —— {e}"


def main():
    """程序入口：取 key → 建客户端 → 打印帮助 → 进入问答主循环。"""
    api_key = load_api_key()                       # 第一步：拿到密钥（失败会在函数内退出）
    client = create_client(api_key)                # 第二步：创建客户端（失败会在函数内退出）
    print_help()                                   # 第三步：打印用法提示

    while True:                                     # 第四步：进入无限循环，反复接收用户问题
        question = input("\n你问：").strip()         # 读取一行输入，并去掉首尾空白（方便判空和判 quit）
        if question.lower() == "quit":              # 不区分大小写地判断是否要退出
            print("👋 再见！")                        # 跟用户道别
            break                                   # 跳出循环，程序结束
        if not question:                            # strip() 之后如果是空字符串 → 属于空输入
            print("（空输入）请输入有内容的问题，或输入 quit 退出。")  # 提示后……
            continue                                # ……跳过本次循环，重新等待输入
        answer = ask_gemini(client, question)       # 正常问题：发给 Gemini 拿回答（内部已处理各种异常）
        print(f"\nGemini：{answer}")                 # 打印回答


if __name__ == "__main__":                          # 只有“直接运行本文件”时才执行 main()
    main()                                          # 启动程序（被 import 时不会自动运行）
