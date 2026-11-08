# CEDAR Icon Pack (`org.cedar.iconpack`)

An installable Android icon pack that themes common app icons in CEDAR's visual
language, for use with the CEDAR launcher (Kvaesitso fork).

## Visual language
- **Plate:** forest-dark `#1A231D`, chamfered (45°-cut) corners, subtle dim-sage hairline
- **Primary glyph:** sage `#7BA88A` geometric shapes
- **Secondary strokes:** dim sage `#4E6B58`
- 192×192 PNGs in `res/drawable-nodpi/`, drawn at 4× supersampling by
  `generate_icons.py` (PIL)

## Coverage — 30 app icons + pack icon
Phone, Messages, Chrome, Camera, Clock, Contacts, Files, Gmail, Google, Maps,
Photos, Settings, YouTube, Calendar, Drive, Play Store, Calculator, WhatsApp,
Telegram, Spotify, Gmail (alt), Keep, Translate, Drive (alt), Wallet,
Photos (alt), YT Music, Podcasts, Home, Recorder — plus the CEDAR evergreen
pack icon (`ic_pack`, also the APK launcher icon).

## Manifest discovery
The `ThemeActivity` declares both `org.adw.launcher.themes` and
`org.adw.launcher.iconpack` (plus `org.adw.launcher.THEMES`,
`org.adw.ActivityStarter.THEMES`, `com.novalauncher.THEME`,
`app.lawnchair.icons.THEMED_ICON`) **with `android.intent.category.DEFAULT`** —
without CATEGORY_DEFAULT launchers will not discover the pack (known pitfall).
The uppercase `org.adw.launcher.THEMES` variant matters: the CEDAR launcher's
`AppFilterIconPackInstaller` queries it (intent actions are case-sensitive).

## appfilter.xml
ADW format `ComponentInfo{package/Activity} → drawable`. Components for apps
installed on the emulator were read from
`adb shell cmd package query-activities -a android.intent.action.MAIN -c android.intent.category.LAUNCHER`.
Apps not installed locally use well-known stable components (see file comments).

## Build
```sh
./build.sh        # aapt2 compile+link → javac → d8 → zip → apksigner → adb install -r
```
No Gradle. Needs `$HOME/Android/Sdk` (build-tools 35.0.0, platform android-35)
and `~/.android/debug.keystore`. Output: `build/cedar-iconpack.apk`.

## End-to-end verification (emulator-5554, 2026-11-08)
1. Install → CEDAR launcher auto-discovers the pack via PACKAGE_ADDED
   (logcat: `Icon pack org.cedar.iconpack has been installed successfully`).
2. Settings → Grid and icons → Icon pack → sheet lists **System** and
   **CEDAR Icons** (live previews rendered from the pack) → select CEDAR Icons.
3. Persisted setting: `iconsPack: "org.cedar.iconpack"` (settings.json).
4. Drawer icons of all 16 sampled installed/covered apps switched from stock
   color icons to dark forest plates with sage glyphs — verified by
   before/after tile pixel-diff (~44% changed pixels, sage glyph pixels appear
   where before ≈ 0): Calendar, Camera, Chrome, Clock, Contacts, Drive, Files,
   Gmail, Google, Maps, Messages, Phone, Photos, Settings, YouTube, YT Music.
   (Google's tile is partly covered by a floating voice-input overlay in both
   screenshots; the themed plate is visible behind it.)
5. Round-trip: switching back to System restores stock icons; re-selecting
   CEDAR Icons re-applies the pack. No launcher restart was required.

## Evidence (`docs/`)
- `icon-contact-sheet.png` — all 31 generated icons
- `drawer-before.png` / `drawer-before-dump.xml` — System pack (stock icons)
- `drawer-after.png` / `drawer-after-dump.xml` — CEDAR pack applied
- `picker-sheet.png` — icon pack picker listing System + CEDAR Icons
- `picker-sheet-selected.png`, `picker-sheet-dump.xml` — Icon pack row now reads "CEDAR Icons"
- `verification-tiles-before-after.png` — 16 before/after tile pairs
- `tiles/*.png` — per-app before/after crops
- `home-after.png` — home screen with pack applied

## Not verified on device (apps not installed / no launcher activity)
Play Store (`com.android.vending/...AssetBrowserActivity` — installed but has
no LAUNCHER activity on this image), Calculator, WhatsApp, Telegram, Spotify,
Keep, Translate, Wallet, Podcasts, Recorder, and the "alternate" activities
GmailActivity / DocsActivity / PhotosActivity. Their appfilter entries use
well-known component names and will resolve on devices that ship them.

## Reproduce the full CEDAR environment
On a fresh Linux machine, the launcher repo's bootstrap script sets up
everything (Android SDK, AVD, both repos, builds, emulator):

    git clone https://github.com/EMQOutlaw/cedar-launcher.git
    ./cedar-launcher/scripts/cedar-env-setup.sh --launch

