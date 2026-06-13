#!/usr/bin/env python3
"""Trigger Android NgsX.Init/Run in a running game process.

This optional bridge only performs the Android native side-effect that pure
HTTP replay cannot currently reproduce. Python still owns TOYSDK and main-game
gateway requests.

It also records the native libgrap-core.so path so Account_Auth(1002)
failures can be correlated with NgsX/GRAP runtime state.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping


DEFAULT_PACKAGE = "com.nexon.bluearchive"
DEFAULT_SERVICE_ID = 2079


@dataclass(frozen=True)
class BridgeArgs:
    package: str
    service_id: int
    guid: str
    npa_code: str
    timeout: float
    init_wait_ms: int
    attach_timeout: float
    output: Path
    no_init: bool
    device_id: str
    adb_path: str
    frida_address: str
    pid: int | None


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Attach to Android Blue Archive and trigger NgsX.Run(guid,npaCode).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--package", default=DEFAULT_PACKAGE, help="Android package/process name to attach")
    parser.add_argument("--service-id", type=int, default=DEFAULT_SERVICE_ID, help="NgsX service id")
    parser.add_argument("--guid", default="", help="TOYSDK guid/user id passed as NgsX.Run first argument")
    parser.add_argument("--npa-code", default="", help="TOYSDK npaCode passed as NgsX.Run second argument")
    parser.add_argument("--toy-login-json", type=Path, help="Read guid/npaCode from toy_login_summary.json")
    parser.add_argument("--device-id", default="", help="Optional Frida device id; defaults to USB device")
    parser.add_argument("--adb-path", default="adb", help="adb executable used when --device-id is an adb serial")
    parser.add_argument("--frida-address", default="", help="Optional remote frida-server address, e.g. 127.0.0.1:27042")
    parser.add_argument("--pid", type=int, default=None, help="Attach this PID directly instead of process-name matching")
    parser.add_argument("--list-devices", action="store_true", help="Print Frida devices and exit")
    parser.add_argument("--list-processes", action="store_true", help="Print processes on the selected Frida device and exit")
    parser.add_argument("--diagnose-attach", action="store_true", help="Try attaching to candidate processes and exit")
    parser.add_argument("--timeout", type=float, default=30.0, help="Seconds to wait for Init/Run callbacks")
    parser.add_argument("--attach-timeout", type=float, default=10.0, help="Seconds to wait for Frida device")
    parser.add_argument("--init-wait-ms", type=int, default=5000, help="Fallback delay before Run if Init callback is slow")
    parser.add_argument("--no-init", action="store_true", help="Call Run directly; useful if the game already initialized NgsX")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("analysis_reports/nexon_webview_login/ngsx_bridge_result.json"),
        help="Where to write bridge result JSON",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    ns = build_arg_parser().parse_args(argv)
    if ns.list_devices or ns.list_processes or ns.diagnose_attach:
        return run_diagnostics(ns)

    guid = ns.guid
    npa_code = ns.npa_code
    if ns.toy_login_json:
        loaded = load_toy_login(ns.toy_login_json)
        guid = guid or str(find_first(loaded, "guid", "userId") or "")
        npa_code = npa_code or str(find_first(loaded, "npaCode", "npa_code") or "")
    if not guid or not npa_code:
        raise SystemExit("--guid/--npa-code or --toy-login-json with guid/npaCode is required")

    args = BridgeArgs(
        package=ns.package,
        service_id=ns.service_id,
        guid=guid,
        npa_code=npa_code,
        timeout=ns.timeout,
        init_wait_ms=ns.init_wait_ms,
        attach_timeout=ns.attach_timeout,
        output=ns.output.resolve(),
        no_init=ns.no_init,
        device_id=ns.device_id,
        adb_path=ns.adb_path,
        frida_address=ns.frida_address,
        pid=ns.pid,
    )
    result = run_bridge(args)
    write_json(args.output, result)
    print(f"[*] NgsX bridge status: {result.get('status')}")
    if result.get("ngsmToken"):
        print("[*] ngsmToken: <present>")
    print(f"[*] Output: {args.output}")
    return 0 if result.get("status") in {"ngsm-token", "run-callback"} else 2


def run_bridge(args: BridgeArgs) -> dict[str, Any]:
    frida = import_frida()
    events: list[dict[str, Any]] = []
    script_errors: list[str] = []
    status = "started"
    pid_source = "unknown"

    def on_message(message: Mapping[str, Any], data: bytes | None) -> None:
        nonlocal status
        if message.get("type") == "send":
            payload = message.get("payload")
            if isinstance(payload, dict):
                events.append(payload)
                event = str(payload.get("event") or "")
                if event == "error":
                    status = event
                elif event == "ngsm-token":
                    token = str(payload.get("ngsmToken") or "")
                    status = "ngsm-token" if token else "ngsm-token-error"
                elif event == "run-callback" and status == "started":
                    status = event
                return
            events.append({"event": "message", "payload": payload})
            return
        if message.get("type") == "error":
            text = str(message.get("stack") or message.get("description") or message)
            script_errors.append(text)
            status = "error"

    device = get_frida_device(
        frida,
        args.device_id,
        args.attach_timeout,
        adb_path=args.adb_path,
        frida_address=args.frida_address,
    )
    target_pid, pid_source = resolve_target_pid(
        device,
        args.package,
        explicit_pid=args.pid,
        device_id=args.device_id,
        adb_path=args.adb_path,
    )
    if target_pid is None:
        raise RuntimeError(f"Could not find target process for package/name {args.package!r}")

    session = None
    script = None
    try:
        try:
            session = device.attach(target_pid)
        except Exception as exc:
            raise RuntimeError(
                f"Frida attach failed for pid {target_pid} on device {device.id}: "
                f"{type(exc).__name__}: {exc}. "
                "If process listing works but every attach says 'frida-server: closed', "
                "restart frida-server with a binary matching local frida-python and Android ABI."
            ) from exc
        script = session.create_script(build_frida_js(args))
        script.on("message", on_message)
        script.load()

        deadline = time.monotonic() + args.timeout
        while time.monotonic() < deadline and status not in {"ngsm-token", "ngsm-token-error", "error"}:
            time.sleep(0.1)
    finally:
        if script is not None:
            try:
                script.unload()
            except Exception:
                pass
        if session is not None:
            try:
                session.detach()
            except Exception:
                pass

    if status == "started":
        status = "timeout"
    session_event = last_event(events, "session")
    backend_event = last_event(events, "security-backend")
    ngsm_event = last_event(events, "ngsm-token")
    run_event = last_event(events, "run-callback")
    native_init_event = last_event(events, "native-export-init")
    native_run_event = last_event(events, "native-export-run")
    native_switch_event = last_event(events, "native-export-switch")
    native_state_event = last_event(events, "native-state")
    native_log_event = last_event(events, "native-log")
    return {
        "status": status,
        "package": args.package,
        "pid": target_pid,
        "pidSource": pid_source,
        "serviceId": args.service_id,
        "guid": args.guid,
        "npaCodePresent": bool(args.npa_code),
        "noInit": args.no_init,
        "runResult": run_event,
        "session": session_event,
        "securityBackend": backend_event,
        "ngsmToken": str((ngsm_event or {}).get("ngsmToken") or ""),
        "ngsmResult": ngsm_event,
        "nativeInit": native_init_event,
        "nativeRun": native_run_event,
        "nativeSwitch": native_switch_event,
        "nativeState": native_state_event,
        "nativeLog": native_log_event,
        "events": events,
        "errors": script_errors,
    }


def import_frida() -> Any:
    try:
        import frida  # type: ignore
    except ImportError as exc:
        raise SystemExit("Python package 'frida' is required: python -m pip install frida-tools") from exc
    return frida


def get_frida_device(
    frida: Any,
    device_id: str,
    timeout: float,
    *,
    adb_path: str = "adb",
    frida_address: str = "",
) -> Any:
    manager = frida.get_device_manager()
    if frida_address:
        return manager.add_remote_device(frida_address)
    if device_id:
        if looks_like_adb_serial(device_id):
            address = ensure_remote_frida_device(device_id, adb_path=adb_path)
            return manager.add_remote_device(address)
        try:
            return manager.get_device(device_id, timeout=timeout)
        except Exception:
            raise
    try:
        return frida.get_usb_device(timeout=timeout)
    except Exception:
        return frida.get_local_device()


def looks_like_adb_serial(value: str) -> bool:
    text = (value or "").strip()
    if not text:
        return False
    if ":" in text:
        return True
    return text.startswith("emulator-")


def ensure_remote_frida_device(serial: str, *, adb_path: str) -> str:
    command = [adb_path, "-s", serial, "forward", "tcp:27042", "tcp:27042"]
    try:
        completed = subprocess.run(command, check=True, capture_output=True, text=True, timeout=15)
    except FileNotFoundError as exc:
        raise RuntimeError(f"adb not found: {adb_path}") from exc
    except subprocess.CalledProcessError as exc:
        stderr = (exc.stderr or "").strip()
        stdout = (exc.stdout or "").strip()
        detail = stderr or stdout or str(exc)
        raise RuntimeError(f"adb forward failed for {serial}: {detail}") from exc
    if completed.stdout.strip():
        print(f"[*] adb forward: {completed.stdout.strip()}")
    return "127.0.0.1:27042"


def resolve_target_pid(
    device: Any,
    package: str,
    *,
    explicit_pid: int | None,
    device_id: str,
    adb_path: str,
) -> tuple[int | None, str]:
    if explicit_pid is not None:
        return explicit_pid, "explicit"
    if looks_like_adb_serial(device_id):
        adb_pid = find_target_pid_via_adb(device_id, package, adb_path=adb_path)
        if adb_pid is not None:
            print(f"[*] Resolved target pid via adb: {adb_pid}")
            return adb_pid, "adb"
    frida_pid = find_target_pid(device, package)
    if frida_pid is not None:
        return frida_pid, "frida-enumerate"
    return None, "not-found"


def run_adb(serial: str, adb_path: str, *adb_args: str, timeout: float = 10.0) -> subprocess.CompletedProcess[str]:
    command = [adb_path, "-s", serial, *adb_args]
    try:
        return subprocess.run(command, check=True, capture_output=True, text=True, timeout=timeout)
    except FileNotFoundError as exc:
        raise RuntimeError(f"adb not found: {adb_path}") from exc


def find_target_pid_via_adb(serial: str, package: str, *, adb_path: str) -> int | None:
    try:
        completed = run_adb(serial, adb_path, "shell", "pidof", package, timeout=8.0)
    except subprocess.CalledProcessError:
        completed = None
    if completed is not None:
        pids = [chunk.strip() for chunk in completed.stdout.split() if chunk.strip().isdigit()]
        if pids:
            return int(pids[0])
    try:
        completed = run_adb(serial, adb_path, "shell", "ps", "-A", timeout=12.0)
    except subprocess.CalledProcessError:
        return None
    for line in completed.stdout.splitlines():
        parts = line.split()
        if len(parts) < 2:
            continue
        name = parts[-1]
        if name == package:
            for item in parts:
                if item.isdigit():
                    return int(item)
    return None


def _candidate_score(process: Any, package: str) -> int:
    package_lower = package.lower()
    name = str(process.name)
    params = getattr(process, "parameters", {})
    apps = params.get("applications", []) if isinstance(params, dict) else []
    app_names = [str(app) for app in apps]
    app_names_lower = [item.lower() for item in app_names]
    if package in app_names:
        return 100
    if package_lower in app_names_lower:
        return 95
    if name == package:
        return 90
    if name.lower() == package_lower:
        return 85
    if package_lower in name.lower():
        return 70
    if "blue archive" in name.lower():
        return 20
    return -1


def find_target_pid(device: Any, package: str) -> int | None:
    ranked: list[tuple[int, Any]] = []
    for process in device.enumerate_processes():
        score = _candidate_score(process, package)
        if score >= 0:
            ranked.append((score, process))
    if not ranked:
        return None
    ranked.sort(key=lambda item: (item[0], int(item[1].pid)), reverse=True)
    best_score, best_process = ranked[0]
    params = getattr(best_process, "parameters", {})
    print(
        f"[*] Matched target process: name={best_process.name!r}, pid={best_process.pid}, "
        f"score={best_score}, params={params}"
    )
    return int(best_process.pid)


def run_diagnostics(ns: argparse.Namespace) -> int:
    frida = import_frida()
    print(f"frida-python: {frida.__version__}")
    if ns.list_devices:
        for device in frida.enumerate_devices():
            print(f"{device.id}\t{device.type}\t{device.name}")
        return 0

    device = get_frida_device(
        frida,
        ns.device_id,
        ns.attach_timeout,
        adb_path=ns.adb_path,
        frida_address=ns.frida_address,
    )
    print(f"device: {device.id}\t{device.type}\t{device.name}")
    processes = device.enumerate_processes()
    if ns.list_processes:
        for process in processes:
            print(f"{process.pid}\t{process.name}\t{getattr(process, 'parameters', {})}")
        return 0

    candidates = []
    for process in processes:
        name = str(process.name).lower()
        if process.pid == ns.pid or "blue archive" in name or "systemui" in name or "webview" in name:
            candidates.append(process)
    if not candidates:
        candidates = processes[:5]
    for process in candidates[:8]:
        print(f"attach-test: pid={process.pid} name={process.name!r}")
        try:
            session = device.attach(process.pid)
            session.detach()
            print("  ok")
        except Exception as exc:
            print(f"  failed: {type(exc).__name__}: {exc}")
    return 0


def build_frida_js(args: BridgeArgs) -> str:
    package_json = json.dumps(args.package)
    guid_json = json.dumps(args.guid)
    npa_code_json = json.dumps(args.npa_code)
    service_id_json = json.dumps(args.service_id)
    init_wait_json = json.dumps(args.init_wait_ms)
    no_init_json = json.dumps(args.no_init)
    return f"""
'use strict';

const TARGET_PACKAGE = {package_json};
const GUID = {guid_json};
const NPA_CODE = {npa_code_json};
const SERVICE_ID = {service_id_json};
const INIT_WAIT_MS = {init_wait_json};
const NO_INIT = {no_init_json};
const LIBGRAP = 'libgrap-core.so';
const NATIVE_RVAS = {{
  NgsXCoreInit: 0x8fc0d0,
  NgsXCoreRun: 0x8fc31c,
  NgsXCoreSwitch: 0x8fc600,
  WorkerRoot: 0x91d1cc,
  WorkerRunStage: 0x91f470,
  WorkerRunAuth: 0x92fdc0,
  WorkerSwitchStage: 0x923838,
  WorkerSwitchAuth: 0x941038,
}};
const NATIVE_GLOBALS = {{
  obj: 0x1bd71c0,
  stateFlagReady: 0x1bd9ee9,
  stateFlagCleanup: 0x1bd9e0d,
}};

function emit(event, data) {{
  data = data || {{}};
  data.event = event;
  send(data);
}}

function boolString(value) {{
  return value ? 'true' : 'false';
}}

function safeString(value) {{
  if (value === null || value === undefined) {{
    return '';
  }}
  return String(value);
}}

function safeInt(value) {{
  if (value === null || value === undefined) {{
    return null;
  }}
  try {{
    return parseInt(String(value), 10);
  }} catch (e) {{
    return null;
  }}
}}

function hexPtr(value) {{
  try {{
    return ptr(value).toString();
  }} catch (e) {{
    return String(value);
  }}
}}

function tryReadCString(value, maxLen) {{
  try {{
    const p = ptr(value);
    if (p.isNull()) {{
      return '';
    }}
    return Memory.readCString(p, maxLen || 512);
  }} catch (e) {{
    return '';
  }}
}}

function tryReadU8(value) {{
  try {{
    return Memory.readU8(ptr(value));
  }} catch (e) {{
    return null;
  }}
}}

function tryReadU32(value) {{
  try {{
    return Memory.readU32(ptr(value));
  }} catch (e) {{
    return null;
  }}
}}

function tryReadPtr(value) {{
  try {{
    return Memory.readPointer(ptr(value));
  }} catch (e) {{
    return null;
  }}
}}

function getLibgrapModule() {{
  try {{
    return Process.findModuleByName(LIBGRAP);
  }} catch (e) {{
    return null;
  }}
}}

function nativeAddr(rva) {{
  const mod = getLibgrapModule();
  if (!mod) {{
    return null;
  }}
  return mod.base.add(rva);
}}

function emitNativeState(stage) {{
  try {{
    const mod = getLibgrapModule();
    if (!mod) {{
      emit('native-state', {{ stage: stage, moduleLoaded: false }});
      return;
    }}
    const objGlobal = mod.base.add(NATIVE_GLOBALS.obj);
    const objPtr = tryReadPtr(objGlobal);
    const state = {{
      stage: stage,
      moduleLoaded: true,
      moduleBase: hexPtr(mod.base),
      objGlobal: hexPtr(objGlobal),
      objPtr: objPtr ? hexPtr(objPtr) : '',
      readyFlag: tryReadU8(mod.base.add(NATIVE_GLOBALS.stateFlagReady)),
      cleanupFlag: tryReadU8(mod.base.add(NATIVE_GLOBALS.stateFlagCleanup)),
    }};
    if (objPtr && !objPtr.isNull()) {{
      state.objState = tryReadU32(objPtr.add(2144));
      state.objFlag2136 = tryReadU8(objPtr.add(2136));
      state.objFlag2153 = tryReadU8(objPtr.add(2153));
      state.objFlag2155 = tryReadU8(objPtr.add(2155));
      const ptr2168 = tryReadPtr(objPtr.add(2168));
      state.objPtr2168 = ptr2168 ? hexPtr(ptr2168) : '';
    }}
    emit('native-state', state);
  }} catch (e) {{
    emit('bridge-note', {{ stage: 'native-state', message: String(e) }});
  }}
}}

function shouldEmitNativeLog(tag, text) {{
  const joined = (safeString(tag) + ' ' + safeString(text)).toLowerCase();
  return (
    joined.indexOf('ngs-x') >= 0 ||
    joined.indexOf('ngsx') >= 0 ||
    joined.indexOf('module=') >= 0 ||
    joined.indexOf('retcode=') >= 0 ||
    joined.indexOf('code=') >= 0
  );
}}

function installAndroidLogHooks() {{
  if (globalThis.__codexAndroidLogHooksInstalled) {{
    return;
  }}
  globalThis.__codexAndroidLogHooksInstalled = true;

  function attachWrite(name, address, argTagIndex, argTextIndex) {{
    if (!address) {{
      return;
    }}
    Interceptor.attach(address, {{
      onEnter(args) {{
        const tag = tryReadCString(args[argTagIndex], 256);
        const text = tryReadCString(args[argTextIndex], 2048);
        if (!shouldEmitNativeLog(tag, text)) {{
          return;
        }}
        emit('native-log', {{
          api: name,
          tag: tag,
          text: text,
          caller: hexPtr(this.returnAddress)
        }});
      }}
    }});
  }}

  attachWrite('__android_log_write', Module.findExportByName(null, '__android_log_write'), 1, 2);
  attachWrite('__android_log_buf_write', Module.findExportByName(null, '__android_log_buf_write'), 2, 3);
}}

function installNativeHooks(retries) {{
  if (globalThis.__codexNativeHooksInstalled) {{
    return;
  }}
  const mod = getLibgrapModule();
  if (!mod) {{
    if (retries <= 0) {{
      emit('bridge-note', {{ stage: 'native-hooks', message: 'libgrap-core.so not loaded' }});
      return;
    }}
    setTimeout(function () {{
      installNativeHooks(retries - 1);
    }}, 250);
    return;
  }}
  globalThis.__codexNativeHooksInstalled = true;
  installAndroidLogHooks();

  function attachNamed(eventName, address, payloadBuilder) {{
    if (!address) {{
      emit('bridge-note', {{ stage: 'native-hook', message: eventName + ' missing address' }});
      return;
    }}
    Interceptor.attach(address, {{
      onEnter(args) {{
        const payload = payloadBuilder ? payloadBuilder(args) : {{}};
        payload.phase = 'enter';
        payload.address = hexPtr(address);
        emit(eventName, payload);
        emitNativeState(eventName + ':enter');
      }},
      onLeave(retval) {{
        emit(eventName, {{
          phase: 'leave',
          address: hexPtr(address),
          retval: hexPtr(retval)
        }});
        emitNativeState(eventName + ':leave');
      }}
    }});
  }}

  attachNamed('native-export-init', Module.findExportByName(LIBGRAP, 'NgsXCoreInit'), function (args) {{
    return {{ arg0: hexPtr(args[0]) }};
  }});
  attachNamed('native-export-run', Module.findExportByName(LIBGRAP, 'NgsXCoreRun'), function (args) {{
    return {{
      guid: tryReadCString(args[0], 256),
      npaCode: tryReadCString(args[1], 256),
      arg0: hexPtr(args[0]),
      arg1: hexPtr(args[1]),
    }};
  }});
  attachNamed('native-export-switch', Module.findExportByName(LIBGRAP, 'NgsXCoreSwitch'), function (args) {{
    return {{
      arg0: hexPtr(args[0]),
      arg1: hexPtr(args[1]),
      arg2: hexPtr(args[2]),
    }};
  }});

  attachNamed('native-worker-root', nativeAddr(NATIVE_RVAS.WorkerRoot));
  attachNamed('native-worker-run-stage', nativeAddr(NATIVE_RVAS.WorkerRunStage));
  attachNamed('native-worker-run-auth', nativeAddr(NATIVE_RVAS.WorkerRunAuth));
  attachNamed('native-worker-switch-stage', nativeAddr(NATIVE_RVAS.WorkerSwitchStage));
  attachNamed('native-worker-switch-auth', nativeAddr(NATIVE_RVAS.WorkerSwitchAuth));

  emit('bridge-note', {{
    stage: 'native-hooks',
    moduleBase: hexPtr(mod.base),
    message: 'native hooks installed'
  }});
  emitNativeState('native-hooks-installed');
}}

function classAvailable(name) {{
  try {{
    Java.use(name);
    return true;
  }} catch (e) {{
    return false;
  }}
}}

function resultToObject(result) {{
  if (result === null || result === undefined) {{
    return {{ isOK: false, code: -1, message: 'null result' }};
  }}
  const out = {{}};
  try {{ out.isOK = result.IsOK(); }} catch (e) {{ out.isOKError = String(e); }}
  try {{ out.code = result.Code(); }} catch (e) {{ out.codeError = String(e); }}
  try {{ out.message = String(result.Message()); }} catch (e) {{ out.messageError = String(e); }}
  return out;
}}

function getDeclaredFieldValue(obj, fieldName) {{
  if (obj === null || obj === undefined) {{
    return undefined;
  }}
  try {{
    return obj[fieldName].value;
  }} catch (e) {{}}
  try {{
    const field = obj.getClass().getDeclaredField(fieldName);
    field.setAccessible(true);
    return field.get(obj);
  }} catch (e) {{}}
  return undefined;
}}

function tryCall(obj, methodName) {{
  if (obj === null || obj === undefined) {{
    return undefined;
  }}
  try {{
    return obj[methodName]();
  }} catch (e) {{
    return undefined;
  }}
}}

function sessionToObject(session) {{
  if (session === null || session === undefined) {{
    return {{ present: false }};
  }}
  return {{
    present: true,
    className: safeString(tryCall(tryCall(session, 'getClass'), 'getName')),
    loginType: safeInt(tryCall(session, 'getType')),
    userId: safeString(tryCall(session, 'getUserId')),
    npaCode: safeString(tryCall(session, 'getNpaCode')),
    npTokenPresent: safeString(tryCall(session, 'getNptoken')).length > 0,
    sessionTokenPresent: safeString(tryCall(session, 'getSessionToken')).length > 0,
    memId: safeString(tryCall(session, 'getMemId')),
    serverMemType: safeInt(tryCall(session, 'getServerMemType')),
    umKey: safeString(tryCall(session, 'getUMKey'))
  }};
}}

function ngsmResultToObject(result) {{
  const resultSet = getDeclaredFieldValue(result, 'result');
  return {{
    className: safeString(tryCall(tryCall(result, 'getClass'), 'getName')),
    errorCode: safeInt(getDeclaredFieldValue(result, 'errorCode')),
    errorText: safeString(getDeclaredFieldValue(result, 'errorText')),
    errorDetail: safeString(getDeclaredFieldValue(result, 'errorDetail')),
    ngsmToken: safeString(getDeclaredFieldValue(resultSet, 'ngsmToken'))
  }};
}}

function getCurrentActivity() {{
  const ActivityThread = Java.use('android.app.ActivityThread');
  const thread = ActivityThread.currentActivityThread();
  if (thread === null) {{
    throw new Error('ActivityThread.currentActivityThread() returned null');
  }}
  const activities = thread.mActivities.value;
  const values = Java.cast(activities, Java.use('java.util.Map')).values().iterator();
  let fallback = null;
  while (values.hasNext()) {{
    const record = values.next();
    const activity = record.activity.value;
    if (activity === null) {{
      continue;
    }}
    fallback = activity;
    try {{
      if (!record.paused.value) {{
        return activity;
      }}
    }} catch (e) {{
      return activity;
    }}
  }}
  if (fallback !== null) {{
    return fallback;
  }}
  throw new Error('No Activity found in ActivityThread.mActivities; start the game UI first');
}}

function waitForJava(retries, delayMs) {{
  if (typeof Java === 'undefined') {{
    if (retries <= 0) {{
      emit('error', {{
        stage: 'bootstrap',
        message: 'Java runtime unavailable in target process after waiting; attach to the Android app process instead of a native-only helper process'
      }});
      return;
    }}
    setTimeout(function () {{
      waitForJava(retries - 1, delayMs);
    }}, delayMs);
    return;
  }}
  Java.perform(function () {{
  try {{
    installNativeHooks(120);
    function emitSessionState() {{
      try {{
        const SessionManager = Java.use('com.nexon.core.session.NXToySessionManager');
        emit('session', sessionToObject(SessionManager.getInstance().getSession()));
      }} catch (e) {{
        emit('session', {{ present: false, error: String(e) }});
      }}
    }}

    function emitSecurityBackend() {{
      try {{
        const Factory = Java.use('kr.co.nexon.npaccount.security.NPNgsFactory');
        const OptionManager = Java.use('com.nexon.platform.settings.NXPOptionManager');
        const options = OptionManager.getInstance().getOptions();
        const backend = Factory.INSTANCE.value.createNexonGameSecurity();
        emit('security-backend', {{
          className: backend ? safeString(tryCall(tryCall(backend, 'getClass'), 'getName')) : '',
          isNgsxEnabled: !!tryCall(options, 'isNgsxEnabled'),
          isNgsmEnabled: !!tryCall(options, 'isNgsmEnabled')
        }});
      }} catch (e) {{
        emit('security-backend', {{ error: String(e) }});
      }}
    }}

    function requestNgsmToken(activity, trigger) {{
      try {{
        if (globalThis.__codexNgsmRequested) {{
          return;
        }}
        globalThis.__codexNgsmRequested = true;
        const TokenListener = Java.use('kr.co.nexon.npaccount.listener.NXPGetNgsmTokenListener');
        const ListenerImpl = Java.registerClass({{
          name: 'org.codex.NgsmTokenListener' + Date.now(),
          implements: [TokenListener],
          methods: {{
            onResult: function (result) {{
              const out = ngsmResultToObject(result);
              out.trigger = trigger;
              emit('ngsm-token', out);
            }}
          }}
        }});
        try {{
          const Factory = Java.use('kr.co.nexon.npaccount.security.NPNgsFactory');
          const backend = Factory.INSTANCE.value.createNexonGameSecurity();
          if (backend) {{
            emit('get-ngsm-token-call', {{
              via: 'NPNgsFactory',
              trigger: trigger,
              backendClass: safeString(tryCall(tryCall(backend, 'getClass'), 'getName'))
            }});
            backend.getNgsToken(activity.getApplicationContext(), ListenerImpl.$new());
            return;
          }}
        }} catch (e) {{
          emit('bridge-note', {{
            stage: 'factory-getNgsmToken',
            message: String(e)
          }});
        }}
        const NPAccount = Java.use('kr.co.nexon.npaccount.NPAccount');
        emit('get-ngsm-token-call', {{ via: 'NPAccount', trigger: trigger }});
        NPAccount.getInstance(activity).getNgsmToken(ListenerImpl.$new());
      }} catch (e) {{
        emit('error', {{ stage: 'getNgsmToken', message: String(e), stack: e.stack || '' }});
      }}
    }}

    function runNgsX(activity) {{
      try {{
        if (globalThis.__codexNgsXDidRun) {{
          return;
        }}
        globalThis.__codexNgsXDidRun = true;
        emitNativeState('before-run-call');
        if (!classAvailable('com.nexon.ngsx.NgsX')) {{
          emit('bridge-note', {{ stage: 'Run', message: 'NgsX class unavailable; skip direct run' }});
          requestNgsmToken(activity, 'no-ngsx-class');
          return;
        }}
        const NgsX = Java.use('com.nexon.ngsx.NgsX');
        const RunInterface = Java.use('com.nexon.ngsx.NgsX$RunCallbackListener');
        const RunCb = Java.registerClass({{
          name: 'org.codex.NgsXRunCallback' + Date.now(),
          implements: [RunInterface],
          methods: {{
            OnRun: function (result) {{
              emit('run-callback', resultToObject(result));
              emitNativeState('run-callback');
              emitSessionState();
              requestNgsmToken(activity, 'run-callback');
            }}
          }}
        }});
        emit('run-call', {{ guid: GUID, npaCode: NPA_CODE }});
        NgsX.getInst().Run(GUID, NPA_CODE, RunCb.$new());
      }} catch (e) {{
        emit('error', {{ stage: 'Run', message: String(e), stack: e.stack || '' }});
      }}
    }}

    Java.scheduleOnMainThread(function () {{
      try {{
        const activity = getCurrentActivity();
        emit('attached', {{
          package: TARGET_PACKAGE,
          activity: String(activity.getClass().getName()),
          hasNgsXClass: classAvailable('com.nexon.ngsx.NgsX'),
          hasNgsmClass: classAvailable('com.nexon.ngsm.Ngsm')
        }});
        emitSessionState();
        emitSecurityBackend();
        if (NO_INIT) {{
          runNgsX(activity);
          setTimeout(function () {{
            requestNgsmToken(activity, 'no-init-fallback');
          }}, INIT_WAIT_MS);
          return;
        }}
        if (!classAvailable('com.nexon.ngsx.NgsX')) {{
          emit('bridge-note', {{ stage: 'Init', message: 'NgsX class unavailable; request token directly' }});
          requestNgsmToken(activity, 'init-skip-no-ngsx');
          return;
        }}
        const NgsX = Java.use('com.nexon.ngsx.NgsX');
        const InitInterface = Java.use('com.nexon.ngsx.NgsX$InitCallbackListener');
        const inst = NgsX.getInst();
        const InitCb = Java.registerClass({{
          name: 'org.codex.NgsXInitCallback' + Date.now(),
          implements: [InitInterface],
          methods: {{
            OnInit: function (result) {{
              emit('init-callback', resultToObject(result));
              runNgsX(activity);
            }}
          }}
        }});
        emit('init-call', {{ serviceId: SERVICE_ID }});
        inst.Init(activity, SERVICE_ID, InitCb.$new());
        setTimeout(function () {{
          emit('init-fallback-run', {{ delayMs: INIT_WAIT_MS }});
          runNgsX(activity);
          requestNgsmToken(activity, 'init-fallback');
        }}, INIT_WAIT_MS);
      }} catch (e) {{
        emit('error', {{ stage: 'main-thread', message: String(e), stack: e.stack || '' }});
      }}
    }});
  }} catch (e) {{
    emit('error', {{ stage: 'Java.perform', message: String(e), stack: e.stack || '' }});
  }}
  }});
}}

waitForJava(60, 250);
"""


def load_toy_login(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def find_first(obj: Any, *names: str) -> Any:
    wanted = {name.lower() for name in names}
    if isinstance(obj, Mapping):
        for key, value in obj.items():
            if str(key).lower() in wanted:
                return value
        for value in obj.values():
            found = find_first(value, *names)
            if found is not None:
                return found
    elif isinstance(obj, list):
        for item in obj:
            found = find_first(item, *names)
            if found is not None:
                return found
    return None


def last_event(events: Iterable[Mapping[str, Any]], event_name: str) -> dict[str, Any] | None:
    for event in reversed(list(events)):
        if str(event.get("event") or "") == event_name:
            return dict(event)
    return None


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")


if __name__ == "__main__":
    raise SystemExit(main())
