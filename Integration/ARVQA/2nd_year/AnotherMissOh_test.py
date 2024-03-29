import json
import argparse
# from this import d
import torch
import ipdb
import utils
import utils_sys
from nltk.tokenize import word_tokenize
import numpy as np
import random
import pickle 
from torch.utils.tensorboard import SummaryWriter
from tqdm import tqdm
import os
from torch import nn, optim
import math
import itertools
import copy

#for reproducibility
torch.manual_seed(42)
torch.cuda.manual_seed(42)
np.random.seed(42)
random.seed(42)
torch.backends.cudnn.deterministic=True
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
cpu = torch.device("cpu")


def process_raw_sentence(exception_object=[], sentences=['This is an example.'], object_list=None, generate_unanswerable_que=False):
	new_data=[]
	if not generate_unanswerable_que:
		for question in sentences:
			extracted_objects_ = []
			word_tokenized_question = word_tokenize(question)
			try:
				extracted_objects = utils.object_extract(question)
			except:
				# ipdb.set_trace()
				print("extraction error occured.")

			for object_, [object_idx1, object_idx2] in extracted_objects:
			# for object_item in extracted_objects:
				exception_list = [1 if exception in object_ else 0 for exception in exception_object]
				if not sum(exception_list) > 0:
					extracted_objects_.append([[object_], [object_idx1, object_idx2]])

			# if len(extracted_objects_) == 0:
				# ipdb.set_trace()
			new_data.append([word_tokenized_question, extracted_objects_])
		return new_data
		# if not generate_unanswerable_que:
		# 	return [word_tokenized_question, extracted_objects_]
	else:
		for question in sentences:
			n = len(extracted_objects_)
			lsts = list(itertools.product([0, 1], repeat=n))

			# if question_dict['qid'] not in list(new_data.keys()):
			# 	new_data[question_dict['qid']] = []
			for lst in lsts: #go through each augmentation case
				#making the 'red' list (refer to reserach notebook for what 'red' list is)
				new_word_tokenized_question = copy.deepcopy(word_tokenized_question)
				new_wordtokenize_idx = copy.deepcopy(extracted_objects_)

				for idx, word_bool in enumerate(lst): 
					#if word_bool is true (that is no augmentation)
					if word_bool:
						continue
					else: #if word_bool is false(we need to augment)
						wordtokenize_idx_single = new_wordtokenize_idx[idx]
						
						object_ = [wordtokenize_idx_single[0]]
						object_wordtokenize_idx = wordtokenize_idx_single[1]
						object_wordtokenize_idx_start = object_wordtokenize_idx[0]
						object_wordtokenize_idx_end = object_wordtokenize_idx[1]

						while True: #TODO for the TODO is the bottom of filtering 
							new_sampled_object_ = random.choice(object_list)
							#TODO later we need to develop how to make sure that the new sampled object is not same as the original.
							new_word_tokenized_question[object_wordtokenize_idx_start:object_wordtokenize_idx_end] = new_sampled_object_

							#update new wordtokenize_idx
							reference_idx = object_wordtokenize_idx_start
							length_diff = len(object_) - len(new_sampled_object_) 
							for idx2, wordtokenize_idx_single_update in enumerate(new_wordtokenize_idx):
								if idx == idx2:
									new_wordtokenize_idx[idx2][0] = new_sampled_object_
									new_wordtokenize_idx[idx2][1][1] -= length_diff

								else: #need to update the idx for other objects 
									if new_wordtokenize_idx[idx2][1][0] > reference_idx: #TODO This is assuming no overlap, which I think is reasonable
										new_wordtokenize_idx[idx2][1][0] -= length_diff #update start idx
										new_wordtokenize_idx[idx2][1][1] -= length_diff #update end idx
							break
				new_data_instance = [new_word_tokenized_question, new_wordtokenize_idx,list(lst)]
				new_data.append(new_data_instance)
		return new_data

def inference_demo(model, classifier_head, inputs):  
	outputs = model(inputs[0].to(device), attention_mask=inputs[1].to(device), token_type_ids=inputs[2].to(device))['last_hidden_state']

	predicate_bool_list = []
	for idx, output in enumerate(outputs):
		predicate_bool = {}
		for idx2, predicate in enumerate(inputs[3][idx]):
			#avg_output = output[]
			avg_output = torch.mean(output[inputs[3][idx][predicate][0]:inputs[3][idx][predicate][-1]+1],dim=0).view(1,-1)
			classifier_output = classifier_head(avg_output)
			predicate_bool[predicate] = bool(torch.argmax(classifier_output).item())

		predicate_bool_list.append(predicate_bool)
	return predicate_bool_list


def main(args):
	model, tokenizer = utils.get_model(args)
	model.load_state_dict(torch.load(args.model_ckpt))
	model.to(device)

	classifier_head = utils.Predicate2Bool(model.config.hidden_size)
	classifier_head.load_state_dict(torch.load(args.classifier_head_ckpt))
	classifier_head.to(device)

	json_data = utils_sys.read_json(os.path.join(args.dataset_dir, f'DramaQA/AnotherMissOhQA_{args.split}_set.json' ))
	test_questions = json_data
	sg_fpath = os.path.join(args.dataset_dir, 'AnotherMissOh', 'scene_graph')

	exception_object = ['Haeyoung', 'Jinsang', 'Taejin', 'relationship', 'kind', 'something', 'communication', 'someone', 'everything', 'com', 'color']


	# for debug, we are currently input scene graph from AnotherMissOh. Maybe the caption of the video can be inputed instead
	test_sg2sentence = {}
	for question in tqdm(test_questions):
		test_sg = utils.AnotherMissOh_sg(args, sg_fpath, question)
		test_sg2sentence[question['qid']] = ". ".join(test_sg)

	# tokenize the sentenced scene graph
	tokenized_sg2sentence = utils.sentence2tokenize(args, tokenizer, test_sg2sentence) # TODO: scene graph를 문장화 하여 tokenize 한 결과

	# you can input user given sentence like "this is an exmaple"
	# if you input generate_unanswerable_que=True, it will generate unanwerable by folloing the object list. 
	# for debug, we utilize AnotherMissOh obejct list as a dummy

	outputs = []
	count_unanswerable = 0
	
	for i in range(len(test_questions)):
		test_question = test_questions[i]['que']
		test_qid = test_questions[i]['qid']
		test_vid = test_questions[i]['vid']

		object_list=utils_sys.read_pkl(os.path.join(args.custom_dataset_dir, args.object_list_path))
		data_instance = process_raw_sentence(exception_object=[], sentences=[test_question], object_list=None, generate_unanswerable_que=False)
		print('data_instance:', data_instance)
		# TODO: answerability를 확인하고자 하는 질문
		# 		- generate_unanswerable_que 를 True로 주면 object_list 에서 주어지는 object 들로 unanswerable data를 생성하여 데이터를 구성함.
		#     	- generate_unanswerable_que 를 False로 주면 unanswerable data 생성 없이 주어진 입력으로만 answerability 판단
		#     	- 한 문장 내에 False가 하나라도 있다면 대답 불가능한 질문으로 간주하게 됩니다.
		# 		- sentences: 입력 비디오에 대해 answerability를 확인하고자 하는 질문들 (list of string)

		# For the case of using user given input question
		# data_instance = process_raw_sentence(exception_object=[], sentences=['This is an example.', 'I have a cat'], object_list=None, generate_unanswerable_que=False) 


		# For the case when generating unanswerable question at the same time with AnotherMissOh
		# data_instance = process_raw_sentence(exception_object=exception_object, sentences=['This is an example.'], object_list=object_list, generate_unanswerable_que=True) 
		try:
			inputs = utils.input_preprocess_demo(args, tokenizer, data_instance, tokenized_sg2sentence[test_qid])
			
			with torch.no_grad():
				if len(inputs) > 1:
					ipdb.set_trace()
					
				for idx, item in enumerate(inputs):
					# label = [[batch[-2], batch[-1].bool()] for batch in item ]
					prediction = inference_demo(model, classifier_head, item)
					answerability = []
					for idx, pred in enumerate(prediction):
						if False in pred.values():
							answerability.append('unanswerable')
							count_unanswerable += 1
						else:
							answerability.append('answerable')
					
					print('prediction:', prediction)
					print('answerability:', answerability)
					
					output = {
						'qid': test_qid,
						'question': test_question,
						'answerability': answerability,
						'prediction': prediction,
						'vid': test_vid,
					}
					outputs.append(output)

			# ipdb.set_trace()
		except:
			print('preprocess_demo error')
			output = {
						'qid': test_qid,
						'question': test_question,
						'answerability': ['answerable'],
						'prediction': [],
						'vid': test_vid,
					}
			outputs.append(output)
		
	print('outputs:', outputs)
	json.dump(outputs, open(args.output_path, 'w'), indent=4)
	print('count_unanswerable:', count_unanswerable)
	
	return


if __name__ =="__main__":
	parser = argparse.ArgumentParser(description='LBAagent-project')
	#parser.add_argument('--v_sg_path', type=str, default='/mnt/hdd/hsyoon/workspace/OOD/VQRR/gqa_data/train_sceneGraphs.json')
	# parser.add_argument('--sg_info', type=str, default='./dataset/AnotherMissOh/scene_graph/AnotherMissOh01/001/0078/custom_data_info.json')

	# parser.add_argument('--train_scenegraph', type=str, default='./dataset/AnotherMissOh/scene_graph/AnotherMissOh15/001/0025/custom_prediction.json')
	# parser.add_argument('--val_scenegraph', type=str, default='/mnt/hdd/hsyoon/workspace/OOD/VQRR/gqa_data/val_sceneGraphs.json')

	# parser.add_argument('--train_question', type=str, default='./dataset/DramaQA/AnotherMissOhQA_test_set.json')
	# parser.add_argument('--train_question', type=str, default='./dataset/DramaQA/AnotherMissOhQA_val_set.json')
	# parser.add_argument('--dummy_question', type=str, default='./dataset/processed/train_data_fixed.pkl')
	# parser.add_argument('--val_question', type=str, default='/mnt/hdd/hsyoon/workspace/OOD/VQRR/val_data_fixed.pkl')
	
	parser.add_argument('--split', type=str, choices=['train', 'val', 'test'], default='val')
	
	# model
	parser.add_argument('--bbox_threshold', type=float, default=0.3)
	parser.add_argument('--rel_threshold', type=float, default=0.7)
	parser.add_argument('--model_name', type=str, default='bert-base-uncased', choices=['bert-base-uncased'])
	parser.add_argument('--max_length', type=int, default=512)
	parser.add_argument('--bsz', type=int, default=4) 
	parser.add_argument('--sg_rels_topk', type=int, default=50)
	
	# ckpt path
	parser.add_argument('--model_ckpt', type=str, default='./saves/ckpt/2023-11-04_04_24_48_best_loss.pt')
	parser.add_argument('--classifier_head_ckpt', type=str, default='./saves/ckpt/2023-11-04_04_24_48_classifier_best_loss.pt')
	
	# data path
	parser.add_argument('--custom_dataset_dir', type=str, default='./saves/custom_dataset')
	parser.add_argument('--dataset_dir', type=str, default='./dataset')
	parser.add_argument('--object_list_path', type=str, default='AnotherMissOhQA_object_list.pkl')
	parser.add_argument('--output_path', type=str, default='../../Integration-Outputs/output_KAIST2.json')
	
	args = parser.parse_args()
	
	main(args)