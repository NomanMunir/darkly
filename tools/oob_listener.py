#!/usr/bin/env python3
import http.server, socketserver, sys, urllib.parse

port = int(sys.argv[1])
logfile = sys.argv[2]

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        open(logfile, "a").write(urllib.parse.unquote(self.path) + "\n")
        self.send_response(200)
        self.send_header("Content-Length", "2")
        self.end_headers()
        self.wfile.write(b"ok")

    def log_message(self, *a):
        pass

socketserver.TCPServer.allow_reuse_address = True
socketserver.TCPServer(("0.0.0.0", port), Handler).serve_forever()
