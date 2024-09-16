import random
from ctgucode.tools.LTP_ import *

lines = []
i , j =0, 0
# 逐行读取文件内容
with open('filtered_output_select3.txt', 'r', encoding='utf-8') as file:
    for line in file:
        # ltptext = LTP_(line)
        # word_pos, word_pos_tostopword = ltptext.ltpToStopwords()
        # new_string = ''
        # # 检查 'nt' 是否在 word_pos 中
        # if 'nt' in word_pos[1]:
        #     # 检查 'nt' 是否在 word_pos 中
        #     for word, pos in zip(word_pos[0],word_pos[1]):
        #         if pos == 'nt':
        #             # 将符合条件的字符添加到新的字符串中
        #             new_string += word
        #     # 输出满足条件的行
        #     if any(char.isdigit() for char in new_string):
        #         print("Line: ", line.strip())
        #         i+=1
        #         # 提示用户输入 'yes' 或 'no'
        #         user_input = input("Do you want to process this line? (yes/no): ").strip().lower()
        #
        #         if user_input == 'y':
        #             # 用户选择处理此行，添加你的处理逻辑
        #             lines.append(line)
        #             print("Processing the line...")
        #             # 在此处添加进一步的处理代码
        #
        #         elif user_input == 'n':
        #             # 用户选择跳过此行
        #             print("Skipping the line.")
        #
        #         else:
        #             # 处理无效输入
        #             print("Invalid input, skipping the line.")
        #     else:
        #         j+=1
        #         lines.append(line)
        # else:
        if '概念：据' in line[:6]:
            i+=1
            # 提示用户输入 'yes' 或 'no'
            print(line)
            continue
        lines.append(line)
print(i,j)
# 打乱行的顺序
random.shuffle(lines)

# 将打乱后的内容写入新文件
with open('filtered_output_select.txt', 'w', encoding='utf-8') as file:
    file.writelines(lines)

print("Lines have been shuffled and saved to shuffled_file.txt.")
