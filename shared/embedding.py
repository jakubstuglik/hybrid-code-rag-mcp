from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import config


def get_embed_model():
    """Get the embedding model based on config."""
    return HuggingFaceEmbedding(
        model_name=config.MODEL_NAME,
        device=config.INDEX_EMBED_DEVICE,
        model_kwargs=config.EMBED_MODEL_KWARGS,
    )
