"use strict";
const $ = (id) => document.getElementById(id);

const state = {
  mainToken: null,
  mainName: null,
  blocks: [],
  patches: [],
  activePatch: -1,
  overwriteMain: true,
};

// ---------- helpers ----------
function fmt(n){ return (n || 0).toLocaleString("en-US"); }
function hex4(cp){ return "U+" + cp.toString(16).toUpperCase().padStart(4, "0"); }
function esc(s){ return String(s).replace(/[&<>"']/g, c => ({ "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;" }[c])); }
function toast(msg, isErr){
  const el = $("toast"); el.textContent = msg; el.className = "toast show" + (isErr ? " err" : "");
  clearTimeout(toast._t); toast._t = setTimeout(() => { el.className = "toast"; }, 3200);
}
function toB64(buf){
  let s = ""; const bytes = new Uint8Array(buf);
  for (let i = 0; i < bytes.length; i += 0x8000) s += String.fromCharCode.apply(null, bytes.subarray(i, i + 0x8000));
  return btoa(s);
}
async function postJSON(url, obj){
  const r = await fetch(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(obj) });
  let j; try { j = await r.json(); } catch (e) { throw new Error(t("serverError")); }
  if (!j.ok) throw new Error(j.error || t("requestFailed"));
  return j;
}
function ap(){ return state.activePatch >= 0 ? state.patches[state.activePatch] : null; }
function activeSupply(){ const p = ap(); return p ? p.supply : {}; }
function activeSelection(){ const p = ap(); return p ? p.selection : new Set(); }
function setStatus(text){ $("serverStatus").innerHTML = '<span class="dot"></span>' + esc(text); }
function setBusy(){ $("serverStatus").innerHTML = '<span class="dot" style="background:#b45309;box-shadow:0 0 0 3px var(--amber-soft)"></span>' + esc(t("parsing")); }

function wireDrop(dropEl, inputEl, handler){
  dropEl.addEventListener("click", () => inputEl.click());
  inputEl.addEventListener("change", () => { if (inputEl.files && inputEl.files.length) handler(inputEl.files); inputEl.value = ""; });
  ["dragenter","dragover"].forEach(ev => dropEl.addEventListener(ev, e => { e.preventDefault(); dropEl.classList.add("drag"); }));
  ["dragleave","drop"].forEach(ev => dropEl.addEventListener(ev, e => { e.preventDefault(); dropEl.classList.remove("drag"); }));
  dropEl.addEventListener("drop", e => { if (e.dataTransfer.files && e.dataTransfer.files.length) handler(e.dataTransfer.files); });
}
function readFile(file){
  return new Promise((resolve, reject) => {
    const fr = new FileReader();
    fr.onload = () => resolve(fr.result);
    fr.onerror = () => reject(new Error(t("readFileFailed")));
    fr.readAsArrayBuffer(file);
  });
}

// ---------- main font ----------
async function loadMain(files){
  const file = files[0];
  setBusy();
  try {
    const buf = await readFile(file);
    const j = await postJSON("/api/analyze", { data: toB64(buf), filename: file.name });
    state.mainToken = j.token;
    state.mainName = j.name;
    state.blocks = j.blocks;
    state.patches = [];
    state.activePatch = -1;
    renderMainMeta(j, file.name);
    renderPatchTabs();
    renderBlocks();
    updateMergeBar();
    toast(t("masterLoaded") + j.name);
  } catch (e) {
    toast(e.message, true);
  } finally {
    setStatus(t("ready"));
  }
}
function renderMainMeta(j, filename){
  const m = $("mainMeta");
  m.className = "meta";
  m.innerHTML =
    '<div class="v tname"></div>' +
    '<div class="k">' + t("upem") + '</div><div class="v">' + fmt(j.upem) + '</div>' +
    '<div class="k">' + t("numGlyphs") + '</div><div class="v">' + fmt(j.numGlyphs) + '</div>' +
    '<div class="k">' + t("coveredBlocks") + '</div><div class="v">' + fmt(j.coveredBlocks) + '</div>' +
    '<div class="fname"></div>';
  m.querySelector(".tname").textContent = j.name;
  m.querySelector(".fname").textContent = filename;
}

// ---------- patch fonts ----------
async function addPatches(files){
  if (!state.mainToken) { toast(t("needMasterFirst"), true); return; }
  const arr = Array.from(files);
  setBusy();
  $("serverStatus").innerHTML = '<span class="dot" style="background:#b45309;box-shadow:0 0 0 3px var(--amber-soft)"></span>' + esc(t("parsingPatches") + " (" + arr.length + ")…");
  try {
    let added = 0;
    for (const file of arr){
      const buf = await readFile(file);
      const j = await postJSON("/api/patch", { data: toB64(buf), filename: file.name, mainToken: state.mainToken });
      state.patches.push({
        token: j.token, name: j.patchName, upem: j.patchUPEM, numGlyphs: j.patchNumGlyphs,
        fillable: j.fillable, replaceable: j.replaceable, supply: j.supply || {}, selection: new Set(),
      });
      added++;
    }
    state.activePatch = state.patches.length - 1;
    renderPatchTabs();
    renderPatchMeta();
    renderBlocks();
    updateMergeBar();
    toast(t("patchesAdded", { n: added, total: state.patches.length }));
  } catch (e) {
    toast(e.message, true);
  } finally {
    setStatus(t("ready"));
  }
}
function renderPatchTabs(){
  const el = $("patchTabs");
  if (!state.patches.length){ el.innerHTML = '<span class="ptab-empty">' + esc(t("noPatchesYet")) + "</span>"; return; }
  el.innerHTML = state.patches.map((p, i) => {
    const cls = (i === state.activePatch ? "ptab active" : "ptab") + (p.selection.size ? " has-sel" : "");
    return '<div class="' + cls + '" data-idx="' + i + '" title="' + esc(p.name) + '">' +
      '<span class="ptab-dot"></span>' +
      '<span class="ptab-name">' + esc(p.name) + '</span>' +
      (p.selection.size ? '<span class="ptab-badge">' + p.selection.size + '</span>' : "") +
      '<span class="ptab-rm" data-rm="' + i + '" title="' + esc(t("remove")) + '">×</span></div>';
  }).join("");
}
function renderPatchMeta(){
  const m = $("patchMeta");
  const p = ap();
  if (!p){ m.className = "meta hidden"; $("tableSub").textContent = t("selectBlocks"); return; }
  m.className = "meta";
  m.innerHTML =
    '<div class="v tname"></div>' +
    '<div class="k">' + t("upem") + '</div><div class="v">' + fmt(p.upem) + '</div>' +
    '<div class="k">' + t("numGlyphs") + '</div><div class="v">' + fmt(p.numGlyphs) + '</div>' +
    '<div class="k">' + t("supplyCps") + '</div><div class="v" style="color:var(--amber)">' + fmt(p.fillable + p.replaceable) + '</div>' +
    '<div class="fname"></div>';
  m.querySelector(".tname").textContent = p.name;
  m.querySelector(".fname").textContent = t("patchIndex", { n: state.activePatch + 1, total: state.patches.length });
  $("tableSub").textContent = t("selectBlocksFor", { name: p.name });
}
function onPatchTabClick(e){
  const rm = e.target.closest(".ptab-rm");
  if (rm){ removePatch(+rm.getAttribute("data-rm")); return; }
  const tab = e.target.closest(".ptab");
  if (tab){
    state.activePatch = +tab.getAttribute("data-idx");
    renderPatchTabs(); renderPatchMeta(); renderBlocks(); updateMergeBar();
  }
}
function removePatch(idx){
  state.patches.splice(idx, 1);
  if (state.activePatch >= state.patches.length) state.activePatch = state.patches.length - 1;
  renderPatchTabs(); renderPatchMeta(); renderBlocks(); updateMergeBar();
}

// ---------- block table ----------
function visibleBlocks(){
  const q = $("searchBox").value.trim().toLowerCase();
  const only = $("onlyFillable").checked;
  const cat = $("catFilter").value;
  const supply = activeSupply();
  let rows = state.blocks.filter(b => {
    if (cat && b.cat !== cat) return false;
    const fill = supply[b.name] || 0;
    if (only && fill === 0) return false;
    if (q){
      const hay = (b.name + " " + b.lang + " " + b.script + " " + b.cat).toLowerCase();
      if (!hay.includes(q)) return false;
    }
    return true;
  });
  rows.sort((a, b) => {
    const fa = (supply[a.name] || 0) > 0 ? 0 : 1;
    const fb = (supply[b.name] || 0) > 0 ? 0 : 1;
    if (fa !== fb) return fa - fb;
    const ma = a.status === "missing" ? 0 : 1, mb = b.status === "missing" ? 0 : 1;
    if (ma !== mb) return ma - mb;
    return a.start - b.start;
  });
  return rows;
}
function rowHTML(b){
  const supply = activeSupply();
  const selection = activeSelection();
  const fill = supply[b.name] || 0;
  const patchable = fill > 0;
  const checked = selection.has(b.name);
  const pct = Math.max(0, Math.min(1, b.frac)) * 100;
  const cls = (checked ? "sel " : "") + (patchable ? "fillable" : "");
  return '<tr class="' + cls.trim() + '" data-name="' + esc(b.name) + '">' +
    '<td class="c-check"><input type="checkbox" class="rowcheck" ' + (patchable ? "" : "disabled") +
    (checked ? " checked" : "") + "></td>" +
    '<td><span class="bname">' + esc(b.name) + '</span><span class="cat-tag">' + esc(b.cat) + "</span></td>" +
    '<td class="lang">' + esc(b.lang) + "</td>" +
    '<td class="c-range"><span class="range">' + hex4(b.start) + "–" + hex4(b.end) + "</span></td>" +
    '<td class="c-cov"><div class="cov-cell"><div class="bar"><i style="width:' + pct.toFixed(1) + "%\"></i></div>" +
    '<span class="badge ' + b.status + '">' + (b.status === "missing" ? t("missingBadge") : t("presentBadge")) + "</span></div></td>" +
    '<td class="c-fill"><span class="fill-num ' + (patchable ? "" : "zero") + '">' + fmt(fill) + "</span></td>" +
    "</tr>";
}
function renderBlocks(){
  const body = $("blockBody");
  if (!state.blocks.length){
    body.innerHTML = '<tr class="empty-row"><td colspan="6">' + esc(t("emptyLoadFirst")) + "</td></tr>";
    $("summaryBar").textContent = t("summaryEmpty");
    populateCats([]);
    return;
  }
  const rows = visibleBlocks();
  body.innerHTML = rows.length
    ? rows.map(rowHTML).join("")
    : '<tr class="empty-row"><td colspan="6">' + esc(t("noMatch")) + "</td></tr>";
  populateCats(state.blocks);
  const missing = state.blocks.filter(b => b.status === "missing").length;
  const present = state.blocks.length - missing;
  let extra = "";
  if (ap()){
    const supply = activeSupply();
    const patchable = state.blocks.filter(b => (supply[b.name] || 0) > 0).length;
    extra = " · " + t("currentMergeable") + " " + patchable;
  }
  $("summaryBar").textContent = t("summaryTotal", { total: state.blocks.length, present, missing }) + extra;
  syncHead();
}
function populateCats(blocks){
  const sel = $("catFilter");
  const cur = sel.value;
  const cats = Array.from(new Set(blocks.map(b => b.cat))).sort();
  sel.innerHTML = '<option value="">' + esc(t("allCategories")) + "</option>" + cats.map(c => '<option value="' + esc(c) + '">' + esc(c) + "</option>").join("");
  sel.value = cur;
}
function onTableClick(e){
  const cb = e.target.closest(".rowcheck");
  if (!cb) return;
  const p = ap(); if (!p) return;
  const tr = cb.closest("tr");
  const name = tr.getAttribute("data-name");
  if (cb.checked){ p.selection.add(name); tr.classList.add("sel"); }
  else { p.selection.delete(name); tr.classList.remove("sel"); }
  syncHead();
  renderPatchTabs();
  updateMergeBar();
}
function syncHead(){
  const rows = visibleBlocks();
  const supply = activeSupply();
  const selection = activeSelection();
  const patchable = rows.filter(b => (supply[b.name] || 0) > 0);
  const sel = patchable.filter(b => selection.has(b.name));
  const head = $("headCheck");
  head.indeterminate = sel.length > 0 && sel.length < patchable.length;
  head.checked = patchable.length > 0 && sel.length === patchable.length;
}
function headToggle(e){
  const p = ap(); if (!p) return;
  const supply = activeSupply();
  const rows = visibleBlocks().filter(b => (supply[b.name] || 0) > 0);
  const on = e.target.checked;
  rows.forEach(b => { if (on) p.selection.add(b.name); else p.selection.delete(b.name); });
  renderBlocks();
  renderPatchTabs();
  updateMergeBar();
}
function checkAllMissing(){
  const p = ap(); if (!p){ toast(t("needPatchFirst"), true); return; }
  const supply = activeSupply();
  let n = 0;
  state.blocks.forEach(b => {
    if ((supply[b.name] || 0) > 0){ p.selection.add(b.name); n++; }
  });
  renderBlocks();
  renderPatchTabs();
  updateMergeBar();
  toast(t("checkedN", { n }));
}

// ---------- merge ----------
function updateMergeBar(){
  let cps = 0, selBlocks = 0;
  state.patches.forEach(p => {
    p.selection.forEach(n => { cps += p.supply[n] || 0; });
    selBlocks += p.selection.size;
  });
  $("selPatches").textContent = fmt(state.patches.length);
  $("selBlocks").textContent = fmt(selBlocks);
  $("selCps").textContent = fmt(cps);
  const hasSelection = state.patches.some(p => p.selection.size > 0);
  $("mergeBtn").disabled = !(hasSelection && state.mainToken && state.patches.length);
}
async function doMerge(){
  if (!state.mainToken || !state.patches.length) return;
  const patches = state.patches.filter(p => p.selection.size).map(p => ({ token: p.token, blocks: Array.from(p.selection) }));
  if (!patches.length) return;
  const btn = $("mergeBtn");
  btn.disabled = true; btn.textContent = t("merging");
  try {
    const j = await postJSON("/api/merge", { mainToken: state.mainToken, patches, overwriteMain: state.overwriteMain });
    await saveResult(j);
  } catch (e) {
    toast(e.message, true);
  } finally {
    btn.textContent = t("mergeBtn");
    updateMergeBar();
  }
}
function isDesktop(){
  return !!(window.pywebview && window.pywebview.api && window.pywebview.api.save_font);
}
async function saveResult(j){
  const msg = t("mergedCpsGlyphs", { cps: fmt(j.mergedCodepoints), glyphs: fmt(j.mergedGlyphs) });
  if (isDesktop()){
    const r = await window.pywebview.api.save_font(j.data, j.filename);
    if (r && r.ok) toast(msg + t("savedTo") + r.path);
    else if (r && r.canceled) toast(t("saveCanceled"));
    else toast((r && r.error) || t("saveFailed"), true);
    return;
  }
  const bin = atob(j.data);
  const bytes = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
  const blob = new Blob([bytes], { type: "font/ttf" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob); a.download = j.filename; a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 10000);
  toast(msg + t("downloadStarting"));
}

/** Re-render dynamic content when language changes. */
function onLangChange(){
  if (state.mainToken) { renderMainMeta; } // meta uses j/filename, only labels re-translate on next render
  renderPatchTabs();
  renderPatchMeta();
  renderBlocks();
  updateMergeBar();
  setStatus(t("ready"));
}

// ---------- init ----------
initLang();
wireDrop($("mainDrop"), $("mainFile"), loadMain);
wireDrop($("patchDrop"), $("patchFile"), addPatches);
$("searchBox").addEventListener("input", renderBlocks);
$("onlyFillable").addEventListener("change", renderBlocks);
$("catFilter").addEventListener("change", renderBlocks);
$("headCheck").addEventListener("change", headToggle);
$("checkAll").addEventListener("click", checkAllMissing);
$("blockBody").addEventListener("click", onTableClick);
$("mergeBtn").addEventListener("click", doMerge);
$("patchTabs").addEventListener("click", onPatchTabClick);
$("overwriteMain").addEventListener("change", e => { state.overwriteMain = e.target.checked; });
renderPatchTabs();
