"""Shared helpers for the opportunities domain tests."""

import uuid
from typing import Any

OPPORTUNITIES = "/v1/opportunities"
ACTIONS = "/v1/opportunity-actions"


def unique(prefix: str = "x") -> str:
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


def create_opportunity(client: Any, owner: dict[str, str], **fields: Any) -> Any:
    body = {"name": unique("Idea"), **fields}
    return client.post(OPPORTUNITIES, headers=owner, json=body)


def new_opportunity(
    client: Any, owner: dict[str, str], **fields: Any
) -> dict[str, Any]:
    response = create_opportunity(client, owner, **fields)
    assert response.status_code == 201, response.text
    created: dict[str, Any] = response.json()
    return created


def create_action(client: Any, owner: dict[str, str], **fields: Any) -> Any:
    body = {"url": f"https://example.com/{unique('post')}", **fields}
    return client.post(ACTIONS, headers=owner, json=body)


def new_action(client: Any, owner: dict[str, str], **fields: Any) -> dict[str, Any]:
    response = create_action(client, owner, **fields)
    assert response.status_code == 201, response.text
    created: dict[str, Any] = response.json()
    return created
