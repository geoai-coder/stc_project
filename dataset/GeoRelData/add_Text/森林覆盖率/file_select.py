# 文件名列表
filenames = ['filtered_output_select.txt', 'pos_tostop.txt', 'word.txt', 'word_tostop.txt']
pos_filename = 'pos.txt'

# 读取 pos.txt 文件并处理每一行
with open(pos_filename, 'r', encoding='utf-8') as pos_file:
    pos_lines = pos_file.readlines()
print(len(pos_lines))
# 过滤行并保留包含 'ns' 或 'nz' 的行
valid_indices = [i for i, line in enumerate(pos_lines) if 'ns' in line]
print(len(valid_indices))
# 对每个文件进行处理
for filename in filenames:
    with open(filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # 保留与 valid_indices 相对应的行
    filtered_lines = [lines[i] for i in valid_indices]

    # 写入新文件或覆盖原文件
    with open(filename, 'w', encoding='utf-8') as file:
        file.writelines(filtered_lines)

# 更新 pos.txt 文件
filtered_pos_lines = [pos_lines[i] for i in valid_indices]
with open(pos_filename, 'w', encoding='utf-8') as pos_file:
    pos_file.writelines(filtered_pos_lines)

print("Files have been filtered and updated based on pos.txt.")
