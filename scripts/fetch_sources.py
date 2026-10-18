#!/usr/bin/env python3
"""
Zenith Browser - Source Fetcher Script
Automatically detects the latest upstream Chromium stable tag, sets up depot_tools,
and prepares the source tree for patching and building.
"""

import sys
import os
import json
import urllib.request
import subprocess
import argparse

CHROMIUM_DASH_API = "https://chromiumdash.appspot.com/fetch_releases?channel=Stable&platform=All&num=1"

def get_latest_stable_version():
    print("[*] Querying ChromiumDash API for latest stable tag...")
    req = urllib.request.Request(
        CHROMIUM_DASH_API,
        headers={"User-Agent": "ZenithBrowserBuilder/1.0"}
    )
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        if data and len(data) > 0:
            version = data[0]["version"]
            print(f"[+] Detected latest Chromium Stable: {version}")
            return version
    # Fallback known stable
    return "128.0.6613.120"

def setup_depot_tools(target_dir):
    depot_path = os.path.join(target_dir, "depot_tools")
    if not os.path.exists(depot_path):
        print("[*] Cloning Google depot_tools...")
        subprocess.run(
            ["git", "clone", "--depth", "1", "https://chromium.googlesource.com/chromium/tools/depot_tools.git", depot_path],
            check=True
        )
    else:
        print("[*] depot_tools already present.")
    os.environ["PATH"] = f"{depot_path}:{os.environ.get('PATH', '')}"
    return depot_path

def fetch_chromium_source(src_dir, version):
    os.makedirs(src_dir, exist_ok=True)
    gclient_config = f"""solutions = [
  {{
    "name": "src",
    "url": "https://chromium.googlesource.com/chromium/src.git@{version}",
    "deps_file": ".DEPS.git",
    "managed": False,
    "custom_deps": {{}},
    "custom_vars": {{}},
  }},
]
"""
    gclient_file = os.path.join(src_dir, ".gclient")
    if not os.path.exists(gclient_file):
        with open(gclient_file, "w") as f:
            f.write(gclient_config)

    print(f"[*] Running gclient sync for version {version} (shallow)...")
    subprocess.run(
        ["gclient", "sync", "--no-history", "--shallow", "--jobs", "16"],
        cwd=src_dir,
        check=True
    )
    print("[+] Chromium sources fetched successfully.")

def main():
    parser = argparse.ArgumentParser(description="Fetch Chromium sources for Zenith Browser")
    parser.add_argument("--dir", default="./chromium", help="Destination directory for Chromium workspace")
    parser.add_argument("--version", default=None, help="Target Chromium version (defaults to latest stable)")
    args = parser.parse_args()

    version = args.version or get_latest_stable_version()
    depot_path = setup_depot_tools(args.dir)
    print(f"[*] Using depot_tools at: {depot_path}")
    print(f"[*] Target Chromium Release: {version}")

    fetch_chromium_source(args.dir, version)

if __name__ == "__main__":
    main()
