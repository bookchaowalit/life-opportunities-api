"""Defaults and repeated writes of opportunities and opportunity actions."""

from opportunities_helpers import (
    ACTIONS,
    OPPORTUNITIES,
    create_action,
    create_opportunity,
    new_action,
    new_opportunity,
)


def test_new_opportunity_starts_as_researching_with_nothing_scored(client, owner):
    response = create_opportunity(client, owner)
    assert response.status_code == 201, response.text
    opportunity = response.json()
    assert opportunity["status"] == "researching"
    assert opportunity["type"] is None
    assert opportunity["window_status"] is None
    assert opportunity["total_score"] is None
    assert opportunity["tier"] is None
    assert opportunity["pain_level"] is None
    assert opportunity["version"] == 1


def test_total_score_keeps_its_decimal_value(client, owner):
    assert new_opportunity(client, owner, total_score=63.75)["total_score"] == 63.75


def test_opportunities_may_share_a_name(client, owner):
    assert create_opportunity(client, owner, name="Same idea").status_code == 201
    assert create_opportunity(client, owner, name="Same idea").status_code == 201


def test_an_import_keeps_the_old_id_and_refuses_a_second_import(client, owner):
    imported = create_opportunity(client, owner, legacy_id=4242)
    assert imported.status_code == 201, imported.text
    assert imported.json()["id"] == 4242
    found = client.get(f"{OPPORTUNITIES}/legacy/4242", headers=owner)
    assert found.status_code == 200, found.text
    assert found.json()["id"] == 4242
    assert create_opportunity(client, owner, legacy_id=4242).status_code == 409


def test_new_action_is_monitored_with_no_revenue(client, owner):
    response = create_action(client, owner)
    assert response.status_code == 201, response.text
    action = response.json()
    assert action["action"] == "monitor"
    assert action["revenue_actual"] == 0
    assert action["revenue_expected"] == 0
    assert action["title"] is None
    assert action["version"] == 1


def test_the_same_url_can_be_recorded_twice(client, owner):
    url = "https://example.com/same-post"
    assert create_action(client, owner, url=url).status_code == 201
    assert create_action(client, owner, url=url).status_code == 201


def test_revenue_keeps_its_decimal_value(client, owner):
    action = new_action(client, owner, revenue_actual=1250.5, revenue_expected=3000.25)
    assert action["revenue_actual"] == 1250.5
    assert action["revenue_expected"] == 3000.25


def test_an_action_import_keeps_the_old_id(client, owner):
    imported = create_action(client, owner, legacy_id=2323)
    assert imported.status_code == 201, imported.text
    found = client.get(f"{ACTIONS}/legacy/2323", headers=owner)
    assert found.status_code == 200, found.text
    assert found.json()["id"] == 2323
    assert create_action(client, owner, legacy_id=2323).status_code == 409
