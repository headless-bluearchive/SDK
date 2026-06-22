from __future__ import annotations

from typing import Any

from modules.game.base import GameService
from modules.game.common import as_list, compact_fields, extra_fields, int_list, required_int


class EventContentService(GameService):
    async def adventure_list(self, event_content_id: int) -> dict[str, Any]:
        payload = await self.request(
            "EventContentAdventureListRequest",
            {"EventContentId": required_int("event_content_id", event_content_id)},
        )
        return format_event_content_adventure_list(payload)

    async def shop_list(
        self,
        event_content_id: int,
        category_list: list[int] | tuple[int, ...] | None = None,
    ) -> dict[str, Any]:
        payload = await self.request(
            "EventContentShopListRequest",
            {
                "EventContentId": required_int("event_content_id", event_content_id),
                "CategoryList": int_list("category_list", category_list) if category_list is not None else [],
            },
        )
        return format_event_content_shop_list(payload)

    async def box_gacha_shop_list(self, event_content_id: int) -> dict[str, Any]:
        payload = await self.request(
            "EventContentBoxGachaShopListRequest",
            {"EventContentId": required_int("event_content_id", event_content_id)},
        )
        return format_event_content_box_gacha_shop_list(payload)

    async def collection_list(self, event_content_id: int, group_id: int | None = None) -> dict[str, Any]:
        payload = await self.request(
            "EventContentCollectionListRequest",
            compact_fields(
                EventContentId=required_int("event_content_id", event_content_id),
                GroupId=required_int("group_id", group_id) if group_id is not None else None,
            ),
        )
        return format_event_content_collection_list(payload)

    async def collection_for_mission(self, event_content_id: int) -> dict[str, Any]:
        payload = await self.request(
            "EventContentCollectionForMissionRequest",
            {"EventContentId": required_int("event_content_id", event_content_id)},
        )
        return format_event_content_collection_for_mission(payload)

    async def location_get_info(self, event_content_id: int) -> dict[str, Any]:
        payload = await self.request(
            "EventContentLocationGetInfoRequest",
            {"EventContentId": required_int("event_content_id", event_content_id)},
        )
        return format_event_content_location_get_info(payload)

    async def sub_event_lobby(self, event_content_id: int) -> dict[str, Any]:
        payload = await self.request(
            "EventContentSubEventLobbyRequest",
            {"EventContentId": required_int("event_content_id", event_content_id)},
        )
        return format_event_content_sub_event_lobby(payload)

    async def dice_race_lobby(self, event_content_id: int) -> dict[str, Any]:
        payload = await self.request(
            "EventContentDiceRaceLobbyRequest",
            {"EventContentId": required_int("event_content_id", event_content_id)},
        )
        return format_event_content_dice_race_lobby(payload)

    async def permanent_list(self) -> dict[str, Any]:
        payload = await self.request("EventContentPermanentListRequest")
        return format_event_content_permanent_list(payload)

    async def treasure_lobby(self, event_content_id: int) -> dict[str, Any]:
        payload = await self.request(
            "EventContentTreasureLobbyRequest",
            {"EventContentId": required_int("event_content_id", event_content_id)},
        )
        return format_event_content_treasure_lobby(payload)

    async def clue_search_get_info(self, event_content_id: int) -> dict[str, Any]:
        payload = await self.request(
            "EventContentClueSearchGetInfoRequest",
            {"EventContentId": required_int("event_content_id", event_content_id)},
        )
        return format_event_content_clue_search_get_info(payload)


def format_event_content_adventure_list(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "StageHistoryDBs",
        "StrategyObjecthistoryDBs",
        "EventContentBonusRewardDBs",
        "AlreadyReceiveRewardId",
        "StagePoint",
    }
    stages = as_list(payload.get("StageHistoryDBs"))
    return {
        "stage_history": stages,
        "strategy_object_history": as_list(payload.get("StrategyObjecthistoryDBs")),
        "bonus_rewards": as_list(payload.get("EventContentBonusRewardDBs")),
        "already_receive_reward_ids": as_list(payload.get("AlreadyReceiveRewardId")),
        "stage_point": payload.get("StagePoint"),
        "stage_count": len(stages),
        "extra": extra_fields(payload, known_keys),
    }


def format_event_content_shop_list(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "ShopInfos",
        "ShopEligmaHistoryDBs",
    }
    shops = as_list(payload.get("ShopInfos"))
    return {
        "shop_infos": shops,
        "eligma_history": as_list(payload.get("ShopEligmaHistoryDBs")),
        "count": len(shops),
        "extra": extra_fields(payload, known_keys),
    }


def format_event_content_box_gacha_shop_list(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "BoxGachaDB",
        "BoxGachaGroupIdByCount",
    }
    return {
        "box_gacha": payload.get("BoxGachaDB"),
        "box_gacha_group_id_by_count": payload.get("BoxGachaGroupIdByCount"),
        "extra": extra_fields(payload, known_keys),
    }


def format_event_content_collection_list(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "EventContentUnlockCGDBs",
    }
    collections = as_list(payload.get("EventContentUnlockCGDBs"))
    return {
        "collections": collections,
        "count": len(collections),
        "extra": extra_fields(payload, known_keys),
    }


def format_event_content_collection_for_mission(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "EventContentCollectionDBs",
    }
    collections = as_list(payload.get("EventContentCollectionDBs"))
    return {
        "collections": collections,
        "count": len(collections),
        "extra": extra_fields(payload, known_keys),
    }


def format_event_content_location_get_info(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "EventContentLocationDB",
    }
    return {
        "location": payload.get("EventContentLocationDB"),
        "extra": extra_fields(payload, known_keys),
    }


def format_event_content_sub_event_lobby(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "EventContentChangeDB",
        "IsOnSubEvent",
    }
    return {
        "event_content_change": payload.get("EventContentChangeDB"),
        "is_on_sub_event": payload.get("IsOnSubEvent"),
        "extra": extra_fields(payload, known_keys),
    }


def format_event_content_dice_race_lobby(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "DiceRaceDB",
    }
    return {
        "dice_race": payload.get("DiceRaceDB"),
        "extra": extra_fields(payload, known_keys),
    }


def format_event_content_permanent_list(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "PermanentDBs",
    }
    permanent = as_list(payload.get("PermanentDBs"))
    return {
        "permanent": permanent,
        "count": len(permanent),
        "extra": extra_fields(payload, known_keys),
    }


def format_event_content_treasure_lobby(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "BoardHistoryDB",
        "HiddenImage",
        "VariationId",
    }
    return {
        "board_history": payload.get("BoardHistoryDB"),
        "hidden_image": payload.get("HiddenImage"),
        "variation_id": payload.get("VariationId"),
        "extra": extra_fields(payload, known_keys),
    }


def format_event_content_clue_search_get_info(payload: dict[str, Any]) -> dict[str, Any]:
    known_keys = {
        "EventContentClueSearchDB",
        "EventContentClueSearchRoundDB",
        "EventContentClueSearchProgressDB",
        "EventContentCollectionDBs",
        "AlreadyReceiveRewardId",
        "EventContentId",
    }
    round_db = payload.get("EventContentClueSearchRoundDB")
    clue_db = payload.get("EventContentClueSearchDB")
    progress_db = payload.get("EventContentClueSearchProgressDB")
    collections = as_list(payload.get("EventContentCollectionDBs"))
    return {
        "clue_search": clue_db,
        "round": round_db,
        "progress": progress_db,
        "collections": collections,
        "already_receive_reward_ids": as_list(payload.get("AlreadyReceiveRewardId")),
        "event_content_id": payload.get("EventContentId"),
        "collection_count": len(collections),
        "extra": extra_fields(payload, known_keys),
    }
