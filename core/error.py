from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from core.error_codes import error_code_name


class HeadlessBAError(Exception):
    pass


class LoginError(HeadlessBAError):
    pass


class LoginRequiredError(LoginError):
    pass


class SessionRestoreError(LoginError):
    pass


class DailyResetSessionExpiredError(SessionRestoreError):
    pass


class AuthenticationError(LoginError):
    pass


class GatewayError(LoginError):
    pass


class ProofTokenError(LoginError):
    pass


class ConfigurationError(HeadlessBAError):
    pass


class RuntimeProfileError(HeadlessBAError):
    pass


class NetworkError(HeadlessBAError):
    pass


class OfficialDataError(HeadlessBAError):
    pass


class OfficialDataDependencyError(OfficialDataError):
    pass


class OfficialDataParseError(OfficialDataError):
    pass


class GameApiError(HeadlessBAError):
    def __init__(
        self,
        message: str | None = None,
        *,
        error_code: int | None = None,
        error_name: str | None = None,
        protocol: int | None = None,
        response_keys: list[str] | None = None,
    ) -> None:
        if message is None:
            from core.i18n import t

            message = t("gateway.error_response")
        self.error_code = error_code
        self.error_name = error_name or error_code_name(error_code)
        self.protocol = protocol
        self.response_keys = response_keys or []
        super().__init__(self._format_message(message))

    @classmethod
    def from_gateway_response(cls, response: Mapping[str, Any]) -> "GameApiError":
        error_code = _optional_int(response.get("ErrorCode"))
        protocol = _optional_int(response.get("Protocol"))
        return cls(
            error_code=error_code,
            protocol=protocol,
            response_keys=sorted(str(key) for key in response.keys()),
        )

    def _format_message(self, message: str) -> str:
        parts = [message]
        if self.error_code is not None:
            detail = f"ErrorCode={self.error_code}"
            display_name = self._localized_error_name()
            if display_name:
                detail = f"{detail} ({display_name})"
            parts.append(detail)
        if self.protocol is not None:
            parts.append(f"Protocol={self.protocol}")
        return ": ".join(parts)

    def _localized_error_name(self) -> str | None:
        if self.error_code is not None:
            from core.i18n import error_code_text

            localized = error_code_text(self.error_code)
            if localized:
                return localized
        return self.error_name


class ProtocolUnavailableError(GameApiError):
    pass


class UnsafeOperationError(GameApiError):
    _CONFIRM_SUFFIX = " requires confirm=True"

    def __init__(self, message: str | None = None, **kwargs: Any) -> None:
        from core.i18n import t

        if isinstance(message, str) and message.endswith(self._CONFIRM_SUFFIX):
            action = message[: -len(self._CONFIRM_SUFFIX)]
            message = t("confirm.requires_confirm", action=action)
        super().__init__(message, **kwargs)


class NexonNgsmValidationError(GameApiError):
    pass


def _optional_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
