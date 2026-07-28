# Exercises the running server (start it first: python server.py --no-browser).
import base64
import json
import urllib.request

import _smoke as s
import fontlib

BASE = "http://127.0.0.1:8765"


def post(path, obj):
    data = json.dumps(obj).encode("utf-8")
    req = urllib.request.Request(BASE + path, data=data,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def main():
    main_bytes = s.build_main()
    main_bytes = s.to_post3(main_bytes)   # regression: format-3 post source
    patch_bytes = s.build_patch()

    with urllib.request.urlopen(BASE + "/", timeout=10) as r:
        html = r.read().decode("utf-8")
    assert "TTF" in html, "index page did not load"
    print("GET / OK")

    j = post("/api/analyze", {"data": base64.b64encode(main_bytes).decode(), "filename": "main.ttf"})
    assert j["ok"], j
    main_token = j["token"]
    print("analyze OK:", j["name"], "| blocks", len(j["blocks"]), "| covered", j["coveredBlocks"])

    j = post("/api/patch", {"data": base64.b64encode(patch_bytes).decode(),
                            "filename": "patch.ttf", "mainToken": main_token})
    assert j["ok"], j
    patch_token = j["token"]
    print("patch OK | fillable", j["fillable"], "| supply", j["supply"])

    blocks = ["Greek and Coptic", "Cyrillic", "CJK Unified Ideographs", "Mathematical Operators"]
    j = post("/api/merge", {"mainToken": main_token, "patchToken": patch_token, "blocks": blocks})
    assert j["ok"], j
    merged = base64.b64decode(j["data"])
    print("merge OK | cps", j["mergedCodepoints"], "| glyphs", j["mergedGlyphs"], "| file", j["filename"])

    m = fontlib.load_font(merged)
    cmap = fontlib.cmap_of(m)
    assert 0x391 in cmap and 0x410 in cmap and 0x4E2D in cmap and 0x2200 in cmap, "merged font missing codepoints"
    assert len(merged) > 1000, "merged font suspiciously small"
    print("HTTP SMOKE PASSED | merged size", len(merged), "bytes")


if __name__ == "__main__":
    main()
