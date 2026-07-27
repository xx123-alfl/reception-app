#!/usr/bin/env python3
"""
接待流程管理系统 - 共享服务器
启动后团队成员可通过浏览器共同访问，数据集中存储在 data.json 文件中。

启动方式：
  python3 server.py

然后浏览器打开 http://localhost:8080
其他设备在同一个局域网下访问 http://<本机IP>:8080
"""

import http.server
import json
import os
import sys
from pathlib import Path
from urllib.parse import urlparse, parse_qs

PORT = int(os.environ.get("PORT", 8080))
# Render.com 持久磁盘路径
DATA_DIR = Path(os.environ.get("RENDER_DATA_DIR", str(Path(__file__).parent)))
DATA_FILE = DATA_DIR / "data.json"
HTML_FILE = Path(__file__).parent / "index.html"


def load_data():
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


class APIHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(HTML_FILE.parent), **kwargs)

    def do_GET(self):
        parsed = urlparse(self.path)

        if parsed.path == "/api/records":
            self.send_json(load_data())
            return

        if parsed.path == "/" or parsed.path == "/index.html":
            # Serve the index.html with injected API mode script
            html = HTML_FILE.read_text(encoding="utf-8")
            # Replace localStorage calls with API calls
            html = html.replace(
                "const STORAGE_KEY = 'reception_records';",
                "const STORAGE_KEY = 'reception_records';\nconst API_BASE = '/api/records';"
            )
            html = html.replace(
                "function getRecords() {\n  try {\n    return JSON.parse(localStorage.getItem(STORAGE_KEY)) || [];\n  } catch { return []; }\n}",
                "async function getRecords() {\n  try {\n    const res = await fetch(API_BASE);\n    const data = await res.json();\n    return data;\n  } catch { return []; }\n}"
            )
            html = html.replace(
                "function saveRecords(records) {\n  localStorage.setItem(STORAGE_KEY, JSON.stringify(records));\n}",
                "function saveRecords(records) {\n  fetch(API_BASE, { method: 'PUT', headers: {'Content-Type':'application/json'}, body: JSON.stringify(records) }).catch(() => {});\n}"
            )
            # Update init to handle async
            html = html.replace(
                "function init() {\n  // Set default date to today\n  document.getElementById('visitDate').value = new Date().toISOString().slice(0, 10);\n  updateStats();\n}",
                "async function init() {\n  document.getElementById('visitDate').value = new Date().toISOString().slice(0, 10);\n  await updateStatsAsync();\n}\nasync function updateStatsAsync() {\n  const records = await getRecords();\n  document.getElementById('recordCount').textContent = records.length;\n  document.getElementById('statTotal').textContent = records.length;\n  document.getElementById('statReviewed').textContent = records.filter(r => r.status === 'reviewed').length;\n  document.getElementById('statSubmitted').textContent = records.filter(r => r.status === 'submitted').length;\n  document.getElementById('statDraft').textContent = records.filter(r => r.status === 'draft').length;\n}"
            )
            # Fix saveRecord to be async
            html = html.replace(
                "saveRecords(records);\n  resetForm();\n  updateStats();\n  if (document.getElementById('tab-records').style.display !== 'none') {\n    renderRecords();\n  }\n}",
                "saveRecords(records);\n  resetForm();\n  updateStatsAsync();\n  if (document.getElementById('tab-records').style.display !== 'none') {\n    renderRecords();\n  }\n}"
            )
            html = html.replace(
                "saveRecords(filtered);\n    toast('🗑️ 记录已删除');\n    renderRecords();\n    updateStats();",
                "saveRecords(filtered);\n    toast('🗑️ 记录已删除');\n    renderRecords();\n    updateStatsAsync();"
            )
            html = html.replace(
                "saveRecords(records);\n    toast(`状态已更新为：${labels[newStatus]}`);\n    renderRecords();\n    updateStats();",
                "saveRecords(records);\n    toast(`状态已更新为：${labels[newStatus]}`);\n    renderRecords();\n    updateStatsAsync();"
            )
            html = html.replace(
                "function renderRecords() {\n  let records = getRecords();",
                "async function renderRecords() {\n  let records = await getRecords();"
            )
            html = html.replace(
                "function updateStats() {\n  const records = getRecords();",
                "function updateStats() {\n  updateStatsAsync();\n}\nasync function _updateStats() {\n  const records = await getRecords();"
            )
            # Fix all direct getRecords() calls in viewDetail, editRecord, deleteRecord - these are already handled
            # Make saveRecord async
            html = html.replace(
                "function saveRecord(event) {\n  event.preventDefault();",
                "async function saveRecord(event) {\n  event.preventDefault();"
            )
            html = html.replace(
                "const editId = document.getElementById('editId').value;\n  const records = getRecords();",
                "const editId = document.getElementById('editId').value;\n  const records = await getRecords();"
            )
            # Fix deleteRecord
            html = html.replace(
                "function deleteRecord(id) {\n  const records = getRecords();",
                "async function deleteRecord(id) {\n  const records = await getRecords();"
            )
            # Fix updateStatus
            html = html.replace(
                "function updateStatus(id, newStatus) {\n  const records = getRecords();",
                "async function updateStatus(id, newStatus) {\n  const records = await getRecords();"
            )
            # Fix viewDetail
            html = html.replace(
                "function viewDetail(id) {\n  const records = getRecords();",
                "async function viewDetail(id) {\n  const records = await getRecords();"
            )
            # Fix editRecord
            html = html.replace(
                "function editRecord(id) {\n  const records = getRecords();",
                "async function editRecord(id) {\n  const records = await getRecords();"
            )
            # Fix exportWord
            html = html.replace(
                "function exportWord(id) {\n  const records = getRecords();",
                "async function exportWord(id) {\n  const records = await getRecords();"
            )
            # Fix printRecord
            html = html.replace(
                "function printRecord(id) {\n  const records = getRecords();",
                "async function printRecord(id) {\n  const records = await getRecords();"
            )

            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(html.encode("utf-8"))
            return

        return super().do_GET()

    def do_PUT(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/records":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            try:
                data = json.loads(body)
                if isinstance(data, list):
                    save_data(data)
                    self.send_json({"ok": True, "count": len(data)})
                else:
                    self.send_json({"ok": False, "error": "数据格式错误，应为数组"}, 400)
            except json.JSONDecodeError:
                self.send_json({"ok": False, "error": "JSON 解析失败"}, 400)
            return

        self.send_error(404)

    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, PUT, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()


def get_local_ip():
    """获取本机局域网 IP"""
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


if __name__ == "__main__":
    ip = get_local_ip()
    print("=" * 60)
    print("   🏢 接待流程管理系统 - 共享服务器已启动")
    print("=" * 60)
    print()
    print(f"  📌 本机访问：  http://localhost:{PORT}")
    print(f"  📌 局域网访问：http://{ip}:{PORT}")
    print()
    print("  💡 将局域网地址发给团队成员，即可多人共同使用")
    print("  💡 所有数据保存在 data.json 文件中")
    print("  💡 按 Ctrl+C 停止服务器")
    print()

    server = http.server.HTTPServer(("0.0.0.0", PORT), APIHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n服务器已停止。")
        server.shutdown()
