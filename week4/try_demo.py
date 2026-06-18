try:
    age = int(input("请输入年龄:"))   # 如果用户输入"abc",这里会出错
    print("明年你", age + 1, "岁")
except ValueError:
    print("请输入数字,不是文字哦")     # 出错就走这里,而不是崩溃