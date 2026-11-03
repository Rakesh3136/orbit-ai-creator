def create_network(client, headers):
    response = client.post("/api/v1/networks", headers=headers, json={"name": "Global Media Network", "default_locale": "en"})
    assert response.status_code == 201
    return response.json()["id"]

def test_management_routes_require_api_key(client):
    assert client.get("/api/v1/networks").status_code == 401

def test_create_and_list_channels(client, auth_headers):
    network_id = create_network(client, auth_headers)
    response = client.post(
        f"/api/v1/networks/{network_id}/channels",
        headers=auth_headers,
        json={"name": "Future Explained", "slug": "future-explained", "niche": "Technology", "primary_language": "EN", "target_regions": ["us", "gb"]},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["primary_language"] == "en"
    assert body["target_regions"] == ["US", "GB"]
    assert body["connected"] is False
    assert "credential_ref" not in body
    listed = client.get(f"/api/v1/networks/{network_id}/channels", headers=auth_headers)
    assert listed.status_code == 200 and len(listed.json()) == 1

def test_duplicate_slug_conflicts(client, auth_headers):
    network_id = create_network(client, auth_headers)
    path = f"/api/v1/networks/{network_id}/channels"
    payload = {"name": "Channel One", "slug": "shared-slug"}
    assert client.post(path, headers=auth_headers, json=payload).status_code == 201
    payload["name"] = "Channel Two"
    assert client.post(path, headers=auth_headers, json=payload).status_code == 409

def test_update_and_network_scope(client, auth_headers):
    network_id = create_network(client, auth_headers)
    item = client.post(
        f"/api/v1/networks/{network_id}/channels",
        headers=auth_headers,
        json={"name": "Science Daily", "slug": "science-daily"},
    ).json()
    changed = client.patch(
        f"/api/v1/networks/{network_id}/channels/{item['id']}",
        headers=auth_headers,
        json={"status": "paused", "niche": "Science"},
    )
    assert changed.status_code == 200 and changed.json()["status"] == "paused"
    missing = client.get(
        f"/api/v1/networks/00000000-0000-0000-0000-000000000000/channels/{item['id']}",
        headers=auth_headers,
    )
    assert missing.status_code == 404

def test_invalid_slug_rejected(client, auth_headers):
    network_id = create_network(client, auth_headers)
    response = client.post(
        f"/api/v1/networks/{network_id}/channels",
        headers=auth_headers,
        json={"name": "Invalid Slug", "slug": "Invalid Slug"},
    )
    assert response.status_code == 422
