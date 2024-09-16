from collections import defaultdict

from tqdm import tqdm

from Ctgu.Tools.LTP_ import LTP_

keywords = ['流域面积']



def getfile():
    max_lines = 36606627
    # 定义参数
    def filter_and_split_file(input_file, output_prefix, keywords):
        try:
            output_file = f"{output_prefix}.txt"
            with open(input_file, 'r', encoding='utf-8') as infile,open(output_file, 'a', encoding='utf-8') as outfile:
                for line in tqdm(infile,desc="getfile", total=max_lines, unit='line', unit_scale=True):
                    if any(keyword in line for keyword in keywords):
                        outfile.write(line)
        except Exception as e:
            print(f"发生错误: {e}")
    input_file = '../../../../EncyclopediaData/wiki_split_cws/wikiSplit.txt'
    # input_file = '../../../../EncyclopediaData/baidu and st _v2/baidu_split_v2.txt'

    output_prefix = 'filtered_output'
    filter_and_split_file(input_file, output_prefix, keywords)

def getkeywords():
    import jieba.analyse

    # 示例中文文档
    max_lines = len(open('filtered_output.txt', 'r', encoding='utf-8').readlines())
    with open('filtered_output.txt', 'r', encoding='utf-8') as file1,open('filtered_output_select.txt', 'w', encoding='utf-8') as file2:
        for line in tqdm(file1,desc="getkeywords", total=max_lines, unit='line', unit_scale=True):
            # 使用 TF-IDF 提取关键词
            keywords_tfidf = jieba.analyse.extract_tags(line, topK=10, withWeight=False)
            if len(line) >20 and any(element in keywords for element in keywords_tfidf):
                file2.write(line)
def getkeypos():
    ns_words_count = defaultdict(int)
    max_lines = len(open('filtered_output_select.txt', 'r', encoding='utf-8').readlines())
    with open('filtered_output_select.txt', 'r', encoding='utf-8') as file1 ,\
            open('filtered_output_select_pos.txt', 'w', encoding='utf-8') as file2,\
        open('ns_words_count.txt', 'w', encoding='utf-8') as dict_file:
        for line in tqdm(file1,desc="getkeypos", total=max_lines, unit='line', unit_scale=True):
            if any(keyword in line for keyword in keywords):
                # 使用 TF-IDF 提取关键词
                ltptext = LTP_(line.strip())
                textword,textpos = ltptext.ltpTowords()
                if textpos != False and 'ns' in textpos:
                    file2.write(line)
                    # 提取 ns 词性对应的词并统计出现次数
                    for word, pos in zip(textword, textpos):
                        if pos == 'ns':
                            ns_words_count[word] += 1
        # 将 ns 词及其出现次数写入字典文件
        for word, count in ns_words_count.items():
            dict_file.write(f'{word}: {count}\n')

def rewritetext():
    with open('filtered_output_select_pos.txt', 'r', encoding='utf-8') as file1,\
    open('filtered_output_select_pos_.txt', 'w', encoding='utf-8') as file2:
        fileline = 0
        for line1 in file1:
            fileline+=1
            if "目录" in line1:
                continue
            else:
                file2.write(line1)

def deletetext():
    with open('filtered_output_select_pos_.txt', 'r', encoding='utf-8') as file1,\
    open('filtered_output_select_pos__.txt', 'a', encoding='utf-8') as file2:
        fileline = 0
        for line1 in file1:
            fileline+=1
            if  ('第' in line1 and '章' in line1):
                print('错误',line1)
                continue
            else:
                if len(line1) > 1000:
                    user_input = input(f"{line1} (y/n): ").strip().lower()
                    if user_input == 'n':
                        print('错误', line1)
                        continue
                    else:
                        file2.write(line1)
                else:
                    file2.write(line1)

def deletetext2():
    with open('filtered_output_select.txt', 'r', encoding='utf-8') as file1,\
    open('filtered_output_select2.txt', 'a', encoding='utf-8') as file2:
        fileline = 0
        for line1 in file1:
            fileline+=1
            if len(line1) < 20:
                user_input = input(f"{len(line1)}-{line1} (y/n): ").strip().lower()
                if user_input == 'n':
                    print('错误', line1)
                    continue
                else:
                    file2.write(line1)
            else:
                file2.write(line1)

def duplicate_removal():
    readlinelist = []
    with open('filtered_output_select.txt', 'r', encoding='utf-8') as file1, \
            open('filtered_output_select2.txt', 'a', encoding='utf-8') as file2:
        fileline = 0
        for line1 in file1:
            fileline += 1
            if line1 not in readlinelist:
                readlinelist.append(line1)
        print(fileline,'---',len(readlinelist))
        for line2 in readlinelist:
            file2.write(line2)


if __name__=='__main__':
    getfile()
    getkeywords()
    getkeypos()
    rewritetext()
    deletetext()
    deletetext2()
    # duplicate_removal()





