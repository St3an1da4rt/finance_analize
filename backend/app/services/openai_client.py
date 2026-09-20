from openai import OpenAI

from app import config


def get_client(client: OpenAI | None = None) -> OpenAI:
    """Return the passed-in client, or build one from the configured token."""
    if client is not None:
        return client
    if not config.OPENAI_TOKEN:
        raise RuntimeError("OPENAI_TOKEN is not set; add it to .env")
    return OpenAI(api_key=config.OPENAI_TOKEN)
