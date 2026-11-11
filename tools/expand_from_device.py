#!/usr/bin/env python3
"""Expand icons.json to cover every app on a device that Arcticons already draws.

Reads tools/audit_device.py --json output, resolves each uncovered component
against the Arcticons appfilter (exact component first, then same package), and
merges new icon entries into icons.json.

Components that map to a glyph CEDAR already ships (phone, contacts, weather,
notes, ...) are appended to that entry instead of creating a near-duplicate.

Usage:
  python3 tools/audit_device.py -s <serial> --json /tmp/phone.json
  python3 tools/expand_from_device.py /tmp/phone.json [--dry-run]
"""
import argparse
import collections
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARCTICONS_APPFILTER = os.environ.get(
    "ARCTICONS_APPFILTER",
    os.path.expanduser("~/Projects/arcticons-source/app/src/main/res/xml/appfilter.xml"),
)

# upstream drawable -> CEDAR drawable we already ship (same concept, better art)
REUSE = {
    "phone": "ic_phone",
    "contacts": "ic_contacts",
    "messages": "ic_messages",
    "clock": "ic_clock",
    "camera": "ic_camera",
    "settings": "ic_settings",
    "documents": "ic_files",
    "calendar": "ic_calendar",
    "weather": "ic_weather",
    "notes": "ic_notes",
    "translate": "ic_translate",
}

LABELS = {
    "kwgt": "KWGT", "kwgt_pro": "KWGT Pro", "kwgt_generic_app": "KWGT Widget",
    "kfc": "KFC", "dji": "DJI", "ups": "UPS", "usps_mobile": "USPS",
    "ps_app": "PS App", "ir_remote": "IR Remote", "muviz_edge": "Muviz Edge",
    "fdroid": "F-Droid", "ddbplayer": "DDB Player", "okta_verify": "Okta Verify",
    "ohealth": "OHealth", "my_oppo": "My OPPO", "my_verizon": "My Verizon",
    "google_find_device": "Find Device", "google_one": "Google One",
    "google_tv": "Google TV", "google_meet": "Meet", "google_lens": "Google Lens",
    "google_home": "Google Home", "amazon_prime_video": "Prime Video",
    "amazon_shopping": "Amazon", "amazon_store_card": "Amazon Store Card",
    "advance_auto_parts": "Advance Auto Parts", "calc_you": "Calculator",
    "arcticons": "Arcticons", "arcticons_material_you": "Arcticons Material You",
    "nothing_icons": "Nothing Icons", "nothing_icon_pack": "Nothing Icon Pack",
    "bank_1": "Bank", "one": "One", "home_assistant": "Home Assistant",
    "openai_chatgpt": "ChatGPT", "instagram_threads": "Threads",
    "team_fight_tactics": "Teamfight Tactics", "govee_home": "Govee Home",
    "renpho_health": "Renpho Health", "sony_sound_connect": "Sony Sound Connect",
    "proton_authenticator": "Proton Authenticator", "proton_calendar": "Proton Calendar",
    "proton_drive": "Proton Drive", "proton_lumo": "Proton Lumo",
    "proton_mail": "Proton Mail", "proton_meet": "Proton Meet",
    "proton_pass": "Proton Pass", "proton_vpn": "Proton VPN",
    "slimsocial": "SlimSocial", "smartlauncher": "Smart Launcher",
    "niagara_launcher": "Niagara Launcher", "nova_launcher": "Nova Launcher",
    "smartwatch": "Smartwatch", "icon_pack": "Icon Pack", "icon_pack_studio": "Icon Pack Studio",
    "theme_store": "Theme Store", "widget": "Widget", "folder": "Folder",
    "games": "Games", "game_center": "Game Center", "keyboard": "Keyboard",
    "mediaplayer": "Media Player", "photo_roulette": "Photo Roulette",
    "currency_dollar": "Currency", "letter_lowercase_square_e": "App",
    "local send": "LocalSend", "localsend": "LocalSend",
}


def load_arcticons():
    with open(ARCTICONS_APPFILTER, encoding="utf-8") as fh:
        items = re.findall(
            r'<item component="ComponentInfo\{([^/}]+)/([^}]+)\}" drawable="([^"]+)"',
            fh.read(),
        )
    comp2d = {"%s/%s" % (p, a): d for p, a, d in items}
    pkg2d = collections.defaultdict(collections.Counter)
    for p, _a, d in items:
        pkg2d[p][d] += 1
    return comp2d, pkg2d


def label_for(drawable):
    if drawable in LABELS:
        return LABELS[drawable]
    return " ".join(w.capitalize() for w in drawable.split("_"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("audit")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    with open(args.audit, encoding="utf-8") as fh:
        audit = json.load(fh)
    with open(os.path.join(ROOT, "icons.json"), encoding="utf-8") as fh:
        spec = json.load(fh)

    comp2d, pkg2d = load_arcticons()
    existing = {i["drawable"] for i in spec["icons"]}
    by_arct = {i["arcticons"]: i for i in spec["icons"] if "arcticons" in i}
    by_drawable = {i["drawable"]: i for i in spec["icons"]}

    added = collections.OrderedDict()
    reused = collections.Counter()
    unknown = []

    for comp in audit["missing"]:
        pkg = comp.split("/")[0]
        upstream = comp2d.get(comp)
        if not upstream and pkg2d.get(pkg):
            upstream = pkg2d[pkg].most_common(1)[0][0]
        if not upstream:
            unknown.append(pkg)
            continue

        target = REUSE.get(upstream)
        if upstream in by_arct:
            target = by_arct[upstream]["drawable"]
        if target:
            entry = by_drawable[target]
            comps = entry.setdefault("components", [])
            if comp not in comps:
                comps.append(comp)
            reused[target] += 1
            continue

        drawable = "ic_" + upstream
        if drawable in existing:
            continue
        added.setdefault(upstream, {"drawable": drawable, "label": label_for(upstream),
                                    "arcticons": upstream})
        existing.add(drawable)

    print("new icons: %d" % len(added))
    print("components folded into existing icons: %d across %d icons"
          % (sum(reused.values()), len(reused)))
    print("no upstream art: %d" % len(set(unknown)))

    if args.dry_run:
        for d in added:
            print("  +", d)
        return

    spec["icons"].extend(added.values())
    # the nightly launcher is CEDAR too
    for icon in spec["icons"]:
        if icon["drawable"] == "ic_cedar":
            comps = icon.setdefault("components", [])
            nightly = "org.cedar.launcher.nightly/de.mm20.launcher2.ui.launcher.LauncherActivity"
            if nightly not in comps:
                comps.append(nightly)

    with open(os.path.join(ROOT, "icons.json"), "w", encoding="utf-8") as fh:
        json.dump(spec, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    print("wrote icons.json: %d icons total" % len(spec["icons"]))


if __name__ == "__main__":
    main()
