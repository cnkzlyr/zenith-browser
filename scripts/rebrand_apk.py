#!/usr/bin/env python3
"""
Zenith Browser - Complete Android Rebranding, Icon Fix, Dex Menu Patch & Built-in Imerek UYAP Engine
- Replaces all Kiwi logos, birds, and names with pure Zenith branding across all locales.
- Fixes Android 16 icon bug by removing anydpi-v26 vector inflation and pointing directly to 32-bit 192x192 bitmaps.
- Patches classes.dex to make the Extensions menu unconditionally visible on all pages.
- Injects embedded native C server (libimerek.so) on port 9936 into libchrome.so.
- Bundles uBlock Origin and Imerek UYAP extensions for instant 100% adblock and desktop integration.
"""

import os
import sys
import math
import struct
import shutil
import zlib
import hashlib
import zipfile
import subprocess
from PIL import Image, ImageDraw, ImageFont

def render_zenith_icon(size, is_round=False):
    """Renders a high-tech cosmic Zenith 'Z' browser icon."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    center = size / 2.0
    r = size * 0.46
    
    # Outer dark cosmic disc
    bg_box = [center - r, center - r, center + r, center + r]
    draw.ellipse(bg_box, fill=(10, 15, 26, 255))
    
    # Subtle depth rings
    for i in range(max(1, int(size * 0.05))):
        step_r = r - (i * (size * 0.02))
        alpha = int(25 + i * 15)
        box = [center - step_r, center - step_r, center + step_r, center + step_r]
        draw.ellipse(box, outline=(18, 30, 52, min(255, alpha)), width=max(1, int(size * 0.01)))

    # Outer neon cyan ring
    draw.ellipse([center - r*0.92, center - r*0.92, center + r*0.92, center + r*0.92], 
                 outline=(0, 242, 254, 220), width=max(1, int(size * 0.025)))

    # Modern geometric Zenith "Z"
    scale = size / 108.0
    def pt(x, y):
        return (x * scale, y * scale)
        
    # Top bar
    top_poly = [pt(30, 32), pt(78, 32), pt(72, 42), pt(38, 42)]
    draw.polygon(top_poly, fill=(0, 242, 254, 255))
    
    # Diagonal beam
    diag_poly = [pt(78, 32), pt(70, 42), pt(36, 76), pt(30, 66)]
    draw.polygon(diag_poly, fill=(56, 189, 248, 255))
    
    # Core inner glow diagonal
    inner_diag = [pt(66, 42), pt(58, 42), pt(40, 66), pt(48, 66)]
    draw.polygon(inner_diag, fill=(129, 140, 248, 255))
    
    # Bottom bar
    draw.polygon([pt(30, 66), pt(78, 66), pt(78, 76), pt(30, 76)], fill=(99, 102, 241, 255))

    # Center apex star / spark
    star_pts = []
    star_r_out = size * 0.08
    star_r_in = size * 0.03
    for i in range(8):
        angle = i * math.pi / 4 - math.pi / 2
        cur_r = star_r_out if i % 2 == 0 else star_r_in
        star_pts.append((center + cur_r * math.cos(angle), center + cur_r * math.sin(angle)))
    draw.polygon(star_pts, fill=(255, 255, 255, 255))

    if is_round:
        mask = Image.new("L", (size, size), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse([center - r, center - r, center + r, center + r], fill=255)
        round_img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        round_img.paste(img, (0, 0), mask=mask)
        return round_img

    return img

def render_zenith_text_logo(width=320, height=80):
    """Renders the sleek ZENITH typography banner for New Tab Page & About."""
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    scale = 56.0 / 108.0
    def pt(x, y):
        return (12 + x * scale, 12 + y * scale)
        
    draw.polygon([pt(30, 32), pt(78, 32), pt(72, 42), pt(38, 42)], fill=(0, 242, 254, 255))
    draw.polygon([pt(78, 32), pt(70, 42), pt(36, 76), pt(30, 66)], fill=(56, 189, 248, 255))
    draw.polygon([pt(30, 66), pt(78, 66), pt(78, 76), pt(30, 76)], fill=(99, 102, 241, 255))
    
    font = None
    for font_path in ["/system/fonts/Roboto-Bold.ttf", "/data/data/com.termux/files/usr/share/fonts/TTF/DejaVuSans-Bold.ttf"]:
        if os.path.exists(font_path):
            try:
                font = ImageFont.truetype(font_path, 40)
                break
            except Exception:
                pass
                
    if font:
        draw.text((80, 16), "ZENITH", fill=(255, 255, 255, 255), font=font)
    else:
        draw.text((80, 20), "ZENITH", fill=(255, 255, 255, 255))
    return img

def rebuild_resources_arsc(arsc_data):
    """
    Parses and rebuilds resources.arsc StringPool chunk:
    - Global replacement of all 'Kiwi Browser', 'Kiwi', 'kiwi', 'Geometry' across all locales.
    - Redirects anydpi-v26 icon paths to xxxhdpi bitmap so Android 16 never falls back to robot icon.
    """
    arsc = bytearray(arsc_data)
    res_type, header_size, orig_total, pkg_count = struct.unpack("<HHII", arsc[:12])
    sp_offset = 12
    sp_type, sp_header_size, sp_size, sp_str_count, sp_style_count, sp_flags, sp_str_offset, sp_style_offset = struct.unpack("<HHIIIIII", arsc[sp_offset:sp_offset+28])
    offsets = struct.unpack(f"<{sp_str_count}I", arsc[sp_offset+28 : sp_offset+28+sp_str_count*4])
    style_offsets = struct.unpack(f"<{sp_style_count}I", arsc[sp_offset+28+sp_str_count*4 : sp_offset+28+(sp_str_count+sp_style_count)*4])
    style_data = arsc[sp_offset + sp_style_offset : sp_offset + sp_size]
    strings_start = sp_offset + sp_str_offset
    chunk1_data = arsc[sp_offset + sp_size :]

    new_string_data = bytearray()
    new_offsets = []

    for i in range(sp_str_count):
        off = offsets[i]
        pos = strings_start + off
        c_len = arsc[pos]
        pos += 1
        if c_len & 0x80:
            c_len = ((c_len & 0x7F) << 8) | arsc[pos]
            pos += 1
        b_len = arsc[pos]
        pos += 1
        if b_len & 0x80:
            b_len = ((b_len & 0x7F) << 8) | arsc[pos]
            pos += 1
        s_bytes = bytes(arsc[pos : pos + b_len])
        
        # Comprehensive global replacement
        if b"Kiwi Browser" in s_bytes:
            s_bytes = s_bytes.replace(b"Kiwi Browser", b"Zenith")
        if b"Kiwi" in s_bytes:
            s_bytes = s_bytes.replace(b"Kiwi", b"Zenith")
        if b"kiwi" in s_bytes:
            s_bytes = s_bytes.replace(b"kiwi", b"zenith")
        if b"Geometry OU" in s_bytes:
            s_bytes = s_bytes.replace(b"Geometry OU", b"Zenith Project")
        if b"Geometry" in s_bytes:
            s_bytes = s_bytes.replace(b"Geometry", b"Zenith")
        if b"res/mipmap-anydpi-v26/ic_launcher.xml" in s_bytes:
            s_bytes = s_bytes.replace(b"res/mipmap-anydpi-v26/ic_launcher.xml", b"res/mipmap-xxxhdpi-v4/ic_launcher")
        if b"res/mipmap-anydpi-v26/ic_launcher_round.xml" in s_bytes:
            s_bytes = s_bytes.replace(b"res/mipmap-anydpi-v26/ic_launcher_round.xml", b"res/mipmap-xxxhdpi-v4/ic_launcher_round")
            
        try:
            c_count = len(s_bytes.decode("utf-8"))
        except Exception:
            c_count = len(s_bytes)
        b_count = len(s_bytes)
        
        new_offsets.append(len(new_string_data))
        
        if c_count <= 0x7F:
            new_string_data.append(c_count)
        else:
            new_string_data.append((c_count >> 8) | 0x80)
            new_string_data.append(c_count & 0xFF)
            
        if b_count <= 0x7F:
            new_string_data.append(b_count)
        else:
            new_string_data.append((b_count >> 8) | 0x80)
            new_string_data.append(b_count & 0xFF)
            
        new_string_data.extend(s_bytes)
        new_string_data.append(0)

    pad_len = (4 - (len(new_string_data) % 4)) % 4
    new_string_data.extend(b"\x00" * pad_len)

    new_strings_start = 28 + (sp_str_count + sp_style_count) * 4
    new_style_offset = new_strings_start + len(new_string_data)
    new_sp_size = new_style_offset + len(style_data)
    chunk_pad = (4 - (new_sp_size % 4)) % 4
    new_sp_size += chunk_pad

    new_sp = bytearray()
    new_sp.extend(struct.pack("<HHIIIIII", sp_type, sp_header_size, new_sp_size, sp_str_count, sp_style_count, sp_flags, new_strings_start, new_style_offset))
    for o in new_offsets:
        new_sp.extend(struct.pack("<I", o))
    for so in style_offsets:
        new_sp.extend(struct.pack("<I", so))
    new_sp.extend(new_string_data)
    new_sp.extend(style_data)
    new_sp.extend(b"\x00" * chunk_pad)

    new_total_size = 12 + len(new_sp) + len(chunk1_data)
    new_arsc = bytearray()
    new_arsc.extend(struct.pack("<HHII", 0x0002, 12, new_total_size, pkg_count))
    new_arsc.extend(new_sp)
    new_arsc.extend(chunk1_data)
    return bytes(new_arsc)

def patch_classes_dex(dex_data):
    """
    Patches classes.dex:
    1. Replaces `if-eqz v1` for main_menu_extensions at 0x4df68a with NOPs so Extensions menu item is unconditionally visible.
    2. Replaces Java string 'Kiwi Browser' with 'Zenith (Web)'.
    3. Recomputes SHA-1 and Adler32 checksums.
    """
    dex = bytearray(dex_data)
    # 1. NOP the condition hiding Extensions in 3-dots menu
    if len(dex) > 0x4df68e and dex[0x4df68a : 0x4df68e] == b"\x38\x01\x0e\x00":
        dex[0x4df68a : 0x4df68e] = b"\x00\x00\x00\x00"
        print("[+] Patched ChromeActivity menu visibility: Extensions menu is now unconditionally visible!")

    # 2. Patch string "Kiwi Browser"
    pos = dex.find(b"\x0cKiwi Browser\x00")
    if pos != -1:
        dex[pos : pos + 14] = b"\x0cZenith (Web)\x00"
        print(f"[+] Replaced DEX string 'Kiwi Browser' at offset {pos} with 'Zenith (Web)'")

    # 3. Recalculate DEX integrity hashes
    sig = hashlib.sha1(dex[32:]).digest()
    dex[12:32] = sig
    chk = zlib.adler32(dex[12:]) & 0xFFFFFFFF
    dex[8:12] = struct.pack("<I", chk)
    print("[+] DEX SHA-1 and Adler-32 checksums recomputed successfully!")
    return bytes(dex)

def compile_imerek_so(work_dir):
    """Compiles the lightweight native embedded Imerek UYAP server."""
    src_c = os.path.join(os.path.dirname(__file__), "imerek_server.c")
    out_so = os.path.join(work_dir, "libimerek.so")
    subprocess.check_call([
        "clang", "-shared", "-fPIC", "-O2",
        src_c, "-o", out_so, "-llog"
    ])
    subprocess.check_call(["strip", out_so])
    return out_so

def rebrand_apk(input_apk, output_apk, keystore_path="zenith.keystore"):
    print(f"\n=======================================================")
    print(f" Zenith Browser - Complete Rebrand & Engine Integration")
    print(f" Source: {input_apk} -> Target: {output_apk}")
    print(f"=======================================================")
    
    work_dir = os.path.join(os.path.dirname(output_apk), "zenith_rebrand_tmp")
    shutil.rmtree(work_dir, ignore_errors=True)
    os.makedirs(work_dir, exist_ok=True)

    print("[*] 1/6 Generating pure 32-bit Zenith bitmap assets & icons...")
    # 1. Launcher mipmaps: 32-bit PNG bitmaps across all densities
    densities = {
        "mipmap-mdpi-v4": 48,
        "mipmap-hdpi-v4": 72,
        "mipmap-xhdpi-v4": 96,
        "mipmap-xxhdpi-v4": 144,
        "mipmap-xxxhdpi-v4": 192,
    }
    rendered_assets = {}
    for folder, px in densities.items():
        reg_img = render_zenith_icon(px, is_round=False)
        rnd_img = render_zenith_icon(px, is_round=True)
        reg_path = os.path.join(work_dir, f"{folder}_reg.png")
        rnd_path = os.path.join(work_dir, f"{folder}_rnd.png")
        reg_img.save(reg_path, format="PNG")
        rnd_img.save(rnd_path, format="PNG")
        with open(reg_path, "rb") as f:
            rendered_assets[f"res/{folder}/ic_launcher"] = f.read()
        with open(rnd_path, "rb") as f:
            rendered_assets[f"res/{folder}/ic_launcher_round"] = f.read()

    # 2. In-app logos (replace all Kiwi birds & logos)
    # chromelogo16 (tablet tab & title bar icon)
    for px, folders in [(16, ["res/drawable/chromelogo16", "res/drawable-hdpi-v4/chromelogo16"]),
                        (24, ["res/drawable-xhdpi-v4/chromelogo16"]),
                        (32, ["res/drawable-xxhdpi-v4/chromelogo16"])]:
        icon_img = render_zenith_icon(px, is_round=False)
        p = os.path.join(work_dir, f"chromelogo_{px}.png")
        icon_img.save(p, format="PNG")
        with open(p, "rb") as f:
            data = f.read()
        for fld in folders:
            rendered_assets[fld] = data

    # ic_chrome & infobar_chrome
    for px, folders in [(24, ["res/drawable/ic_chrome", "res/drawable-hdpi-v4/ic_chrome", "res/drawable/infobar_chrome", "res/drawable-hdpi-v4/infobar_chrome"]),
                        (36, ["res/drawable-xhdpi-v4/ic_chrome", "res/drawable-xhdpi-v4/infobar_chrome"]),
                        (48, ["res/drawable-xxhdpi-v4/ic_chrome", "res/drawable-xxhdpi-v4/infobar_chrome"])]:
        icon_img = render_zenith_icon(px, is_round=False)
        p = os.path.join(work_dir, f"ic_chrome_{px}.png")
        icon_img.save(p, format="PNG")
        with open(p, "rb") as f:
            data = f.read()
        for fld in folders:
            rendered_assets[fld] = data

    # fre_product_logo (NTP main splash logo)
    fre_img = render_zenith_icon(192, is_round=False)
    fre_p = os.path.join(work_dir, "fre_product_logo.png")
    fre_img.save(fre_p, format="PNG")
    with open(fre_p, "rb") as f:
        fre_data = f.read()
    for fld in ["res/drawable/fre_product_logo", "res/drawable-hdpi-v4/fre_product_logo", 
                "res/drawable-xhdpi-v4/fre_product_logo", "res/drawable-xxhdpi-v4/fre_product_logo"]:
        rendered_assets[fld] = fre_data

    # product_logo_name (NTP name banner)
    banner_img = render_zenith_text_logo(320, 80)
    banner_p = os.path.join(work_dir, "product_logo_name.png")
    banner_img.save(banner_p, format="PNG")
    with open(banner_p, "rb") as f:
        banner_data = f.read()
    for fld in ["res/drawable/product_logo_name", "res/drawable-hdpi-v4/product_logo_name",
                "res/drawable-xhdpi-v4/product_logo_name", "res/drawable-xxhdpi-v4/product_logo_name"]:
        rendered_assets[fld] = banner_data

    # 3. Built-in Imerek UYAP Native Server Injection
    print("[*] 2/6 Compiling & linking Built-in Imerek UYAP Server (libimerek.so)...")
    libimerek_path = compile_imerek_so(work_dir)
    with open(libimerek_path, "rb") as f:
        libimerek_data = f.read()

    # Extract libchrome.so to add DT_NEEDED dependency
    print("[*] 3/6 Patching libchrome.so to auto-launch Imerek Server on startup...")
    temp_libchrome = os.path.join(work_dir, "libchrome.so")
    with zipfile.ZipFile(input_apk, "r") as z:
        with z.open("lib/arm64-v8a/libchrome.so") as so, open(temp_libchrome, "wb") as out:
            shutil.copyfileobj(so, out)
            
    subprocess.check_call(["patchelf", "--add-needed", "libimerek.so", temp_libchrome])
    with open(temp_libchrome, "rb") as f:
        patched_libchrome = f.read()

    # 4. Preparing bundled extension packages
    print("[*] 4/6 Preparing uBlock Origin & Imerek extensions...")
    ublock_src = "/sdcard/Download/uBlock0_latest.chromium.zip"
    imerek_src = "/sdcard/Download/imerek_uyap_android.zip"
    
    # Also copy to convenient user location
    user_ext_dir = "/sdcard/Download/Zenith_Extensions"
    os.makedirs(user_ext_dir, exist_ok=True)
    if os.path.exists(ublock_src):
        shutil.copy2(ublock_src, os.path.join(user_ext_dir, "uBlock0_latest.chromium.zip"))
        shutil.copy2(ublock_src, "/sdcard/Download/Zenith_uBlock0.zip")
    if os.path.exists(imerek_src):
        shutil.copy2(imerek_src, os.path.join(user_ext_dir, "imerek_uyap_android.zip"))
        shutil.copy2(imerek_src, "/sdcard/Download/Zenith_Imerek_UYAP.zip")

    # 5. Repackaging APK
    print("[*] 5/6 Rebuilding string pool, DEX and repackaging APK...")
    unaligned_apk = os.path.join(work_dir, "unaligned.apk")
    with zipfile.ZipFile(input_apk, "r") as src, zipfile.ZipFile(unaligned_apk, "w", compression=zipfile.ZIP_DEFLATED) as dst:
        for item in src.infolist():
            # Strip old Kiwi signatures
            if item.filename.startswith("META-INF/") and any(item.filename.endswith(ext) for ext in [".SF", ".RSA", ".DSA", ".MF"]):
                continue
            
            # Remove anydpi-v26 files so Android 16 directly loads 192x192 bitmaps
            if item.filename.startswith("res/mipmap-anydpi-v26/"):
                print(f"[+] Stripped legacy vector {item.filename}")
                continue

            # Rebuild resources.arsc with full global replacement
            if item.filename == "resources.arsc":
                print("[*] Rebuilding complete ARSC string pool...")
                data = rebuild_resources_arsc(src.read(item.filename))
                dst.writestr(item, data)
            # Patch classes.dex
            elif item.filename == "classes.dex":
                print("[*] Patching classes.dex (unconditional Extensions menu)...")
                data = patch_classes_dex(src.read(item.filename))
                dst.writestr(item, data)
            # Inject rendered brand assets
            elif item.filename in rendered_assets:
                dst.writestr(item, rendered_assets[item.filename])
            # Inject patched libchrome.so
            elif item.filename == "lib/arm64-v8a/libchrome.so":
                print("[+] Injected patched libchrome.so with libimerek.so DT_NEEDED")
                dst.writestr(item, patched_libchrome)
            # Clear Kiwi bird gradient parts
            elif item.filename in ["res/drawable/$ic_launcher_background__0.xml",
                                   "res/drawable/$ic_launcher_foreground__0.xml",
                                   "res/drawable/$ic_launcher_foreground__1.xml"]:
                dummy_xml = b'<vector xmlns:android="http://schemas.android.com/apk/res/android" android:width="1dp" android:height="1dp" android:viewportWidth="1" android:viewportHeight="1"/>'
                dst.writestr(item, dummy_xml)
            else:
                dst.writestr(item, src.read(item.filename))

        # Add libimerek.so into APK
        imerek_entry = zipfile.ZipInfo("lib/arm64-v8a/libimerek.so")
        imerek_entry.compress_type = zipfile.ZIP_DEFLATED
        dst.writestr(imerek_entry, libimerek_data)
        print("[+] Embedded lib/arm64-v8a/libimerek.so directly into APK")

        # Add extension zip packages into assets/default_extensions/
        if os.path.exists(ublock_src):
            with open(ublock_src, "rb") as f:
                dst.writestr("assets/default_extensions/uBlock0.chromium.zip", f.read())
                print("[+] Bundled assets/default_extensions/uBlock0.chromium.zip")
        if os.path.exists(imerek_src):
            with open(imerek_src, "rb") as f:
                dst.writestr("assets/default_extensions/imerek_uyap.zip", f.read())
                print("[+] Bundled assets/default_extensions/imerek_uyap.zip")

    # 6. Align and Sign
    print("[*] 6/6 Aligning and signing final release APK...")
    aligned_apk = os.path.join(work_dir, "aligned.apk")
    subprocess.check_call(["zipalign", "-p", "-f", "4", unaligned_apk, aligned_apk])

    if not os.path.exists(keystore_path):
        print(f"[*] Keystore {keystore_path} not found, generating release keystore...")
        subprocess.check_call([
            "keytool", "-genkeypair", "-v",
            "-keystore", keystore_path,
            "-alias", "zenith",
            "-keyalg", "RSA", "-keysize", "2048",
            "-validity", "10000",
            "-storepass", "zenith123", "-keypass", "zenith123",
            "-dname", "CN=Zenith, OU=ZenithBrowser, O=Zenith, L=SanFrancisco, ST=CA, C=US"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    subprocess.check_call([
        "apksigner", "sign",
        "--ks", keystore_path,
        "--ks-pass", "pass:zenith123",
        "--key-pass", "pass:zenith123",
        "--ks-key-alias", "zenith",
        "--out", output_apk,
        aligned_apk
    ])

    subprocess.check_call(["apksigner", "verify", "--verbose", output_apk])
    shutil.rmtree(work_dir, ignore_errors=True)
    print(f"\n[SUCCESS] Zenith Browser built & signed successfully: {output_apk} ({os.path.getsize(output_apk):,} bytes)")

if __name__ == "__main__":
    src_apk = sys.argv[1] if len(sys.argv) > 1 else "/sdcard/Download/com.kiwibrowser.browser-arm64-14310011181-github.apk"
    dst_apk = sys.argv[2] if len(sys.argv) > 2 else "/sdcard/Download/ZenithBrowser-Android-arm64.apk"
    rebrand_apk(src_apk, dst_apk)
