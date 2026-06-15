# 从 Python 自带的 os 模块里借用一些和"文件、文件夹"打交道的工具
import os

# __file__ 是 rename.py 这个脚本自己的路径；os.path.abspath 把它变成完整路径
# os.path.dirname 再取出"脚本所在的文件夹"，这样不管你从哪里运行都能定位准
here = os.path.dirname(os.path.abspath(__file__))

# 把"脚本所在文件夹"和"images"拼起来，得到 images 文件夹的完整、可靠路径
folder = os.path.join(here, "images")

# 把 folder 文件夹里所有文件的名字列出来，存进一个叫 names 的列表里
names = os.listdir(folder)

# 只保留图片文件：用 lower() 把名字转成小写后，看结尾是不是常见图片后缀
# endswith 后面是一个"后缀元组"，名字以其中任意一个结尾就算图片
names = [n for n in names if n.lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"))]

# 按名字排序，保证每次重命名的先后顺序是固定的、可预测的
names.sort()

# 准备一个计数器，从 1 开始，用来生成 photo_1、photo_2……
i = 1

# 依次取出列表里的每一个图片文件名，放进变量 name 里循环处理
for name in names:
    # os.path.splitext 会把文件名拆成"主体"和"后缀"两部分，比如 ("side", ".png")
    # 我们只要第二个（后缀），所以用 [1] 取出来
    ext = os.path.splitext(name)[1]

    # 拼出旧文件的完整路径，比如 images/side.png
    old_path = os.path.join(folder, name)

    # 拼出新文件的完整路径，比如 images/photo_1.png（后缀沿用原来的 ext）
    new_path = os.path.join(folder, "photo_" + str(i) + ext)

    # 真正执行改名：把 old_path 改成 new_path
    os.rename(old_path, new_path)

    # 在屏幕上打印一行，告诉你哪个文件被改成了什么，方便核对
    print(name, "->", "photo_" + str(i) + ext)

    # 计数器加 1，下一张图片就会变成 photo_2、photo_3……
    i = i + 1

# 全部处理完后，打印一句提示
print("完成！一共重命名了", i - 1, "个文件")
