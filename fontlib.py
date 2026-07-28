"""Font analysis and glyph merging built on fontTools.

Supports TrueType (.ttf, glyf-outline) fonts. Glyphs from the patch font are
copied into the main font for the selected Unicode blocks; codepoints the main
font already maps are left untouched. Composite glyphs pull in any referenced
component glyphs recursively.
"""
import copy
import io
import os
import sys

# Make the bundled ./libs dependency importable when running from source.
_HERE = os.path.dirname(os.path.abspath(__file__))
_LIBS = os.path.join(_HERE, "libs")
if os.path.isdir(_LIBS) and _LIBS not in sys.path:
    sys.path.insert(0, _LIBS)

from fontTools.ttLib import TTFont  # noqa: E402

import unicode_blocks as ub  # noqa: E402

from fontTools.misc.fixedTools import otRound  # noqa: E402


class FontError(Exception):
    """User-facing font processing error."""


def load_font(data: bytes) -> TTFont:
    try:
        return TTFont(io.BytesIO(data), fontNumber=0)
    except Exception as exc:  # noqa: BLE001
        raise FontError("无法解析字体文件: %s" % exc) from exc


def font_name(font: TTFont) -> str:
    for nid in (4, 1, 6, 16):
        try:
            v = font["name"].getDebugName(nid)
        except Exception:  # noqa: BLE001
            v = None
        if v:
            return v
    return "未命名字体"


def num_glyphs(font: TTFont) -> int:
    return len(font.getGlyphOrder())


def cmap_of(font: TTFont) -> dict:
    return font.getBestCmap() or {}


def analyze(data: bytes) -> dict:
    """Return font metadata plus per-Unicode-block coverage."""
    font = load_font(data)
    cmap = cmap_of(font)
    counts = {}
    for cp in cmap:
        b = ub.block_of(cp)
        if b is None:
            continue
        counts[b[2]] = counts.get(b[2], 0) + 1

    blocks = []
    covered_blocks = 0
    for (start, end, name, script, lang, cat) in ub.BLOCKS:
        cov = counts.get(name, 0)
        size = end - start + 1
        status = "missing" if cov == 0 else "present"
        covered_blocks += 1 if cov else 0
        blocks.append({
            "name": name,
            "start": start,
            "end": end,
            "size": size,
            "script": script,
            "lang": lang,
            "cat": cat,
            "covered": cov,
            "status": status,
            "frac": round(cov / size, 4) if size else 0.0,
        })
    return {
        "name": font_name(font),
        "numGlyphs": num_glyphs(font),
        "numCodepoints": len(cmap),
    "coveredBlocks": covered_blocks,
        "upem": font["head"].unitsPerEm,
        "blocks": blocks,
    }


def patch_supply(main_data: bytes, patch_data: bytes) -> dict:
    """For each block, count codepoints the patch has that the main lacks."""
    main = load_font(main_data)
    patch = load_font(patch_data)
    main_cmap = cmap_of(main)
    patch_cmap = cmap_of(patch)
    supply = {}
    fillable = 0
    replaceable = 0
    for cp in patch_cmap:
        b = ub.block_of(cp)
        if b is None:
            continue
        supply[b[2]] = supply.get(b[2], 0) + 1
        if cp in main_cmap:
            replaceable += 1
        else:
            fillable += 1
    return {
        "patchName": font_name(patch),
        "patchNumGlyphs": num_glyphs(patch),
        "patchUPEM": patch["head"].unitsPerEm,
        "supply": supply,
        "fillable": fillable,
        "replaceable": replaceable,
    }


def _unique_name(name: str, existing: set) -> str:
    if name not in existing:
        return name
    i = 1
    while True:
        cand = "%s.m%d" % (name, i)
        if cand not in existing:
            return cand
        i += 1


def _set_cmap(font: TTFont, cp: int, name: str) -> None:
    """Map a codepoint to a glyph name across the font's cmap subtables."""
    for sub in font["cmap"].tables:
        fmt = getattr(sub, "format", None)
        if fmt == 12:
            sub.cmap[cp] = name
        elif fmt == 4 and cp <= 0xFFFF:
            sub.cmap[cp] = name
        elif fmt in (0, 6) and cp <= 0xFF:
            sub.cmap[cp] = name


def _scale_glyph(glyph, scale: float, glyf_table) -> None:
    """Scale a glyph's outlines and offsets in-place to match a different UPEM.

    For simple glyphs, point coordinates are scaled and rounded. For composite
    glyphs, the translation (x, y) of each component is scaled — the 2x2 matrix
    is dimensionless so it is left alone.
    """
    if abs(scale - 1.0) < 1e-9:
        return
    if glyph.isComposite():
        for comp in glyph.components:
            comp.x = otRound(comp.x * scale)
            comp.y = otRound(comp.y * scale)
    elif hasattr(glyph, "coordinates") and glyph.coordinates is not None:
        coords = glyph.coordinates
        coords.scale((scale, scale))
        coords.toInt()
        if hasattr(glyph, "recalcBounds"):
            glyph.recalcBounds(glyf_table)
        elif hasattr(glyph, "recalcBoundingBox"):
            glyph.recalcBoundingBox(glyf_table)


def _merge_glyf(main: TTFont, patch: TTFont, targets) -> tuple:
    """Copy target glyphs (with composite components) into the main glyf font."""
    glyf_main = main["glyf"]
    glyf_patch = patch["glyf"]
    hmtx_main = main["hmtx"]
    hmtx_patch = patch["hmtx"]
    vmtx_main = main["vmtx"] if "vmtx" in main else None
    vmtx_patch = patch["vmtx"] if "vmtx" in patch else None

    # Scale glyphs/metrics when UPEM differs so patch glyphs render at the right size.
    scale = main["head"].unitsPerEm / patch["head"].unitsPerEm

    # Ensure TTFont.glyphOrder is materialized so we can append to it.
    _ = main.getGlyphOrder()
    existing = set(main.glyphOrder)
    added_glyphs = [0]

    def add_one(src_name: str, allow_reuse: bool) -> str:
        if allow_reuse and src_name in existing:
            return src_name
        tgt = _unique_name(src_name, existing)
        existing.add(tgt)
        main.glyphOrder.append(tgt)
        # Access via the table accessor so the glyph is expanded (fontTools
        # loads glyf glyphs lazily; .glyphs[name] stays unexpanded).
        glyph = copy.deepcopy(glyf_patch[src_name])
        _scale_glyph(glyph, scale, glyf_main)
        glyf_main[tgt] = glyph
        try:
            w, lsb = hmtx_patch[src_name]
            hmtx_main[tgt] = (otRound(w * scale), otRound(lsb * scale))
        except KeyError:
            hmtx_main[tgt] = (0, 0)
        if vmtx_main is not None and vmtx_patch is not None:
            try:
                w, tsb = vmtx_patch[src_name]
                vmtx_main[tgt] = (otRound(w * scale), otRound(tsb * scale))
            except KeyError:
                pass
        added_glyphs[0] += 1
        # Pull in referenced components and rewrite their names in the copy.
        if glyph.isComposite():
            for comp in glyph.components:
                comp.glyphName = add_one(comp.glyphName, allow_reuse=True)
            # Recompute the composite bounding box (method name varies by version).
            if hasattr(glyph, "recalcBounds"):
                glyph.recalcBounds(glyf_main)
            elif hasattr(glyph, "recalcBoundingBox"):
                glyph.recalcBoundingBox(glyf_main)
        return tgt

    added_cps = 0
    for cp, src_name in targets:
        if src_name not in glyf_patch.glyphs:
            continue
        tgt = add_one(src_name, allow_reuse=False)
        _set_cmap(main, cp, tgt)
        added_cps += 1

    main["maxp"].numGlyphs = len(main.glyphOrder)
    _rebuild_post(main)
    return added_glyphs[0], added_cps


def _rebuild_post(font: TTFont) -> None:
    """Rebuild the post table so added glyph names are stored correctly.

    Source fonts often ship a format-3.0 post table (no glyph names) to save
    space. That table never populates the ``extraNames`` / ``mapping`` state
    that format-2.0 encoding needs, so simply setting ``formatType = 2.0``
    crashes at save time. We rebuild that state from the current glyph order
    so the merged font keeps readable names for every glyph.
    """
    post = font["post"]
    if post is None:
        return
    try:
        post.glyphOrder = list(font.getGlyphOrder())
        post.formatType = 2.0
        post.build_psNameMapping(font)  # sets self.mapping
        post.extraNames = []            # repopulated lazily in encode_format_2_0
    except Exception:  # noqa: BLE001 - fall back to a nameless but valid post
        post.formatType = 3.0


def merge(main_data: bytes, patch_data: bytes, selected_blocks,
          overwrite_main: bool = True) -> dict:
    """Single-patch convenience wrapper around merge_multi."""
    return merge_multi(main_data, [(patch_data, selected_blocks)], overwrite_main)


def merge_multi(main_data: bytes, patches, overwrite_main: bool = True) -> dict:
    """Chain-merge multiple patches into the main font (in memory).

    ``patches`` is a list of ``(patch_data, selected_blocks)`` tuples, applied
    in order. For codepoints claimed by more than one patch, the earlier patch
    wins (later patches skip it). ``overwrite_main`` controls whether the main
    font's own glyphs in selected blocks are replaced by patch glyphs.
    """
    main = load_font(main_data)
    if "glyf" not in main:
        if "CFF " in main:
            raise FontError(
                "主体字体使用 CFF 轮廓 (OTF)，当前仅支持 TrueType (glyf) 轮廓的合并。"
            )
        raise FontError("不支持的字体类型 (缺少 glyf 轮廓表)。")
    orig_main_cps = set(cmap_of(main).keys())

    targets = []
    total_glyphs = 0
    total_cps = 0
    details = []
    for patch_data, blocks in patches:
        patch = load_font(patch_data)
        patch_name = font_name(patch)
        if "glyf" not in patch:
            details.append({"name": patch_name, "codepoints": 0, "glyphs": 0,
                            "skipped": True})
            continue
        patch_cmap = cmap_of(patch)
        selected = set(blocks)
        current = cmap_of(main)
        targets = []
        for cp in patch_cmap:
            b = ub.block_of(cp)
            if b is None or b[2] not in selected:
                continue
            if cp in current:
                # Keep main's original glyph unless overwrite is requested.
                if cp in orig_main_cps and overwrite_main:
                    pass
                else:
                    continue
            targets.append((cp, patch_cmap[cp]))
        glyphs, cps = _merge_glyf(main, patch, targets)
        total_glyphs += glyphs
        total_cps += cps
        details.append({"name": patch_name, "codepoints": cps, "glyphs": glyphs})

    buf = io.BytesIO()
    main.save(buf)
    return {
        "bytes": buf.getvalue(),
        "mergedCodepoints": total_cps,
        "mergedGlyphs": total_glyphs,
        "details": details,
    }
