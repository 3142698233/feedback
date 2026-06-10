"""
DeepSeek API proxy + Tag data API
Usage: python3 proxy.py
"""
import json, urllib.request, urllib.error, ssl, os, threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

PORT = 3001
API_KEY = "sk-1b1a962fbcb54abfb8526ec9e80d29f5"
DEEPSEEK_URL = "https://api.deepseek.com/v1/chat/completions"

# Blessings JSON file storage
BLESSINGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "blessings.json")
_blessings_lock = threading.Lock()

# Load tag data at startup
_tags_data = {}
_tags_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tags.json")
try:
    with open(_tags_file, "r", encoding="utf-8") as f:
        _tags_data = json.load(f)
    subj_count = len(_tags_data.get("subjects", {}))
    print(f"Loaded tags.json: {subj_count} subjects, {len(_tags_data.get('focusOpts',{}))} focus grades")
except Exception as e:
    print(f"WARNING: Failed to load tags.json: {e}")


class Proxy(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print(f"[{self.log_date_time_string()}] {args[0]}")

    def send_cors(self, methods="POST, OPTIONS"):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", methods)

    def _json_response(self, data, status=200):
        self.send_response(status)
        self.send_cors("GET, POST, OPTIONS")
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def _read_blessings(self):
        """Read blessings from JSON file (thread-safe)"""
        try:
            if os.path.exists(BLESSINGS_FILE):
                with open(BLESSINGS_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            print(f"ERROR reading blessings.json: {e}")
        return []

    def _write_blessings(self, data):
        """Write blessings to JSON file (thread-safe with lock)"""
        with _blessings_lock:
            try:
                with open(BLESSINGS_FILE, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False)
            except Exception as e:
                print(f"ERROR writing blessings.json: {e}")

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_cors("GET, POST, OPTIONS")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        params = parse_qs(parsed.query)

        # GET /api/tags/all - return all tag data
        if path == "/api/tags/all":
            self._json_response(_tags_data)
            return

        # GET /api/tags?subject=math&grade=primary - return tags for one subject
        if path == "/api/tags":
            subject = (params.get("subject", [""])[0]).strip()
            grade = (params.get("grade", [""])[0]).strip()
            if not subject or not grade:
                self._json_response({"error": "subject and grade required"}, 400)
                return
            sj_data = _tags_data.get("subjects", {}).get(subject)
            if not sj_data:
                self._json_response({"error": f"unknown subject: {subject}"}, 404)
                return
            # Resolve grade: grade-structured subjects have primary/junior/senior/kindergarten
            if any(k in sj_data for k in ("primary", "junior", "senior", "kindergarten")):
                g = sj_data.get(grade) or sj_data.get("primary") or sj_data.get("junior")
                result = {
                    "subject": subject,
                    "grade": grade,
                    "strengths": g.get("strengths", []) if g else [],
                    "weaks": g.get("weaks", []) if g else [],
                    "homework": sj_data.get("homework", [])
                }
            else:
                # Flat subject (e.g. quannao)
                result = {
                    "subject": subject,
                    "grade": grade,
                    "strengths": sj_data.get("strengths", []),
                    "weaks": sj_data.get("weaks", []),
                    "homework": sj_data.get("homework", [])
                }
            self._json_response(result)
            return

        # GET /api/opts - return focus/understand/participate options
        if path == "/api/opts":
            self._json_response({
                "focusOpts": _tags_data.get("focusOpts", {}),
                "understandOpts": _tags_data.get("understandOpts", {}),
                "participateOpts": _tags_data.get("participateOpts", {})
            })
            return

        # GET /api/blessings - return all blessings
        if path == "/api/blessings":
            try:
                data = self._read_blessings()
                data.sort(key=lambda x: x.get("id", 0), reverse=True)
                self._json_response(data[:500])
            except Exception as e:
                self._json_response({"error": str(e)}, 500)
            return

        # Unknown GET path
        self._json_response({"error": "not found"}, 404)

    def do_POST(self):
        # POST /api/blessings - save new blessing
        if self.path == "/api/blessings":
            try:
                length = int(self.headers.get("Content-Length", 0))
                entry = json.loads(self.rfile.read(length))
                if not entry.get("id") or not entry.get("school") or not entry.get("bless"):
                    self._json_response({"error": "missing required fields: id, school, bless"}, 400)
                    return
                # Reject script tags
                if "<script" in json.dumps(entry, ensure_ascii=False).lower():
                    self._json_response({"error": "invalid content"}, 400)
                    return
                # Truncate long fields
                if len(entry.get("bless", "")) > 200:
                    entry["bless"] = entry["bless"][:200]
                if len(entry.get("school", "")) > 50:
                    entry["school"] = entry["school"][:50]
                if entry.get("uni") and len(entry["uni"]) > 60:
                    entry["uni"] = entry["uni"][:60]
                # Limit avatar size
                avatar = entry.get("avatar") or {}
                data_url = avatar.get("dataURL", "") if isinstance(avatar, dict) else ""
                if len(data_url) > 100000:
                    entry["avatar"]["dataURL"] = ""
                data = self._read_blessings()
                if not any(d.get("id") == entry["id"] for d in data):
                    data.append(entry)
                    self._write_blessings(data)
                self._json_response({"ok": True, "total": len(data)})
            except Exception as e:
                self._json_response({"error": str(e)}, 500)
            return

        # 通用 DeepSeek 代理
        def _proxy_deepseek(messages, temperature=0.7, max_tokens=1000):
            req_body = json.dumps({
                "model": "deepseek-chat",
                "messages": messages,
                "temperature": temperature,
                "max_completion_tokens": max_tokens
            }).encode("utf-8")
            ctx = ssl.create_default_context()
            req = urllib.request.Request(DEEPSEEK_URL, data=req_body, headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {API_KEY}"
            })
            resp = urllib.request.urlopen(req, timeout=60, context=ctx)
            result = json.loads(resp.read().decode("utf-8"))
            if result.get("choices") and result["choices"][0]:
                return {"ok": True, "text": result["choices"][0]["message"]["content"]}
            err = result.get("error", {}).get("message", "no response from DeepSeek")
            return {"ok": False, "error": err}

        length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(length))

        # /api/chat — 通用聊天（家长沟通等）
        if self.path in ("/api/chat", "/api/parent-chat"):
            messages = body.get("messages", [])
            if not messages:
                self._json_response({"error": "messages is required"}, 400)
                return
            try:
                result = _proxy_deepseek(messages, body.get("temperature", 0.7), body.get("max_tokens", 500))
                self._json_response({"text": result["text"]} if result["ok"] else {"error": result["error"]}, 200 if result["ok"] else 500)
            except Exception as e:
                self._json_response({"error": str(e)}, 500)
            return

        # /api/polish — 反馈润色
        if self.path == "/api/polish":
            draft = body.get("draft", "").strip()
            sys_prompt = body.get("sysPrompt", "你是一个专业的课后反馈润色助手。")
            if not draft:
                self._json_response({"error": "draft is required"}, 400)
                return
            try:
                result = _proxy_deepseek([
                    {"role": "system", "content": sys_prompt},
                    {"role": "user", "content": f"请改写以下反馈草稿：\n\n{draft}"}
                ], 0.7, 1000)
                self._json_response({"text": result["text"]} if result["ok"] else {"error": result["error"]}, 200 if result["ok"] else 500)
            except Exception as e:
                self._json_response({"error": str(e)}, 500)
            return

        self._json_response({"error": "not found"}, 404)


if __name__ == "__main__":
    server = HTTPServer(("127.0.0.1", PORT), Proxy)
    print(f"API server running on http://127.0.0.1:{PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()
