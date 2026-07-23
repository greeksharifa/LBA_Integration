from transformers import AutoTokenizer, RobertaModel
import os
import json

from configs.load_configs import get_config_path
from get_feature.load_data import get_data

def get_knowledge(qa:dict, scene_graphs:dict, idx2eng:dict, save_path=None, overwrite:bool=False, verbose:bool=False) -> dict:
    """
    return sg_grounded knowledge dict per questions
    :param qa: [un]balanced_qa.txt
    :param scene_graphs: AGQA scene_graphs
    :param idx2eng: ENG.txt -> {"o1": "person", ...}
    :param save_path: directory path to save knowledge dict
    :param overwrite: overwrite json file to save_path
    :param verbose: if true, print {question_id: word_list} per 10000 questions
    :return: grounded_knowledge:dict = {question_id: word_list}
    """
    print('loading {:<25s}: {:<75s} ...'.format('grounded_knowledge', save_path), end='')

    if not overwrite and save_path is not None and os.path.isfile(save_path):
        with open(save_path, 'r', encoding='utf8') as f:
            grounded_knowledge = json.load(f)
    else:
        grounded_knowledge = {}
        for i, (question_id, value) in enumerate(qa.items()):
            # if i > 5:
            #     break
            word_list = []
            sg_grounding = value["sg_grounding"]
            video_id = value["video_id"]
            for idxs, sg_key_list in sg_grounding.items():  # "37-59": ["000247", "000252", ..., "000270"]},
                if len(sg_key_list) == 0:
                    continue
                for sg_key in sg_key_list:
                    # print('sg_key:', sg_key)
                    sg = scene_graphs[video_id][sg_key]
                    if 'verb' not in sg.keys():  # sg['type'] not in ['frame', 'act', 'object']
                        continue
                    verbs = sg['verb']
                    # print(type(verbs))
                    if type(verbs) is list:
                        for verb in verbs:
                            word_list.append(idx2eng[verb['class']])
                    else:
                        word_list.extend(list(map(lambda x: idx2eng[x], verbs['names'])))

            word_list = set(word_list)
            grounded_knowledge[question_id] = list(word_list)

            if verbose and i % 10000 == 0:
                print('question_id:', question_id)
                print('word_list:', word_list)
                print()

        if save_path:
            with open(save_path, 'w', encoding='utf8') as f:
                json.dump(grounded_knowledge, f)

    print('done. len is:', len(grounded_knowledge))

    return grounded_knowledge


def main():

    tokenizer = AutoTokenizer.from_pretrained("roberta-base")
    model = RobertaModel.from_pretrained("roberta-base")

    inputs = tokenizer("This is a sample input text.", return_tensors="pt")
    print('inputs:', inputs)
    outputs = model(**inputs)
    # outputs.__dict__.keys()
    # ['last_hidden_state', 'pooler_output', 'hidden_states', 'past_key_values', 'attentions', 'cross_attentions']

    last_hidden_states = outputs.last_hidden_state
    print(last_hidden_states.shape, '\n', last_hidden_states)

    # ----------------------------------------------------------------------------------------------------------------

    config_path = get_config_path()

    balanced_qa, scene_graphs, idx2eng = get_data('test')
    grounded_knowledge = get_knowledge(qa=balanced_qa, scene_graphs=scene_graphs, idx2eng=idx2eng,
                                       save_path=config_path['grounded_knowledge_path'], overwrite=False, verbose=True)


if __name__ == "__main__":
    main()

# list(map(lambda x: x['type'], sg['verb']))
