# Here is a detailed explanation of all the findings in Section 5, "Experimental Results and Analysis."

## 1. "Table 2: Details of Publicly Available Datasets" is described as follows

### 1.1 Table Introduction
Table 2 presents the publicly available entity-relation datasets and knowledge bases used in the experiments. These datasets are utilized to construct the spatio-temporal correlation calculation model, with a particular focus on relations (or triple types) relevant to the geographical domain, as well as the original texts containing these relationships. Through these datasets, we are able to obtain relevant information about geographical features such as mountains, elevation, and population. The table provides the following key information for each dataset:

(1). **Number of Relations**: The total number of relationship types covered in each dataset.    
(2). **Total Data**: The quantity of texts contained within the dataset.  
(3). **Average Text Length**: Refers to the average character length of each text segment in the dataset, assisting in evaluating text complexity.  
(4). **Data Annotation Format**: The annotation format of the texts in the dataset, detailing how entities and relationships are marked for subsequent analysis and model processing.    

This information provides the data foundation for the development of the spatio-temporal correlation calculation module, particularly in obtaining geographical relationships. Relationships such as "mountains," "elevation," and "population," as shown in Table 2, are extracted from these datasets and utilized in the spatio-temporal correlation analysis in the study.    

### 1.2 Data Source:
All datasets listed in the table are publicly available, including: The DocRED dataset is a large-scale document-level relation extraction dataset (related links: https://github.com/thunlp/DocRED). The FewRel dataset is a large-scale few-shot relation extraction dataset, which contains more than one hundred relations and tens of thousands of annotated instances across different domains. (Related links：https://github.com/thunlp/FewRel). The NYT10 dataset is the most commonly used dataset for relation extraction tasks based on distant supervision (related links: https://github.com/thunlp/OpenNRE/blob/master/benchmark/download_nyt10.sh). The SemEval dataset is the dataset used for the Task8 task in the 2010 International Conference on Semantic Evaluation (related link: https://github.com/thunlp/OpenNRE/blob/master/benchmark/download_semeval.sh). The Wiki80 dataset is a relation dataset extracted from the FewRel dataset (related links: https://github.com/thunlp/OpenNRE/blob/master/benchmark/download_wiki80.sh). The DuIE2.0 dataset is the largest schema-based Chinese relation extraction dataset in the industry (related links: https://www.luge.ai/#/luge/dataDetail?id=5). CN-DBpedia is a large-scale, general-domain structured encyclopedia developed and maintained by the Knowledge Workbench Laboratory of Fudan University (related links: http://kw.fudan.edu.cn/cndbpedia/intro/).    

## 2. "Table 3. Dataset Statistics" is described as follows

### 2.1 Table Introduction
Table 3 presents the statistical information for each dataset used in the spatio-temporal correlation calculation module. The table includes key statistical indicators such as the number of relationships, the number of texts, and the average character length of the texts for each dataset. This statistical information helps to understand the distribution of input data for the spatio-temporal correlation module and provides a foundation for subsequent analyses.    

### 2.2 Data Source:
The data mainly comes from the publicly available datasets listed in Table 2 and encyclopedic data. By combining these data sources, a comprehensive dataset suitable for spatio-temporal correlation analysis has been constructed.    

### 2.3 Methods and Tools
Development is conducted using PyCharm, with Python code written for batch data processing. The code automates the handling of datasets and knowledge bases, ensuring data consistency and efficiency.    

### 2.4 Processing Workflow
(1). **Separate Annotated Data**: Process the data according to the annotation format of each dataset, extracting "head entity" (e.g., "subject" in DuIE2.0), "relationship" (e.g., "predicate" in DuIE2.0), "tail entity" (e.g., "object" in DuIE2.0), "head entity type" (e.g., "subject_type" in DuIE2.0), and "tail entity type" (e.g., "object_type" in DuIE2.0).    
(2). **Classify and Store by Relationship**: Store texts from each dataset according to relationship types. For instance, if both FewRel and DuIE2.0 contain the "population" relationship, all texts related to "population," along with their corresponding head entities, tail entities, and entity types, are stored in a "population" file. The storage format is: {"text": sentence, "spo": (s, p, o), "spo_type": (s_type, p, o_type)}.    
(3). **Complete Dataset Processing**: Through the aforementioned steps, the full relationships and corresponding texts for each dataset were generated. For English texts, translation processing was performed.    
(4). **Knowledge Base (CN-DBpedia) Processing**: For the CN-DBpedia knowledge base, relationships are extracted based on the "relation" in the triples. For "BaiduTAG" relationships, the tail entity represents the entity type. Although an entity may correspond to multiple types, when the relationship is fixed, the head and tail entity types tend to be the same or similar categories. Thus, processing the knowledge base allows for the extraction of relationships and their corresponding triple types.    
(5). **Data Integration**: The processed datasets are combined with the results from the knowledge base to filter out relationships (or triple types) relevant to the geographical domain, extracting the corresponding texts accordingly.    
(6). **Data Augmentation**: The number of texts for each filtered relationship is counted, and encyclopedic data is used for augmentation. The TF-IDF algorithm calculates a keyword list for each encyclopedic text, extracting the top 10 keywords. If these keywords are similar to known relationship types, the text is added to the corresponding relationship text set.    
(7). **Dataset Construction**: The construction of relationships (or triple types) relevant to the geographical domain and their corresponding texts has been completed, resulting in the final dataset for the spatio-temporal correlation module.    
(8). **Dataset Statistical Analysis**: A comprehensive analysis of the constructed dataset is performed, including metrics such as text length and vocabulary distribution to ensure the quality and diversity of the dataset.    

## 3. "Table 4. Data content of some triple types in the dataset." is described as follows

### 3.1 Table Introduction
Table 4 presents the dataset of the spatio-temporal correlation calculation module, which includes textual content of specific types of triplets. Taking the following two types of triplets as examples:

(1). **(Administrative Region, Population, Number)**: This triple type represents the relationship between an administrative region and its corresponding population count.    
(2). **(Location, Climate, Climate)**: This triplet type describes the relationship between a geographical location and its climate characteristics.    

### 3.2 Data Source
The data used in the table is sourced from the dataset corresponding to the spatio-temporal correlation module in Table 3.    

## 4. "Table 5. Data situation of training and testing sets." is described as follows

### 4.1 Table Introduction
Table 5 presents the dataset used in the spatio-temporal correlation pattern matching module, specifically the textual statistics of the testing and training sets. This table helps to understand the distribution of the data used in the experiment, including the number of texts, features, and distribution of both the training and testing sets.    

### 4.2 Data Source
Due to the use of large models in this module's experiments, and to balance budget and computational resource constraints, only 220 data entries were selected for the experiment. All data is sourced from the spatio-temporal correlation dataset constructed in Section 5.1.1.    

### 4.3 Data Processing
Different tasks require different data formats. In Section 5.1.2, to construct the spatio-temporal knowledge representation model based on spatio-temporal correlation, this paper expands the data annotation structure. The specific format is as follows:
```python
{
 "text": sentence, 
 "spo": (s, p, o), 
 "L": Spatio information, 
 "T": temporal information, 
 "spoType": (s_type, p, o_type), 
 "STC": {"STC_T": value, "STC_S": value}, 
 "STTuple": STtuple
}
```
For example:
```python
{
 "text": "Based on the urban population, the GDP of Hong Kong in 2004 was $164 billion.",
 "spo": ["Hong Kong", "Total GDP", "$164 billion"], 
 "L": "Hong Kong", 
 "T": "2004年", 
 "spoType": "(行政区, GDP总计, 数值)", 
 "STC": {"STC_T": "Strong", "STC_S": "Strong"}, 
 "STTuple": "(香港, GDP总计, 1640亿美元, 2004年, 香港)"
}
[{
 "text": "Based on the urban population, the GDP of Hong Kong was US$164 billion in 2004." ,
 "spo": ['Hong Kong', 'Total GDP', 'US$164 Billion'],
 "L": 'Hong Kong',
 "T": '2004',
 "spoType": '(Administrative Region, Total GDP, Value)',
 "STC": {"STC_T": 'Strong', 'STC_S': 'Strong'}, 
 "STTuple":"(Hong Kong, Total GDP, $164 billion, 2004, Hong Kong)"
}]
```
In addition to the original data annotation structure, time information (T) and spatial information (L) have been added, introducing the STtuple that integrates spatio-temporal information for a more comprehensive expression of spatio-temporal correlation:
```python
L: Represents the geographical location involved in the text (spatial information).    
T：Indicates the time point or time range in the text (temporal information).    
STC：Reflects the strength of spatio-temporal correlation, divided into temporal correlation (STC_T) and spatial correlation (STC_S).    
STtuple：Provides a complete description of the corresponding spatio-temporal information for each triplet.    
```

This annotation structure enables the spatio-temporal correlation module to better understand and process spatio-temporal knowledge, thereby constructing a spatio-temporal knowledge representation model.    

## 5. "Figure 5. Feature statistics results." is described as follows

### 5.1 Chart Introduction
The content in the chart displays the calculation results of the spatio-temporal correlation module regarding spatio-temporal dependency features and dynamic semantic features. To clearly present the performance of different triple types under these two features, we have adopted a step-by-step display method:

(1). **Figure a**: Displays the statistical results of spatio-temporal dependency features for different triple types. This feature is used to assess the dependency of tuples in both temporal and spatial dimensions.    
(2). **Figure b**: Shows the statistical results of the dynamic semantic features of tuples, which describe the extent of semantic variation under different spatio-temporal conditions.    
(3). **Figure c**: Presents the statistical results of dependency features and dynamic semantic features in the temporal dimension, reflecting the impact of time changes on tuples.    
(4). **Figure d**: Illustrates the statistical results of dependency features and dynamic semantic features in the spatial dimension, focusing on the influence of space on tuples.    

Through these charts, users can intuitively understand the spatio-temporal dependency and dynamic semantic variation characteristics of different triple types across various dimensions.    

### 5.2 Processing Flow
The processing flow depicted in this figure refers to Section 4.1, "The Calculation of spatio-temporal Correlation," which outlines the method for calculating spatio-temporal correlation. The specific process includes:

1. Extract spatio-temporal dependency features and dynamic semantic features based on the spatio-temporal information of tuples.    
2. Perform separate statistical analyses for each feature.    
3. Display the statistical results according to the temporal and spatial dimensions, generating feature maps for different dimensions.    

## 6. "Table 6. Spatio-temporal correlation of triple types." is described as follows

### 6.1 Table Introduction
The table lists four types of tuples along with their feature calculation values:

(1). **(Administrative Region, Population, Number)**: Analyzes the population figures of different administrative regions.    
(2). **(Mountains, Main Peaks, Peaks)**: Involves information about the main peaks of specific mountain ranges.    
(3). **(Person, Proposed, Conception)**: Concepts proposed by specific individuals.    
(4). **(Conception, Concepts, Text)**: Describes the defining texts of concepts.    

The calculated values of the four triple types for spatio-temporal dependency features and dynamic semantic features yield the spatio-temporal correlation values for each triple type through a combined analysis of the two features.    

### 6.2 Processing Flow
The following presents the pseudocode for calculating spatio-temporal correlation, taking into account the impact of both features on knowledge within the spatio-temporal dimension:
Algorithm 1 Determine Spatio-Temporal Correlation (STC) for a Triple Type
```python
Input: 
TextSet_spotype: Text set containing a collection of spotype information
Output: 
STC: Spatio-temporal correlation for triple types, including spatial correlation (STC_S) and temporal correlation (STC_T)
1: for TextSet_spotype in TextSet_spotype_List do // Retrieve the text set for each triple type from the dataset.    
2: Initialize STC_T and STC_S 
3: [sta_time, sta_space] ← SemanticsBootstrap(File_spotype) // Feature 1: Calculate the spatio-temporal dependency.    
4: [dyn_time, dyn_space] ← DynamicSemantic(File_spotype) // Feature 2: Calculate the dynamic semantic value of the tuples.    
5: for (sta_value, dyn_value, STC) in [(sta_time, dyn_time, STC_T), (sta_space, dyn_space, STC_S)] do // Combined Calculation of Features.    
6: if sta_value < sta_threshold and dyn_value < dyn_threshold then 
7: STC ← 'Weak'
8: else if sta_value >= sta_threshold and dyn_value < dyn_threshold then 
9: STC ← 'Medium'
10: else 
11: STC ← 'Strong'
12: end if
13: end for
14: end for
15: return STC
```

## 7. "Figure 6. Ontology layer of geographic knowledge graph based on spatio-temporal correlation." is described as follows

### 7.1 Chart Introduction
Figure 6 displays the ontology layer of the geographic knowledge graph based on spatio-temporal correlation, showcasing the 22 types of tuples constructed so far and their visualized spatio-temporal correlation values.    

### 7.2 Processing Flow
Based on the results from Section 5.2.1 and the analysis method in Section 4.1.3, the spatio-temporal correlation for each triple type is calculated. The specific steps are as follows:

(1). **Weak Relevance**: For tuples with weak spatio-temporal correlation, spatio-temporal information is not included, such as in the case of concept definitions.    
(2). **Moderate Relevance**: Tuples with moderate spatio-temporal correlation incorporate relevant spatio-temporal information as tuple attributes, based on specific moderate temporal, spatial, or spatio-temporal correlation.    
(3). **Strong Relevance**: For tuples with strong spatio-temporal correlation, relevant spatio-temporal information is integrated into the tuple based on specific strong temporal, spatial, or spatio-temporal correlation.    

This processing approach helps clearly represent the relationships of different triple types within the spatio-temporal dimension, making the construction of the geographic knowledge graph more precise.    

## 8. "Table 7. Examples of spatio-temporal knowledge representation model construction." is described as follows

### 8.1 Table Introduction
Table 7 presents example results of spatio-temporal correlation matching and the construction of the spatio-temporal knowledge representation model using a large language model (LLM) on the texts in "Sentences."

### 8.2 Processing Flow
(1). Create a prompt for entity-relation triple type extraction tasks. For example: "Now I have an entity-relation triple type table spoTypeTable: {self.spoType}. Spo is a data structure for representing knowledge, typically denoted as (S, P, O), where S and O are entity objects and P represents their relationship, e.g., (China, Capital, Beijing). SpoType refers to the categories or concepts of the elements in the triple. For instance, (China, Capital, Beijing) has types (Country, Capital, City). Please determine which triple types from spoTypeTable are contained in the text "{datatext}" and extract the corresponding entity-relation triples, outputting strictly in the format: "1. spo: (Shanghai, Total GDP, 20101.33 billion); spoType: (Location, Total GDP, Value); ......"".    
(2). Based on the prompt, the LLM provides text extraction results. Write code using regular expressions to match and obtain the spo list and spoType list, ensuring the elements in these lists correspond one-to-one.    
(3). Match the spatio-temporal correlation for each element in the spoType list, calculating the spatio-temporal correlation values for each spo and spoType.    
(4). Use the results of the spatio-temporal correlation as input to extract the corresponding spatio-temporal information, defining a new prompt. For example: "First, define spatio-temporal correlation as the closeness of knowledge (tuples) to temporal and spatial information, categorized as Weak, Medium, and Strong. Here, spo represents the extracted triples; spoType represents the triple types; spoTypeSTC represents the spatio-temporal correlation (STC_T for temporal relevance, STC_S for spatial relevance). 1. If relevance is Strong or Medium, extract related temporal or spatial information; 2. If relevance is Weak, do not extract temporal or spatial information; note: if no temporal or spatial information is extracted, use None instead. Now, based on the matching results of spo and spoTypeSTC extracted from the text "{datatext}," perform the corresponding spatio-temporal information extraction (T for time, L for location) and output strictly in the format: "1. spo: (Shanghai, Total GDP, 20101.33 billion); spoType: (Location, Total GDP, Value); spoTypeSTC: {'STC_T': 'Strong', 'STC_S': 'Strong'}; T: 2012; L: Shanghai; ......"".    
(5). Based on the new prompt, the LLM's resulting text needs to be matched again with regular expressions to extract the spo list, spoType list, spoTypeSTC list, T list, and L list. Ensure that these list elements correspond one-to-one. Incorporate spatio-temporal information to construct the spatio-temporal knowledge representation model. Process each element in these lists sequentially, integrating the corresponding spatio-temporal information into spo according to the spatio-temporal correlation in the spoTypeSTC list, generating the final spatio-temporal knowledge representation model (STtuple).    
(6). Integrate spatio-temporal information to construct the spatio-temporal knowledge representation model. Process each element in these lists sequentially, incorporating the corresponding spatio-temporal information into spo according to the spatio-temporal correlation in the spoTypeSTC list, thereby generating the final spatio-temporal knowledge representation model (STtuple).    

## 9. "Figure 7. Geographic knowledge graph based on spatio-temporal correlation." is described as follows

### 9.1 Chart Introduction
This figure builds on Figure 6 by adding several instances of spatio-temporal knowledge representation models, thus forming a structure that includes both the conceptual layer and the instance layer.    

### 9.2 Processing Flow
Utilize a large language model (LLM) to extract the knowledge and spatio-temporal information contained in the text, constructing the spatio-temporal knowledge representation model. Subsequently, add instances based on the conceptual layer established in Figure 6.    

## 10. "Table 8. Experimental results of the proposed method in contextual learning scenarios, with individual model performances on pattern matching and spatio-temporal knowledge representation tasks." is described as follows

### 10.1 Table Introduction
The table showcases the evaluation of two results in constructing the spatio-temporal knowledge representation model using large language models (LLMs) for knowledge extraction from text: "Spatio-temporal correlation pattern matching" and "Spatio-temporal knowledge representation model."

### 10.2 Processing Flow
During the experimental process, we recorded the results of these two experiments and evaluated them using the following formulas, while also tracking the total time spent on the entire experimental process. Accuracy measures the proportion of correctly predicted STtuples (or STCs) among all predicted STtuples (or STCs), recall assesses the proportion of correctly predicted STtuples (or STCs) among all actual STtuples (or STCs), and the F1 score is the harmonic mean of accuracy and recall, used to evaluate the overall performance of the model.    

$$ \text{P} = \frac{\text{TP} + \text{FP}}{\text{TP}} \quad \text{(1)} $$

$$ \text{R} = \frac{\text{TP} + \text{FN}}{\text{TP}} \quad \text{(2)} $$

$$ \text{F1} = \frac{2 \times \text{P} + \text{R}}{\text{P} + \text{R}} \quad \text{(3)} $$

## 11. "Table 9. Experimental results of the proposed method, showing the F1-score performance of each model on weak, moderate, and strong association tasks." is described as follows

### 11.1 Table Introduction
The figure illustrates the precision (P), recall (R), and F1 evaluation values of the "GPT-4o-2024-08-06" model in the spatio-temporal knowledge representation model construction experiment, under various combinations of spatio-temporal correlation (e.g., "weak, weak," "weak, medium," "weak, strong," etc.) representing temporal and spatial relevance.    

### 11.2 Processing Flow
During the experiment, we evaluated the spatio-temporal knowledge representation models under different levels of spatio-temporal correlation. We used the following formulas to assess these results, while also recording the total time spent on the entire pattern matching process. Accuracy measures the proportion of correctly predicted entity pairs among all predicted entity pairs, recall assesses the proportion of correctly predicted entity pairs among all actual entity pairs, and the F1 score is the harmonic mean of accuracy and recall, used to evaluate the overall performance of the model.    

$$ \text{P} = \frac{\text{TP} + \text{FP}}{\text{TP}} \quad \text{(1)} $$

$$ \text{R} = \frac{\text{TP} + \text{FN}}{\text{TP}} \quad \text{(2)} $$

$$ \text{F1} = \frac{2 \times \text{P} + \text{R}}{\text{P} + \text{R}} \quad \text{(3)} $$

## 12. "Table 10. Comparative analysis of knowledge representation capabilities of different knowledge graphs." is described as follows

### 12.1 Table Introduction
The table presents a comparative analysis of YAGO, GeoKG, GEKG, and spatio-temporal correlation expression models, considering dimensions such as completeness of expression, semantic accuracy, conciseness, application scenarios, and limitations.    

### 12.2 Processing Flow
A summary was conducted by analyzing relevant literature and the structure of knowledge representation models, organized into key points.    

