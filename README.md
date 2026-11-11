# CEDAR Icons (`org.cedar.iconpack`)

An installable Android icon pack that re-skins apps in CEDAR's visual language.
Works with the CEDAR launcher (Kvaesitso fork) and any launcher that reads ADW
`appfilter.xml` packs.

**252 icons** — 244 app glyphs derived from [Arcticons](https://github.com/Arcticons-Team/Arcticons)
plus 8 CEDAR-original glyphs.

On the owner's phone (303 launchable components) this covers **262 apps**; the
41 without upstream art are listed by `tools/audit_device.py` for hand-drawing.

## Visual language

| Element | Value |
| --- | --- |
| Plate | forest-dark `#1A231D`, 45° chamfered corners (24 px at 192 px) |
| Hairline | dim sage `#4E6B58` @ 31%, inset 8 px, following the chamfer |
| Glyph | sage `#7BA88A`, 48×48 line art, stroke 1.25, 108/192 glyph box |
| Output | 192×192 PNG, 4× supersampled then LANCZOS-downsampled |

The glyph box matches the v1 pack's proportions (84–116 px glyphs inside a
192 px tile), so the new line-art icons sit at the same visual weight as the
original bold glyphs.

## Two glyph sources

1. **Arcticons** (GPL-3.0) — 15,476 monochrome line icons covering the long tail
   of Android apps. Referenced in `icons.json` by upstream icon name, e.g.
   `"arcticons": "google_phone"`.
2. **CEDAR originals** in `custom/` — hand-drawn on the same 48×48 grid:
   `cedar`, `strata`, `fieldstation`, `trailwatch`, `weather`, `vault`, `notes`,
   `tasks`.

Modifications to Arcticons glyphs: recolour `#000` → `#7BA88A`, normalise stroke
width to 1.25, composite on the CEDAR plate. See `NOTICE` for attribution and
the GPL-3.0 terms.

## Manifest discovery

`ThemeActivity` declares `org.adw.launcher.themes`, `org.adw.launcher.iconpack`,
`org.adw.launcher.THEMES` (uppercase — this is the action the CEDAR launcher's
`AppFilterIconPackInstaller` queries), `org.adw.ActivityStarter.THEMES`,
`com.novalauncher.THEME` and `app.lawnchair.icons.THEMED_ICON`, all **with
`android.intent.category.DEFAULT`**. Without CATEGORY_DEFAULT launchers will not
discover the pack.

## Layout

```
icons.json               # source of truth: drawable -> glyph + explicit components
custom/                  # CEDAR-original 48x48 SVGs
tools/render_icons.py    # render plates + contact sheet
tools/gen_appfilter.py   # build res/xml/appfilter.xml
data/legacy-appfilter.xml# v1 hand-maintained mappings (still fed into the build)
res/drawable-nodpi/      # generated ic_*.png
res/xml/appfilter.xml    # generated
build.sh                 # aapt2 -> javac -> d8 -> apksigner -> adb install
```

## Add an icon

1. Add an entry to `icons.json`:

```json
{"drawable": "ic_linear", "label": "Linear", "arcticons": "linear"}
```

`arcticons` must match a file in the Arcticons checkout (`icons/black/<name>.svg`).
For a custom glyph use `"custom": "linear.svg"` and drop the file in `custom/`.

2. Render and regenerate the mapping:

```sh
python3 tools/render_icons.py      # PNGs + docs/contact-sheet-v2.png
python3 tools/gen_appfilter.py     # res/xml/appfilter.xml
```

3. **Bump `version_name` in `build.sh` and `icons.json`** (see gotcha below), then:

```sh
./build.sh                         # builds, signs, installs if a device is attached
```

The appfilter is built in three layers: explicit `components` in `icons.json`,
then `data/legacy-appfilter.xml`, then every Arcticons component that maps to a
glyph we ship. That third layer is where most of the coverage comes from —
Arcticons has 51k verified package/activity pairs.

## Cover a real phone

```sh
python3 tools/audit_device.py -s <host:port> --json /tmp/phone.json   # what's uncovered
python3 tools/expand_from_device.py /tmp/phone.json                   # add every Arcticons-covered app
python3 tools/render_icons.py && python3 tools/gen_appfilter.py
```

`audit_device.py` resolves every LAUNCHER component (all profiles) against the
built appfilter. `expand_from_device.py` looks each uncovered component up in
Arcticons — exact activity first, then any activity of the same package — and
merges new entries into `icons.json`. Components that map to a concept CEDAR
already ships (phone, contacts, files, calendar, weather, notes, translate) are
appended to that icon instead of creating a near-duplicate. Whatever remains has
no upstream art and genuinely needs drawing.

## Build requirements

No Gradle. Needs:

- `$HOME/Android/Sdk` with build-tools 35.0.0 and platform android-35
- JDK 17+ (`javac`, `d8`)
- `~/.android/debug.keystore`
- `rsvg-convert` (librsvg) and Pillow — only to regenerate icons; the rendered
  PNGs are committed, so a plain clone builds the APK without them
- an Arcticons checkout at `~/Projects/arcticons-source` (only to regenerate
  icons): `git clone --depth 1 --filter=blob:none --sparse`, then
  `git sparse-checkout set icons app/src/main/res/xml`

## Gotcha: launcher re-ingest is keyed on versionName

The CEDAR launcher decides whether to re-parse a pack with
`installed.version == iconPack.version`, and `IconPack.version` is the pack's
**versionName**, not versionCode. Rebuild with the same versionName and the new
appfilter is silently ignored (`Icon pack ... is up to date` in logcat), leaving
stale or stock icons. Bump `version_name` on every content change.

Forcing a re-ingest without a bump: `adb uninstall org.cedar.iconpack` then
reinstall.

## Verification (emulator-5554, 2026-11-11)

- `adb install -r build/cedar-iconpack.apk` → logcat:
  `Icon pack org.cedar.iconpack has been installed successfully`
- Settings → Grid and icons → Icon pack → **CEDAR Icons**; persisted as
  `iconsPack: "org.cedar.iconpack"` in the launcher datastore.
- **22/22** launchable components on the emulator resolve to a themed drawable
  (checked against `cmd package query-activities`).
- Drawer screenshots show every app on a dark chamfered plate with sage line art.

## Evidence

- `docs/contact-sheet-v2.png` — all 47 rendered icons with labels
- `docs/icon-contact-sheet.png`, `docs/drawer-before.png` — v1 captures

## License

GPL-3.0-or-later. Glyph artwork derived from Arcticons (GPL-3.0); see `NOTICE`.
