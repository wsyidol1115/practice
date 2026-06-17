print("hello, Python")
name="王诗逸"
age=30
height=1.67
is_staff=True
print(name,age,)
fruits = ["苹果", "香蕉", "橙子"]
print(fruits[0])     # 取第 1 个 —— 注意从 0 开始数!
print(len(fruits))   # 看列表里有几个
fruits.append("葡萄")  # 末尾加一个
print(fruits)
student = {
    "name": "小明",
    "age": 25,
    "city": "北京"
}
print(student["name"])   # 用"名字"取对应的值
student["age"] = 26      # 改值
student["grade"] = "A"   # 加一对新的
print(student)
student["phone"] = "13800138000"
print(student["phone"])

score=70
if score>=60:
    print("及格")
else:
    print("不及格")

fruits = ["苹果", "香蕉", "橙子"]

for fruit in fruits:        # 把列表里每个东西,轮流叫 fruit
    print("我喜欢吃", fruit)


sts=["张三","李四","王五","赵六"]
sts[0]={"name":"张三","age":20,"city":"北京","score":90}
sts[1]={"name":"李四","age":21,"city":"上海","score":30}
sts[2]={"name":"王五","age":22,"city":"广州","score":30}
sts[3]={"name":"赵六","age":23,"city":"深圳","score":20}
j=0
for st in sts:
    score=st["score"]
    if score>=90:   # 优秀
        print(st["name"],"优秀")
    elif score>=60:   # 及格
        print(st["name"],"及格")
    else:   # 不及格
        print(st["name"],"不及格")
        j=j+1
print("不合格人数是:",j,"人")