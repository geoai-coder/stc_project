import json
from ctgucode.tools.SetGlobalVariables import RelLabel, spoType, config_loader
import os

def percentage_to_float(percentage):
    """Convert a percentage string to a float."""
    return float(percentage.strip('%')) / 100.0


def get_stc_run(input_mergeddata, output_stc, inputfile ='merged_data.json'):
    """Update STC (Spatial-Temporal Consistency) values based on the merged data."""
    # 读取 merged_data.json 文件
    merged_data_path = os.path.join(input_mergeddata, inputfile)
    with open(merged_data_path, 'r', encoding='utf-8') as f:
        merged_data = json.load(f)

    spo_stc = {}

    # 遍历 merged_data 并进行判断
    for key, value in merged_data.items():
        mapped_key = RelLabel.get(key, {}).get("spo_chinese")
        if mapped_key and mapped_key in spoType:
            sta_time = percentage_to_float(value.get('sta_time', '0%'))
            sta_space = percentage_to_float(value.get('sta_space', '0%'))

            # 尝试读取 dyn_time 和 dyn_space
            dyn_time = percentage_to_float(value.get('dyn_time', '0%'))
            dyn_space = percentage_to_float(value.get('dyn_space', '0%'))

            # 初始化字典项
            if mapped_key not in spo_stc:
                spo_stc[mapped_key] = {'STC_T': 'Medium', 'STC_S': 'Medium'}

            # 更新 STC_T
            if sta_time < 0.1 and dyn_time < 0.05:
                spo_stc[mapped_key]['STC_T'] = 'Weak'
            elif sta_time >= 0.1 and dyn_time < 0.05:
                spo_stc[mapped_key]['STC_T'] = 'Medium'
            else:
                spo_stc[mapped_key]['STC_T'] = 'Strong'

            # 更新 STC_S
            if sta_space < 0.1 and dyn_space < 0.05:
                spo_stc[mapped_key]['STC_S'] = 'Weak'
            elif sta_space >= 0.1 and dyn_space < 0.05:
                spo_stc[mapped_key]['STC_S'] = 'Medium'
            else:
                spo_stc[mapped_key]['STC_S'] = 'Strong'

    # 将结果写回 spotype_STC.json 文件
    with open(output_stc, 'w', encoding='utf-8') as f:
        json.dump(spo_stc, f, ensure_ascii=False, indent=4)

    print("Process completed successfully!")


