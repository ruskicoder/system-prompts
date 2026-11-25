#!/usr/bin/env python3
"""Validate opt-in packs in packs/<pack-id>/ against pack format v1 (packs/README.md).

    python3 tools/validate_packs.py                  every pack under packs/
    python3 tools/validate_packs.py --packs-dir DIR  packs in another folder (tests, fixtures)

Checks per pack: pack.json keys and types, the id against the folder name, sets (each skill
folder under skills/ in exactly one set, each listed skill present), every SKILL.md front matter
(name equals the folder, name pattern, description of at most 1024 characters, the third-party
fields when the pack has an upstream), the payload folder for kind "package", the release lock
for kind "release", the npm pins and the MCP server of a pack that has them, set requirements,
the LICENSE file, and skill names that clash with the core or another pack. It also checks that
each description uses a YAML form that the po-skills index reader in install/pack_helper.mjs reads
(plain, quoted or a > or | block), and that no pack MCP server takes the po-skills server name.

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
ANY_KIND = ("npm", "mcp")  # optional keys for kinds skills and package
SET_KEYS = {"id", "label", "description", "skills"}
SET_OPTIONAL = {"requires"}
NPM_NAME_RE = re.compile(r"^(?:@[a-z0-9][a-z0-9._-]*/)?[a-z0-9][a-z0-9._-]*$")
EXACT_RE = re.compile(r"^\d+\.\d+\.\d+$")
INTEGRITY_RE = re.compile(r"^sha512-[A-Za-z0-9+/]{86}==$")
PLATFORM_RE = re.compile(r"^(?:linux|darwin|win32)-(?:x64|arm64|ia32|arm)$")
RANGE_RE = re.compile(r"^(?:\^|>=)?\d+\.\d+\.\d+(?: \|\| (?:\^|>=)?\d+\.\d+\.\d+)*$")
MCP_KEYS = {"set", "name", "command", "args", "env"}
RELEASE_KEYS = {"lock", "tag", "bundle", "engine", "providers", "codex_hooks", "skill_roots", "hook_files"}
FRONT_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---\r?\n", re.DOTALL)
# Description forms that the po-skills index reader (install/pack_helper.mjs) reads.
DESCRIPTION_FORM_RE = re.compile(r"""^description:[ \t]*(?:[>|][+-]?[ \t]*|'.*|".*|[^\s&*!%@`{\[|>#'"].*)$""")


def reserved_mcp_name() -> str:
    """The server name of the po-skills MCP server (install/spec.json skills_mcp.name)."""
    try:
        spec = json.loads((ROOT / "install" / "spec.json").read_text(encoding="utf-8"))
        return str(spec["skills_mcp"]["name"])
    except (OSError, ValueError, KeyError, TypeError):
        return "po-skills"


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
    raw = FRONT_RE.match(skill_md.read_text(encoding="utf-8")).group(1)
    form = [line for line in raw.splitlines() if line.startswith("description:")]
    if form and not DESCRIPTION_FORM_RE.match(form[0]):
        errors.append(f"{where}: description must be a plain, quoted or > or | block scalar for the po-skills index")
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


def check_npm(pack: dict, set_ids: dict, errors: list[str]) -> None:
    npm = pack.get("npm")
    if not isinstance(npm, dict) or set(npm) != {"node", "packages"}:
        errors.append('npm must be {"node": RANGE, "packages": [...]}')
        return
    if not isinstance(npm["node"], str) or not RANGE_RE.match(npm["node"]):
        errors.append("npm.node must be versions joined by ' || ', each X.Y.Z, ^X.Y.Z or >=X.Y.Z")
    packages = npm["packages"]
    if not isinstance(packages, list) or not packages:
        errors.append("npm.packages must be a non-empty list")
        return
    base = packages[0].get("set") if isinstance(packages[0], dict) else None
    for i, entry in enumerate(packages):
        where = f"npm.packages[{i}]"
        if not isinstance(entry, dict) or not {"set", "name", "version", "integrity"} <= set(entry) \
                or not set(entry) <= {"set", "name", "version", "integrity", "binding"}:
            errors.append(f"{where} needs set, name, version and integrity, and may add binding")
            continue
        if [p.get("set") for p in packages if isinstance(p, dict)].count(entry["set"]) > 1:
            errors.append(f"{where}: set {entry['set']} has more than one npm package")
        if entry["set"] not in set_ids:
            errors.append(f"{where}: set {entry['set']!r} is not a set of this pack")
        elif i == 0 and set_ids[entry["set"]].get("requires"):
            errors.append(f"{where}: the first package installs the prefix, so its set requires nothing")
        elif i > 0 and base not in (set_ids[entry["set"]].get("requires") or []):
            errors.append(f"{where}: set {entry['set']} must require set {base}, which installs the prefix")
        if not isinstance(entry["name"], str) or not NPM_NAME_RE.match(entry["name"]):
            errors.append(f"{where}: name {entry['name']!r} is not an npm package name")
        if not isinstance(entry["version"], str) or not EXACT_RE.match(entry["version"]):
            errors.append(f"{where}: version must be an exact X.Y.Z pin, got {entry['version']!r}")
        if not isinstance(entry["integrity"], str) or not INTEGRITY_RE.match(entry["integrity"]):
            errors.append(f"{where}: integrity must be the npm sha512 integrity string")
        binding = entry.get("binding")
        if binding is None:
            continue
        if not isinstance(binding, dict) or set(binding) != {"url", "member", "sha256"}:
            errors.append(f"{where}.binding must have exactly url, member and sha256")
            continue
        url, member, digests = binding["url"], binding["member"], binding["sha256"]
        if not (isinstance(url, str) and url.startswith("https://github.com/") and "{version}" in url
                and "{platform}" in url and url.endswith(".tar.gz")):
            errors.append(f"{where}.binding.url must be an https://github.com/ .tar.gz URL with {{version}} and {{platform}}")
        if not isinstance(member, str) or not member or member.startswith(("/", "\\")) or ".." in member.split("/"):
            errors.append(f"{where}.binding.member must be a relative path inside the archive")
        if not isinstance(digests, dict) or not digests:
            errors.append(f"{where}.binding.sha256 must map platforms to digests")
            continue
        for plat, digest in digests.items():
            if not PLATFORM_RE.match(plat):
                errors.append(f"{where}.binding.sha256: {plat!r} is not <process.platform>-<process.arch>")
            if not isinstance(digest, str) or not re.match(r"^[0-9a-f]{64}$", digest):
                errors.append(f"{where}.binding.sha256[{plat}] must be 64 lowercase hex characters")


def check_mcp(pack: dict, set_ids: dict, errors: list[str]) -> None:
    mcp = pack.get("mcp")
    if not isinstance(mcp, dict) or set(mcp) != MCP_KEYS:
        errors.append(f"mcp must have exactly the keys {sorted(MCP_KEYS)}")
        return
    if mcp["set"] not in set_ids:
        errors.append(f"mcp.set {mcp['set']!r} is not a set of this pack")
    if not isinstance(mcp["name"], str) or not NAME_RE.match(mcp["name"]):
        errors.append(f"mcp.name must match {NAME_RE.pattern}")
    elif mcp["name"] == reserved_mcp_name():
        errors.append(f"mcp.name {mcp['name']} is the name of the installer's own MCP server")
    if not isinstance(mcp["command"], str) or not mcp["command"]:
        errors.append("mcp.command must be a non-empty string")
    if not isinstance(mcp["args"], list) or not all(isinstance(a, str) for a in mcp["args"]):
        errors.append("mcp.args must be a list of strings")
    env = mcp["env"]
    if not isinstance(env, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in env.items()):
        errors.append("mcp.env must map names to strings")
    text = json.dumps([mcp["command"], mcp["args"], env])
    if "@latest" in text or re.search(r"\bnpx\b", text):
        errors.append("mcp must run a pinned local install: no npx and no @latest")
    if "{PACKAGE}" in text and "npm" not in pack:
        errors.append("mcp uses {PACKAGE}, so the pack needs an npm object")


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
    if kind in ("skills", "package"):
        allowed |= set(ANY_KIND)
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
    npm_sets = {p.get("set") for p in (pack.get("npm") or {}).get("packages", []) if isinstance(p, dict)}
    set_ids = {s["id"]: s for s in sets if isinstance(s, dict) and isinstance(s.get("id"), str)}
    for entry in sets:
        if not isinstance(entry, dict) or not SET_KEYS <= set(entry) <= SET_KEYS | SET_OPTIONAL:
            errors.append(f"set {entry!r} must have the keys {sorted(SET_KEYS)} and may add {sorted(SET_OPTIONAL)}")
            continue
        sid = entry["id"]
        if not isinstance(sid, str) or not NAME_RE.match(sid) or sid in seen_sets:
            errors.append(f"set id {sid!r} must be unique and match {NAME_RE.pattern}")
        seen_sets.add(sid)
        if not isinstance(entry["label"], str) or not entry["label"]:
            errors.append(f"set {sid}: label must be a non-empty string")
        if not one_sentence(entry["description"]):
            errors.append(f"set {sid}: description must be one sentence ending with a period")
        requires = entry.get("requires")
        if requires is not None:
            if not isinstance(requires, list) or not requires or any(r == sid or r not in set_ids for r in requires):
                errors.append(f"set {sid}: requires must list other sets of this pack")
            elif any(set_ids[r].get("requires") for r in requires):
                errors.append(f"set {sid}: a required set may not require another set")
        if not isinstance(entry["skills"], list) or (not entry["skills"] and sid not in npm_sets):
            errors.append(f"set {sid}: skills must be a non-empty list, unless the set installs an npm package")
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
    if "npm" in pack:
        check_npm(pack, set_ids, errors)
    if "mcp" in pack:
        check_mcp(pack, set_ids, errors)
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
