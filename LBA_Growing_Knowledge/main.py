import json
import pickle
import os
from pprint import pprint

import numpy as np
from transformers import AutoTokenizer, RobertaModel
from transformers import logging
import torch
import platform

from configs.load_configs import get_config_path
from get_feature.generate_sub_questions import get_sub_qa
from get_feature.get_attention_score import get_attention_score
from get_feature.get_grounded_frames import get_grounded_frames
from get_feature.load_data import get_data
from get_feature.get_knowledge_from_sg import get_knowledge
from get_feature.get_phrase_from_question import get_phrase_of_question


GPU_NUM = 0  # 원하는 GPU 번호 입력


def main():
    print('torch.cuda.is_available():', torch.cuda.is_available())

    device = torch.device(f'cuda:{GPU_NUM}' if torch.cuda.is_available() else 'cpu')
    torch.cuda.set_device(device)  # change allocation of current GPU

    config_path = get_config_path()

    balanced_qa, scene_graphs, idx2eng = get_data('test')

    grounded_knowledge = get_knowledge(qa=balanced_qa, scene_graphs=scene_graphs, idx2eng=idx2eng,
                                       save_path=config_path['grounded_knowledge_path'], overwrite=False, verbose=False)

    phrases = get_phrase_of_question(qa=balanced_qa,
                                     save_path=config_path['phrases_path'], overwrite=False, verbose=True)

    for i, question_id in enumerate(balanced_qa.keys()):
        if i>=2:
            break
        knowledge_sentences = grounded_knowledge[question_id]
        # phrases_sentences = phrases[question_id]
        phrases_sentences = [t[1] for t in phrases[question_id]]
        print('\n\nquestion_id         :', question_id)
        print('knowledge_sentences :')
        pprint(knowledge_sentences)
        print('phrases_sentences   :')
        pprint(phrases_sentences)
        attention_score = get_attention_score(knowledge_sentences=knowledge_sentences, phrases_sentences=phrases_sentences)
        print('attention_score:')
        print(attention_score)
        attention_score_average = torch.mean(attention_score, dim=0)
        print(attention_score_average, '<- average by column')
        uncertain_phrase_idx = torch.argmin(attention_score_average)
        print('uncertain_phrase_idx:', uncertain_phrase_idx)
        uncertain_phrases = phrases_sentences[uncertain_phrase_idx]
        print('uncertain_phrases:', type(uncertain_phrases), uncertain_phrases)

        # ChatCaptioner/Video_ChatCaptioner/generate_caption_msvd.py 을 참고해서
        # prompt 수정: uncertainty를 반영하게
        # uniform frame sampling 대신 question에 grounded된 scene graph에 포함된 frame만 선택하여
        # 해당 frame들에 대해 질문 생성하기

        frames, frames_for_visual_info, frame_id_list, frame_id_with_interval_list = \
            get_grounded_frames(scene_graphs, balanced_qa, config_path['charades_frame_path'],
                                question_id, #uncertain_phrases=None,
                                max_frames=5,
                                only_uncertain_frame=False, verbose=True)
        print('frame_id_list:', frame_id_list)
        print('frame_id_with_interval_list:', frame_id_with_interval_list)
        print('len(frames):', len(frames), type(frames))#, type(frames[0]))#'\t', 'frames[0].shape:', np.ndarray(frames[0]).shape)
        # print('frames:', np.array(frames[0]).shape)#, np.array(frames[0]))
        # for j, frame in enumerate(frames):
        #     print('j:', j, '\t', 'frame.shape:', np.array(frame).shape)
        #     print(np.array(frame))
        # print('frames_for_visual_info:', np.array(frames_for_visual_info[0]).shape)#, np.array(frames_for_visual_info[0]))

        questions, answers, total_tokens = get_sub_qa(model='gpt-3.5-turbo',
                                                      frames=frames,
                                                      frames_for_visual_info=frames_for_visual_info,
                                                      uncertain_phrase=uncertain_phrases,
                                                      frame_id_list=frame_id_list,
                                                      frame_id_with_interval_list=frame_id_with_interval_list,
                                                      n_questions=1,
                                                      max_gpt_token=30,
                                                      verbose=True)

        # print('questions:')
        # pprint(questions)
        # print('answers:')
        # pprint(answers)
        print('total_tokens:', total_tokens)



if __name__ == "__main__":
    main()

