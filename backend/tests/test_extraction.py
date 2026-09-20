from types import SimpleNamespace

import pytest

from app.models import Category
from app.services.extraction import CATEGORY_DESCRIPTIONS, ExtractedOperation, SYSTEM_PROMPT, extract_operation


class FakeClient:
    def __init__(self, parsed=None, refusal=None):
        self.calls = []
        message = SimpleNamespace(parsed=parsed, refusal=refusal)
        self._completion = SimpleNamespace(choices=[SimpleNamespace(message=message)])
        self.chat = SimpleNamespace(completions=SimpleNamespace(parse=self._parse))

    def _parse(self, **kwargs):
        self.calls.append(kwargs)
        return self._completion


@pytest.fixture
def image(tmp_path):
    p = tmp_path / "receipt.jpg"
    p.write_bytes(b"jpegdata")
    return p


def test_extract_sends_record_format_and_image(image):
    expected = ExtractedOperation(
        category=Category.transfer, amount=12.5, description="Coffee"
    )
    client = FakeClient(parsed=expected)

    assert extract_operation(image, client) == expected

    call = client.calls[0]
    assert call["response_format"] is ExtractedOperation
    assert call["messages"][0]["content"] == SYSTEM_PROMPT
    for c in Category:
        assert c.value in SYSTEM_PROMPT
    url = call["messages"][1]["content"][1]["image_url"]["url"]
    assert url.startswith("data:image/jpeg;base64,")


def test_extract_refusal(image):
    with pytest.raises(ValueError, match="nope"):
        extract_operation(image, FakeClient(refusal="nope"))


def test_every_category_is_described():
    assert set(CATEGORY_DESCRIPTIONS) == set(Category)
