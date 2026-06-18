with open("note.txt", "w") as f:
    f.write("first line\n")
    f.write("second line\n")
    f.write("last line\n")



with open("note.txt", "a") as f:
    f.write("第一行\n")
    f.write("第二行\n")
    f.write("第三行\n")

with open("note.txt","r") as f:
    content = f.read()
    print(content)

with open("notes.txt", "w") as f:
    f.write("apple\n")
    f.write("banana\n")

with open("notes.txt", "r") as f:
    content=f.read()
    print(content)