from __future__ import annotations

import asyncio
from dataclasses import dataclass
import json
from pathlib import Path
import shutil
from typing import Any, Mapping
from urllib.parse import urljoin

import httpx

from config.game import DEFAULTS
from config.paths import CORE_DATA_DIR, OFFICIAL_DATA_DIR
from core.error import OfficialDataDependencyError, OfficialDataError
from core.official_table_parser import parse_official_academy_tables, resolve_sqlcipher_material

OFFICIAL_CORE_MANIFEST = CORE_DATA_DIR / "official_data_manifest.json"
ACADEMY_MESSANGER_DATA = CORE_DATA_DIR / "academy_messanger.json"
ACADEMY_FAVOR_SCHEDULE_DATA = CORE_DATA_DIR / "academy_favor_schedule.json"


@dataclass(frozen=True)
class OfficialResource:
    path: str
    url: str
    size: int | None = None
    md5: str | None = None


@dataclass(frozen=True)
class OfficialCatalog:
    client_version: str
    build_number: str
    resource_data_url: str
    resource_root_url: str
    resource_count: int
    table_count: int
    resources: tuple[OfficialResource, ...]


async def fetch_global_catalog(
    *,
    client_version: str,
    build_number: int | str | None = None,
    market_game_id: str | None = None,
    market_code: str | None = None,
    timeout: float = 30.0,
) -> OfficialCatalog:
    version = _required_text("client_version", client_version)
    build = str(build_number or _build_number_from_version(version))
    headers = {"User-Agent": DEFAULTS.official_resource_user_agent, "Accept": "application/json"}
    body = {
        "market_game_id": market_game_id or DEFAULTS.official_global_market_game_id,
        "market_code": market_code or DEFAULTS.official_global_market_code,
        "curr_build_version": version,
        "curr_build_number": build,
    }
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True, headers=headers) as client:
        patch_response = await client.post(DEFAULTS.official_global_patch_url, json=body)
        patch_response.raise_for_status()
        patch_payload = patch_response.json()
        resource_data_url = _extract_resource_data_url(patch_payload)

        resource_response = await client.get(resource_data_url)
        resource_response.raise_for_status()
        resource_payload = resource_response.json()

    resources = _extract_resources(resource_payload, resource_data_url)
    table_count = sum(1 for item in resources if _is_table_resource(item.path))
    return OfficialCatalog(
        client_version=str(patch_payload.get("latest_build_version") or version),
        build_number=str(patch_payload.get("latest_build_number") or build),
        resource_data_url=resource_data_url,
        resource_root_url=resource_data_url.rsplit("/", 1)[0] + "/",
        resource_count=len(resources),
        table_count=table_count,
        resources=tuple(resources),
    )


async def download_global_table_bundles(
    *,
    client_version: str,
    build_number: int | str | None = None,
    targets: tuple[str, ...] | None = None,
    output_dir: Path | None = None,
    timeout: float = 120.0,
    show_progress: bool = True,
    workers: int | None = None,
    chunk_size: int | None = None,
    cleanup_after_parse: bool = True,
) -> dict[str, Any]:
    catalog = await fetch_global_catalog(
        client_version=client_version,
        build_number=build_number,
        timeout=timeout,
    )
    wanted = tuple(targets or DEFAULTS.official_global_table_targets)
    selected = _select_targets(catalog.resources, wanted)
    base_dir = Path(output_dir or OFFICIAL_DATA_DIR / "global" / catalog.client_version).resolve()
    base_dir.mkdir(parents=True, exist_ok=True)

    downloaded: list[dict[str, Any]] = []
    headers = {"User-Agent": DEFAULTS.official_resource_user_agent, "Accept": "*/*"}
    async with httpx.AsyncClient(timeout=timeout, follow_redirects=True, headers=headers) as client:
        for target in selected:
            local_path = base_dir / Path(target.path).name
            if local_path.exists() and target.size is not None and local_path.stat().st_size == target.size:
                downloaded.append(_file_result(target, local_path, skipped=True, download_method="cache"))
                continue
            download_method = await _download_resource(
                client,
                target,
                local_path,
                show_progress=show_progress,
                workers=workers or DEFAULTS.official_download_workers,
                chunk_size=chunk_size or DEFAULTS.official_download_chunk_size,
            )
            downloaded.append(_file_result(target, local_path, skipped=False, download_method=download_method))

    result = {
        "source": "official-global-cdn",
        "client_version": catalog.client_version,
        "build_number": catalog.build_number,
        "resource_count": catalog.resource_count,
        "table_count": catalog.table_count,
        "resource_data_url": catalog.resource_data_url,
        "output_dir": str(base_dir),
        "files": downloaded,
        "missing_targets": [target for target in wanted if target not in {item.path for item in selected}],
        "parsed": _parsed_status(),
        "next_step": "parse ExcelDB.db into core/data/academy_*.json",
    }
    _save_manifest(base_dir, result)
    if cleanup_after_parse and result["parsed"].get("ready"):
        result["cleanup"] = cleanup_download_cache(base_dir)
    return result


def data_status(
    *,
    client_version: str | None = None,
    build_number: int | str | None = None,
    base_dir: Path | None = None,
) -> dict[str, Any]:
    root = Path(base_dir or OFFICIAL_DATA_DIR / "global").resolve()
    manifest = _load_latest_manifest(root, include_core_manifest=base_dir is None)
    if manifest is None:
        parsed = _parsed_status()
        return {
            "ready": bool(parsed.get("ready")),
            "needs_download": not bool(parsed.get("ready")),
            "needs_update": False,
            "reason": "official data is ready" if parsed.get("ready") else "official dependency files are missing",
            "expected_client_version": client_version,
            "cached_client_version": None,
            "parsed": parsed,
            "next_step": None if parsed.get("ready") else "call await client.prepare_data()",
        }

    cached_version = manifest.get("client_version")
    requested_version = str(client_version) if client_version else cached_version
    version_mismatch = bool(client_version and cached_version != str(client_version))
    parsed = _parsed_status()
    if not parsed.get("ready") and isinstance(manifest.get("parsed"), dict):
        parsed = manifest["parsed"]
    files_ready = _manifest_files_ready(manifest)
    parsed_ready = bool(parsed.get("ready"))
    ready = not version_mismatch and parsed_ready
    return {
        "ready": ready,
        "needs_download": version_mismatch or (not files_ready and not parsed_ready),
        "needs_update": version_mismatch,
        "reason": _status_reason(version_mismatch, manifest, parsed),
        "expected_client_version": requested_version,
        "cached_client_version": cached_version,
        "cached_build_number": manifest.get("build_number"),
        "expected_build_number": str(build_number) if build_number is not None else None,
        "output_dir": manifest.get("output_dir"),
        "files": manifest.get("files", []),
        "parsed": parsed,
        "next_step": "call await client.prepare_data()" if version_mismatch or not ready else None,
    }


async def prepare_global_data(
    *,
    client_version: str,
    build_number: int | str | None = None,
    sqlcipher_key: bytes | str | None = None,
    sqlcipher_license: str | None = None,
    session: Mapping[str, Any] | None = None,
    profile: Mapping[str, Any] | None = None,
    download_large: bool = True,
    show_progress: bool = True,
    timeout: float = 120.0,
    workers: int | None = None,
    chunk_size: int | None = None,
    cleanup_after_parse: bool = True,
) -> dict[str, Any]:
    targets = DEFAULTS.official_global_table_targets if download_large else ("Preload/TableBundles/Excel.zip",)
    result = await download_global_table_bundles(
        client_version=client_version,
        build_number=build_number,
        targets=targets,
        timeout=timeout,
        show_progress=show_progress,
        workers=workers,
        chunk_size=chunk_size,
        cleanup_after_parse=False,
    )
    if not download_large:
        result["parsed"] = _empty_parsed_status()
        result["next_step"] = "call prepare_data(download_large=True) to fetch and parse master data"
        _save_manifest(Path(result["output_dir"]), result)
        return result
    try:
        resolved_sqlcipher_key, resolved_sqlcipher_license = resolve_sqlcipher_material(
            sqlcipher_key=sqlcipher_key,
            sqlcipher_license=sqlcipher_license,
            session=session,
            profile=profile,
        )
        result["parsed"] = parse_official_academy_tables(
            excel_db_path=Path(result["output_dir"]) / "ExcelDB.db",
            sqlcipher_key=resolved_sqlcipher_key,
            sqlcipher_license=resolved_sqlcipher_license,
        )
        result["next_step"] = None
        result.pop("parser_error", None)
        if cleanup_after_parse:
            result["cleanup"] = cleanup_download_cache(Path(result["output_dir"]))
    except OfficialDataError as exc:
        result["parsed"] = _parsed_status()
        result["parser_error"] = {"type": exc.__class__.__name__, "message": str(exc)}
        if isinstance(exc, OfficialDataDependencyError) and "material is missing" in str(exc):
            result["next_step"] = "configure SQLCipher material, then call await client.prepare_data() again"
        else:
            result["next_step"] = "install/configure SQLCipher backend, then call await client.prepare_data() again"
    _save_manifest(Path(result["output_dir"]), result)
    return result


def catalog_summary(catalog: OfficialCatalog) -> dict[str, Any]:
    return {
        "source": "official-global-cdn",
        "client_version": catalog.client_version,
        "build_number": catalog.build_number,
        "resource_count": catalog.resource_count,
        "table_count": catalog.table_count,
        "resource_data_url": catalog.resource_data_url,
    }


def cleanup_download_cache(path: Path | None = None) -> dict[str, Any]:
    target = Path(path or OFFICIAL_DATA_DIR).resolve()
    root = OFFICIAL_DATA_DIR.resolve()
    if not _is_relative_to(target, root):
        raise ValueError(f"refuse to delete path outside official data directory: {target}")
    if not target.exists():
        return {"deleted": False, "path": str(target), "reason": "path does not exist"}
    if target == root:
        shutil.rmtree(target)
        return {"deleted": True, "path": str(target)}
    shutil.rmtree(target)
    return {"deleted": True, "path": str(target)}


def _progress_bar(*, total: int | None, desc: str, enabled: bool):
    if not enabled:
        return None
    try:
        from tqdm import tqdm
    except ImportError:
        return None
    return tqdm(total=total, unit="B", unit_scale=True, unit_divisor=1024, desc=desc)


async def _download_resource(
    client: httpx.AsyncClient,
    resource: OfficialResource,
    local_path: Path,
    *,
    show_progress: bool,
    workers: int,
    chunk_size: int,
) -> str:
    supports_range = bool(resource.size) and workers > 1 and await _supports_range(client, resource.url)
    if supports_range and resource.size is not None:
        await _download_resource_ranged(
            client,
            resource,
            local_path,
            show_progress=show_progress,
            workers=workers,
            chunk_size=chunk_size,
        )
        return "range"
    await _download_resource_stream(client, resource, local_path, show_progress=show_progress)
    return "stream"


async def _supports_range(client: httpx.AsyncClient, url: str) -> bool:
    try:
        response = await client.get(url, headers={"Range": "bytes=0-0"})
    except httpx.HTTPError:
        return False
    return response.status_code == 206


async def _download_resource_stream(
    client: httpx.AsyncClient,
    resource: OfficialResource,
    local_path: Path,
    *,
    show_progress: bool,
) -> None:
    tmp_path = local_path.with_suffix(local_path.suffix + ".tmp")
    async with client.stream("GET", resource.url) as response:
        response.raise_for_status()
        with tmp_path.open("wb") as file:
            progress = _progress_bar(
                total=resource.size or _safe_int(response.headers.get("content-length")),
                desc=Path(resource.path).name,
                enabled=show_progress,
            )
            try:
                async for chunk in response.aiter_bytes():
                    file.write(chunk)
                    if progress is not None:
                        progress.update(len(chunk))
            finally:
                if progress is not None:
                    progress.close()
    tmp_path.replace(local_path)


async def _download_resource_ranged(
    client: httpx.AsyncClient,
    resource: OfficialResource,
    local_path: Path,
    *,
    show_progress: bool,
    workers: int,
    chunk_size: int,
) -> None:
    if resource.size is None:
        raise ValueError("resource size is required for ranged download")
    part_dir = local_path.with_name(local_path.name + ".parts")
    part_dir.mkdir(parents=True, exist_ok=True)
    chunks = _range_chunks(resource.size, max(1, chunk_size))
    semaphore = asyncio.Semaphore(max(1, workers))
    progress = _progress_bar(total=resource.size, desc=Path(resource.path).name, enabled=show_progress)

    async def download_part(index: int, start: int, end: int) -> None:
        part_path = part_dir / f"{index:05d}.part"
        expected_size = end - start + 1
        if part_path.exists() and part_path.stat().st_size == expected_size:
            if progress is not None:
                progress.update(expected_size)
            return
        if part_path.exists():
            part_path.unlink()
        async with semaphore:
            async with client.stream("GET", resource.url, headers={"Range": f"bytes={start}-{end}"}) as response:
                if response.status_code != 206:
                    raise RuntimeError(f"server did not honor range request for {resource.path}")
                with part_path.open("wb") as file:
                    async for chunk in response.aiter_bytes():
                        file.write(chunk)
                        if progress is not None:
                            progress.update(len(chunk))
        if part_path.stat().st_size != expected_size:
            raise RuntimeError(f"incomplete range chunk for {resource.path}: {part_path.name}")

    try:
        await asyncio.gather(*(download_part(index, start, end) for index, (start, end) in enumerate(chunks)))
    finally:
        if progress is not None:
            progress.close()

    tmp_path = local_path.with_suffix(local_path.suffix + ".tmp")
    with tmp_path.open("wb") as output:
        for index in range(len(chunks)):
            part_path = part_dir / f"{index:05d}.part"
            with part_path.open("rb") as part:
                while True:
                    data = part.read(1024 * 1024)
                    if not data:
                        break
                    output.write(data)
    if tmp_path.stat().st_size != resource.size:
        raise RuntimeError(f"merged file size mismatch for {resource.path}")
    tmp_path.replace(local_path)
    for part_path in part_dir.glob("*.part"):
        part_path.unlink()
    part_dir.rmdir()


def _range_chunks(total_size: int, chunk_size: int) -> list[tuple[int, int]]:
    chunks = []
    start = 0
    while start < total_size:
        end = min(start + chunk_size - 1, total_size - 1)
        chunks.append((start, end))
        start = end + 1
    return chunks


def _save_manifest(base_dir: Path, result: dict[str, Any]) -> None:
    manifest = dict(result)
    manifest["manifest_version"] = 1
    base_dir.mkdir(parents=True, exist_ok=True)
    version_manifest = base_dir / "manifest.json"
    version_manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    latest_manifest = base_dir.parent / "manifest.json"
    latest_manifest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if _is_relative_to(base_dir.resolve(), OFFICIAL_DATA_DIR.resolve()):
        CORE_DATA_DIR.mkdir(parents=True, exist_ok=True)
        OFFICIAL_CORE_MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _load_latest_manifest(root: Path, *, include_core_manifest: bool = True) -> dict[str, Any] | None:
    candidates = [root / "manifest.json"]
    if include_core_manifest:
        candidates.insert(0, OFFICIAL_CORE_MANIFEST)
    if root.exists():
        candidates.extend(sorted(root.glob("*/manifest.json"), key=lambda path: path.stat().st_mtime, reverse=True))
    for path in candidates:
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(raw, dict):
            return raw
    return None


def _manifest_files_ready(manifest: dict[str, Any]) -> bool:
    files = manifest.get("files")
    if not isinstance(files, list) or not files:
        return False
    for item in files:
        if not isinstance(item, dict):
            return False
        path = item.get("local_path")
        expected = _safe_int(item.get("expected_size"))
        if not isinstance(path, str) or not Path(path).exists():
            return False
        if expected is not None and Path(path).stat().st_size != expected:
            return False
    return True


def _status_reason(version_mismatch: bool, manifest: dict[str, Any], parsed: dict[str, Any]) -> str:
    if version_mismatch:
        return "cached official data version does not match current game version"
    if parsed.get("ready"):
        return "official data is ready"
    if not _manifest_files_ready(manifest):
        return "official dependency files are incomplete"
    return "official files are downloaded but required JSON has not been parsed yet"


def _parsed_status() -> dict[str, Any]:
    files = {
        "academy_messanger": ACADEMY_MESSANGER_DATA,
        "academy_favor_schedule": ACADEMY_FAVOR_SCHEDULE_DATA,
    }
    parsed_files = {
        name: str(path)
        for name, path in files.items()
        if path.exists() and path.stat().st_size > 0
    }
    return {
        "ready": set(parsed_files) == set(files),
        "files": parsed_files,
        "missing": [name for name in files if name not in parsed_files],
    }


def _empty_parsed_status() -> dict[str, Any]:
    return {
        "ready": False,
        "files": {},
        "missing": ["academy_messanger", "academy_favor_schedule"],
    }


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _extract_resource_data_url(payload: dict[str, Any]) -> str:
    patch = payload.get("patch")
    if not isinstance(patch, dict):
        raise ValueError("official patch response missing patch object")
    value = patch.get("resource_path")
    return _required_text("patch.resource_path", value)


def _extract_resources(payload: dict[str, Any], resource_data_url: str) -> list[OfficialResource]:
    raw_resources = payload.get("resources")
    if not isinstance(raw_resources, list):
        raise ValueError("official resource catalog missing resources list")
    root = resource_data_url.rsplit("/", 1)[0] + "/"
    result: list[OfficialResource] = []
    for item in raw_resources:
        if not isinstance(item, dict):
            continue
        path = item.get("resource_path")
        if not isinstance(path, str) or not path:
            continue
        result.append(
            OfficialResource(
                path=path,
                url=urljoin(root, path),
                size=_safe_int(item.get("resource_size")),
                md5=item.get("resource_hash") if isinstance(item.get("resource_hash"), str) else None,
            )
        )
    return result


def _select_targets(resources: tuple[OfficialResource, ...], targets: tuple[str, ...]) -> list[OfficialResource]:
    by_path = {item.path: item for item in resources}
    return [by_path[target] for target in targets if target in by_path]


def _file_result(resource: OfficialResource, path: Path, *, skipped: bool, download_method: str) -> dict[str, Any]:
    return {
        "resource_path": resource.path,
        "local_path": str(path),
        "size": path.stat().st_size,
        "expected_size": resource.size,
        "md5": resource.md5,
        "skipped": skipped,
        "download_method": download_method,
    }


def _is_table_resource(path: str) -> bool:
    return "/TableBundles/" in path or path.startswith("Preload/TableBundles/")


def _build_number_from_version(version: str) -> str:
    parts = version.rsplit(".", 1)
    if len(parts) == 2 and parts[1].isdigit():
        return parts[1]
    raise ValueError("build_number is required when client_version does not end with a numeric build")


def _required_text(name: str, value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} is required")
    return value.strip()


def _safe_int(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
