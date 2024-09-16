import openpyxl

# Load the Excel workbook and the specific sheet
file_path = '../../otherDatas/全国及各省森林面积.xlsx'
wb = openpyxl.load_workbook(file_path)
sheet = wb.active
rainfall_texts = list()
# Iterate through each row (skip the header row)
for row in sheet.iter_rows(min_row=2, values_only=True):
    print(row)
    year, region, forestry_land_area, forest_area, plantation_area, forest_coverage,_ = row

    # Format the string
    summary = f"{year}年，{region}地区的林业用地面积为{forestry_land_area}万公顷，森林面积为{forest_area}万公顷，人工林面积为{plantation_area}万公顷，森林覆盖率为{forest_coverage}%。\n"

    # Print or store the result
    rainfall_texts.append(summary)
input1_txt = 'filtered_output_select.txt'
input2_txt = 'filtered_output_select2.txt'

for text in rainfall_texts:
    print(text)
print(len(rainfall_texts))

txtlist = list(set(open(input1_txt,'r',encoding='utf-8').readlines()+rainfall_texts))
print(len(txtlist))
open(input2_txt,'w',encoding='utf-8').writelines(txtlist)