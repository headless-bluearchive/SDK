from __future__ import annotations

from typing import Any

from core.error import UnsafeOperationError
from modules.game.base import GameService
from modules.game.common import compact_fields, optional_int


class RecipeService(GameService):
    async def craft(
        self,
        *,
        recipe_craft_unique_id: int | None = None,
        recipe_ingredient_unique_id: int | None = None,
        confirm: bool = False,
    ) -> dict[str, Any]:
        if confirm is not True:
            raise UnsafeOperationError("recipe.craft requires confirm=True")
        fields = compact_fields(
            RecipeCraftUniqueId=optional_int("recipe_craft_unique_id", recipe_craft_unique_id),
            RecipeIngredientUniqueId=optional_int(
                "recipe_ingredient_unique_id", recipe_ingredient_unique_id
            ),
        )
        return await self.request("RecipeCraftRequest", fields)
