CUDA_VISIBLE_DEVICES=2 python test.py --cfg-path projects/LBA/eval/DramaQA_eval_sq_finetune.yaml \
	--options model.frame_num=5 \
	run.batch_size_eval=1
