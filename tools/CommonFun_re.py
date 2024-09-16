'''
replace_spaces_with_comma:将多个空格替换为一个空格
'''

import re


def replace_unicode_with_space(text):
    # 使用正则表达式匹配 Unicode 字符
    unicode_pattern = re.compile(r'[\x00-\x7F\x80-\xFF\u0100-\uFFFF]')  # 匹配所有 Unicode 字符
    # 替换匹配到的 Unicode 字符为 UTF-8 中的空格
    result_text = unicode_pattern.sub(' ', text)

    return result_text

def replace_spaces_with_comma(input_string):
    # 将多个空格替换为一个空格

    # single_space1 = replace_unicode_with_space(input_string)
    input_string = input_string.replace('', ' ')
    input_string = input_string.replace('\x7F', '')  #空格字符
    input_string = input_string.replace('\u00AD', '')  #空格字符
    result = re.sub(r'\s+', ' ', input_string)

    # 将空格替换为逗号，但只在空格前后没有标点符号的情况下替换
    # pattern = r'(?<=[^，。！？.,!?“”":；：;])\s(?=[^，。！？.,!?“”":；：;])'
    # result = re.sub(pattern, '，', content)
    # result = content.replace(' ','，')
    # result = result.replace('','，')
    return result
