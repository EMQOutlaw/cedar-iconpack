#!/usr/bin/env bash
# Build the CEDAR icon pack APK (aapt2 pipeline, no Gradle).
#
#   ./build.sh               build, sign, install if a device is attached
#   ./build.sh --build-only  build + sign, never touch a device
#
# Works from any clone: the repo root is derived from this script's location.
set -euo pipefail

IPK="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SDK="${ANDROID_HOME:-$HOME/Android/Sdk}"
BT="$SDK/build-tools/35.0.0"
PLATFORM="$SDK/platforms/android-35/android.jar"
ADB="$SDK/platform-tools/adb"

VERSION_CODE=5
VERSION_NAME=3.1

BUILD_ONLY=0
[ "${1:-}" = "--build-only" ] && BUILD_ONLY=1

mkdir -p "$IPK/build/classes"
cd "$IPK"

"$BT/aapt2" compile --dir res -o build/res.zip
"$BT/aapt2" link -I "$PLATFORM" --manifest AndroidManifest.xml \
  --min-sdk-version 24 --target-sdk-version 35 \
  --version-code "$VERSION_CODE" --version-name "$VERSION_NAME" \
  -o build/iconpack-unsigned.apk build/res.zip

javac --release 11 -cp "$PLATFORM" -d build/classes src/org/cedar/iconpack/ThemeActivity.java
"$BT/d8" --output build build/classes/org/cedar/iconpack/*.class
(cd build && zip -q iconpack-unsigned.apk classes.dex)

"$BT/apksigner" sign --ks "$HOME/.android/debug.keystore" \
  --ks-pass pass:android --out build/cedar-iconpack.apk build/iconpack-unsigned.apk

echo "Built: $IPK/build/cedar-iconpack.apk"

if [ "$BUILD_ONLY" = "1" ]; then
  exit 0
fi

if [ -n "${ANDROID_SERIAL:-}" ]; then
  "$ADB" -s "$ANDROID_SERIAL" install -r build/cedar-iconpack.apk
  echo "Installed org.cedar.iconpack on $ANDROID_SERIAL"
elif [ "$("$ADB" devices | awk '$2=="device"' | wc -l)" = "1" ]; then
  "$ADB" install -r build/cedar-iconpack.apk
  echo "Installed org.cedar.iconpack on the only connected device"
else
  echo "No single device attached — APK built but not installed."
  echo "Set ANDROID_SERIAL=<serial> (see: adb devices) to install on a specific one."
fi
