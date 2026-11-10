def create_network(client, headers):
    response = client.post("/api/v1/networks", headers=headers, json={"name": "Global Media Network", "default_locale": "en"})
    assert response.status_code == 201
    return response.json()["id"]

def test_agent_catalogue_is_available(client, auth_headers):
    response = client.get("/api/v1/agents", headers=auth_headers)
    assert response.status_code == 200
    assert {agent["id"] for agent in response.json()} >= {"research", "writer", "publisher"}

def test_internal_task_enters_queue(client, auth_headers):
    network_id = create_network(client, auth_headers)
    response = client.post(
        f"/api/v1/networks/{network_id}/tasks",
        headers=auth_headers,
        json={"agent_id": "research", "title": "Find channel opportunities", "instruction": "Research audience demand in educational technology."},
    )
    assert response.status_code == 201
    assert response.json()["status"] == "queued"
    assert response.json()["external_action"] is False

def test_external_action_is_blocked_until_approval(client, auth_headers):
    network_id = create_network(client, auth_headers)
    created = client.post(
        f"/api/v1/networks/{network_id}/tasks",
        headers=auth_headers,
        json={"agent_id": "publisher", "title": "Publish episode", "instruction": "Upload the approved episode to YouTube.", "external_action": True},
    )
    assert created.status_code == 201
    task = created.json()
    assert task["status"] == "awaiting_approval"
    approvals = client.get(f"/api/v1/networks/{network_id}/approvals?status=pending", headers=auth_headers)
    assert approvals.status_code == 200 and len(approvals.json()) == 1
    approval = approvals.json()[0]
    decision = client.post(
        f"/api/v1/approvals/{approval['id']}/decision",
        headers=auth_headers,
        json={"decision": "approved", "note": "Reviewed by channel owner."},
    )
    assert decision.status_code == 200
    assert decision.json()["status"] == "approved"
    tasks = client.get(f"/api/v1/networks/{network_id}/tasks", headers=auth_headers)
    assert tasks.status_code == 200 and tasks.json()[0]["status"] == "queued"
    duplicate = client.post(
        f"/api/v1/approvals/{approval['id']}/decision",
        headers=auth_headers,
        json={"decision": "rejected"},
    )
    assert duplicate.status_code == 409

def test_external_action_can_be_rejected(client, auth_headers):
    network_id = create_network(client, auth_headers)
    created = client.post(
        f"/api/v1/networks/{network_id}/tasks",
        headers=auth_headers,
        json={"agent_id": "community", "title": "Reply to comment", "instruction": "Post a public reply to a viewer.", "external_action": True},
    ).json()
    approval = client.get(f"/api/v1/networks/{network_id}/approvals", headers=auth_headers).json()[0]
    result = client.post(
        f"/api/v1/approvals/{approval['id']}/decision",
        headers=auth_headers,
        json={"decision": "rejected", "note": "Needs rewriting."},
    )
    assert result.status_code == 200
    tasks = client.get(f"/api/v1/networks/{network_id}/tasks", headers=auth_headers).json()
    assert next(x for x in tasks if x["id"] == created["id"])["status"] == "cancelled"

def test_unknown_agent_and_cross_network_channel_are_rejected(client, auth_headers):
    network_id = create_network(client, auth_headers)
    second_network_id = create_network(client, auth_headers)
    channel = client.post(
        f"/api/v1/networks/{second_network_id}/channels",
        headers=auth_headers,
        json={"name": "Other Channel", "slug": "other-channel"},
    ).json()
    unknown = client.post(
        f"/api/v1/networks/{network_id}/tasks",
        headers=auth_headers,
        json={"agent_id": "unknown", "title": "Invalid task", "instruction": "This should fail."},
    )
    assert unknown.status_code == 422
    foreign = client.post(
        f"/api/v1/networks/{network_id}/tasks",
        headers=auth_headers,
        json={"channel_id": channel["id"], "agent_id": "research", "title": "Foreign channel", "instruction": "This should fail."},
    )
    assert foreign.status_code == 404



def test_agent_catalogue_exposes_versioned_zero_paid_provider_profiles(client, auth_headers):
    response = client.get("/api/v1/agents", headers=auth_headers)
    assert response.status_code == 200
    agents = response.json()
    assert len(agents) == 9
    assert all(agent["registry_version"] == "1.0.0" for agent in agents)
    assert all(agent["skill_version"] == "1.0.0" for agent in agents)
    assert all(agent["execution_mode"] == "local_planning_only" for agent in agents)
    assert all(agent["allowed_tools"] == [] for agent in agents)
    assert all(agent["external_writes"] is False for agent in agents)
    assert all(agent["max_paid_provider_cost_usd"] == 0 for agent in agents)
    assert len({agent["skill_id"] for agent in agents}) == len(agents)



def test_task_accepts_bounded_producer_script_payload(client, auth_headers):
    network_id = create_network(client, auth_headers)
    response = client.post(
        f"/api/v1/networks/{network_id}/tasks",
        headers=auth_headers,
        json={"agent_id":"producer","title":"Render episode",
              "instruction":"Render this supplied script locally.",
              "input_payload":{"script":{"title":"A test","hook":"Hook","body":"Body","conclusion":"End"}}},
    )
    assert response.status_code == 201
    assert response.json()["status"] == "queued"


def test_task_rejects_oversized_input_payload(client, auth_headers):
    network_id = create_network(client, auth_headers)
    response = client.post(
        f"/api/v1/networks/{network_id}/tasks",
        headers=auth_headers,
        json={"agent_id":"producer","title":"Render episode",
              "instruction":"Render this supplied script locally.",
              "input_payload":{"script":{"body":"x" * 40000}}},
    )
    assert response.status_code == 422
