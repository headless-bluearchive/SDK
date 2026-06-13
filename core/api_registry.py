"""Registry for game API request builders.

Future game modules should register descriptors here instead of scattering
protocol names and request class strings across unrelated files.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping, Any


RequestBuilder = Callable[..., Mapping[str, Any]]


@dataclass(frozen=True)
class GameApiDescriptor:
    module: str
    name: str
    protocol_name: str
    request_class: str
    builder: RequestBuilder | None = None


_REGISTRY: dict[str, GameApiDescriptor] = {}


def register_api(descriptor: GameApiDescriptor) -> GameApiDescriptor:
    key = f"{descriptor.module}.{descriptor.name}"
    if key in _REGISTRY:
        raise KeyError(f"game api already registered: {key}")
    _REGISTRY[key] = descriptor
    return descriptor


def get_api(key: str) -> GameApiDescriptor:
    return _REGISTRY[key]


def list_apis() -> tuple[GameApiDescriptor, ...]:
    return tuple(_REGISTRY.values())
