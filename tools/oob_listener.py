#!/usr/bin/env python3
"""
Tiny out-of-band HTTP collector used by the XXE/SSRF and the stored-XSS
exploits. The target VM reaches the host at 10.0.2.2 (QEMU/VirtualBox NAT),
so we point exfil callbacks at http://10.0.2.2:<port>/.

Every request is appended (URL-decoded) to the log file. Run it before the
exploit, then read the log.

Usage:
    oob_listener.py <port> <logfile>
"""
import http.server, socketserver, sys, urllib.parse

PORT = int(sys.argv[1])
LOG = sys.argv[2]


class H(http.server.BaseHTTPRequestHandler):
    def _log(self):
        with open(LOG, "a") as f:
            f.write("HIT " + urllib.parse.unquote(self.path) + "\n")

    def do_GET(self):
        self._log()
        self.send_response(200)
        self.send_header("Content-Length", "2")
        self.end_headers()
        self.wfile.write(b"ok")

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0) or 0)
        body = self.rfile.read(n).decode("latin-1") if n else ""
        with open(LOG, "a") as f:
            f.write("POST " + urllib.parse.unquote(self.path) + " " + body + "\n")
        self.send_response(200)
        self.send_header("Content-Length", "2")
        self.end_headers()
        self.wfile.write(b"ok")

    def log_message(self, *a):
        pass


socketserver.TCPServer.allow_reuse_address = True
print(f"[*] OOB listener on 0.0.0.0:{PORT} -> {LOG}  (VM reaches us at 10.0.2.2:{PORT})")
socketserver.TCPServer(("0.0.0.0", PORT), H).serve_forever()
