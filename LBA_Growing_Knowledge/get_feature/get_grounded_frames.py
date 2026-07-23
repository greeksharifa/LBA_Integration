import os
from typing import List

import cv2
from PIL import Image


def get_grounded_frames(scene_graph: dict, qa: dict, charades_frame_path: str,
                        question_id: str, #uncertain_phrases: List[((int, int), str)]=None,
                        only_uncertain_frame: bool = False,
                        max_frames: int = None,
                        verbose:bool=False) -> (List, List):    #dict:
    """
    This function returns the grounded frame for a given question id.
    :param scene_graph:
    :param qa:
    :param charades_frame_path:
    :param question_id:
    :param uncertain_phrases:
    :param only_uncertain_frame:
    :param max_frames:
    :param verbose:
    :return:
    """
    question_data = qa[question_id]
    video_id = question_data['video_id']
    sg_grounding = question_data['sg_grounding']
    frame_id_list = []
    if only_uncertain_frame:
        pass
    else:
        for value in sg_grounding.values():
            for v in value:
                if len(v) == 6 and '/' not in v:
                    frame_id_list.append(v)

    frame_id_list = list(set(frame_id_list))
    frame_id_list.sort()
    # print('1st       frame_id_list:', frame_id_list)

    frame_id_with_interval_list = [frame_id_list[0]]
    for i in range(1, len(frame_id_list)-1):
        if int(frame_id_list[i]) - int(frame_id_with_interval_list[-1]) >= 24:
            frame_id_with_interval_list.append(frame_id_list[i])
    # print('after 24  frame_id_list:', frame_id_list)

    if max_frames is not None and len(frame_id_with_interval_list) > max_frames:
        idxs = list(range(0, len(frame_id_with_interval_list), len(frame_id_with_interval_list)//max_frames))
        idxs = idxs[:max_frames]
        frame_id_with_interval_list = [frame_id_with_interval_list[idx] for idx in idxs]
    # print('after max frame_id_with_interval_list:', frame_id_with_interval_list)


    def get_frames(_frame_id_list):
        _frames = []
        for _frame_id in _frame_id_list:
            _frame_path = os.path.join(charades_frame_path, video_id, f'{video_id}-{_frame_id}.jpg')
            _raw_image = Image.open(_frame_path).convert('RGB')
            _frames.append(_raw_image)
            # frame = cv2.imread(frame_path)
            # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # result[frame_id] = raw_image

        return _frames


    grounded_frames = get_frames(frame_id_list)
    frames_for_visual_info = get_frames(frame_id_with_interval_list)

    return grounded_frames, frames_for_visual_info, frame_id_list, frame_id_with_interval_list

