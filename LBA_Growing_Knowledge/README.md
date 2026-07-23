# LBA_Growing_Knowledge
Knowledge Learning by Asking


## Install

```bash
git clone https://github.com/greeksharifa/LBA_Growing_Knowledge.git

git submodule foreach init
git submodule foreach update

# git submodule foreach 'git pull'
```

**참고: git submodule** 

- https://github.com/madeleinegrunde/AGQA_baselines_code
- https://github.com/JingweiJ/ActionGenome.git
- https://github.com/csbobby/STAR_Benchmark.git


- https://data-engineer-tech.tistory.com/20


### AGQA benchmarks erorr resolution

- https://ssaru.github.io/2021/05/05/20210505-til_install_rtx3090_supported_pytorch/
- https://kingnamji.tistory.com/57
- https://bluecolorsky.tistory.com/71
- https://developer.nvidia.com/cuda-gpus
- https://chaloalto.tistory.com/23
- https://yjs-program.tistory.com/294?category=804886
- https://stackoverflow.com/questions/58194852/modulenotfounderror-no-module-named-numpy-core-multiarray-r


### Requirements
```bash
conda install -c conda-forge spacy
python -m spacy download en
```

## Data Preparation

- Download Charades RGB frames at 24fps
```bash
cd /home/{username}/data/Charades/
wget https://ai2-public-datasets.s3-us-west-2.amazonaws.com/charades/Charades_v1_rgb.tar
tar -xvf Charades_v1_rgb.tar
```


- AGQA: https://cs.stanford.edu/people/ranjaykrishna/agqa/
- Action Genome: https://www.actiongenome.org/#download
- Charades: https://prior.allenai.org/projects/charades
- STAR Benchmark: https://bobbywu.com/STAR/#repo

### Action Genome
data에 대한 symbolic link 생성
```bash
ln -s <original path> <link path>
ln -s ~/data/Charades/Charades_v1_480/  dataset/ag/videos
ln -s ~/data/Action_Genome/annotations/ dataset/ag/annotations
```

### STAR Benchmark

- homepage: https://bobbywu.com/STAR/
- code: https://github.com/csbobby/STAR_Benchmark

---

## challenge

- STAR: https://eval.ai/web/challenges/challenge-page/1325/overview