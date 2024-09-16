import json
import random


def generate_text(date,area_data):
    # 处理每个地区的文本拼接
    province_name = area_data['name']
    citys = area_data['children']
    for city in citys:
        city_name = city['name']
        if city_name == '市辖区':
            districts = city['children']

            # 获取区县的名称列表
            district_names = [district['name'] for district in districts]

            # 拼接结果文本
            text = f"{date},{province_name}下辖{len(district_names)}个{city_name}，包括{', '.join(district_names)}。\n"
        else:
            districts = city['children']

            # 获取区县的名称列表
            district_names = [district['name'] for district in districts[1:]]

            # 拼接结果文本
            text = f"{date},{province_name}的{city_name}下辖{len(district_names)}个市辖区，包括{', '.join(district_names)}。\n"

        return text


def process_area_json(date,file_path):
    # 读取 JSON 文件
    with open(file_path, 'r', encoding='utf-8') as file:
        area_data = json.load(file)

    # 遍历每个省份并生成相应的文本
    results = []
    for province in area_data:
        result_text = generate_text(date,province)
        results.append(result_text)

    return results

# 主程序入口
if __name__ == "__main__":
    json_file_path = ['../../otherDatas/china_area-master/china_area-master/area_code_2018.json',
                      '../../otherDatas/china_area-master/china_area-master/area_code_2019.json',
                      '../../otherDatas/china_area-master/china_area-master/area_code_2020.json',
                      '../../otherDatas/china_area-master/china_area-master/area_code_2021.json',
                      '../../otherDatas/china_area-master/china_area-master/area_code_2022.json']  # 确保将此路径更改为实际文件路径
    datelist=['2018','2019','2020','2021','2022']
    textlist = []
    for date,jsonfile in zip(datelist,json_file_path):
        result_texts = process_area_json(date,jsonfile)
        textlist+=result_texts

    # 读取原始文件内容并追加新的内容
    combined_list = open('filtered_output_select.txt', 'r', encoding='utf-8').readlines() + textlist * 2

    # 打乱顺序
    random.shuffle(combined_list)

    # 将打乱后的内容写入新文件
    with open('filtered_output_select2.txt', 'w', encoding='utf-8') as outfile:
        outfile.writelines(combined_list)
