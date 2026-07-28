# TTF 字体合并工具

本地工具（浏览器版 / 桌面单文件版均可）：选择**主体字体** → 用**多个补丁字体**分别补齐不同语言的字形 → 一键合并保存。

## 桌面单文件版（推荐，无需浏览器）

双击 `dist\TtfMergeTool.exe` 即可，弹出自带窗口（基于 Windows 内置 WebView2），完全不需要浏览器。合并后的字体通过系统"另存为"对话框保存。

也可在不打包时运行：`python desktop.py`（打开窗口，不自动开浏览器），用于打包前测试。

### 打包成 exe

首次需把打包依赖装进 `libs/`（已装可跳过）：

    python -m pip install --target=libs pywebview pyinstaller

然后执行：

    build.bat

生成的单文件在 `dist\TtfMergeTool.exe`（约 18 MB）。

要点：build.bat 里设置了 `PYTHONNOUSERSITE=1`，否则会把用户全局 site-packages 里的 torch/numpy 等一起打进去，体积膨胀到 200MB+。

运行依赖：目标机器需有 WebView2 运行时（Windows 10/11 通常自带；若缺失会提示，安装"Microsoft Edge WebView2 Runtime"即可）。

## 浏览器版（开发调试）

在项目目录执行：

    python server.py

启动后会自动打开浏览器，地址为 http://127.0.0.1:8765/ （可用 PORT=9000 指定端口，加 --no-browser 不自动开浏览器）。按 Ctrl+C 退出。

## 依赖

仅依赖 fontTools，已随项目内置在 libs/ 目录，开箱即用（Python 3.8+）。
若想改用系统安装的版本：python -m pip install fontTools，并删除 libs/ 即可。

## 使用流程

1. 主体字体：拖入或选择一个 .ttf，下方表格展示每个 Unicode 区块的覆盖情况（缺失/已含、覆盖码位数、对应语言）。
2. 补丁字体：点击"添加补丁字体"可一次添加多个 .ttf。每个补丁字体显示为上方一个标签页，标签上标注已选区块数。
3. 选择区块：点击标签页切换到某个补丁字体，勾选该字体要合并的区块。可添加多个补丁，分别为每个选不同的区块（例如一个补高棉语、一个补藏文）。可用搜索、分类筛选快速定位。
4. 合并并下载：点击按钮，一次性把所有补丁字体的选中区块合入主体。多个补丁间若有码位重叠，先添加的补丁优先。合并栏实时显示补丁数、已选区块数与将合并的码位数。
5. 覆盖开关：默认开启"覆盖主体已有字形"——若主体本身就有某些字形（如 SimHei 自带偏小的高棉语），补丁会用更大更好的字形替换它。关闭则只补充主体缺失的码位。

## 说明与限制

- 支持 TrueType（glyf 轮廓）字体，即最常见的 .ttf。
- 暂不支持 CFF/OTF 轮廓（会给出明确提示）。
- 合并只针对"补丁有、主体没有"的码位，不会改动主体已有的字形。
- 复合字形（composite）会自动连同引用的组件字形一起带入。
- 合并产生新文件，不会修改原始字体文件。

## 文件结构

- server.py：基于 Python 标准库 http.server 的本地服务与 API
- fontlib.py：字体解析、区块覆盖统计、字形合并（fontTools）
- unicode_blocks.py：Unicode 区块数据集（含语言标注）
- static/：前端页面（index.html / app.js / style.css）
- libs/：内置 fontTools
- _smoke.py / _http_smoke.py：自动化测试
- desktop.py：桌面窗口启动器（pywebview，供打包与桌面运行）
- build.bat：打包成单文件 exe 的脚本

## 测试

    python _smoke.py                  # 字体解析/统计/合并逻辑（无需启动服务）
    python server.py --no-browser     # 另开终端启动服务
    python _http_smoke.py             # HTTP 接口端到端

测试会用 fontBuilder 生成两个合成字体（主体仅含基本拉丁，补丁含希腊/西里尔/中日韩及一个复合字形），完整走通分析→统计→合并→校验流程。
