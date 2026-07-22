"""
 Copyright (c) 2022, salesforce.com, inc.
 All rights reserved.
 SPDX-License-Identifier: BSD-3-Clause
 For full license text, see the LICENSE file in the repo root or https://opensource.org/licenses/BSD-3-Clause
"""

import gzip
import logging
import os
import random as rnd
import tarfile
import zipfile

import decord
import webdataset as wds
import numpy as np
import torch
from torch.utils.data.dataset import IterableDataset, ChainDataset
from decord import VideoReader
from lavis.common.registry import registry
from lavis.datasets.datasets.base_dataset import ConcatDataset
from tqdm import tqdm
import cv2

decord.bridge.set_bridge("torch")
MAX_INT = registry.get("MAX_INT")

# add for loading video
def load_video(video_path, n_frms=MAX_INT, height=-1, width=-1, sampling="uniform", clip_proposal=None):
    vr = VideoReader(uri=video_path, height=height, width=width)
    vlen = len(vr)
    n_frms = min(n_frms, vlen)
    fps = vr.get_avg_fps()
    if clip_proposal is None:
        start, end = 0, vlen
    else:
        start, end = int(clip_proposal[0]*fps), int(clip_proposal[1]*fps)
        if start < 0:
            start = 0
        if end > vlen:
            end = vlen

    intervals = np.linspace(start=start, stop=end, num=n_frms + 1).astype(int)
    ranges = []
    for idx, interv in enumerate(intervals[:-1]):
        ranges.append((interv, intervals[idx + 1]))

    if sampling == 'random':
        indices = []
        for x in ranges:
            if x[0] == x[1]:
                indices.append(x[0])
            else:
                indices.append(rnd.choice(range(x[0], x[1])))
    elif sampling == 'uniform':

        indices = [(x[0] + x[1]) // 2 for x in ranges]

    elif sampling == "headtail":
        indices_h = sorted(rnd.sample(range(vlen // 2), n_frms // 2))
        indices_t = sorted(rnd.sample(range(vlen // 2, vlen), n_frms // 2))
        indices = indices_h + indices_t
    else:
        raise NotImplementedError

    if len(indices) < n_frms:
        rest = [indices[-1] for i in range(n_frms - len(indices))]
        indices = indices + rest
    # get_batch -> T, H, W, C
    frms = vr.get_batch(indices).permute(3, 0, 1, 2).float()  # (C, T, H, W)

    return frms, indices, fps

def load_video_demo(video_path, n_frms=MAX_INT, height=-1, width=-1, sampling="uniform", clip_proposal=None):
    vr = VideoReader(uri=video_path, height=height, width=width)
    vlen = len(vr)
    n_frms = min(n_frms, vlen)
    fps = vr.get_avg_fps()
    if clip_proposal is None:
        start, end = 0, vlen
    else:
        start, end = int(clip_proposal[0]*fps), int(clip_proposal[1]*fps)
        if start < 0:
            start = 0
        if end > vlen:
            end = vlen

    intervals = np.linspace(start=start, stop=end, num=n_frms + 1).astype(int)
    ranges = []
    for idx, interv in enumerate(intervals[:-1]):
        ranges.append((interv, intervals[idx + 1]))

    if sampling == 'random':
        indices = []
        for x in ranges:
            if x[0] == x[1]:
                indices.append(x[0])
            else:
                indices.append(rnd.choice(range(x[0], x[1])))
    elif sampling == 'uniform':

        indices = [(x[0] + x[1]) // 2 for x in ranges]

    elif sampling == "headtail":
        indices_h = sorted(rnd.sample(range(vlen // 2), n_frms // 2))
        indices_t = sorted(rnd.sample(range(vlen // 2, vlen), n_frms // 2))
        indices = indices_h + indices_t
    else:
        raise NotImplementedError

    if len(indices) < n_frms:
        rest = [indices[-1] for i in range(n_frms - len(indices))]
        indices = indices + rest
    # get_batch -> T, H, W, C

    frms = vr.get_batch(indices)
    frms = frms.asnumpy()
    frms = torch.from_numpy(frms)
    frms = frms.permute(3, 0, 1, 2).float()  # (C, T, H, W)

    return frms, indices, fps, vlen

def apply_to_sample(f, sample):
    if len(sample) == 0:
        return {}

    def _apply(x):
        if torch.is_tensor(x):
            return f(x)
        elif isinstance(x, dict):
            return {key: _apply(value) for key, value in x.items()}
        elif isinstance(x, list):
            return [_apply(x) for x in x]
        else:
            return x

    return _apply(sample)


def move_to_cuda(sample):
    def _move_to_cuda(tensor):
        return tensor.cuda()

    return apply_to_sample(_move_to_cuda, sample)


def prepare_sample(samples, cuda_enabled=True):
    if cuda_enabled:
        samples = move_to_cuda(samples)

    # TODO fp16 support

    return samples


def reorg_datasets_by_split(datasets):
    """
    Organizes datasets by split.

    Args:
        datasets: dict of torch.utils.data.Dataset objects by name.

    Returns:
        Dict of datasets by split {split_name: List[Datasets]}.
    """
    # if len(datasets) == 1:
    #     return datasets[list(datasets.keys())[0]]
    # else:
    reorg_datasets = dict()

    # reorganize by split
    for _, dataset in datasets.items():
        for split_name, dataset_split in dataset.items():
            if split_name not in reorg_datasets:
                reorg_datasets[split_name] = [dataset_split]
            else:
                reorg_datasets[split_name].append(dataset_split)

    return reorg_datasets


def concat_datasets(datasets):
    """
    Concatenates multiple datasets into a single dataset.

    It supports may-style datasets and DataPipeline from WebDataset. Currently, does not support
    generic IterableDataset because it requires creating separate samplers.

    Now only supports conctenating training datasets and assuming validation and testing
    have only a single dataset. This is because metrics should not be computed on the concatenated
    datasets.

    Args:
        datasets: dict of torch.utils.data.Dataset objects by split.

    Returns:
        Dict of concatenated datasets by split, "train" is the concatenation of multiple datasets,
        "val" and "test" remain the same.

        If the input training datasets contain both map-style and DataPipeline datasets, returns
        a tuple, where the first element is a concatenated map-style dataset and the second
        element is a chained DataPipeline dataset.

    """
    # concatenate datasets in the same split
    for split_name in datasets:
        if split_name != "train":
            assert (
                len(datasets[split_name]) == 1
            ), "Do not support multiple {} datasets.".format(split_name)
            datasets[split_name] = datasets[split_name][0]
        else:
            iterable_datasets, map_datasets = [], []
            for dataset in datasets[split_name]:
                if isinstance(dataset, wds.DataPipeline):
                    logging.info(
                        "Dataset {} is IterableDataset, can't be concatenated.".format(
                            dataset
                        )
                    )
                    iterable_datasets.append(dataset)
                elif isinstance(dataset, IterableDataset):
                    raise NotImplementedError(
                        "Do not support concatenation of generic IterableDataset."
                    )
                else:
                    map_datasets.append(dataset)

            # if len(iterable_datasets) > 0:
            # concatenate map-style datasets and iterable-style datasets separately
            chained_datasets = (
                ChainDataset(iterable_datasets) if len(iterable_datasets) > 0 else None
            )
            concat_datasets = (
                ConcatDataset(map_datasets) if len(map_datasets) > 0 else None
            )

            train_datasets = concat_datasets, chained_datasets
            train_datasets = tuple([x for x in train_datasets if x is not None])
            train_datasets = (
                train_datasets[0] if len(train_datasets) == 1 else train_datasets
            )

            datasets[split_name] = train_datasets

    return datasets


def extract_archive(from_path, to_path=None, overwrite=False):
    """Extract archive.

    Args:
        from_path: the path of the archive.
        to_path: the root path of the extracted files (directory of from_path)
        overwrite: overwrite existing files (False)

    Returns:
        List of paths to extracted files even if not overwritten.

    Examples:
        >>> url = 'http://www.quest.dcs.shef.ac.uk/wmt16_files_mmt/validation.tar.gz'
        >>> from_path = './validation.tar.gz'
        >>> to_path = './'
        >>> torchtext.utils.download_from_url(url, from_path)
        >>> torchtext.utils.extract_archive(from_path, to_path)
        >>> ['.data/val.de', '.data/val.en']
        >>> torchtext.utils.download_from_url(url, from_path)
        >>> torchtext.utils.extract_archive(from_path, to_path)
        >>> ['.data/val.de', '.data/val.en']

    """

    if to_path is None:
        to_path = os.path.dirname(from_path)

    if from_path.endswith((".tar.gz", ".tgz")):
        logging.info("Opening tar file {} to {}.".format(from_path, to_path))
        with tarfile.open(from_path, "r") as tar:
            files = []
            for file_ in tqdm(tar):
                file_path = os.path.join(to_path, file_.name)
                if file_.isfile():
                    files.append(file_path)
                    if os.path.exists(file_path):
                        logging.info("{} already extracted.".format(file_path))
                        if not overwrite:
                            continue
                tar.extract(file_, to_path)
            logging.info("Finished extracting tar file {}.".format(from_path))
            return files

    elif from_path.endswith(".zip"):
        assert zipfile.is_zipfile(from_path), from_path
        logging.info("Opening zip file {} to {}.".format(from_path, to_path))
        with zipfile.ZipFile(from_path, "r") as zfile:
            files = []
            for file_ in tqdm(zfile.namelist()):
                file_path = os.path.join(to_path, file_)
                files.append(file_path)
                if os.path.exists(file_path):
                    logging.info("{} already extracted.".format(file_path))
                    if not overwrite:
                        continue
                zfile.extract(file_, to_path)
        files = [f for f in files if os.path.isfile(f)]
        logging.info("Finished extracting zip file {}.".format(from_path))
        return files

    elif from_path.endswith(".gz"):
        logging.info("Opening gz file {} to {}.".format(from_path, to_path))
        default_block_size = 65536
        filename = from_path[:-3]
        files = [filename]
        with gzip.open(from_path, "rb") as gzfile, open(filename, "wb") as d_file:
            while True:
                block = gzfile.read(default_block_size)
                if not block:
                    break
                else:
                    d_file.write(block)
            d_file.write(block)
        logging.info("Finished extracting gz file {}.".format(from_path))
        return files

    else:
        raise NotImplementedError(
            "We currently only support tar.gz, .tgz, .gz and zip achives."
        )


def save_frames_grid(img_array, out_path):
    import torch
    from PIL import Image
    from torchvision.utils import make_grid

    if len(img_array.shape) == 3:
        img_array = img_array.unsqueeze(0)
    elif len(img_array.shape) == 5:
        b, t, c, h, w = img_array.shape
        img_array = img_array.view(-1, c, h, w)
    elif len(img_array.shape) == 4:
        pass
    else:
        raise NotImplementedError(
            "Supports only (b,t,c,h,w)-shaped inputs. First two dimensions can be ignored."
        )

    assert img_array.shape[1] == 3, "Exepcting input shape of (H, W, 3), i.e. RGB-only."

    grid = make_grid(img_array)
    ndarr = grid.permute(1, 2, 0).to("cpu", torch.uint8).numpy()

    img = Image.fromarray(ndarr)

    img.save(out_path)


def _open_video(video_path, num_frames):
    if num_frames <= 0:
        raise ValueError("num_frames must be greater than zero")

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        cap.release()
        raise ValueError(f"Unable to open video: {video_path}")

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_rate = float(cap.get(cv2.CAP_PROP_FPS))
    if total_frames <= 0:
        cap.release()
        raise ValueError(f"Video has no readable frames: {video_path}")
    if frame_rate <= 0:
        cap.release()
        raise ValueError(f"Video has invalid FPS ({frame_rate}): {video_path}")

    return cap, total_frames, frame_rate


def _sample_frame_indices(total_frames, frame_rate, num_frames, start_time, end_time):
    start_frame = 0 if start_time is None else int(start_time * frame_rate)
    end_frame = total_frames - 1 if end_time is None else int(end_time * frame_rate)
    start_frame = min(max(start_frame, 0), total_frames - 1)
    end_frame = min(max(end_frame, 0), total_frames - 1)
    if end_frame < start_frame:
        raise ValueError("end_time must not precede start_time")
    if num_frames == 1:
        return [start_frame]

    span = end_frame - start_frame
    return [
        round(start_frame + span * index / (num_frames - 1))
        for index in range(num_frames)
    ]


def _read_video_frames(cap, frame_indices, target_height, target_width):
    frames = []
    for frame_index in frame_indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        success, frame = cap.read()
        if not success or frame is None:
            raise ValueError(f"Unable to read video frame {frame_index}")
        frames.append(cv2.resize(frame, (target_width, target_height)))
    if not frames:
        raise ValueError("No video frames were read")
    return frames


def _frames_to_tensor(frames):
    return torch.stack(
        [torch.tensor(frame).permute(2, 0, 1).float() for frame in frames],
        dim=1,
    )


def uniform_frame_sampling(video_path, num_frames, target_height, target_width, start_time=None, end_time=None):
    cap, total_frames, frame_rate = _open_video(video_path, num_frames)
    try:
        frame_indices = _sample_frame_indices(
            total_frames, frame_rate, num_frames, start_time, end_time
        )
        frames = _read_video_frames(
            cap, frame_indices, target_height, target_width
        )
    finally:
        cap.release()
    return _frames_to_tensor(frames)


def head_tail_frame_sampling(video_path, num_frames, target_height, target_width, start_time=None, end_time=None):
    cap, total_frames, frame_rate = _open_video(video_path, num_frames)
    try:
        frame_indices = _sample_frame_indices(
            total_frames, frame_rate, num_frames, start_time, end_time
        )
        frames = _read_video_frames(
            cap, frame_indices, target_height, target_width
        )
    finally:
        cap.release()
    return _frames_to_tensor(frames)


def load_clip(video_path, num_frames, target_height, target_width, start_time=None, end_time=None, sampling="headtail"):
    if sampling == "headtail":
        return head_tail_frame_sampling(video_path, num_frames, target_height, target_width, start_time, end_time)
    elif sampling == "uniform":
        return uniform_frame_sampling(video_path, num_frames, target_height, target_width, start_time, end_time)
    else:
        raise NotImplementedError
