from decimal import Decimal, getcontext, ROUND_DOWN
import json
import csv
import ast  # 用于将字符串解析为 Python 对象

def format_number(value, decimals=4):
    """格式化数字，保留指定小数位数，不进行四舍五入"""
    # 设置小数位数精度
    getcontext().prec = decimals + 10  # 设置足够的精度
    decimal_value = Decimal(str(value)).quantize(Decimal('1.' + '0' * decimals), rounding=ROUND_DOWN)
    return float(decimal_value)

# 读取 JSON 文件的函数
def read_json(file_path):
    with open(file_path, mode='r', encoding='utf-8') as file:
        data = json.load(file)
    return data

def write_json(file_path, data, indent=4):
    """
    将字典数据写入 JSON 文件。

    参数:
    - file_path: 要写入的 JSON 文件路径
    - data: 要写入的字典数据
    - indent: JSON 文件的缩进级别（默认为 4）
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=indent)
        print(f"数据已成功写入 {file_path}")
    except Exception as e:
        print(f"写入 JSON 文件时出错: {e}")

def find_values_in_column(csv_file, search_values, column_index):
    results = []
    with open(csv_file, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.reader(file,delimiter=';')
        header = next(reader)  # 跳过标题行
        for row in reader:
            if all(value in row for value in search_values):
                results = eval(row[column_index])
    return results

