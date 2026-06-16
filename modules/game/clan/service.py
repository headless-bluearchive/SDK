from __future__ import annotations

from typing import Any

from modules.game.base import GameService
from modules.game.common import as_list, compact_fields, extra_fields, optional_int, required_int


class ClanService(GameService):
    async def lobby(self) -> dict[str, Any]:
        payload = await self.request("ClanLobbyRequest")
        return format_clan_lobby(payload)

    async def search(
        self,
        *,
        clan_join_option: int | None = None,
        clan_unique_code: str | None = None,
        search_string: str | None = None,
    ) -> dict[str, Any]:
        fields = compact_fields(
            ClanJoinOption=optional_int("clan_join_option", clan_join_option),
            ClanUniqueCode=str(clan_unique_code) if clan_unique_code is not None else None,
            SearchString=str(search_string) if search_string is not None else None,
        )
        payload = await self.request("ClanSearchRequest", fields)
        return format_clan_search(payload)

    async def member(self, clan_db_id: int, member_account_id: int) -> dict[str, Any]:
        payload = await self.request(
            "ClanMemberRequest",
            {
                "ClanDBId": required_int("clan_db_id", clan_db_id),
                "MemberAccountId": required_int("member_account_id", member_account_id),
            },
        )
        return format_clan_member(payload)

    async def member_list(self, clan_db_id: int) -> dict[str, Any]:
        payload = await self.request(
            "ClanMemberListRequest",
            {"ClanDBId": required_int("clan_db_id", clan_db_id)},
        )
        return format_clan_member_list(payload)

    async def my_assist_list(self) -> dict[str, Any]:
        payload = await self.request("ClanMyAssistListRequest")
        return format_clan_my_assist_list(payload)

    async def all_assist_list(
        self,
        *,
        echelon_type: int,
        is_practice: bool = False,
        pending_assist_use_info: list[dict[str, Any]] | tuple[dict[str, Any], ...] | None = None,
    ) -> dict[str, Any]:
        payload = await self.request(
            "ClanAllAssistListRequest",
            {
                "EchelonType": required_int("echelon_type", echelon_type),
                "IsPractice": bool(is_practice),
                "PendingAssistUseInfo": list(pending_assist_use_info or []),
            },
        )
        return format_clan_all_assist_list(payload)


def format_clan_lobby(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "IrcConfig",
        "AccountClanDB",
        "DefaultExposedClanDBs",
        "AccountClanMemberDB",
        "ClanMemberDBs",
    }
    members = as_list(payload.get("ClanMemberDBs"))
    exposed = as_list(payload.get("DefaultExposedClanDBs"))
    return {
        "irc_config": payload.get("IrcConfig"),
        "account_clan": payload.get("AccountClanDB"),
        "default_exposed_clans": exposed,
        "account_clan_member": payload.get("AccountClanMemberDB"),
        "clan_members": members,
        "member_count": len(members),
        "default_exposed_count": len(exposed),
        "extra": extra_fields(payload, known_keys),
    }


def format_clan_search(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "ClanDBs",
    }
    clans = as_list(payload.get("ClanDBs"))
    return {
        "clans": clans,
        "count": len(clans),
        "extra": extra_fields(payload, known_keys),
    }


def format_clan_member(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "ClanDB",
        "ClanMemberDB",
        "DetailedAccountInfoDB",
    }
    return {
        "clan": payload.get("ClanDB"),
        "clan_member": payload.get("ClanMemberDB"),
        "detailed_account_info": payload.get("DetailedAccountInfoDB"),
        "extra": extra_fields(payload, known_keys),
    }


def format_clan_member_list(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "ClanDB",
        "ClanMemberDBs",
    }
    members = as_list(payload.get("ClanMemberDBs"))
    return {
        "clan": payload.get("ClanDB"),
        "clan_members": members,
        "count": len(members),
        "extra": extra_fields(payload, known_keys),
    }


def format_clan_my_assist_list(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "ClanAssistSlotDBs",
    }
    slots = as_list(payload.get("ClanAssistSlotDBs"))
    return {
        "assist_slots": slots,
        "count": len(slots),
        "extra": extra_fields(payload, known_keys),
    }


def format_clan_all_assist_list(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "AssistCharacterDBs",
        "AssistCharacterRentHistoryDBs",
        "ClanDBId",
    }
    assists = as_list(payload.get("AssistCharacterDBs"))
    return {
        "assist_characters": assists,
        "assist_character_rent_history": as_list(payload.get("AssistCharacterRentHistoryDBs")),
        "clan_db_id": payload.get("ClanDBId"),
        "count": len(assists),
        "extra": extra_fields(payload, known_keys),
    }
