import json
from pathlib import Path

from openai import OpenAI
from pydantic import BaseModel, Field

from app import config
from app.services.extraction import CATEGORY_HINTS, ExtractedOperation
from app.services.openai_client import get_client


class ExtractedOperations(BaseModel):
    """Every purchase described in one voice note."""

    operations: list[ExtractedOperation] = Field(
        description="One record per purchase mentioned, in the order they are spoken. "
        "Empty list if the note describes no purchase at all."
    )


SYSTEM_PROMPT = f"""\
You read a transcript of a voice note in which a person describes their spending, \
and fill in one record of the `operations` database table per purchase mentioned.

Response format (JSON Schema of what you must return):
{json.dumps(ExtractedOperations.model_json_schema(), indent=2)}

Allowed categories:
{CATEGORY_HINTS}

Never guess: if a value is not mentioned, or no category clearly applies, return null.
Split the note into separate records only for genuinely separate purchases; \
do not split one purchase that is described in several sentences.
"""


def transcribe_audio(audio_path: Path, client: OpenAI | None = None) -> str:
    """Transcribe a voice note to plain text."""
    client = get_client(client)
    with audio_path.open("rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model=config.OPENAI_TRANSCRIBE_MODEL,
            file=audio_file,
            language="ru",  # known in advance: faster and more accurate
        )
    return transcript.text


def extract_operations(text: str, client: OpenAI | None = None) -> list[ExtractedOperation]:
    """Ask OpenAI to read operation records from a transcript."""
    client = get_client(client)
    completion = client.chat.completions.parse(
        model=config.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ],
        response_format=ExtractedOperations,
    )
    message = completion.choices[0].message
    if message.parsed is None:
        raise ValueError(f"Model returned no structured data: {message.refusal}")
    return message.parsed.operations


def extract_audio_operations(
    audio_path: Path, client: OpenAI | None = None
) -> list[ExtractedOperation]:
    """Full pipeline: voice note -> transcript -> operation records."""
    client = get_client(client)
    return extract_operations(transcribe_audio(audio_path, client), client)
