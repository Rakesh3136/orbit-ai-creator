from types import SimpleNamespace
from aimn_api.main import app
from aimn_api.db import get_db
from aimn_api.models import AgentTask


def _complete_task(task_id):
    generator = app.dependency_overrides[get_db]()
    db = next(generator)
    try:
        task = db.get(AgentTask, task_id)
        task.status = "completed"
        task.result = {"skill_version": "1.0.0", "registry_version": "1.0.0"}
        db.commit()
    finally:
        generator.close()


def test_evaluation_requires_completed_internal_task_and_owner_approves_lesson(client, auth_headers, monkeypatch):
    import aimn_api.api as api_module
    monkeypatch.setattr(api_module, "settings", SimpleNamespace(owner_email="owner@example.test"))
    network = client.post("/api/v1/networks", headers=auth_headers, json={"name": "Feedback network"}).json()
    task = client.post(f"/api/v1/networks/{network['id']}/tasks", headers=auth_headers,
        json={"agent_id": "research", "title": "Research task", "instruction": "Prepare a topic brief."}).json()
    _complete_task(task["id"])
    created = client.post(f"/api/v1/networks/{network['id']}/tasks/{task['id']}/evaluation",
        headers=auth_headers, json={"rating": 5, "correction": "Add source dates.", "lesson": "Cite dated primary sources."})
    assert created.status_code == 201
    evaluation = created.json()
    assert evaluation["lesson_status"] == "pending"
    assert evaluation["reviewer_email"] == "owner@example.test"
    assert evaluation["skill_id"] == "research.topic_discovery"
    assert evaluation["skill_version"] == "1.0.0"
    decision = client.post(f"/api/v1/evaluations/{evaluation['id']}/lesson-decision",
        headers=auth_headers, json={"decision": "approved", "note": "Verified useful."})
    assert decision.status_code == 200
    assert decision.json()["lesson_status"] == "approved"
    duplicate = client.post(f"/api/v1/networks/{network['id']}/tasks/{task['id']}/evaluation",
        headers=auth_headers, json={"rating": 4})
    assert duplicate.status_code == 409


def test_external_action_task_cannot_be_evaluated(client, auth_headers, monkeypatch):
    import aimn_api.api as api_module
    monkeypatch.setattr(api_module, "settings", SimpleNamespace(owner_email="owner@example.test"))
    network = client.post("/api/v1/networks", headers=auth_headers, json={"name": "External guard"}).json()
    task = client.post(f"/api/v1/networks/{network['id']}/tasks", headers=auth_headers,
        json={"agent_id": "publisher", "title": "Publish", "instruction": "Publish only after approval.", "external_action": True}).json()
    response = client.post(f"/api/v1/networks/{network['id']}/tasks/{task['id']}/evaluation",
        headers=auth_headers, json={"rating": 5})
    assert response.status_code == 409
