from http.server import HTTPServer, BaseHTTPRequestHandler
import json, urllib.parse

MEM_FILE = "memories.json"

def load():
    try:
        with open(MEM_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save(memories):
    with open(MEM_FILE, "w", encoding="utf-8") as f:
        json.dump(memories, f, ensure_ascii=False, indent=2)

TOOLS = [
    {
        "name": "read_memory",
        "description": "在记忆库里按关键词查找记忆",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "要查找的关键词"}
            },
            "required": ["query"]
        }
    },
    {
        "name": "write_memory",
        "description": "把一条新记忆存进记忆库",
        "inputSchema": {
            "type": "object",
            "properties": {
                "content": {"type": "string", "description": "要保存的记忆内容"}
            },
            "required": ["content"]
        }
    }
]

PAGE = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>清明与秋 · 记忆库</title></head>
<body style="font-family:sans-serif;max-width:400px;margin:40px auto;text-align:center">
<h2>记忆库</h2>
<form method="POST" action="/save">
<textarea name="content" rows="6" style="width:100%" placeholder="输入要存的记忆"></textarea><br><br>
<button type="submit" style="padding:10px 30px;font-size:16px">保存</button>
</form>
</body></html>"""

class Handler(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _sse(self, obj, code=200):
        data = json.dumps(obj, ensure_ascii=False).encode()
        body = b"event: message\ndata: " + data + b"\n\n"
        self.send_response(code)
        self._cors()
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _json(self, obj, code=200):
        data = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self._cors()
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _html(self, text, code=200):
        body = text.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_GET(self):
        print("收到GET:", self.path)
        if self.path in ("/", "/index.html"):
            self._html(PAGE)
        else:
            self._html("not found", 404)

    def do_POST(self):
        ctype = self.headers.get("Content-Type", "")
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length)
        if "application/json" in ctype:
            try:
                req = json.loads(raw)
            except Exception:
                self._sse({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error"}})
                return
            print("收到POST:", req)
            method = req.get("method", "")
            rid = req.get("id")
            if "id" not in req:
                self.send_response(204)
                self._cors()
                self.send_header("Content-Length", "0")
                self.end_headers()
                return
            if method == "initialize":
                version = req.get("params", {}).get("protocolVersion", "2025-06-18")
                self._sse({"jsonrpc": "2.0", "id": rid, "result": {
                    "protocolVersion": version,
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "qingming-memory", "version": "1.0.0"}
                }})
            elif method == "tools/list":
                self._sse({"jsonrpc": "2.0", "id": rid, "result": {"tools": TOOLS}})
            elif method == "tools/call":
                params = req.get("params", {})
                name = params.get("name", "")
                args = params.get("arguments", {})
                if name == "read_memory":
                    q = args.get("query", "")
                    hits = [m for m in load() if q in m]
                    text = "\n".join(hits) if hits else "没有找到相关记忆"
                    self._json({"jsonrpc": "2.0", "id": rid, "result": {"content": [{"type": "text", "text": text}]}})
                elif name == "write_memory":
                    content = args.get("content", "")
                    memories = load()
                    memories.append(content)
                    save(memories)
                    self._json({"jsonrpc": "2.0", "id": rid, "result": {"content": [{"type": "text", "text": "已保存"}]}})
                else:
                    self._json({"jsonrpc": "2.0", "id": rid, "error": {"code": -32601, "message": "Method not found"}})
            else:
                self._sse({"jsonrpc": "2.0", "id": rid, "error": {"code": -32601, "message": "Method not found"}})
        elif "x-www-form-urlencoded" in ctype:
            params = urllib.parse.parse_qs(raw.decode("utf-8"))
            content = params.get("content", [""])[0].strip()
            if content:
                memories = load()
                memories.append(content)
                save(memories)
                self._html("<h2>已保存</h2><p><a href='/'>再存一条</a></p>")
            else:
                self._html("<h2>空的，没保存</h2><p><a href='/'>回去</a></p>")
        else:
            self._html("unknown request", 400)

    def log_message(self, fmt, *args):
        print(fmt % args)

HTTPServer(("127.0.0.1", 8000), Handler).serve_forever()
