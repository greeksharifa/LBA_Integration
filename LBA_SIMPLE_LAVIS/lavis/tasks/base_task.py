"""
 Copyright (c) 2022, salesforce.com, inc.
 All rights reserved.
 SPDX-License-Identifier: BSD-3-Clause
 For full license text, see the LICENSE file in the repo root or https://opensource.org/licenses/BSD-3-Clause
"""

import logging
import os
import json
from colors import Colors, print_sample

import torch
import torch.distributed as dist
from lavis.common.dist_utils import get_rank, get_world_size, is_main_process, is_dist_avail_and_initialized
from lavis.common.logger import MetricLogger, SmoothedValue
from lavis.common.registry import registry
from lavis.datasets.data_utils import prepare_sample


class BaseTask:
    def __init__(self, **kwargs):
        super().__init__()

        self.inst_id_key = "instance_id"

    @classmethod
    def setup_task(cls, **kwargs):
        return cls()

    def build_model(self, cfg):
        model_config = cfg.model_cfg

        model_cls = registry.get_model_class(model_config.arch)
        return model_cls.from_config(model_config)

    def build_datasets(self, cfg):
        """
        Build a dictionary of datasets, keyed by split 'train', 'valid', 'test'.
        Download dataset and annotations automatically if not exist.

        Args:
            cfg (common.config.Config): _description_

        Returns:
            dict: Dictionary of torch.utils.data.Dataset objects by split.
        """

        datasets = dict()

        datasets_config = cfg.datasets_cfg

        assert len(datasets_config) > 0, "At least one dataset has to be specified."

        for name in datasets_config:
            logging.info('name: ' + str(name))
            dataset_config = datasets_config[name]
            logging.info('dataset_config: ' + str(dataset_config))

            builder = registry.get_builder_class(name)(dataset_config)
            dataset = builder.build_datasets()

            datasets[name] = dataset

        return datasets

    def train_step(self, model, samples):
        output = model(samples)
        loss_dict = {}
        for k,v in output.items():
            if "loss" in k:
                loss_dict[k] = v
        return output["loss"], loss_dict

    def valid_step(self, model, samples):
        raise NotImplementedError
    
    def before_training(self, model, dataset, **kwargs):
        model.before_training(dataset=dataset, task_type=type(self))

    def before_evaluation(self, model, dataset, **kwargs):
        model.before_evaluation(dataset=dataset, task_type=type(self))

    def after_evaluation(self, **kwargs):
        pass

    def inference_step(self):
        raise NotImplementedError

    def evaluation(self, model, data_loader, cuda_enabled=True):
        metric_logger = MetricLogger(delimiter="  ")
        header = "Evaluation"
        # TODO make it configurable
        print_freq = 20

        results = []
        results_for_save = []
        _cnt = 0

        for samples in metric_logger.log_every(data_loader, print_freq, header):
            samples = prepare_sample(samples, cuda_enabled=cuda_enabled)
            
            if _cnt == 0:
                print_sample(samples, msg="eval sample: ", color=Colors.CYAN)
            elif _cnt >= 100:
                break
            """
            samples: {
                'image': Tensor
                'image_id': tensor([565248, 284885, 276693, 119210], device='cuda:0'),
                'main_question_id': ['565248001', '284885001', '276693003', '119210000'],
                'instance_id': ['0', '4', '8', '12'],
                'text_input': ["write a informative sub-question about image, when main-question is 'are they at the beach?'",
                                "write a sub-question about image, when main-question is 'is the house new?'",
                                "write a informative sub-question about image, when main-question is 'is the woman going up or downhill?'",
                                "write a sub-question about image, when main-question is 'what feature is significant about this animal?'"],
                'prompt': ["write a informative sub-question about image, when main-question is 'are they at the beach?'",
                            "write a sub-question about image, when main-question is 'is the house new?'",
                            "write a informative sub-question about image, when main-question is 'is the woman going up or downhill?'",
                            "write a sub-question about image, when main-question is 'what feature is significant about this animal?'"],
                'sub_question_id': 무언가,
                'text_output': ['are the woman on the horses near to the sea?</s>',
                                'is the window of the house boarded up?</s>',
                                'is the path in the distance higher or lower than in the front?</s>',
                                'does the zebra have stripes?</s>']
                }
            """
            eval_output = self.valid_step(model=model, samples=samples)

            if len(eval_output) == 2:
                eval_output, eval_output_for_save = eval_output
                if _cnt < 5:
                    json.dump(eval_output_for_save, open(f'results/{_cnt}.json', 'w'), indent=4)
                results_for_save.extend(eval_output_for_save)
            # import pudb; pudb.set_trace()
            results.extend(eval_output)
            # print("results: ", results)
            """
            ques_id: <class 'int'> 3205
            pred_answer: <class 'int'> 0
            gt_answer: <class 'torch.Tensor'> tensor(0, device='cuda:0')
            results:  [{'question_id': 3205, 'pred_ans': 0, 'gt_ans': tensor(0, device='cuda:0')}]
            """
            _cnt += 1
        
        if is_dist_avail_and_initialized():
            dist.barrier()
        
        json.dump(results_for_save, open('results/result.json', 'w'), indent=4)
        
        if results_for_save:
            return results, results_for_save
        else:
            return results

    def train_epoch(
        self,
        epoch,
        model,
        data_loader,
        optimizer,
        lr_scheduler,
        scaler=None,
        cuda_enabled=False,
        log_freq=50,
        accum_grad_iters=1,
    ):
        return self._train_inner_loop(
            epoch=epoch,
            iters_per_epoch=len(data_loader),
            model=model,
            data_loader=data_loader,
            optimizer=optimizer,
            scaler=scaler,
            lr_scheduler=lr_scheduler,
            log_freq=log_freq,
            cuda_enabled=cuda_enabled,
            accum_grad_iters=accum_grad_iters,
        )

    def train_iters(
        self,
        epoch,
        start_iters,
        iters_per_inner_epoch,
        model,
        data_loader,
        optimizer,
        lr_scheduler,
        scaler=None,
        cuda_enabled=False,
        log_freq=50,
        accum_grad_iters=1,
    ):
        return self._train_inner_loop(
            epoch=epoch,
            start_iters=start_iters,
            iters_per_epoch=iters_per_inner_epoch,
            model=model,
            data_loader=data_loader,
            optimizer=optimizer,
            scaler=scaler,
            lr_scheduler=lr_scheduler,
            log_freq=log_freq,
            cuda_enabled=cuda_enabled,
            accum_grad_iters=accum_grad_iters,
        )

    def _train_inner_loop(
        self,
        epoch,
        iters_per_epoch,
        model,
        data_loader,
        optimizer,
        lr_scheduler,
        scaler=None,
        start_iters=None,
        log_freq=100,
        cuda_enabled=False,
        accum_grad_iters=1,
    ):
        """
        An inner training loop compatible with both epoch-based and iter-based training.

        When using epoch-based, training stops after one epoch; when using iter-based,
        training stops after #iters_per_epoch iterations.
        """
        use_amp = scaler is not None

        if not hasattr(data_loader, "__next__"):
            # convert to iterator if not already
            data_loader = iter(data_loader)

        metric_logger = MetricLogger(delimiter="  ")
        metric_logger.add_meter("lr", SmoothedValue(window_size=1, fmt="{value:.6f}"))
        metric_logger.add_meter("loss", SmoothedValue(window_size=1, fmt="{value:.4f}"))

        # if iter-based runner, schedule lr based on inner epoch.
        logging.info(
            "Start training epoch {}, {} iters per inner epoch.".format(
                epoch, iters_per_epoch
            )
        )
        header = "Train: data epoch: [{}]".format(epoch)
        if start_iters is None:
            # epoch-based runner
            inner_epoch = epoch
        else:
            # In iter-based runner, we schedule the learning rate based on iterations.
            inner_epoch = start_iters // iters_per_epoch
            header = header + "; inner epoch [{}]".format(inner_epoch)
            
        _cnt = 0

        for i in metric_logger.log_every(range(iters_per_epoch), log_freq, header):
            # if using iter-based runner, we stop after iters_per_epoch iterations.
            if i >= iters_per_epoch:
                break

            samples = next(data_loader)
            if _cnt == 0:
                _cnt += 1
                print_sample(samples, msg="train sample: ", color=Colors.BRIGHT_CYAN)

            samples = prepare_sample(samples, cuda_enabled=cuda_enabled)
            samples.update(
                {
                    "epoch": inner_epoch,
                    "num_iters_per_epoch": iters_per_epoch,
                    "iters": i,
                }
            )
            # logging.info(samples)

            lr_scheduler.step(cur_epoch=inner_epoch, cur_step=i)

            with torch.cuda.amp.autocast(enabled=use_amp):
                loss, loss_dict = self.train_step(model=model, samples=samples)
                loss /= accum_grad_iters #TODO: not affect loss_dict values for logging

            # after_train_step()
            if use_amp:
                scaler.scale(loss).backward()
            else:
                loss.backward()

            # update gradients every accum_grad_iters iterations
            if (i + 1) % accum_grad_iters == 0:
                if use_amp:
                    scaler.step(optimizer)
                    scaler.update()                     
                else:    
                    optimizer.step()
                optimizer.zero_grad()

            metric_logger.update(**loss_dict)
            metric_logger.update(lr=optimizer.param_groups[0]["lr"])

        # after train_epoch()
        # gather the stats from all processes
        metric_logger.synchronize_between_processes()
        logging.info("Averaged stats: " + str(metric_logger.global_avg()))
        
        return {
            k: "{:.3f}".format(meter.global_avg)
            for k, meter in metric_logger.meters.items()
        }

    @staticmethod
    def save_result(result, result_dir, filename, remove_duplicate=""):
        import json

        result_file = os.path.join(
            result_dir, "%s_rank%d.json" % (filename, get_rank())
        )
        final_result_file = os.path.join(result_dir, "%s.json" % filename)
        for r in result:
            try:
                r['gt_ans'] = r['gt_ans'].item()
            except:
                if type(r['text_output']) == str:
                    r['gt_ans'] = r['text_output']
                else:
                    r['gt_ans'] = r['text_output'].item()

        json.dump(result, open(result_file, "w"), indent=4)     # ywjang: add indent=4

        if is_dist_avail_and_initialized():
            dist.barrier()

        if is_main_process():
            logging.warning("rank %d starts merging results." % get_rank())
            # combine results from all processes
            result = []

            for rank in range(get_world_size()):
                result_file = os.path.join(
                    result_dir, "%s_rank%d.json" % (filename, rank)
                )
                res = json.load(open(result_file, "r"))
                result += res

            if remove_duplicate:
                result_new = []
                id_list = []
                for res in result:
                    if res[remove_duplicate] not in id_list:
                        id_list.append(res[remove_duplicate])
                        result_new.append(res)
                result = result_new

            json.dump(result, open(final_result_file, "w"), indent=4)     # ywjang: add indent=4
            print("result file saved to %s" % final_result_file)

        return final_result_file
