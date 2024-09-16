import csv


# 第一个方法：拼接气温文本
def concatenate_temperature_text(file_path):
    temperature_texts = []

    # 打开CSV文件
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # 跳过表头

        for row in reader:
            year = int(row[2])
            region = row[0]
            annual_rainfall = row[4]
            if row[3] == 'nan':
                continue
            avg_temp = round(float(row[3]), 2)
            sentence = f"{year}年，{region}地区的年平均气温为{avg_temp}摄氏度，年降雨量为{annual_rainfall}毫米。\n"
            temperature_texts.append(sentence)

    return temperature_texts

# 调用方法并打印结果
file_path = '../../otherDatas/气温降雨data.csv'
input1_txt = 'filtered_output_select2.txt'
input2_txt = 'filtered_output_select.txt'
temperature_texts = concatenate_temperature_text(file_path)

print("气温文本：")
for text in temperature_texts:
    print(text)
print(len(temperature_texts))
txtlist = list(set(open(input1_txt,'r',encoding='utf-8').readlines()+temperature_texts[:700]))
print(len(txtlist))
open(input2_txt,'w',encoding='utf-8').writelines(txtlist)
