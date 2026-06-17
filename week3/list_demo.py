# 创建一个列表（list），里面放了 3 种水果，用方括号 [] 包起来
fruits = ["苹果", "香蕉", "橘子"]

# 打印整个列表，看看里面有什么
print("我的水果列表：", fruits)

# 通过“下标”取出第 1 个元素（注意：Python 从 0 开始数，所以 0 就是第一个）
print("第一个水果是：", fruits[0])

# 取出最后一个元素，-1 表示倒数第一个
print("最后一个水果是：", fruits[2])

# 用 append() 往列表末尾添加一个新元素
fruits.append("西瓜")
print("最后一个水果是：", fruits[1])
print("加了西瓜之后：", fruits)

# 用 len() 计算列表里一共有几个元素
print("现在一共有几种水果：", len(fruits))

# 用 for 循环把列表里的每个元素挨个取出来打印
for fruit in fruits:
    print("我有：", fruit)
