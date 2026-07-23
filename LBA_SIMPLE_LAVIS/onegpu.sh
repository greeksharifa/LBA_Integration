CUDA_VISIBLE_DEVICES=2 python test.py --cfg-path projects/LBA/eval/DramaQA_eval_sq_finetune.yaml \
	--options model.frame_num=5 \
	datasets.dramaqa_sq.vis_processor.eval.n_frms=7 \
	datasets.dramaqa_sq.vis_processor.eval.name='blip_image_eval' \
	run.batch_size_eval=1 
