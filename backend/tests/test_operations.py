from app.models import Category, Operation, OperationSource


def seed(session_factory, n, category=None):
    with session_factory() as db:
        db.add_all(
            Operation(source=OperationSource.image, file_path=f"{i}.jpg", category=category)
            for i in range(n)
        )
        db.commit()


def test_empty(client):
    r = client.get("/operations")
    assert r.status_code == 200
    assert r.json() == {"items": [], "total": 0, "limit": 20, "offset": 0}


def test_first_page(client, session_factory):
    seed(session_factory, 45)
    body = client.get("/operations?limit=20&offset=0").json()
    assert len(body["items"]) == 20
    assert body["total"] == 45
    ids = [i["id"] for i in body["items"]]
    assert ids == sorted(ids, reverse=True)


def test_last_partial_page(client, session_factory):
    seed(session_factory, 45)
    assert len(client.get("/operations?limit=20&offset=40").json()["items"]) == 5


def test_invalid_params(client):
    assert client.get("/operations?limit=1000").status_code == 422
    assert client.get("/operations?limit=0").status_code == 422
    assert client.get("/operations?offset=-1").status_code == 422


def test_category_in_response(client, session_factory):
    seed(session_factory, 1, Category.salary)
    assert client.get("/operations").json()["items"][0]["category"] == "salary"


def test_date_filter(client, session_factory):
    from datetime import datetime, timezone

    with session_factory() as db:
        for day in (1, 10, 20):
            db.add(
                Operation(
                    source=OperationSource.image,
                    file_path=f"{day}.jpg",
                    created_at=datetime(2026, 1, day, tzinfo=timezone.utc),
                )
            )
        db.commit()

    body = client.get("/operations?date_from=2026-01-05T00:00:00&date_to=2026-01-15T00:00:00").json()
    assert body["total"] == 1
    assert client.get("/operations?date_from=2026-01-10T00:00:00").json()["total"] == 2
    assert client.get("/operations?date_to=2026-01-10T00:00:00Z").json()["total"] == 2
    assert client.get("/operations?date_from=2026-02-01&date_to=2026-01-01").status_code == 422
