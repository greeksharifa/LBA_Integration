from pprint import pprint
from typing import List

import numpy as np
import openai
import os, sys

from PIL.Image import Image

from get_feature.utils_from_VideoChatCaptioner import get_chat_log, prepare_chatgpt_message, call_chatgpt, find_digit, \
    prepare_short_chatgpt_message

from ChatCaptioner.Video_ChatCaptioner.chatcaptioner.blip2 import Blip2
# from ChatCaptioner.Video_ChatCaptioner.chatcaptioner.video_chat import get_chat_log, prepare_chatgpt_message, \
#     call_chatgpt, find_digit

openai.api_key = os.getenv('OPENAI_API_KEY')

# TODO: QUESTION_INSTRUCTION prompt 수정하기
QUESTION_INSTRUCTION= \
"You are an Agent Assistant. " \
"You have to assist an agent who needs to answer questions about a video. " \
"That agent is currently unsure about '%s'. " \
"You have to generate a question to find out meaning of '%s'. " \
"The answer will be given by another expert. " \
"The video contains %s frames. " \
"Agent Assistant CAN NOT ask question from the frame with the index MORE THAN %s. " \
"The descriptions for some frames are each given in the format of Frame_id: description. "

'''
당신은 Agent Assistant이다.
비디오를 보고 그 비디오에 대한 질문에 답해야 하는 agent를 도와야 한다.
그 agent는 지금 {uncertain phrase}에 대해 잘 모른다.
이를 해소하기 위한 질문을 생성해야 한다.
답변은 다른 전문가가 해 줄 것이다.
질문: 
'''

# TODO: restrictions 수정하기
SUB_QUESTION_INSTRUCTION = \
"Action: ask more questions to find out meaning of '%s'." \
"Goal: Agent Assistant will design a frame sampling strategy to ask questions to maximize its information gain about the meaning of '%s'. " \
"Restrictions: (1) Agent Assistant MUST ask questions from Frame 1 to Frame %s. (2) Agent Assistant CAN NOT ask questions with person or objects or animals NOT mentioned in previous conversation." \
"Next Question. The question format MUST be Frame_id: question. AVOID asking yes/no questions. Try to ask questions about as many different frames as possible." \
"Agent Assistant Question: "

# TODO: SUB_QUESTION_INSTRUCTION_ALTERNATIVE 수정하기
SUB_QUESTION_INSTRUCTION_ALTERNATIVE = SUB_QUESTION_INSTRUCTION.replace(
"Next Question. The question format MUST be Frame_id: question. AVOID asking yes/no questions. Try to ask questions about as many different frames as possible.",
"Next Question. The question format MUST be Frame_id: question. Ask the question from the frame %s. AVOID asking yes/no questions. Try to ask questions about as many different frames as possible."
)


QUESTION_INSTRUCTION_FOR_VISUAL_INFO = 'Frame_%d: Describe it in details.'

# TODO: ANSWER_INSTRUCTION prompt 수정하기
ANSWER_INSTRUCTION = 'Answer given questions with the following restrictions. (1) If you are not sure about the answer, say you DO NOT KNOW honestly.  (2) DO NOT IMAGINE any contents that are NOT in the image. '

SUB_ANSWER_INSTRUCTION = 'Answer: '  # template following blip2 huggingface demo


VALID_CHATGPT_MODELS = ['gpt-3.5-turbo']
# VALID_GPT3_MODELS = ['text-davinci-003', 'text-davinci-002', 'davinci']


blip2s = {
    # 'FlanT5 XXL': Blip2('FlanT5 XXL', device_id=sys.argv[1], bit8=True)
    'FlanT5 XXL': Blip2('FlanT5 XXL', device_id=0, bit8=True)
}


def get_VideoChatCaptioner_chat_log_for_visual_info(frames_for_visual_info: List[Image],
                                                    n_blip2_context:int=0,
                                                    verbose:bool=False):
    """
    This function generates a chat log like VideoChatCaptioner, but 1 FIRST_QUESTION per 1 frame.
    :param frames_for_visual_info:
    :param n_blip2_context:
    :param verbose:
    :return:
    """
    questions = []
    answers = []
    blip2 = blip2s['FlanT5 XXL']

    if verbose:
        print('--------Chat like VideoChatCaptioner Starts----------')

    for i, frame in enumerate(frames_for_visual_info):
        question = QUESTION_INSTRUCTION_FOR_VISUAL_INFO % (i + 1)

        questions.append(question)

        # prepare the context for blip2
        blip2_prompt = '\n'.join([ANSWER_INSTRUCTION,
                                  get_chat_log(questions, answers, last_n=n_blip2_context),
                                  SUB_ANSWER_INSTRUCTION])

        answer = blip2.ask(frame, blip2_prompt)
        # small blip2 models may ask itself a new bad question. remove it and trim the answer
        answer = answer.split('Question:')[0].replace('\n', ' ').strip()
        answers.append(answer)

        if verbose:
            print('GPT-3  (round {:2d}) {}'.format(i+1, question))
            print('BLIP-2 (round {:2d}) {}'.format(i+1, answer))

    if verbose:
        print('--------Chat like VideoChatCaptioner Ends------------')

    return questions, answers


def get_sub_qa(model:str, frames: List, frames_for_visual_info: List, uncertain_phrase:str,
               n_questions:int, max_gpt_token:int,
               frame_id_list: List, frame_id_with_interval_list:List,
               n_blip2_context:int=0, max_frame_number:int=1000, verbose:bool=False):
    # This function generates questions about the uncertain phrase.

    # TODO: frames 수정하기
    # frames = grounded_frames['frames']
    frames = frames[:max_frame_number]
    questions, answers = get_VideoChatCaptioner_chat_log_for_visual_info(frames_for_visual_info,
                                                                         n_blip2_context=0, verbose=verbose)
    total_tokens = 0
    blip2 = blip2s['FlanT5 XXL']

    N = str(len(frames))
    # M = str(len(frames_for_visual_info))

    question_instruction_adapt = QUESTION_INSTRUCTION % (uncertain_phrase, uncertain_phrase, N, N)
    sub_question_instruction_adapt = SUB_QUESTION_INSTRUCTION % (uncertain_phrase, uncertain_phrase, N)

    if verbose:
        print('--------Generate sub-questions Starts----------')

    current_frame_id = 1
    round_number = 1
    while n_questions > 0:
        tag = True
        chatgpt_messages = prepare_short_chatgpt_message(
            question_instruction_adapt,
            questions, answers,
            sub_question_instruction_adapt,
            frame_id_list, frame_id_with_interval_list,
        )
        if n_questions == 1:
            print('chatgpt_messages:')
            pprint(chatgpt_messages)
        question, n_tokens = '', 0
        while tag:
            try:
                question, n_tokens = call_chatgpt(chatgpt_messages, model=model, max_tokens=max_gpt_token)
                frame_id = int(find_digit(question.split(":")[0])) - 1

                if question.startswith("Frame_") and frame_id < max_frame_number:
                    tag = False
            except Exception as e:
                print('Exception:', e)
                if current_frame_id >= max_frame_number - 1:
                    hard_coded_frame_id = 1
                else:
                    hard_coded_frame_id = current_frame_id + 1

                sub_question_instruction_alternative_adapt = SUB_QUESTION_INSTRUCTION_ALTERNATIVE % \
                                                             (uncertain_phrase, uncertain_phrase, N, str(hard_coded_frame_id))
                chatgpt_messages = prepare_chatgpt_message(
                    question_instruction_adapt,
                    questions, answers,
                    sub_question_instruction_alternative_adapt
                )
                # print(question)

            total_tokens = total_tokens + n_tokens

        question = question.split('Question: ')[-1].replace('\n', ' ').strip()
        if 'Answer:' in question:  # Some models make up an answer after asking. remove it
            q, a = question.split('Answer:')[:2]
            if len(q) == 0:  # some not so clever models will put the question after 'Answer:'.
                question = a.strip()
            else:
                question = q.strip()

        # prepare the context for blip2
        blip2_prompt = '\n'.join([ANSWER_INSTRUCTION,
                                  get_chat_log(questions, answers, last_n=n_blip2_context),
                                  SUB_ANSWER_INSTRUCTION])

        # frame_id = question.split(":")[0].split(" ")[1]
        current_frame_id = int(find_digit(question.split(":")[0]))

        current_frame = frames[current_frame_id - 1]
        answer = blip2.ask(current_frame, blip2_prompt)
        # small blip2 models may ask itself a new bad question. remove it and trim the answer
        answer = answer.split('Question:')[0].replace('\n', ' ').strip()
        if answer == 'DO NOT KNOW':
            pass
        else:
            n_questions -= 1
            questions.append(question)
            answers.append(answer)

        if verbose:
            print('GPT-3  (round {:2d}) {}'.format(round_number, question))
            print('BLIP-2 (round {:2d}) {}'.format(round_number, answer))

        # blip2_prompt = '{} {}'.format(blip2_prompt, answer)
        round_number += 1

    if verbose:
        print('--------Generate sub-questions Ends------------')

    return questions, answers, total_tokens


