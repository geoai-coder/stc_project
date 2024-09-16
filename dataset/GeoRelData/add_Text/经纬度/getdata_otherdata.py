import openpyxl

# Load the Excel workbook and the specific sheet
file_path = '../../otherDatas/数据资源整理【三】：最全中国各省份城市编码以及经纬度数据/省市区adcode与经纬度映射表utf8.xlsx'
wb = openpyxl.load_workbook(file_path)
sheet = wb.active
rainfall_texts = list()
# Iterate through each row (skip the header row)
for row in sheet.iter_rows(min_row=2, values_only=True):
    print(row)
    _, region, longitude, latitude = row

    # Format the string
    summary = f"简介：{region}的经纬度为东经{longitude}度，北纬{latitude}度。\n"

    # Print or store the result
    rainfall_texts.append(summary)
input1_txt = 'filtered_output_select4.txt'
input2_txt = 'filtered_output_select.txt'

for text in rainfall_texts:
    print(text)
print(len(rainfall_texts))

txtlist = list(set(open(input1_txt,'r',encoding='utf-8').readlines()+rainfall_texts[:1500]))
print(len(txtlist))
open(input2_txt,'w',encoding='utf-8').writelines(txtlist)