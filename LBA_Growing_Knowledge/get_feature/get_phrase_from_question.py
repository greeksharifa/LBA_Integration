import json

import spacy
import os
from pprint import pprint

from configs.load_configs import get_config_path
from get_feature.load_data import get_data

# Load the English language model
nlp = spacy.load("en_core_web_sm")


def get_phrase_of_question(qa:dict, save_path=None, overwrite:bool=False, verbose:bool=False) -> dict:
    """
    return the phrases and its indices of question.
    :param qa: QnA dict
    :param save_path: directory path to save phrases dict
    :param overwrite: overwrite json file to save_path
    :param verbose: if true, print {question_id: list of phrases} per 10000 questions
    :return: phrases: dir. {question_id: [
                                            (start_idx, end_idx),
                                            phrase
                                         ]
                            , ...}
    """

    if not overwrite and save_path is not None and os.path.isfile(save_path):
        print('loading {:<25s}: {:<75s} ...'.format('phrases_path', save_path), end='')
        with open(save_path, 'r', encoding='utf8') as f:
            phrases = json.load(f)
    else:
        print('creating {:<25s}: {:<75s} ...'.format('phrases_path', save_path))

        phrases = {}
        for i, (question_id, value) in enumerate(qa.items()):
            # if i > 5: break
            question = value["question"]

            doc = nlp(question)     # Parse the sentence with spaCy
            phrases[question_id] = []

            if verbose and i % 10000 == 0:
                print('\nquestion:', question_id, question)

            for token in doc:
                if len([child for child in token.children]) != 0:
                    phrase = ' '.join([str(t) for t in token.subtree])
                    phrases[question_id].append(
                        ((token.idx, token.idx + len(phrase)),
                        phrase)
                    )

                    if verbose and i % 10000 == 0:
                        print('{:<15s} | {:3d}-{:3d} | '.format(token.text, token.idx, token.idx + len(phrase), phrase))

        if save_path:
            with open(save_path, 'w', encoding='utf8') as f:
                json.dump(phrases, f)

    print('done. len is:', len(phrases))

    return phrases


def main():
    config_path = get_config_path()

    balanced_qa, scene_graphs, idx2eng = get_data('test')
    phrases = get_phrase_of_question(qa=balanced_qa,
                                     save_path=config_path['phrases_path'], overwrite=False, verbose=True)


if __name__ == "__main__":
    main()
    """
    question: 'YSKX3-8': Were they interacting with a blanket while holding a pillow?
    
    interacting     |  Were they interacting with a blanket while holding a pillow ?
    with            |  with a blanket
    blanket         |  a blanket
    holding         |  while holding a pillow
    pillow          |  a pillow
    
    {'YSKX3-11': ['Is there a pillow the person interacts with after tidying up a blanket ?',
              'a pillow the person interacts with',
              'the person',
              'the person interacts with',
              'after tidying up a blanket',
              'tidying up a blanket',
              'a blanket'],
    'YSKX3-13': ['Were they interacting with a pillow ?',
              'with a pillow',
              'a pillow'],
    'YSKX3-461': ['Was the person holding the first thing they touched ?',
               'the person holding the first thing they touched',
               'holding the first thing they touched',
               'the first thing they touched',
               'they touched'],
    'YSKX3-524': ['the person',
               'Was the person tidying the object they were in front of ?',
               'the object they were in front of',
               'they were in front of',
               'in front of',
               'front of'],
    'YSKX3-8': ['Were they interacting with a blanket while holding a pillow ?',
             'with a blanket',
             'a blanket',
             'while holding a pillow',
             'a pillow'],
    'YSKX3-9': ['Was a blanket one of the things they were interacting with ?',
             'a blanket',
             'one of the things they were interacting with',
             'of the things they were interacting with',
             'the things they were interacting with',
             'they were interacting with']}
    
    """
