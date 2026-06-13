from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Callable

from config.game import DEFAULTS
from modules.auth.flows import IntegratedLoginOptions, IntegratedLoginResult, run_android_direct_login_async
from modules.runtime.android_mobile_profile import DEFAULT_ANDROID_MOBILE_PROFILE_PATH


@dataclass(frozen=True)
class LoginOptions:
    region: str = ""
    country: str = DEFAULTS.country
    locale: str = DEFAULTS.locale
    host_url: str = ""
    api_url: str = ""
    android_mobile_profile_path: Path = DEFAULT_ANDROID_MOBILE_PROFILE_PATH
    nx_id: str = ""
    nx_password: str = ""
    nx_preflight_nexon_sn: bool = True
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
            "nx_id": self.nx_id,
            "nx_password": self.nx_password,
            "nx_preflight_nexon_sn": self.nx_preflight_nexon_sn,
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


def _resolve_options(
    options: LoginOptions | IntegratedLoginOptions | None,
    kwargs: dict[str, Any],
) -> IntegratedLoginOptions:
    if options is None:
        return LoginOptions(**kwargs).to_integrated()
    if isinstance(options, LoginOptions):
        if kwargs:
            options = replace(options, **kwargs)
        return options.to_integrated()
    if kwargs:
        options = replace(options, **kwargs)
    return options
