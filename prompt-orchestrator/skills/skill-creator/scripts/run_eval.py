#!/usr/bin/env python3
"""Run trigger evaluation for a skill description.

Tests whether a skill's description causes Claude to trigger (read the skill)
for a set of queries. Outputs results as JSON.

Default mode writes a temporary command into the project's .claude/commands/ and
runs claude -p with the user's settings. --isolated runs each query in a throwaway
project that holds only the skill under test, with user settings off.
"""

import argparse
import json
import os
import select
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from scripts.utils import parse_skill_md, set_skill_description

ISOLATED_TOOLS = ["Skill", "Read", "Glob", "Grep"]
DEFAULT_TIMEOUT = 30
DEFAULT_ISOLATED_TIMEOUT = 120
DEFAULT_MIN_AVAILABLE_MB = 3072
MEMORY_POLL_SECONDS = 5


def find_project_root() -> Path:
    """Find the project root by walking up from cwd looking for .claude/.

    Mimics how Claude Code discovers its project root, so the command file
    we create ends up where claude -p will look for it.
    """
    current = Path.cwd()
    for parent in [current, *current.parents]:
        if (parent / ".claude").is_dir():
            return parent
    return current


def run_single_query(
    query: str,
    skill_name: str,
    skill_description: str,
    timeout: int,
    project_root: str,
    model: str | None = None,
) -> bool:
    """Run a single query and return whether the skill was triggered.

    Creates a command file in .claude/commands/ so it appears in Claude's
    available_skills list, then runs `claude -p` with the raw query.
    Uses --include-partial-messages to detect triggering early from
    stream events (content_block_start) rather than waiting for the
    full assistant message, which only arrives after tool execution.
    """
    unique_id = uuid.uuid4().hex[:8]
    clean_name = f"{skill_name}-skill-{unique_id}"
    project_commands_dir = Path(project_root) / ".claude" / "commands"
    command_file = project_commands_dir / f"{clean_name}.md"

    try:
        project_commands_dir.mkdir(parents=True, exist_ok=True)
        # Use YAML block scalar to avoid breaking on quotes in description
        indented_desc = "\n  ".join(skill_description.split("\n"))
        command_content = (
            f"---\n"
            f"description: |\n"
            f"  {indented_desc}\n"
            f"---\n\n"
            f"# {skill_name}\n\n"
            f"This skill handles: {skill_description}\n"
        )
        command_file.write_text(command_content)

        cmd = [
            "claude",
            "-p", query,
            "--output-format", "stream-json",
            "--verbose",
            "--include-partial-messages",
        ]
        if model:
            cmd.extend(["--model", model])

        # Remove CLAUDECODE env var to allow nesting claude -p inside a
        # Claude Code session. The guard is for interactive terminal conflicts;
        # programmatic subprocess usage is safe.
        env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            cwd=project_root,
            env=env,
        )

        triggered = False
        start_time = time.time()
        buffer = ""
        # Track state for stream event detection
        pending_tool_name = None
        accumulated_json = ""

        try:
            while time.time() - start_time < timeout:
                if process.poll() is not None:
                    remaining = process.stdout.read()
                    if remaining:
                        buffer += remaining.decode("utf-8", errors="replace")
                    break

                ready, _, _ = select.select([process.stdout], [], [], 1.0)
                if not ready:
                    continue

                chunk = os.read(process.stdout.fileno(), 8192)
                if not chunk:
                    break
                buffer += chunk.decode("utf-8", errors="replace")

                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    line = line.strip()
                    if not line:
                        continue

                    try:
                        event = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    # Early detection via stream events
                    if event.get("type") == "stream_event":
                        se = event.get("event", {})
                        se_type = se.get("type", "")

                        if se_type == "content_block_start":
                            cb = se.get("content_block", {})
                            if cb.get("type") == "tool_use":
                                tool_name = cb.get("name", "")
                                if tool_name in ("Skill", "Read"):
                                    pending_tool_name = tool_name
                                    accumulated_json = ""
                                else:
                                    return False

                        elif se_type == "content_block_delta" and pending_tool_name:
                            delta = se.get("delta", {})
                            if delta.get("type") == "input_json_delta":
                                accumulated_json += delta.get("partial_json", "")
                                if clean_name in accumulated_json:
                                    return True

                        elif se_type in ("content_block_stop", "message_stop"):
                            if pending_tool_name:
                                return clean_name in accumulated_json
                            if se_type == "message_stop":
                                return False

                    # Fallback: full assistant message
                    elif event.get("type") == "assistant":
                        message = event.get("message", {})
                        for content_item in message.get("content", []):
                            if content_item.get("type") != "tool_use":
                                continue
                            tool_name = content_item.get("name", "")
                            tool_input = content_item.get("input", {})
                            if tool_name == "Skill" and clean_name in tool_input.get("skill", ""):
                                triggered = True
                            elif tool_name == "Read" and clean_name in tool_input.get("file_path", ""):
                                triggered = True
                            return triggered

                    elif event.get("type") == "result":
                        return triggered
        finally:
            # Clean up process on any exit path (return, exception, timeout)
            if process.poll() is None:
                process.kill()
                process.wait()

        return triggered
    finally:
        if command_file.exists():
            command_file.unlink()


def available_memory_mb() -> int | None:
    """MemAvailable from /proc/meminfo in MB, or None where it is not readable."""
    try:
        for line in Path("/proc/meminfo").read_text().splitlines():
            if line.startswith("MemAvailable:"):
                return int(line.split()[1]) // 1024
    except (OSError, ValueError):
        pass
    return None


def wait_for_memory(min_available_mb: int, max_wait: int) -> None:
    """Block until MemAvailable reaches the floor; raise after max_wait seconds."""
    deadline = time.time() + max_wait
    while True:
        available = available_memory_mb()
        if available is None or available >= min_available_mb:
            return
        if time.time() >= deadline:
            raise RuntimeError(
                f"available memory {available} MB stayed under {min_available_mb} MB for {max_wait}s"
            )
        time.sleep(MEMORY_POLL_SECONDS)


def run_single_query_isolated(
    query: str,
    skill_name: str,
    snapshot_dir: str,
    timeout: int,
    model: str | None = None,
    min_available_mb: int = DEFAULT_MIN_AVAILABLE_MB,
    memory_max_wait: int = 3600,
) -> bool:
    """Run one query in a throwaway project holding only the skill under test.

    The project has just `.claude/skills/<skill>/`, user settings are off
    (`--setting-sources project`) and the tool set is limited, so always-on user
    skills cannot answer the query before the skill under test is considered.
    A hit is any assistant Skill tool_use whose input names the skill.
    """
    wait_for_memory(min_available_mb, memory_max_wait)
    workspace = tempfile.mkdtemp(prefix="skilltrig-")
    process = None
    try:
        skills_dir = Path(workspace) / ".claude" / "skills"
        skills_dir.mkdir(parents=True)
        shutil.copytree(snapshot_dir, skills_dir / skill_name)

        cmd = [
            "claude",
            "-p", query,
            "--output-format", "stream-json",
            "--verbose",
            "--setting-sources", "project",
        ]
        if model:
            cmd.extend(["--model", model])
        cmd.extend(["--tools", *ISOLATED_TOOLS])

        env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            cwd=workspace,
            env=env,
            text=True,
        )

        start_time = time.time()
        while time.time() - start_time < timeout:
            ready, _, _ = select.select([process.stdout], [], [], 1.0)
            if not ready:
                if process.poll() is not None:
                    return False
                continue
            line = process.stdout.readline()
            if not line:
                return False
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            if event.get("type") == "assistant":
                for item in event.get("message", {}).get("content", []):
                    if (
                        item.get("type") == "tool_use"
                        and item.get("name") == "Skill"
                        and skill_name in json.dumps(item.get("input", {}))
                    ):
                        return True
            elif event.get("type") == "result":
                return False
        return False
    finally:
        if process is not None and process.poll() is None:
            process.kill()
            process.wait()
        shutil.rmtree(workspace, ignore_errors=True)


def make_snapshot(skill_path: Path, skill_name: str, description: str, original_description: str) -> str:
    """Copy the skill folder once so later runs do not depend on a folder that is rewritten."""
    snapshot = Path(tempfile.mkdtemp(prefix="skillsnap-")) / skill_name
    shutil.copytree(skill_path, snapshot)
    if description != original_description:
        skill_md = snapshot / "SKILL.md"
        skill_md.write_text(set_skill_description(skill_md.read_text(), description))
    return str(snapshot)


def run_eval(
    eval_set: list[dict],
    skill_name: str,
    description: str,
    num_workers: int,
    timeout: int,
    project_root: Path,
    runs_per_query: int = 1,
    trigger_threshold: float = 0.5,
    model: str | None = None,
    isolated: bool = False,
    skill_path: Path | None = None,
    original_description: str | None = None,
    min_available_mb: int = DEFAULT_MIN_AVAILABLE_MB,
) -> dict:
    """Run the full eval set and return results.

    With isolated=True each run uses a throwaway project that holds only
    `skill_path` (see run_single_query_isolated); project_root is unused.
    """
    results = []
    snapshot = None
    if isolated:
        snapshot = make_snapshot(skill_path, skill_name, description, original_description or description)

    query_triggers: dict[str, list[bool]] = {}
    query_items: dict[str, dict] = {}
    try:
        with ProcessPoolExecutor(max_workers=num_workers) as executor:
            future_to_info = {}
            for item in eval_set:
                for run_idx in range(runs_per_query):
                    if isolated:
                        future = executor.submit(
                            run_single_query_isolated,
                            item["query"],
                            skill_name,
                            snapshot,
                            timeout,
                            model,
                            min_available_mb,
                        )
                    else:
                        future = executor.submit(
                            run_single_query,
                            item["query"],
                            skill_name,
                            description,
                            timeout,
                            str(project_root),
                            model,
                        )
                    future_to_info[future] = (item, run_idx)

            for future in as_completed(future_to_info):
                item, _ = future_to_info[future]
                query = item["query"]
                query_items[query] = item
                if query not in query_triggers:
                    query_triggers[query] = []
                try:
                    query_triggers[query].append(future.result())
                except Exception as e:
                    print(f"Warning: query failed: {e}", file=sys.stderr)
                    query_triggers[query].append(False)
    finally:
        if snapshot:
            shutil.rmtree(Path(snapshot).parent, ignore_errors=True)

    for query, triggers in query_triggers.items():
        item = query_items[query]
        trigger_rate = sum(triggers) / len(triggers)
        should_trigger = item["should_trigger"]
        if should_trigger:
            did_pass = trigger_rate >= trigger_threshold
        else:
            did_pass = trigger_rate < trigger_threshold
        results.append({
            "query": query,
            "should_trigger": should_trigger,
            "trigger_rate": trigger_rate,
            "triggers": sum(triggers),
            "runs": len(triggers),
            "pass": did_pass,
        })

    passed = sum(1 for r in results if r["pass"])
    total = len(results)

    return {
        "skill_name": skill_name,
        "description": description,
        "results": results,
        "summary": {
            "total": total,
            "passed": passed,
            "failed": total - passed,
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Run trigger evaluation for a skill description")
    parser.add_argument("--eval-set", required=True, help="Path to eval set JSON file")
    parser.add_argument("--skill-path", required=True, help="Path to skill directory")
    parser.add_argument("--description", default=None, help="Override description to test")
    parser.add_argument("--num-workers", type=int, default=10, help="Number of parallel workers")
    parser.add_argument("--timeout", type=int, default=None,
                        help=f"Timeout per query in seconds (default {DEFAULT_TIMEOUT}, {DEFAULT_ISOLATED_TIMEOUT} with --isolated)")
    parser.add_argument("--runs-per-query", type=int, default=3, help="Number of runs per query")
    parser.add_argument("--trigger-threshold", type=float, default=0.5, help="Trigger rate threshold")
    parser.add_argument("--model", default=None, help="Model to use for claude -p (default: user's configured model)")
    parser.add_argument("--isolated", action="store_true",
                        help="Run each query in a throwaway project holding only the skill, with user settings off "
                             "and tools limited to Skill, Read, Glob, Grep")
    parser.add_argument("--min-available-mb", type=int, default=DEFAULT_MIN_AVAILABLE_MB,
                        help="--isolated: wait before each run until this much memory is available (0 disables)")
    parser.add_argument("--verbose", action="store_true", help="Print progress to stderr")
    args = parser.parse_args()

    eval_set = json.loads(Path(args.eval_set).read_text())
    skill_path = Path(args.skill_path)

    if not (skill_path / "SKILL.md").exists():
        print(f"Error: No SKILL.md found at {skill_path}", file=sys.stderr)
        sys.exit(1)

    name, original_description, content = parse_skill_md(skill_path)
    description = args.description or original_description
    project_root = find_project_root()

    if args.verbose:
        print(f"Evaluating: {description}", file=sys.stderr)

    output = run_eval(
        eval_set=eval_set,
        skill_name=name,
        description=description,
        num_workers=args.num_workers,
        timeout=args.timeout or (DEFAULT_ISOLATED_TIMEOUT if args.isolated else DEFAULT_TIMEOUT),
        project_root=project_root,
        runs_per_query=args.runs_per_query,
        trigger_threshold=args.trigger_threshold,
        model=args.model,
        isolated=args.isolated,
        skill_path=skill_path,
        original_description=original_description,
        min_available_mb=args.min_available_mb,
    )

    if args.verbose:
        summary = output["summary"]
        print(f"Results: {summary['passed']}/{summary['total']} passed", file=sys.stderr)
        for r in output["results"]:
            status = "PASS" if r["pass"] else "FAIL"
            rate_str = f"{r['triggers']}/{r['runs']}"
            print(f"  [{status}] rate={rate_str} expected={r['should_trigger']}: {r['query'][:70]}", file=sys.stderr)

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
