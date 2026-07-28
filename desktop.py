"""Desktop launcher: runs the local server in a thread and shows the UI in a
native window via pywebview (uses Windows' built-in WebView2). No browser needed.

Run with:  python desktop.py
"""
import base64
import os
import socket
import sys
import threading
import time

_HERE = os.path.dirname(os.path.abspath(__file__))
_LIBS = os.path.join(_HERE, "libs")
if os.path.isdir(_LIBS) and _LIBS not in sys.path:
    sys.path.insert(0, _LIBS)

import server  # noqa: E402
import webview  # noqa: E402


def _wait_for_port():
    deadline = time.time() + 10
    while time.time() < deadline:
        try:
            s = socket.create_connection(("127.0.0.1", server.PORT), timeout=0.5)
            s.close()
            return True
        except OSError:
            time.sleep(0.1)
    return False


class Api:
    """JS-callable bridge. Exposed to the page as window.pywebview.api."""

    def is_desktop(self):
        return True

    def save_font(self, b64data, filename):
        """Show a native Save As dialog and write the merged font bytes."""
        try:
            data = base64.b64decode(b64data)
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "error": "数据解码失败: %s" % exc}
        active = webview.active_window() or (webview.windows[0] if webview.windows else None)
        if active is None:
            return {"ok": False, "error": "没有可用窗口"}
        if not filename.lower().endswith(".ttf"):
            filename += ".ttf"
        result = active.create_file_dialog(webview.SAVE_DIALOG, save_filename=filename)
        if not result:
            return {"ok": False, "canceled": True}
        path = result if isinstance(result, str) else result[0]
        try:
            with open(path, "wb") as fh:
                fh.write(data)
        except Exception as exc:  # noqa: BLE001
            return {"ok": False, "error": "写入失败: %s" % exc}
        return {"ok": True, "path": path}


def main():
    t = threading.Thread(target=lambda: server.create_server().serve_forever(), daemon=True)
    t.start()
    _wait_for_port()
    url = "http://127.0.0.1:%d/" % server.PORT
    webview.create_window(
        "TTF 字体合并工具",
        url,
        js_api=Api(),
        width=1320,
        height=900,
        min_size=(900, 600),
    )
    webview.start()
    os._exit(0)


if __name__ == "__main__":
    main()
