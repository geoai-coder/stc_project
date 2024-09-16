import os
import logging
from ctgucode.stc_analysis.dynamic_semantic import *
from ctgucode.stc_analysis.bootstrap_km_dep import *
from ctgucode.stc_analysis.dataAnalysis import *
from ctgucode.plotpreocess.dynamic_plots import *
from ctgucode.plotpreocess.statistical_plots import *
from ctgucode.plotpreocess.spatiotemporal_synthesis import *
from ctgucode.pm_exper.get_stc import *
from ctgucode.pm_exper.gpt_dataFilter import *
from ctgucode.pm_exper.gpt_exper import *
from dataset.GeoRelData.add_Text import word_pos

# 设置日志配置
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def init_paths():
    logging.info('Initializing paths...')
    paths = {
        'bert_path': config_loader.get_value('modelpath', 'bert_path'),
        'geo_path': config_loader.get_value('dataset', 'geo_path'),
        'stc_dynsemantic_path': config_loader.get_value('resultpath', 'stc_dynsemantic_path'),
        'stc_bootstrapAnalyse_path': config_loader.get_value('resultpath', 'stc_bootstrapAnalyse_path'),
        'stc_StatisticalPlot_path': config_loader.get_value('resultpath', 'stc_StatisticalPlot_path'),
        'stc_DynSemanticPlot_path': config_loader.get_value('resultpath', 'stc_DynSemanticPlot_path'),
        'stc_allanalysis_path': config_loader.get_value('resultpath', 'stc_allanalysis_path'),
        'output_stc' : config_loader.get_value('static', 'stc_schema_path')
    }

    dynfilename = 'DynSemantic_new.json'
    stafilename = 'new_dep_stop_2000_3500'
    file_m = '2000'
    data_stats, traindata, testdata = 'data_stats.json', 'traindatalist.txt', 'testdatalist.txt'
    models = ["gpt-4o-mini", "gpt-4o", "gpt-4o-2024-08-06"]
    logging.info('Paths initialized.')
    return paths, dynfilename, stafilename, file_m, data_stats, traindata, testdata, models

def data_analysis():
    paths, _, _, _, data_stats, traindata, testdata, models = init_paths()
    logging.info('0- 数据统计')
    all_data_analysis_run()
    gpt_dataFilter_run(data_stats, traindata, testdata)

def all_analysis_plots_run():
    logging.info('1- 时空关联度计算：')
    paths, dynfilename, stafilename, file_m,_ ,_ ,_,_ = init_paths()

    def dyn_analysis_plot(paths, dynfilename, file_m, stafilename):
        bootresult = os.path.join(paths['stc_bootstrapAnalyse_path'], file_m,
                                  f'GeoRelAnalyseBootstrap_{stafilename}.json')
        analyzer = DynamicSemanticAnalyzer(
            bootresult,
            model_path=paths['bert_path'],
            input_folder=paths['geo_path'],
            output_folder=paths['stc_dynsemantic_path'],
            dynfilename=dynfilename
        )
        analyzer.process_files()

        visualizer = DynDataVisualizer(
            input_dir=paths['stc_dynsemantic_path'],
            output_dir=paths['stc_DynSemanticPlot_path'],
            dynfilename=dynfilename
        )
        visualizer.plot_time_space_mean_sorted()

    def sta_analysis_plot(paths, file_m, stafilename):
        # sta_run(start=500, step=200, count=50, fixed_values=[500, 1000,1500,2000,2500,3000])
        visualizer = StaDataVisualizer(
            input_dir=paths['stc_bootstrapAnalyse_path'],
            input_m=file_m,
            filenum=stafilename,
            output_dir=paths['stc_StatisticalPlot_path']
        )
        visualizer.plot_time_space_mean_sorted()

    def all_analysis_plot(paths, stafilename, file_m, dynfilename):
        visualizer = All_DataVisualizer(
            input_json_dyn=paths['stc_dynsemantic_path'],
            file_m=file_m,
            dynfilename=dynfilename,
            input_dir_sta=paths['stc_bootstrapAnalyse_path'],
            filenum=stafilename,
            output_dir_plt=paths['stc_allanalysis_path']
        )
        visualizer.plot_time_sorted()
        visualizer.plot_space_sorted()
    # logging.info('1.0- 时空关联度统计 - 数据处理：')
    # word_pos.main()
    logging.info('1.1- 时空关联度统计 - 静态：')
    sta_analysis_plot(paths, file_m, stafilename)
    logging.info('1.2- 时空关联度统计 - 动态：')
    dyn_analysis_plot(paths, dynfilename,file_m, stafilename)
    logging.info('1.3- 时空关联度统计 - 特征1图+特征2图：')
    all_analysis_plot(paths, stafilename,file_m, dynfilename)
    logging.info('1.4- 时空关联度值确定：')
    get_stc_run(paths['stc_allanalysis_path'], paths['output_stc'])


def gpt_exper():
    paths, _, _, _, data_stats, traindata, testdata, models = init_paths()

    logging.info('2- 时空关联度值匹配：')
    logging.info('2.1- 时空关联度值匹配 - GPT实验：')
    gpt_exper_run(models,endlen=-1)

if __name__ == '__main__':
    # data_analysis()
    all_analysis_plots_run()    # 时空关联度计算
    # gpt_exper()     # 大模型
