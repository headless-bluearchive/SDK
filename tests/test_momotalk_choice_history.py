"""Regression: legacy Iroha outline omits a reply stored in ChoiceDBs."""
import asyncio
from copy import deepcopy
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from core.error import GameApiError
from modules.game.momotalk import service as momo

OLD_GROUP = 200160230
OLD_CHOICE = 200160280
NEXT_GROUP = 200160240


def payload():
    return {
        "MomoTalkOutLineDB": {"CharacterDBId": 10, "CharacterId": 20016, "LatestMessageGroupId": OLD_GROUP},
        "MomoTalkChoiceDBs": [{"CharacterDBId": 10, "MessageGroupId": OLD_GROUP, "ChosenMessageId": OLD_CHOICE}],
    }


def master():
    return {
        "ready": True, "source": "test", "first_message_group_by_character": {20016: OLD_GROUP},
        "favor_by_character": {},
        "message_by_group": {
            OLD_GROUP: [{"id": OLD_CHOICE, "message_group_id": OLD_GROUP, "message_condition": 3,
                         "character_id": 20016, "next_group_id": NEXT_GROUP}],
            NEXT_GROUP: [{"id": 200160290, "message_group_id": NEXT_GROUP, "message_condition": 1,
                          "character_id": 20016, "condition_value": 15, "next_group_id": 0}],
        },
    }


def test_message_list_restores_current_legacy_choice_without_mutating_raw_outline():
    raw = payload()
    original = deepcopy(raw)
    result = momo.format_momotalk_messages(raw)
    assert result["chosen_message_id"] == OLD_CHOICE
    assert result["chosen_message_source"] == "choice_history"
    assert raw == original


@pytest.mark.parametrize("changes", [
    {"MessageGroupId": OLD_GROUP - 10}, {"CharacterDBId": 99}, {"ChosenMessageId": 0},
])
def test_history_must_match_current_group_and_character(changes):
    raw = payload()
    raw["MomoTalkChoiceDBs"][0].update(changes)
    assert momo.format_momotalk_messages(raw)["chosen_message_id"] is None


def test_conflicting_history_is_not_guessed():
    raw = payload()
    raw["MomoTalkChoiceDBs"].append({"CharacterDBId": 10, "MessageGroupId": OLD_GROUP, "ChosenMessageId": OLD_CHOICE + 1})
    assert momo.format_momotalk_messages(raw)["chosen_message_id"] is None


def test_outline_choice_takes_precedence():
    raw = payload()
    raw["MomoTalkOutLineDB"]["ChosenMessageId"] = OLD_CHOICE + 1
    result = momo.format_momotalk_messages(raw)
    assert result["chosen_message_id"] == OLD_CHOICE + 1
    assert result["chosen_message_source"] == "outline"


@pytest.mark.parametrize("include_details", [False, True])
def test_status_resolves_legacy_choice_even_without_full_scan(monkeypatch, include_details):
    run_status_case(monkeypatch, include_details=include_details)


@pytest.mark.parametrize("failure", ["missing", "invalid", "api_error"])
def test_unresolved_history_cannot_report_exact_zero(monkeypatch, failure):
    run_status_case(monkeypatch, failure=failure)


def test_known_choice_needs_no_additional_request(monkeypatch):
    run_status_case(monkeypatch, known_choice=True)


def run_status_case(monkeypatch, *, include_details=False, failure=None, known_choice=False):
    service = momo.MomoTalkService(None)
    data = payload()
    outline = {"outlines": [dict(data["MomoTalkOutLineDB"])], "favor_schedule_records": {}, "outline_count": 1}
    characters = {"characters": [{"UniqueId": 20016, "ServerId": 10, "FavorRank": 20}], "count": 1}
    if known_choice:
        outline["outlines"][0]["ChosenMessageId"] = OLD_CHOICE
    if failure == "missing":
        data["MomoTalkChoiceDBs"] = []
    if failure == "invalid":
        data["MomoTalkChoiceDBs"][0]["ChosenMessageId"] = 999
    calls = []

    async def messages(character_db_id):
        calls.append(character_db_id)
        if failure == "api_error":
            raise GameApiError("failure", error_code=5)
        return momo.format_momotalk_messages(data)

    monkeypatch.setattr(momo, "_load_momotalk_master_data", master)
    monkeypatch.setattr(service, "messages", messages)
    result = asyncio.run(service._format_status(
        outline, characters, character_ids=None, include_message_details=include_details,
        include_owned_without_outline=True,
    ))
    assert calls == ([] if known_choice else [10])
    if failure:
        assert result["exact_unread_count_available"] is False
        assert result["actionable"]["unresolved_choice_character_ids"] == [20016]
    else:
        assert result["exact_unread_count_available"] is True
        assert result["actionable"]["unread_total_count"] == 1
        assert result["actionable"]["messages"][0]["advance_args"]["last_read_message_group_id"] == NEXT_GROUP
