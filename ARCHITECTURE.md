# 🏛️ Zenith Browser Architecture & Engineering Guide

This document details the internal systems, patch strategies, and build pipeline of **Zenith Browser**.

---

## 1. Android Extension Architecture (Kiwi Engine Port)

In standard Chromium for Android:
- `enable_extensions = false` is enforced in `src/build/config/features.gni`.
- Extension UI bindings (dialogs, toolbars, popup bubbles) only exist in `chrome/browser/ui/views/` (desktop views).
- Mobile Android UI lives in `chrome/android/java/src/org/chromium/chrome/browser/`.

### Zenith's Extension Subsystem:
```
+-------------------------------------------------------------+
|               Chromium Android UI Layer                     |
|  (Toolbar -> 3-dots Menu -> "Extensions" Tab & Badges)      |
+-------------------------------------------------------------+
                              | JNI Bridge
+-----------------------------v-------------------------------+
|      Zenith Android Extension Controller (C++ / Java)       |
|  - ExtensionActionMenu.java     - ExtensionHostView.java    |
|  - ExtensionPopupDialog.java    - ExtensionNavigation.java  |
+-------------------------------------------------------------+
                              |
+-----------------------------v-------------------------------+
|       Chromium Native Extension System (C++ Core)           |
|  - src/extensions/browser/      - src/extensions/common/    |
|  - ExtensionRegistry            - ExtensionService          |
|  - WebAccessibleResources       - ContentScriptEngine       |
+-------------------------------------------------------------+
```

### Key Technical Patches:
1. **`enable_extensions = true`**: Re-enabled for Android target builds in `args.gn`.
2. **JNI Window Integration**: Custom Java view `ExtensionHostView` wraps the WebContents of the extension popup into an Android `BottomSheetDialogFragment`.
3. **Chrome Web Store Interception**: When browsing `chromewebstore.google.com`, Zenith automatically sends desktop Chromium headers (`User-Agent: Windows NT 10.0; Win64; x64`) and hooks the "Add to Chrome" button, routing the `.crx` stream to `ExtensionInstallPrompt`.

---

## 2. Brave-Grade Native Adblocking Engine

Instead of relying on slow JavaScript extensions or restrictive Manifest V3 `declarativeNetRequest` limits (30k rules), Zenith embeds a native Rust-powered matching engine:

```
[Web Page Request] ---> [network::ResourceRequest]
                              |
                     [Zenith Network Filter Hook]
                              |
            +-----------------v-----------------+
            |   Native Rust Adblock Engine      |
            |   (libadblock_ffi / Fast C-ABI)   |
            |                                   |
            |  - Hash-indexed Rule Trees        |
            |  - Substring Bloom Filters        |
            |  - Regex Matching (Fast Engine)   |
            +-----------------+-----------------+
                              |
               +--------------+--------------+
               |                             |
          [MATCH: BLOCK]               [NO MATCH: ALLOW]
               |                             |
      Cancel Request (net::ERR_BLOCKED)    Continue to Remote Server
```

### Supported Filter Formats:
- Standard Adblock Plus / uBlock Origin syntax
- Element Hiding (`##.ad-banner`, `###sponsored`)
- Scriptlet Injection (`##+js(set, ads, false)`)
- Dynamic rule updates via background worker checking filter URLs every 24h.

---

## 3. Zenith Sync: End-to-End Encrypted (E2EE) Sync Chain

Google disabled private Chromium sync keys, cutting off third-party browsers from Chrome Sync. Zenith implements a decentralized, zero-knowledge sync protocol:

```
[Device A (Android)]                                     [Device B (PC / Mac)]
        |                                                          |
  1. Generate 24-word Seed                                         |
     (PBKDF2 Key Derivation)                                       |
        |                                                          |
  2. Local Encrypt (AES-256-GCM)                                   |
     Payload: Bookmarks, Passwords, History                        |
        |                                                          |
        +------------> [Zenith Sync Relay Server] <----------------+
                             (Zero Knowledge)              3. Enter Seed / Scan QR
                             Only stores:                  4. Fetch Encrypted Blobs
                             - user_id_hash                5. Local Decrypt with Key
                             - encrypted_blob              6. Merge into Chromium DB
                             - version & timestamp
```

### Security Properties:
- **Zero Knowledge:** The relay server only stores ciphertext. Even if the server is compromised, no browsing data, bookmarks, or passwords can be decrypted.
- **Self-Hostable:** The server is a single Go binary (`sync-server/main.go`) or Docker container with minimal RAM usage (<20MB).

---

## 4. GitHub Actions Multi-Platform Build Pipeline

Chromium is notoriously resource-heavy (~40GB checkout, 4-6 hours build). Zenith solves this on GitHub Actions by:

1. **Shallow Tag Fetching:** Only fetching the specific release tag rather than the full git history (`--depth 1`).
2. **Artifact Splitting & Matrix Builds:**
   - Linux: Ubuntu 22.04 runner
   - Android: Ubuntu runner with Android NDK r26d
   - Windows: Windows Server 2022 runner with MSVC v143
   - macOS: macOS 14 runner with Xcode 15
3. **Ccache & Sccache Integration:** Shared GitHub Actions Cache for intermediate object files, cutting incremental build times from 4 hours to 45 minutes.
4. **Nightly Automated Releases:** The workflow automatically drafts a GitHub Release tagged `nightly-YYYYMMDD`, attaches all binaries, generates SHA256 checksums, and updates `updates.json` for in-app auto-updates.
