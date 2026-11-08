#!/usr/bin/env bash
# Build the CEDAR icon pack APK (aapt2 pipeline, no Gradle).
# Adapted from the proven build-test-iconpack.sh approach.
set -euo pipefail

IPK="$HOME/Projects/cedar-iconpack"
SDK="${ANDROID_HOME:-$HOME/Android/Sdk}"
BT="$SDK/build-tools/35.0.0"
PLATFORM="$SDK/platforms/android-35/android.jar"
ADB="$SDK/platform-tools/adb"

mkdir -p "$IPK/build/classes"

cd "$IPK"
"$BT/aapt2" compile --dir res -o build/res.zip
"$BT/aapt2" link -I "$PLATFORM" --manifest AndroidManifest.xml \
  --min-sdk-version 24 --target-sdk-version 35 --version-code 1 --version-name 1.0 \
  -o build/iconpack-unsigned.apk build/res.zip

javac --release 11 -cp "$PLATFORM" -d build/classes src/org/cedar/iconpack/ThemeActivity.java
"$BT/d8" --output build build/classes/org/cedar/iconpack/*.class
(cd build && zip -q iconpack-unsigned.apk classes.dex)

"$BT/apksigner" sign --ks "$HOME/.android/debug.keystore" \
  --ks-pass pass:android --out build/cedar-iconpack.apk build/iconpack-unsigned.apk

echo "Built: $IPK/build/cedar-iconpack.apk"
if "$ADB" get-state >/dev/null 2>&1; then
  "$ADB" install -r build/cedar-iconpack.apk
  echo "Installed org.cedar.iconpack on $("$ADB" get-state)"
else
  echo "No device attached — APK built but not installed."
fi
