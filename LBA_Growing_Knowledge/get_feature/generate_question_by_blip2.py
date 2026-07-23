import openai
import os
import requests
from PIL import Image
from transformers import AutoProcessor, Blip2ForConditionalGeneration
import torch

url = 'https://storage.googleapis.com/sfr-vision-language-research/LAVIS/assets/merlion.png'
image = Image.open(requests.get(url, stream=True).raw).convert('RGB')
# image.resize((596, 437))


processor = AutoProcessor.from_pretrained("Salesforce/blip2-opt-2.7b")
# by default `from_pretrained` loads the weights in float32 we load in float16 instead to save memory
model = Blip2ForConditionalGeneration.from_pretrained("Salesforce/blip2-opt-2.7b", torch_dtype=torch.float16)

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"using device: {device}")
model.to(device)



uncertain_phrase = "holding a pillow"

prompt=f"""\\
You are given a video and a phrase of unclear meaning, separated by a triple backtick.
You are not sure what the phrase means.

Your task is to generate 3 questions about the phrase to find out its meaning.
Each question should contain a maximum of 20 words.

phrase: ```{uncertain_phrase}```
"""

inputs = processor(image, text=prompt, return_tensors="pt").to(device, torch.float16)

generated_ids = model.generate(**inputs, max_new_tokens=30)
generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()
print('generated_text:', generated_text)
