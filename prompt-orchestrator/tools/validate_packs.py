#!/usr/bin/env python3
"""Validate opt-in packs in packs/<pack-id>/ against pack format v1.

    python3 tools/validate_packs.py                  every pack under packs/
    python3 tools/validate_packs.py --packs-dir DIR  packs in another folder (tests, fixtures)

Checks per pack: pack.json keys and types, the id against the folder name, sets (each skill
folder under skills/ in exactly one set, each listed skill present), every SKILL.md front matter
(name equals the folder, name pattern, description of at most 1024 characters, the third-party
fields when the pack has an upstream), the payload folder for kind "package", the release lock
for kind "release", the LICENSE file, and skill names that clash with the core or another pack.

Standard library only. Front matter is read with PyYAML when it is installed, otherwise with a
small reader for the flat key: value form that pack skills use.
"""
from __future__ import annotations

import argparse
import datetime
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
UPSTREAM_RE = re.compile(r"^https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
KINDS = ("skills", "package", "release")
REQUIRED = ("schema", "id", "label", "description", "kind", "license", "upstream", "upstream_commit",
            "vetting", "sets")
OPTIONAL = {"package": "package", "release": "release"}  # key -> kind that requires it
SET_KEYS = {"id", "label", "description", "skills"}
RELEASE_KEYS = {"lock", "tag", "bundle", "engine", "providers", "codex_hooks", "skill_roots", "hook_files"}
FRONT_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)


def read_front_matter(path: Path) -> dict | None:
    text = path.read_text(encoding="utf-8")
    match = FRONT_RE.match(text)
    if not match:
        return None
    raw = match.group(1)
    try:
        import yaml  # noqa: PLC0415
        data = yaml.safe_load(raw)
        if isinstance(data, dict):
            return {k: (v.isoformat() if isinstance(v, datetime.date) else v) for k, v in data.items()}
        return None
    except ImportError:
        pass
    data = {}
    for line in raw.splitlines():
        if not line.strip() or line.startswith((" ", "\t", "#")):
            continue
        key, sep, value = line.partition(":")
        if not sep:
            return None
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
            value = value[1:-1].replace("''", "'") if value[0] == "'" else value[1:-1]
        data[key.strip()] = value
    return data


def check_date(value, label: str, errors: list[str]) -> None:
    if not isinstance(value, str) or not DATE_RE.match(value):
        errors.append(f"{label} must be YYYY-MM-DD, got {value!r}")
        return
    try:
        day = datetime.date.fromisoformat(value)
    except ValueError:
        errors.append(f"{label} is not a valid date: {value}")
        return
    if day > datetime.date.today():
        errors.append(f"{label} {value} is in the future")


def one_sentence(value) -> bool:
    return isinstance(value, str) and value.strip() == value and bool(value) and "\n" not in value \
        and value.endswith(".") and ". " not in value[:-1]


def check_skill(skill_dir: Path, pack: dict, errors: list[str]) -> None:
    where = f"skills/{skill_dir.name}"
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        errors.append(f"{where}: missing SKILL.md")
        return
    data = read_front_matter(skill_md)
    if data is None:
        errors.append(f"{where}/SKILL.md: missing or unreadable front matter")
        return
    name = str(data.get("name", "")).strip()
    description = str(data.get("description", "")).strip()
    if name != skill_dir.name:
        errors.append(f"{where}: front-matter name {name!r} differs from the folder name")
    if not NAME_RE.match(name):
        errors.append(f"{where}: name {name!r} must match {NAME_RE.pattern}")
    if not description:
        errors.append(f"{where}: front matter has no description")
    elif len(description) > 1024:
        errors.append(f"{where}: description is {len(description)} characters (limit 1024)")
    if pack.get("upstream"):
        if data.get("origin") != "third-party":
            errors.append(f"{where}: third-party pack skill needs origin: third-party")
        if data.get("vetting") != "passed":
            errors.append(f"{where}: third-party pack skill needs vetting: passed")
        check_date(str(data.get("vetted", "")), f"{where}: vetted", errors)
        if not data.get("license"):
            errors.append(f"{where}: front matter has no license")
        commit = str(data.get("upstream-commit", ""))
        if not SHA_RE.match(commit):
            errors.append(f"{where}: upstream-commit must be a 40-hex sha")
        upstream = str(data.get("upstream", ""))
        prefix = f"{pack['upstream']}/blob/{commit}/"
        if not (upstream.startswith(prefix) and upstream.endswith("SKILL.md")):
            errors.append(f"{where}: upstream must be the blob URL of SKILL.md under {prefix}")


def check_release(pack_dir: Path, pack: dict, errors: list[str]) -> None:
    release = pack.get("release")
    if not isinstance(release, dict):
        errors.append("kind release needs a release object")
        return
    missing = RELEASE_KEYS - set(release)
    if missing:
        errors.append(f"release misses {sorted(missing)}")
    lock_path = pack_dir / str(release.get("lock", ""))
    try:
        lock = json.loads(lock_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        errors.append(f"release lock {lock_path.name}: {error}")
        return
    if not re.match(r"^[0-9a-f]{64}$", str(lock.get("sha256sums", ""))):
        errors.append("release lock needs a 64-hex sha256sums digest")
    for key in ("version", "repo"):
        if not lock.get(key):
            errors.append(f"release lock has no {key}")
    if "{version}" not in str(release.get("tag", "")):
        errors.append("release tag must contain {version}")
    if "{os}" not in str(release.get("engine", "")) or "{arch}" not in str(release.get("engine", "")):
        errors.append("release engine must contain {os} and {arch}")
    if len(pack.get("sets", [])) != 1 or len(pack["sets"][0].get("skills", [])) != 1:
        errors.append("kind release holds one set with one skill")


def validate_pack(pack_dir: Path, core_names: set[str]) -> tuple[list[str], dict | None]:
    errors: list[str] = []
    path = pack_dir / "pack.json"
    try:
        pack = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        return [f"pack.json: {error}"], None
    if not isinstance(pack, dict):
        return ["pack.json must hold an object"], None
    kind = pack.get("kind")
    allowed = set(REQUIRED) | {key for key, need in OPTIONAL.items() if need == kind}
    for key in REQUIRED:
        if key not in pack:
            errors.append(f"pack.json misses key {key!r}")
    for key in pack:
        if key not in allowed:
            errors.append(f"pack.json has unexpected key {key!r}")
    if pack.get("schema") != 1:
        errors.append("schema must be 1")
    if pack.get("id") != pack_dir.name or not NAME_RE.match(str(pack.get("id", ""))):
        errors.append(f"id {pack.get('id')!r} must equal the folder name and match {NAME_RE.pattern}")
    if not isinstance(pack.get("label"), str) or not pack.get("label"):
        errors.append("label must be a non-empty string")
    if not one_sentence(pack.get("description")):
        errors.append("description must be one sentence ending with a period")
    if kind not in KINDS:
        errors.append(f"kind must be one of {KINDS}")
    if not isinstance(pack.get("license"), str) or not pack.get("license"):
        errors.append("license must be an SPDX id")
    upstream, commit, vetting = pack.get("upstream"), pack.get("upstream_commit"), pack.get("vetting")
    if upstream is not None and not (isinstance(upstream, str) and UPSTREAM_RE.match(upstream)):
        errors.append("upstream must be https://github.com/<owner>/<repo> or null")
    if commit is not None and not (isinstance(commit, str) and SHA_RE.match(commit)):
        errors.append("upstream_commit must be a 40-hex sha or null")
    if upstream is None and (commit is not None or vetting is not None):
        errors.append("in-house packs (upstream null) keep upstream_commit and vetting null")
    if upstream is not None and kind != "release" and commit is None:
        errors.append("a third-party pack needs upstream_commit")
    if vetting is not None:
        if not isinstance(vetting, dict) or set(vetting) != {"status", "vetted"} or vetting.get("status") != "passed":
            errors.append('vetting must be {"status": "passed", "vetted": "YYYY-MM-DD"} or null')
        else:
            check_date(vetting.get("vetted"), "vetting.vetted", errors)
    elif upstream is not None:
        errors.append("a third-party pack needs vetting")
    if not (pack_dir / "LICENSE").is_file():
        errors.append("LICENSE is missing")

    sets = pack.get("sets")
    listed: dict[str, str] = {}
    if not isinstance(sets, list) or not sets:
        errors.append("sets must be a non-empty list")
        sets = []
    seen_sets = set()
    for entry in sets:
        if not isinstance(entry, dict) or set(entry) != SET_KEYS:
            errors.append(f"set {entry!r} must have exactly the keys {sorted(SET_KEYS)}")
            continue
        sid = entry["id"]
        if not isinstance(sid, str) or not NAME_RE.match(sid) or sid in seen_sets:
            errors.append(f"set id {sid!r} must be unique and match {NAME_RE.pattern}")
        seen_sets.add(sid)
        if not isinstance(entry["label"], str) or not entry["label"]:
            errors.append(f"set {sid}: label must be a non-empty string")
        if not one_sentence(entry["description"]):
            errors.append(f"set {sid}: description must be one sentence ending with a period")
        if not isinstance(entry["skills"], list) or not entry["skills"]:
            errors.append(f"set {sid}: skills must be a non-empty list")
            continue
        for skill in entry["skills"]:
            if skill in listed:
                errors.append(f"skill {skill} is in set {listed[skill]} and set {sid}")
            listed[skill] = sid

    skills_dir = pack_dir / "skills"
    folders = sorted(p.name for p in skills_dir.iterdir() if p.is_dir()) if skills_dir.is_dir() else []
    if kind == "release":
        check_release(pack_dir, pack, errors)
        if folders:
            errors.append("kind release ships no skills/ folder; the release bundle holds the skill")
    else:
        for name in folders:
            if name not in listed:
                errors.append(f"skills/{name} belongs to no set")
            check_skill(skills_dir / name, pack, errors)
        for name in listed:
            if name not in folders:
                errors.append(f"set {listed[name]} lists {name}, but skills/{name}/ does not exist")
    for name in listed:
        if name in core_names:
            errors.append(f"skill {name} has the name of a core skill or workflow")
    if kind == "package":
        payload = pack.get("package")
        if payload != {"payload": "package"}:
            errors.append('kind package needs "package": {"payload": "package"}')
        target = pack_dir / "package"
        if not target.is_dir() or not any(target.iterdir()):
            errors.append("kind package needs a non-empty package/ folder")
    return errors, pack


def core_names(root: Path) -> set[str]:
    names = set()
    for sub in ("skills", "workflows"):
        for path in (root / sub).glob("*.md"):
            data = read_front_matter(path) or {}
            names.add(str(data.get("name") or path.stem))
    return names


def load_packs(packs_dir: Path, root: Path = ROOT) -> tuple[list[dict], list[str]]:
    """Return (packs, errors). Errors carry the pack id as prefix."""
    packs, errors = [], []
    names = core_names(root)
    owners: dict[str, str] = {}
    for pack_dir in sorted(p for p in packs_dir.iterdir() if p.is_dir()) if packs_dir.is_dir() else []:
        errs, pack = validate_pack(pack_dir, names)
        errors += [f"{pack_dir.name}: {e}" for e in errs]
        if pack is None:
            continue
        for entry in pack.get("sets", []):
            for skill in entry.get("skills", []) if isinstance(entry, dict) else []:
                if skill in owners and owners[skill] != pack_dir.name:
                    errors.append(f"{pack_dir.name}: skill {skill} also ships in pack {owners[skill]}")
                owners[skill] = pack_dir.name
        packs.append(pack)
    return packs, errors


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--packs-dir", type=Path, default=ROOT / "packs")
    args = parser.parse_args(argv)
    packs, errors = load_packs(args.packs_dir)
    for pack in packs:
        count = sum(len(s.get("skills", [])) for s in pack.get("sets", []) if isinstance(s, dict))
        print(f"pack {pack.get('id')}: {len(pack.get('sets', []))} sets, {count} skills, kind {pack.get('kind')}")
    for error in errors:
        print(f"FAIL {error}")
    print(f"{len(packs)} packs checked, {len(errors)} problems")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
