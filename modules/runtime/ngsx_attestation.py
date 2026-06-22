from __future__ import annotations

import json
import shlex
import subprocess
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Mapping
from urllib.request import Request, urlopen

from core.error import ConfigurationError, GatewayError


@dataclass(frozen=True)
class NgsxAttestationRequest:
    service_id: str
    package_name: str
    client_version: str
    guid: str
    npa_code: str
    np_sn: int
    np_token_present: bool
    ngsm_token: str = ""
    device: Mapping[str, Any] = field(default_factory=dict)

    def to_payload(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class NgsxAttestationResult:
    ok: bool
    status: str = ""
    code: int | None = None
    message: str = ""
    _ngsm_token: str = field(default="", repr=False, compare=False)
    ngsm_token_present: bool = False
    source: str = ""

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any], *, source: str = "") -> "NgsxAttestationResult":
        ok_value = _find_first(value, "ok", "success", "isOK", "isOk", "passed", "runCompleted")
        code_value = _find_first(value, "code", "errorCode", "ngsxCode")
        status = str(_find_first(value, "status", "state") or "")
        message = str(_find_first(value, "message", "errorDetail", "detail") or "")
        token = _find_first(value, "ngsmToken", "NgsmToken", "ngsm_token")
        ok = _coerce_bool(ok_value)
        if ok_value is None:
            ok = status.strip().lower() in {"ok", "success", "passed", "run-completed", "attested"}
        return cls(
            ok=bool(ok),
            status=status,
            code=_optional_int(code_value),
            message=message,
            _ngsm_token=str(token or ""),
            ngsm_token_present=bool(token),
            source=source,
        )

    @property
    def ngsm_token(self) -> str:
        return self._ngsm_token

    def to_public_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "status": self.status,
            "code": self.code,
            "message": self.message,
            "source": self.source,
            "ngsmTokenPresent": self.ngsm_token_present,
        }


def run_ngsx_attestation(
    request: NgsxAttestationRequest,
    *,
    mode: str = "disabled",
    url: str = "",
    command: str = "",
    file_path: str | Path | None = None,
    timeout: float = 30.0,
    strict: bool = False,
) -> NgsxAttestationResult | None:
    normalized = (mode or "disabled").strip().lower().replace("_", "-")
    if normalized in {"", "disabled", "none", "off"}:
        return None

    payload = request.to_payload()
    if normalized in {"http", "rpc", "url"}:
        if not url:
            raise ConfigurationError("ngsx_attestation_url is required when ngsx_attestation_mode='http'")
        result = _post_json(url, payload, timeout=timeout)
        attestation = NgsxAttestationResult.from_mapping(result, source=url)
    elif normalized in {"command", "cmd", "process"}:
        if not command:
            raise ConfigurationError("ngsx_attestation_command is required when ngsx_attestation_mode='command'")
        result = _run_command(command, payload, timeout=timeout)
        attestation = NgsxAttestationResult.from_mapping(result, source=command)
    elif normalized in {"file", "json-file"}:
        if not file_path:
            raise ConfigurationError("ngsx_attestation_file is required when ngsx_attestation_mode='file'")
        result = _read_json_file(file_path)
        attestation = NgsxAttestationResult.from_mapping(result, source=str(file_path))
    elif normalized in {"native-sim", "native-simulated", "sim", "simulated"}:
        from modules.runtime.ngsx_native_sim import simulate_ngsx_native_run

        result = simulate_ngsx_native_run(payload)
        attestation = NgsxAttestationResult.from_mapping(result, source="native-sim")
    else:
        raise ConfigurationError("ngsx_attestation_mode must be disabled/http/command/file/native-sim")

    if strict and not attestation.ok:
        raise GatewayError(
            "NGS-X attestation provider did not return ok=True"
            + (f" code={attestation.code}" if attestation.code is not None else "")
            + (f" message={attestation.message}" if attestation.message else "")
        )
    return attestation


def _post_json(url: str, payload: Mapping[str, Any], *, timeout: float) -> dict[str, Any]:
    body = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    request = Request(
        url,
        data=body,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        method="POST",
    )
    with urlopen(request, timeout=timeout) as response:
        text = response.read().decode("utf-8", errors="replace")
    parsed = json.loads(text or "{}")
    if not isinstance(parsed, Mapping):
        raise GatewayError("NGS-X attestation provider response must be a JSON object")
    return dict(parsed)


def _run_command(command: str, payload: Mapping[str, Any], *, timeout: float) -> dict[str, Any]:
    args = shlex.split(command)
    if not args:
        raise GatewayError("NGS-X attestation command is empty")
    completed = subprocess.run(
        args,
        input=json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
    )
    if completed.returncode != 0:
        raise GatewayError(
            f"NGS-X attestation command failed with exit code {completed.returncode}: "
            f"{completed.stderr.strip()[:500]}"
        )
    parsed = json.loads(completed.stdout or "{}")
    if not isinstance(parsed, Mapping):
        raise GatewayError("NGS-X attestation command output must be a JSON object")
    return dict(parsed)


def _read_json_file(file_path: str | Path) -> dict[str, Any]:
    parsed = json.loads(Path(file_path).read_text(encoding="utf-8"))
    if not isinstance(parsed, Mapping):
        raise GatewayError("NGS-X attestation file must contain a JSON object")
    return dict(parsed)


def _find_first(obj: Any, *names: str) -> Any:
    wanted = {name.lower() for name in names}
    if isinstance(obj, Mapping):
        for key, value in obj.items():
            if str(key).lower() in wanted:
                return value
        for value in obj.values():
            found = _find_first(value, *names)
            if found is not None:
                return found
    elif isinstance(obj, list):
        for item in obj:
            found = _find_first(item, *names)
            if found is not None:
                return found
    return None


def _coerce_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y", "ok", "success", "passed"}
    return False


def _optional_int(value: Any) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


__all__ = [
    "NgsxAttestationRequest",
    "NgsxAttestationResult",
    "run_ngsx_attestation",
]
