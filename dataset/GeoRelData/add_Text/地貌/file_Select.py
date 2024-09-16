def test01():
    with open('filtered_output_select2.txt', 'r', encoding='utf-8') as infile, open('filtered_output_select.txt', 'w', encoding='utf-8') as outfile:
        # 逐行读取源文件
        i = 0
        for line in infile:
            # 检查行中是否包含“山”字
            if '该区' in line[:5]:
                # 将包含“山”的行写入新文件
                i+=1
                continue
            outfile.write(line)
        print(i)

    print("处理完成，已写入 new_file.txt。")

def test02():
    import random

    # 读取文件中的所有行
    with open('filtered_output_select2.txt', 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # 打乱行的顺序
    random.shuffle(lines)

    # 将打乱后的内容写入新文件
    with open('filtered_output_select.txt', 'w', encoding='utf-8') as file:
        file.writelines(lines)

    print("Lines have been shuffled and saved to shuffled_file.txt.")
test02()
