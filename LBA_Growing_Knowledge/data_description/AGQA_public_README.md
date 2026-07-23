# AGQA Benchmark

​For more details, see our [paper](https://arxiv.org/pdf/2103.16002.pdf) and our [AGQA 2.0 update explanation](https://arxiv.org/pdf/2204.06105.pdf). We recommend using the updated version AGQA 2.0 in future experiments. 
​
## Download videos and questions. 
​
Download videos ("Data") from [Charades](https://prior.allenai.org/projects/charades).

​
Download our Question-Answer pairs from our [website](https://cs.stanford.edu/people/ranjaykrishna/agqa/)
​
### Training Question Format
​
```json
{
    'question_id': {
        'question': 'Did they contact a blanket?', 
        'answer': 'No', 
        'video_id': 'YSKX3', 
        'global': ['exists', 'obj-rel'],
        'local': 'yes-no-o4', 
        'ans_type': 'binary',
        'steps': 1,
        'semantic': 'object',
        'structural': 'verify',
        'novel_comp': 0,
        'more_steps': 0,
        'sg_grounding': {(start char, end char): [scene graph vertices]},
        'program': 'program string',
     }
 }
​
 ```
 
o4 in the question's local value is an identifer for blanket. English translations of these identifiers can be found [here]().
​
​
### Testing Question Format
 
```json
{
    'question_id': {
        'question': 'Did they contact a blanket?, 
        'answer': 'No', 
        'video_id': 'YSKX3', 
        'global': ['exists', 'obj-rel'],
        'local': 'yes-no-o4', 
        'ans_type': 'binary',
        'steps': 1,
        'semantic': 'object',
        'structural': 'verify',
        'novel_comp': 0,
        'nc_seq': 0,
        'nc_sup': 0, 
        'nc_dur': 0,
        'nc_objrel': 0,
        'indirect': 0, 
        'i_obj': 0,
        'i_rel': 0, 
        'i_act': 0,
        'i_temp': 0, 
        'more_steps': 0,
        'direct_equiv': 'question_id',
        'sg_grounding': {(start char, end char): [scene graph vertices]},
        'program': 'program string',
     }
}
​
 ```
 
o4 in the question's local value is an identifer for blanket. English translations of these identifiers can be found [here](https://drive.google.com/uc?export=download&id=1d0Gx4x5qnvp13Su_sIS_nlSn47ZggY8n).
​
# Splitting test set by categories
​
These question attributes are describe in more detail in [Section 3.2](https://arxiv.org/pdf/2103.16002.pdf).
​
​
### 1. Reasoning
​
The reasoning categories are included in the list under `'global'`. If a question has multiple reasoning categories, it should be included in the accuracy for all categories. 
​
​
### 2. Semantic 
​
Split the test set by the values of `'semantic'`.
​
### 3. Structural 
​
Split the test set by the values of `'structural'`.
​
​
### 4. Binary vs open
​
Split the test set by the values of `'ans_type'`.
​
​
​
# Additional Metrics
​
We describe these metric in more detail in [Section 3.4](https://arxiv.org/pdf/2103.16002.pdf).
​
​
### 1. Novel compositions metric
​
​
To run the Novel Compositions metric, train on questions without a novel composition (`'novel_comp' == 0`) and test on questions with novel compositions (`'novel_comp' == 1`).
​
#### For a more detailed analysis ([Table 4](https://arxiv.org/pdf/2103.16002.pdf)): 
​
Sequencing compositions: `'nc_seq' == 1`
​
Superlative compositions: `'nc_sup' == 1`
​
Duration compositions: `'nc_dur' == 1`
​
Object-Relationship compositions: `'nc_objrel' == 1`
​
### 2. Indirect References metric
​
To use the Indirect References metric, train and test on all questions. 
​
#### Split by reference type
​
Indirect object reference: `'i_obj' == 1`
​
Indirect relationship reference: `'i_rel' == 1`
​
Indirect action reference: `'i_act' == 1`
​
Temporal localization phrase: `'i_temp' == 1`
​
​
#### To calculate Recall scores
​
The Recall scores are the accuracy of each reference category. 
​
​
#### To calculate Precision scores
​
Take the subset of questions that:
​
1. contain an indirect reference AND
    - `'indirect' == 1`
​
2. have a **correctly-answered** equivalent question: 
    - `'direct_equiv' == 'direct_equiv_question_id'` AND
    - `'direct_equiv_question_id'` was answered correctly
​
If no such equivalent question is included in the dataset, `'direct_equiv' == None`. 
​
The Precision scores are the accuracy on each of these subsets. Split this subset by reference type for a more detailed representation. 
​
​
### 3. Compositional Steps metric
​
To run the More Compositional Steps metric, train on questions in which `'more_steps' == 0` and test on questions in which `'more_steps' == 1`.
​
​



# Program formatting
​
Each question has a program of interlocking functions that break down the reasoning steps needed to answer the question. Note that Localize('between' []) takes two action arguments. We specify the program names below. An 'item' can refer to any type of data structure.
​


| Function     | Input                                                        | Output                                                                                                       |
|:--------------|:--------------------------------------------------------------|:--------------------------------------------------------------------------------------------------------------|
| AND          | bool 1<br>bool 2                                             | True if bool 1 AND bool 2, else False                                                                        |
| Choose       | item 1<br>item 2<br>[items]                                  | item iff item 1 OR item 2 exists in [items]                                                           |
| Compare      | [items]<br>bool func                                         | The item that returns True from function                                                                        |
| Equals       | item 1<br>item 2                                             | boolean                                                                                                      |
| Exists       | item<br>[items]                                              | boolean                                                                                                      |
| Filter       | dict<br>[keys]                                               | mapping of [keys] to dictionary (dict[keys[0]][keys[1]]...)                                                                                    |
| HasItem      | [items]                                                      | True if length of list > 0, else False                                                                       |
| Iterate      | [items]<br>function                                          | list with function mapped to each item in [items]                                                                         |
| IterateUntil | 'forward/backward'<br>[items]<br>bool func<br>secondary func | output of secondary function on the first item to satisfy the bool func when iterating forwards or backwards |
| Localize     | temporal phrase<br>action                                    | [frames]                                                                                                     |
| OnlyItem     | [item]                                                      | item in list, if length of list is 1                                                                                  |
| Query        | attribute<br>item                                            | value of attribute within item                                                                               |
| Superlative  | 'min/max'<br>[items]<br>func                                 | item with min or max value when func applied                                                                 |
| XOR          | bool 1<br>bool 2                                             | True if bool 1 XOR bool 2, else False                                                                        |
​


# Scene graph grounding
​
Each question associates parts of the question to nodes in the scene graph. This grounding maps keys of character indices to lists of node indices. The character indices refer to the 'start-end' characters of the phrase. These node indices refer to items in the scene graph. 
- We only include the relevant node indices (e.g. if the question asks 'Did they contact a cup after walking through a doorway?', the reference to 'a cup' only includes vertices with that cup during frames after they walked through a doorway. If the list is empty, there are no such vertices so the answer is 'No'). Relevancy is determined by the highest level in the program.
- If the keys are the same number "X-X", then they refer to all the frames in the video. Some questions do not have a phrase for temporal localization (e.g. "Do they contact a cup"), so the reference to relevant frames has the same start and end index. 
- *Some scene graphs currently have negative values. This is a bug with one template and one indirect reference. We are fixing it now, and will re-upload shortly.*
​
​


As an example, the question "Does someone contact a paper before drinking from a cup?" may have the following scene graph grounding: 
​
```json
{
    # refers to the nodes for 'a paper'. 'o23' is the idx reference for 'a paper' (see IDX.pkl)
    "21-28": [ "o23/000083", "o23/000084", ..., "o23/000813", "o23/000826"],
    
    # refers to the node for 'drinking from a  cup'. 'c106' is the idx reference for 'drinking from a cup' (see IDX.pkl)
    "36-55": ["c106/1"],  
    
    # refers to the frames localized by the phrase 'before drinking from a cup'
    "29-55": ["000083", "000084", ..., "000869", "000900"]
}
```
​
# Using Scene Graphs
​
The scene graph files map video ids to scene graph dictionaries. Each scene graph maps vertex ids to vertex information. 
​
Each vertex contains information about the other vertices to which it is connected. The type of information included depends on vertex type.
​
```json
{
    'frameid': {
        'id': '000105' 
    'type':  'frame'
    'secs': 6.3 
    'objects': [connecting object nodes]
    'attention': [connecting attention nodes]
    'contact': [connecting contact nodes]
    'spatial': [connecting spatial nodes]
    'verb': [connecting verb nodes]
    'actions': [connecting action nodes]
    'metadata': test / train
    'next': next frame 
    'prev': previous frame
     }
}
```

```json
{
    'actionid': {
        'id': 'c076/1'
    'charades': 'c076'
    'phrase': 'holding a pillow'
    'type':  'act'
    'start': 14.56
    'end': 17.5 
    'length': 2.94 
    'objects': [connecting object nodes]
    'attention': [connecting attention nodes]
    'contact': [connecting contact nodes]
    'spatial': [connecting spatial nodes]
    'verb': [connecting verb nodes]
    'metadata': test / train
    'all_f': [list of frame ids]
    'subject':  'o9'
    'verb': 'v25
    'next_discrete': next non-overlapping action
    'prev_discrete': previous non-overlapping
    'next_instance': next c076 action
    'prev_instance': previous c076 action
    'while': [list of co-occuring action objects]
     }
}
```

```json
{
    'objectid': {
        'id': 'o4/000105' 
    'type':  'object'
    'class': 'o4'
    'attention': [connecting attention nodes]
    'contact': [connecting contact nodes]
    'spatial': [connecting spatial nodes]
    'verb': [connecting verb nodes]
    'visible': True if visible, False otherwise
    'bbox': [list of bbox values from Action Genome]
    'metadata': test / train
    'frame_num': 000105
    'secs': 6.3
    'next': next o4 object
    'prev': previous o4 object
     }
}
```
​
​
note: relationid contains attention id(ex. `r1/000105`) and verb id(ex. `v025/000270`).
```json
{
    'relationid': {
        'id': 'r22/000209' 
    'type':  'contact'
    'class': 'r22'
    'objects': [connecting object nodes]
    'metadata': test / train
    'frame_num': 000209
    'secs': 12.6
    'next': next r22 relation
    'prev': previous r22 relation
     }
 }
```


**Previous updates that are now solved**

*Updated 08/19/21*

We have released a new version of the balanced dataset that fixes small bugs in data formatting.

There is one error in programs for the instances in which the object in an action is referred to indirectly as 'the last thing they were [relationship]'. This program should include IterateUntil(backward, ...), but instead states IterateUntil(forward, ...).

*Updated 07/22/21*

*We have been alerted to several small bugs in the dataset. We will be releasing an updated version with those changes within the next week.*
- There are several negative time stamps in scene graph annotations(from one template and one indirect reference) that we are fixing
- The 'ans_type' labels are incorrect. Questions with the structure 'query' are open answer, while all others are binary answer.
- We are entirely re-generating the logic questions. 

