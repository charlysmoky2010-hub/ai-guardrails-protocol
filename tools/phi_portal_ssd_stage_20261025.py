#!/usr/bin/env python3
"""Prepare a non-destructive SSD-only preview of PHI communication portal.
Does not activate, stop, modify or delete any running services or source files.
Does not access Desktop. Never publishes private configuration data.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib, json, os, plistlib, re, shutil

HOME = Path.home()
SSD = Path("/Volumes/SSD4TB")
SRC = HOME / "PHI-BRAIN-CANONICAL"
PLIST = HOME / "Library/LaunchAgents/local.phi-brain.communication-portal.plist"
BASE = SSD / "CERBERRUS144_OS"
EXCLUDE_DIR = {".git", "node_modules", "__pycache__", ".venv", "venv", ".cache", "logs"}
EXCLUDE_SUFFIX = {".sqlite3", ".sqlite", ".db", ".key", ".pem", ".p12", ".log"}
EXCLUDE_NAMES = {".env", ".env.local", ".env.production", ".DS_Store"}
SCAN_SUFFIX = {".py", ".sh", ".command", ".json", ".yaml", ".yml", ".toml"}
ABS_REF = re.compile(rb"/Users/|Path\s*\.\s*home\s*\(|expanduser\s*\(")

def sha(path):
    digest = hashlib.sha256()
    with path.open("rb") as inp:
        for block in iter(lambda: inp.read(1048576), b""):
            digest.update(block)
    return digest.hexdigest()

def walk_files(root):
    for parent, dirs, names in os.walk(root, followlinks=False):
        dirs[:] = [d for d in dirs if not (Path(parent) / d).is_symlink()]
        for name in names:
            p = Path(parent) / name
            if p.is_file() and not p.is_symlink():
                yield p

def main():
    if not os.path.ismount(SSD) or SSD.is_symlink():
        raise SystemExit("DURDURULDU: SSD4TB gercek bagli disk degil.")
    if not SRC.is_dir() or SRC.is_symlink() or not BASE.is_dir() or BASE.is_symlink():
        raise SystemExit("DURDURULDU: kaynak veya hedef proje koku guvensiz.")
    if not PLIST.is_file() or PLIST.is_symlink():
        raise SystemExit("DURDURULDU: LaunchAgent dosyasi bulunamadi.")
    with PLIST.open("rb") as f:
        conf = plistlib.load(f)
    script = SRC / "tools/phi_portal.py"
    args = conf.get("ProgramArguments", [])
    if conf.get("Label") != "local.phi-brain.communication-portal":
        raise SystemExit("DURDURULDU: Beklenmeyen servis.")
    if Path(conf.get("WorkingDirectory", "")) != SRC or not script.is_file():
        raise SystemExit("DURDURULDU: Gercek portal yolu beklenenden farkli.")
    if not isinstance(args, list) or str(script) not in args:
        raise SystemExit("DURDURULDU: Portal betigi ProgramArguments icinde degil.")
    stage = BASE / ("COMMUNICATION_PORTAL_STAGING_" +
                    datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ"))
    stage.mkdir(mode=0o700, exist_ok=False)
    ignored_paths = []
    def ignore(parent, names):
        rejected = []
        for name in names:
            p = Path(parent) / name
            is_rejected = (p.is_symlink() or
                           (p.is_dir() and name in EXCLUDE_DIR) or
                           (p.is_file() and (name in EXCLUDE_NAMES or p.suffix.lower() in EXCLUDE_SUFFIX)) or
                           name.startswith(".env."))
            if is_rejected:
                rejected.append(name)
                ignored_paths.append(str(p.relative_to(SRC)))
        return rejected
    dest = stage / "project"
    try:
        shutil.copytree(SRC, dest, ignore=ignore, symlinks=False)
        if not (dest / "tools/phi_portal.py").is_file():
            raise RuntimeError("Portal betigi kopyalanamadi")
        checked = 0
        for p in walk_files(dest):
            original = SRC / p.relative_to(dest)
            if sha(original) != sha(p):
                raise RuntimeError("SHA256 mismatch: " + str(p.relative_to(dest)))
            checked += 1
        preview = dict(conf)
        preview["Label"] = "local.phi-brain.communication-portal.ssd-preview"
        preview["WorkingDirectory"] = str(dest)
        preview["ProgramArguments"] = [
            str(dest) + a[len(str(SRC)):] if a.startswith(str(SRC) + "/") else a
            for a in args
        ]
        preview["RunAtLoad"] = False
        preview["KeepAlive"] = False
        for sensitive_key in ("EnvironmentVariables", "Sockets", "MachServices"):
            preview.pop(sensitive_key, None)
        with (stage / "NOT_INSTALLED.preview.plist").open("wb") as f:
            plistlib.dump(preview, f)
        hits = []
        for p in walk_files(dest):
            if p.suffix.lower() in SCAN_SUFFIX and p.stat().st_size <= 1048576:
                n = len(ABS_REF.findall(p.read_bytes()))
                if n:
                    hits.append({"path": str(p.relative_to(dest)), "matches": n})
        report = {
            "status": "STAGED_LOCKED_NOT_ACTIVE",
            "source": str(SRC),
            "staging": str(stage),
            "files_sha256_verified": checked,
            "excluded_paths": ignored_paths,
            "home_reference_candidates": hits,
            "environment_variable_names_not_copied": sorted(conf.get("EnvironmentVariables", {}).keys()),
            "needs_manual_runtime_and_path_review": True,
            "modified_original_plist": False,
            "modified_original_code": False,
            "activated_portal": False,
        }
        (stage / "REPORT.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    except BaseException:
        print("HAZIRLIK DURDU. KAYNAKLAR KORUNDU. KISMI_SSD_KLASOR:", stage)
        raise
    print("SSD_STAGE:", stage)
    print("HASH_OK_FILE_COUNT:", checked)
    print("EXCLUDED:", len(ignored_paths))
    print("MAC_WRITE_REVIEW_FILES:", len(hits))
    for item in hits[:20]:
        print("REVIEW:", item["path"], item["matches"])
    print("REPORT:", stage / "REPORT.json")
    print("SAFE: ORIGINALS_UNCHANGED; NOT_ACTIVATED; NO_DELETION")
if __name__ == "__main__":
    main()
