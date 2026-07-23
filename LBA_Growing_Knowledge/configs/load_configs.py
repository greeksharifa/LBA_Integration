import os


def get_config_path():
    username = os.environ.get('USER', os.environ.get('USERNAME'))

    root_data_path = f'/home/{username}/data/AGQA/'
    features_path = os.path.join(root_data_path, 'features/')

    config_path = {
        'root_path': root_data_path,
        'features_path': features_path,
        'test_qa_path': os.path.join(root_data_path, 'AGQA2/AGQA_balanced/test_balanced.txt'),
        'test_sg_path': os.path.join(root_data_path, 'AGQA_scene_graphs/AGQA_test_stsgs.pkl'),
        'idx2eng_path': os.path.join(root_data_path, 'ENG.txt'),
        'charades_frame_path': f'/home/{username}/data/Charades/Charades_v1_rgb',
        'grounded_knowledge_path': os.path.join(features_path, 'grounded_knowledge.json'),
        'phrases_path': os.path.join(features_path, 'phrases_from_questions.json'),

    }

    return config_path
