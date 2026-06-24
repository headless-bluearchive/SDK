from __future__ import annotations

from typing import Any

from core.error import UnsafeOperationError
from modules.game.base import GameService
from modules.game.common import as_list, compact_fields, extra_fields, optional_int, required_int


class RaidService(GameService):
    async def list(
        self,
        *,
        raid_boss_group: str | None = None,
        raid_difficulty: int | None = None,
        raid_room_sort_option: int | None = None,
    ) -> dict[str, Any]:
        fields = compact_fields(
            RaidBossGroup=str(raid_boss_group) if raid_boss_group is not None else None,
            RaidDifficulty=optional_int("raid_difficulty", raid_difficulty),
            RaidRoomSortOption=optional_int("raid_room_sort_option", raid_room_sort_option),
        )
        payload = await self.request("RaidListRequest", fields)
        return format_raid_list(payload)

    async def complete_list(self) -> dict[str, Any]:
        payload = await self.request("RaidCompleteListRequest")
        return format_raid_complete_list(payload)

    async def search(
        self,
        *,
        secret_code: str | None = None,
        tags: list[str] | tuple[str, ...] | None = None,
    ) -> dict[str, Any]:
        fields = compact_fields(
            SecretCode=str(secret_code) if secret_code is not None else None,
            Tags=[str(tag) for tag in tags] if tags is not None else None,
        )
        payload = await self.request("RaidSearchRequest", fields)
        return format_raid_search(payload)

    async def lobby(self) -> dict[str, Any]:
        payload = await self.request("RaidLobbyRequest")
        return format_raid_lobby(payload)

    async def detail(self, *, raid_server_id: int, raid_unique_id: int) -> dict[str, Any]:
        return await self.request(
            "RaidDetailRequest",
            {
                "RaidServerId": required_int("raid_server_id", raid_server_id),
                "RaidUniqueId": required_int("raid_unique_id", raid_unique_id),
            },
        )

    async def login(self) -> dict[str, Any]:
        return await self.request("RaidLoginRequest")

    async def opponent_list(
        self,
        *,
        is_first_request: bool | None = None,
        is_upper: bool | None = None,
        rank: int | None = None,
        score: int | None = None,
        search_type: int | None = None,
    ) -> dict[str, Any]:
        fields = compact_fields(
            IsFirstRequest=bool(is_first_request) if is_first_request is not None else None,
            IsUpper=bool(is_upper) if is_upper is not None else None,
            Rank=optional_int("rank", rank),
            Score=optional_int("score", score),
            SearchType=optional_int("search_type", search_type),
        )
        payload = await self.request("RaidOpponentListRequest", fields)
        return format_raid_opponent_list(payload)

    async def get_best_team(self, search_account_id: int) -> dict[str, Any]:
        payload = await self.request(
            "RaidGetBestTeamRequest",
            {"SearchAccountId": required_int("search_account_id", search_account_id)},
        )
        return format_raid_best_team(payload)

    async def ranking_index(self) -> dict[str, Any]:
        payload = await self.request("RaidRankingIndexRequest")
        return format_raid_ranking_index(payload)

    async def reward(
        self, raid_server_id: int, *, is_practice: bool = False, confirm: bool = False, validate: bool = True
    ) -> dict[str, Any]:
        server_id = required_int("raid_server_id", raid_server_id)
        if confirm is not True:
            raise UnsafeOperationError("raid.reward requires confirm=True")
        if validate and not (await self.complete_list())["receive_reward_ids"]:
            raise UnsafeOperationError("no raid reward is currently claimable")
        return await self.request("RaidRewardRequest", {"IsPractice": bool(is_practice), "RaidServerId": server_id})

    async def reward_all(self, *, confirm: bool = False, validate: bool = True) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("raid.reward_all requires confirm=True")
        if validate and not (await self.complete_list())["receive_reward_ids"]:
            raise UnsafeOperationError("no raid reward is currently claimable")
        return await self.request("RaidRewardAllRequest")

    async def season_reward(self, *, confirm: bool = False) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("raid.season_reward requires confirm=True")
        return await self.request("RaidSeasonRewardRequest")

    async def ranking_reward(self, *, confirm: bool = False) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("raid.ranking_reward requires confirm=True")
        return await self.request("RaidRankingRewardRequest")

    async def sweep(
        self,
        *,
        unique_id: int,
        sweep_count: int = 1,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("raid.sweep requires confirm=True")
        fields = {
            "UniqueId": required_int("unique_id", unique_id),
            "SweepCount": required_int("sweep_count", sweep_count),
        }
        return await self.request("RaidSweepRequest", fields)


def format_raid_list(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "CreateRaidDBs",
        "EnterRaidDBs",
        "ListRaidDBs",
    }
    listed = as_list(payload.get("ListRaidDBs"))
    return {
        "create_raids": as_list(payload.get("CreateRaidDBs")),
        "enter_raids": as_list(payload.get("EnterRaidDBs")),
        "list_raids": listed,
        "count": len(listed),
        "extra": extra_fields(payload, known_keys),
    }


def format_raid_complete_list(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "RaidDBs",
        "StackedDamage",
        "ReceiveRewardId",
        "CurSeasonUniqueId",
    }
    raids = as_list(payload.get("RaidDBs"))
    return {
        "raids": raids,
        "stacked_damage": payload.get("StackedDamage"),
        "receive_reward_ids": as_list(payload.get("ReceiveRewardId")),
        "current_season_unique_id": payload.get("CurSeasonUniqueId"),
        "count": len(raids),
        "extra": extra_fields(payload, known_keys),
    }


def format_raid_search(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "RaidDBs",
    }
    raids = as_list(payload.get("RaidDBs"))
    return {
        "raids": raids,
        "count": len(raids),
        "extra": extra_fields(payload, known_keys),
    }


def format_raid_lobby(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "SeasonType",
        "RaidGiveUpDB",
        "RaidLobbyInfoDB",
        "AccountCurrencyDB",
        "ParcelResultDB",
    }
    return {
        "season_type": payload.get("SeasonType"),
        "raid_give_up": payload.get("RaidGiveUpDB"),
        "raid_lobby_info": payload.get("RaidLobbyInfoDB"),
        "account_currency": payload.get("AccountCurrencyDB"),
        "parcel_result": payload.get("ParcelResultDB"),
        "extra": extra_fields(payload, known_keys),
    }


def format_raid_opponent_list(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "OpponentUserDBs",
    }
    opponents = as_list(payload.get("OpponentUserDBs"))
    return {
        "opponents": opponents,
        "count": len(opponents),
        "extra": extra_fields(payload, known_keys),
    }


def format_raid_best_team(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "RaidTeamSettingDBs",
    }
    teams = as_list(payload.get("RaidTeamSettingDBs"))
    return {
        "team_settings": teams,
        "count": len(teams),
        "extra": extra_fields(payload, known_keys),
    }


def format_raid_ranking_index(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "RankBrackets",
    }
    brackets = as_list(payload.get("RankBrackets"))
    return {
        "rank_brackets": brackets,
        "count": len(brackets),
        "extra": extra_fields(payload, known_keys),
    }
