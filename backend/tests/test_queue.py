import asyncio

from app import config
from app.models import Category
from app.services.extraction import ExtractedOperation
from app.services.queue import ExtractionQueue, process_operation


def upload_image(client):
    r = client.post("/images", files={"file": ("f", b"data", "image/jpeg")})
    assert r.status_code == 201
    return r.json()


def upload_audio(client):
    r = client.post("/audio", files={"file": ("f", b"data", "audio/ogg")})
    assert r.status_code == 201
    return r.json()


def get_operation(client, operation_id):
    return next(i for i in client.get("/operations").json()["items"] if i["id"] == operation_id)


def test_image_upload_is_enqueued_and_pending(client, fake_queue):
    body = upload_image(client)
    assert body["status"] == "pending"
    assert body["category"] is None
    assert fake_queue.ids == [body["id"]]


def test_audio_upload_is_enqueued_and_pending(client, fake_queue):
    body = upload_audio(client)
    assert body["status"] == "pending"
    assert body["category"] is None
    assert fake_queue.ids == [body["id"]]


def test_process_fills_extracted_fields(client, monkeypatch):
    seen = []

    def fake(path):
        seen.append(path)
        return ExtractedOperation(category=Category.restaurants, amount=12.5, description="Coffee")

    monkeypatch.setattr("app.services.queue.extract_operation", fake)
    op_id = upload_image(client)["id"]
    process_operation(op_id)

    op = get_operation(client, op_id)
    assert (op["status"], op["category"], op["description"]) == ("done", "restaurants", "Coffee")
    assert float(op["amount"]) == 12.5
    assert seen == [next(config.UPLOAD_DIR.iterdir())]


def test_audio_note_fans_out_into_one_operation_per_expense(client, monkeypatch):
    seen = []

    def fake(path):
        seen.append(path)
        return [
            ExtractedOperation(category=Category.restaurants, amount=300, description="Кофе"),
            ExtractedOperation(category=Category.transport, amount=500, description="Такси"),
        ]

    monkeypatch.setattr("app.services.queue.extract_audio_operations", fake)
    op_id = upload_audio(client)["id"]
    process_operation(op_id)

    items = client.get("/operations").json()["items"]
    assert [(i["category"], i["description"], float(i["amount"])) for i in items] == [
        ("transport", "Такси", 500.0),
        ("restaurants", "Кофе", 300.0),
    ]
    assert {i["status"] for i in items} == {"done"}
    assert {i["source"] for i in items} == {"audio"}
    assert seen == [next(config.UPLOAD_DIR.iterdir())]  # one file, shared by both operations


def test_audio_note_without_expenses_stays_empty(client, monkeypatch):
    monkeypatch.setattr("app.services.queue.extract_audio_operations", lambda path: [])
    op_id = upload_audio(client)["id"]
    process_operation(op_id)

    op = get_operation(client, op_id)
    assert (op["status"], op["category"], op["amount"]) == ("done", None, None)
    assert len(client.get("/operations").json()["items"]) == 1


def test_process_failure_marks_failed(client, monkeypatch):
    def boom(path):
        raise RuntimeError("openai down")

    monkeypatch.setattr("app.services.queue.extract_operation", boom)
    op_id = upload_image(client)["id"]
    process_operation(op_id)

    op = get_operation(client, op_id)
    assert op["status"] == "failed"
    assert op["category"] is None
    assert len(list(config.UPLOAD_DIR.iterdir())) == 1


def test_process_skips_finished_operation(client, monkeypatch):
    op_id = upload_image(client)["id"]
    process_operation(op_id)
    monkeypatch.setattr(
        "app.services.queue.extract_operation", lambda p: 1 / 0
    )  # would mark failed if it ran again
    process_operation(op_id)
    assert get_operation(client, op_id)["status"] == "done"


def test_worker_processes_enqueued_and_restart_recovers_pending(client):
    first = upload_image(client)["id"]  # pending in DB, never enqueued (fake queue)
    second = upload_image(client)["id"]

    async def run():
        q = ExtractionQueue()
        await q.start()  # re-enqueues pending image operations
        await q.join()
        await q.stop()

    asyncio.run(run())
    assert get_operation(client, first)["status"] == "done"
    assert get_operation(client, second)["status"] == "done"
