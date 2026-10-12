#!/usr/bin/env python3
import argparse
import datetime as _dt
import json
import mimetypes
import os
from pathlib import Path
import signal
import sys
import threading
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent
STATIC = ROOT / "static"
write_lock = threading.Lock()


def utc_now():
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")


def load_json(path, default=None):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        if default is not None:
            return default
        raise


def atomic_write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.parent / (".%s.tmp.%s.%s" % (path.name, os.getpid(), threading.get_ident()))
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)


def collect_task_ids(tasks_doc):
    ids = set()
    for section in tasks_doc.get("sections", []):
        for task in section.get("tasks", []):
            tid = task.get("id")
            if tid:
                ids.add(str(tid))
    return ids


class ReviewHandler(BaseHTTPRequestHandler):
    server_version = "BlindReview/1.0"

    def log_message(self, fmt, *args):
        if getattr(self.server, "quiet", False):
            return
        sys.stderr.write("%s %s\n" % (self.command, self.path))

    def send_json(self, status, data):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def send_text(self, status, body, content_type="text/plain; charset=utf-8"):
        raw = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(raw)

    def read_json_body(self):
        length = int(self.headers.get("Content-Length", "0") or "0")
        if length > 2_000_000:
            raise ValueError("request body too large")
        raw = self.rfile.read(length)
        try:
            data = json.loads(raw.decode("utf-8") if raw else "{}")
        except json.JSONDecodeError as e:
            raise ValueError("invalid JSON: %s" % e)
        if not isinstance(data, dict):
            raise ValueError("JSON body must be an object")
        return data

    def do_GET(self):
        try:
            if self.path == "/" or self.path == "/index.html":
                self.serve_file(STATIC / "index.html")
            elif self.path.startswith("/static/"):
                name = unquote(self.path[len("/static/"):])
                if "/" in name or "\\" in name or name.startswith("."):
                    self.send_error(404)
                    return
                self.serve_file(STATIC / name)
            elif self.path == "/api/tasks":
                self.send_json(200, load_json(self.server.tasks_path))
            elif self.path == "/api/responses":
                self.send_json(200, load_json(self.server.responses_path, {"meta": {}, "responses": {}}))
            else:
                self.send_error(404)
        except Exception as e:
            self.send_json(500, {"error": str(e)})

    def serve_file(self, path):
        path = Path(path)
        if not path.is_file():
            self.send_error(404)
            return
        ctype = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
        if path.suffix == ".js":
            ctype = "application/javascript"
        elif path.suffix == ".css":
            ctype = "text/css"
        elif path.suffix == ".html":
            ctype = "text/html"
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", ctype + ("; charset=utf-8" if ctype.startswith("text/") or ctype == "application/javascript" else ""))
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        try:
            if self.path.startswith("/api/responses/"):
                task_id = unquote(self.path[len("/api/responses/"):])
                if not task_id or task_id not in self.server.task_ids:
                    self.send_json(400, {"error": "unknown task id"})
                    return
                body = self.read_json_body()
                with write_lock:
                    data = load_json(self.server.responses_path, {"meta": {}, "responses": {}})
                    data.setdefault("meta", {})
                    data.setdefault("responses", {})
                    body["saved_at"] = utc_now()
                    data["responses"][task_id] = body
                    atomic_write_json(self.server.responses_path, data)
                    answered = len(data["responses"])
                self.send_json(200, {"ok": True, "answered": answered})
            elif self.path == "/api/meta":
                body = self.read_json_body()
                with write_lock:
                    data = load_json(self.server.responses_path, {"meta": {}, "responses": {}})
                    data.setdefault("meta", {})
                    data.setdefault("responses", {})
                    data["meta"].update(body)
                    atomic_write_json(self.server.responses_path, data)
                self.send_json(200, {"ok": True})
            else:
                self.send_error(404)
        except ValueError as e:
            self.send_json(400, {"error": str(e)})
        except Exception as e:
            self.send_json(500, {"error": str(e)})

    def do_DELETE(self):
        try:
            if not self.path.startswith("/api/responses/"):
                self.send_error(404)
                return
            task_id = unquote(self.path[len("/api/responses/"):])
            with write_lock:
                data = load_json(self.server.responses_path, {"meta": {}, "responses": {}})
                data.setdefault("meta", {})
                data.setdefault("responses", {})
                data["responses"].pop(task_id, None)
                atomic_write_json(self.server.responses_path, data)
                answered = len(data["responses"])
            self.send_json(200, {"ok": True, "answered": answered})
        except Exception as e:
            self.send_json(500, {"error": str(e)})


def main():
    parser = argparse.ArgumentParser(description="Local blind review app")
    parser.add_argument("--tasks", required=True, help="Tasks JSON path")
    parser.add_argument("--responses", required=True, help="Responses JSON path")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    tasks_path = Path(args.tasks).resolve()
    responses_path = Path(args.responses).resolve()
    tasks_doc = load_json(tasks_path)
    httpd = ThreadingHTTPServer(("127.0.0.1", args.port), ReviewHandler)
    httpd.tasks_path = tasks_path
    httpd.responses_path = responses_path
    httpd.task_ids = collect_task_ids(tasks_doc)
    httpd.quiet = True
    url = "http://127.0.0.1:%d/" % httpd.server_address[1]
    print(url, flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()


if __name__ == "__main__":
    main()
