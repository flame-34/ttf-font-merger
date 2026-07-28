# End-to-end logic test for fontlib (no server needed).
# Builds two synthetic TTF fonts and checks analyze / supply / merge.
import io
import fontlib  # also puts bundled libs/ on sys.path
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.ttGlyphPen import TTGlyphPen

def _box():
    pen = TTGlyphPen(None)
    pen.moveTo((100, 0))
    pen.lineTo((500, 0))
    pen.lineTo((500, 700))
    pen.lineTo((100, 700))
    pen.closePath()
    return pen.glyph()


def _empty():
    return TTGlyphPen(None).glyph()


def build_font(family, glyph_names, cmap, composite_for=None):
    """Build a minimal TrueType font.
    composite_for: optional (name, base_name) to make `name` a composite of base.
    """
    fb = FontBuilder(1000, isTTF=True)
    fb.setupGlyphOrder(glyph_names)
    fb.setupCharacterMap(cmap)
    comp_name = composite_for[0] if composite_for else None
    comp_base = composite_for[1] if composite_for else None
    glyphs = {}
    for n in glyph_names:
        if n == comp_name:
            continue
        glyphs[n] = _empty() if n == "space" else _box()
    if comp_name:
        pen = TTGlyphPen(glyphs)
        pen.addComponent(comp_base, (1, 0, 0, 1, 0, 0))
        glyphs[comp_name] = pen.glyph()
    fb.setupGlyf(glyphs)
    fb.setupHorizontalMetrics({n: ((250 if n == "space" else 600), 100) for n in glyph_names})
    fb.setupHorizontalHeader(ascent=800, descent=-200)
    fb.setupNameTable({"familyName": family, "styleName": "Regular"})
    fb.setupOS2(sTypoAscender=800, sTypoDescender=-200)
    fb.setupPost()
    fb.setupHead(unitsPerEm=1000)
    font = fb.font
    buf = io.BytesIO()
    font.save(buf)
    return buf.getvalue()


def build_main():
    names = [".notdef", "space"] + ["latin%02X" % c for c in range(0x41, 0x5B)]
    cmap = {c: "latin%02X" % c for c in range(0x41, 0x5B)}
    cmap[0x20] = "space"
    return build_font("MainTest", names, cmap)


def build_patch():
    names = [".notdef", "space", "base"]
    cmap = {0x20: "space"}
    for c in range(0x41, 0x5B):
        g = "latin%02X" % c
        names.append(g); cmap[c] = g
    # Greek capitals (skip reserved 0x3A2)
    for c in range(0x391, 0x3B0):
        if c == 0x3A2:
            continue
        g = "greek%04X" % c
        names.append(g); cmap[c] = g
    # a few Cyrillic
    for c in range(0x410, 0x41A):
        g = "cyrl%04X" % c
        names.append(g); cmap[c] = g
    # one CJK char
    cmap[0x4E2D] = "cjk4E2D"; names.append("cjk4E2D")
    # composite glyph for 0x2200 referencing base
    cmap[0x2200] = "forall"; names.append("forall")
    return build_font("PatchTest", names, cmap, composite_for=("forall", "base"))


def to_post3(data):
    """Recompile a font with a format-3.0 post table (no stored glyph names).

    Real fonts frequently use format 3.0 to save space; this reproduces that
    case so the merge path gets exercised against a nameless source font.
    """
    f = fontlib.load_font(data)
    if "post" in f:
        f["post"].formatType = 3.0
    buf = io.BytesIO()
    f.save(buf)
    return buf.getvalue()


def main():
    main_bytes = build_main()
    main_bytes = to_post3(main_bytes)   # mimic real fonts that drop glyph names
    patch_bytes = build_patch()

    info = fontlib.analyze(main_bytes)
    print("MAIN:", info["name"], "| glyphs", info["numGlyphs"], "| cps", info["numCodepoints"],
          "| covered blocks", info["coveredBlocks"])
    by_name = {b["name"]: b for b in info["blocks"]}
    for n in ("Basic Latin", "Greek and Coptic", "Cyrillic", "CJK Unified Ideographs",
              "Mathematical Operators"):
        b = by_name.get(n)
        print("  %-28s %s cov=%d" % (n, b["status"] if b else "?", b["covered"] if b else 0))
    assert by_name["Basic Latin"]["status"] == "present"
    assert by_name["Greek and Coptic"]["status"] == "missing"
    assert by_name["Cyrillic"]["status"] == "missing"
    assert by_name["CJK Unified Ideographs"]["status"] == "missing"
    assert by_name["Mathematical Operators"]["status"] == "missing"

    sup = fontlib.patch_supply(main_bytes, patch_bytes)
    print("PATCH:", sup["patchName"], "| fillable", sup["fillable"], "| supply", sup["supply"])
    assert sup["supply"].get("Greek and Coptic", 0) > 0
    assert sup["supply"].get("Cyrillic", 0) > 0
    assert sup["supply"].get("CJK Unified Ideographs", 0) == 1
    assert sup["supply"].get("Mathematical Operators", 0) == 1

    sel = ["Greek and Coptic", "Cyrillic", "CJK Unified Ideographs", "Mathematical Operators"]
    merged = fontlib.merge(main_bytes, patch_bytes, sel)
    print("MERGED: cps", merged["mergedCodepoints"], "| glyphs", merged["mergedGlyphs"])

    # Verify the merged font actually gained those codepoints and kept Latin.
    m = fontlib.load_font(merged["bytes"])
    cmap = fontlib.cmap_of(m)
    assert 0x41 in cmap and 0x5A in cmap, "Latin lost!"
    assert 0x391 in cmap, "Greek alpha missing"
    assert 0x410 in cmap, "Cyrillic missing"
    assert 0x4E2D in cmap, "CJK missing"
    assert 0x2200 in cmap, "composite glyph codepoint missing"
    # Composite component 'base' must have been copied into the merged font.
    assert "base" in m.getGlyphOrder(), "composite component 'base' not copied"
    print("glyphOrder has 'base':", "base" in m.getGlyphOrder())
    print("numGlyphs merged:", len(m.getGlyphOrder()))
    print("ALL ASSERTS PASSED")


def test_upem_scaling():
    """Merge glyphs between fonts with different UPEM; verify coordinates scale."""
    from fontTools.fontBuilder import FontBuilder
    main_upem = 2048
    patch_upem = 1000
    scale = main_upem / patch_upem

    fb = FontBuilder(patch_upem, isTTF=True)
    fb.setupGlyphOrder([".notdef", "space", "latin41"])
    fb.setupCharacterMap({0x41: "latin41", 0x20: "space"})
    fb.setupGlyf({".notdef": _empty(), "space": _empty(), "latin41": _box()})
    fb.setupHorizontalMetrics({".notdef": (500, 0), "space": (250, 0), "latin41": (600, 100)})
    fb.setupHorizontalHeader(ascent=800, descent=-200)
    fb.setupNameTable({"familyName": "PatchSmall", "styleName": "Regular"})
    fb.setupOS2(sTypoAscender=800, sTypoDescender=-200)
    fb.setupPost()
    fb.setupHead(unitsPerEm=patch_upem)
    buf = io.BytesIO()
    fb.font.save(buf)
    patch_small = buf.getvalue()

    main_big = build_main()  # UPEM 1000 from FontBuilder default
    # bump main to UPEM 2048
    mf = fontlib.load_font(main_big)
    mf["head"].unitsPerEm = main_upem
    buf2 = io.BytesIO()
    mf.save(buf2)
    main_big = buf2.getvalue()

    result = fontlib.merge(main_big, patch_small, ["Basic Latin"])
    m = fontlib.load_font(result["bytes"])
    cmap = fontlib.cmap_of(m)
    assert 0x41 in cmap, "Latin lost after UPEM merge"
    gname = cmap[0x41]
    adv = m["hmtx"][gname][0]
    expected = round(600 * scale)
    assert adv == expected, "advance %d != expected %d (scale %s)" % (adv, expected, scale)
    glyf = m["glyf"][gname]
    assert hasattr(glyf, "xMax"), "glyph has no bounds"
    # _box() draws 100..500 x 0..700; scaled by 2.048 -> ~205..1024
    assert glyf.xMin > 150, "xMin %d not scaled (expected ~205)" % glyf.xMin
    print("UPEM SCALING PASSED: patch advance %d -> merged %d (scale %.3f)" % (600, adv, scale))


def build_patch_subset(blocks):
    """Build a patch font covering only the given Unicode codepoint ranges.
    blocks is a list of (start, end) inclusive ranges.
    """
    names = [".notdef", "space", "base"]
    cmap = {0x20: "space"}
    for (start, end) in blocks:
        for c in range(start, end + 1):
            if c == 0x3A2:  # reserved
                continue
            g = "u%04X" % c
            names.append(g)
            cmap[c] = g
    return build_font("PatchSubset", names, cmap)


def test_multi_patch():
    """Merge two patches (Greek vs CJK) into the main font in one call."""
    main_bytes = to_post3(build_main())
    greek_patch = build_patch_subset([(0x391, 0x3A9)])   # Greek
    cjk_patch = build_patch_subset([(0x4E00, 0x4E10)])   # a few CJK chars

    patches = [
        (greek_patch, ["Greek and Coptic"]),
        (cjk_patch, ["CJK Unified Ideographs"]),
    ]
    result = fontlib.merge_multi(main_bytes, patches, overwrite_main=True)
    m = fontlib.load_font(result["bytes"])
    cmap = fontlib.cmap_of(m)
    assert 0x391 in cmap, "Greek missing in multi-merge"
    assert 0x4E00 in cmap, "CJK missing in multi-merge"
    assert 0x41 in cmap, "Latin lost in multi-merge"
    print("MULTI-PATCH PASSED: cps=%d glyphs=%d details=%s" % (
        result["mergedCodepoints"], result["mergedGlyphs"], result["details"]))

    # Overlap test: first patch wins when two patches cover the same codepoint.
    p1 = build_patch_subset([(0x500, 0x503)])  # Cyrillic Supplement
    p2 = build_patch_subset([(0x500, 0x503)])
    res2 = fontlib.merge_multi(main_bytes, [
        (p1, ["Cyrillic Supplement"]),
        (p2, ["Cyrillic Supplement"]),
    ], overwrite_main=True)
    # Second patch contributes nothing (all cps already taken by first).
    assert res2["details"][1]["codepoints"] == 0, "second patch should contribute 0"
    print("MULTI-OVERLAP PASSED: first patch wins (2nd cps=%d)" % res2["details"][1]["codepoints"])


if __name__ == "__main__":
    main()
    test_upem_scaling()
    test_multi_patch()


if __name__ == "__main__":
    main()
