// i18n dictionary for the TTF Font Merger.
// Keys are referenced via data-i18n / data-i18n-html / data-i18n-ph attributes in index.html,
// and looked up directly via t("key") in app.js for dynamic text.

const I18N = {
  zh: {
    title: "TTF 字体合并工具",
    appName: "字体合并工具",
    tagline: "选择主体字体 → 用多个补丁字体分别补齐不同语言的字形",
    ready: "就绪",
    masterFont: "主体字体",
    masterHint: "作为合并的基础",
    mainDrop: "选择或拖入 <b>主体 TTF</b>",
    fileTypes: "支持 .ttf / .otf / .ttc",
    patchFonts: "补丁字体",
    patchHint: "可添加多个，分别选择区块",
    addPatchFonts: "＋ 添加补丁字体（可多选）",
    blockCoverage: "Unicode 区块覆盖",
    selectBlocks: "为当前补丁选择要合并的区块",
    searchPlaceholder: "搜索区块 / 语言 / 文字…",
    onlyMergeable: "仅显示可合并区块",
    allCategories: "全部分类",
    checkAllMergeable: "勾选当前可合并",
    legendMissing: "主体缺失",
    legendPresent: "主体已含",
    legendFill: "补丁提供",
    summaryEmpty: "载入主体字体后显示覆盖情况",
    colBlock: "区块",
    colLang: "语言 / 文字",
    colRange: "码位范围",
    colCoverage: "主体覆盖",
    colSupply: "补丁提供",
    emptyLoadFirst: "请先载入主体字体。",
    overwriteExisting: "覆盖主体已有字形",
    patches: "个补丁",
    selectedBlocks: "已选",
    blocksUnit: "个区块",
    willMerge: "将合并",
    codepointsUnit: "个码位",
    mergeBtn: "合并并下载",
    // dynamic strings
    parsing: "解析中…",
    masterLoaded: "主体字体已载入：",
    parsingPatches: "解析补丁",
    needMasterFirst: "请先载入主体字体",
    patchesAdded: "已添加 {n} 个补丁字体，共 {total} 个",
    noPatchesYet: "还没有补丁字体，下方添加",
    remove: "移除",
    upem: "UPEM",
    numGlyphs: "字形数",
    coveredBlocks: "已覆盖区块",
    codepoints: "已映射码位",
    supplyCps: "可提供码位",
    patchIndex: "补丁 {n} / {total}",
    selectBlocksFor: "为「{name}」选择要合并的区块",
    missingBadge: "缺失",
    presentBadge: "已含",
    noMatch: "没有匹配的区块。",
    currentMergeable: "当前补丁可合并",
    summaryTotal: "共 {total} 区块：已含 {present}，缺失 {missing}",
    needPatchFirst: "请先载入补丁字体",
    checkedN: "已勾选 {n} 个可合并区块",
    merging: "合并中…",
    mergedCpsGlyphs: "已合并 {cps} 个码位 / {glyphs} 个字形",
    savedTo: "，已保存：",
    saveCanceled: "已取消保存（合并已完成）",
    saveFailed: "保存失败",
    downloadStarting: "，开始下载",
    serverError: "服务器返回异常",
    requestFailed: "请求失败",
    readFileFailed: "读取文件失败",
  },

  en: {
    title: "TTF Font Merger",
    appName: "Font Merger",
    tagline: "Load a master font → merge glyphs from multiple patch fonts into it",
    ready: "Ready",
    masterFont: "Master Font",
    masterHint: "The base font to merge into",
    mainDrop: "Drop or select <b>master TTF</b>",
    fileTypes: "Supports .ttf / .otf / .ttc",
    patchFonts: "Patch Fonts",
    patchHint: "Add multiple, select blocks for each",
    addPatchFonts: "＋ Add patch fonts (multi-select)",
    blockCoverage: "Unicode Block Coverage",
    selectBlocks: "Select blocks to merge for the active patch",
    searchPlaceholder: "Search block / language / script…",
    onlyMergeable: "Mergeable only",
    allCategories: "All categories",
    checkAllMergeable: "Check all mergeable",
    legendMissing: "Missing",
    legendPresent: "Present",
    legendFill: "Patch supply",
    summaryEmpty: "Load a master font to see coverage",
    colBlock: "Block",
    colLang: "Language / Script",
    colRange: "Codepoint range",
    colCoverage: "Coverage",
    colSupply: "Patch supply",
    emptyLoadFirst: "Load a master font first.",
    overwriteExisting: "Overwrite existing glyphs",
    patches: "patches",
    selectedBlocks: "selected",
    blocksUnit: "blocks",
    willMerge: "merging",
    codepointsUnit: "codepoints",
    mergeBtn: "Merge & download",
    // dynamic strings
    parsing: "Parsing…",
    masterLoaded: "Master font loaded: ",
    parsingPatches: "Parsing patches",
    needMasterFirst: "Load a master font first",
    patchesAdded: "Added {n} patch fonts ({total} total)",
    noPatchesYet: "No patch fonts yet — add below",
    remove: "Remove",
    upem: "UPEM",
    numGlyphs: "Glyphs",
    coveredBlocks: "Covered blocks",
    codepoints: "Mapped codepoints",
    supplyCps: "Supply codepoints",
    patchIndex: "Patch {n} / {total}",
    selectBlocksFor: "Select blocks to merge from \"{name}\"",
    missingBadge: "Missing",
    presentBadge: "Present",
    noMatch: "No matching blocks.",
    currentMergeable: "current mergeable",
    summaryTotal: "{total} blocks: {present} present, {missing} missing",
    needPatchFirst: "Load a patch font first",
    checkedN: "Checked {n} mergeable blocks",
    merging: "Merging…",
    mergedCpsGlyphs: "Merged {cps} codepoints / {glyphs} glyphs",
    savedTo: ", saved to: ",
    saveCanceled: "Save canceled (merge complete)",
    saveFailed: "Save failed",
    downloadStarting: ", download starting",
    serverError: "Server returned an error",
    requestFailed: "Request failed",
    readFileFailed: "Failed to read file",
  },
};

let LANG = "zh";

/** Translate a key, with optional {placeholder} substitution. */
function t(key, params) {
  let s = (I18N[LANG] && I18N[LANG][key]) || (I18N.zh[key]) || key;
  if (params) {
    for (const [k, v] of Object.entries(params)) {
      s = s.replace(new RegExp("\\{" + k + "\\}", "g"), v);
    }
  }
  return s;
}

/** Apply the current language to all static DOM elements with data-i18n*. */
function applyLang() {
  document.documentElement.lang = LANG === "zh" ? "zh-CN" : "en";
  document.querySelectorAll("[data-i18n]").forEach(el => { el.textContent = t(el.getAttribute("data-i18n")); });
  document.querySelectorAll("[data-i18n-html]").forEach(el => { el.innerHTML = t(el.getAttribute("data-i18n-html")); });
  document.querySelectorAll("[data-i18n-ph]").forEach(el => { el.placeholder = t(el.getAttribute("data-i18n-ph")); });
  document.querySelectorAll(".lang-btn").forEach(b => {
    b.classList.toggle("active", b.getAttribute("data-lang") === LANG);
  });
}

/** Load saved language preference, defaulting to browser language. */
function initLang() {
  const saved = localStorage.getItem("ttfmerge-lang");
  if (saved === "zh" || saved === "en") {
    LANG = saved;
  } else {
    LANG = navigator.language && navigator.language.toLowerCase().startsWith("zh") ? "zh" : "en";
  }
  applyLang();
  document.querySelectorAll(".lang-btn").forEach(b => {
    b.addEventListener("click", () => {
      LANG = b.getAttribute("data-lang");
      localStorage.setItem("ttfmerge-lang", LANG);
      applyLang();
      // Re-render dynamic content that holds translated strings
      if (typeof onLangChange === "function") onLangChange();
    });
  });
}
