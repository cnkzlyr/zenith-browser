#!/usr/bin/env python3
"""
Zenith Browser - Android Branding & Resource Injection Engine
Injects custom Zenith Browser branding, adaptive vector icons, 
and application strings into the upstream mobile extension engine.
"""

import os
import sys
import math
import shutil
import zipfile
import subprocess
from PIL import Image, ImageDraw

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
    for i in range(8):
        step_r = r - (i * (size * 0.02))
        alpha = int(25 + i * 15)
        box = [center - step_r, center - step_r, center + step_r, center + step_r]
        draw.ellipse(box, outline=(18, 30, 52, alpha), width=max(1, int(size * 0.01)))

    # Outer neon cyan ring
    draw.ellipse([center - r*0.92, center - r*0.92, center + r*0.92, center + r*0.92], 
                 outline=(0, 242, 254, 220), width=max(2, int(size * 0.025)))

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
        print("[!] Warning: Exact length target not matched in resources.arsc, searching raw string...")
        raw_pos = arsc.find(b"Kiwi Browser")
        if raw_pos != -1:
            arsc[raw_pos : raw_pos + 6] = b"Zenith"
    return bytes(arsc)

def rebrand_apk(input_apk, output_apk, keystore_path="zenith.keystore"):
    print(f"\n=======================================================")
    print(f" Zenith Browser - Rebranding APK: {input_apk}")
    print(f"=======================================================")
    
    work_dir = os.path.join(os.path.dirname(output_apk), "zenith_rebrand_tmp")
    shutil.rmtree(work_dir, ignore_errors=True)
    os.makedirs(work_dir, exist_ok=True)

    print("[*] Compiling Zenith adaptive vector drawables...")
    compiled_vectors = compile_vector_drawables(work_dir)

    print("[*] Generating Zenith mipmap raster icons...")
    densities = {
        "mipmap-mdpi-v4": 48,
        "mipmap-hdpi-v4": 72,
        "mipmap-xhdpi-v4": 96,
        "mipmap-xxhdpi-v4": 144,
        "mipmap-xxxhdpi-v4": 192,
    }
    rendered_mipmaps = {}
    for folder, px in densities.items():
        reg_img = render_zenith_icon(px, is_round=False)
        rnd_img = render_zenith_icon(px, is_round=True)
        reg_path = os.path.join(work_dir, f"{folder}_reg.webp")
        rnd_path = os.path.join(work_dir, f"{folder}_rnd.webp")
        reg_img.save(reg_path, format="WEBP", lossless=True)
        rnd_img.save(rnd_path, format="WEBP", lossless=True)
        with open(reg_path, "rb") as f:
            rendered_mipmaps[f"res/{folder}/ic_launcher"] = f.read()
        with open(rnd_path, "rb") as f:
            rendered_mipmaps[f"res/{folder}/ic_launcher_round"] = f.read()

    unaligned_apk = os.path.join(work_dir, "unaligned.apk")
    print(f"[*] Repackaging APK to {unaligned_apk}...")
    with zipfile.ZipFile(input_apk, "r") as src, zipfile.ZipFile(unaligned_apk, "w", compression=zipfile.ZIP_DEFLATED) as dst:
        for item in src.infolist():
            # Strip old Kiwi signature
            if item.filename.startswith("META-INF/") and any(item.filename.endswith(ext) for ext in [".SF", ".RSA", ".DSA", ".MF"]):
                continue
            
            # Patch resources.arsc
            if item.filename == "resources.arsc":
                data = patch_resources_arsc(src.read(item.filename))
                dst.writestr(item, data)
            # Replace adaptive vector drawables
            elif item.filename in compiled_vectors:
                print(f"[+] Injected vector: {item.filename}")
                dst.writestr(item, compiled_vectors[item.filename])
            # Replace bitmap mipmaps
            elif item.filename in rendered_mipmaps:
                print(f"[+] Injected mipmap: {item.filename}")
                dst.writestr(item, rendered_mipmaps[item.filename])
            # Clear Kiwi gradient parts
            elif item.filename in ["res/drawable/$ic_launcher_background__0.xml",
                                   "res/drawable/$ic_launcher_foreground__0.xml",
                                   "res/drawable/$ic_launcher_foreground__1.xml"]:
                # Empty dummy vector to preserve resource indices without loading Kiwi graphics
                dummy_xml = b'<vector xmlns:android="http://schemas.android.com/apk/res/android" android:width="1dp" android:height="1dp" android:viewportWidth="1" android:viewportHeight="1"/>'
                dst.writestr(item, dummy_xml)
            else:
                dst.writestr(item, src.read(item.filename))

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

    # Clean up
    shutil.rmtree(work_dir, ignore_errors=True)
    print(f"\n[SUCCESS] Successfully built branded Zenith APK: {output_apk} ({os.path.getsize(output_apk)} bytes)")

if __name__ == "__main__":
    src_apk = sys.argv[1] if len(sys.argv) > 1 else "kiwi_next_arm64.apk"
    dst_apk = sys.argv[2] if len(sys.argv) > 2 else "ZenithBrowser-Android-arm64.apk"
    rebrand_apk(src_apk, dst_apk)
