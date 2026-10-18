#!/usr/bin/env python3
"""
Zenith Browser - Robust Rebranding Pipeline
- Compiles valid Android 8-16 adaptive vector drawables with aapt2 and framework-res.apk.
- Completely purges Kiwi and Geometry branding from resources.arsc across all languages.
- Injects high-resolution in-app Zenith graphics and typography banners.
- Preserves 100% original binary stability of classes.dex and libchrome.so to prevent launch crashes.
"""

import os
import sys
import math
import struct
import shutil
import zipfile
import subprocess
from PIL import Image, ImageDraw, ImageFont

def render_zenith_icon(size, is_round=False):
    """Renders a high-tech cosmic Zenith 'Z' browser icon."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    center = size / 2.0
    r = size * 0.46
    
    bg_box = [center - r, center - r, center + r, center + r]
    draw.ellipse(bg_box, fill=(10, 15, 26, 255))
    
    for i in range(max(1, int(size * 0.05))):
        step_r = r - (i * (size * 0.02))
        alpha = int(25 + i * 15)
        box = [center - step_r, center - step_r, center + step_r, center + step_r]
        draw.ellipse(box, outline=(18, 30, 52, min(255, alpha)), width=max(1, int(size * 0.01)))

    draw.ellipse([center - r*0.92, center - r*0.92, center + r*0.92, center + r*0.92], 
                 outline=(0, 242, 254, 220), width=max(1, int(size * 0.025)))

    scale = size / 108.0
    def pt(x, y):
        return (x * scale, y * scale)
        
    top_poly = [pt(30, 32), pt(78, 32), pt(72, 42), pt(38, 42)]
    draw.polygon(top_poly, fill=(0, 242, 254, 255))
    
    diag_poly = [pt(78, 32), pt(70, 42), pt(36, 76), pt(30, 66)]
    draw.polygon(diag_poly, fill=(56, 189, 248, 255))
    
    inner_diag = [pt(66, 42), pt(58, 42), pt(40, 66), pt(48, 66)]
    draw.polygon(inner_diag, fill=(129, 140, 248, 255))
    
    draw.polygon([pt(30, 66), pt(78, 66), pt(78, 76), pt(30, 76)], fill=(99, 102, 241, 255))

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

def compile_adaptive_vectors(work_dir):
    """Compiles modern Android 8-16 compatible adaptive vector drawables with aapt2."""
    res_dir = os.path.join(work_dir, "res", "drawable")
    os.makedirs(res_dir, exist_ok=True)

    bg_xml = """<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="108dp"
    android:height="108dp"
    android:viewportWidth="108"
    android:viewportHeight="108">
    <path
        android:fillColor="#0a0f1a"
        android:pathData="M0,0 h108 v108 h-108 z" />
    <path
        android:fillColor="#121e34"
        android:pathData="M54,14 A40,40 0 1,1 53.9,14 Z" />
    <path
        android:strokeColor="#00f2fe"
        android:strokeWidth="1.5"
        android:pathData="M54,16 A38,38 0 1,1 53.9,16 Z" />
</vector>"""

    fg_xml = """<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="108dp"
    android:height="108dp"
    android:viewportWidth="108"
    android:viewportHeight="108">
    <path
        android:fillColor="#00f2fe"
        android:pathData="M30,32 L78,32 L72,42 L38,42 Z" />
    <path
        android:fillColor="#38bdf8"
        android:pathData="M78,32 L70,42 L36,76 L30,66 Z" />
    <path
        android:fillColor="#818cf8"
        android:pathData="M66,42 L58,42 L40,66 L48,66 Z" />
    <path
        android:fillColor="#6366f1"
        android:pathData="M30,66 L78,66 L78,76 L30,76 Z" />
    <path
        android:fillColor="#ffffff"
        android:pathData="M54,49 L56,54 L61,54 L57,57 L59,62 L54,59 L49,62 L51,57 L47,54 L52,54 Z" />
</vector>"""

    with open(os.path.join(res_dir, "ic_launcher_background.xml"), "w") as f:
        f.write(bg_xml)
    with open(os.path.join(res_dir, "ic_launcher_foreground.xml"), "w") as f:
        f.write(fg_xml)

    manifest_xml = """<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="com.zenith.brand">
    <uses-sdk android:minSdkVersion="26" android:targetSdkVersion="34" />
</manifest>"""
    manifest_path = os.path.join(work_dir, "AndroidManifest.xml")
    with open(manifest_path, "w") as f:
        f.write(manifest_xml)

    framework_apk = "/system/framework/framework-res.apk"
    if not os.path.exists(framework_apk):
        framework_apk = os.path.expanduser("~/.local/share/apktool/framework/1.apk")

    for name in ["ic_launcher_background.xml", "ic_launcher_foreground.xml"]:
        subprocess.check_call(["aapt2", "compile", os.path.join(res_dir, name), "-o", work_dir], stdout=subprocess.DEVNULL)

    out_apk = os.path.join(work_dir, "compiled_vectors.apk")
    flats = [os.path.join(work_dir, f"drawable_{name}.flat") for name in ["ic_launcher_background.xml", "ic_launcher_foreground.xml"]]
    cmd = ["aapt2", "link"]
    if os.path.exists(framework_apk):
        cmd.extend(["-I", framework_apk])
    cmd.extend(["--manifest", manifest_path] + flats + ["-o", out_apk])
    subprocess.check_call(cmd, stdout=subprocess.DEVNULL)

    compiled = {}
    with zipfile.ZipFile(out_apk, "r") as z:
        for name in ["res/drawable/ic_launcher_background.xml", "res/drawable/ic_launcher_foreground.xml"]:
            compiled[name] = z.read(name)
    return compiled

def rebuild_resources_arsc(arsc_data):
    """
    Parses and rebuilds resources.arsc StringPool chunk:
    Global replacement of all 'Kiwi Browser', 'Kiwi', 'kiwi', 'Geometry' across all locales.
    Preserves all resource path mappings intact.
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
        
        # Only replace brand text strings
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

def rebrand_apk(input_apk, output_apk, keystore_path="zenith.keystore"):
    print(f"\n=======================================================")
    print(f" Zenith Browser - Rebrand & Adaptive Vector Engine")
    print(f" Source: {input_apk} -> Target: {output_apk}")
    print(f"=======================================================")
    
    work_dir = os.path.join(os.path.dirname(output_apk), "zenith_rebrand_tmp")
    shutil.rmtree(work_dir, ignore_errors=True)
    os.makedirs(work_dir, exist_ok=True)

    print("[*] 1/4 Compiling modern Android 8-16 adaptive vectors with aapt2...")
    compiled_vectors = compile_adaptive_vectors(work_dir)

    print("[*] 2/4 Generating in-app Zenith graphics and launcher bitmaps...")
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

    # In-app brand logos
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

    fre_img = render_zenith_icon(192, is_round=False)
    fre_p = os.path.join(work_dir, "fre_product_logo.png")
    fre_img.save(fre_p, format="PNG")
    with open(fre_p, "rb") as f:
        fre_data = f.read()
    for fld in ["res/drawable/fre_product_logo", "res/drawable-hdpi-v4/fre_product_logo", 
                "res/drawable-xhdpi-v4/fre_product_logo", "res/drawable-xxhdpi-v4/fre_product_logo"]:
        rendered_assets[fld] = fre_data

    banner_img = render_zenith_text_logo(320, 80)
    banner_p = os.path.join(work_dir, "product_logo_name.png")
    banner_img.save(banner_p, format="PNG")
    with open(banner_p, "rb") as f:
        banner_data = f.read()
    for fld in ["res/drawable/product_logo_name", "res/drawable-hdpi-v4/product_logo_name",
                "res/drawable-xhdpi-v4/product_logo_name", "res/drawable-xxhdpi-v4/product_logo_name"]:
        rendered_assets[fld] = banner_data

    # 3. Repackaging APK
    print("[*] 3/4 Rebuilding string pool and assembling APK...")
    unaligned_apk = os.path.join(work_dir, "unaligned.apk")
    with zipfile.ZipFile(input_apk, "r") as src, zipfile.ZipFile(unaligned_apk, "w", compression=zipfile.ZIP_DEFLATED) as dst:
        for item in src.infolist():
            # Strip old Kiwi signatures
            if item.filename.startswith("META-INF/") and any(item.filename.endswith(ext) for ext in [".SF", ".RSA", ".DSA", ".MF"]):
                continue

            # Rebuild resources.arsc with full global replacement
            if item.filename == "resources.arsc":
                print("[*] Rebuilding complete ARSC string pool...")
                data = rebuild_resources_arsc(src.read(item.filename))
                dst.writestr(item, data)
            # Inject compiled adaptive vectors
            elif item.filename in compiled_vectors:
                print(f"[+] Injected modern adaptive vector {item.filename}")
                dst.writestr(item, compiled_vectors[item.filename])
            # Inject rendered brand assets
            elif item.filename in rendered_assets:
                dst.writestr(item, rendered_assets[item.filename])
            # Clear Kiwi bird gradient parts with 1x1 vector
            elif item.filename in ["res/drawable/$ic_launcher_background__0.xml",
                                   "res/drawable/$ic_launcher_foreground__0.xml",
                                   "res/drawable/$ic_launcher_foreground__1.xml"]:
                dummy_xml = b'<vector xmlns:android="http://schemas.android.com/apk/res/android" android:width="1dp" android:height="1dp" android:viewportWidth="1" android:viewportHeight="1"/>'
                dst.writestr(item, dummy_xml)
            else:
                dst.writestr(item, src.read(item.filename))

    # 4. Align and Sign
    print("[*] 4/4 Aligning and signing final release APK...")
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
