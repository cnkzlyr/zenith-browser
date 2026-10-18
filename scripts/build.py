#!/usr/bin/env python3
"""
Zenith Browser - Unified Build Script
Generates GN configuration (args.gn) and compiles Zenith Browser targets
for Android, Windows, Linux, and macOS.
"""

import sys
import os
import subprocess
import argparse

def generate_gn_args(target_os, target_cpu, is_release=True):
    args = [
        f'target_os = "{target_os}"',
        f'target_cpu = "{target_cpu}"',
        f'is_debug = {"false" if is_release else "true"}',
        f'is_official_build = {"true" if is_release else "false"}',
        'is_component_build = false',
        'symbol_level = 0',
        'blink_symbol_level = 0',
        'enable_nacl = false',
        'proprietary_codecs = true',
        'ffmpeg_branding = "Chrome"',
        
        # Zenith Core Features
        'enable_extensions = true',         # Re-enabled on Android!
        'enable_widevine = true',
        'use_official_google_api_keys = false',
    ]

    if target_os == "android":
        args.extend([
            'android_channel = "stable"',
            'enable_vr = false',
            'chrome_public_manifest_package = "org.zenith.browser"',
            'build_apk_secondary_abi = true',
        ])
    elif target_os == "linux":
        args.extend([
            'use_sysroot = true',
            'use_custom_libcxx = true',
            'use_vaapi = true',
        ])
    elif target_os == "win":
        args.extend([
            'is_clang = true',
            'visual_studio_version = "2022"',
        ])
    elif target_os == "mac":
        args.extend([
            'enable_dsyms = false',
            'enable_stripping = true',
        ])

    return "\n".join(args) + "\n"

def main():
    parser = argparse.ArgumentParser(description="Build Zenith Browser for any supported platform")
    parser.add_argument("--src", default="./chromium/src", help="Path to Chromium src directory")
    parser.add_argument("--out", default="out/ZenithRelease", help="Output directory inside src")
    parser.add_argument("--os", choices=["android", "linux", "win", "mac"], default="linux", help="Target OS")
    parser.add_argument("--cpu", choices=["x64", "arm64", "arm"], default="x64", help="Target CPU")
    parser.add_argument("--ninja-args", default="", help="Extra arguments passed to ninja (e.g. -j16)")
    args = parser.parse_args()

    src_dir = os.path.abspath(args.src)
    out_dir = os.path.join(src_dir, args.out)
    os.makedirs(out_dir, exist_ok=True)

    print(f"[*] Configuring Zenith Browser for: OS={args.os}, CPU={args.cpu}")
    gn_args_content = generate_gn_args(args.os, args.cpu)
    gn_args_file = os.path.join(out_dir, "args.gn")
    with open(gn_args_file, "w") as f:
        f.write(gn_args_content)

    print(f"[+] Written {gn_args_file}:")
    print(gn_args_content)

    print("[*] Running gn gen...")
    subprocess.run(["gn", "gen", out_dir], cwd=src_dir, check=True)

    target_binary = "chrome_public_apk" if args.os == "android" else "chrome"
    print(f"[*] Starting compilation for target '{target_binary}'...")
    ninja_cmd = ["autoninja", "-C", out_dir, target_binary]
    if args.ninja_args:
        ninja_cmd.extend(args.ninja_args.split())

    subprocess.run(ninja_cmd, cwd=src_dir, check=True)
    print(f"\n[SUCCESS] Build complete! Binaries located at: {out_dir}")

if __name__ == "__main__":
    main()
