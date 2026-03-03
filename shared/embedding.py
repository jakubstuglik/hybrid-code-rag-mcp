from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import config


def get_embed_model(device: str | None = None) -> HuggingFaceEmbedding:
    """Get the embedding model based on config."""
    return HuggingFaceEmbedding(
        model_name=config.MODEL_NAME,
        device=device or config.INDEX_EMBED_DEVICE,
        model_kwargs=config.EMBED_MODEL_KWARGS,
    )
