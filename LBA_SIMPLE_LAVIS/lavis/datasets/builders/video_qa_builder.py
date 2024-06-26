"""
 Copyright (c) 2022, salesforce.com, inc.
 All rights reserved.
 SPDX-License-Identifier: BSD-3-Clause
 For full license text, see the LICENSE file in the repo root or https://opensource.org/licenses/BSD-3-Clause
"""

from lavis.common.registry import registry
from lavis.common.utils import get_cache_path
from lavis.datasets.builders.base_dataset_builder import BaseDatasetBuilder
from lavis.datasets.datasets.video_vqa_datasets import (
    VideoQADataset, DramaQAEvalDataset, DramaQAIncludingSubQAEvalDataset, DramaQASQDataset, DramaQAEvalDataset
)

class VideoQABuilder(BaseDatasetBuilder):
    train_dataset_cls = VideoQADataset
    eval_dataset_cls = VideoQADataset

    def build(self):
        datasets = super().build()

        ans2label = self.config.build_info.annotations.get("ans2label")
        if ans2label is None:
            raise ValueError("ans2label is not specified in build_info.")

        ans2label = get_cache_path(ans2label.storage)

        for split in datasets:
            datasets[split]._build_class_labels(ans2label)

        return datasets


@registry.register_builder("msrvtt_qa")
class MSRVTTQABuilder(VideoQABuilder):
    DATASET_CONFIG_DICT = {
        "default": "configs/datasets/msrvtt/defaults_qa.yaml",
    }


@registry.register_builder("msvd_qa")
class MSVDQABuilder(VideoQABuilder):
    DATASET_CONFIG_DICT = {
        "default": "configs/datasets/msvd/defaults_qa.yaml",
    }


@registry.register_builder("dramaqa_sq")
class DramaQASQBuilder(VideoQABuilder):
    train_dataset_cls = DramaQASQDataset
    eval_dataset_cls = DramaQASQDataset

    DATASET_CONFIG_DICT = {
        "default": "configs/datasets/dramaqa/defaults_sq.yaml",
    }


@registry.register_builder("dramaqa_eval")
class DramaQAEvalBuilder(VideoQABuilder):
    # train_dataset_cls = TODO      # dummy
    eval_dataset_cls = DramaQAEvalDataset

    DATASET_CONFIG_DICT = {
        "default": "configs/datasets/dramaqa/defaults_test.yaml",
    }
    
    
@registry.register_builder("dramaqa_subqa_eval")
class DramaQAIncludingSubQAEvalBuilder(VideoQABuilder):
    # train_dataset_cls = TODO      # dummy
    eval_dataset_cls = DramaQAIncludingSubQAEvalDataset

    DATASET_CONFIG_DICT = {
        "default": "configs/datasets/dramaqa/includingSubQA_test.yaml",
    }
    