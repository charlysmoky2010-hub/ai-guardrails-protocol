"""Regression tests for non-destructive PHI portal SSD staging."""
import importlib.util
import json
from pathlib import Path
import plistlib
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "phi_portal_ssd_stage_20261025.py"
SPEC = importlib.util.spec_from_file_location("ssd_portal_stage", SCRIPT)
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)

class PortalStageTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        home = root / "home"
        ssd = root / "ssd"
        source = home / "PHI-BRAIN-CANONICAL"
        (source / "tools").mkdir(parents=True)
        (source / "tools/phi_portal.py").write_text("print('portal')\n")
        (source / ".env").write_text("SUPER_SECRET=never_copy\n")
        (source / "data.db").write_text("private database")
        (source / "logs").mkdir()
        (source / "logs/launchd.log").write_text("private log")
        (source / "public").mkdir()
        (source / "public" / "index.html").write_text("<h1>Test</h1>")
        try:
            (source / "tools/link-secret").symlink_to(source / ".env")
        except OSError:
            pass
        launch = home / "Library/LaunchAgents"
        launch.mkdir(parents=True)
        plist = launch / "local.phi-brain.communication-portal.plist"
        with plist.open("wb") as f:
            plistlib.dump({
                "Label": "local.phi-brain.communication-portal",
                "ProgramArguments": ["/usr/bin/python3", str(source / "tools/phi_portal.py")],
                "WorkingDirectory": str(source),
                "RunAtLoad": True, "KeepAlive": True,
                "EnvironmentVariables": {"PRIVATE_TOKEN": "do_not_copy"},
            }, f)
        base = ssd / "CERBERRUS144_OS"
        base.mkdir(parents=True)
        self.home,self.ssd,self.source,self.plist,self.base=home,ssd,source,plist,base
        self.original_plist=plist.read_bytes()
    def patch_paths(self):
        return patch.multiple(module, HOME=self.home, SSD=self.ssd, SRC=self.source,
                              PLIST=self.plist, BASE=self.base)

    def test_stage_protects_secrets_and_originals(self):
        with self.patch_paths(), patch.object(module.os.path,"ismount",return_value=True):
            module.main()
        stages=list(self.base.glob("COMMUNICATION_PORTAL_STAGING_*"))
        self.assertEqual(len(stages),1)
        stage=stages[0]; new_src=stage/"project"
        self.assertTrue((new_src/"tools/phi_portal.py").exists())
        self.assertFalse((new_src/".env").exists())
        self.assertFalse((new_src/"data.db").exists())
        self.assertFalse((new_src/"logs").exists())
        self.assertFalse((new_src/"tools/link-secret").exists())
        self.assertEqual(self.plist.read_bytes(),self.original_plist)
        preview=plistlib.loads((stage/"NOT_INSTALLED.preview.plist").read_bytes())
        self.assertFalse(preview["RunAtLoad"])
        self.assertFalse(preview["KeepAlive"])
        self.assertNotIn("EnvironmentVariables",preview)
        self.assertTrue(preview["ProgramArguments"][1].startswith(str(new_src)))
        report=json.loads((stage/"REPORT.json").read_text())
        self.assertFalse(report["activated_portal"])
        self.assertGreater(report["files_sha256_verified"],0)
        self.assertNotIn("do_not_copy",json.dumps(report))
    def test_missing_ssd_fails_without_creating_stage(self):
        with self.patch_paths(), patch.object(module.os.path,"ismount",return_value=False):
            with self.assertRaises(SystemExit):
                module.main()
        self.assertEqual(list(self.base.iterdir()),[])
    def test_mismatched_script_fails_closed(self):
        d=plistlib.loads(self.plist.read_bytes())
        d["ProgramArguments"] = ["/usr/bin/python3","/tmp/unknown.py"]
        with self.plist.open("wb") as f: plistlib.dump(d,f)
        with self.patch_paths(), patch.object(module.os.path,"ismount",return_value=True):
            with self.assertRaises(SystemExit):
                module.main()
        self.assertEqual(list(self.base.iterdir()),[])

if __name__=="__main__":
    unittest.main()
