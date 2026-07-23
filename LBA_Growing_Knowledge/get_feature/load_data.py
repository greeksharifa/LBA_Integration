import os
import json
import pickle

from transformers import AutoTokenizer, RobertaModel
from transformers import logging
import torch
import platform

from configs.load_configs import get_config_path

logging.set_verbosity_error()


def get_data(split='test'):
    config_path = get_config_path()
    # load data
    qa_path = config_path[f'{split}_qa_path']
    print('loading {:<25s}: {:<75s} ...'.format('qa', qa_path), end='')
    balanced_qa = json.load(open(qa_path, mode='r', encoding='utf8'))
    print('done. len is:', len(balanced_qa))

    sg_path = config_path[f'{split}_sg_path']
    print('loading {:<25s}: {:<75s} ...'.format('scene_graphs', sg_path), end='')
    scene_graphs = pickle.load(open(sg_path, mode='rb'))
    print('done. len is:', len(scene_graphs))

    idx_path = config_path['idx2eng_path']
    print('loading {:<25s}: {:<75s} ...'.format('idx2eng', idx_path), end='')
    idx2eng = json.load(open(idx_path, mode='r', encoding='utf8'))
    print('done. len is:', len(idx2eng))

    return balanced_qa, scene_graphs, idx2eng


if __name__ == "__main__":
    OS = platform.system()
    print('OS:', OS)
    ROOT_DIR = 'data/AGQA/' if OS == 'Windows' else '/home/ywjang/data/AGQA/'
    os.makedirs(ROOT_DIR + 'features/', exist_ok=True)
