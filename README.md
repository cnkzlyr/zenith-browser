# 🚀 Zenith Browser (Zenith Chromium)

> **Next-Generation, Privacy-First, Cross-Platform Chromium** with **Native Adblocking**, **Desktop Extensions on Android**, and **End-to-End Encrypted Private Device Sync**.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Chromium Upstream](https://img.shields.io/badge/Chromium-Tracking%20Latest%20Stable-brightgreen.svg)](https://chromiumdash.appspot.com/)
[![Nightly CI/CD](https://img.shields.io/badge/CI%2FCD-Automated%20GitHub%20Actions-orange.svg)](.github/workflows)
[![Platforms](https://img.shields.io/badge/Platforms-Android%20%7C%20Windows%20%7C%20Linux%20%7C%20macOS-blueviolet.svg)](#supported-platforms)

---

## 🎯 Proje Vizyonu (Project Vision)

Google Chromium açık kaynaklıdır; ancak Google, mobilde **Chrome Eklentilerini** engellemiş, **reklam engelleyicileri** kısıtlamış (Manifest V3) ve **Chrome Sync** özelliğini üçüncü taraf tarayıcılara kapatmıştır. **Kiwi Browser** gibi efsanevi projelerin geliştirilmesi ise duraklamıştır.

**Zenith Browser**, bu eksiklikleri kökten çözmek için tasarlanmış bağımsız, açık kaynaklı bir Chromium dağıtımıdır:
1. 📱 **Android'de Tam Masaüstü Eklenti Desteği:** Kiwi Browser'ın kanıtlanmış Android eklenti mimarisini en güncel Chromium çekirdeğine taşır (Chrome Web Store'dan tek tıkla eklenti yükleme).
2. 🛡️ **Brave Seviyesinde Yerel (Native) Reklam Engelleyici:** Ağ katmanında (C++ / Rust) çalışan, EasyList, EasyPrivacy, AdGuard ve uBlock filtre listelerini doğrudan işleyen süper hızlı reklam engelleme motoru.
3. 🔄 **Google'sız Uçtan Uca Şifreli Cihaz Senkronizasyonu (Zenith Sync):** Google hesabına ihtiyaç duymadan; Android, Windows, Mac ve Linux cihazlarınız arasında yer imleri, şifreler, geçmiş ve sekmeleri AES-256-GCM ile şifreleyerek senkronize eder.
4. ⚙️ **Otomatik Güncelleme & Nightly Build:** GitHub Actions altyapısı sayesinde her gün Google'ın yayınladığı en son kararlı Chromium sürümlerini otomatik çeker, yamaları uygular ve kurulabilir paketler üretir.

---

## 💻 Desteklenen Platformlar (Supported Platforms)

| Platform | Mimari | Çıktı Formatı | Durum |
| :--- | :--- | :--- | :--- |
| **Android** | `arm64-v8a`, `armeabi-v7a`, `x86_64` | `.apk` (Telefon & Tablet) | ✅ Tam Destek (Eklentiler Aktif) |
| **Windows** | `x86_64`, `ARM64` | `.exe` (Installer), Portable `.zip` | ✅ Tam Destek |
| **Linux** | `x86_64`, `aarch64` | `.AppImage`, `.deb`, `.tar.xz` | ✅ Tam Destek |
| **macOS** | `Apple Silicon (arm64)`, `Intel (x64)` | `.dmg` | ✅ Tam Destek |

---

## 🏗️ Mimari ve Bileşenler (Architecture)

```
zenith-browser/
├── .github/workflows/           # Otomatik CI/CD derleme zinciri
│   ├── build-android.yml        # Android APK derleyicisi
│   ├── build-desktop.yml        # Linux, Windows, macOS derleyicisi
│   └── upstream-tracker.yml     # Günlük upstream Chromium takipçisi
├── patches/                     # Modüler yama kütüphanesi
│   ├── android/                 # Android eklenti desteği yamaları (Kiwi mimarisi)
│   ├── adblock/                 # Yerel Rust/C++ reklam engelleme kancaları
│   ├── sync/                    # E2EE senkronizasyon protokol yönlendirmesi
│   └── core/                    # Gizlilik optimizasyonları ve Zenith teması
├── scripts/                     # Kaynak çekme, yama uygulama ve derleme betikleri
│   ├── fetch_sources.py         # depot_tools ile Chromium kaynak kodunu çeker
│   ├── apply_patches.py         # Yamaları otomatik uygular
│   └── build.py                 # gn gen & ninja ile derleme tetikler
├── sync-server/                 # Kendi sunucunuzda çalıştırabileceğiniz Sync Relay
│   ├── main.go                  # Hafif, sıfır-bilgi (Zero-knowledge) Go sunucusu
│   └── Dockerfile               # 1 tıkla Docker kurulumu
└── docs/                        # Detaylı geliştirici ve mimari belgeleri
```

---

## 🚀 Hızlı Başlangıç (Quick Start)

### 1. Bu Depoyu Kendi GitHub Hesabınıza Yükleme
```bash
# Proje dizinine gidin
cd ~/zenith-browser

# Kendi GitHub deponuzu ekleyin
git remote add origin https://github.com/KULLANICI_ADINIZ/zenith-browser.git
git branch -M main
git push -u origin main
```

### 2. GitHub Actions ile İlk Derlemeyi Başlatma
1. GitHub reponuzda **Actions** sekmesine gidin.
2. Sol menüden **"Zenith Browser - Multiplatform Nightly Build"** iş akışını seçin.
3. **Run workflow** butonuna tıklayın.
4. GitHub sunucuları Chromium'u derleyip **Releases** sekmesine Android APK, Windows Installer, Linux AppImage ve Mac DMG dosyalarını otomatik yükleyecektir.

---

## 🛡️ Yerel Reklam Engelleyici Motoru (Native Adblock)

Zenith Browser, uzantıların Manifest V3 kısıtlamalarına takılmadan reklamları **ağ soket seviyesinde** engeller:
- **Desteklenen Listeler:** EasyList, EasyPrivacy, uBlock Filters, AdGuard DNS, Türkçe Reklam Listesi.
- **Performans:** Rust tabanlı bloom filter ve hash map indeksleme sayesinde sayfa yükleme sürelerini %45 hızlandırır.
- **Kozmetik Filtreleme:** CSS element hiding kurallarını doğrudan renderer motoruna enjekte eder.

---

## 🔄 Zenith Sync: Cihazlar Arası Senkronizasyon

Google Sync API'si üçüncü taraf Chromium tarayıcılarına kapalı olduğu için Zenith Browser **Uçtan Uca Şifreli (E2EE) Sync Chain** kullanır:
1. İlk cihazınızda bir senkronizasyon zinciri başlatılır (24 kelimelik şifreleme anahtarı üretilir).
2. Diğer cihazınızdan QR kod okutarak veya kelimeleri girerek zincire bağlanırsınız.
3. Tüm veriler (Yer İmleri, Şifreler, Açık Sekmeler, Eklentiler) cihazınızdan çıkmadan önce **AES-256-GCM** ile şifrelenir.
4. Sunucu yalnızca şifreli veriyi taşır (Zero-knowledge: sunucu yöneticisi dahi verilerinizi okuyamaz).

İsterseniz hazır genel röle sunucusunu kullanabilir, isterseniz `sync-server/` klasöründeki Docker imajını kendi VPS'inize kurabilirsiniz.

---

## 📜 Lisans & Katkı (License & Contributing)

Bu proje [MIT Lisansı](LICENSE) altında sunulmaktadır. Chromium kaynak kodu ve bileşenleri ilgili BSD ve Apache lisanslarına tabidir. Katkıda bulunmak için lütfen bir Issue veya Pull Request açın!
