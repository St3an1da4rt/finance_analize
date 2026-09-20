import base64
import json
from pathlib import Path

from openai import OpenAI
from pydantic import BaseModel, Field

from app import config
from app.models import Category

MIME_BY_EXT = {ext: mime for mime, ext in config.ALLOWED_IMAGE_TYPES.items()}


class ExtractedOperation(BaseModel):
    """Fields of an `operations` DB record that can be read from an image."""

    category: Category | None = Field(
        description="Best matching category. null if none of the categories clearly applies."
    )
    amount: float | None = Field(
        description="Total amount as a positive number, without currency symbol. "
        "null if not visible."
    )
    description: str | None = Field(
        description="Short summary: merchant / counterparty and what the payment was for. "
        "null if not visible."
    )


CATEGORY_DESCRIPTIONS = {
    Category.transfer: "money sent to / received from a person or between accounts",
    Category.salary: "income from an employer",
    Category.groceries: "supermarkets, food shops, markets",
    Category.restaurants: "restaurants, cafes, bars, food delivery",
    Category.transport: "taxi, public transport, fuel, parking, car services",
    Category.housing: "rent, mortgage, home maintenance, furniture",
    Category.utilities: "electricity, water, gas, internet, phone",
    Category.health: "pharmacies, doctors, clinics, insurance, fitness",
    Category.entertainment: "cinema, events, games, hobbies",
    Category.shopping: "clothes, electronics, household goods, marketplaces",
    Category.travel: "flights, hotels, tours, visas",
    Category.education: "courses, tuition, books",
    Category.subscriptions: "recurring digital services and memberships",
}
CATEGORY_HINTS = "\n".join(f"- {c.value}: {CATEGORY_DESCRIPTIONS[c]}" for c in Category)

SYSTEM_PROMPT = f"""\
You extract data from an image of a financial document (receipt, bank transfer \
screenshot, payslip, etc.) and fill in one record of the `operations` database table.

Record format (JSON Schema of the fields you must return):
{json.dumps(ExtractedOperation.model_json_schema(), indent=2)}

Allowed categories:
{CATEGORY_HINTS}

Never guess: if a value is not visible in the image, or no category clearly applies, return null.
"""


def extract_operation(image_path: Path, client: OpenAI | None = None) -> ExtractedOperation:
    """Ask OpenAI to read an operation record from an image file."""
    mime = MIME_BY_EXT[image_path.suffix.lower()]
    data = base64.b64encode(image_path.read_bytes()).decode()
    if client is None:
        if not config.OPENAI_TOKEN:
            raise RuntimeError("OPENAI_TOKEN is not set; add it to .env")
        client = OpenAI(api_key=config.OPENAI_TOKEN)

    completion = client.chat.completions.parse(
        model=config.OPENAI_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Extract the operation record from this image."},
                    {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{data}"}},
                ],
            },
        ],
        response_format=ExtractedOperation,
    )
    message = completion.choices[0].message
    if message.parsed is None:
        raise ValueError(f"Model returned no structured data: {message.refusal}")
    return message.parsed
