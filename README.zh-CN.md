# TTF 字体合并工具

[English](./README.md) | [简体中文](./README.zh-CN.md)

将多个 TrueType 字体的字形合并到一个主体字体中——自动处理 UPEM 缩放、Unicode 区块检测与复合字形。

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)
![Powered by fontTools](https://img.shields.io/badge/Powered%20by-fontTools-orange.svg)

面向字体开发者和本地化工程师的本地工具。载入**主体字体**，查看它缺失了哪些 Unicode 区块和文字，然后**添加多个补丁字体**，按需选择性地合并字形。专为常见场景而设计：让一个中文字体（例如 SimHei）从 Noto 字体获得可读的高棉语、藏文、泰文等——无需手写 fontTools 脚本。

![截图](docs/images/screenshot-main.png)

## 功能特性

- **Unicode 区块分析** —— 125 个区块，含覆盖率统计、文字名称和可读的语言标注
- **多字体合并** —— 一次会话可添加任意数量的补丁字体，每个字体独立标签页、独立选择区块
- **自动 UPEM 缩放** —— 来自 1000 UPEM 补丁字体的字形会被正确缩放到 2048 UPEM 的主体字体中（告别过小字形）
- **复合字形支持** —— 复合字形引用的组件字形会被递归带入
- **覆盖开关** —— 控制补丁字形是否替换主体已有的字形，或仅补充缺失部分
- **冲突处理** —— 当多个补丁覆盖同一码位时，先添加的补丁优先
- **两种运行方式** —— 独立桌面应用（原生窗口，无需浏览器）或经典 Web 界面（开发用）
- **开箱即用** —— fontTools 已内置在 `libs/` 中，从源码运行无需 `pip` 安装

## 目录

- [快速开始](#快速开始)
- [使用流程](#使用流程)
- [工作原理](#工作原理)
- [从源码构建](#从源码构建)
- [测试](#测试)
- [项目结构](#项目结构)
- [限制](#限制)
- [常见问题](#常见问题)
- [参与贡献](#参与贡献)
- [许可证](#许可证)

## 快速开始

### 桌面应用（推荐）

从 [Releases](../../releases) 页面下载 `TtfMergeTool.exe`，双击即可。应用会打开自带窗口——无需 Python、无需浏览器、无需安装。

> 需要 Windows 10/11 及 WebView2 运行时（大多数现代系统已预装）。

### 从源码运行

```powershell
git clone https://github.com/flame-34/ttf-font-merger.git
cd ttf-font-merger
python desktop.py
```

`fontTools` 已内置在 `libs/` 中，无需 `pip install`。

## 使用流程

1. **载入主体字体** —— 拖入或选择一个 `.ttf`。下方表格展示每个 Unicode 区块的覆盖情况：缺失或已含、码位数量、关联的文字和语言。
2. **添加补丁字体** —— 点击"添加补丁字体"可一次添加多个 `.ttf`。每个补丁字体显示为标签页，标注它能提供的码位数。
3. **为每个补丁选择区块** —— 点击标签页切换到该字体，勾选要从它合并的区块。可以给不同补丁分配不同区块（例如一个补高棉语、一个补藏文、一个补泰文）。可用搜索框和分类筛选快速定位。
4. **合并** —— 点击合并按钮，一次性把所有选中的区块合入主体。底部状态栏实时显示补丁数、已选区块数和将合并的码位数。当多个补丁覆盖同一码位时，先添加的补丁优先。
5. **覆盖开关** —— 默认开启。当主体在某区块已有（例如偏小的）字形时，开启会用补丁的字形替换；关闭则只补充主体完全缺失的码位。

## 工作原理

合并引擎（位于 `fontlib.py`）基于 fontTools，工作流程如下：

1. **覆盖率分析** —— 扫描主体字体的 `cmap`（通过 `getBestCmap`），与内置的 Unicode 区块数据集比对。每个区块标记为缺失/已含，并计算覆盖率。
2. **UPEM 缩放** —— 当主体与补丁的 `unitsPerEm` 不同时，计算缩放系数 `main.upem / patch.upem`。所有字形坐标、复合偏移和水平/垂直度量都乘以该系数并用 `otRound` 取整，使 1000 UPEM 的字形在 2048 UPEM 的字体中尺寸正确。
3. **字形复制** —— 每个目标字形从补丁深拷贝，并赋予唯一名称（加后缀避免冲突）。复合字形递归带入其引用的组件，并重算边界框。
4. **多补丁链式合并** —— 补丁按顺序应用到同一个内存中的主体字体。已被前一个补丁提供的码位会被后续补丁跳过，实现确定性的"先到先得"。
5. **表完整性** —— 更新 `maxp.numGlyphs`，重写所有子表的 `cmap`，并重建 `post` 表（format-3 源字体转换为 format 2.0 并重建字形名元数据）。

## 从源码构建

打包独立 `.exe`：

1. 将构建依赖安装到 `libs/`：

```powershell
python -m pip install --target=libs pywebview pyinstaller
```

2. 运行构建脚本：

```powershell
build.bat
```

生成的单文件 `dist\TtfMergeTool.exe`（约 18 MB）。`build.bat` 中的 `PYTHONNOUSERSITE=1` 标志很重要——没有它，PyInstaller 会拖入无关的全局包（torch、numpy），体积膨胀到 200 MB 以上。

开发时以 Web 模式运行：

```powershell
python server.py
```

然后打开 `http://127.0.0.1:8765/`（设置 `PORT` 可改端口；加 `--no-browser` 不自动打开浏览器）。

## 测试

```powershell
python _smoke.py
```

覆盖字体分析、UPEM 缩放、多补丁链式合并和冲突处理，无需启动服务。

HTTP 接口测试——在一个终端启动服务，另一个终端运行：

```powershell
python server.py --no-browser
python _http_smoke.py
```

测试会用 fontBuilder 合成两个最小字体（仅含拉丁字母的主体，以及含希腊/西里尔/中日韩和一个复合字形的补丁），验证完整流程。

## 项目结构

```text
.
├── server.py            # HTTP 服务 + JSON 接口（标准库 http.server）
├── fontlib.py           # 字体分析 + 字形合并（fontTools）
├── unicode_blocks.py    # Unicode 区块数据集（125 个区块，含语言标注）
├── desktop.py           # 桌面窗口启动器（pywebview + WebView2）
├── build.bat            # 一键打包 exe 脚本
├── app.ico              # 应用图标（多分辨率）
├── static/
│   ├── index.html       # 单页界面
│   ├── app.js           # 前端逻辑（多补丁状态管理）
│   ├── style.css        # 样式
│   └── icon.svg         # 矢量应用图标
├── libs/                # 内置 fontTools（已 gitignore，见构建步骤）
├── docs/images/         # 截图
├── _smoke.py            # 逻辑测试
└── _http_smoke.py       # HTTP 接口测试
```

## 限制

- **仅支持 TrueType（glyf）轮廓。** CFF/OTF 轮廓会被检测并给出明确提示，但不参与合并。
- **桌面版为 Windows 平台。** 打包应用使用 WebView2 运行时。Web 界面可在任何装有 Python 3.8+ 的平台上运行。
- **TTC 字体集合。** 只读取 `.ttc` 中的第一个字体。
- **合并产生新文件。** 永远不会修改原始字体文件。

## 常见问题

**可以合并 OTF 字体吗？**
不可以——仅支持带 `glyf` 轮廓的 TrueType（`.ttf`）字体。工具会检测 CFF 轮廓并提示。

**合并后的字形看起来太小，为什么？**
这发生在 UPEM 不同时，正是自动缩放要解决的问题。如果仍然出现，请确认没有把旧的合并结果当作主体重新载入。

**多个补丁可以覆盖同一个区块吗？**
可以。先添加的补丁优先提供字形；后续补丁会跳过已被覆盖的码位。

**会修改我的原始字体吗？**
不会。合并始终产生新的 `_merged.ttf` 文件。

## 参与贡献

欢迎提 Issue 和 Pull Request。提交前请运行测试：

```powershell
python _smoke.py
```

## 许可证

[MIT](./LICENSE)
