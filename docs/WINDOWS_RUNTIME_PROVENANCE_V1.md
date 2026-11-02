# Windows runtime provenance — read-only evidence candidate

**Status: source-only developer candidate.** This utility has not been run against Lappy's installed services, qualified on VN1, or used to attest a live Portal → Project Runner → Executor route. Tests use synthetic subprocess results. It is not an authorization, repair, service installer, remote command broker, or model-runtime qualifier.

`tools/inspect_windows_runtime.py` gives operators a minimal, deliberately redacted, local-only snapshot of selected Windows services, scheduled-task states, and two named Git checkouts. It writes one JSON object to stdout; no files, service configurations, credentials, permissions, tasks, or repository state are changed. The tool does read executable bytes to compute an optional launcher digest, and `git status` can inspect tracked files.

From an already authorized Windows PowerShell session in a checked-out copy of Discovery:

```powershell
py -3 tools/inspect_windows_runtime.py --portal-root 'D:\VERA\portal' --runner-root 'D:\VERA\project-runner'
```

This command is **only an operator example**, not evidence that the utility ran or that those directories are the loaded service source. No redirection, scheduled task, auto-start, or background collector is provided.

The fixed inventory covers VeraPortAgent, VeraTrainingDayHostBroker, VeraMeshTunnelRuntime, VeraMonoPilot; and Executor Device, Vera Local Inference Gateway, WorkBridge Commander Recovery, WorkBridgeMCP, VeraUnifiedRuntime, VeraPortal-PR22-SourceOnly, VERA-Blotter scheduled tasks. Additional host processes, tasks, WSL/container services, VN1/VN2 devices, and authenticated gateway traffic are *not* covered.

The report contains only: service name/state/PID, executable basename and optional SHA-256 of the **launcher executable**; task name/state; checkout Git HEAD and tracked-dirty flag; timestamp; and fixed evidence limits. It intentionally omits hostnames, UPNs, absolute paths, process command lines, task actions, environment variables, secrets and command output. Missing paths or missing records are not evidence that a component is absent globally. An executable checksum (especially Python) does **not** attest imported module bytes, package environment, source commit loaded into RAM, active request route, host identity, signing key custody, or provenance after the process started.

The script invokes only fixed read-oriented PowerShell CIM/task queries and `git rev-parse` / `git status` through argument arrays, not a shell-built string containing caller inputs. The PowerShell code does not inspect or serialize command lines or task actions. Errors intentionally suppress raw subprocess stderr, which can include private paths. Output should still be treated as operational data; do not publish real host snapshots automatically.

Security and release boundaries:

- This reports *local observations*, not a signed or host-authenticated attestation. A caller can modify output or replace the probe, and service names alone are not identities.
- `Running` is availability evidence, not functional health. `Ready` is registration, not execution. `Stopped` is not proof that another unrelated process doesn't implement the same capability.
- A Git checkout HEAD is not the running Python import graph. Do not infer a deployed Portal or Runner version, even if it matches a reviewed PR.
- This probe cannot repair Portal's owner-held command-driver hostile failures, authenticate Executor, establish durable receipt custody or qualify an end-to-end effect.
- Treat a live result as private operational evidence until an owner approves a redacted summary. The script does no network transfers or uploads.
- Windows native CIM and ScheduledTasks cmdlets require compatible Windows PowerShell and sufficient read privileges. Behavior on actual Windows systems is **not qualified** by the included cross-platform synthetic tests.

A future independently tested runtime binding should have each **running service itself** report signed or otherwise integrity-protected process/module metadata and a correlation ID, then cross-check it against the observed PID, original installer artifact, and exact immutable release manifest. That is intentionally outside this utility.
