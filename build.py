#!/usr/bin/env python3

"""
Example:
build.py --runtime docker \
    --frappe-path https://github.com/Tebayaki/frappe \
    --frappe-branch version-16 \
    --apps-file apps.json \
    --tag frappe_custom:16 \
    --file images/custom/Containerfile
"""

import argparse
import base64
import shlex
import subprocess
import sys
from pathlib import Path
from typing import List


def encode_apps_json(path: Path) -> str:
    data = path.read_bytes()
    return base64.b64encode(data).decode("ascii")


def build_cmd(args):
    cmd = [args.runtime, "build"]

    build_args = {
        "FRAPPE_PATH": args.frappe_path,
        "FRAPPE_BRANCH": args.frappe_branch,
        "APPS_JSON_BASE64": encode_apps_json(args.apps_file) if args.apps_file else None,
        "PYTHON_VERSION": args.python_version,
        "NODE_VERSION": args.node_version,
        "WKHTMLTOPDF_VERSION": args.wkhtmltopdf_version,
        "WKHTMLTOPDF_DISTRO": args.wkhtmltopdf_distro,
        "DEBIAN_BASE": args.debian_base,
    }

    [cmd.append(f"--build-arg={k}={v}") for k, v in build_args.items() if v is not None]

    if args.tag:
        cmd.extend(["--tag", args.tag])
    cmd.extend(["--file", args.file, "."])

    return cmd


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--runtime", choices=["docker", "podman"], default="docker")
    parser.add_argument("--frappe-path")
    parser.add_argument("--frappe-branch")
    parser.add_argument("--apps-file", type=Path)
    parser.add_argument("--python-version")
    parser.add_argument("--node-version")
    parser.add_argument("--wkhtmltopdf-version")
    parser.add_argument("--wkhtmltopdf-distro")
    parser.add_argument("--debian-base")
    parser.add_argument("--tag")
    parser.add_argument("--file", default="Containerfile")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    cmd = build_cmd(args)

    print(" ".join(shlex.quote(p) for p in cmd))

    if args.dry_run:
        return 0

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Build failed({e.returncode})", file=sys.stderr)
        return e.returncode
    except KeyboardInterrupt:
        return 130

    print("Build successful")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
