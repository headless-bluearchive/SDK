from __future__ import annotations

from typing import Any

from modules.game.base import GameService
from modules.game.common import as_list, compact_fields, extra_fields, optional_int, required_int


class EliminateRaidService(GameService):
    async def lobby(self) -> dict[str, Any]:
        payload = await self.request("EliminateRaidLobbyRequest")
        return format_eliminate_raid_lobby(payload)

    async def opponent_list(
        self,
        *,
        boss_group_index: int | None = None,
        is_first_request: bool | None = None,
        is_upper: bool | None = None,
        rank: int | None = None,
        score: int | None = None,
        search_type: int | None = None,
    ) -> dict[str, Any]:
        fields = compact_fields(
            BossGroupIndex=optional_int("boss_group_index", boss_group_index),
            IsFirstRequest=bool(is_first_request) if is_first_request is not None else None,
            IsUpper=bool(is_upper) if is_upper is not None else None,
            Rank=optional_int("rank", rank),
            Score=optional_int("score", score),
            SearchType=optional_int("search_type", search_type),
        )
        payload = await self.request("EliminateRaidOpponentListRequest", fields)
        return format_eliminate_raid_opponent_list(payload)

    async def get_best_team(self, search_account_id: int) -> dict[str, Any]:
        payload = await self.request(
            "EliminateRaidGetBestTeamRequest",
            {"SearchAccountId": required_int("search_account_id", search_account_id)},
        )
        return format_eliminate_raid_best_team(payload)

    async def ranking_index(self) -> dict[str, Any]:
        payload = await self.request("EliminateRaidRankingIndexRequest")
        return format_eliminate_raid_ranking_index(payload)


def format_eliminate_raid_lobby(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "RaidLobbyInfoDB",
        "EliminateRaidGiveUpDB",
        "RaidGiveUpDB",
        "SeasonType",
        "AccountCurrencyDB",
        "ParcelResultDB",
    }
    return {
        "lobby_info": payload.get("RaidLobbyInfoDB"),
        "give_up": payload.get("RaidGiveUpDB", payload.get("EliminateRaidGiveUpDB")),
        "season_type": payload.get("SeasonType"),
        "account_currency": payload.get("AccountCurrencyDB"),
        "parcel_result": payload.get("ParcelResultDB"),
        "extra": extra_fields(payload, known_keys),
    }


def format_eliminate_raid_opponent_list(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "OpponentUserDBs",
    }
    opponents = as_list(payload.get("OpponentUserDBs"))
    return {
        "opponents": opponents,
        "count": len(opponents),
        "extra": extra_fields(payload, known_keys),
    }


def format_eliminate_raid_best_team(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "RaidTeamSettingDBsDict",
        "RaidTeamSettingDBs",
        "EliminateRaidTeamSettingDBs",
    }
    teams_by_key = payload.get("RaidTeamSettingDBsDict")
    teams = as_list(payload.get("EliminateRaidTeamSettingDBs", payload.get("RaidTeamSettingDBs")))
    return {
        "team_settings_by_key": teams_by_key if isinstance(teams_by_key, dict) else {},
        "team_settings": teams,
        "count": len(teams),
        "extra": extra_fields(payload, known_keys),
    }


def format_eliminate_raid_ranking_index(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "RankBrackets",
    }
    brackets = as_list(payload.get("RankBrackets"))
    return {
        "rank_brackets": brackets,
        "count": len(brackets),
        "extra": extra_fields(payload, known_keys),
    }
