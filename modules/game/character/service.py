from __future__ import annotations

from typing import Any

from core.error import UnsafeOperationError
from modules.game.base import GameService
from modules.game.common import as_list, compact_fields, extra_fields, optional_int


class CharacterService(GameService):
    async def list(self) -> dict[str, Any]:
        payload = await self.request("CharacterListRequest")
        return format_character_list(payload)

    async def transcendence(
        self,
        *,
        target_character_server_id: int | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("character.transcendence requires confirm=True")
        fields = compact_fields(
            TargetCharacterServerId=optional_int("target_character_server_id", target_character_server_id),
        )
        return await self.request("CharacterTranscendenceRequest", fields)

    async def exp_growth(
        self,
        *,
        consume_request_db: Any = None,
        target_character_server_id: int | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("character.exp_growth requires confirm=True")
        fields = compact_fields(
            ConsumeRequestDB=consume_request_db,
            TargetCharacterServerId=optional_int("target_character_server_id", target_character_server_id),
        )
        return await self.request("CharacterExpGrowthRequest", fields)

    async def favor_growth(
        self,
        *,
        consume_item_db_ids_and_counts: Any = None,
        target_character_db_id: int | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("character.favor_growth requires confirm=True")
        fields = compact_fields(
            ConsumeItemDBIdsAndCounts=consume_item_db_ids_and_counts,
            TargetCharacterDBId=optional_int("target_character_db_id", target_character_db_id),
        )
        return await self.request("CharacterFavorGrowthRequest", fields)

    async def update_skill_level(
        self,
        *,
        level: int | None = None,
        replace_infos: Any = None,
        skill_slot: int | None = None,
        target_character_db_id: int | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("character.update_skill_level requires confirm=True")
        fields = compact_fields(
            Level=optional_int("level", level),
            ReplaceInfos=replace_infos,
            SkillSlot=optional_int("skill_slot", skill_slot),
            TargetCharacterDBId=optional_int("target_character_db_id", target_character_db_id),
        )
        return await self.request("CharacterSkillLevelUpdateRequest", fields)

    async def unlock_weapon(
        self,
        *,
        target_character_server_id: int | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("character.unlock_weapon requires confirm=True")
        fields = compact_fields(
            TargetCharacterServerId=optional_int("target_character_server_id", target_character_server_id),
        )
        return await self.request("CharacterUnlockWeaponRequest", fields)

    async def weapon_exp_growth(
        self,
        *,
        consume_unique_id_and_counts: Any = None,
        target_character_server_id: int | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("character.weapon_exp_growth requires confirm=True")
        fields = compact_fields(
            ConsumeUniqueIdAndCounts=consume_unique_id_and_counts,
            TargetCharacterServerId=optional_int("target_character_server_id", target_character_server_id),
        )
        return await self.request("CharacterWeaponExpGrowthRequest", fields)

    async def weapon_transcendence(
        self,
        *,
        target_character_server_id: int | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("character.weapon_transcendence requires confirm=True")
        fields = compact_fields(
            TargetCharacterServerId=optional_int("target_character_server_id", target_character_server_id),
        )
        return await self.request("CharacterWeaponTranscendenceRequest", fields)

    async def batch_skill_level_update(
        self,
        *,
        skill_level_update_request_dbs: Any = None,
        target_character_db_id: int | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("character.batch_skill_level_update requires confirm=True")
        fields = compact_fields(
            SkillLevelUpdateRequestDBs=skill_level_update_request_dbs,
            TargetCharacterDBId=optional_int("target_character_db_id", target_character_db_id),
        )
        return await self.request("CharacterBatchSkillLevelUpdateRequest", fields)

    async def potential_growth(
        self,
        *,
        potential_growth_request_dbs: Any = None,
        replace_infos: Any = None,
        target_character_db_id: int | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("character.potential_growth requires confirm=True")
        fields = compact_fields(
            PotentialGrowthRequestDBs=potential_growth_request_dbs,
            ReplaceInfos=replace_infos,
            TargetCharacterDBId=optional_int("target_character_db_id", target_character_db_id),
        )
        return await self.request("CharacterPotentialGrowthRequest", fields)

    async def set_favorites(
        self,
        *,
        activate_by_server_ids: Any = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("character.set_favorites requires confirm=True")
        fields = compact_fields(
            ActivateByServerIds=activate_by_server_ids,
        )
        return await self.request("CharacterSetFavoritesRequest", fields)

    async def set_costume(
        self,
        *,
        character_unique_id: int | None = None,
        costume_id_to_set: int | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("character.set_costume requires confirm=True")
        fields = compact_fields(
            CharacterUniqueId=optional_int("character_unique_id", character_unique_id),
            CostumeIdToSet=optional_int("costume_id_to_set", costume_id_to_set),
        )
        return await self.request("CharacterSetCostumeRequest", fields)


def format_character_list(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "CharacterDBs",
        "TSSCharacterDBs",
    }
    characters = as_list(payload.get("CharacterDBs"))
    tss_characters = as_list(payload.get("TSSCharacterDBs"))
    return {
        "characters": characters,
        "tss_characters": tss_characters,
        "count": len(characters),
        "extra": extra_fields(payload, known_keys),
    }
