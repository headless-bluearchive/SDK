from __future__ import annotations

from typing import Any

from core.error import UnsafeOperationError
from modules.game.base import GameService
from modules.game.common import as_list, compact_fields, extra_fields, optional_int, required_int


class ClanService(GameService):
    async def lobby(self) -> dict[str, Any]:
        payload = await self.request("ClanLobbyRequest")
        return format_clan_lobby(payload)

    async def login(self) -> dict[str, Any]:
        payload = await self.request("ClanLoginRequest")
        return format_clan_login(payload)

    async def applicant(self, *, offset: int | None = None) -> dict[str, Any]:
        fields = compact_fields(OffSet=optional_int("offset", offset))
        return await self.request("ClanApplicantRequest", fields)

    async def chat_log(self, *, channel: str | None = None, from_date: str | None = None) -> dict[str, Any]:
        fields = compact_fields(
            Channel=str(channel) if channel is not None else None,
            FromDate=str(from_date) if from_date is not None else None,
        )
        return await self.request("ClanChatLogRequest", fields)

    async def check(self) -> dict[str, Any]:
        return await self.request("ClanCheckRequest")

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

    async def setting(
        self,
        *,
        changed_clan_name: str | None = None,
        changed_notice: str | None = None,
        clan_join_option: int | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("clan.setting requires confirm=True")
        fields = compact_fields(
            ChangedClanName=str(changed_clan_name) if changed_clan_name is not None else None,
            ChangedNotice=str(changed_notice) if changed_notice is not None else None,
            ClanJoinOption=optional_int("clan_join_option", clan_join_option),
        )
        return await self.request("ClanSettingRequest", fields)

    async def set_assist(
        self,
        *,
        character_db_id: int | None = None,
        combat_style_index: int | None = None,
        echelon_type: int | None = None,
        slot_number: int | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("clan.set_assist requires confirm=True")
        fields = compact_fields(
            CharacterDBId=optional_int("character_db_id", character_db_id),
            CombatStyleIndex=optional_int("combat_style_index", combat_style_index),
            EchelonType=optional_int("echelon_type", echelon_type),
            SlotNumber=optional_int("slot_number", slot_number),
        )
        return await self.request("ClanSetAssistRequest", fields)

    async def create(
        self,
        *,
        clan_join_option: int | None = None,
        clan_nick_name: str | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("clan.create requires confirm=True")
        fields = compact_fields(
            ClanJoinOption=optional_int("clan_join_option", clan_join_option),
            ClanNickName=str(clan_nick_name) if clan_nick_name is not None else None,
        )
        return await self.request("ClanCreateRequest", fields)

    async def join(self, *, clan_db_id: int | None = None, confirm: bool = False) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("clan.join requires confirm=True")
        fields = compact_fields(ClanDBId=optional_int("clan_db_id", clan_db_id))
        return await self.request("ClanJoinRequest", fields)

    async def quit(self, *, confirm: bool = False) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("clan.quit requires confirm=True")
        return await self.request("ClanQuitRequest")

    async def permit(
        self,
        *,
        applicant_account_id: int | None = None,
        is_permit: bool | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("clan.permit requires confirm=True")
        fields = compact_fields(
            ApplicantAccountId=optional_int("applicant_account_id", applicant_account_id),
            IsPerMit=is_permit,
        )
        return await self.request("ClanPermitRequest", fields)

    async def kick(self, *, member_account_id: int | None = None, confirm: bool = False) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("clan.kick requires confirm=True")
        fields = compact_fields(MemberAccountId=optional_int("member_account_id", member_account_id))
        return await self.request("ClanKickRequest", fields)

    async def confer(
        self,
        *,
        confering_grade: int | None = None,
        member_account_id: int | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("clan.confer requires confirm=True")
        fields = compact_fields(
            ConferingGrade=optional_int("confering_grade", confering_grade),
            MemberAccountId=optional_int("member_account_id", member_account_id),
        )
        return await self.request("ClanConferRequest", fields)

    async def dismiss(self, *, confirm: bool = False) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("clan.dismiss requires confirm=True")
        return await self.request("ClanDismissRequest")

    async def auto_join(self, *, confirm: bool = False) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("clan.auto_join requires confirm=True")
        return await self.request("ClanAutoJoinRequest")

    async def cancel_apply(self, *, confirm: bool = False) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("clan.cancel_apply requires confirm=True")
        return await self.request("ClanCancelApplyRequest")


def format_clan_login(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "AccountClanMemberDB",
    }
    return {
        "account_clan_member": payload.get("AccountClanMemberDB"),
        "extra": extra_fields(payload, known_keys),
    }


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
