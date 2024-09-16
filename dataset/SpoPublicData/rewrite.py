import json

readfile = open('relation.json','r',encoding='utf-8').read()
original_dict = json.loads(readfile)


# 创建一个新的字典，用于存储修改后的键值对
new_dict = {}

# 使用 enumerate 为每个键分配一个序号，序号从 1 开始
print(len(original_dict.keys()))
for i, (key, value) in enumerate(original_dict.items(), 1):
    new_key = f"Rel{i}"
    new_dict[new_key] = value
    print(f'{i}:{value}\n-{value["Chinese"]}\n')


print(new_dict)

with open('relation.json', 'w') as json_file:
    json.dump(new_dict, json_file,ensure_ascii=False, indent=4)

print("字典已写入 output.json 文件")