import csv


# 第二个方法：拼接年平均降雨量文本
# 第二个方法：拼接年平均降雨量文本
# 第二个方法：拼接年平均降雨量文本
def concatenate_rainfall_text(file_path):
    rainfall_texts = []
    data = {}

    # 读取数据并按地区存储在字典中
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)  # 跳过表头

        for row in reader:
            year = int(row[2])
            region = row[0]
            rainfall = float(row[4])
            if region not in data:
                data[region] = []
            data[region].append((year, rainfall))

    # 对每个地区的数据按年份排序
    for region, records in data.items():
        records.sort(key=lambda x: x[0])

        i = 0
        grouped_intervals = []

        while i <= len(records) - 5:
            start_year = records[i][0]
            end_year = records[i + 4][0]

            if end_year == start_year + 4:
                avg_rainfall = sum(x[1] for x in records[i:i + 5]) / 5
                min_rainfall = int(avg_rainfall // 50 * 50)
                max_rainfall = min_rainfall + 50
                current_range = (min_rainfall, max_rainfall)

                # 检查当前区间是否可以合并到之前的区间
                if grouped_intervals and grouped_intervals[-1]['rainfall_range'] == current_range:
                    grouped_intervals[-1]['end_year'] = end_year
                else:
                    grouped_intervals.append({
                        'start_year': start_year,
                        'end_year': end_year,
                        'rainfall_range': current_range
                    })

                i += 5
            else:
                i += 1

        # 格式化并添加到结果列表中
        for interval in grouped_intervals:
            start_year = interval['start_year']
            end_year = interval['end_year']
            min_rainfall, max_rainfall = interval['rainfall_range']
            sentence = f"{start_year}年-{end_year}年，{region}年平均降雨量为{min_rainfall}-{max_rainfall}毫米。\n"
            rainfall_texts.append(sentence)

    return rainfall_texts
# 调用方法并打印结果
file_path = '../../otherDatas/气温降雨data.csv'
input1_txt = 'filtered_output_select2.txt'
input2_txt = 'filtered_output_select.txt'
rainfall_texts = concatenate_rainfall_text(file_path)

print("\n降雨量文本：")
for text in rainfall_texts:
    print(text)
print(len(rainfall_texts))

txtlist = list(set(open(input1_txt,'r',encoding='utf-8').readlines()+rainfall_texts[:150]))
print(len(txtlist))
open(input2_txt,'w',encoding='utf-8').writelines(txtlist)
