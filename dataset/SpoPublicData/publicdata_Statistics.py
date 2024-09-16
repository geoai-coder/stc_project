#数据集数据结构获取
import json
from nltk import *

def load_json(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        return json.load(file)

def getDocRED_rel(labels,result,file,i):
    # 遍历labels列表中的每个字典
    for label in labels:
        r_value = label["r"]
        evid = []
        for evid_id in label["evidence"]:
            evid.append(f'{file}-{i}-{evid_id}')
        new_evidence_set = set(evid)  # 将新的evidence列表转换为集合以去重
        # 如果r_value已经在result字典中，则合并新的evidence集合与现有的evidence集合
        if r_value in result:
            result[r_value].update(new_evidence_set)  # 更新现有集合，合并去重
        else:
            result[r_value] = new_evidence_set  # 否则，直接将新的集合赋值给result
    # 将result字典中的集合转换为每个r_value对应的evidence元素总数

    # 输出最终结果
    return result

def process_data(data_list,label_result,file):
    sentences = []
    flag = False
    for i,data in enumerate(data_list):
        for sentence in data["sents"]:
            sentences.append(' '.join(sentence))
        if 'labels' in data:
            label_result = getDocRED_rel(data['labels'],label_result,file,i)
    sentence_lengths = [len(sent) for sent in sentences]
    return sentences, sentence_lengths,label_result

def process_data2(filepath,relation_counts,token=True):
    sentences = []
    sentence_lengths = []
    with open(filepath,'r',encoding='utf-8') as file:
        for line in file:
            data = json.loads(line)
            if token:
                sent = ' '.join(data['token'])
            else:
                sent = data['text']
            sentences.append(sent)
            sentence_lengths.append(len(sent))
            relation = data.get('relation')
            if relation:
                if relation in relation_counts:
                    relation_counts[relation] += 1
                else:
                    relation_counts[relation] = 1
    return sentences, sentence_lengths,relation_counts

def process_data3(filepath,predicate_count):
    sentences = []
    sentence_lengths = []
    with open(filepath,'r',encoding='utf-8') as file:
        for line in file:
            data = json.loads(line)
            sent = data['text']
            sentences.append(sent)
            sentence_lengths.append(len(sent))
            # 遍历 data_list 中的每个字典
            for spo in data.get("spo_list", []):
                predicate = spo.get("predicate")
                if predicate:
                    predicate_count[predicate] += 1
    return sentences, sentence_lengths,predicate_count


def gather_statistics(root_folder):
    print('数据集\t关系数量\t训练数据量\t验证数据量\t测试数据量\t训练集文本均长度\t验证集文本均长度\t测试集文本均长度\t某关系最大文本数量\t某关系最小文本数量')


    reldoc = os.path.join(root_folder, 'DocRED', 'rel_info.json')
    traindoc = os.path.join(root_folder, 'DocRED', 'train_annotated.json')
    testdoc = os.path.join(root_folder, 'DocRED', 'test.json')
    devdoc = os.path.join(root_folder, 'DocRED', 'dev.json')
    reljson, trainlist, testlist, devlist = (load_json(doc) for doc in [reldoc, traindoc, testdoc, devdoc])
    sen_train, senlen_train,label_result1 = process_data(trainlist,{},'train')
    sen_test, senlen_test,label_result2 = process_data(testlist,label_result1,'test')
    sen_dev, senlen_dev,label_result3 = process_data(devlist,label_result2,'dev')
    final_result3 = {key: len(value) for key, value in label_result3.items()}
    max_len = max(final_result3.values())
    min_len = min(final_result3.values())
    print(f'DocRED\t{len(reljson.keys())}\t{len(sen_train)}\t{len(sen_dev)}\t{len(sen_test)}\t'
          f'{sum(senlen_train) / len(senlen_train):.2f}\t{sum(senlen_dev) / len(senlen_dev):.2f}\t{sum(senlen_test) / len(senlen_test):.2f}'
          f'\t{max_len}\t{min_len}')

    relfewrel1,relfewrel2 = os.path.join(root_folder, 'fewrel', 'fewrel_train_rel2id.json'),\
                          os.path.join(root_folder, 'fewrel', 'fewrel_val_rel2id.json')
    trainfewrel = os.path.join(root_folder, 'fewrel', 'fewrel_train.txt')
    devfewrel = os.path.join(root_folder, 'fewrel', 'fewrel_val.txt')
    reljson1,reljson2 = load_json(relfewrel1),load_json(relfewrel2)
    rellist_fewrel = list(set(reljson1.keys()).union(set(reljson2.keys())))
    sen_train_fewrel, senlen_train_fewrel,relation_counts = process_data2(trainfewrel,{})
    sen_dev_fewrel, senlen_dev_fewrel,relation_counts = process_data2(devfewrel,relation_counts)
    max_len = max(relation_counts.values())
    min_len = min(relation_counts.values())
    print(f'fewrel\t{len(rellist_fewrel)}\t{len(sen_train_fewrel)}\t{len(sen_dev_fewrel)}\t-\t'
          f'{sum(senlen_train_fewrel) / len(senlen_train_fewrel):.2f}\t{sum(senlen_dev_fewrel) / len(senlen_dev_fewrel):.2f}\t'
          f'{max_len}\t{min_len}')

    relnyt101 = os.path.join(root_folder, 'nyt10', 'nyt10_rel2id.json')
    trainnyt10 = os.path.join(root_folder, 'nyt10', 'nyt10_train.txt')
    testnyt10 = os.path.join(root_folder, 'nyt10', 'nyt10_test.txt')
    reljson_nyt10 = load_json(relnyt101)
    sen_train_nyt10, senlen_train_nyt10,relation_counts = process_data2(trainnyt10,{},False)
    sen_test_nyt10, senlen_test_nyt10,relation_counts = process_data2(testnyt10,relation_counts,False)
    max_len = max(relation_counts.values())
    min_len = min(relation_counts.values())
    print(f'nyt10\t{len(reljson_nyt10.keys())}\t{len(sen_train_nyt10)}\t-\t{len(sen_test_nyt10)}\t'
          f'{sum(senlen_train_nyt10) / len(senlen_train_nyt10):.2f}\t-\t{sum(senlen_test_nyt10) / len(senlen_test_nyt10):.2f}\t'
          f'{max_len}\t{min_len}')

    relsemeval = os.path.join(root_folder, 'semeval', 'semeval_rel2id.json')
    trainsemeval = os.path.join(root_folder, 'semeval', 'semeval_train.txt')
    devsemeval = os.path.join(root_folder, 'semeval', 'semeval_val.txt')
    testsemeval = os.path.join(root_folder, 'semeval', 'semeval_test.txt')
    reljsonsemeval = load_json(relsemeval)
    sen_train_semeval, senlen_train_semeval,relation_counts = process_data2(trainsemeval,{})
    sen_dev_semeval, senlen_dev_semeval,relation_counts = process_data2(devsemeval,relation_counts)
    sen_test_semeval, senlen_test_semeval,relation_counts = process_data2(testsemeval,relation_counts)
    max_len = max(relation_counts.values())
    min_len = min(relation_counts.values())
    print(f'semeval\t{len(reljsonsemeval.keys())}\t{len(sen_train_semeval)}\t{len(sen_dev_semeval)}\t{len(sen_test_semeval)}\t'
          f'{sum(senlen_train_semeval) / len(senlen_train_semeval):.2f}\t{sum(senlen_dev_semeval) / len(senlen_dev_semeval):.2f}\t{sum(senlen_test_semeval) / len(senlen_test_semeval):.2f}\t'
          f'{max_len}\t{min_len}')

    relwiki80 = os.path.join(root_folder, 'wiki80', 'wiki80_rel2id.json')
    trainwiki80 = os.path.join(root_folder, 'wiki80', 'wiki80_train.txt')
    devwiki80 = os.path.join(root_folder, 'wiki80', 'wiki80_val.txt')
    reljsonwiki80 = load_json(relwiki80)
    sen_train_wiki80, senlen_train_wiki80,relation_counts = process_data2(trainwiki80,{})
    sen_dev_wiki80, senlen_dev_wiki80,relation_counts = process_data2(devwiki80,relation_counts)
    max_len = max(relation_counts.values())
    min_len = min(relation_counts.values())
    print(f'wiki80\t{len(reljsonwiki80.keys())}\t{len(sen_train_wiki80)}\t{len(sen_dev_wiki80)}\t-\t'
          f'{sum(senlen_train_wiki80) / len(senlen_train_wiki80):.2f}\t{sum(senlen_dev_wiki80) / len(senlen_dev_wiki80):.2f}\t\t'
          f'{max_len}\t{min_len}')

    relDuIE20 = os.path.join(root_folder, 'DuIE2.0', 'duie_schema.json')
    trainDuIE20 = os.path.join(root_folder, 'DuIE2.0', 'duie_train.json')
    devDuIE20 = os.path.join(root_folder, 'DuIE2.0', 'duie_dev.json')
    testDuIE20 = os.path.join(root_folder, 'DuIE2.0', 'duie_test2.json')
    reljson = open(relDuIE20,'r',encoding='utf-8').readlines()
    sen_train_DuIE20, senlen_train_DuIE20,predicate_count = process_data3(trainDuIE20, defaultdict(int))
    sen_dev_DuIE20, senlen_dev_DuIE20,predicate_count = process_data3(devDuIE20,predicate_count)
    sen_test_DuIE20, senlen_test_DuIE20,predicate_count = process_data3(testDuIE20,predicate_count)
    predicate_count = dict(predicate_count)
    max_len = max(predicate_count.values())
    min_len = min(predicate_count.values())
    print(f'DuIE2.0\t{len(reljson)}\t{len(sen_train_DuIE20)}\t{len(sen_dev_DuIE20)}\t{len(sen_test_DuIE20)}\t'
          f'{sum(senlen_train_DuIE20) / len(senlen_train_DuIE20):.2f}\t{sum(senlen_dev_DuIE20) / len(senlen_dev_DuIE20):.2f}\t{sum(senlen_test_DuIE20) / len(senlen_test_DuIE20):.2f}\t'
          f'{max_len}\t{min_len}')

if __name__ == "__main__":
    root_folder = 'DataSets'  # 修改为你的文件夹路径
    statistics = gather_statistics(root_folder)
