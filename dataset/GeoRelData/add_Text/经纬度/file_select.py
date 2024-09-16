import re
def test01():
    # 定义匹配是否包含数字的正则表达式
    number_pattern = re.compile(r'\d')
    lines = []
    i = 0
    # 读取文件并进行处理
    with open('filtered_output_select3.txt', 'r', encoding='utf-8') as file:
        for line in file:
            if len(line) > 2000:
                print(len(line),line)
                i+=1
                continue
            lines.append(line)
        print(i)
    # # 过滤不符合条件的行
    # filtered_lines = [
    #     line for line in lines
    #     if '《' not in line
    #        and number_pattern.search(line)
    #        and "地震" not in line
    #        and '】' not in line
    #        and '《' not in line
    #        and '【' not in line
    #        and ('°' in line or '度' in line)
    # ]

    # 将符合条件的行写入新文件
    with open('filtered_output_select.txt', 'w', encoding='utf-8') as file:
        file.writelines(lines)

    print("Filtered lines have been saved to filtered_file.txt.")

def test02():
    import re
    def has_digit_around_keywords(line, keyword, window=5):
        """检查关键字前后指定范围内是否有数字"""
        # 找到关键词的位置
        keyword_pos = line.find(keyword)
        if keyword_pos == -1:
            return False

        # 获取关键词前后指定范围的子字符串
        start_pos = max(0, keyword_pos - window)
        end_pos = min(len(line), keyword_pos + len(keyword) + window)
        substring = line[start_pos:end_pos]

        # 检查子字符串是否包含数字
        return bool(re.search(r'\d', substring))

    def process_file(file_path):
        linelist = []
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                # 检查是否存在满足条件的行
                if has_digit_around_keywords(line, "经") or has_digit_around_keywords(line, "纬"):
                    print(line.strip())  # 输出符合条件的行
                    linelist.append(line)
        return linelist
    # 示例使用
    open('filtered_output_select.txt','w',encoding='utf-8').writelines(process_file('filtered_output_select3.txt'))
test01()