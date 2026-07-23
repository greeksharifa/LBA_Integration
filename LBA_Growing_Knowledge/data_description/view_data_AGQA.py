import pickle
from pprint import pprint
import os
import json
import sys
import platform

OS = platform.system()
ROOT_DIR = 'data/AGQA/' if OS == 'Windows' else '~/data/AGQA/'

"""
AGQA2.0 dataset이 제일 최신 데이터이다.
순서:
- AGQA2.0 , and Google Drive data
- AGQA Benchmark with programs and scene graphs(includes the additional program and scene graph data)
- AGQA Benchmark(version of the benchmark that has the baseline results published in CVPR 2021)
"""

def view_scene_graphs(split: str = 'train'):
    """
    from AGQA paper: Suppl 6.2 (page 13)
    Action Genome’s spatio-temporal scene graphs [19] annotate five sampled frames from each Charades action [47].
    Each frame contains object annotations with lists of the contact, spatial, and attention relationships
        between the subject and the object [19].
    We generate questions and answers based on these spatio-temporal scene graphs.
    Inaccurate or incomplete scene graph data can lead to uninformative and incorrect question generation.
    Since the scene graph annotations in Action Genome are often noisy, inconsistent, and sparse,
        we augment them using the following techniques to minimize errors:
        Duplication, Inconsistency, Sparsity, Entailments, Uncertainty in action localization.
    -----------------------------------------------------------------------------------------------
    from Action Genome paper: 2. Related Work (page 3)
    Action Genome’s annotation pipeline: For every
    action, we uniformly sample 5 frames across the action and
    annotate the person performing the action along with the
    objects they interact with. We also annotate the pairwise
    relationships between the person and those objects. Here,
    we show a video with 4 actions labelled, resulting in 20
    (= 4 × 5) frames annotated with scene graphs. The objects
    are grounded back in the video as bounding boxes.
    -----------------------------------------------------------------------------------------------
    Github Issues: https://github.com/madeleinegrunde/AGQA_baselines_code/issues/6
    The structure is quite different from Action Genome. I cover the structure of these scene graphs in the README
    (at the bottom). We changed the structure to make it easier to use to generate questions.
    We also augmented the annotations using the strategies outlined in sections 3.1 and 6.2 of our paper.
    Some of the ways the updated structure helps us are:
        - We made relationships their own nodes in the scene graph, so we could reason about them independently and
            create questions like "What were they holding?"
        - We added actions as nodes. Since we combined the Charades and Action Genome data, we could not just rely on
            having object nodes as Action Genome does. Therefore, we also had nodes for Charades action annotations.
        - When answering the questions programmatically, it was helpful to have pointers to the next and previous
            instances of that particular relationship or object. The original Action Genome dataset does not have
            those pointers.

    We do not use attention relationships in the questions we generate, but they may remain in the scene graphs.
    from AGQA paper : Finally, we remove all attention relationships (e.g. looking at) from Action Genome’s annotations
        because our human evaluations indicated that evaluators were unable to accurately discern the actor’s gaze.

    포인터(refernence)를 그냥 그대로 달아놓아서 node가 그대로 붙어 있는 것처럼 보인다. 그래서 json으로 저장할 수 없고 pickle로만 가능.

    Q: The train-balanced-tgif.csv question files used for training has different format for each entry compared to the
        train_balanced.txt question file format stated in the README files, what is the reason behind this?
    A: The .csv file is formatted to have the correct headings needed to work with the models. It also does not include
        much information about each question (for example the program or scene graph grounding).
        This new format functioned to make it consistent with the data structure originally used for HCRN, HME, and PSAC
        , without including extra information it would take a while to upload wherever you run your models.
        The question content, answers, and ids will be the same.
    -----------------------------------------------------------------------------------------------

    test key: len=1814, dict_keys(['YSKX3', 'T5ECU', 'AAH6R', '015XE', ..., 'LSKA2'])

    scene graph의 각 key(=vid)마다 type별로 들어가 있는 정보가 다름.
    ex. scene_graphs['YSKX3']의 key로는 '000105', 'c077/1', 'o4/000105', 'r1/000105', 'v025/000270' 등이 있음.
    '000105'는 현 vid(video)에 포함되는 frame id,
    'o4/000105', 'r1/000105', 'v025/000270'는 해당 frame에 나타나는 object, relation(attention or verb),
    'c077/1'는 action을 의미함. '/' 뒤의 숫자는 현재 vid에서 몇 번째 'c077' action인지를 나타냄. '1': 15918, '2': 219, '3': 12개

        scene_graphs['YSKX3']['000105']['type']         : 'frame'
            ['id', 'secs', 'type', 'metadata', 'objects', 'attention', 'contact', 'spatial', 'verb', 'actions', 'next', 'prev']
        scene_graphs['YSKX3']['c077/1']['type']         : 'action'
            ['id', 'charades', 'phrase', 'type', 'start', 'end', 'length', 'objects', 'attention', 'contact', 'spatial',
            'verb', 'metadata', 'all_f', 'object_id', 'verb_id',
            'next_discrete', 'prev_discrete', 'next_instance', 'prev_instance', 'while']
        scene_graphs['YSKX3']['o4/000105']['type']      : 'object'
            ['id', 'type', 'class', 'attention', 'contact', 'spatial', 'verb', 'visible', 'bbox', 'metadata',
            'frame_num', 'secs', 'next', 'prev']
        scene_graphs['YSKX3']['r1/000105']['type']      : 'attention'
            ['id', 'type', 'class', 'objects', 'metadata', 'frame', 'secs', 'next', 'prev']
        scene_graphs['YSKX3']['v025/000270']['type']    : 'verb'
            ['id', 'type', 'class', 'objects', 'metadata', 'frame', 'secs', 'next', 'prev']


    type: key가 각각
        frame       = "숫자6자리"
        action      = "c.../X"
        object      = "o.../숫자6자리"
        attention   = "r.../숫자6자리"
        verb        = "v.../숫자6자리"

    example)
    key(frame id) = 'YSKX3'
    value: dict{
        '000105'(=frame_id): {
            id        (<class 'str'>       ) : '000105',
            secs      (<class 'float'>     ) : 6.3,
            type      (<class 'str'>       ) : 'frame',
            metadata  (<class 'str'>       ) : 'test',    test / train
            objects   (<class 'dict'>      ) : [connecting object nodes]
            {
                'names'(<class 'list'>     ) : ['o4'], (=blanket)
                'vertices'(<class 'list'>  ) : len 1 [
                    이 frame과 연관된 objects(type: dict)를 그냥 reference해서 넣어두었다...
                ]
            }
            attention (<class 'dict'>      ) : [connecting attention nodes].    names: ['r1']    'looking at'
            contact   (<class 'dict'>      ) : [connecting contact nodes].      names: ['r22']   'touching'
            spatial   (<class 'dict'>      ) : [connecting spatial nodes].      names: ['r7']    'behind'
            verb      (<class 'dict'>      ) : [connecting verb nodes].         names: ['v026']  'tidying'
            actions   (<class 'dict'>      ) : [connecting action nodes].       names: ['c075']  'tidying up a blanket'
            next      (<class 'dict'>      ) : next frame or None.              names: ['r1']    'looking at'
            prev      (<class 'dict'>      ) : previous frame or None.          None
        },
        '000134': {...},
        '000163': {...},
        ...,
        'c077/1': {...}, ...,                       # "c077": "putting a pillow somewhere"
        'o4/000105': {...}, ...,                    # "o4"  : "blanket"
        'r1/000105': {...}, ...,                    # "r1"  : "looking at"
        'v025/000270': {...}                        # "v025": "throwing",       "v026": "tidying",
    }
    :param split: 'train' or 'test'
    :return: None
    """
    # split = 'test'
    scene_graphs = pickle.load(open(ROOT_DIR + f'AGQA_scene_graphs/AGQA_{split}_stsgs.pkl', mode='rb'))
    key = next(iter(scene_graphs.keys()))
    value = next(iter(scene_graphs.values()))
    # print(type(value['000105']['id'])) # str
    # print(value['000105']['objects'].keys())

    for k in value['000105'].keys():
        print('{:<10s}({:<20s}) : '.format(k, str(type(value['000105'][k]))))

    for i, (key, value) in enumerate(scene_graphs.items()):
        if i > 0:
            break
        pprint(key)
        print(type(value))
        # pprint(value) circular reference 때문에 무조건 print함수의 memoryError로 터진다.

    from collections import Counter
    counter = Counter()
    for vid in scene_graphs.keys():
        for k in scene_graphs[vid].keys():
            if 'c' in k:
                counter[k[-1]] += 1
                # print(vid, k)
    print(counter)

def view_AGQA2_AGQA_balanced(split: str = 'train'):
    split = 'test'
    balanced_qa = json.load(open(ROOT_DIR + f'AGQA2/AGQA_balanced/{split}_balanced.txt', mode='r', encoding='utf8'))
    print(len(balanced_qa.keys()))  # test: 669207
    # key = next(iter(balanced_qa.keys()))
    # value = next(iter(balanced_qa.values()))
    # print('len(key:', key)
    # print('len(value):', len(value))
    '''
    {"YSKX3-8": {
        "question": "Were they interacting with a blanket while holding a pillow?", 
        "answer": "no", 
        "video_id": "YSKX3", 
        "global": ["exists"], 
        "local": "yes-no-o4-while-c076", 
        "ans_type": "binary", 
        "steps": 3, 
        "semantic": "object", 
        "structural": "verify", 
        "novel_comp": 0, 
        "more_steps": 0, 
        "program": "Exists(blanket, Iterate(Localize(while, holding a pillow), Filter(frame, [objects])))", 
        "sg_grounding": {
            "27-36": [], 
            "43-59": ["c076/1"], 
            "37-59": ["000247", "000252", "000254", "000258", "000268", "000269", "000270"]}, 
        "nc_seq": 0, "nc_sup": 0, "nc_dur": 0, "nc_objrel": 0, 
        "indirect": 1, "i_obj": 0, "i_rel": 0, "i_act": 0, "i_temp": 1, 
        "direct_equiv": "YSKX3-9"
    }, ...}
    
    {
        'question_id': {
            'question': 'Did they contact a blanket?', 
            'answer': 'No', 
            'video_id': 'YSKX3', 
            'global': ['exists', 'obj-rel'],
            'local': 'yes-no-o4', 
            'ans_type': 'binary',
            'steps': 1,
            'semantic': 'object',
            'structural': 'verify',
            'novel_comp': 0,
            'more_steps': 0,
            'sg_grounding': {(start char, end char): [scene graph vertices]},
            'program': 'program string',
        }
    }
    We handcraft 269 natural language question frames that can be answered from a set of 28 programs.
    
    Our 28 templates generate AGQA’s question-answer
pairs (Table 14). Each template has multiple natural language
options that can be filled with scene graph information
to create a diverse set of questions (Figure 10).
    The templates are also each associated with a program that automatically generates the answer 
    to questions using the spatio-temporal scene graph. 
    '''


def view_AGQA2_CSV_formatted_questions_for_evaluation_csvs():
    """
    train : 1,600,894
    test  :   669,207
    total : 2,270,101
    
    이유는 모르겠지만 train, test, total 전부 description이 'none'임
    그리고 train은 id가 1441052+159842개가 나누어져 있음
    test:
            ,key,       question,                                                   answer,vid_id,gif_name,description
    0,00607-10552,Which object were they tidying before taking the thing they put down from somewhere?,table,00607,00607,none
    1,00607-11002,Did the person interact with the thing they held before or after tidying up the first thing they went in front of?,after,00607,00607,none
    ...
    669206,ZZ4GP-1266,What was the person tidying before holding the thing they took?,floor,ZZ4GP,ZZ4GP,none

    그리고, 'data/AGQA2/CSV_formatted_questions_for_evaluation_csvs/balanced/Test_frameqa_question-balanced.csv' 파일은
            'data/AGQA2/AGQA_balanced/test_balanced.txt' 파일과 같은 질문들을 담고 있음.
        하지만, test_balanced.txt에는 scene graph grounding 등 더 많은 정보들이 포함되어 있음.
        csv 파일은 순수하게 testing question을 위한 것임.
            csv header가 [,key,question,answer,vid_id,gif_name,description]만 존재함.
        'data/AGQA2/CSV_formatted_questions_for_evaluation_csvs/balanced/` 말고 다른 폴더(decomp/, novel compositions/ 등)
        도 역시 세팅만 다를 뿐 csv header가 [,key,question,answer,vid_id,gif_name,description]만 존재

    :return: None
    """



if __name__ == '__main__':
    # view_scene_graphs('test')
    view_AGQA2_AGQA_balanced('test')
