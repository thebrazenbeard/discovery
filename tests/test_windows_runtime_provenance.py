import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

MOD_PATH = Path(__file__).parents[1] / "tools" / "inspect_windows_runtime.py"
spec = importlib.util.spec_from_file_location("runtime_probe", MOD_PATH)
probe = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = probe
spec.loader.exec_module(probe)


class ReadOnlyWindowsProvenanceTests(unittest.TestCase):
    def test_private_process_fields_cannot_escape(self):
        raw = json.dumps({"services": [{"name": "VeraPortAgent", "state": "Running", "pid": 40,
                "process": "python.exe", "launcher_sha256": "A" * 64,
                "ExecutablePath": "C:/private/tokens/secret.py",
                "CommandLine": "--token NEVER_PUBLISH_THIS",
                "Environment": {"TOKEN": "NEVER_PUBLISH_THIS"}}],
                "tasks": [{"name": "Executor Device", "state": "Ready", "Action": "--secret"}]})
        scrubbed = probe.sanitize_powershell_report(raw)
        encoded = json.dumps(scrubbed)
        self.assertNotIn("NEVER_PUBLISH_THIS", encoded)
        self.assertNotIn("C:/", encoded)
        self.assertNotIn("--secret", encoded)
        self.assertFalse(scrubbed["services"][0]["loaded_module_sources_verified"])
        self.assertEqual(scrubbed["services"][0]["launcher_sha256"], "a" * 64)

    def test_windows_command_has_no_shell_or_user_interpolation(self):
        commands = []
        def runner(args, **kw):
            commands.append((args, kw))
            return SimpleNamespace(stdout=json.dumps({"services": [], "tasks": []}))
        self.assertEqual(probe.observe_windows(runner=runner), {"services":[], "tasks":[]})
        args, kwargs = commands[0]
        self.assertEqual(args[:3], ["powershell.exe", "-NoProfile", "-NonInteractive"])
        self.assertFalse(kwargs.get("shell", False))
        self.assertTrue(kwargs["check"])
        self.assertIn("Get-CimInstance", args[4])
        self.assertNotIn("CommandLine", args[4])

    def test_invalid_pid_and_name_fail_closed(self):
        for pid in (True, -1, "42", 2**31):
            with self.subTest(pid=pid), self.assertRaises(probe.ProbeError):
                probe.sanitize_powershell_report(json.dumps({"services":[{
                    "name":"VeraPortAgent","state":"Running","pid":pid}],"tasks":[]}))
        with self.assertRaises(probe.ProbeError):
            probe.sanitize_powershell_report(json.dumps({"services":[{
                "name":"x;Remove-Item C:","state":"Running","pid":1}],"tasks":[]}))

    def test_duplicate_service_is_rejected(self):
        row = {"name":"VeraPortAgent","state":"Running","pid":1}
        with self.assertRaisesRegex(probe.ProbeError, "duplicate"):
            probe.sanitize_powershell_report(json.dumps({"services":[row,row],"tasks":[]}))

    def test_checkout_reports_head_not_active_import(self):
        seen = []
        def runner(args, **kw):
            seen.append(args)
            return SimpleNamespace(stdout="a" * 40 + "\n" if "rev-parse" in args else " M README.md\n")
        with patch.object(Path, "is_dir", return_value=True):
            result = probe.observe_checkout(Path("/synthetic/portal"), runner=runner)
        self.assertTrue(result["present"])
        self.assertEqual(result["head"], "a"*40)
        self.assertTrue(result["tracked_dirty"])
        self.assertFalse(result["loaded_in_resident_runtime_verified"])
        self.assertEqual(len(seen), 2)

    def test_missing_checkout_never_becomes_absence_of_runtime(self):
        with patch.object(Path, "is_dir", return_value=False):
            row = probe.observe_checkout(Path("/absent"))
        self.assertFalse(row["present"])
        self.assertFalse(row["loaded_in_resident_runtime_verified"])

    def test_report_claim_ceilings_explicit(self):
        report = probe.build_report({"services":[],"tasks":[]},{},observed_at="2026-11-02T20:00:00Z")
        self.assertFalse(report["host_identity_authenticated"])
        self.assertFalse(report["portal_runner_executor_integration_verified"])
        self.assertIn("NOT_RUNTIME_ATTESTATION", report["evidence_ceiling"])
        self.assertNotIn("C:", json.dumps(report))

    def test_error_does_not_leak_subprocess_details(self):
        def runner(*args, **kwargs):
            raise subprocess.CalledProcessError(1, ["secret"], stderr="TOKEN_KEY=secret")
        with self.assertRaises(probe.ProbeError) as caught:
            probe.observe_windows(runner=runner)
        self.assertNotIn("TOKEN", str(caught.exception))
        self.assertNotIn("secret", str(caught.exception))

if __name__ == "__main__":
    unittest.main()
