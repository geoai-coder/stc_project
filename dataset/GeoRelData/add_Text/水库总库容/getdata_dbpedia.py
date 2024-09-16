from Ctgu.Tools.LTP_ import LTP_


def filter_and_split_file(input_file, output_prefix, keywords):
    try:
        readnum, wikinum = 1, 15360810
        output_file = f"{output_prefix}.txt"
        with open(input_file, 'r', encoding='utf-8') as infile,open(output_file, 'a', encoding='utf-8') as outfile:
            for line in infile:
                readnum += 1
                rate = readnum / wikinum
                if ('水库'in line) and '总库容' in line:
                    outfile.write(line)
                print(f'第：{rate:.3%}')
    except Exception as e:
        print(f"发生错误: {e}")


def getfile():
    # 定义参数
    # input_file = '../../../../EncyclopediaData/wiki_split_cws/wikiSplit.txt'
    input_file = '../../../../EncyclopediaData/baidu and st _v2/baidu_split_v2.txt'

    output_prefix = 'filtered_output'
    keywords = ['水系']

    # 运行函数
    filter_and_split_file(input_file, output_prefix, keywords)

def getkeywords():
    import jieba.analyse

    keywords = ['总库容']
    # 示例中文文档
    readnum,filelen = 0,12152
    with open('filtered_output_select.txt', 'r', encoding='utf-8') as file1,open('filtered_output_select_pos.txt', 'w', encoding='utf-8') as file2:
        for line in file1:
            readnum += 1
            rate = readnum / filelen
            # 使用 TF-IDF 提取关键词
            if ('水库' in line) and '总库容' in line:
                ltptext = LTP_(line.strip())
                textword, textpos = ltptext.ltpTowords()
                if textpos != False and 'ns' in textpos and 'm' in textpos:
                    file2.write(line)
                    # print(line.strip())
                    # print("TF-IDF Keywords:", keywords_tfidf,'\n')
            print(f'第：{rate:.3%}')

def deletetext():
    with open('filtered_output_select_pos_.txt', 'r', encoding='utf-8') as file1,\
    open('filtered_output_select_pos__.txt', 'a', encoding='utf-8') as file2:
        fileline = 0
        for line1 in file1:
            fileline+=1
            print(f"7811-{fileline}")
            # if fileline > 2797:
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
    # getkeypos()
    # deletetext()
    # deletechinse()
    duplicate_removal()
