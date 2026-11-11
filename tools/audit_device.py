#!/usr/bin/env python3
"""Audit a connected device against the CEDAR icon pack's appfilter.

Enumerates every LAUNCHER activity (all profiles) on the device, resolves each
component against res/xml/appfilter.xml, and reports which apps would still show
their stock icon.

Usage:
  python3 tools/audit_device.py              # auto-pick the only device
  python3 tools/audit_device.py -s <serial>
  python3 tools/audit_device.py --json out.json
"""
import argparse
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ADB = os.environ.get("ADB", os.path.expanduser("~/Android/Sdk/platform-tools/adb"))


def adb(serial, *args):
    cmd = [ADB] + (["-s", serial] if serial else []) + list(args)
    return subprocess.run(cmd, capture_output=True, text=True).stdout


def devices():
    out = subprocess.run([ADB, "devices"], capture_output=True, text=True).stdout
    return [line.split("\t")[0] for line in out.splitlines()[1:] if "\tdevice" in line]


def launchables(serial):
    out = adb(serial, "shell", "cmd", "package", "query-activities",
              "-a", "android.intent.action.MAIN",
              "-c", "android.intent.category.LAUNCHER")
    comps = []
    for block in out.split("Activity #")[1:]:
        name = re.search(r"^\s+name=(\S+)", block, re.M)
        pkg = re.search(r"^\s+packageName=(\S+)", block, re.M)
        if name and pkg:
            comps.append("%s/%s" % (pkg.group(1), name.group(1)))
    return sorted(set(comps))


def mapped(path):
    with open(path, encoding="utf-8") as fh:
        return {m.group(1) for m in re.finditer(r"ComponentInfo\{([^}]+)\}", fh.read())}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-s", "--serial")
    ap.add_argument("--json")
    args = ap.parse_args()

    serial = args.serial
    if not serial:
        ds = devices()
        if len(ds) != 1:
            print("devices: %s — pass -s <serial>" % (ds or "none"), file=sys.stderr)
            sys.exit(1)
        serial = ds[0]

    model = adb(serial, "shell", "getprop", "ro.product.model").strip()
    comps = launchables(serial)
    have = mapped(os.path.join(ROOT, "res", "xml", "appfilter.xml"))

    covered = [c for c in comps if c in have]
    missing = [c for c in comps if c not in have]

    # collapse multiple launcher activities of one package into one missing entry
    miss_pkgs = {}
    for c in missing:
        pkg, act = c.split("/", 1)
        miss_pkgs.setdefault(pkg, []).append(act)

    print("device: %s (%s)" % (serial, model))
    print("launchable components: %d" % len(comps))
    print("themed:  %d" % len(covered))
    print("missing: %d across %d packages" % (len(missing), len(miss_pkgs)))
    print()
    for pkg in sorted(miss_pkgs):
        print("  %-45s %s" % (pkg, ", ".join(miss_pkgs[pkg])))

    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump({"serial": serial, "model": model,
                       "covered": covered, "missing": missing}, fh, indent=2)
        print("\nwrote %s" % args.json)


if __name__ == "__main__":
    main()
