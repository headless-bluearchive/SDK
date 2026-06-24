from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Callable

from config.game import DEFAULTS
from modules.auth.flows import (
    IntegratedLoginOptions,
    IntegratedLoginResult,
    run_android_direct_login_async,
    run_android_direct_login_auto_region_async,
)
from modules.runtime.android_mobile_profile import DEFAULT_ANDROID_MOBILE_PROFILE_PATH


@dataclass(frozen=True)
class LoginOptions:
    region: str = ""
    country: str = DEFAULTS.country
    locale: str = DEFAULTS.locale
    host_url: str = ""
    api_url: str = ""
    android_mobile_profile_path: Path = DEFAULT_ANDROID_MOBILE_PROFILE_PATH
    android_mobile_profile: Any = None
    nx_id: str = ""
    nx_password: str = ""
    nx_preflight_nexon_sn: bool = True
    allow_synthetic_ngsm_token: bool = True
    ngsx_attestation_mode: str = "disabled"
    ngsx_attestation_url: str = ""
    ngsx_attestation_command: str = ""
    ngsx_attestation_file: str = ""
    ngsx_attestation_timeout: float = 30.0
    ngsx_attestation_strict: bool = False
    proxy: str = ""
    timeout: float = 60.0
    debug_logger: Callable[[str], None] | None = None

    def to_integrated(self) -> IntegratedLoginOptions:
        values: dict[str, Any] = {
            "region": self.region,
            "country": self.country,
            "locale": self.locale,
            "host_url": self.host_url,
            "api_url": self.api_url,
            "android_mobile_profile_path": self.android_mobile_profile_path,
            "android_mobile_profile": self.android_mobile_profile,
            "nx_id": self.nx_id,
            "nx_password": self.nx_password,
            "nx_preflight_nexon_sn": self.nx_preflight_nexon_sn,
            "allow_synthetic_ngsm_token": self.allow_synthetic_ngsm_token,
            "ngsx_attestation_mode": self.ngsx_attestation_mode,
            "ngsx_attestation_url": self.ngsx_attestation_url,
            "ngsx_attestation_command": self.ngsx_attestation_command,
            "ngsx_attestation_file": self.ngsx_attestation_file,
            "ngsx_attestation_timeout": self.ngsx_attestation_timeout,
            "ngsx_attestation_strict": self.ngsx_attestation_strict,
            "proxy": self.proxy,
            "timeout": self.timeout,
            "debug_logger": self.debug_logger,
        }
        return IntegratedLoginOptions(**values)


async def Login(
    options: LoginOptions | IntegratedLoginOptions | None = None,
    **kwargs: Any,
) -> IntegratedLoginResult:
    resolved = _resolve_options(options, kwargs)
    return await run_android_direct_login_async(resolved)


async def LoginAutoRegion(
    regions: list[str],
    options: LoginOptions | IntegratedLoginOptions | None = None,
    *,
    region_probe_timeout: float = 60.0,
    **kwargs: Any,
) -> IntegratedLoginResult:
    resolved = _resolve_options(options, kwargs)
    return await run_android_direct_login_auto_region_async(
        resolved, regions, region_probe_timeout=region_probe_timeout
    )


def _resolve_options(
    options: LoginOptions | IntegratedLoginOptions | None,
    kwargs: dict[str, Any],
) -> IntegratedLoginOptions:
    if options is None:
        login_fields = set(LoginOptions.__dataclass_fields__)
        integrated_fields = set(IntegratedLoginOptions.__dataclass_fields__)
        unknown = set(kwargs) - integrated_fields
        if unknown:
            raise TypeError(f"unexpected login option(s): {', '.join(sorted(unknown))}")
        if set(kwargs) - login_fields:
            return IntegratedLoginOptions(**kwargs)
        return LoginOptions(**kwargs).to_integrated()
    if isinstance(options, LoginOptions):
        if kwargs:
            options = replace(options, **kwargs)
        return options.to_integrated()
    if kwargs:
        options = replace(options, **kwargs)
    return options
