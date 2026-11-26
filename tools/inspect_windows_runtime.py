"""Sanitized read-only Windows host provenance snapshot, without trust claims.

Usage (on an authorized Windows workstation):
    py -3 tools/inspect_windows_runtime.py --portal-root D:\\VERA\\portal \\
      --runner-root D:\\VERA\\project-runner

Only fixed PowerShell/CIM inventory and Git HEAD/dirty checks are performed.
No process command lines, environment, absolute file paths, secrets, or
private host identifiers are written to the report. This cannot attest the
source of imported modules, authenticate an Executor host, or grant effects.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

SCHEMA = "DISCOVERY_WINDOWS_RUNTIME_PROVENANCE_V1"
_GIT_SHA = re.compile(r"[0-9a-f]{40}\Z")
_HASH = re.compile(r"[0-9A-Fa-f]{64}\Z")
_SAFE_NAME = re.compile(r"[A-Za-z0-9 ._()-]{1,100}\Z")

# No caller-controlled string is interpolated into the PowerShell program.
POWERSHELL_INVENTORY = r'''
$ErrorActionPreference = 'Stop'
$services = @('VeraPortAgent','VeraTrainingDayHostBroker','VeraMeshTunnelRuntime','VeraMonoPilot')
$tasks = @('Executor Device','Vera Local Inference Gateway',
 'WorkBridge Commander Recovery','WorkBridgeMCP','VeraUnifiedRuntime',
 'VeraPortal-PR22-SourceOnly','VERA-Blotter')
$inventory = @()
foreach ($name in $services) {
 $s = Get-CimInstance Win32_Service | Where-Object { $_.Name -eq $name } | Select-Object -First 1
 if ($null -eq $s) {
   $inventory += @{name=$name;state='MISSING';pid=0;process='';launcher_sha256=$null}
   continue
 }
 $procName = ''
 $digest = $null
 if ($s.ProcessId -gt 0) {
   $p = Get-CimInstance Win32_Process -Filter "ProcessId=$($s.ProcessId)"
   if ($null -ne $p) {
     $procName = [IO.Path]::GetFileName([string]$p.ExecutablePath)
     try {
       if ($p.ExecutablePath -and [IO.File]::Exists($p.ExecutablePath)) {
         $digest = (Get-FileHash -Algorithm SHA256 -LiteralPath $p.ExecutablePath -ErrorAction Stop).Hash
       }
     } catch { $digest = $null }
   }
 }
 $inventory += @{name=$name;state=[string]$s.State;pid=[int]$s.ProcessId;
                 process=$procName;launcher_sha256=$digest}
}
$taskInventory = @()
foreach ($name in $tasks) {
 $t = @(Get-ScheduledTask -ErrorAction Stop | Where-Object { $_.TaskName -eq $name })
 if ($t.Count -gt 1) { throw 'Ambiguous scheduled task name' }
 $taskInventory += @{name=$name;state=$(if($t.Count -eq 1){[string]$t[0].State}else{'MISSING'})}
}
@{services=$inventory;tasks=$taskInventory} | ConvertTo-Json -Depth 6 -Compress
'''


class ProbeError(ValueError):
    """Source/currentness observation failed; never execution authority."""


def _safe_text(value: Any, label: str, *, allow_empty: bool = False) -> str:
    if type(value) is not str or (not value and not allow_empty) or (
        value and not _SAFE_NAME.fullmatch(value)
    ):
        raise ProbeError(f"invalid {label}")
    return value


def sanitize_powershell_report(raw: str) -> dict[str, Any]:
    """Strictly project fields; unknown fields are discarded, never emitted."""
    try:
        data = json.loads(raw.lstrip("\ufeff"))
    except (ValueError, TypeError) as exc:
        raise ProbeError("invalid inventory JSON") from exc
    if type(data) is not dict or type(data.get("services")) is not list or type(data.get("tasks")) is not list:
        raise ProbeError("invalid inventory structure")
    if len(data["services"]) > 20 or len(data["tasks"]) > 40:
        raise ProbeError("inventory exceeds bounds")
    services = []
    for entry in data["services"]:
        if type(entry) is not dict:
            raise ProbeError("invalid service record")
        name = _safe_text(entry.get("name"), "service name")
        state = _safe_text(entry.get("state"), "service state")
        pid = entry.get("pid")
        if type(pid) is not int or not 0 <= pid < 2**31:
            raise ProbeError("invalid service PID")
        process = _safe_text(entry.get("process", ""), "process basename", allow_empty=True)
        digest = entry.get("launcher_sha256")
        if digest is not None and (type(digest) is not str or not _HASH.fullmatch(digest)):
            raise ProbeError("invalid launcher digest")
        services.append({
            "name": name, "state": state, "pid": pid,
            "process_basename": process or None,
            "launcher_sha256": digest.lower() if digest else None,
            "loaded_module_sources_verified": False,
        })
    tasks = []
    for entry in data["tasks"]:
        if type(entry) is not dict:
            raise ProbeError("invalid task record")
        tasks.append({
            "name": _safe_text(entry.get("name"), "task name"),
            "state": _safe_text(entry.get("state"), "task state"),
        })
    if len({x["name"] for x in services}) != len(services):
        raise ProbeError("duplicate service record")
    if len({x["name"] for x in tasks}) != len(tasks):
        raise ProbeError("duplicate task record")
    return {"services": sorted(services, key=lambda x: x["name"]),
            "tasks": sorted(tasks, key=lambda x: x["name"])}


def observe_windows(*, runner: Callable[..., Any] = subprocess.run) -> dict[str, Any]:
    try:
        completed = runner(
            ["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", POWERSHELL_INVENTORY],
            capture_output=True, text=True, timeout=40, check=True,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        # Do not emit error strings: they can contain local paths or process details.
        raise ProbeError("Windows read-only inventory failed") from exc
    return sanitize_powershell_report(completed.stdout)


def observe_checkout(root: Path, *, runner: Callable[..., Any] = subprocess.run) -> dict[str, Any]:
    if not root.is_dir():
        return {"present": False, "head": None, "tracked_dirty": None,
                "loaded_in_resident_runtime_verified": False}
    try:
        head = runner(["git", "-C", str(root), "rev-parse", "--verify", "HEAD"],
                      capture_output=True, text=True, timeout=8, check=True).stdout.strip()
        dirty = runner(["git", "-C", str(root), "status", "--porcelain", "--untracked-files=no"],
                       capture_output=True, text=True, timeout=12, check=True).stdout
    except (OSError, subprocess.SubprocessError) as exc:
        raise ProbeError("Git checkout inspection failed") from exc
    if not _GIT_SHA.fullmatch(head):
        raise ProbeError("invalid Git HEAD")
    return {"present": True, "head": head, "tracked_dirty": bool(dirty.strip()),
            "loaded_in_resident_runtime_verified": False}


def build_report(host: dict[str, Any], checkouts: dict[str, dict[str, Any]], *,
                 observed_at: str) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "observed_at_utc": observed_at,
        "host_identity_authenticated": False,
        "portal_runner_executor_integration_verified": False,
        "services": host["services"], "tasks": host["tasks"],
        "checkouts": checkouts,
        "evidence_ceiling": "READ_ONLY_LOCAL_OBSERVATION_NOT_RUNTIME_ATTESTATION",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--portal-root", type=Path, required=True)
    parser.add_argument("--runner-root", type=Path, required=True)
    options = parser.parse_args(argv)
    if os.name != "nt":
        print("Windows host required for live probe", file=sys.stderr)
        return 2
    try:
        inventory = observe_windows()
        checkouts = {
            "portal": observe_checkout(options.portal_root),
            "project_runner": observe_checkout(options.runner_root),
        }
        report = build_report(inventory, checkouts,
                              observed_at=datetime.now(timezone.utc).isoformat())
    except ProbeError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(json.dumps(report, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
