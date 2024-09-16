import ast
import json
import re


def parse_response(response):
    def clean_response_string(response):
        # 使用正则表达式匹配冒号前的无关字符
        cleaned_response = re.sub(r'\s*[\*\-\s]+(?=\S*:\s*)', '', response)
        return cleaned_response

    def clean_quotes(text):
        # 去掉每个字符串前后的引号
        return text.strip("'\"‘’“”")
    # 初始化空列表
    spo_list, spoType_list, spoTypeSTC_list, T_list, S_list = [], [], [], [], []
    # 使用正则表达式提取 spo, spoType, spoTypeSTC 和 T
    patterns = {
        'spo': re.compile(r'spo\d*:\s*[\(\[]([^,\]\)]+),\s*([^,\]\)]+),\s*([^\)\]]+)[\)\]]'),
        'spoType': re.compile(r'spoType\d*:\s*[\(\[]([^,\]\)]+),\s*([^,\]\)]+),\s*([^\)\]]+)[\)\]]'),
        'spoTypeSTC': re.compile(r'spoTypeSTC\d*:\s*\{([^}]*?)\}'),  # 捕获大括号中的内容
        'T': re.compile(r'T\d*:\s*([^;,. \n]+(?:\s+[^;,. \n]+)*)'),
        'S': re.compile(r'L\d*:\s*([^;,. \n]+(?:\s+[^;,. \n]+)*)')
    }
    # 按行拆分响应字符串
    lines = response.split('\n')
    # 逐行匹配
    for line in lines:
        clean_line = clean_response_string(line)
        for key, pattern in patterns.items():
            match = pattern.search(clean_line)
            if match:
                if key == 'spo' or key == 'spoType':
                    # 合并元组中的元素
                    result = ', '.join(clean_quotes(group) for group in match.groups())
                elif key == 'spoTypeSTC':
                    # 处理字典格式的内容
                    result = ', '.join(f"{kv.split(':')[0].strip()}: {kv.split(':')[1].strip()}"
                                       for kv in match.group(1).split(','))
                else:
                    # 对 T 和 S 直接添加
                    result = match.group(1).strip()
                locals()[f'{key}_list'].append(result)
    return spo_list, spoType_list, spoTypeSTC_list, T_list, S_list


# 测试用例
strlist = (
    "1. spo--: ['广州', 'GDP总计', '1.25万亿元]; spoType: (‘“地点, GDP总计, 数值) \n"
    "2. **spo***: [佛山, GDP总计, 1.25万亿元]; spoType: (地点, GDP总计, 数值) \n"
)

spo_list, spo_type_list, spoSTC_list, T_list, S_list = parse_response(strlist)
print(spo_list)
print(spo_type_list)
def addsttuple():
    dataspo = ('广东', 'GDP总计', '36796.71亿元')
    dataspo_str = dataspo[0] + ', ' + dataspo[1] + ', ' + dataspo[2]
    st_tuple, st_tuple_stc = 'error_tuple', 'error_stc'  # 对于匹配错误时的标签
    for index, (spo_value, spo_type_value, spo_STC_value, T, L) in enumerate(
            zip(spo_list, spo_type_list, spoSTC_list, T_list, S_list), start=1):
        if spo_value == dataspo_str:
            spo_STC_value = '{' + spo_STC_value + '}'
            print(type(spo_STC_value), spo_STC_value)

            stc_info = ast.literal_eval(spo_STC_value)  # 使用 ast.literal_eval 将字符串转换为字典
            stc_t, stc_s = stc_info.get('STC_T', ''), stc_info.get('STC_S', '')
            st_tuple_stc = f"{stc_t}_{stc_s}"
            flag_t = {'Strong': 0, 'Medium': 1}.get(stc_t, -1)  # 根据STC_T和STC_S确定flag和初始st_tuple
            st_tuple = f'({dataspo[0]}, {dataspo[1]}, {dataspo[2]}'
            if flag_t == 0:  # 添加时间信息
                st_tuple += f', {T}'
            elif flag_t == 1:
                st_tuple += f'), {{{T}'
            if stc_s == 'Strong':  # 添加空间信息
                if flag_t in [0, -1]:
                    st_tuple += f', {L})'
                else:  # flag_t == 1
                    st_tuple = f'({dataspo[0]}, {dataspo[1]}, {dataspo[2]}, {L}), {{{T}}}'
            elif stc_s == 'Medium':
                if flag_t == 1:
                    st_tuple += f', {L}}}'
                else:
                    st_tuple += f'), {{{L}}}'
            else:
                st_tuple += f')' if flag_t != 1 else '})'
            break
    print(type(st_tuple),st_tuple)
    print(type(st_tuple_stc),st_tuple_stc)

addsttuple()


def get_keys_from_json(file_path='allDataAnalysis/spotype_STC_updated.json'):
    """读取JSON文件并返回键列表"""
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data, list(data.keys())
def Pattern_matching(spoType,STC, spo_list, spo_type_list):
    spolist, spoTypelist, spotypeSTC = [],[],[]
    for spo,spotype in zip(spo_list,spo_type_list):
        print(spotype)
        spotype = '('+spotype+')'
        if spotype in spoType:
            print(spotype)
            print(spo)
            print(STC[spotype])
            spotypeSTC.append(STC[spotype])
            spolist.append(spo)
            spoTypelist.append(spotype)
        else:
            continue
    return spolist, spoTypelist, spotypeSTC

stc,spotype = get_keys_from_json()
print(stc,spotype)
Pattern_matching(spotype,stc,spo_list, spo_type_list)

import re

def clean_response_string(response):
    # 使用正则表达式匹配冒号前的无关字符
    cleaned_response = re.sub(r'\s*[\*\-\s]+(?=\S*:\s*)', '', response)
    return cleaned_response

# 测试字符串
response = (
    "13. **spo**: *(重庆, GDP总计, 6528.72亿元)\n"
    "    - **spoType**: (地点, GDP总计, 数值)\n"
    "    - **spoTypeSTC**: {'STC_T': 'Strong', 'STC_S': 'Strong'}\n"
    "    - **T**: 2009年\n"
    "    - **L**: 重庆"
)

cleaned_response = clean_response_string(response)
print(response)
print(cleaned_response)
