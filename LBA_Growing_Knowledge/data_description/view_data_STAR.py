import pickle
from pprint import pprint
import os
import json
import sys
import platform

OS = platform.system()
ROOT_DIR = 'data/STAR_Benchmark/' if OS == 'Windows' else '~/data/STAR_Benchmark/'

# Questions, Answers and Situation Graphs
# STAR_train/val/test.json, split_file.json

# Question-Answer Templates and Programs
# QA_templates.csv: Question Templates csv. 20행
# QA_programs.csv : QA Programs csv.        20행

# Situation Video Data
# Video_Segments.csv    : header: question_id, video_id, start, end.                   총 60206개
# Video_Keyframe_IDs.csv: header: question_id, video_id, Keyframe_IDs(situation keys). 총 60206개
# 1개의 q당 평균적으로 22개의 situation
Interaction_T1_13_situation_keys = [
    '000198', '000202', '000205', '000206', '000212', '000217', '000218', '000221', '000223', '000236', '000240',
    '000242', '000243', '000245', '000247', '000257', '000267', '000269', '000270', '000272', '000274', '000275',
    '000286', '000289', '000294', '000301', '000303', '000308', '000313', '000314', '000316', '000318', '000320',
    '000322', '000331', '000332', '000336', '000337', '000339'
]
def view_STAR_split_json():
    split = 'val'
    STAR_val = json.load(open(ROOT_DIR + f'STAR_{split}.json', mode='r', encoding='utf8'))
    pprint(STAR_val[0])
    """
    {
     "question_id": "Interaction_T1_13",
     "question": "Which object was tidied up by the person?",
     "video_id": "6H78U",
     "start": 11.1,
     "end": 19.6,
     "choices": [{"choice": "The closet/cabinet.",
                  "choice_id": 0,
                  "choice_program": [{"function": "Equal",
                                      "value_input": ["closet/cabinet"]}]},
                 {"choice": "The blanket.",
                  "choice_id": 1,
                  "choice_program": [{"function": "Equal",
                                      "value_input": ["blanket"]}]},
                 {"choice": "The clothes.",
                  "choice_id": 2,
                  "choice_program": [{"function": "Equal",
                                      "value_input": ["clothes"]}]},
                 {"choice": "The table.",
                  "choice_id": 3,
                  "choice_program": [{"function": "Equal",
                                      "value_input": ["table"]}]}],
     "answer": "The clothes.",
     "question_program": [{"function": "Situations", "value_input": []},
                          {"function": "Actions", "value_input": []},
                          {"function": "Filter_Actions_with_Verb",
                           "value_input": ["tidy"]},
                          {"function": "Unique", "value_input": []},
                          {"function": "Query_Objs", "value_input": []}],
     "situations": {"000198": {"actions": ["a004", "a002"],
                               "bbox": [[113.9, 270.28, 169.28, 303.74],
                                        [254.22, 34.15, 318.76, 467.99]],
                               "bbox_labels": ["o019", "o000"],
                               "rel_labels": ["r003"],
                               "rel_pairs": [["o000", "o019"]]},

                               ...,

                    "000339": {"actions": ["a004", "a056", "a001"],
                               "bbox": [[141.44, 161.96, 198.31, 211.96],
                                        [139.1, 162.63, 197.93, 211.75],
                                        [141.64, 161.2, 199.14, 212.7],
                                        [158.54, 17.52, 303.67, 458.43]],
                               "bbox_labels": ["o027", "o019", "o004", "o000"],
                               "rel_labels": ["r009",
                                              "r002",
                                              "r009",
                                              "r002",
                                              "r009",
                                              "r002"],
                               "rel_pairs": [["o000", "o027"],
                                             ["o000", "o027"],
                                             ["o000", "o019"],
                                             ["o000", "o019"],
                                             ["o000", "o004"],
                                             ["o000", "o004"]]}},
    }
    """
# Raw Videos from Charades(scaled to 480p) mp4
# Keyframe Dumping Tool from Action Genome

# Annotations
# Classes Files zip
# Object Bounding Boxes pkl
# Human Poses zip
# Human Bounding Boxes pkl
def view_person_bbox_pkl():
    person_bbox = pickle.load(open(ROOT_DIR + 'person_bbox.pkl', mode='rb'))
    # len: 288782
    type(person_bbox)
    person_bbox.keys()
    key = next(iter(person_bbox))
    print(key)
    pprint(person_bbox[key])
    """
    {
    'bbox': array([[ 24.29774 ,  71.443954, 259.23602 , 268.20288 ]], dtype=float32),
    'bbox_mode': 'xyxy',
    'bbox_score': array([0.9960979], dtype=float32),
    'bbox_size': (480, 270),
    'keypoints': array([[
        [149.51952 , 120.54931 ,   1.      ],
        [146.48587 , 111.43697 ,   1.      ],
        [141.09274 , 115.824394,   1.      ],
        [111.76759 , 123.58676 ,   1.      ],
        [112.44173 , 124.26174 ,   1.      ],
        [ 82.10537 , 154.6362  ,   1.      ],
        [113.45295 , 168.47343 ,   1.      ],
        [153.56436 , 207.96022 ,   1.      ],
        [162.66527 , 247.44699 ,   1.      ],
        [146.48587 , 149.91127 ,   1.      ],
        [216.59659 , 229.22232 ,   1.      ],
        [112.10466 , 243.73456 ,   1.      ],
        [163.3394  , 267.69662 ,   1.      ],
        [237.83205 , 202.56032 ,   1.      ],
        [239.18031 , 202.56032 ,   1.      ],
        [186.93436 , 219.0975  ,   1.      ],
        [220.9785  , 227.87234 ,   1.      ]]], dtype=float32),
    'keypoints_logits': array([[
        11.073427  , 10.578527  , 10.863391  ,  3.6263876 , 11.451177  ,
         4.500312  ,  6.419147  ,  3.4865067 ,  7.920906  ,  5.6766253 ,
         9.343614  , -0.7024717 , -0.36381796,  1.039403  ,  1.1701871 ,
        -0.03817523, -2.2913933 ]], dtype=float32)}
    """
def view_object_bbox_and_relationship_pkl():
    object_bbox_and_relationship = pickle.load(open(ROOT_DIR + 'object_bbox_and_relationship.pkl', mode='rb'))
    # len: 288782
    type(object_bbox_and_relationship)
    object_bbox_and_relationship.keys()
    key = next(iter(object_bbox_and_relationship))
    print(key)
    pprint(object_bbox_and_relationship[key])
    """
    '001YG.mp4/000089.png': 
    [
        {
            'attention_relationship': ['unsure'],
            'bbox': (222.10317460317458, 143.829365079365, 257.77777777777777, 101.11111111111109),
            'class': 'table',
            'contacting_relationship': ['not_contacting'],
            'metadata': {'set': 'train', 'tag': '001YG.mp4/table/000089'},
            'spatial_relationship': ['in_front_of'],
            'visible': True
        },
        {
            'attention_relationship': ['not_looking_at'],
            'bbox': (56.34126984126985, 179.16666666666663, 192.77777777777777, 90.56890211160798),
            'class': 'chair',
            'contacting_relationship': ['sitting_on', 'leaning_on'],
            'metadata': {'set': 'train', 'tag': '001YG.mp4/chair/000089'},
            'spatial_relationship': ['beneath', 'behind'],
            'visible': True
        }
    ]
    """