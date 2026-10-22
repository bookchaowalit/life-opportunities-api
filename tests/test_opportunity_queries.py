"""Listing, grouping and the lifecycle of opportunities and opportunity actions."""

from opportunities_helpers import (
    ACTIONS,
    OPPORTUNITIES,
    new_action,
    new_opportunity,
    unique,
)


def test_list_filters_by_type_status_and_window(client, owner):
    mine = new_opportunity(
        client, owner, type="consulting", status="active", window_status="narrowing"
    )
    new_opportunity(client, owner, type="saas", status="paused", window_status="open")
    for params in (
        {"type": "consulting"},
        {"status": "active"},
        {"window_status": "narrowing"},
        {"type": "consulting", "status": "active", "window_status": "narrowing"},
    ):
        listed = client.get(OPPORTUNITIES, headers=owner, params=params)
        assert listed.status_code == 200, listed.text
        assert mine["id"] in [o["id"] for o in listed.json()["items"]], params
    mismatch = client.get(
        OPPORTUNITIES, headers=owner, params={"type": "consulting", "status": "paused"}
    )
    assert mine["id"] not in [o["id"] for o in mismatch.json()["items"]]


def test_list_can_ask_for_opportunities_with_no_type(client, owner):
    untyped = new_opportunity(client, owner)
    new_opportunity(client, owner, type="saas")
    listed = client.get(
        OPPORTUNITIES, headers=owner, params={"null": "type", "id": untyped["id"]}
    )
    assert [o["id"] for o in listed.json()["items"]] == [untyped["id"]]


def test_list_is_in_creation_order_and_can_be_reversed(client, owner):
    ids = [new_opportunity(client, owner)["id"] for _ in range(3)]
    ascending = client.get(OPPORTUNITIES, headers=owner, params={"id": ids})
    assert [o["id"] for o in ascending.json()["items"]] == ids
    descending = client.get(
        OPPORTUNITIES, headers=owner, params={"id": ids, "order": "desc"}
    )
    assert [o["id"] for o in descending.json()["items"]] == ids[::-1]


def test_list_refuses_a_field_that_is_not_a_filter(client, owner):
    assert (
        client.get(OPPORTUNITIES, headers=owner, params={"tier": 1}).status_code == 422
    )


def test_stats_count_opportunities_per_status_type_and_window(client, owner):
    new_opportunity(
        client, owner, status="killed", type="product", window_status="closed"
    )
    for field, value in (
        ("status", "killed"),
        ("type", "product"),
        ("window_status", "closed"),
    ):
        stats = client.get(
            f"{OPPORTUNITIES}/stats", headers=owner, params={"group_by": field}
        )
        assert stats.status_code == 200, stats.text
        assert stats.json()["groups"][value] >= 1, field


def test_stats_refuse_a_field_that_is_not_a_filter(client, owner):
    stats = client.get(
        f"{OPPORTUNITIES}/stats", headers=owner, params={"group_by": "tier"}
    )
    assert stats.status_code == 422


def test_scoring_an_opportunity_bumps_the_version_once(client, owner):
    opportunity = new_opportunity(client, owner)
    path = f"{OPPORTUNITIES}/{opportunity['id']}"
    scored = client.patch(
        path, headers=owner, json={"pain_level": 5, "fit_level": 4, "total_score": 82.5}
    )
    assert scored.status_code == 200, scored.text
    assert scored.json()["version"] == 2
    assert scored.json()["total_score"] == 82.5
    unchanged = client.patch(path, headers=owner, json={"pain_level": 5})
    assert unchanged.json()["version"] == 2


def test_killing_an_opportunity_keeps_it_listed(client, owner):
    opportunity = new_opportunity(client, owner, status="validating")
    path = f"{OPPORTUNITIES}/{opportunity['id']}"
    killed = client.patch(
        path, headers=owner, json={"status": "killed", "notes": "No demand"}
    )
    assert killed.status_code == 200, killed.text
    listed = client.get(OPPORTUNITIES, headers=owner, params={"status": "killed"})
    assert opportunity["id"] in [o["id"] for o in listed.json()["items"]]


def test_a_stale_expected_version_is_refused(client, owner):
    opportunity = new_opportunity(client, owner)
    path = f"{OPPORTUNITIES}/{opportunity['id']}"
    client.patch(path, headers=owner, json={"notes": "first"})
    stale = client.patch(
        path, headers=owner, json={"notes": "second", "expected_version": 1}
    )
    assert stale.status_code == 409


def test_a_deleted_opportunity_is_gone(client, owner):
    opportunity = new_opportunity(client, owner)
    path = f"{OPPORTUNITIES}/{opportunity['id']}"
    assert client.delete(path, headers=owner).status_code == 204
    assert client.get(path, headers=owner).status_code == 404
    assert client.delete(path, headers=owner).status_code == 404


def test_actions_are_listed_by_category_and_action(client, owner):
    category = unique("cat")
    act = new_action(client, owner, category=category, action="act_on")
    new_action(client, owner, category=category, action="skip")
    by_category = client.get(ACTIONS, headers=owner, params={"category": category})
    assert len(by_category.json()["items"]) == 2
    only_act = client.get(
        ACTIONS, headers=owner, params={"category": category, "action": "act_on"}
    )
    assert [a["id"] for a in only_act.json()["items"]] == [act["id"]]


def test_action_stats_count_per_action_and_refuse_other_fields(client, owner):
    new_action(client, owner, action="skip")
    stats = client.get(f"{ACTIONS}/stats", headers=owner, params={"group_by": "action"})
    assert stats.status_code == 200, stats.text
    assert stats.json()["groups"]["skip"] >= 1
    refused = client.get(f"{ACTIONS}/stats", headers=owner, params={"group_by": "url"})
    assert refused.status_code == 422


def test_acting_on_an_action_records_the_revenue(client, owner):
    action = new_action(client, owner, revenue_expected=500)
    path = f"{ACTIONS}/{action['id']}"
    acted = client.patch(
        path,
        headers=owner,
        json={
            "action": "act_on",
            "revenue_actual": 450.5,
            "action_notes": "Closed a deal",
        },
    )
    assert acted.status_code == 200, acted.text
    assert acted.json()["revenue_actual"] == 450.5
    assert acted.json()["revenue_expected"] == 500
    assert acted.json()["version"] == 2


def test_a_required_action_field_cannot_be_cleared(client, owner):
    action = new_action(client, owner)
    path = f"{ACTIONS}/{action['id']}"
    assert client.patch(path, headers=owner, json={"url": None}).status_code == 422
    assert client.patch(path, headers=owner, json={"url": ""}).status_code == 422


def test_a_deleted_action_is_gone(client, owner):
    action = new_action(client, owner)
    path = f"{ACTIONS}/{action['id']}"
    assert client.delete(path, headers=owner).status_code == 204
    assert client.get(path, headers=owner).status_code == 404
