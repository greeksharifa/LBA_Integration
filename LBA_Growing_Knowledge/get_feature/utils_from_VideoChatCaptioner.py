import re

import openai
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)  # for exponential backoff


def get_chat_log(questions, answers, last_n=-1):
    n_addition_q = len(questions) - len(answers)
    assert (n_addition_q) in [0, 1]
    template = 'Question: {} \nAnswer: {} \n'
    chat_log = ''
    if last_n > 0:
        answers = answers[-last_n:]
        questions = questions[-(last_n + n_addition_q):]
    elif last_n == 0:
        answers = []
        questions = questions[-1:] if n_addition_q else []

    for i in range(len(answers)):
        chat_log = chat_log + template.format(questions[i], answers[i])
    if n_addition_q:
        chat_log = chat_log + 'Question: {}'.format(questions[-1])
    else:
        chat_log = chat_log[:-2]  # remove the last '/n'
    return chat_log


def prepare_short_chatgpt_message(task_prompt, questions, answers, sub_prompt,
                                  frame_id_list, frame_id_with_interval_list):
    assert len(questions) == len(answers)

    descriptions = ''
    for answer, frame_id in zip(answers, frame_id_with_interval_list):
        idx = frame_id_list.index(frame_id)
        descriptions += f'Frame_{idx+1}: {answer}. '

    messages = [
        {
            "role": "system",
            "content":
                task_prompt + '\n' + descriptions + '\n' + sub_prompt
         }
    ]

    return messages


def prepare_chatgpt_message(task_prompt, questions, answers, sub_prompt):
    messages = [{"role": "system", "content": task_prompt}]

    assert len(questions) == len(answers)
    for q, a in zip(questions, answers):
        messages.append({'role': 'assistant', 'content': 'Question: {}'.format(q)})
        messages.append({'role': 'user', 'content': 'Answer: {}'.format(a)})
    messages.append({"role": "system", "content": sub_prompt})

    return messages



@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
def call_chatgpt(chatgpt_messages, max_tokens=40, model="gpt-3.5-turbo"):
    # print("chatgpt message",chatgpt_messages)
    response = openai.ChatCompletion.create(model=model, messages=chatgpt_messages, temperature=0.6, max_tokens=max_tokens)
    reply = response['choices'][0]['message']['content']
    total_tokens = response['usage']['total_tokens']
    return reply, total_tokens


def find_digit(input):
    regex = r"Frame_(\d+)"

    # Use re.search() to find the match in the sentence
    match = re.search(regex, input)

    # Extract the index from the match object
    if match:
        index = match.group(1)
        # print("Index found:", index)
        return index
    else:
        print("input: "+input)
        print("No index found in sentence.")
        return None


