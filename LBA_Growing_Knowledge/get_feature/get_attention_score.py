"""
reference
- https://torchmetrics.readthedocs.io/en/stable/pairwise/cosine_similarity.html
"""

from sentence_transformers import SentenceTransformer
import torch
from torchmetrics.functional import pairwise_cosine_similarity

sbert_model = SentenceTransformer('paraphrase-MiniLM-L6-v2')


def get_attention_score(knowledge_sentences:list, phrases_sentences:list) -> torch.Tensor:
    knowledge_embeddings = torch.Tensor(sbert_model.encode(knowledge_sentences))
    phrase_embeddings = torch.Tensor(sbert_model.encode(phrases_sentences))

    return pairwise_cosine_similarity(knowledge_embeddings, phrase_embeddings)


def main():
    # sample
    x = torch.tensor([[2, 3], [3, 5], [5, 8]], dtype=torch.float32)
    y = torch.tensor([[1, 0], [2, 1]], dtype=torch.float32)
    print(pairwise_cosine_similarity(x, y))
    print(pairwise_cosine_similarity(x))

    # Sentences we want to encode. Example:
    sentence = ['This framework generates embeddings for each input sentence']
    # Sentences are encoded by calling model.encode()
    embedding = sbert_model.encode(sentence)
    print('sentence embedding.shape:', embedding.shape)
    # print(embedding)

    sentences = [
        'This framework generates embeddings for each input sentence',
        'This is a sample text',
        'I have a pencil',
    ]
    embedding = sbert_model.encode(sentences)
    print('sentences embedding.shape:', embedding.shape)

    sentences2 = [
        'This framework generates embeddings for each input sentence.',
        'This is a gorgeous sample text.',
        'I have a apple pencil.',
        'I have a pineapple pencil.',
    ]
    embedding2 = sbert_model.encode(sentences2)
    print('sentences2 embedding2.shape:', embedding2.shape)

    result = get_attention_score(sentences, sentences2)
    print('result.shape:', result.shape)
    print(result)


if __name__ == "__main__":
    main()
