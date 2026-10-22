"""What opportunities and opportunity actions refuse."""

from opportunities_helpers import (
    ACTIONS,
    OPPORTUNITIES,
    create_action,
    create_opportunity,
    new_opportunity,
)

TYPES = [
    "ai_automation",
    "saas",
    "service",
    "content",
    "consulting",
    "product",
    "other",
]
WINDOWS = ["opening", "open", "narrowing", "closed"]
LEVELS = [
    "pain_level",
    "budget_level",
    "frequency_level",
    "ai_leverage_level",
    "competition_level",
    "distribution_level",
    "fit_level",
]


def test_an_opportunity_needs_a_name(client, owner):
    response = client.post(OPPORTUNITIES, headers=owner, json={"type": "saas"})
    assert response.status_code == 422


def test_the_name_cannot_be_empty(client, owner):
    assert create_opportunity(client, owner, name="").status_code == 422


def test_the_name_cannot_be_cleared_on_update(client, owner):
    opportunity = new_opportunity(client, owner)
    path = f"{OPPORTUNITIES}/{opportunity['id']}"
    assert client.patch(path, headers=owner, json={"name": None}).status_code == 422
    assert client.patch(path, headers=owner, json={"name": ""}).status_code == 422
    assert client.get(path, headers=owner).json()["name"] == opportunity["name"]


def test_type_must_be_a_known_kind(client, owner):
    for kind in TYPES:
        assert create_opportunity(client, owner, type=kind).status_code == 201, kind
    assert create_opportunity(client, owner, type="hardware").status_code == 422


def test_status_must_be_a_known_state(client, owner):
    assert create_opportunity(client, owner, status="dreaming").status_code == 422
    for status in ("validating", "killed", "completed"):
        assert create_opportunity(client, owner, status=status).status_code == 201, (
            status
        )


def test_window_status_must_be_a_known_state(client, owner):
    for window in WINDOWS:
        assert (
            create_opportunity(client, owner, window_status=window).status_code == 201
        ), window
    assert create_opportunity(client, owner, window_status="ajar").status_code == 422


def test_scores_and_levels_must_be_numbers(client, owner):
    for field in (*LEVELS, "tier", "estimated_window_months"):
        refused = create_opportunity(client, owner, **{field: "high"})
        assert refused.status_code == 422, field
        fractional = create_opportunity(client, owner, **{field: 2.5})
        assert fractional.status_code == 422, field
    assert create_opportunity(client, owner, total_score="best").status_code == 422
    assert create_opportunity(client, owner, total_score=71.5).status_code == 201


def test_levels_accept_whole_numbers(client, owner):
    levels = dict.fromkeys(LEVELS, 4)
    response = create_opportunity(client, owner, **levels, tier=1, total_score=80)
    assert response.status_code == 201, response.text
    assert response.json()["pain_level"] == 4


def test_an_unknown_field_is_refused(client, owner):
    assert create_opportunity(client, owner, mood="hopeful").status_code == 422


def test_an_action_needs_a_url(client, owner):
    assert (
        client.post(ACTIONS, headers=owner, json={"title": "Post"}).status_code == 422
    )
    assert create_action(client, owner, url="").status_code == 422


def test_an_action_must_be_a_known_choice(client, owner):
    for choice in ("act_on", "skip", "monitor"):
        assert create_action(client, owner, action=choice).status_code == 201, choice
    assert create_action(client, owner, action="ignore").status_code == 422


def test_action_numbers_must_be_numbers(client, owner):
    assert create_action(client, owner, trend_score="hot").status_code == 422
    assert create_action(client, owner, trend_score=1.5).status_code == 422
    assert create_action(client, owner, revenue_actual="lots").status_code == 422
    assert create_action(client, owner, revenue_expected="lots").status_code == 422
