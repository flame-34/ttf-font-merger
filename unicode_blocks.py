# Unicode block dataset used to detect font coverage gaps.
# Each entry: (start, end, english_name, script, lang_zh, category)
# Ranges follow Unicode 15.1 block names. Coverage is counted against the
# font's cmap, so "covered" means the font actually maps that codepoint.
 
BLOCKS = [
    # ---- Latin / European basics ----
    (0x0000, 0x007F, "Basic Latin", "Latin", "拉丁字母-基础 (英语/西欧)", "拉丁"),
    (0x0080, 0x00FF, "Latin-1 Supplement", "Latin", "拉丁字母-补充 (西欧特殊字符)", "拉丁"),
    (0x0100, 0x017F, "Latin Extended-A", "Latin", "拉丁字母扩展A (东欧)", "拉丁"),
    (0x0180, 0x024F, "Latin Extended-B", "Latin", "拉丁字母扩展B", "拉丁"),
    (0x0250, 0x02AF, "IPA Extensions", "Latin", "国际音标扩展", "符号"),
    (0x02B0, 0x02FF, "Spacing Modifier Letters", "Common", "间距修饰符", "符号"),
    (0x0300, 0x036F, "Combining Diacritical Marks", "Inherited", "组合附加符号", "符号"),
    (0x0370, 0x03FF, "Greek and Coptic", "Greek", "希腊语/科普特语", "欧洲"),
    (0x0400, 0x04FF, "Cyrillic", "Cyrillic", "西里尔字母 (俄语/乌克兰语等)", "欧洲"),
    (0x0500, 0x052F, "Cyrillic Supplement", "Cyrillic", "西里尔字母补充", "欧洲"),
    (0x0530, 0x058F, "Armenian", "Armenian", "亚美尼亚语", "欧洲"),
    # ---- Middle East ----
    (0x0590, 0x05FF, "Hebrew", "Hebrew", "希伯来语 (以色列)", "中东"),
    (0x0600, 0x06FF, "Arabic", "Arabic", "阿拉伯语", "中东"),
    (0x0700, 0x074F, "Syriac", "Syriac", "叙利亚语", "中东"),
    (0x0750, 0x077F, "Arabic Supplement", "Arabic", "阿拉伯语补充", "中东"),
    (0x0800, 0x083F, "Samaritan", "Samaritan", "撒马利亚文", "中东"),
    (0x0840, 0x085F, "Mandaic", "Mandaic", "曼达恩文", "中东"),
    # ---- South Asia ----
    (0x0900, 0x097F, "Devanagari", "Devanagari", "天城文 (印地语/梵语)", "南亚"),
    (0x0980, 0x09FF, "Bengali", "Bengali", "孟加拉语", "南亚"),
    (0x0A00, 0x0A7F, "Gurmukhi", "Gurmukhi", "古木基文 (旁遮普语)", "南亚"),
    (0x0A80, 0x0AFF, "Gujarati", "Gujarati", "古吉拉特语", "南亚"),
    (0x0B00, 0x0B7F, "Oriya", "Oriya", "奥里亚语", "南亚"),
    (0x0B80, 0x0BFF, "Tamil", "Tamil", "泰米尔语", "南亚"),
    (0x0C00, 0x0C7F, "Telugu", "Telugu", "泰卢固语", "南亚"),
    (0x0C80, 0x0CFF, "Kannada", "Kannada", "卡纳达语", "南亚"),
    (0x0D00, 0x0D7F, "Malayalam", "Malayalam", "马拉雅拉姆语", "南亚"),
    (0x0D80, 0x0DFF, "Sinhala", "Sinhala", "僧伽罗语 (斯里兰卡)", "南亚"),
    (0x0780, 0x07BF, "Thaana", "Thaana", "塔安那文 (马尔代夫)", "南亚"),
    # ---- Southeast / East Asia scripts ----
    (0x0E00, 0x0E7F, "Thai", "Thai", "泰语", "东南亚"),
    (0x0E80, 0x0EFF, "Lao", "Lao", "老挝语", "东南亚"),
    (0x0F00, 0x0FFF, "Tibetan", "Tibetan", "藏文", "东亚"),
    (0x1000, 0x109F, "Myanmar", "Myanmar", "缅甸语", "东南亚"),
    (0x10A0, 0x10FF, "Georgian", "Georgian", "格鲁吉亚语", "欧洲"),
    (0x1780, 0x17FF, "Khmer", "Khmer", "高棉语 (柬埔寨)", "东南亚"),
    (0x1800, 0x18AF, "Mongolian", "Mongolian", "蒙古文", "东亚"),
    (0x1100, 0x11FF, "Hangul Jamo", "Hangul", "韩文字母", "东亚"),
    # ---- Africa / Americas / Other scripts ----
    (0x1200, 0x137F, "Ethiopic", "Ethiopic", "埃塞俄比亚语 (阿姆哈拉语)", "非洲"),
    (0x07C0, 0x07FF, "NKo", "Nko", "恩科文 (西非)", "非洲"),
    (0x13A0, 0x13FF, "Cherokee", "Cherokee", "切罗基语", "美洲土著"),
    (0x1400, 0x167F, "Unified Canadian Aboriginal Syllabics", "UCAS", "加拿大原住民音节", "美洲土著"),
    # ---- General punctuation & symbols ----
    (0x2000, 0x206F, "General Punctuation", "Common", "通用标点", "标点"),
    (0x2070, 0x209F, "Superscripts and Subscripts", "Common", "上下标", "符号"),
    (0x20A0, 0x20CF, "Currency Symbols", "Common", "货币符号", "符号"),
    (0x20D0, 0x20FF, "Combining Diacritical Marks for Symbols", "Inherited", "符号组合附加符", "符号"),
    (0x2100, 0x214F, "Letterlike Symbols", "Common", "字母式符号", "符号"),
    (0x2150, 0x218F, "Number Forms", "Common", "数字形式", "符号"),
    (0x2190, 0x21FF, "Arrows", "Common", "箭头", "符号"),
    (0x2200, 0x22FF, "Mathematical Operators", "Common", "数学运算符", "符号"),
    (0x2300, 0x23FF, "Miscellaneous Technical", "Common", "杂项技术符号", "符号"),
    (0x2400, 0x243F, "Control Pictures", "Common", "控制符图形", "符号"),
    (0x2440, 0x245F, "Optical Character Recognition", "Common", "光学识别符号", "符号"),
    (0x2460, 0x24FF, "Enclosed Alphanumerics", "Common", "带圈字母数字", "符号"),
    (0x2500, 0x257F, "Box Drawing", "Common", "制表符", "符号"),
    (0x2580, 0x259F, "Block Elements", "Common", "方块元素", "符号"),
    (0x25A0, 0x25FF, "Geometric Shapes", "Common", "几何图形", "符号"),
    (0x2600, 0x26FF, "Miscellaneous Symbols", "Common", "杂项符号", "符号"),
    (0x2700, 0x27BF, "Dingbats", "Common", "杂锦符号", "符号"),
    (0x27C0, 0x27EF, "Miscellaneous Mathematical Symbols-A", "Common", "数学符号A", "符号"),
    (0x27F0, 0x27FF, "Supplemental Arrows-A", "Common", "补充箭头A", "符号"),
    (0x2800, 0x28FF, "Braille Patterns", "Braille", "盲文", "符号"),
    (0x2B00, 0x2BFF, "Miscellaneous Symbols and Arrows", "Common", "杂项符号与箭头", "符号"),
    # ---- CJK radicals, symbols, kana, bopomofo ----
    (0x2E80, 0x2EFF, "CJK Radicals Supplement", "Han", "中日韩部首补充", "东亚"),
    (0x2F00, 0x2FDF, "Kangxi Radicals", "Han", "康熙部首", "东亚"),
    (0x2FF0, 0x2FFF, "Ideographic Description Characters", "Han", "表意文字描述符", "东亚"),
    (0x3000, 0x303F, "CJK Symbols and Punctuation", "Han", "中日韩符号与标点", "东亚"),
    (0x3040, 0x309F, "Hiragana", "Hiragana", "平假名 (日文)", "东亚"),
    (0x30A0, 0x30FF, "Katakana", "Katakana", "片假名 (日文)", "东亚"),
    (0x3100, 0x312F, "Bopomofo", "Bopomofo", "注音符号 (中文)", "东亚"),
    (0x3130, 0x318F, "Hangul Compatibility Jamo", "Hangul", "韩文兼容字母", "东亚"),
    (0x3190, 0x319F, "Kanbun", "Han", "汉文注释标记", "东亚"),
    (0x31A0, 0x31BF, "Bopomofo Extended", "Bopomofo", "注音符号扩展", "东亚"),
    (0x31F0, 0x31FF, "Katakana Phonetic Extensions", "Katakana", "片假名扩展", "东亚"),
    (0x3200, 0x32FF, "Enclosed CJK Letters and Months", "Han", "带圈中日韩字母与月份", "东亚"),
    (0x3300, 0x33FF, "CJK Compatibility", "Han", "中日韩兼容字符", "东亚"),
    (0x3400, 0x4DBF, "CJK Unified Ideographs Extension A", "Han", "中日韩统一汉字扩展A", "东亚"),
    (0x4DC0, 0x4DFF, "Yijing Hexagram Symbols", "Common", "易经卦象", "符号"),
    (0x4E00, 0x9FFF, "CJK Unified Ideographs", "Han", "中日韩统一汉字 (中文/日文/韩文)", "东亚"),
    (0xA000, 0xA48F, "Yi Syllables", "Yi", "彝文音节", "东亚"),
    (0xA490, 0xA4CF, "Yi Radicals", "Yi", "彝文字根", "东亚"),
    (0xAC00, 0xD7AF, "Hangul Syllables", "Hangul", "韩文音节", "东亚"),
    (0xD7B0, 0xD7FF, "Hangul Jamo Extended-B", "Hangul", "韩文字母扩展B", "东亚"),
    (0xE000, 0xF8FF, "Private Use Area", "Private", "专用区", "专用区"),
    (0xF900, 0xFAFF, "CJK Compatibility Ideographs", "Han", "中日韩兼容汉字", "东亚"),
    # ---- Presentation / compatibility forms ----
    (0xFB00, 0xFB4F, "Alphabetic Presentation Forms", "Latin", "字母变形形式", "兼容"),
    (0xFB50, 0xFDFF, "Arabic Presentation Forms-A", "Arabic", "阿拉伯变形形式A", "兼容"),
    (0xFE00, 0xFE0F, "Variation Selectors", "Inherited", "变体选择符", "符号"),
    (0xFE20, 0xFE2F, "Combining Half Marks", "Inherited", "组合半角符号", "符号"),
    (0xFE30, 0xFE4F, "CJK Compatibility Forms", "Han", "中日韩兼容形式", "兼容"),
    (0xFE50, 0xFE6F, "Small Form Variants", "Common", "小型变体", "兼容"),
    (0xFE70, 0xFEFF, "Arabic Presentation Forms-B", "Arabic", "阿拉伯变形形式B", "兼容"),
    (0xFF00, 0xFFEF, "Halfwidth and Fullwidth Forms", "Common", "全角与半角形式", "兼容"),
    (0xFFF0, 0xFFFF, "Specials", "Common", "特殊字符区", "符号"),
    # ---- Supplementary Multilingual Plane (ancient + symbols) ----
    (0x10000, 0x1007F, "Linear B Syllabary", "Linear B", "线形文字B音节", "古文字"),
    (0x10080, 0x100FF, "Linear B Ideograms", "Linear B", "线形文字B表意", "古文字"),
    (0x10300, 0x1032F, "Old Italic", "Old Italic", "古意大利文", "古文字"),
    (0x10330, 0x1034F, "Gothic", "Gothic", "哥特文", "古文字"),
    (0x10380, 0x1039F, "Ugaritic", "Ugaritic", "乌加里特文", "古文字"),
    (0x10400, 0x1044F, "Deseret", "Deseret", "德塞雷特文", "古文字"),
    (0x10450, 0x1047F, "Shavian", "Shavian", "萧伯纳文", "古文字"),
    (0x10480, 0x104AF, "Osmanya", "Osmanya", "奥斯曼亚文", "古文字"),
    (0x10800, 0x1083F, "Cypriot Syllabary", "Cypriot", "塞浦路斯音节", "古文字"),
    (0x10A00, 0x10A5F, "Kharoshthi", "Kharoshthi", "佉卢文", "古文字"),
    (0x12000, 0x123FF, "Cuneiform", "Cuneiform", "楔形文字", "古文字"),
    (0x12400, 0x1247F, "Cuneiform Numbers and Punctuation", "Cuneiform", "楔形数字与标点", "古文字"),
    (0x1D000, 0x1D0FF, "Byzantine Musical Symbols", "Common", "拜占庭音乐符号", "符号"),
    (0x1D300, 0x1D35F, "Tai Xuan Jing Symbols", "Common", "太玄经符号", "符号"),
    (0x1D400, 0x1D7FF, "Mathematical Alphanumeric Symbols", "Common", "数学字母数字符号", "符号"),
    (0x1F000, 0x1F02F, "Mahjong Tiles", "Common", "麻将牌", "符号"),
    (0x1F030, 0x1F09F, "Domino Tiles", "Common", "多米诺骨牌", "符号"),
    (0x1F0A0, 0x1F0FF, "Playing Cards", "Common", "扑克牌", "符号"),
    (0x1F100, 0x1F1FF, "Enclosed Alphanumeric Supplement", "Common", "带圈字母数字补充", "符号"),
    (0x1F200, 0x1F2FF, "Enclosed Ideographic Supplement", "Common", "带圈表意文字补充", "符号"),
    (0x1F300, 0x1F5FF, "Miscellaneous Symbols and Pictographs", "Common", "杂项符号与象形 (含部分emoji)", "表情"),
    (0x1F600, 0x1F64F, "Emoticons", "Common", "表情符号", "表情"),
    (0x1F650, 0x1F67F, "Ornamental Dingbats", "Common", "装饰杂锦符号", "符号"),
    (0x1F680, 0x1F6FF, "Transport and Map Symbols", "Common", "交通与地图符号", "表情"),
    (0x1F700, 0x1F77F, "Alchemical Symbols", "Common", "炼金术符号", "符号"),
    (0x1F900, 0x1F9FF, "Supplemental Symbols and Pictographs", "Common", "补充符号与象形", "表情"),
    (0x1FA70, 0x1FAFF, "Symbols and Pictographs Extended-A", "Common", "符号象形扩展A", "表情"),
    # ---- CJK extensions (astral plane) ----
    (0x20000, 0x2A6DF, "CJK Unified Ideographs Extension B", "Han", "中日韩统一汉字扩展B", "东亚"),
    (0x2A700, 0x2B73F, "CJK Unified Ideographs Extension C", "Han", "中日韩统一汉字扩展C", "东亚"),
    (0x2B740, 0x2B81F, "CJK Unified Ideographs Extension D", "Han", "中日韩统一汉字扩展D", "东亚"),
    (0x2B820, 0x2CEAF, "CJK Unified Ideographs Extension E", "Han", "中日韩统一汉字扩展E", "东亚"),
    (0x2CEB0, 0x2EBEF, "CJK Unified Ideographs Extension F", "Han", "中日韩统一汉字扩展F", "东亚"),
    (0x2F800, 0x2FA1F, "CJK Compatibility Ideographs Supplement", "Han", "中日韩兼容汉字补充", "东亚"),
]
 
# Precompute sorted structures for fast codepoint -> block lookup.
_BLOCKS_SORTED = sorted(BLOCKS, key=lambda b: b[0])
_STARTS = [b[0] for b in _BLOCKS_SORTED]
 
 
def _find_block_index(cp):
    """Return index into _BLOCKS_SORTED for a codepoint, or -1 if none."""
    import bisect
    i = bisect.bisect_right(_STARTS, cp) - 1
    if i < 0:
        return -1
    b = _BLOCKS_SORTED[i]
    if cp <= b[1]:
        return i
    return -1
 
 
def block_of(cp):
    """Return the block tuple (start,end,name,script,lang,cat) for cp, or None."""
    i = _find_block_index(cp)
    return _BLOCKS_SORTED[i] if i >= 0 else None
