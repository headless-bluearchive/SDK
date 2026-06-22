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
        message: str = "game gateway returned an error response",
        *,
        error_code: int | None = None,
        error_name: str | None = None,
        protocol: int | None = None,
        response_keys: list[str] | None = None,
    ) -> None:
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
            if self.error_name:
                detail = f"{detail} ({self.error_name})"
            parts.append(detail)
        if self.protocol is not None:
            parts.append(f"Protocol={self.protocol}")
        return ": ".join(parts)


class ProtocolUnavailableError(GameApiError):
    pass


class UnsafeOperationError(GameApiError):
    pass


class NexonNgsmValidationError(GameApiError):
    pass


def _optional_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
