from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from config.game import DEFAULTS
from core.client import BAReplayClient
from core.error import GameApiError, LoginRequiredError, NexonNgsmValidationError, ProtocolUnavailableError
from core.i18n import t
from core.protocol import protocol_value, request_protocol


class GameService:
    def __init__(self, owner: Any) -> None:
        self._owner = owner

    @property
    def client(self) -> BAReplayClient:
        try:
            return self._owner._require_gateway_client()
        except AttributeError as exc:
            raise LoginRequiredError(t("login.game_service_needs_session")) from exc

    async def request(
        self,
        request_class: str,
        fields: Mapping[str, Any] | None = None,
        *,
        include_base_defaults: bool = True,
    ) -> dict[str, Any]:
        self._ensure_protocol_available(request_class)
        response = await self.client.post_async(
            request_class,
            dict(fields or {}),
            url=self.client.session_api_url,
            body_mode=DEFAULTS.body_mode,
            include_base_defaults=include_base_defaults,
        )
        if isinstance(response, dict):
            if int(response.get("Protocol", 0) or 0) == -1:
                if int(response.get("ErrorCode", 0) or 0) == 1032:
                    raise NexonNgsmValidationError(
                        t("ngsm.validation_failed"),
                        error_code=1032,
                        protocol=_optional_int(response.get("Protocol")),
                        response_keys=sorted(str(key) for key in response.keys()),
                    )
                raise GameApiError.from_gateway_response(response)
            return response
        return {"payload": response}

    @staticmethod
    def _ensure_protocol_available(request_class: str) -> None:
        try:
            request_protocol(request_class)
        except Exception as exc:
            try:
                protocol_value(request_class)
            except Exception:
                raise ProtocolUnavailableError(t("protocol.unavailable", request_class=request_class)) from exc


def _optional_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
