#!/usr/bin/env python3
"""
Zenith Browser - Full Android Branding, In-App Graphics & Built-in Imerek UYAP Engine
- Replaces all Kiwi logos, birds, and names with high-tech Zenith branding.
- Injects embedded native C server (libimerek.so) on port 9936 into libchrome.so.
- Produces clean, pure Chromium look with zero Kiwi traces.
"""

import os
import sys
import math
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

def compile_vector_drawables(work_dir):
    """Compiles Android vector drawables into binary XML format using aapt."""
    res_dir = os.path.join(work_dir, "res", "drawable")
    os.makedirs(res_dir, exist_ok=True)
    
    bg_xml = """<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="108dp"
    android:height="108dp"
    android:viewportWidth="108"
    android:viewportHeight="108">
    <path
        android:fillColor="#090d16"
        android:pathData="M0,0 h108 v108 h-108 z" />
    <path
        android:fillColor="#131d31"
        android:pathData="M54,16 A38,38 0 1,1 53.9,16 Z" />
    <path
        android:fillColor="#1e293b"
        android:pathData="M54,26 A28,28 0 1,1 53.9,26 Z" />
</vector>"""

    fg_xml = """<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="108dp"
    android:height="108dp"
    android:viewportWidth="108"
    android:viewportHeight="108">
    <path
        android:fillColor="#155e75"
        android:pathData="M54,24 A30,30 0 0,1 84,54 A30,30 0 0,1 54,84 A30,30 0 0,1 24,54 A30,30 0 0,1 54,24 Z M54,28 A26,26 0 1,0 80,54 A26,26 0 0,0 54,28 Z" />
    <path
        android:fillColor="#00f2fe"
        android:pathData="M32,34 L76,34 L72,42 L38,42 Z" />
    <path
        android:fillColor="#38bdf8"
        android:pathData="M32,34 L76,34 L76,43 L49,70 L76,70 L76,76 L32,76 L32,67 L59,40 L32,40 Z" />
    <path
        android:fillColor="#818cf8"
        android:pathData="M44,40 L69,40 L45,68 L37,68 Z" />
    <path
        android:fillColor="#ffffff"
        android:pathData="M54,49 L56,54 L61,54 L57,57 L59,62 L54,59 L49,62 L51,57 L47,54 L52,54 Z" />
</vector>"""

    mono_xml = """<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="108dp"
    android:height="108dp"
    android:viewportWidth="108"
    android:viewportHeight="108">
    <path
        android:fillColor="#ffffff"
        android:pathData="M32,34 L76,34 L76,43 L49,70 L76,70 L76,76 L32,76 L32,67 L59,40 L32,40 Z" />
    <path
        android:fillColor="#ffffff"
        android:pathData="M54,49 L56,54 L61,54 L57,57 L59,62 L54,59 L49,62 L51,57 L47,54 L52,54 Z" />
</vector>"""

    with open(os.path.join(res_dir, "ic_launcher_background.xml"), "w") as f:
        f.write(bg_xml)
    with open(os.path.join(res_dir, "ic_launcher_foreground.xml"), "w") as f:
        f.write(fg_xml)
    with open(os.path.join(res_dir, "ic_launcher_monochrome.xml"), "w") as f:
        f.write(mono_xml)

    manifest_xml = '<manifest xmlns:android="http://schemas.android.com/apk/res/android" package="com.zenith.brand" />'
    manifest_path = os.path.join(work_dir, "AndroidManifest.xml")
    with open(manifest_path, "w") as f:
        f.write(manifest_xml)

    out_apk = os.path.join(work_dir, "compiled_vectors.apk")
    framework_apk = os.path.expanduser("~/.local/share/apktool/framework/1.apk")
    cmd = ["aapt", "package", "-f", "-M", manifest_path, "-S", os.path.join(work_dir, "res"), "-F", out_apk]
    if os.path.exists(framework_apk):
        cmd.extend(["-I", framework_apk])
    subprocess.check_call(cmd, stdout=subprocess.DEVNULL)

    compiled = {}
    with zipfile.ZipFile(out_apk, "r") as z:
        for name in ["res/drawable/ic_launcher_background.xml", 
                     "res/drawable/ic_launcher_foreground.xml", 
                     "res/drawable/ic_launcher_monochrome.xml"]:
            compiled[name] = z.read(name)
    return compiled

def patch_resources_arsc(arsc_data):
    """Patches application-label in resources.arsc from 'Kiwi Browser' to 'Zenith'."""
    arsc = bytearray(arsc_data)
    target = b"\x0c\x0cKiwi Browser\x00"
    pos = arsc.find(target)
    if pos != -1:
        print(f"[*] Found string 761 ('Kiwi Browser') at offset {pos}. Replacing with 'Zenith'...")
        arsc[pos] = 6
        arsc[pos + 1] = 6
        new_text = b"Zenith\x00" + b"\x00" * 6
        arsc[pos + 2 : pos + 15] = new_text
    else:
        raw_pos = arsc.find(b"Kiwi Browser")
        if raw_pos != -1:
            arsc[raw_pos : raw_pos + 6] = b"Zenith"
    return bytes(arsc)

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

    print("[*] 1/5 Compiling Zenith adaptive vector drawables...")
    compiled_vectors = compile_vector_drawables(work_dir)

    print("[*] 2/5 Generating Zenith in-app brand logos & icons...")
    # 1. Launcher mipmaps
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
        reg_path = os.path.join(work_dir, f"{folder}_reg.webp")
        rnd_path = os.path.join(work_dir, f"{folder}_rnd.webp")
        reg_img.save(reg_path, format="WEBP", lossless=True)
        rnd_img.save(rnd_path, format="WEBP", lossless=True)
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
        p = os.path.join(work_dir, f"chromelogo_{px}.webp")
        icon_img.save(p, format="WEBP", lossless=True)
        with open(p, "rb") as f:
            data = f.read()
        for fld in folders:
            rendered_assets[fld] = data

    # ic_chrome & infobar_chrome
    for px, folders in [(24, ["res/drawable/ic_chrome", "res/drawable-hdpi-v4/ic_chrome", "res/drawable/infobar_chrome", "res/drawable-hdpi-v4/infobar_chrome"]),
                        (36, ["res/drawable-xhdpi-v4/ic_chrome", "res/drawable-xhdpi-v4/infobar_chrome"]),
                        (48, ["res/drawable-xxhdpi-v4/ic_chrome", "res/drawable-xxhdpi-v4/infobar_chrome"])]:
        icon_img = render_zenith_icon(px, is_round=False)
        p = os.path.join(work_dir, f"ic_chrome_{px}.webp")
        icon_img.save(p, format="WEBP", lossless=True)
        with open(p, "rb") as f:
            data = f.read()
        for fld in folders:
            rendered_assets[fld] = data

    # fre_product_logo (NTP main splash logo)
    fre_img = render_zenith_icon(192, is_round=False)
    fre_p = os.path.join(work_dir, "fre_product_logo.webp")
    fre_img.save(fre_p, format="WEBP", lossless=True)
    with open(fre_p, "rb") as f:
        fre_data = f.read()
    for fld in ["res/drawable/fre_product_logo", "res/drawable-hdpi-v4/fre_product_logo", 
                "res/drawable-xhdpi-v4/fre_product_logo", "res/drawable-xxhdpi-v4/fre_product_logo"]:
        rendered_assets[fld] = fre_data

    # product_logo_name (NTP name banner)
    banner_img = render_zenith_text_logo(320, 80)
    banner_p = os.path.join(work_dir, "product_logo_name.webp")
    banner_img.save(banner_p, format="WEBP", lossless=True)
    with open(banner_p, "rb") as f:
        banner_data = f.read()
    for fld in ["res/drawable/product_logo_name", "res/drawable-hdpi-v4/product_logo_name",
                "res/drawable-xhdpi-v4/product_logo_name", "res/drawable-xxhdpi-v4/product_logo_name"]:
        rendered_assets[fld] = banner_data

    # 3. Built-in Imerek UYAP Native Server Injection
    print("[*] 3/5 Compiling & linking Built-in Imerek UYAP Server (libimerek.so)...")
    libimerek_path = compile_imerek_so(work_dir)
    with open(libimerek_path, "rb") as f:
        libimerek_data = f.read()

    # Extract libchrome.so to add DT_NEEDED dependency
    print("[*] 4/5 Patching libchrome.so to auto-launch Imerek Server on startup...")
    temp_libchrome = os.path.join(work_dir, "libchrome.so")
    with zipfile.ZipFile(input_apk, "r") as z:
        with z.open("lib/arm64-v8a/libchrome.so") as so, open(temp_libchrome, "wb") as out:
            shutil.copyfileobj(so, out)
            
    subprocess.check_call(["patchelf", "--add-needed", "libimerek.so", temp_libchrome])
    with open(temp_libchrome, "rb") as f:
        patched_libchrome = f.read()

    # 4. Repackage APK
    print("[*] 5/5 Repackaging and signing Zenith APK...")
    unaligned_apk = os.path.join(work_dir, "unaligned.apk")
    with zipfile.ZipFile(input_apk, "r") as src, zipfile.ZipFile(unaligned_apk, "w", compression=zipfile.ZIP_DEFLATED) as dst:
        for item in src.infolist():
            # Strip old Kiwi signatures
            if item.filename.startswith("META-INF/") and any(item.filename.endswith(ext) for ext in [".SF", ".RSA", ".DSA", ".MF"]):
                continue
            
            # Patch resources.arsc
            if item.filename == "resources.arsc":
                data = patch_resources_arsc(src.read(item.filename))
                dst.writestr(item, data)
            # Inject adaptive vectors
            elif item.filename in compiled_vectors:
                dst.writestr(item, compiled_vectors[item.filename])
            # Inject rendered brand assets
            elif item.filename in rendered_assets:
                dst.writestr(item, rendered_assets[item.filename])
            # Inject patched libchrome.so
            elif item.filename == "lib/arm64-v8a/libchrome.so":
                print("[+] Injected patched libchrome.so with libimerek.so dependency")
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

    aligned_apk = os.path.join(work_dir, "aligned.apk")
    print(f"[*] Running zipalign on package...")
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

    print(f"[*] Signing APK with Zenith release key...")
    subprocess.check_call([
        "apksigner", "sign",
        "--ks", keystore_path,
        "--ks-pass", "pass:zenith123",
        "--key-pass", "pass:zenith123",
        "--ks-key-alias", "zenith",
        "--out", output_apk,
        aligned_apk
    ])

    print(f"[*] Verifying final signature...")
    subprocess.check_call(["apksigner", "verify", "--verbose", output_apk])

    shutil.rmtree(work_dir, ignore_errors=True)
    print(f"\n[SUCCESS] Successfully built Zenith APK with Built-in UYAP Server: {output_apk} ({os.path.getsize(output_apk)} bytes)")

if __name__ == "__main__":
    src_apk = sys.argv[1] if len(sys.argv) > 1 else "/sdcard/Download/com.kiwibrowser.browser-arm64-14310011181-github.apk"
    dst_apk = sys.argv[2] if len(sys.argv) > 2 else "/sdcard/Download/ZenithBrowser-Android-arm64.apk"
    rebrand_apk(src_apk, dst_apk)
