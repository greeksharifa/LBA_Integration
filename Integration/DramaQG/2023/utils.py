import json
import torch
import random
import ast
import numpy as np
from tqdm import tqdm

def set_random_seed(seed):
    torch.manual_seed(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    np.random.seed(seed)
    random.seed(seed)
    torch.cuda.manual_seed(seed)

def get_info_from_vid(vid):
    episode_id = vid[13:15]
    scene_id = vid[16:19]
    shot_id = vid[20:]

    return (episode_id, scene_id, shot_id)

def load_subtitles(path):

    subtitles_list = {}
    
    with open(path, 'r') as f:
        subtitles = json.load(f)

        for vid, contents in tqdm(subtitles.items(), desc="Load subtitles"):

            utterances = []
            contained_subs = contents["contained_subs"]
            
            for sub in contained_subs:
                speaker = sub["speaker"]
                utter = sub["utter"]

                utterances.append(speaker + " : " + utter.strip())

            episode_id, scene_id, shot_id = get_info_from_vid(vid) 

            if episode_id not in subtitles_list.keys():
                subtitles_list[episode_id] = {scene_id : {shot_id : utterances}}

            elif scene_id not in subtitles_list[episode_id].keys():
                subtitles_list[episode_id][scene_id] = {shot_id : utterances}

            else:
                subtitles_list[episode_id][scene_id][shot_id] = utterances

    return subtitles_list

def get_subtitles_by_vid(subtitiles_list, vid):
    
    episode_id, scene_id, shot_id = get_info_from_vid(vid) 

    subtitles = []
    
    try:
        if shot_id == "0000":
            for shot_id, utterances in subtitiles_list[episode_id][scene_id].items():
                subtitles += utterances
        else:
            subtitiles = subtitiles_list[episode_id][scene_id][shot_id]
    except:
        pass
    
    return subtitles
        
def get_object_name_from_inputs(object_list):
    
    ambiguous_entity_list = []
    for object in object_list:
        for object_name, label in object.items():
            if isinstance(object_name,str):
                object_name = ast.literal_eval(object_name)
            if str(label) == "False":  
                if isinstance(object_name,list):
                    full_object_name = " ".join(object_name)
                else:
                    full_object_name = object_name
                    
                ambiguous_entity_list.append(full_object_name) 
                
    return ambiguous_entity_list   

def convert_inputs_to_examples(inputs_list):
    
    examples = []
    for inputs in inputs_list:
        ambiguous_objects = get_object_name_from_inputs(inputs['prediction'])
        for object_name in ambiguous_objects:
            example = {}
            example['ambiguous_object'] = object_name
            example['vid'] = inputs['vid']
            example['qid'] = inputs['qid']
            example['question'] = inputs['question']
            examples.append(example)
    
    return examples