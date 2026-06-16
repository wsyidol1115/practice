from pathlib import Path  # 从 pathlib 模块导入 Path，用来更方便地表示和操作文件路径。

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tif", ".tiff"}  # 定义一组常见图片后缀名，用来判断哪些文件是图片。

current_folder = Path(__file__).parent  # 获取这个脚本所在的文件夹，也就是当前项目文件夹。
images_folder = current_folder / "images"  # 拼出 images 子文件夹的路径。

if not images_folder.exists():  # 判断 images 文件夹是否不存在。
    raise FileNotFoundError("找不到 images 文件夹，请先在当前文件夹下创建 images 文件夹。")  # 如果找不到 images 文件夹，就报错并告诉你原因。

image_files = sorted(  # 把找到的图片文件按文件名排序，保证重命名顺序稳定。
    [file_path for file_path in images_folder.iterdir() if file_path.is_file() and file_path.suffix.lower() in IMAGE_EXTENSIONS],  # 遍历 images 文件夹，只保留文件，并且只保留后缀名属于图片类型的文件。
    key=lambda file_path: file_path.name.lower(),  # 排序时忽略文件名大小写，比如 A.jpg 和 a.jpg 会按同一种规则排序。
)  # sorted 调用结束，image_files 里就是按顺序排好的图片文件列表。

temporary_files = []  # 创建一个空列表，用来保存临时改名后的文件路径。

for index, file_path in enumerate(image_files, start=1):  # 依次处理每一张图片，index 从 1 开始计数。
    temporary_path = images_folder / f"__renaming_codex_temp_{index}{file_path.suffix}"  # 给当前图片生成一个临时文件名，并保留原来的后缀名。
    file_path.rename(temporary_path)  # 先把原文件改成临时文件名，避免直接改成 photo_1 时和已有文件名冲突。
    temporary_files.append(temporary_path)  # 把临时文件路径保存起来，下一步再统一改成最终名字。

for index, temporary_path in enumerate(temporary_files, start=1):  # 再次依次处理所有临时文件，index 仍然从 1 开始。
    final_path = images_folder / f"photo_{index}{temporary_path.suffix}"  # 生成最终文件名，比如 photo_1.jpg，并保留原来的后缀名。
    temporary_path.rename(final_path)  # 把临时文件名改成最终文件名。

print(f"完成：已重命名 {len(temporary_files)} 张图片。")  # 在终端输出完成提示，并显示一共改了多少张图片。
