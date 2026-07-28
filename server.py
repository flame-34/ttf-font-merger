"""Local web server for the TTF merge tool.

Run with:  python server.py
Then open: http://127.0.0.1:8765/

Endpoints:
  POST /api/analyze   {data: base64}                 -> analysis + mainToken
  POST /api/patch     {data: base64, mainToken}      -> patch coverage + patchToken
  POST /api/merge     {mainToken, patchToken, blocks} -> {data: base64, ...}
"""
import base64
import json
import os
import secrets
import sys
import threading
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import fontlib

HERE = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(HERE, "static")
PORT = int(os.environ.get("PORT", "8765"))

# token -> {"bytes": ..., "filename": ...}; single-user local tool, in-memory.
_STORE = {}
_STORE_LOCK = threading.Lock()


def _store(filename: str, data: bytes) -> str:
    token = secrets.token_hex(12)
    with _STORE_LOCK:
        _STORE[token] = {"bytes": data, "filename": filename}
    return token


def _load(token: str):
    with _STORE_LOCK:
        return _STORE.get(token)


def _json_error(start, code: int, message: str):
    body = json.dumps({"ok": False, "error": message}, ensure_ascii=False).encode("utf-8")
    start(code, [("Content-Type", "application/json; charset=utf-8"),
                 ("Content-Length", str(len(body)))])
    return body


class Handler(BaseHTTPRequestHandler):
    server_version = "TtfMerge/1.0"

    def log_message(self, *args):  # silence default logging
        pass

    # ---- helpers ----------------------------------------------------------
    def _read_body(self) -> bytes:
        length = int(self.headers.get("Content-Length", 0))
        return self.rfile.read(length) if length else b""

    def _send(self, code: int, body: bytes, ctype="application/json; charset=utf-8"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, obj: dict, code: int = 200):
        self._send(code, json.dumps(obj, ensure_ascii=False).encode("utf-8"))

    # ---- GET: static files -------------------------------------------------
    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path == "/" or path == "/index.html":
            return self._serve_file(os.path.join(STATIC_DIR, "index.html"),
                                    "text/html; charset=utf-8")
        if path.startswith("/static/"):
            rel = path[len("/static/"):]
            rel = rel.replace("/", os.sep)
            target = os.path.normpath(os.path.join(STATIC_DIR, rel))
            if not target.startswith(STATIC_DIR):
                return self._send(403, b"Forbidden", "text/plain")
            ctype = {
                ".css": "text/css; charset=utf-8",
                ".js": "application/javascript; charset=utf-8",
                ".html": "text/html; charset=utf-8",
                ".svg": "image/svg+xml",
                ".ico": "image/x-icon",
            }.get(os.path.splitext(target)[1], "application/octet-stream")
            return self._serve_file(target, ctype)
        self._send(404, b"Not Found", "text/plain")

    def _serve_file(self, target: str, ctype: str):
        if not os.path.isfile(target):
            return self._send(404, b"Not Found", "text/plain")
        with open(target, "rb") as fh:
            data = fh.read()
        self._send(200, data, ctype)

    # ---- POST: API --------------------------------------------------------
    def do_POST(self):
        path = self.path.split("?", 1)[0]
        try:
            payload = json.loads(self._read_body().decode("utf-8"))
        except Exception:  # noqa: BLE001
            return self._send_json({"ok": False, "error": "请求体不是有效的 JSON"}, 400)

        try:
            if path == "/api/analyze":
                return self._api_analyze(payload)
            if path == "/api/patch":
                return self._api_patch(payload)
            if path == "/api/merge":
                return self._api_merge(payload)
        except fontlib.FontError as exc:
            return self._send_json({"ok": False, "error": str(exc)}, 400)
        except Exception as exc:  # noqa: BLE001
            import traceback
            traceback.print_exc()
            return self._send_json({"ok": False, "error": "处理出错: %s" % exc}, 500)
        self._send_json({"ok": False, "error": "未知接口: %s" % path}, 404)

    def _b64(self, s) -> bytes:
        if not s:
            raise fontlib.FontError("缺少字体数据")
        return base64.b64decode(s)

    def _api_analyze(self, payload):
        data = self._b64(payload.get("data"))
        token = _store(payload.get("filename", "main.ttf"), data)
        result = fontlib.analyze(data)
        self._send_json({"ok": True, "token": token, **result})

    def _api_patch(self, payload):
        data = self._b64(payload.get("data"))
        main = _load(payload.get("mainToken", ""))
        if not main:
            return self._send_json({"ok": False, "error": "主体字体已失效，请重新载入"}, 400)
        token = _store(payload.get("filename", "patch.ttf"), data)
        result = fontlib.patch_supply(main["bytes"], data)
        self._send_json({"ok": True, "token": token, **result})

    def _api_merge(self, payload):
        main = _load(payload.get("mainToken", ""))
        if not main:
            return self._send_json({"ok": False, "error": "主体字体令牌已失效，请重新载入"}, 400)
        patches_req = payload.get("patches") or []
        # Backward-compatible single-patch form.
        if not patches_req and payload.get("patchToken"):
            patches_req = [{"token": payload["patchToken"], "blocks": payload.get("blocks") or []}]
        patches = []
        for p in patches_req:
            rec = _load(p.get("token", ""))
            if not rec:
                return self._send_json({"ok": False, "error": "补丁字体令牌已失效，请重新载入"}, 400)
            blocks = p.get("blocks") or []
            if blocks:
                patches.append((rec["bytes"], blocks))
        if not patches:
            return self._send_json({"ok": False, "error": "请至少添加一个补丁字体并选择区块"}, 400)
        overwrite = payload.get("overwriteMain", True)
        result = fontlib.merge_multi(main["bytes"], patches, overwrite)
        b64 = base64.b64encode(result["bytes"]).decode("ascii")
        base = os.path.splitext(os.path.basename(main["filename"]))[0] or "merged"
        filename = "%s_merged.ttf" % base
        self._send_json({
            "ok": True,
            "data": b64,
            "filename": filename,
            "mergedCodepoints": result["mergedCodepoints"],
            "mergedGlyphs": result["mergedGlyphs"],
            "details": result.get("details", []),
        })


def open_browser(url: str):
    try:
        os.startfile(url)  # type: ignore[attr-defined]
    except Exception:  # noqa: BLE001
        pass


def main():
    if not os.path.isdir(os.path.join(HERE, "static")):
        print("缺少 static/ 目录", file=sys.stderr)
        sys.exit(1)
    httpd = create_server()
    if "--no-browser" not in sys.argv:
        threading.Thread(target=open_browser, args=(httpd.url,), daemon=True).start()
    run_server(httpd)


def create_server():
    """Create (but do not run) the HTTP server. Returns the httpd with a .url."""
    if not os.path.isdir(os.path.join(HERE, "static")):
        print("缺少 static/ 目录", file=sys.stderr)
        sys.exit(1)
    httpd = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    httpd.url = "http://127.0.0.1:%d/" % PORT
    return httpd


def run_server(httpd):
    """Run the server on the calling thread until interrupted."""
    print("TTF 合并工具已启动: %s" % getattr(httpd, "url", ""))
    print("按 Ctrl+C 退出。")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n已退出。")


if __name__ == "__main__":
    main()
