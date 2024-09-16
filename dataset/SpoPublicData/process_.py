#文本错误，处理英文文本无空格的情况
import os
import json
import re

def is_non_chinese_text_without_spaces(text):
    # 仅保留非中文字符
    non_chinese_text = re.sub(r'[\u4e00-\u9fff]', '', text)
    # 检查非中文文本中是否没有空格
    return non_chinese_text and ' ' not in non_chinese_text

def process_file(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'a', encoding='utf-8') as outfile:
        for line in infile:
            try:
                line_dict = json.loads(line.strip())
                text = line_dict.get('text', '')
                if is_non_chinese_text_without_spaces(text):
                    continue
                outfile.write(line)
            except json.JSONDecodeError:
                print(f"Skipping invalid JSON line in file {input_file}: {line.strip()}")

def process_text(input_file, output_file):
    with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'a', encoding='utf-8') as outfile:
        for line in infile:
            try:
                if is_non_chinese_text_without_spaces(line):
                    continue
                outfile.write(line)
            except json.JSONDecodeError:
                print(f"Skipping invalid JSON line in file {input_file}: {line.strip()}")


def main():
    input_folder1 = 'RelFiles/RelJson'
    output_folder1 = 'RelFiles/RelJson_'

    input_folder2 = 'RelFiles/RelText'
    output_folder2 = 'RelFiles/RelText_'

    # Ensure the output directory exists
    os.makedirs(output_folder1, exist_ok=True)
    os.makedirs(output_folder2, exist_ok=True)



    # # Process each text file in the folder
    # for filename in os.listdir(input_folder1):
    #     input_path = os.path.join(input_folder1, filename)
    #     output_path = os.path.join(output_folder1, filename)
    #     if os.path.isfile(input_path):
    #         process_file(input_path, output_path)
    # # Ensure the output directory exists

    # Process each text file in the folder
    for filename in os.listdir(input_folder2):
        input_path = os.path.join(input_folder2, filename)
        output_path = os.path.join(output_folder2, filename)
        if os.path.isfile(input_path):
            process_text(input_path, output_path)

if __name__ == '__main__':
    main()
