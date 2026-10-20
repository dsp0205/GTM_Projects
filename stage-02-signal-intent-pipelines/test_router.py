import pytest
from fastapi.testclient import TestClient
import router

TARGETS = """domain,name,segment
acme.com,Acme Corp,enterprise
smallshop.io,Small Shop,smb
"""


@pytest.fixture()
def client(tmp_path, monkeypatch):
    (tmp_path / "targets.csv").write_text(TARGETS, encoding="utf-8")
    monkeypatch.setattr(router, "TARGETS_CSV", str(tmp_path / "targets.csv"))
    monkeypatch.setattr(router, "DB_PATH", str(tmp_path / "t.db"))
    monkeypatch.setattr(router, "SHARED_SECRET", "")
    sent = []
    monkeypatch.setattr(router, "post_to_slack", sent.append)
    c = TestClient(router.app)
    c.sent = sent
    return c


def evt(mid, visitor, domain="acme.com", path="/pricing"):
    return {"type": "page", "messageId": mid, "anonymousId": visitor,
            "properties": {"path": path, "company_domain": domain}}


def post(client, *args, **kw):
    return client.post("/events", json=evt(*args, **kw)).json()["status"]


def test_third_visitor_alerts_once_and_replays_are_ignored(client):
    out = [post(client, f"m{i}", f"v{i}") for i in range(5)]
    assert out == ["counted", "counted", "alerted", "counted", "counted"]
    assert post(client, "m0", "v0") == "duplicate"
    assert len(client.sent) == 1


def test_same_visitor_same_day_counts_once(client):
    assert [post(client, f"m{i}", "v1") for i in range(5)] == ["counted"] * 5


def test_non_target_and_non_pricing_ignored(client):
    assert post(client, "a", "v", "smallshop.io") == "not a target"
    assert post(client, "b", "v", path="/blog") == "ignored"


def test_bad_signature_is_rejected(client, monkeypatch):
    monkeypatch.setattr(router, "SHARED_SECRET", "s3cret")
    assert client.post("/events", json=evt("x", "v")).status_code == 401
    assert client.post("/events", json=evt("x", "v"),
                       headers={"x-signature": "bad"}).status_code == 401


def test_missing_message_id_is_400(client):
    assert client.post("/events", json={"type": "page"}).status_code == 400
