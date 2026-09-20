import pytest

from app import config

CASES = {
    "images": dict(ok="image/jpeg", bad="application/pdf", limit="MAX_IMAGE_SIZE"),
    "audio": dict(ok="audio/ogg", bad="image/png", limit="MAX_AUDIO_SIZE"),
}


@pytest.fixture(params=CASES)
def case(request):
    return request.param, CASES[request.param]


def test_upload_success(client, case):
    url, c = case
    r = client.post(f"/{url}", files={"file": ("f", b"data", c["ok"])})
    assert r.status_code == 201
    body = r.json()
    assert body["status"] == "pending"
    assert body["category"] is None
    assert len(list(config.UPLOAD_DIR.iterdir())) == 1


def test_upload_missing_file(client, case):
    url, _ = case
    assert client.post(f"/{url}").status_code == 422


def test_upload_bad_type(client, case):
    url, c = case
    r = client.post(f"/{url}", files={"file": ("f", b"data", c["bad"])})
    assert r.status_code == 415
    assert client.get("/operations").json()["total"] == 0
    assert not config.UPLOAD_DIR.exists() or not list(config.UPLOAD_DIR.iterdir())


def test_upload_too_large(client, case, monkeypatch):
    url, c = case
    monkeypatch.setattr(config, c["limit"], 10)
    r = client.post(f"/{url}", files={"file": ("f", b"x" * 11, c["ok"])})
    assert r.status_code == 413
    assert client.get("/operations").json()["total"] == 0
    assert not list(config.UPLOAD_DIR.iterdir())
