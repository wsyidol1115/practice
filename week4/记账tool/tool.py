import json   # json 工具：帮我们把“列表+字典”数据存进文件、再读出来

# 数据存在哪个文件里（和本程序放同一个文件夹）
FILE_NAME = "expenses.json"


def load_expenses():
    """① 读数据：开机时从文件里把以前记的支出读出来"""
    try:
        # 试着打开文件来读（"r" = read 读取，encoding 保证中文不乱码）
        with open(FILE_NAME, "r", encoding="utf-8") as f:
            return json.load(f)        # 把文件内容变回 Python 列表
    except FileNotFoundError:
        # 如果文件还不存在（第一次用），就返回一个空列表
        return []


def save_expenses(expenses):
    """② 存数据：每次改动后把支出列表写回文件，下次还能看到"""
    with open(FILE_NAME, "w", encoding="utf-8") as f:   # "w" = write 写入（覆盖）
        # ensure_ascii=False 让中文正常显示，indent=2 让文件排版好看
        json.dump(expenses, f, ensure_ascii=False, indent=2)


def add_expense(expenses):
    """功能1：添加一笔支出（金额 + 类别）"""
    try:
        amount = float(input("请输入支出金额："))   # float 支持小数，比如 9.9
    except ValueError:
        print("⚠️ 金额必须是数字哦，这笔没记上\n")
        return                                       # 输入错就直接退出这个功能
    # float() 只保证“是个数”，挡不住 0、负数、或 1e62 这种荒谬大数 —— 这里补一道业务校验
    if amount <= 0 or amount > 1_000_000:
        print("⚠️ 金额要在 0~100万 之间，这笔没记上\n")
        return
    category = input("请输入支出类别（如 餐饮/交通）：")
    # 把这一笔做成一个字典，再装进列表
    expenses.append({"金额": amount, "类别": category})
    save_expenses(expenses)                          # 记完马上存盘
    print("✅ 添加成功！\n")


def show_expenses(expenses):
    """功能2：查看所有支出"""
    if len(expenses) == 0:                           # 列表是空的
        print("📭 还没有任何支出记录\n")
        return
    print("---------- 全部支出 ----------")
    # enumerate 让我们一边遍历、一边拿到编号 i（从 1 开始数）
    for i, e in enumerate(expenses, start=1):
        print(f"{i}. {e['类别']}：{e['金额']} 元")
    print("-----------------------------\n")


def show_total(expenses):
    """功能3：查看支出总金额"""
    total = 0
    for e in expenses:            # 把每一笔的金额加起来
        total = total + e["金额"]
    print(f"💰 支出总金额：{total} 元\n")


def main():
    """主程序：显示菜单，根据用户选择调用对应功能"""
    expenses = load_expenses()    # 开机先读出以前的数据

    while True:                   # 一直循环，直到用户选择退出
        print("===== 记账小工具 =====")
        print("1. 添加支出")
        print("2. 查看所有支出")
        print("3. 查看支出总金额")
        print("4. 退出")
        choice = input("请输入功能编号：")

        if choice == "1":
            add_expense(expenses)
        elif choice == "2":
            show_expenses(expenses)
        elif choice == "3":
            show_total(expenses)
        elif choice == "4":
            print("👋 再见！")
            break                 # 跳出 while 循环，程序结束
        else:
            print("⚠️ 没有这个编号，请输入 1~4\n")


# 程序从这里开始运行
main()
