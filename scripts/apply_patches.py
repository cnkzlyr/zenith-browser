#!/usr/bin/env python3
"""
Zenith Browser - Patch Application Script
Applies all modular patches from patches/ onto the target Chromium source tree.
"""

import sys
import os
import subprocess
import argparse

def find_patches(patches_dir):
    patch_files = []
    categories = ["core", "android", "adblock", "sync", "ui"]
    for cat in categories:
        cat_dir = os.path.join(patches_dir, cat)
        if os.path.exists(cat_dir):
            for f in sorted(os.listdir(cat_dir)):
                if f.endswith(".patch") or f.endswith(".diff"):
                    patch_files.append((cat, os.path.join(cat_dir, f)))
    return patch_files

def apply_patch(src_dir, patch_path, reverse=False):
    cmd = ["git", "apply", "--whitespace=nowarn"]
    if reverse:
        cmd.append("-R")
    cmd.append(os.path.abspath(patch_path))

    res = subprocess.run(cmd, cwd=src_dir, capture_output=True, text=True)
    if res.returncode != 0:
        # Fallback to patch utility if git apply has fuzzy mismatch
        cmd_fallback = ["patch", "-p1", "--no-backup-if-mismatch"]
        if reverse:
            cmd_fallback.append("-R")
        with open(patch_path, "r") as pf:
            res_fallback = subprocess.run(cmd_fallback, cwd=src_dir, stdin=pf, capture_output=True, text=True)
            if res_fallback.returncode != 0:
                print(f"[ERROR] Failed to apply: {os.path.basename(patch_path)}")
                print(f"Git Apply Error:\n{res.stderr}")
                print(f"Patch Tool Error:\n{res_fallback.stderr}")
                return False
    return True

def main():
    parser = argparse.ArgumentParser(description="Apply Zenith Browser patches to Chromium")
    parser.add_argument("--src", required=True, help="Path to Chromium src directory")
    parser.add_argument("--patches", default="patches", help="Path to patches directory")
    parser.add_argument("--reverse", action="store_true", help="Reverse/Rollback applied patches")
    args = parser.parse_args()

    if not os.path.exists(args.src):
        print(f"[FATAL] Source directory does not exist: {args.src}")
        sys.exit(1)

    patches = find_patches(args.patches)
    print(f"[*] Found {len(patches)} Zenith patches in {args.patches}/")

    success_count = 0
    for cat, ppath in patches:
        action_name = "Reversing" if args.reverse else "Applying"
        print(f"[{cat.upper()}] {action_name}: {os.path.basename(ppath)}...")
        if apply_patch(args.src, ppath, reverse=args.reverse):
            success_count += 1
        else:
            print(f"[ABORT] Patch process halted due to conflict in {ppath}")
            sys.exit(1)

    print(f"\n[SUCCESS] Successfully applied {success_count}/{len(patches)} patches to {args.src}!")

if __name__ == "__main__":
    main()
