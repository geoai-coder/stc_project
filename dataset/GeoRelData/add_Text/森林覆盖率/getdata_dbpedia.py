from collections import defaultdict

from Ctgu.Tools.LTP_ import LTP_

keywords = ['森林覆盖率']


def filter_and_split_file(input_file, output_prefix, keywords):
    try:
        readnum, wikinum = 1, 15360810
        output_file = f"{output_prefix}.txt"
        with open(input_file, 'r', encoding='utf-8') as infile,open(output_file, 'a', encoding='utf-8') as outfile:
            for line in infile:
                readnum += 1
                rate = readnum / wikinum
                if keywords[0] in line:
                    outfile.write(line)
                print(f'第：{rate:.3%}')
    except Exception as e:
        print(f"发生错误: {e}")


def getfile():
    # 定义参数
    # input_file = '../../../../EncyclopediaData/wiki_split_cws/wikiSplit.txt'
    input_file = '../../../../EncyclopediaData/baidu and st _v2/baidu_split_v2.txt'

    output_prefix = 'filtered_output'

    # 运行函数
    filter_and_split_file(input_file, output_prefix, keywords)

def getkeywords():
    import jieba.analyse
    import jieba
    for key in keywords:
        jieba.add_word(key)

    # 示例中文文档
    readnum,filelen = 0,12152
    with open('filtered_output.txt', 'r', encoding='utf-8') as file1,open('filtered_output_select.txt', 'w', encoding='utf-8') as file2:
        print('在读取文件')
        for line in file1:
            readnum += 1
            rate = readnum / filelen
            print(f'第：{rate:.3%}')
            # 使用 TF-IDF 提取关键词
            keywords_tfidf = jieba.analyse.extract_tags(line, topK=10, withWeight=False)
            if len(line) > 20 and any(element in keywords for element in keywords_tfidf):
                file2.write(line)
                # print(line.strip())
                # print("TF-IDF Keywords:", keywords_tfidf,'\n')

def getkeypos_m():
    ns_words_count_nz = defaultdict(int)
    with open('filtered_output_select.txt', 'r', encoding='utf-8') as file1 ,\
            open('filtered_output_select_pos.txt', 'w', encoding='utf-8') as file2,\
        open('ns_words_count.txt', 'w', encoding='utf-8') as dict_file_nz:
        readnum, filelen = 0, 27469
        for line in file1:
            readnum += 1
            rate = readnum / filelen
            print(f'第：{rate:.3%}')
            if keywords[0] in line:
                # 使用 TF-IDF 提取关键词
                ltptext = LTP_(line.strip())
                textword,textpos = ltptext.ltpTowords()
                if textpos != False and 'm' in textpos:
                    file2.write(line)
                    # 提取 ns 词性对应的词并统计出现次数
                    for word, pos in zip(textword, textpos):
                        if pos == 'nz' or pos =='ns':
                            ns_words_count_nz[word] += 1
        # 将 ns 词及其出现次数写入字典文件
        for word, count in ns_words_count_nz.items():
            dict_file_nz.write(f'{word}: {count}\n')

def rewritetext():
    with open('filtered_output_select_pos.txt', 'r', encoding='utf-8') as file1,\
    open('filtered_output_select_pos_.txt', 'w', encoding='utf-8') as file2:
        fileline = 0
        for line1 in file1:
            fileline+=1
            print(f"7811-{fileline}")
            if "目录" in line1:
                print(fileline, line1)
                continue
            else:
                file2.write(line1)

def deletetext():
    with open('filtered_output_select_pos_.txt', 'r', encoding='utf-8') as file1,\
    open('filtered_output_select_pos__.txt', 'a', encoding='utf-8') as file2:
        fileline = 0
        for line1 in file1:
            fileline+=1
            print(f"7811-{fileline}")
            if  ('第' in line1 and '章' in line1):
                print('错误',line1)
                continue
            else:
                if len(line1) > 1000:
                    user_input = input(f"{line1} (y/n): ").strip().lower()
                    if user_input == 'n':
                        print(len(line1),'错误', line1)
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

    # getfile()
    # getkeywords()
    # getkeypos_m()
    # rewritetext()
    # deletetext()
    duplicate_removal()
