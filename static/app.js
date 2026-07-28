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

function fmt(n){ return (n || 0).toLocaleString("en-US"); }
function hex4(cp){ return "U+" + cp.toString(16).toUpperCase().padStart(4, "0"); }
function esc(s){ return String(s).replace(/[&<>"']/g, c => ({ "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;" }[c])); }
function toast(msg, isErr){
  const t = $("toast"); t.textContent = msg; t.className = "toast show" + (isErr ? " err" : "");
  clearTimeout(toast._t); toast._t = setTimeout(() => { t.className = "toast"; }, 3200);
}
function toB64(buf){
  let s = ""; const bytes = new Uint8Array(buf);
  for (let i = 0; i < bytes.length; i += 0x8000) s += String.fromCharCode.apply(null, bytes.subarray(i, i + 0x8000));
  return btoa(s);
}
async function postJSON(url, obj){
  const r = await fetch(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(obj) });
  let j; try { j = await r.json(); } catch (e) { throw new Error("服务器返回异常"); }
  if (!j.ok) throw new Error(j.error || "请求失败");
  return j;
}
function ap(){ return state.activePatch >= 0 ? state.patches[state.activePatch] : null; }
function activeSupply(){ const p = ap(); return p ? p.supply : {}; }
function activeSelection(){ const p = ap(); return p ? p.selection : new Set(); }

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
    fr.onerror = () => reject(new Error("读取文件失败"));
    fr.readAsArrayBuffer(file);
  });
}

// ---- main font ----
async function loadMain(files){
  const file = files[0];
  $("serverStatus").innerHTML = '<span class="dot" style="background:#b45309;box-shadow:0 0 0 3px var(--amber-soft)"></span>解析中…';
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
    toast("主体字体已载入：" + j.name);
  } catch (e) {
    toast(e.message, true);
  } finally {
    $("serverStatus").innerHTML = '<span class="dot"></span>就绪';
  }
}
function renderMainMeta(j, filename){
  const m = $("mainMeta");
  m.className = "meta";
  m.innerHTML =
    '<div class="v tname"></div>' +
    '<div class="k">UPEM</div><div class="v">' + fmt(j.upem) + '</div>' +
    '<div class="k">字形数</div><div class="v">' + fmt(j.numGlyphs) + '</div>' +
    '<div class="k">已覆盖区块</div><div class="v">' + fmt(j.coveredBlocks) + '</div>' +
    '<div class="fname"></div>';
  m.querySelector(".tname").textContent = j.name;
  m.querySelector(".fname").textContent = filename;
}

// ---- patch fonts (multiple) ----
async function addPatches(files){
  if (!state.mainToken) { toast("请先载入主体字体", true); return; }
  const arr = Array.from(files);
  $("serverStatus").innerHTML = '<span class="dot" style="background:#b45309;box-shadow:0 0 0 3px var(--amber-soft)"></span>解析补丁 (' + arr.length + ')…';
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
    toast("已添加 " + added + " 个补丁字体，共 " + state.patches.length + " 个");
  } catch (e) {
    toast(e.message, true);
  } finally {
    $("serverStatus").innerHTML = '<span class="dot"></span>就绪';
  }
}
function renderPatchTabs(){
  const el = $("patchTabs");
  if (!state.patches.length){ el.innerHTML = '<span class="ptab-empty">还没有补丁字体，下方添加</span>'; return; }
  el.innerHTML = state.patches.map((p, i) => {
    const cls = (i === state.activePatch ? "ptab active" : "ptab") + (p.selection.size ? " has-sel" : "");
    return '<div class="' + cls + '" data-idx="' + i + '" title="' + esc(p.name) + '">' +
      '<span class="ptab-dot"></span>' +
      '<span class="ptab-name">' + esc(p.name) + '</span>' +
      (p.selection.size ? '<span class="ptab-badge">' + p.selection.size + '</span>' : '') +
      '<span class="ptab-rm" data-rm="' + i + '" title="移除">×</span></div>';
  }).join("");
}
function renderPatchMeta(){
  const m = $("patchMeta");
  const p = ap();
  if (!p){ m.className = "meta hidden"; $("tableSub").textContent = "为当前补丁选择要合并的区块"; return; }
  m.className = "meta";
  m.innerHTML =
    '<div class="v tname"></div>' +
    '<div class="k">UPEM</div><div class="v">' + fmt(p.upem) + '</div>' +
    '<div class="k">字形数</div><div class="v">' + fmt(p.numGlyphs) + '</div>' +
    '<div class="k">可提供码位</div><div class="v" style="color:var(--amber)">' + fmt(p.fillable + p.replaceable) + '</div>' +
    '<div class="fname"></div>';
  m.querySelector(".tname").textContent = p.name;
  m.querySelector(".fname").textContent = "补丁 " + (state.activePatch + 1) + " / " + state.patches.length;
  $("tableSub").textContent = "为「" + p.name + "」选择要合并的区块";
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

// ---- block table ----
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
    '<span class="badge ' + b.status + '">' + (b.status === "missing" ? "缺失" : "已含") + "</span></div></td>" +
    '<td class="c-fill"><span class="fill-num ' + (patchable ? "" : "zero") + '">' + fmt(fill) + "</span></td>" +
    "</tr>";
}
function renderBlocks(){
  const body = $("blockBody");
  if (!state.blocks.length){
    body.innerHTML = '<tr class="empty-row"><td colspan="6">请先载入主体字体。</td></tr>';
    $("summaryBar").textContent = "载入主体字体后显示覆盖情况";
    populateCats([]);
    return;
  }
  const rows = visibleBlocks();
  body.innerHTML = rows.length
    ? rows.map(rowHTML).join("")
    : '<tr class="empty-row"><td colspan="6">没有匹配的区块。</td></tr>';
  populateCats(state.blocks);
  const missing = state.blocks.filter(b => b.status === "missing").length;
  const present = state.blocks.length - missing;
  let extra = "";
  if (ap()){
    const supply = activeSupply();
    const patchable = state.blocks.filter(b => (supply[b.name] || 0) > 0).length;
    extra = " · 当前补丁可合并 " + patchable;
  }
  $("summaryBar").textContent = "共 " + state.blocks.length + " 区块：已含 " + present + "，缺失 " + missing + extra;
  syncHead();
}
function populateCats(blocks){
  const sel = $("catFilter");
  const cur = sel.value;
  const cats = Array.from(new Set(blocks.map(b => b.cat))).sort();
  sel.innerHTML = '<option value="">全部分类</option>' + cats.map(c => '<option value="' + esc(c) + '">' + esc(c) + "</option>").join("");
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
  const p = ap(); if (!p){ toast("请先载入补丁字体", true); return; }
  const supply = activeSupply();
  let n = 0;
  state.blocks.forEach(b => {
    if ((supply[b.name] || 0) > 0){ p.selection.add(b.name); n++; }
  });
  renderBlocks();
  renderPatchTabs();
  updateMergeBar();
  toast("已勾选 " + n + " 个可合并区块");
}

// ---- merge bar ----
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
  btn.disabled = true; btn.textContent = "合并中…";
  try {
    const j = await postJSON("/api/merge", { mainToken: state.mainToken, patches, overwriteMain: state.overwriteMain });
    await saveResult(j);
  } catch (e) {
    toast(e.message, true);
  } finally {
    btn.textContent = "合并并下载";
    updateMergeBar();
  }
}
function isDesktop(){
  return !!(window.pywebview && window.pywebview.api && window.pywebview.api.save_font);
}
async function saveResult(j){
  const msg = "已合并 " + fmt(j.mergedCodepoints) + " 个码位 / " + fmt(j.mergedGlyphs) + " 个字形";
  if (isDesktop()){
    const r = await window.pywebview.api.save_font(j.data, j.filename);
    if (r && r.ok) toast(msg + "，已保存：" + r.path);
    else if (r && r.canceled) toast("已取消保存（合并已完成）");
    else toast((r && r.error) || "保存失败", true);
    return;
  }
  const bin = atob(j.data);
  const bytes = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) bytes[i] = bin.charCodeAt(i);
  const blob = new Blob([bytes], { type: "font/ttf" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob); a.download = j.filename; a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 10000);
  toast(msg + "，开始下载");
}

// ---- init ----
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
