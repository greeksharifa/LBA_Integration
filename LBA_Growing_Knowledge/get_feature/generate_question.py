import openai
import os

# from dotenv import load_dotenv, find_dotenv
# _ = load_dotenv(find_dotenv()) # read local .env file

openai.api_key  = os.getenv('OPENAI_API_KEY')

def get_completion(prompt, model="gpt-3.5-turbo"):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0.5, # this is the degree of randomness of the model's output
    )
    return response.choices[0].message["content"]


uncertain_phrase = "holding a pillow"

# What questions can you ask when you're not sure about the meaning of text separated by triple backticks?\

# Your job is to generate 3 questions about the text, given a video and some text associated with it.
# Text is delimited by triple backticks.

"""
You've been given a video and some text delimited by a triple backtick.
And you are not sure what the text means.

Your task is to generate 3 questions about the text to find out what it means.
Each question should contain a maximum of 20 words.
"""


prompt=f"""\\
You are given a video and a phrase of unclear meaning, separated by a triple backtick.
You are not sure what the phrase means.

Your task is to generate 3 questions about the phrase to find out its meaning.
Each question should contain a maximum of 20 words.

phrase: ```{uncertain_phrase}```
"""

response = get_completion(prompt)
print(response)
