import csv
import random


def generate_text_from_csv(file_path: str) -> list:
    result_texts = []
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            year = row['年度'].strip()
            river_name = row['河流'].strip()
            river_name_en = row['英文'].strip()
            area = row['流域面积'].strip()
            percentage = row['占外流河内陆河流域面积'].strip()

            text = f"{year}，{river_name}（英文：{river_name_en}）的流域面积为{area}平方千米，占外流河内陆河流域面积的{percentage}%。\n"
            result_texts.append(text)

    return result_texts


# 使用示例
file_path = '../../otherDatas/【编号223】中国水利统计年鉴/all.csv'
# 调用方法并打印结果
input1_txt = 'filtered_output_select.txt'
input2_txt = 'filtered_output_select2.txt'
rainfall_texts = generate_text_from_csv(file_path)

print("\n降雨量文本：")
for text in rainfall_texts:
    print(text)
print(len(rainfall_texts))

txtlist = list(open(input1_txt,'r',encoding='utf-8').readlines()+rainfall_texts*4)
random.shuffle(txtlist)
print('2719',len(txtlist))

open(input2_txt,'w',encoding='utf-8').writelines(txtlist)
